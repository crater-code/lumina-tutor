"""Bounded chatbot with conversational LLM responses."""

import re
import os
import json
import requests
import logging
from typing import List, Optional
from src.models import Chunk, Response
from src.book_metadata import BookMetadata, BookMetadataStore
from src.query_classifier import QueryClassifier, QueryType
from src.age_inference import AgeInferencer

# Set up logging
logger = logging.getLogger(__name__)


class BoundedChatbotEngine:
    """Conversational chatbot that stays grounded in book content."""
    
    def __init__(self):
        self.metadata_store = BookMetadataStore()
        self.classifier = QueryClassifier()
        self.age_inferencer = AgeInferencer()
        self.metadata: Optional[BookMetadata] = None
        self._load_metadata()
        
        # LLM Configuration - GEMINI ONLY
        self.llm_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        
        # Force Gemini only
        if self.llm_provider != "gemini":
            raise RuntimeError(f"SYSTEM FAILURE: Only Gemini is supported. Current provider: {self.llm_provider}")
        
        # Gemini configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Check Gemini availability - MUST be available
        self.llm_available = self._check_gemini()
        
        if not self.llm_available:
            raise RuntimeError("SYSTEM FAILURE: Gemini API is not available. System cannot function without Gemini.")
    
    def _check_gemini(self) -> bool:
        """Check if Gemini API is configured - REQUIRED."""
        if not self.gemini_api_key or self.gemini_api_key == "your_gemini_api_key_here":
            logger.error("SYSTEM FAILURE: Gemini API key not configured")
            return False
        
        try:
            from google import genai
            # Test connection
            client = genai.Client(api_key=self.gemini_api_key)
            logger.info(f"✅ Gemini API configured with model: {self.gemini_model}")
            return True
        except ImportError:
            logger.error("SYSTEM FAILURE: google-genai package not installed. Run: pip install google-genai")
            return False
        except Exception as e:
            logger.error(f"SYSTEM FAILURE: Gemini configuration failed: {e}")
            return False
    
    def _load_metadata(self):
        """Load book metadata at startup."""
        self.metadata = self.metadata_store.load()
    
    def _handle_metadata_query(self, query: str, user_age: Optional[int], language: str) -> Response:
        """Handle book metadata queries (author, title, year)."""
        # Infer age if not provided
        if user_age is None:
            user_age = self.age_inferencer.infer_age(query)
        
        if not self.metadata:
            return Response(
                text="Book information is not available.",
                chunk_ids=[],
                is_refusal=True,
                metadata={"query_type": "metadata", "language": language}
            )
        
        query_lower = query.lower()
        
        # Direct answers - NO LLM needed for speed
        if 'author' in query_lower or 'who wrote' in query_lower:
            text = f"The author is {self.metadata.author}"
        elif 'title' in query_lower or 'name of' in query_lower or 'called' in query_lower:
            text = f"The book is called '{self.metadata.title}'"
        elif 'year' in query_lower or 'published' in query_lower or 'when' in query_lower:
            if self.metadata.publication_year:
                text = f"It was published in {self.metadata.publication_year}"
            else:
                text = "The publication year isn't clearly stated in the book"
        else:
            text = f"The book is '{self.metadata.title}' by {self.metadata.author}"
        
        return Response(
            text=text,
            chunk_ids=[],
            is_refusal=False,
            metadata={"query_type": "metadata", "language": language}
        )
    
    def _handle_overview_query(self, query: str, user_age: Optional[int], language: str) -> Response:
        """Handle book overview queries."""
        if not self.metadata or not self.metadata.description_quotes:
            return Response(
                text="The book doesn't clearly state its overall topic in the introduction.",
                chunk_ids=[],
                is_refusal=False,
                metadata={"query_type": "overview", "language": language}
            )
        
        # Infer age if not provided
        if user_age is None:
            user_age = self.age_inferencer.infer_age(query)
        
        # Use first description quote
        quote = self.metadata.description_quotes[0]
        quote_text = self._simplify_for_age(quote["text"], user_age)
        
        # Generate conversational response with the quote
        text = self._generate_conversational_response(
            query=query,
            facts=[f"On page {quote['page']}, the book states: \"{quote_text}\""],
            user_age=user_age,
            response_type="overview"
        )
        
        return Response(
            text=text,
            chunk_ids=[],
            is_refusal=False,
            metadata={"query_type": "overview", "language": language}
        )
    
    def _handle_invalid_query(self, user_age: Optional[int], language: str) -> Response:
        """Handle invalid/nonsense queries."""
        # Infer age if not provided (though not used for invalid queries)
        if user_age is None:
            user_age = 10  # Default age for refusal messages
        
        text = "I can only answer questions using this book. Could you ask your question in a clearer way?"
        
        return Response(
            text=text,
            chunk_ids=[],
            is_refusal=True,
            metadata={"query_type": "invalid", "language": language}
        )
    
    def _handle_content_query(self, query: str, chunks: List[Chunk], user_age: Optional[int], language: str) -> Response:
        """Handle content queries using chunks with Gemini - NO FALLBACKS."""
        # Infer age if not provided
        if user_age is None:
            user_age = self.age_inferencer.infer_age(query)
        
        if not chunks:
            return Response(
                text="I can only answer questions using this book. Could you ask your question in a clearer way?",
                chunk_ids=[],
                is_refusal=True,
                metadata={"query_type": "content", "language": language}
            )
        
        # Use Gemini ONLY - no fallbacks
        response_text = self._generate_complete_response(
            query=query,
            chunks=chunks,
            user_age=user_age,
            language=language
        )
        
        return Response(
            text=response_text,
            chunk_ids=[c.chunk_id for c in chunks],
            is_refusal=False,
            metadata={"age_group": self._get_age_group(user_age), "language": language}
        )
    
    def generate_refusal(self, query: str, user_age: Optional[int] = None, language: str = "en") -> Response:
        """Generate refusal message."""
        text = "I can only answer questions using this book. Could you ask your question in a clearer way?"
        return Response(text=text, chunk_ids=[], is_refusal=True, metadata={"language": language})
    
    def _generate_complete_response(self, query: str, chunks: List[Chunk], user_age: int, language: str) -> str:
        """Generate a complete natural conversational response using Gemini - GEMINI ONLY."""
        # Combine relevant chunks
        combined_text = "\n\n".join([
            f"[Page {', '.join(map(str, chunk.page_numbers))}]: {chunk.text}"
            for chunk in chunks[:3]  # Use top 3 chunks
        ])
        
        # Build natural conversational prompt
        prompt = f"""You are a helpful, friendly assistant having a natural conversation with someone who's reading a book.

THEIR QUESTION: "{query}"

RELEVANT CONTENT FROM THE BOOK:
{combined_text}

YOUR TASK:
Answer their question naturally and conversationally, like you're chatting with a friend. Use the book content above to inform your answer.

STYLE GUIDELINES:
- Be natural and conversational, not formal or robotic
- Speak like a real person, not a textbook
- Use casual language and contractions (like "it's", "you'll", "that's")
- Be friendly and engaging
- Keep it clear and easy to understand
- Don't use phrases like "The book says..." unless it feels natural
- Just answer the question directly and naturally
- Use ONLY information from the book content provided above
- Don't add facts or information not in the book

Generate your response now:"""

        # Call Gemini with resilient grounded quote fallback
        try:
            return self._call_gemini(prompt, max_tokens=500)
        except Exception as e:
            logger.warning(f"Gemini API unavailable ({e}), falling back to grounded text excerpts")
            top_chunk = chunks[0]
            pages = f"Page {', '.join(map(str, top_chunk.page_numbers))}" if top_chunk.page_numbers else "the book"
            clean_text = top_chunk.text.strip().replace("\n", " ")
            if len(clean_text) > 400:
                clean_text = clean_text[:400] + "..."
            return f"According to {pages} of the book:\n\n\"{clean_text}\""
    
    def _generate_conversational_response(self, query: str, facts: List[str], user_age: int, response_type: str) -> str:
        """Generate a natural conversational response using Gemini or verified facts fallback."""
        logger.info(f"Generating conversational response")
        
        # Build natural prompt
        system_prompt = f"""You are a helpful, friendly assistant having a natural conversation.

RULES:
- Be conversational and natural, like chatting with a friend
- Use casual language and contractions
- Don't be formal or robotic
- Just answer directly and naturally
- Use ONLY the information provided below"""

        if response_type == "metadata":
            user_prompt = f"""Question: "{query}"

Information: {chr(10).join(f"- {fact}" for fact in facts)}

Answer naturally and conversationally."""

        elif response_type == "overview":
            user_prompt = f"""Question: "{query}"

From the book: {facts[0]}

Answer naturally about what the book is about."""

        else:  # content
            user_prompt = f"""Question: "{query}"

Information: {chr(10).join(f"- {fact}" for fact in facts)}

Answer naturally and conversationally."""

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Call Gemini with factual fallback
        try:
            return self._call_gemini(full_prompt, max_tokens=400)
        except Exception as e:
            logger.warning(f"Gemini API unavailable ({e}), returning verified fact")
            return facts[0] if facts else "Here is what the book explains."
    
    def _simplify_for_age(self, text: str, age: int) -> str:
        """Simplify text for younger children."""
        if age >= 12:
            return text
        
        if age >= 8:
            # Break very long sentences
            if len(text.split()) > 30:
                text = text.replace(", ", ". ")
            return text
        
        # Ages 4-7: more simplification
        text = text.replace(" and ", ". ").replace(" but ", ". ")
        return text
    
    def _get_age_group(self, age: int) -> str:
        """Get age group name."""
        if age <= 7:
            return "young_child"
        elif age <= 11:
            return "elementary"
        return "middle_school"
    
    def _call_gemini(self, prompt: str, max_tokens: int = 150) -> str:
        """Call Gemini API to generate a response using the new SDK."""
        try:
            from google import genai
            from google.genai import types
            
            # Create client
            client = genai.Client(api_key=self.gemini_api_key)
            
            logger.info(f"Calling Gemini with max_tokens={max_tokens}")
            
            # Generate response
            response = client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                    safety_settings=[
                        types.SafetySetting(
                            category='HARM_CATEGORY_HARASSMENT',
                            threshold='BLOCK_NONE'
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_HATE_SPEECH',
                            threshold='BLOCK_NONE'
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                            threshold='BLOCK_NONE'
                        ),
                        types.SafetySetting(
                            category='HARM_CATEGORY_DANGEROUS_CONTENT',
                            threshold='BLOCK_NONE'
                        ),
                    ]
                )
            )
            
            # Extract text from response
            if hasattr(response, 'text') and response.text:
                result = response.text.strip()
                logger.info(f"✅ Gemini response: {len(result)} characters")
                return result
            
            # Check candidates if text is not available
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                result = part.text.strip()
                                logger.info(f"✅ Gemini response from parts: {len(result)} characters")
                                return result
            
            logger.error("❌ GEMINI RETURNED EMPTY RESPONSE")
            logger.error(f"Response object: {response}")
            raise RuntimeError("SYSTEM FAILURE: Gemini returned empty response")
                
        except Exception as e:
            logger.error(f"❌ GEMINI API CALL FAILED: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise RuntimeError(f"SYSTEM FAILURE: Gemini API call failed: {e}")
    
