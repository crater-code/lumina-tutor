"""
Unit tests for the BookIngestionPipeline class.

These tests verify the orchestration of the complete book ingestion process,
including error handling and status updates.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch
from src.book_ingestion_pipeline import BookIngestionPipeline
from src.models import PageContent, Chunk
from src.exceptions import PDFParseError, FileSizeError, NoTextError, RetrievalError
import numpy as np


class TestBookIngestionPipeline:
    """Test suite for BookIngestionPipeline class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_components(self):
        """Create mock components for the pipeline."""
        pdf_parser = Mock()
        chunking_engine = Mock()
        embedding_generator = Mock()
        vector_store = Mock()
        database = Mock()
        
        return {
            "pdf_parser": pdf_parser,
            "chunking_engine": chunking_engine,
            "embedding_generator": embedding_generator,
            "vector_store": vector_store,
            "database": database
        }
    
    @pytest.fixture
    def pipeline(self, mock_components):
        """Create a BookIngestionPipeline with mocked components."""
        return BookIngestionPipeline(
            pdf_parser=mock_components["pdf_parser"],
            chunking_engine=mock_components["chunking_engine"],
            embedding_generator=mock_components["embedding_generator"],
            vector_store=mock_components["vector_store"],
            database=mock_components["database"]
        )
    
    def test_successful_ingestion(self, pipeline, mock_components):
        """Test successful book ingestion through the complete pipeline."""
        # Setup mock data
        pages = [
            PageContent(1, "This is page 1 content.", {"language": "en"}),
            PageContent(2, "This is page 2 content.", {"language": "en"})
        ]
        
        chunks = [
            Chunk("book_test_chunk_0", "This is page 1 content.", [1], 0, 23, {}),
            Chunk("book_test_chunk_1", "This is page 2 content.", [2], 24, 47, {})
        ]
        
        embeddings = np.random.rand(2, 384).astype(np.float32)
        
        # Configure mocks
        mock_components["pdf_parser"].extract_text.return_value = pages
        mock_components["chunking_engine"].create_chunks.return_value = chunks
        mock_components["embedding_generator"].generate_batch_embeddings.return_value = embeddings
        mock_components["database"].book_exists.return_value = True
        
        # Execute ingestion
        result = pipeline.ingest_book("test.pdf", title="Test Book", book_id="test-id")
        
        # Verify result
        assert result["status"] == "completed"
        assert result["book_id"] == "test-id"
        assert result["page_count"] == 2
        assert result["chunk_count"] == 2
        assert result["language"] == "en"
        
        # Verify all components were called
        mock_components["pdf_parser"].extract_text.assert_called_once_with("test.pdf")
        mock_components["chunking_engine"].create_chunks.assert_called_once()
        mock_components["embedding_generator"].generate_batch_embeddings.assert_called_once()
        mock_components["vector_store"].add_chunks.assert_called_once()
        
        # Verify database operations
        mock_components["database"].create_book.assert_called_once()
        assert mock_components["database"].update_book_status.call_count == 2  # processing, completed
    
    def test_ingestion_with_auto_generated_book_id(self, pipeline, mock_components):
        """Test that book_id is auto-generated if not provided."""
        pages = [PageContent(1, "Content", {"language": "en"})]
        chunks = [Chunk("book_auto_chunk_0", "Content", [1], 0, 7, {})]
        embeddings = np.random.rand(1, 384).astype(np.float32)
        
        mock_components["pdf_parser"].extract_text.return_value = pages
        mock_components["chunking_engine"].create_chunks.return_value = chunks
        mock_components["embedding_generator"].generate_batch_embeddings.return_value = embeddings
        mock_components["database"].book_exists.return_value = True
        
        result = pipeline.ingest_book("test.pdf")
        
        # Verify a book_id was generated
        assert "book_id" in result
        assert result["book_id"] is not None
        assert len(result["book_id"]) > 0
    
    def test_ingestion_with_auto_generated_title(self, pipeline, mock_components):
        """Test that title is derived from filename if not provided."""
        pages = [PageContent(1, "Content", {"language": "en"})]
        chunks = [Chunk("book_test_chunk_0", "Content", [1], 0, 7, {})]
        embeddings = np.random.rand(1, 384).astype(np.float32)
        
        mock_components["pdf_parser"].extract_text.return_value = pages
        mock_components["chunking_engine"].create_chunks.return_value = chunks
        mock_components["embedding_generator"].generate_batch_embeddings.return_value = embeddings
        mock_components["database"].book_exists.return_value = True
        
        result = pipeline.ingest_book("/path/to/my_book.pdf", book_id="test-id")
        
        # Verify database was called with filename as title
        call_args = mock_components["database"].create_book.call_args
        assert call_args[1]["title"] == "my_book.pdf"
    
    def test_ingestion_handles_pdf_parse_error(self, pipeline, mock_components):
        """Test that PDFParseError is handled gracefully."""
        mock_components["pdf_parser"].extract_text.side_effect = PDFParseError("Cannot parse PDF")
        mock_components["database"].book_exists.return_value = False
        
        result = pipeline.ingest_book("bad.pdf", book_id="test-id")
        
        assert result["status"] == "failed"
        assert result["book_id"] == "test-id"
        assert "PDF processing error" in result["error"]
        assert result["error_type"] == "PDFParseError"
    
    def test_ingestion_handles_file_size_error(self, pipeline, mock_components):
        """Test that FileSizeError is handled gracefully."""
        mock_components["pdf_parser"].extract_text.side_effect = FileSizeError("PDF exceeds 450 pages")
        mock_components["database"].book_exists.return_value = True
        
        result = pipeline.ingest_book("large.pdf", book_id="test-id")
        
        assert result["status"] == "failed"
        assert "PDF processing error" in result["error"]
        assert result["error_type"] == "FileSizeError"
        
        # Verify status was updated to failed
        mock_components["database"].update_book_status.assert_called_with("test-id", "failed")
    
    def test_ingestion_handles_no_text_error(self, pipeline, mock_components):
        """Test that NoTextError is handled gracefully."""
        mock_components["pdf_parser"].extract_text.side_effect = NoTextError("No extractable text")
        mock_components["database"].book_exists.return_value = True
        
        result = pipeline.ingest_book("empty.pdf", book_id="test-id")
        
        assert result["status"] == "failed"
        assert "PDF processing error" in result["error"]
        assert result["error_type"] == "NoTextError"
    
    def test_ingestion_handles_retrieval_error(self, pipeline, mock_components):
        """Test that RetrievalError during storage is handled gracefully."""
        pages = [PageContent(1, "Content", {"language": "en"})]
        chunks = [Chunk("book_test_chunk_0", "Content", [1], 0, 7, {})]
        embeddings = np.random.rand(1, 384).astype(np.float32)
        
        mock_components["pdf_parser"].extract_text.return_value = pages
        mock_components["chunking_engine"].create_chunks.return_value = chunks
        mock_components["embedding_generator"].generate_batch_embeddings.return_value = embeddings
        mock_components["vector_store"].add_chunks.side_effect = RetrievalError("Storage failed")
        mock_components["database"].book_exists.return_value = True
        
        result = pipeline.ingest_book("test.pdf", book_id="test-id")
        
        assert result["status"] == "failed"
        assert "Storage error" in result["error"]
        assert result["error_type"] == "RetrievalError"
        
        # Verify cleanup was attempted
        mock_components["vector_store"].delete_book.assert_called_once_with("test-id")
        mock_components["database"].update_book_status.assert_called_with("test-id", "failed")
    
    def test_ingestion_handles_no_chunks_created(self, pipeline, mock_components):
        """Test that error is raised when no chunks are created."""
        pages = [PageContent(1, "Content", {"language": "en"})]
        
        mock_components["pdf_parser"].extract_text.return_value = pages
        mock_components["chunking_engine"].create_chunks.return_value = []  # No chunks
        mock_components["database"].book_exists.return_value = True
        
        result = pipeline.ingest_book("test.pdf", book_id="test-id")
        
        assert result["status"] == "failed"
        assert "No chunks were created" in result["error"]
    
    def test_ingestion_detects_urdu_language(self, pipeline, mock_components):
        """Test that Urdu language is correctly detected."""
        pages = [
            PageContent(1, "یہ اردو متن ہے", {"language": "ur"}),
            PageContent(2, "مزید اردو", {"language": "ur"})
        ]
        chunks = [Chunk("book_test_chunk_0", "یہ اردو متن ہے", [1], 0, 14, {})]
        embeddings = np.random.rand(1, 384).astype(np.float32)
        
        mock_components["pdf_parser"].extract_text.return_value = pages
        mock_components["chunking_engine"].create_chunks.return_value = chunks
        mock_components["embedding_generator"].generate_batch_embeddings.return_value = embeddings
        mock_components["database"].book_exists.return_value = True
        
        result = pipeline.ingest_book("urdu.pdf", book_id="test-id")
        
        assert result["status"] == "completed"
        assert result["language"] == "ur"
    
    def test_ingestion_detects_mixed_language(self, pipeline, mock_components):
        """Test that mixed language is correctly detected."""
        pages = [
            PageContent(1, "English text", {"language": "en"}),
            PageContent(2, "اردو متن", {"language": "ur"}),
            PageContent(3, "Mixed content", {"language": "mixed"})
        ]
        chunks = [Chunk("book_test_chunk_0", "Content", [1], 0, 7, {})]
        embeddings = np.random.rand(1, 384).astype(np.float32)
        
        mock_components["pdf_parser"].extract_text.return_value = pages
        mock_components["chunking_engine"].create_chunks.return_value = chunks
        mock_components["embedding_generator"].generate_batch_embeddings.return_value = embeddings
        mock_components["database"].book_exists.return_value = True
        
        result = pipeline.ingest_book("mixed.pdf", book_id="test-id")
        
        assert result["status"] == "completed"
        assert result["language"] == "mixed"
    
    def test_delete_book(self, pipeline, mock_components):
        """Test deleting a book and its associated data."""
        pipeline.delete_book("test-id")
        
        # Verify both vector store and database were called
        mock_components["vector_store"].delete_book.assert_called_once_with("test-id")
        mock_components["database"].delete_book.assert_called_once_with("test-id")
    
    def test_delete_book_handles_errors_gracefully(self, pipeline, mock_components):
        """Test that delete_book continues even if components fail."""
        mock_components["vector_store"].delete_book.side_effect = Exception("Vector store error")
        mock_components["database"].delete_book.side_effect = Exception("Database error")
        
        # Should not raise exception
        pipeline.delete_book("test-id")
        
        # Both deletes should have been attempted
        mock_components["vector_store"].delete_book.assert_called_once()
        mock_components["database"].delete_book.assert_called_once()
    
    def test_get_book_status(self, pipeline, mock_components):
        """Test retrieving book status."""
        expected_status = {
            "book_id": "test-id",
            "title": "Test Book",
            "processing_status": "completed"
        }
        mock_components["database"].get_book.return_value = expected_status
        
        result = pipeline.get_book_status("test-id")
        
        assert result == expected_status
        mock_components["database"].get_book.assert_called_once_with("test-id")
    
    def test_list_books(self, pipeline, mock_components):
        """Test listing all books."""
        expected_books = [
            {"book_id": "book1", "title": "Book 1"},
            {"book_id": "book2", "title": "Book 2"}
        ]
        mock_components["database"].list_books.return_value = expected_books
        
        result = pipeline.list_books()
        
        assert result == expected_books
        mock_components["database"].list_books.assert_called_once()
    
    def test_status_updates_during_ingestion(self, pipeline, mock_components):
        """Test that status is updated at each stage of ingestion."""
        pages = [PageContent(1, "Content", {"language": "en"})]
        chunks = [Chunk("book_test_chunk_0", "Content", [1], 0, 7, {})]
        embeddings = np.random.rand(1, 384).astype(np.float32)
        
        mock_components["pdf_parser"].extract_text.return_value = pages
        mock_components["chunking_engine"].create_chunks.return_value = chunks
        mock_components["embedding_generator"].generate_batch_embeddings.return_value = embeddings
        mock_components["database"].book_exists.return_value = True
        
        pipeline.ingest_book("test.pdf", book_id="test-id")
        
        # Verify status updates: processing, then completed
        calls = mock_components["database"].update_book_status.call_args_list
        assert len(calls) == 2
        assert calls[0][0] == ("test-id", "processing")
        assert calls[1][0] == ("test-id", "completed")
