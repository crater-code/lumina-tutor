"""
Unit tests for API endpoints.

This module tests the FastAPI endpoints to ensure they handle
requests correctly and return appropriate responses.
"""

import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from src.main import app
from src.models import Chunk, Response


# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check and root endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Book-Bounded Tutoring Chatbot API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "book-bounded-tutor"


class TestBookUploadEndpoint:
    """Test book upload endpoint"""
    
    @patch('src.main.book_ingestion_pipeline')
    def test_upload_pdf_success(self, mock_pipeline):
        """Test successful PDF upload"""
        # Mock the ingestion pipeline
        mock_pipeline.ingest_book.return_value = {
            "book_id": "test-book-123",
            "status": "completed",
            "page_count": 10,
            "chunk_count": 50
        }
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'%PDF-1.4 fake pdf content')
            tmp_path = tmp_file.name
        
        try:
            # Upload the file
            with open(tmp_path, 'rb') as f:
                response = client.post(
                    "/api/books/upload",
                    files={"file": ("test.pdf", f, "application/pdf")},
                    data={"title": "Test Book"}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert "book_id" in data
            assert data["page_count"] == 10
            assert data["chunk_count"] == 50
        
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_upload_non_pdf_fails(self):
        """Test that non-PDF files are rejected"""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b'This is not a PDF')
            tmp_path = tmp_file.name
        
        try:
            # Try to upload the file
            with open(tmp_path, 'rb') as f:
                response = client.post(
                    "/api/books/upload",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 400
            assert "Only PDF files are supported" in response.json()["detail"]
        
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestListBooksEndpoint:
    """Test list books endpoint"""
    
    @patch('src.main.database')
    def test_list_books_empty(self, mock_db):
        """Test listing books when none exist"""
        mock_db.list_books.return_value = []
        
        response = client.get("/api/books")
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('src.main.database')
    def test_list_books_with_data(self, mock_db):
        """Test listing books with data"""
        mock_db.list_books.return_value = [
            {
                "book_id": "book-1",
                "title": "Test Book 1",
                "filename": "test1.pdf",
                "upload_date": "2024-01-01T00:00:00",
                "page_count": 10,
                "processing_status": "completed",
                "language": "en",
                "metadata": {}
            },
            {
                "book_id": "book-2",
                "title": "Test Book 2",
                "filename": "test2.pdf",
                "upload_date": "2024-01-02T00:00:00",
                "page_count": 20,
                "processing_status": "processing",
                "language": "ur",
                "metadata": {}
            }
        ]
        
        response = client.get("/api/books")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["book_id"] == "book-1"
        assert data[1]["book_id"] == "book-2"


class TestDeleteBookEndpoint:
    """Test delete book endpoint"""
    
    @patch('src.main.database')
    @patch('src.main.book_ingestion_pipeline')
    def test_delete_book_success(self, mock_pipeline, mock_db):
        """Test successful book deletion"""
        mock_db.get_book.return_value = {
            "book_id": "book-1",
            "title": "Test Book",
            "filename": "test.pdf",
            "upload_date": "2024-01-01T00:00:00",
            "page_count": 10,
            "processing_status": "completed",
            "language": "en",
            "metadata": {}
        }
        
        response = client.delete("/api/books/book-1")
        assert response.status_code == 200
        data = response.json()
        assert data["book_id"] == "book-1"
        assert "deleted successfully" in data["message"]
        
        # Verify pipeline delete was called
        mock_pipeline.delete_book.assert_called_once_with("book-1")
    
    @patch('src.main.database')
    def test_delete_nonexistent_book(self, mock_db):
        """Test deleting a book that doesn't exist"""
        mock_db.get_book.return_value = None
        
        response = client.delete("/api/books/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestChatEndpoint:
    """Test chat endpoint"""
    
    @patch('src.main.database')
    @patch('src.main.retrieval_system')
    @patch('src.main.chatbot_engine')
    @patch('src.main.response_validator')
    def test_chat_with_chunks(self, mock_validator, mock_chatbot, mock_retrieval, mock_db):
        """Test chat with successful chunk retrieval"""
        # Mock database
        mock_db.get_book.return_value = {
            "book_id": "book-1",
            "processing_status": "completed"
        }
        mock_db.get_chat_session.return_value = None
        mock_db.create_chat_session.return_value = None
        mock_db.create_message.return_value = None
        
        # Mock retrieval
        mock_chunk = Chunk(
            chunk_id="chunk-1",
            text="This is test content",
            page_numbers=[1],
            start_char=0,
            end_char=20,
            metadata={}
        )
        mock_retrieval.retrieve_chunks.return_value = [mock_chunk]
        
        # Mock chatbot
        mock_response = Response(
            text="Based on the book, this is test content.",
            chunk_ids=["chunk-1"],
            is_refusal=False,
            metadata={}
        )
        mock_chatbot.generate_response.return_value = mock_response
        
        # Mock validator
        from src.models import ValidationResult
        mock_validator.validate_response.return_value = ValidationResult(
            is_valid=True,
            confidence=0.9,
            issues=[]
        )
        
        # Make request
        response = client.post(
            "/api/chat",
            json={
                "query": "What is this about?",
                "book_id": "book-1",
                "user_age": 10,
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["chunk_ids"] == ["chunk-1"]
        assert data["is_refusal"] is False
        assert "session_id" in data
    
    @patch('src.main.database')
    @patch('src.main.retrieval_system')
    @patch('src.main.chatbot_engine')
    def test_chat_no_chunks_refusal(self, mock_chatbot, mock_retrieval, mock_db):
        """Test chat when no relevant chunks are found"""
        # Mock database
        mock_db.get_book.return_value = {
            "book_id": "book-1",
            "processing_status": "completed"
        }
        mock_db.get_chat_session.return_value = None
        mock_db.create_chat_session.return_value = None
        mock_db.create_message.return_value = None
        
        # Mock retrieval - no chunks
        mock_retrieval.retrieve_chunks.return_value = []
        
        # Mock chatbot refusal
        mock_response = Response(
            text="I couldn't find information about that in this book.",
            chunk_ids=[],
            is_refusal=True,
            metadata={}
        )
        mock_chatbot.generate_refusal.return_value = mock_response
        
        # Make request
        response = client.post(
            "/api/chat",
            json={
                "query": "What is quantum mechanics?",
                "book_id": "book-1",
                "user_age": 10,
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_refusal"] is True
        assert data["chunk_ids"] == []
    
    @patch('src.main.database')
    def test_chat_book_not_found(self, mock_db):
        """Test chat with nonexistent book"""
        mock_db.get_book.return_value = None
        
        response = client.post(
            "/api/chat",
            json={
                "query": "Test query",
                "book_id": "nonexistent",
                "user_age": 10,
                "language": "en"
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_chat_invalid_age(self):
        """Test chat with invalid age"""
        response = client.post(
            "/api/chat",
            json={
                "query": "Test query",
                "book_id": "book-1",
                "user_age": 3,  # Too young
                "language": "en"
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestChatHistoryEndpoint:
    """Test chat history endpoint"""
    
    @patch('src.main.database')
    def test_get_chat_history_success(self, mock_db):
        """Test retrieving chat history"""
        mock_db.get_chat_session.return_value = {
            "session_id": "session-1",
            "book_id": "book-1",
            "user_age": 10,
            "created_at": "2024-01-01T00:00:00"
        }
        
        mock_db.list_messages_by_session.return_value = [
            {
                "message_id": "msg-1",
                "session_id": "session-1",
                "role": "user",
                "content": "What is this?",
                "chunk_ids": [],
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "message_id": "msg-2",
                "session_id": "session-1",
                "role": "assistant",
                "content": "This is a test.",
                "chunk_ids": ["chunk-1"],
                "timestamp": "2024-01-01T00:00:01"
            }
        ]
        
        response = client.get("/api/chat/history/session-1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["role"] == "user"
        assert data[1]["role"] == "assistant"
    
    @patch('src.main.database')
    def test_get_chat_history_not_found(self, mock_db):
        """Test retrieving history for nonexistent session"""
        mock_db.get_chat_session.return_value = None
        
        response = client.get("/api/chat/history/nonexistent")
        assert response.status_code == 404


class TestGetChunkEndpoint:
    """Test get chunk endpoint"""
    
    @patch('src.main.database')
    def test_get_chunk_success(self, mock_db):
        """Test retrieving chunk content"""
        mock_db.get_chunk.return_value = {
            "chunk_id": "chunk-1",
            "book_id": "book-1",
            "text": "This is chunk content",
            "page_numbers": [1, 2],
            "start_char": 0,
            "end_char": 20,
            "metadata": {}
        }
        
        response = client.get("/api/chunks/chunk-1")
        assert response.status_code == 200
        data = response.json()
        assert data["chunk_id"] == "chunk-1"
        assert data["text"] == "This is chunk content"
        assert data["page_numbers"] == [1, 2]
    
    @patch('src.main.database')
    def test_get_chunk_not_found(self, mock_db):
        """Test retrieving nonexistent chunk"""
        mock_db.get_chunk.return_value = None
        
        response = client.get("/api/chunks/nonexistent")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
