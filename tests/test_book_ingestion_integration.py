"""
Integration tests for the BookIngestionPipeline.

These tests verify the complete pipeline works with real components
(not mocked) using sample PDF files.
"""

import pytest
import os
import tempfile
import shutil
from src.book_ingestion_pipeline import BookIngestionPipeline
from src.pdf_parser import PDFParser
from src.chunking_engine import ChunkingEngine
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.database import Database


class TestBookIngestionIntegration:
    """Integration test suite for BookIngestionPipeline."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def pipeline(self, temp_dir):
        """Create a real BookIngestionPipeline with temporary storage."""
        vector_store_dir = os.path.join(temp_dir, "vector_store")
        db_path = os.path.join(temp_dir, "test.db")
        
        pipeline = BookIngestionPipeline(
            pdf_parser=PDFParser(use_pdfplumber=True),
            chunking_engine=ChunkingEngine(),
            embedding_generator=EmbeddingGenerator(),
            vector_store=VectorStore(storage_dir=vector_store_dir),
            database=Database(db_path=db_path)
        )
        
        return pipeline
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Get path to sample PDF for testing."""
        # Use the sample PDF from the test data directory
        pdf_path = "test_data/sample.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip(f"Sample PDF not found at {pdf_path}")
        
        return pdf_path
    
    def test_end_to_end_ingestion(self, pipeline, sample_pdf_path):
        """Test complete end-to-end book ingestion with real components."""
        # Ingest the book
        result = pipeline.ingest_book(
            sample_pdf_path,
            title="Sample Book",
            book_id="sample-book-1"
        )
        
        # Verify successful ingestion
        assert result["status"] == "completed"
        assert result["book_id"] == "sample-book-1"
        assert result["page_count"] > 0
        assert result["chunk_count"] > 0
        assert result["language"] in ["en", "ur", "mixed"]
        
        # Verify book is in database
        book_status = pipeline.get_book_status("sample-book-1")
        assert book_status is not None
        assert book_status["book_id"] == "sample-book-1"
        assert book_status["title"] == "Sample Book"
        assert book_status["processing_status"] == "completed"
        
        # Verify chunks are in vector store
        chunk_count = pipeline.vector_store.get_chunk_count("sample-book-1")
        assert chunk_count == result["chunk_count"]
        assert chunk_count > 0
    
    def test_multiple_book_ingestion_isolation(self, pipeline, sample_pdf_path):
        """Test that multiple books are processed independently."""
        # Ingest first book
        result1 = pipeline.ingest_book(
            sample_pdf_path,
            title="Book 1",
            book_id="book-1"
        )
        
        # Ingest second book (same PDF, different ID)
        result2 = pipeline.ingest_book(
            sample_pdf_path,
            title="Book 2",
            book_id="book-2"
        )
        
        # Both should succeed
        assert result1["status"] == "completed"
        assert result2["status"] == "completed"
        
        # Verify both books exist in database
        books = pipeline.list_books()
        book_ids = [book["book_id"] for book in books]
        assert "book-1" in book_ids
        assert "book-2" in book_ids
        
        # Verify both have chunks in vector store
        assert pipeline.vector_store.get_chunk_count("book-1") > 0
        assert pipeline.vector_store.get_chunk_count("book-2") > 0
    
    def test_delete_book_removes_all_data(self, pipeline, sample_pdf_path):
        """Test that deleting a book removes all associated data."""
        # Ingest a book
        result = pipeline.ingest_book(
            sample_pdf_path,
            title="Book to Delete",
            book_id="delete-me"
        )
        
        assert result["status"] == "completed"
        
        # Verify book exists
        assert pipeline.get_book_status("delete-me") is not None
        assert pipeline.vector_store.get_chunk_count("delete-me") > 0
        
        # Delete the book
        pipeline.delete_book("delete-me")
        
        # Verify book is removed from database
        assert pipeline.get_book_status("delete-me") is None
        
        # Verify chunks are removed from vector store
        assert pipeline.vector_store.get_chunk_count("delete-me") == 0
    
    def test_ingestion_with_nonexistent_pdf(self, pipeline):
        """Test ingestion fails gracefully with nonexistent PDF."""
        result = pipeline.ingest_book(
            "nonexistent.pdf",
            title="Nonexistent Book",
            book_id="nonexistent"
        )
        
        assert result["status"] == "failed"
        assert "error" in result
        assert result["error_type"] == "PDFParseError"
    
    def test_list_books_returns_all_ingested_books(self, pipeline, sample_pdf_path):
        """Test that list_books returns all ingested books."""
        # Ingest multiple books
        pipeline.ingest_book(sample_pdf_path, title="Book A", book_id="book-a")
        pipeline.ingest_book(sample_pdf_path, title="Book B", book_id="book-b")
        pipeline.ingest_book(sample_pdf_path, title="Book C", book_id="book-c")
        
        # List all books
        books = pipeline.list_books()
        
        # Verify all books are listed
        assert len(books) >= 3
        book_ids = [book["book_id"] for book in books]
        assert "book-a" in book_ids
        assert "book-b" in book_ids
        assert "book-c" in book_ids
    
    def test_ingestion_preserves_metadata(self, pipeline, sample_pdf_path):
        """Test that book metadata is correctly stored and retrieved."""
        result = pipeline.ingest_book(
            sample_pdf_path,
            title="Metadata Test Book",
            book_id="metadata-test"
        )
        
        assert result["status"] == "completed"
        
        # Retrieve book status
        book_status = pipeline.get_book_status("metadata-test")
        
        # Verify metadata
        assert book_status["title"] == "Metadata Test Book"
        assert book_status["filename"] == os.path.basename(sample_pdf_path)
        assert book_status["page_count"] == result["page_count"]
        assert "upload_date" in book_status
        assert "metadata" in book_status
