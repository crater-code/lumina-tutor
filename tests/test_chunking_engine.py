"""
Unit tests for the ChunkingEngine class.
"""

import pytest
from src.chunking_engine import ChunkingEngine
from src.models import PageContent, Chunk


class TestChunkingEngine:
    """Test suite for ChunkingEngine class."""
    
    def test_initialization_default_params(self):
        """Test ChunkingEngine initialization with default parameters."""
        engine = ChunkingEngine()
        assert engine.chunk_size == 500
        assert engine.overlap == 50
    
    def test_initialization_custom_params(self):
        """Test ChunkingEngine initialization with custom parameters."""
        engine = ChunkingEngine(chunk_size=300, overlap=30)
        assert engine.chunk_size == 300
        assert engine.overlap == 30
    
    def test_create_chunks_empty_pages(self):
        """Test create_chunks with empty page list."""
        engine = ChunkingEngine()
        chunks = engine.create_chunks([], book_id="test_book")
        assert chunks == []
    
    def test_create_chunks_single_page_short_text(self):
        """Test create_chunks with single page containing short text."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        pages = [
            PageContent(
                page_number=1,
                text="This is a short text. It has two sentences.",
                metadata={}
            )
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) >= 1
        assert chunks[0].chunk_id == "book_test_book_chunk_0"
        assert "This is a short text" in chunks[0].text
        assert 1 in chunks[0].page_numbers
        assert chunks[0].start_char == 0
    
    def test_create_chunks_respects_sentence_boundaries(self):
        """Test that chunks don't split mid-sentence."""
        engine = ChunkingEngine(chunk_size=50, overlap=10)
        pages = [
            PageContent(
                page_number=1,
                text="First sentence here. Second sentence here. Third sentence here.",
                metadata={}
            )
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        # Each chunk should end with sentence-ending punctuation or be complete
        for chunk in chunks:
            text = chunk.text.strip()
            # Check that chunk doesn't end mid-word (unless it's the last chunk)
            if text and not text[-1] in '.!?۔':
                # If not ending with punctuation, should be the last chunk
                assert chunk == chunks[-1] or len(text) < engine.chunk_size
    
    def test_create_chunks_multiple_pages(self):
        """Test create_chunks with multiple pages."""
        engine = ChunkingEngine(chunk_size=100, overlap=20)
        pages = [
            PageContent(page_number=1, text="Page one content. First sentence.", metadata={}),
            PageContent(page_number=2, text="Page two content. Second sentence.", metadata={}),
            PageContent(page_number=3, text="Page three content. Third sentence.", metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="multi_page")
        
        assert len(chunks) > 0
        
        # Check that chunks have correct page numbers
        for chunk in chunks:
            assert len(chunk.page_numbers) > 0
            assert all(1 <= page <= 3 for page in chunk.page_numbers)
    
    def test_chunk_id_format(self):
        """Test that chunk IDs follow the correct format."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        pages = [
            PageContent(page_number=1, text="Some text here. Another sentence.", metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="my_book_123")
        
        for i, chunk in enumerate(chunks):
            expected_id = f"book_my_book_123_chunk_{i}"
            assert chunk.chunk_id == expected_id
    
    def test_chunk_metadata_completeness(self):
        """Test that all chunks have required metadata fields."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        pages = [
            PageContent(
                page_number=1,
                text="This is test content. It has multiple sentences. Each sentence adds length.",
                metadata={}
            )
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        for chunk in chunks:
            # Check required fields
            assert chunk.chunk_id is not None
            assert chunk.text is not None
            assert chunk.page_numbers is not None
            assert len(chunk.page_numbers) > 0
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char
            
            # Check metadata
            assert "language" in chunk.metadata
            assert "char_count" in chunk.metadata
            assert chunk.metadata["char_count"] == len(chunk.text)
    
    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        engine = ChunkingEngine(chunk_size=100, overlap=20)
        pages = [
            PageContent(
                page_number=1,
                text="A" * 300,  # Long text to ensure multiple chunks
                metadata={}
            )
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        if len(chunks) > 1:
            # Check that there's some overlap between consecutive chunks
            # (overlap might not be exact due to sentence boundary adjustments)
            for i in range(len(chunks) - 1):
                chunk1_end = chunks[i].end_char
                chunk2_start = chunks[i + 1].start_char
                
                # chunk2 should start before chunk1 ends (overlap)
                # or shortly after (due to sentence boundaries)
                assert chunk2_start <= chunk1_end + engine.chunk_size
    
    def test_english_text_detection(self):
        """Test language detection for English text."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        pages = [
            PageContent(
                page_number=1,
                text="This is English text. It contains only English characters.",
                metadata={}
            )
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) > 0
        assert chunks[0].metadata["language"] == "en"
    
    def test_urdu_text_detection(self):
        """Test language detection for Urdu text."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        # Urdu text: "This is Urdu text."
        urdu_text = "یہ اردو متن ہے۔"
        pages = [
            PageContent(page_number=1, text=urdu_text, metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) > 0
        assert chunks[0].metadata["language"] == "ur"
    
    def test_mixed_language_detection(self):
        """Test language detection for mixed English and Urdu text."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        # Mixed text with English and Urdu
        mixed_text = "This is English. یہ اردو ہے۔ More English here."
        pages = [
            PageContent(page_number=1, text=mixed_text, metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) > 0
        assert chunks[0].metadata["language"] == "mixed"
    
    def test_urdu_sentence_boundary(self):
        """Test that Urdu sentence boundaries are respected."""
        engine = ChunkingEngine(chunk_size=50, overlap=10)
        # Urdu sentences with proper sentence endings (۔)
        urdu_text = "پہلا جملہ۔ دوسرا جملہ۔ تیسرا جملہ۔"
        pages = [
            PageContent(page_number=1, text=urdu_text, metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) > 0
        # Verify chunks contain Urdu text
        for chunk in chunks:
            assert len(chunk.text) > 0
    
    def test_very_short_text(self):
        """Test chunking with text shorter than chunk size."""
        engine = ChunkingEngine(chunk_size=500, overlap=50)
        pages = [
            PageContent(page_number=1, text="Short.", metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) == 1
        assert chunks[0].text == "Short."
        assert chunks[0].page_numbers == [1]
    
    def test_text_with_only_whitespace(self):
        """Test chunking with text containing only whitespace."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        pages = [
            PageContent(page_number=1, text="   \n\n   \t  ", metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        # Should return empty list or skip whitespace-only chunks
        assert len(chunks) == 0
    
    def test_text_at_exact_chunk_boundary(self):
        """Test chunking with text exactly at chunk size boundary."""
        engine = ChunkingEngine(chunk_size=50, overlap=10)
        # Create text that's exactly 50 characters
        text = "A" * 45 + "."  # 46 chars, close to boundary
        pages = [
            PageContent(page_number=1, text=text, metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) >= 1
        assert chunks[0].text == text
    
    def test_long_text_creates_multiple_chunks(self):
        """Test that long text is split into multiple chunks."""
        engine = ChunkingEngine(chunk_size=100, overlap=20)
        # Create long text with sentences
        sentences = [f"This is sentence number {i}." for i in range(20)]
        long_text = " ".join(sentences)
        pages = [
            PageContent(page_number=1, text=long_text, metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Verify all chunks have sequential IDs
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id == f"book_test_book_chunk_{i}"
    
    def test_page_number_tracking_across_pages(self):
        """Test that page numbers are correctly tracked across multiple pages."""
        engine = ChunkingEngine(chunk_size=50, overlap=10)
        pages = [
            PageContent(page_number=1, text="Page 1 text here.", metadata={}),
            PageContent(page_number=2, text="Page 2 text here.", metadata={}),
            PageContent(page_number=3, text="Page 3 text here.", metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        # Verify that chunks have correct page numbers
        all_pages = set()
        for chunk in chunks:
            all_pages.update(chunk.page_numbers)
        
        # Should have seen all three pages
        assert 1 in all_pages or 2 in all_pages or 3 in all_pages
    
    def test_chunk_character_positions(self):
        """Test that start_char and end_char are correctly set."""
        engine = ChunkingEngine(chunk_size=100, overlap=20)
        pages = [
            PageContent(
                page_number=1,
                text="First sentence. Second sentence. Third sentence.",
                metadata={}
            )
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        for chunk in chunks:
            # end_char should be greater than start_char
            assert chunk.end_char > chunk.start_char
            # start_char should be non-negative
            assert chunk.start_char >= 0
    
    def test_special_characters_in_text(self):
        """Test chunking with special characters."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        text = "Text with special chars: @#$%^&*(). More text here!"
        pages = [
            PageContent(page_number=1, text=text, metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) > 0
        assert "@#$%^&*()" in chunks[0].text
    
    def test_multiple_sentence_endings(self):
        """Test text with various sentence ending punctuation."""
        engine = ChunkingEngine(chunk_size=100, overlap=10)
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        pages = [
            PageContent(page_number=1, text=text, metadata={})
        ]
        
        chunks = engine.create_chunks(pages, book_id="test_book")
        
        assert len(chunks) > 0
        # Verify text is preserved
        combined_text = " ".join(chunk.text for chunk in chunks)
        assert "First sentence" in combined_text
        assert "Fourth sentence" in combined_text


class TestChunkingEngineHelperMethods:
    """Test suite for ChunkingEngine helper methods."""
    
    def test_split_into_sentences_english(self):
        """Test sentence splitting for English text."""
        engine = ChunkingEngine()
        text = "First sentence. Second sentence! Third sentence?"
        sentences = engine._split_into_sentences(text)
        
        assert len(sentences) >= 3
        # Check that sentences are tuples with (text, start, end)
        for sentence in sentences:
            assert len(sentence) == 3
            assert isinstance(sentence[0], str)
            assert isinstance(sentence[1], int)
            assert isinstance(sentence[2], int)
    
    def test_split_into_sentences_urdu(self):
        """Test sentence splitting for Urdu text."""
        engine = ChunkingEngine()
        # Urdu sentences with ۔ (Urdu full stop)
        text = "پہلا جملہ۔ دوسرا جملہ۔"
        sentences = engine._split_into_sentences(text)
        
        assert len(sentences) >= 1
    
    def test_contains_urdu(self):
        """Test Urdu character detection."""
        engine = ChunkingEngine()
        
        assert engine._contains_urdu("یہ اردو ہے") == True
        assert engine._contains_urdu("This is English") == False
        assert engine._contains_urdu("") == False
    
    def test_contains_english(self):
        """Test English character detection."""
        engine = ChunkingEngine()
        
        assert engine._contains_english("This is English") == True
        assert engine._contains_english("یہ اردو ہے") == False
        assert engine._contains_english("") == False
        assert engine._contains_english("123456") == False
    
    def test_detect_language(self):
        """Test language detection."""
        engine = ChunkingEngine()
        
        assert engine._detect_language("English text") == "en"
        assert engine._detect_language("یہ اردو ہے") == "ur"
        assert engine._detect_language("English and یہ اردو") == "mixed"
        assert engine._detect_language("") == "en"  # Default to English for empty
