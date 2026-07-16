"""Infer student age from query text."""

import re


class AgeInferencer:
    """Infer student age from query characteristics."""
    
    def infer_age(self, query: str) -> int:
        """Infer age from query text (returns 4-15)."""
        score = 0
        
        # Sentence length
        words = query.split()
        word_count = len(words)
        
        if word_count <= 5:
            score += 0  # Very young
        elif word_count <= 10:
            score += 3
        elif word_count <= 15:
            score += 6
        else:
            score += 9
        
        # Vocabulary complexity
        complex_words = ['however', 'therefore', 'consequently', 'furthermore', 'moreover', 'nevertheless']
        if any(word in query.lower() for word in complex_words):
            score += 4
        
        # Grammar patterns
        if '?' in query:
            score += 2  # Proper question formation
        
        if re.search(r'\b(can|could|would|should)\s+you\b', query.lower()):
            score += 2  # Polite phrasing
        
        # Spelling consistency (simple check)
        if query[0].isupper() and query.endswith('?'):
            score += 1  # Proper capitalization
        
        # Map score to age (4-15)
        if score <= 3:
            return 6  # Young child
        elif score <= 7:
            return 9  # Elementary
        elif score <= 12:
            return 12  # Middle school
        else:
            return 14  # Older student
