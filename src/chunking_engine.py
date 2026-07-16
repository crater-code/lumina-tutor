"""
Chunking Engine for dividing book content into semantic chunks.

This module provides the ChunkingEngine class that divides book content into
semantically meaningful, retrievable segments with metadata.
"""

import re
from typing import List
from src.models import PageContent, Chunk


class ChunkingEngine:
    """
    Divides book content into semantic chunks with automatic boundary detection.
    
    This engine creates fixed-size chunks with overlap while respecting sentence
    boundaries to maintain semantic coherence. It handles both English and Urdu text.
    """
    
    DEFAULT_CHUNK_SIZE = 500  # characters
    DEFAULT_OVERLAP = 50  # characters
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP):
        """
        Initialize the chunking engine.
        
        Args:
            chunk_size: Target chunk size in characters (default: 500)
            overlap: Overlap between chunks in characters (default: 50)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def create_chunks(
        self,
        pages: List[PageContent],
        book_id: str = "default"
    ) -> List[Chunk]:
        """
        Creates semantic chunks from page content.
        
        Args:
            pages: List of PageContent objects
            book_id: Unique identifier for the book (default: "default")
            
        Returns:
            List of Chunk objects with unique IDs and metadata
        """
        if not pages:
            return []
        
        # Combine all pages into a single text with page tracking
        full_text = ""
        char_to_page = []  # Maps character index to page number
        
        for page in pages:
            page_start = len(full_text)
            full_text += page.text
            page_end = len(full_text)
            
            # Track which page each character belongs to
            for _ in range(page_start, page_end):
                char_to_page.append(page.page_number)
            
            # Add space between pages if not already present
            if full_text and not full_text.endswith((' ', '\n')):
                full_text += ' '
                char_to_page.append(page.page_number)
        
        # Split text into sentences
        sentences = self._split_into_sentences(full_text)
        
        # Create chunks respecting sentence boundaries
        chunks = []
        chunk_index = 0
        current_pos = 0
        
        while current_pos < len(full_text):
            # Find the end position for this chunk
            chunk_end = min(current_pos + self.chunk_size, len(full_text))
            
            # Adjust chunk_end to respect sentence boundaries
            chunk_text, actual_end = self._extract_chunk_at_sentence_boundary(
                full_text, sentences, current_pos, chunk_end
            )
            
            if not chunk_text.strip():
                # Skip empty chunks
                current_pos = actual_end
                if current_pos == 0:
                    current_pos += 1  # Avoid infinite loop
                continue
            
            # Determine page numbers for this chunk
            chunk_pages = self._get_page_numbers(char_to_page, current_pos, actual_end)
            
            # Create chunk ID
            chunk_id = f"book_{book_id}_chunk_{chunk_index}"
            
            # Detect language for this chunk
            language = self._detect_language(chunk_text)
            
            # Create chunk object
            chunk = Chunk(
                chunk_id=chunk_id,
                text=chunk_text.strip(),
                page_numbers=chunk_pages,
                start_char=current_pos,
                end_char=actual_end,
                metadata={
                    "language": language,
                    "char_count": len(chunk_text.strip())
                }
            )
            
            chunks.append(chunk)
            chunk_index += 1
            
            # Move to next chunk position with overlap
            # If we've reached the end, stop
            if actual_end >= len(full_text):
                break
            
            # Calculate next position with overlap
            next_pos = actual_end - self.overlap
            
            # Ensure we're making progress (avoid infinite loop)
            if next_pos <= current_pos:
                next_pos = current_pos + 1
            
            current_pos = next_pos
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[tuple]:
        """
        Split text into sentences and track their positions.
        
        Handles both English and Urdu sentence boundaries.
        
        Args:
            text: Input text
            
        Returns:
            List of tuples (sentence_text, start_pos, end_pos)
        """
        # Sentence boundary patterns for English and Urdu
        # English: . ! ? followed by space or end
        # Urdu: ۔ (U+06D4) is the Urdu full stop
        sentence_pattern = r'[.!?۔]\s+|[.!?۔]$'
        
        sentences = []
        last_end = 0
        
        for match in re.finditer(sentence_pattern, text):
            end_pos = match.end()
            sentence_text = text[last_end:end_pos].strip()
            
            if sentence_text:
                sentences.append((sentence_text, last_end, end_pos))
            
            last_end = end_pos
        
        # Add remaining text as final sentence if exists
        if last_end < len(text):
            remaining = text[last_end:].strip()
            if remaining:
                sentences.append((remaining, last_end, len(text)))
        
        return sentences
    
    def _extract_chunk_at_sentence_boundary(
        self,
        text: str,
        sentences: List[tuple],
        start_pos: int,
        target_end: int
    ) -> tuple:
        """
        Extract chunk text respecting sentence boundaries.
        
        Args:
            text: Full text
            sentences: List of (sentence_text, start_pos, end_pos) tuples
            start_pos: Starting position for chunk
            target_end: Target ending position for chunk
            
        Returns:
            Tuple of (chunk_text, actual_end_pos)
        """
        # Find sentences that overlap with our chunk range
        chunk_sentences = []
        actual_end = start_pos
        
        for sentence_text, sent_start, sent_end in sentences:
            # Check if sentence overlaps with our chunk range
            if sent_end <= start_pos:
                continue  # Sentence is before our chunk
            
            if sent_start >= target_end:
                # Sentence starts after our target end
                # Only include if we have no sentences yet (avoid empty chunks)
                if not chunk_sentences:
                    chunk_sentences.append((sentence_text, sent_start, sent_end))
                    actual_end = sent_end
                break
            
            # Include this sentence
            chunk_sentences.append((sentence_text, sent_start, sent_end))
            actual_end = sent_end
            
            # If we've exceeded target size significantly, stop
            if actual_end >= target_end:
                break
        
        # If no sentences found, fall back to character-based chunking
        if not chunk_sentences:
            actual_end = min(target_end, len(text))
            chunk_text = text[start_pos:actual_end]
        else:
            # Combine sentences
            chunk_start = chunk_sentences[0][1]
            chunk_end = chunk_sentences[-1][2]
            chunk_text = text[chunk_start:chunk_end]
            actual_end = chunk_end
        
        return chunk_text, actual_end
    
    def _get_page_numbers(
        self,
        char_to_page: List[int],
        start_pos: int,
        end_pos: int
    ) -> List[int]:
        """
        Get unique page numbers for a character range.
        
        Args:
            char_to_page: List mapping character index to page number
            start_pos: Starting character position
            end_pos: Ending character position
            
        Returns:
            Sorted list of unique page numbers
        """
        if not char_to_page:
            return [1]
        
        # Ensure positions are within bounds
        start_pos = max(0, min(start_pos, len(char_to_page) - 1))
        end_pos = max(start_pos, min(end_pos, len(char_to_page)))
        
        # Get unique page numbers in range
        pages = set()
        for i in range(start_pos, end_pos):
            if i < len(char_to_page):
                pages.add(char_to_page[i])
        
        return sorted(list(pages))
    
    def _detect_language(self, text: str) -> str:
        """
        Detect the primary language of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code: "en" (English), "ur" (Urdu), or "mixed"
        """
        if not text:
            return "en"
        
        has_urdu = self._contains_urdu(text)
        has_english = self._contains_english(text)
        
        if has_urdu and has_english:
            return "mixed"
        elif has_urdu:
            return "ur"
        else:
            return "en"
    
    def _contains_urdu(self, text: str) -> bool:
        """
        Check if text contains Urdu characters.
        
        Urdu uses Arabic script with Unicode range U+0600 to U+06FF.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains Urdu characters
        """
        if not text:
            return False
        
        # Check for Arabic/Urdu Unicode range
        for char in text:
            if '\u0600' <= char <= '\u06FF':
                return True
        return False
    
    def _contains_english(self, text: str) -> bool:
        """
        Check if text contains English characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains English characters
        """
        if not text:
            return False
        
        # Check for ASCII letters
        for char in text:
            if 'a' <= char.lower() <= 'z':
                return True
        return False
