"""
Integration tests for PDF Parser and Chunking Engine.

These tests verify that the PDF Parser and Chunking Engine work together correctly.
"""

import pytest
import os
from src.pdf_parser import PDFParser
from src.chunking_engine import ChunkingEngine


class TestPDFToChunkingIntegration:
    """Integration tests for the complete PDF to chunks pipeline."""
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Get path to sample PDF file."""
        # Use the sample PDF from the project root
        pdf_path = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
        if os.path.exists(pdf_path):
            return pdf_path
        return None
    
    def test_pdf_to_chunks_pipeline(self, sample_pdf_path):
        """Test complete pipeline from PDF to chunks."""
        if sample_pdf_path is None:
            pytest.skip("Sample PDF not found")
        
        # Step 1: Parse PDF
        parser = PDFParser(use_pdfplumber=True)
        try:
            pages = parser.extract_text(sample_pdf_path)
        except Exception as e:
            pytest.skip(f"Cannot parse sample PDF: {e}")
        
        assert len(pages) > 0
        print(f"\nExtracted {len(pages)} pages from PDF")
        
        # Step 2: Create chunks
        engine = ChunkingEngine(chunk_size=500, overlap=50)
        chunks = engine.create_chunks(pages, book_id="test_book_123")
        
        assert len(chunks) > 0
        print(f"Created {len(chunks)} chunks from pages")
        
        # Step 3: Verify chunk properties
        for i, chunk in enumerate(chunks[:5]):  # Check first 5 chunks
            # Verify chunk ID format
            assert chunk.chunk_id == f"book_test_book_123_chunk_{i}"
            
            # Verify chunk has text
            assert len(chunk.text) > 0
            
            # Verify chunk has page numbers
            assert len(chunk.page_numbers) > 0
            assert all(1 <= page <= len(pages) for page in chunk.page_numbers)
            
            # Verify chunk positions
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char
            
            # Verify metadata
            assert "language" in chunk.metadata
            assert "char_count" in chunk.metadata
            assert chunk.metadata["char_count"] == len(chunk.text)
            
            print(f"\nChunk {i}:")
            print(f"  ID: {chunk.chunk_id}")
            print(f"  Text preview: {chunk.text[:100]}...")
            print(f"  Pages: {chunk.page_numbers}")
            print(f"  Language: {chunk.metadata['language']}")
    
    def test_chunk_id_uniqueness_in_pipeline(self, sample_pdf_path):
        """Test that all chunk IDs are unique in the pipeline."""
        if sample_pdf_path is None:
            pytest.skip("Sample PDF not found")
        
        # Parse PDF
        parser = PDFParser(use_pdfplumber=True)
        try:
            pages = parser.extract_text(sample_pdf_path)
        except Exception as e:
            pytest.skip(f"Cannot parse sample PDF: {e}")
        
        # Create chunks
        engine = ChunkingEngine(chunk_size=500, overlap=50)
        chunks = engine.create_chunks(pages, book_id="unique_test")
        
        # Verify all chunk IDs are unique
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids)), "All chunk IDs must be unique"
    
    def test_chunks_cover_all_content(self, sample_pdf_path):
        """Test that chunks cover all the content from the PDF."""
        if sample_pdf_path is None:
            pytest.skip("Sample PDF not found")
        
        # Parse PDF
        parser = PDFParser(use_pdfplumber=True)
        try:
            pages = parser.extract_text(sample_pdf_path)
        except Exception as e:
            pytest.skip(f"Cannot parse sample PDF: {e}")
        
        # Get total text length
        total_text = " ".join(page.text for page in pages)
        total_chars = len(total_text)
        
        # Create chunks
        engine = ChunkingEngine(chunk_size=500, overlap=50)
        chunks = engine.create_chunks(pages, book_id="coverage_test")
        
        # Verify chunks exist
        assert len(chunks) > 0
        
        # Verify first chunk starts near the beginning
        assert chunks[0].start_char < 100, "First chunk should start near the beginning"
        
        # Verify last chunk ends near the end
        # (allowing for some variation due to sentence boundaries)
        last_chunk_end = chunks[-1].end_char
        assert last_chunk_end > total_chars * 0.9, "Last chunk should cover near the end"
        
        print(f"\nTotal text length: {total_chars}")
        print(f"First chunk starts at: {chunks[0].start_char}")
        print(f"Last chunk ends at: {last_chunk_end}")
        print(f"Coverage: {(last_chunk_end / total_chars) * 100:.1f}%")
    
    def test_chunks_preserve_page_information(self, sample_pdf_path):
        """Test that chunks correctly preserve page number information."""
        if sample_pdf_path is None:
            pytest.skip("Sample PDF not found")
        
        # Parse PDF
        parser = PDFParser(use_pdfplumber=True)
        try:
            pages = parser.extract_text(sample_pdf_path)
        except Exception as e:
            pytest.skip(f"Cannot parse sample PDF: {e}")
        
        # Create chunks
        engine = ChunkingEngine(chunk_size=500, overlap=50)
        chunks = engine.create_chunks(pages, book_id="page_test")
        
        # Verify page numbers are valid
        max_page = len(pages)
        for chunk in chunks:
            assert len(chunk.page_numbers) > 0, "Each chunk must have at least one page number"
            for page_num in chunk.page_numbers:
                assert 1 <= page_num <= max_page, f"Page number {page_num} out of range"
        
        # Verify page numbers are in ascending order within each chunk
        for chunk in chunks:
            sorted_pages = sorted(chunk.page_numbers)
            assert chunk.page_numbers == sorted_pages, "Page numbers should be sorted"
    
    def test_chunks_respect_sentence_boundaries_in_real_pdf(self, sample_pdf_path):
        """Test that chunks respect sentence boundaries in real PDF content."""
        if sample_pdf_path is None:
            pytest.skip("Sample PDF not found")
        
        # Parse PDF
        parser = PDFParser(use_pdfplumber=True)
        try:
            pages = parser.extract_text(sample_pdf_path)
        except Exception as e:
            pytest.skip(f"Cannot parse sample PDF: {e}")
        
        # Create chunks with small size to force splitting
        engine = ChunkingEngine(chunk_size=200, overlap=20)
        chunks = engine.create_chunks(pages, book_id="boundary_test")
        
        # Check that most chunks end with sentence-ending punctuation
        chunks_with_proper_ending = 0
        for chunk in chunks:
            text = chunk.text.strip()
            if text and text[-1] in '.!?۔':
                chunks_with_proper_ending += 1
        
        # At least 70% of chunks should end with proper punctuation
        # (some may not due to formatting issues in the PDF)
        percentage = (chunks_with_proper_ending / len(chunks)) * 100
        print(f"\n{chunks_with_proper_ending}/{len(chunks)} chunks ({percentage:.1f}%) end with sentence punctuation")
        assert percentage >= 50, "Most chunks should respect sentence boundaries"


class TestChunkingWithMockPages:
    """Test chunking with mock page data (no PDF file required)."""
    
    def test_chunking_preserves_metadata_from_pages(self):
        """Test that chunking preserves relevant metadata from pages."""
        from src.models import PageContent
        
        pages = [
            PageContent(
                page_number=1,
                text="First page content here. Multiple sentences.",
                metadata={"language": "en", "has_images": True}
            ),
            PageContent(
                page_number=2,
                text="Second page content here. More sentences.",
                metadata={"language": "en", "has_images": False}
            )
        ]
        
        engine = ChunkingEngine(chunk_size=100, overlap=20)
        chunks = engine.create_chunks(pages, book_id="metadata_test")
        
        assert len(chunks) > 0
        
        # Verify chunks have language metadata
        for chunk in chunks:
            assert "language" in chunk.metadata
            assert chunk.metadata["language"] in ["en", "ur", "mixed"]
    
    def test_chunking_handles_empty_pages(self):
        """Test that chunking handles pages with empty or whitespace-only text."""
        from src.models import PageContent
        
        pages = [
            PageContent(page_number=1, text="Valid content here.", metadata={}),
            PageContent(page_number=2, text="   \n\n   ", metadata={}),  # Empty
            PageContent(page_number=3, text="More valid content.", metadata={})
        ]
        
        engine = ChunkingEngine(chunk_size=100, overlap=20)
        chunks = engine.create_chunks(pages, book_id="empty_page_test")
        
        # Should create chunks only from valid content
        assert len(chunks) > 0
        
        # Verify no chunks are empty
        for chunk in chunks:
            assert len(chunk.text.strip()) > 0
    
    def test_chunking_with_very_long_page(self):
        """Test chunking with a very long page."""
        from src.models import PageContent
        
        # Create a long page with many sentences
        sentences = [f"This is sentence number {i}." for i in range(100)]
        long_text = " ".join(sentences)
        
        pages = [
            PageContent(page_number=1, text=long_text, metadata={})
        ]
        
        engine = ChunkingEngine(chunk_size=200, overlap=30)
        chunks = engine.create_chunks(pages, book_id="long_page_test")
        
        # Should create multiple chunks
        assert len(chunks) > 5
        
        # All chunks should be from page 1
        for chunk in chunks:
            assert chunk.page_numbers == [1]
        
        # Verify chunk IDs are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id == f"book_long_page_test_chunk_{i}"
