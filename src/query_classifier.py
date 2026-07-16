"""Query classification for routing."""

import re
from enum import Enum


class QueryType(Enum):
    BOOK_METADATA = "book_metadata"
    BOOK_OVERVIEW = "book_overview"
    CONTENT_QUERY = "content_query"
    GREETING = "greeting"
    REDIRECTION = "redirection"
    INVALID = "invalid"


class QueryClassifier:
    """Classify user queries."""
    
    GREETING_PATTERNS = [
        r'^\s*(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))',
        r'^\s*how\s+are\s+you',
        r'^\s*what\'?s\s+up',
    ]
    
    METADATA_PATTERNS = [
        r'\b(who|what)\s+(is|are)\s+the\s+author',
        r'\bauthor\b',
        r'\bwho\s+wrote',
        r'\bname\s+of\s+(the\s+|this\s+)?book',
        r'\btitle\s+of\s+(the\s+|this\s+)?book',
        r'\bwhat\s+(is\s+)?(the\s+|this\s+)?book\s+called',
        r'\bwhen\s+was\s+(it|this)\s+published',
        r'\bpublication\s+year',
        r'\bwhat\s+year',
        r'\b(list|show|give|tell).*chapters?',
        r'\btable\s+of\s+contents',
        r'\bchapter\s+list',
        r'\bwhat\s+chapters',
    ]
    
    OVERVIEW_PATTERNS = [
        r'\bwhat\s+(is|does)\s+(this|the)\s+book\s+about',
        r'\bwhat\s+does\s+(this|the)\s+book\s+focus',
        r'\bwhat\s+(is|are)\s+the\s+main\s+(topic|theme|idea)',
        r'\bsummar(y|ize)',
        r'\boverall\s+purpose',
        r'\bwhat\s+(is|does)\s+(this|the)\s+book\s+discuss',
        r'\bwhat\s+(is|are)\s+the\s+topic',
        r'\bwhat\s+(is|are)\s+the\s+subject',
        r'\btopic\s+of\s+(this|the)\s+book',
        r'\bsubject\s+of\s+(this|the)\s+book',
    ]
    
    REDIRECTION_PATTERNS = [
        r'\b(is|are)\s+(this|that|it)\s+(good|bad|important|useful)',
        r'\bwhy\s+(should|does|do)\s+(i|we|people)\s+(care|need|want)',
        r'\bhow\s+(does|do)\s+(this|that|it)\s+(help|matter|affect)',
        r'\bwhat\s+(is|are)\s+the\s+(benefit|advantage|importance)',
        r'\b(does|do)\s+(this|that|it)\s+matter',
        r'\bin\s+real\s+life',
        r'\bwhy\s+(is|are)\s+(this|that|it)\s+important',
    ]
    
    INVALID_PATTERNS = [
        r'^[^a-zA-Z]*$',  # No letters
        r'^\s*$',  # Empty
        r'^(.)\1{5,}',  # Repeated characters (aaaaaa)
        r'^[a-z]{8,}$',  # Single lowercase word with no spaces (likely gibberish like asdfghjkl)
        r'^[^aeiou\s]{6,}$',  # 6+ consonants with no vowels (likely gibberish)
    ]
    
    def classify(self, query: str) -> QueryType:
        """Classify query type."""
        query_lower = query.lower().strip()
        
        # Check invalid first
        if len(query_lower) < 2:
            return QueryType.INVALID
        
        for pattern in self.INVALID_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryType.INVALID
        
        # Check greetings
        for pattern in self.GREETING_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryType.GREETING
        
        # Check metadata
        for pattern in self.METADATA_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryType.BOOK_METADATA
        
        # Check overview
        for pattern in self.OVERVIEW_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryType.BOOK_OVERVIEW
        
        # Check redirection (opinion/importance questions)
        for pattern in self.REDIRECTION_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryType.REDIRECTION
        
        # Default to content query
        return QueryType.CONTENT_QUERY
