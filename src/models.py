"""
Data models for the Book-Bounded Tutoring Chatbot system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class PageContent:
    """Represents the content of a single page from a PDF."""
    page_number: int
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    """Represents a semantic chunk of book content."""
    chunk_id: str
    text: str
    page_numbers: List[int]
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StructuralChunk:
    """Structural chunk with hierarchy metadata."""
    chunk_id: str
    text: str
    page_numbers: List[int]
    hierarchy: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    """Represents a chatbot response."""
    text: str
    chunk_ids: List[str]
    is_refusal: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Represents the result of response validation."""
    is_valid: bool
    confidence: float
    issues: List[str] = field(default_factory=list)


@dataclass
class QueryContext:
    """Represents the context for a user query."""
    query: str
    book_id: str
    user_age: int
    language: str
    session_id: Optional[str] = None
