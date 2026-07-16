"""Strict validator for quote-based responses."""

import re
from typing import List
from src.models import Response, Chunk, ValidationResult


class StrictGroundingValidator:
    """Validates responses contain only direct quotes."""
    
    def validate_response(self, response: Response, chunks: List[Chunk]) -> ValidationResult:
        """Validate response is grounded in chunks."""
        if response.is_refusal:
            return ValidationResult(is_valid=True, confidence=1.0, issues=[])
        
        issues = []
        
        # Check 1: Has citations
        if not response.chunk_ids:
            issues.append("No chunk citations")
        
        # Check 2: Extract quotes from response
        quotes = self._extract_quotes(response.text)
        
        if not quotes:
            issues.append("No direct quotes found in response")
        
        # Check 3: Verify quotes exist in chunks
        for quote in quotes:
            if not self._verify_quote_in_chunks(quote, chunks):
                issues.append(f"Quote not found in chunks: '{quote[:50]}...'")
        
        is_valid = len(issues) == 0
        confidence = 1.0 if is_valid else 0.0
        
        return ValidationResult(is_valid=is_valid, confidence=confidence, issues=issues)
    
    def _extract_quotes(self, text: str) -> List[str]:
        """Extract quoted text from response."""
        # Find text in quotes
        quotes = re.findall(r'"([^"]+)"', text)
        return quotes
    
    def _verify_quote_in_chunks(self, quote: str, chunks: List[Chunk]) -> bool:
        """Verify quote exists in chunks."""
        quote_normalized = quote.lower().strip()
        
        for chunk in chunks:
            chunk_normalized = chunk.text.lower().strip()
            if quote_normalized in chunk_normalized:
                return True
        
        return False
