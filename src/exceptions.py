"""
Custom exceptions for the Book-Bounded Tutoring Chatbot system.
"""


class PDFParseError(Exception):
    """Raised when a PDF file cannot be parsed or read."""
    pass


class FileSizeError(Exception):
    """Raised when a PDF file exceeds the maximum allowed page count."""
    pass


class NoTextError(Exception):
    """Raised when a PDF file contains no extractable text."""
    pass


class BookNotFoundError(Exception):
    """Raised when a requested book is not found in the system."""
    pass


class RetrievalError(Exception):
    """Raised when chunk retrieval fails."""
    pass


class LLMError(Exception):
    """Raised when LLM API calls fail."""
    pass
