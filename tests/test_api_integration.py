"""
Integration tests for API endpoints.

This module tests the complete flow of the API endpoints with real
components (not mocked) to ensure end-to-end functionality.
"""

import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from src.main import app, database, vector_store


# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def cleanup_test_data():
    """Cleanup test data after each test"""
    yield
    
    # Clean up test books from database
    books = database.list_books()
    for book in books:
        if book["title"].startswith("Test"):
            try:
                database.delete_book(book["book_id"])
                vector_store.delete_book(book["book_id"])
            except Exception:
                pass


class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    def test_health_endpoints(self):
        """Test health check endpoints work"""
        # Test root
        response = client.get("/")
        assert response.status_code == 200
        
        # Test health
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_list_books_initially_empty_or_populated(self, cleanup_test_data):
        """Test listing books returns a list"""
        response = client.get("/api/books")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_chat_with_nonexistent_book_fails(self, cleanup_test_data):
        """Test chat with nonexistent book returns 404"""
        response = client.post(
            "/api/chat",
            json={
                "query": "Test query",
                "book_id": "nonexistent-book-id",
                "user_age": 10,
                "language": "en"
            }
        )
        assert response.status_code == 404
    
    def test_get_nonexistent_chunk_fails(self, cleanup_test_data):
        """Test getting nonexistent chunk returns 404"""
        response = client.get("/api/chunks/nonexistent-chunk-id")
        assert response.status_code == 404
    
    def test_get_nonexistent_chat_history_fails(self, cleanup_test_data):
        """Test getting nonexistent chat history returns 404"""
        response = client.get("/api/chat/history/nonexistent-session-id")
        assert response.status_code == 404
    
    def test_delete_nonexistent_book_fails(self, cleanup_test_data):
        """Test deleting nonexistent book returns 404"""
        response = client.delete("/api/books/nonexistent-book-id")
        assert response.status_code == 404
    
    def test_chat_validation_errors(self, cleanup_test_data):
        """Test chat endpoint validates input correctly"""
        # Test with invalid age (too young)
        response = client.post(
            "/api/chat",
            json={
                "query": "Test query",
                "book_id": "book-1",
                "user_age": 3,
                "language": "en"
            }
        )
        assert response.status_code == 422
        
        # Test with invalid age (too old)
        response = client.post(
            "/api/chat",
            json={
                "query": "Test query",
                "book_id": "book-1",
                "user_age": 16,
                "language": "en"
            }
        )
        assert response.status_code == 422
        
        # Test with invalid language
        response = client.post(
            "/api/chat",
            json={
                "query": "Test query",
                "book_id": "book-1",
                "user_age": 10,
                "language": "fr"
            }
        )
        assert response.status_code == 422
        
        # Test with empty query
        response = client.post(
            "/api/chat",
            json={
                "query": "",
                "book_id": "book-1",
                "user_age": 10,
                "language": "en"
            }
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
