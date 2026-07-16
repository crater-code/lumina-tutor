"""
Response Validator for the Book-Bounded Tutoring Chatbot.

This module provides the ResponseValidator class that enforces content boundaries
and prevents hallucination by validating that responses only contain content
from retrieved book chunks.
"""

import re
import logging
from datetime import datetime
from typing import List, Set
from difflib import SequenceMatcher
from src.models import Response, Chunk, ValidationResult


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Validates that response content originates from retrieved chunks.
    
    This class is responsible for:
    1. Checking that response content is traceable to retrieved chunks
    2. Detecting hallucination using keyword matching and similarity
    3. Logging rejected responses with timestamp and reason
    4. Returning validation results with issues list
    
    The validator enforces strict content boundaries to ensure educational
    integrity and prevent misinformation.
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.3,
        keyword_match_threshold: float = 0.5
    ):
        """
        Initialize the ResponseValidator.
        
        Args:
            similarity_threshold: Minimum similarity score for sentence matching (0-1)
                                 Lower values are more permissive
            keyword_match_threshold: Minimum ratio of keywords that must match (0-1)
                                    Lower values are more permissive
        """
        self.similarity_threshold = similarity_threshold
        self.keyword_match_threshold = keyword_match_threshold
    
    def validate_response(
        self,
        response: Response,
        retrieved_chunks: List[Chunk]
    ) -> ValidationResult:
        """
        Validate that response content originates from retrieved chunks.
        
        This method performs multiple checks:
        1. Verifies response has citations (unless it's a refusal)
        2. Checks for hallucination using keyword matching
        3. Checks for hallucination using sentence similarity
        4. Logs rejected responses
        
        Args:
            response: Generated response to validate
            retrieved_chunks: Chunks that were used for generation
        
        Returns:
            ValidationResult indicating if response is valid, with:
            - is_valid: True if response passes all checks
            - confidence: Confidence score (0-1) based on validation checks
            - issues: List of detected problems (empty if valid)
        
        Example:
            >>> validator = ResponseValidator()
            >>> result = validator.validate_response(response, chunks)
            >>> if not result.is_valid:
            ...     print(f"Validation failed: {result.issues}")
        """
        issues = []
        confidence_scores = []
        
        # Check 1: Refusal messages are always valid
        if response.is_refusal:
            return ValidationResult(
                is_valid=True,
                confidence=1.0,
                issues=[]
            )
        
        # Check 2: Non-refusal responses must have citations
        if not response.chunk_ids:
            issues.append("Response has no chunk citations")
            confidence_scores.append(0.0)
        else:
            confidence_scores.append(1.0)
        
        # Check 3: Verify chunks exist
        if not retrieved_chunks:
            issues.append("No retrieved chunks provided for validation")
            confidence_scores.append(0.0)
        else:
            confidence_scores.append(1.0)
        
        # If we already have critical issues, return early
        if issues:
            result = ValidationResult(
                is_valid=False,
                confidence=sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
                issues=issues
            )
            self._log_rejected_response(response, result)
            return result
        
        # Check 4: Check for hallucination
        hallucination_detected = self.check_hallucination(
            response.text,
            [chunk.text for chunk in retrieved_chunks]
        )
        
        if hallucination_detected:
            issues.append("Response contains content not found in retrieved chunks (hallucination detected)")
            confidence_scores.append(0.0)
        else:
            confidence_scores.append(1.0)
        
        # Calculate overall confidence
        confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Determine if valid
        is_valid = len(issues) == 0
        
        # Create result
        result = ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues
        )
        
        # Log if rejected
        if not is_valid:
            self._log_rejected_response(response, result)
        
        return result
    
    def check_hallucination(
        self,
        response_text: str,
        chunk_texts: List[str]
    ) -> bool:
        """
        Check if response contains content not in chunks.
        
        Uses multiple heuristics:
        1. Keyword extraction and matching
        2. Sentence similarity comparison
        3. Named entity checking (basic implementation)
        
        Args:
            response_text: The generated response text
            chunk_texts: List of chunk text content
        
        Returns:
            True if hallucination detected, False otherwise
        
        Example:
            >>> validator = ResponseValidator()
            >>> is_hallucinated = validator.check_hallucination(
            ...     "The sky is blue because of Rayleigh scattering",
            ...     ["The sky appears blue during the day."]
            ... )
        """
        # Combine all chunk texts
        combined_chunks = " ".join(chunk_texts)
        
        # Extract keywords from response and chunks
        response_keywords = self._extract_keywords(response_text)
        chunk_keywords = self._extract_keywords(combined_chunks)
        
        # Check 1: Keyword matching
        # If response has significant keywords not in chunks, it's likely hallucinated
        if response_keywords:
            matching_keywords = response_keywords.intersection(chunk_keywords)
            match_ratio = len(matching_keywords) / len(response_keywords)
            
            if match_ratio < self.keyword_match_threshold:
                logger.debug(
                    f"Keyword match ratio {match_ratio:.2f} below threshold "
                    f"{self.keyword_match_threshold}"
                )
                return True
        
        # Check 2: Sentence similarity
        # Break response into sentences and check if each has similar content in chunks
        response_sentences = self._split_into_sentences(response_text)
        
        for sentence in response_sentences:
            # Skip very short sentences (like "Yes." or "I see.")
            if len(sentence.split()) < 4:
                continue
            
            # Check if this sentence has similar content in any chunk
            has_similar_content = False
            for chunk_text in chunk_texts:
                chunk_sentences = self._split_into_sentences(chunk_text)
                for chunk_sentence in chunk_sentences:
                    similarity = self._calculate_similarity(sentence, chunk_sentence)
                    if similarity >= self.similarity_threshold:
                        has_similar_content = True
                        break
                
                if has_similar_content:
                    break
            
            if not has_similar_content:
                logger.debug(
                    f"Sentence has no similar content in chunks: '{sentence[:50]}...'"
                )
                return True
        
        # Check 3: Named entity checking (basic)
        # Look for proper nouns or specific facts that might be hallucinated
        response_entities = self._extract_entities(response_text)
        chunk_entities = self._extract_entities(combined_chunks)
        
        # If response has entities not in chunks, it might be hallucinated
        # But be lenient - only flag if there are multiple unmatched entities
        unmatched_entities = response_entities - chunk_entities
        if len(unmatched_entities) > 2:
            logger.debug(
                f"Multiple unmatched entities found: {unmatched_entities}"
            )
            return True
        
        # If all checks pass, no hallucination detected
        return False
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """
        Extract significant keywords from text.
        
        This is a simple implementation that:
        1. Converts to lowercase
        2. Removes punctuation
        3. Filters out common stop words
        4. Returns unique words
        
        Args:
            text: Input text
        
        Returns:
            Set of keywords
        """
        # Common stop words (simplified list)
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'this', 'but', 'they', 'have', 'had',
            'what', 'when', 'where', 'who', 'which', 'why', 'how', 'can', 'could',
            'would', 'should', 'may', 'might', 'must', 'shall', 'i', 'you', 'we',
            'or', 'not', 'no', 'yes', 'if', 'then', 'than', 'so', 'very', 'just',
            'about', 'all', 'also', 'am', 'been', 'being', 'do', 'does', 'did',
            'doing', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'there', 'these', 'those', 'through', 'up', 'down', 'out', 'into'
        }
        
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words and filter
        words = text.split()
        keywords = {word for word in words if word not in stop_words and len(word) > 2}
        
        return keywords
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Uses simple regex-based sentence splitting.
        
        Args:
            text: Input text
        
        Returns:
            List of sentences
        """
        # Split on sentence boundaries (., !, ?)
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up and filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.
        
        Uses SequenceMatcher for simple string similarity.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0-1)
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _extract_entities(self, text: str) -> Set[str]:
        """
        Extract named entities from text (basic implementation).
        
        This is a simple implementation that looks for:
        1. Capitalized words (potential proper nouns)
        2. Numbers (potential facts/statistics)
        
        A more sophisticated implementation would use NER models.
        
        Args:
            text: Input text
        
        Returns:
            Set of potential entities
        """
        entities = set()
        
        # Find capitalized words (potential proper nouns)
        # Exclude sentence-starting words by looking for mid-sentence capitals
        words = text.split()
        for i, word in enumerate(words):
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Check if capitalized and not at sentence start
            if clean_word and clean_word[0].isupper():
                # Skip if it's the first word or follows sentence-ending punctuation
                if i > 0 and not words[i-1].endswith(('.', '!', '?')):
                    entities.add(clean_word)
        
        # Find numbers (potential facts/statistics)
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        entities.update(numbers)
        
        return entities
    
    def _log_rejected_response(
        self,
        response: Response,
        validation_result: ValidationResult
    ) -> None:
        """
        Log rejected responses with timestamp and reason.
        
        This creates a log entry that can be used for monitoring
        and improving the system.
        
        Args:
            response: The rejected response
            validation_result: The validation result with issues
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "response_text": response.text[:200] + "..." if len(response.text) > 200 else response.text,
            "chunk_ids": response.chunk_ids,
            "is_refusal": response.is_refusal,
            "confidence": validation_result.confidence,
            "issues": validation_result.issues,
            "metadata": response.metadata
        }
        
        logger.warning(
            f"Response validation failed: {log_entry}"
        )
