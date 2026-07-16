"""
Chatbot Engine for the Book-Bounded Tutoring Chatbot.

This module provides the ChatbotEngine class that generates bounded responses
using only retrieved book chunks. It enforces strict content boundaries and
includes age-adaptive language prompting.
"""

import os
import re
from typing import List, Optional
from src.models import Chunk, Response
from src.exceptions import LLMError


class ChatbotEngine:
    """
    Generates bounded responses using only retrieved book chunks.
    
    This class is responsible for:
    1. Building prompts with system instructions and age adaptation
    2. Generating responses using a free LLM API
    3. Including chunk citations in responses
    4. Adapting language complexity based on user age
    5. Generating responses in the same language as the query
    
    The engine enforces strict content boundaries - responses must only
    use content from the provided chunks, with no external knowledge.
    """
    
    # Age group definitions for language adaptation
    AGE_GROUPS = {
        (4, 7): {
            "name": "young_child",
            "guidance": "Use very simple words and short sentences. Explain like talking to a 5-year-old.",
            "example": "The sun is very hot. It gives us light."
        },
        (8, 11): {
            "name": "elementary",
            "guidance": "Use clear language appropriate for elementary students. Use moderate vocabulary.",
            "example": "The sun is a star that provides heat and light to Earth."
        },
        (12, 15): {
            "name": "middle_school",
            "guidance": "Use age-appropriate language for middle school students. You can use more complex vocabulary.",
            "example": "The sun is a star that generates energy through nuclear fusion."
        }
    }
    
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the ChatbotEngine.
        
        Args:
            model_name: Name of the LLM model to use (optional)
                       Defaults to a free Hugging Face model
            api_key: API key for the LLM service (optional)
                    Can also be set via HUGGINGFACE_API_KEY environment variable
        """
        self.model_name = model_name or "mistralai/Mistral-7B-Instruct-v0.2"
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        
        # For now, we'll use a simple implementation that doesn't require API calls
        # This can be extended to use actual LLM APIs when needed
        self.use_mock_llm = not self.api_key or os.getenv("USE_MOCK_LLM", "true").lower() == "true"
    
    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Chunk],
        user_age: int,
        language: str = "en"
    ) -> Response:
        """
        Generate a bounded response using only retrieved chunks.
        
        This method:
        1. Validates inputs
        2. Builds a prompt with system instructions and age adaptation
        3. Includes retrieved chunks in the prompt
        4. Calls the LLM to generate a response
        5. Extracts chunk citations from the response
        6. Returns a Response object with text and citations
        
        Args:
            query: User's question
            retrieved_chunks: List of Chunk objects retrieved from the book
            user_age: User's age (4-15) for language adaptation
            language: Response language ("en" for English, "ur" for Urdu)
        
        Returns:
            Response object containing:
            - text: The generated answer
            - chunk_ids: List of chunk IDs used in the response
            - is_refusal: False (this is not a refusal)
            - metadata: Additional information (age_group, language)
        
        Raises:
            ValueError: If inputs are invalid
            LLMError: If response generation fails
        
        Example:
            >>> engine = ChatbotEngine()
            >>> chunks = [chunk1, chunk2]
            >>> response = engine.generate_response(
            ...     query="What is photosynthesis?",
            ...     retrieved_chunks=chunks,
            ...     user_age=10,
            ...     language="en"
            ... )
            >>> print(response.text)
            >>> print(response.chunk_ids)
        """
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not retrieved_chunks:
            raise ValueError("Retrieved chunks cannot be empty. Use generate_refusal() instead.")
        
        if not (4 <= user_age <= 15):
            raise ValueError("User age must be between 4 and 15")
        
        if language not in ["en", "ur"]:
            raise ValueError("Language must be 'en' or 'ur'")
        
        try:
            # Build the prompt
            prompt = self._build_prompt(query, retrieved_chunks, user_age, language)
            
            # Generate response using LLM
            response_text = self._call_llm(prompt)
            
            # Extract chunk IDs from the response
            chunk_ids = [chunk.chunk_id for chunk in retrieved_chunks]
            
            # Create Response object
            response = Response(
                text=response_text,
                chunk_ids=chunk_ids,
                is_refusal=False,
                metadata={
                    "age_group": self._get_age_group_name(user_age),
                    "language": language,
                    "num_chunks_used": len(retrieved_chunks)
                }
            )
            
            return response
            
        except Exception as e:
            raise LLMError(f"Failed to generate response: {str(e)}")
    
    def generate_refusal(
        self,
        query: str,
        user_age: int,
        language: str = "en"
    ) -> Response:
        """
        Generate a polite refusal message when no relevant chunks are found.
        
        The refusal message:
        - Explains that the answer is not found in the book
        - Is age-appropriate based on user age
        - Does not suggest external resources
        - Encourages asking different questions about the book
        
        Args:
            query: User's question
            user_age: User's age (4-15) for age-appropriate language
            language: Response language ("en" or "ur")
        
        Returns:
            Response object containing:
            - text: The refusal message
            - chunk_ids: Empty list (no chunks used)
            - is_refusal: True
            - metadata: Additional information (age_group, language)
        
        Raises:
            ValueError: If inputs are invalid
        
        Example:
            >>> engine = ChatbotEngine()
            >>> response = engine.generate_refusal(
            ...     query="What is quantum mechanics?",
            ...     user_age=10,
            ...     language="en"
            ... )
            >>> print(response.text)
            >>> print(response.is_refusal)  # True
        """
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not (4 <= user_age <= 15):
            raise ValueError("User age must be between 4 and 15")
        
        if language not in ["en", "ur"]:
            raise ValueError("Language must be 'en' or 'ur'")
        
        # Generate age-appropriate refusal message
        refusal_text = self._generate_refusal_text(user_age, language)
        
        # Create Response object
        response = Response(
            text=refusal_text,
            chunk_ids=[],
            is_refusal=True,
            metadata={
                "age_group": self._get_age_group_name(user_age),
                "language": language
            }
        )
        
        return response
    
    def _build_prompt(
        self,
        query: str,
        chunks: List[Chunk],
        age: int,
        language: str
    ) -> str:
        """
        Build a prompt that enforces bounded responses.
        
        The prompt structure:
        1. System instruction: Enforce bounded responses
        2. Age adaptation: Adjust language complexity
        3. Language instruction: Generate response in correct language
        4. Constraints: No external knowledge, cite chunk IDs
        5. Book excerpts: Include chunk text with IDs
        6. User query
        
        Args:
            query: User's question
            chunks: List of retrieved chunks
            age: User's age
            language: Response language
        
        Returns:
            Formatted prompt string
        """
        # Get age-appropriate guidance
        age_guidance = self._get_age_guidance(age)
        
        # Language instruction
        language_instruction = {
            "en": "Answer in English.",
            "ur": "Answer in Urdu (اردو میں جواب دیں)."
        }[language]
        
        # Build the prompt
        prompt_parts = [
            "You are a helpful tutor for children. Follow these rules strictly:",
            "",
            "RULES:",
            "1. Answer ONLY using the book excerpts provided below.",
            "2. Do NOT add any external knowledge, examples, or facts.",
            "3. If the excerpts don't contain the answer, say you cannot answer.",
            f"4. {age_guidance}",
            f"5. {language_instruction}",
            "6. Keep your answer clear and accurate.",
            "",
            "BOOK EXCERPTS:",
        ]
        
        # Add chunks with IDs
        for i, chunk in enumerate(chunks, 1):
            prompt_parts.append(f"\n[Excerpt {i} - ID: {chunk.chunk_id}]")
            prompt_parts.append(chunk.text)
            prompt_parts.append("")
        
        # Add the query
        prompt_parts.append("QUESTION:")
        prompt_parts.append(query)
        prompt_parts.append("")
        prompt_parts.append("ANSWER:")
        
        return "\n".join(prompt_parts)
    
    def _get_age_guidance(self, age: int) -> str:
        """
        Get age-appropriate language guidance.
        
        Args:
            age: User's age (4-15)
        
        Returns:
            Guidance string for the LLM
        """
        for (min_age, max_age), group_info in self.AGE_GROUPS.items():
            if min_age <= age <= max_age:
                return group_info["guidance"]
        
        # Default to middle school if age is out of range
        return self.AGE_GROUPS[(12, 15)]["guidance"]
    
    def _get_age_group_name(self, age: int) -> str:
        """
        Get the age group name for a given age.
        
        Args:
            age: User's age (4-15)
        
        Returns:
            Age group name (e.g., "young_child", "elementary", "middle_school")
        """
        for (min_age, max_age), group_info in self.AGE_GROUPS.items():
            if min_age <= age <= max_age:
                return group_info["name"]
        
        return "middle_school"
    
    def _generate_refusal_text(self, age: int, language: str) -> str:
        """
        Generate an age-appropriate refusal message.
        
        Args:
            age: User's age (4-15)
            language: Response language ("en" or "ur")
        
        Returns:
            Refusal message text
        """
        if language == "en":
            if 4 <= age <= 7:
                return (
                    "I'm sorry, but I can't find the answer to your question in this book. "
                    "Can you ask me something else about the book?"
                )
            elif 8 <= age <= 11:
                return (
                    "I couldn't find information about that in this book. "
                    "The book doesn't seem to cover this topic. "
                    "Would you like to ask me something else about what's in the book?"
                )
            else:  # 12-15
                return (
                    "I couldn't find relevant information about that in this book. "
                    "The content you're asking about doesn't appear to be covered in this book. "
                    "Feel free to ask me other questions about the topics that are in the book."
                )
        else:  # Urdu
            if 4 <= age <= 7:
                return (
                    "مجھے افسوس ہے، لیکن میں اس کتاب میں آپ کے سوال کا جواب نہیں ڈھونڈ سکتا۔ "
                    "کیا آپ مجھ سے کتاب کے بارے میں کچھ اور پوچھ سکتے ہیں؟"
                )
            elif 8 <= age <= 11:
                return (
                    "مجھے اس کتاب میں اس کے بارے میں معلومات نہیں مل سکیں۔ "
                    "یہ کتاب اس موضوع کا احاطہ نہیں کرتی۔ "
                    "کیا آپ مجھ سے کتاب میں موجود چیزوں کے بارے میں کچھ اور پوچھنا چاہیں گے؟"
                )
            else:  # 12-15
                return (
                    "مجھے اس کتاب میں اس کے بارے میں متعلقہ معلومات نہیں مل سکیں۔ "
                    "جو مواد آپ پوچھ رہے ہیں وہ اس کتاب میں شامل نہیں ہے۔ "
                    "براہ کرم مجھ سے کتاب میں موجود موضوعات کے بارے میں دوسرے سوالات پوچھیں۔"
                )
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM API to generate a response.
        
        For now, this uses a mock implementation that extracts content
        from the chunks in the prompt. This can be extended to use
        actual LLM APIs (Hugging Face, Ollama, etc.) when needed.
        
        Args:
            prompt: The formatted prompt
        
        Returns:
            Generated response text
        
        Raises:
            LLMError: If API call fails
        """
        if self.use_mock_llm:
            return self._mock_llm_response(prompt)
        else:
            return self._call_huggingface_api(prompt)
    
    def _mock_llm_response(self, prompt: str) -> str:
        """
        Generate a mock response for testing purposes.
        
        This extracts the first excerpt from the prompt and uses it
        to create a simple response. This is useful for testing without
        requiring actual LLM API calls.
        
        Args:
            prompt: The formatted prompt
        
        Returns:
            Mock response text
        """
        # Extract the question from the prompt
        question_match = re.search(r"QUESTION:\s*(.+?)\s*ANSWER:", prompt, re.DOTALL)
        question = question_match.group(1).strip() if question_match else "your question"
        
        # Extract the first excerpt
        excerpt_match = re.search(r"\[Excerpt \d+ - ID: (.+?)\]\s*(.+?)(?=\[Excerpt|\nQUESTION:)", prompt, re.DOTALL)
        
        if excerpt_match:
            chunk_id = excerpt_match.group(1).strip()
            excerpt_text = excerpt_match.group(2).strip()
            
            # Create a simple response based on the excerpt
            # Take the first sentence or first 100 characters
            first_sentence = excerpt_text.split('.')[0] + '.'
            if len(first_sentence) > 150:
                first_sentence = excerpt_text[:100] + "..."
            
            return f"Based on the book, {first_sentence}"
        else:
            return "I can help you understand the content from the book."
    
    def _call_huggingface_api(self, prompt: str) -> str:
        """
        Call the Hugging Face Inference API to generate a response.
        
        This method can be implemented when actual LLM API integration is needed.
        It would use the Hugging Face Inference API with a free model.
        
        Args:
            prompt: The formatted prompt
        
        Returns:
            Generated response text
        
        Raises:
            LLMError: If API call fails
        """
        try:
            import requests
            
            api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Extract only the answer part (after "ANSWER:")
                if "ANSWER:" in generated_text:
                    answer = generated_text.split("ANSWER:")[-1].strip()
                    return answer
                return generated_text
            
            raise LLMError("Unexpected API response format")
            
        except requests.exceptions.RequestException as e:
            raise LLMError(f"API request failed: {str(e)}")
        except Exception as e:
            raise LLMError(f"Failed to call LLM API: {str(e)}")
