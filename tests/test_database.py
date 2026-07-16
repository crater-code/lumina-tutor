"""
Unit tests for the Database module.

Tests CRUD operations for books, chunks, chat sessions, and messages.
"""

import pytest
import os
import tempfile
import uuid
from datetime import datetime
from src.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Create database instance
    db = Database(db_path=path)
    
    yield db
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


class TestBookOperations:
    """Test book CRUD operations."""
    
    def test_create_and_get_book(self, temp_db):
        """Test creating and retrieving a book."""
        book_id = str(uuid.uuid4())
        
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100,
            language="en",
            metadata={"author": "Test Author"}
        )
        
        book = temp_db.get_book(book_id)
        
        assert book is not None
        assert book["book_id"] == book_id
        assert book["title"] == "Test Book"
        assert book["filename"] == "test.pdf"
        assert book["page_count"] == 100
        assert book["processing_status"] == "pending"
        assert book["language"] == "en"
        assert book["metadata"]["author"] == "Test Author"
    
    def test_update_book_status(self, temp_db):
        """Test updating book processing status."""
        book_id = str(uuid.uuid4())
        
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        temp_db.update_book_status(book_id, "completed")
        
        book = temp_db.get_book(book_id)
        assert book["processing_status"] == "completed"
    
    def test_list_books(self, temp_db):
        """Test listing all books."""
        book_id1 = str(uuid.uuid4())
        book_id2 = str(uuid.uuid4())
        
        temp_db.create_book(
            book_id=book_id1,
            title="Book 1",
            filename="book1.pdf",
            page_count=100
        )
        
        temp_db.create_book(
            book_id=book_id2,
            title="Book 2",
            filename="book2.pdf",
            page_count=200
        )
        
        books = temp_db.list_books()
        
        assert len(books) == 2
        # Should be ordered by upload_date DESC (most recent first)
        assert books[0]["book_id"] == book_id2
        assert books[1]["book_id"] == book_id1
    
    def test_delete_book(self, temp_db):
        """Test deleting a book."""
        book_id = str(uuid.uuid4())
        
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        assert temp_db.book_exists(book_id)
        
        temp_db.delete_book(book_id)
        
        assert not temp_db.book_exists(book_id)
        assert temp_db.get_book(book_id) is None
    
    def test_book_exists(self, temp_db):
        """Test checking if a book exists."""
        book_id = str(uuid.uuid4())
        
        assert not temp_db.book_exists(book_id)
        
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        assert temp_db.book_exists(book_id)
    
    def test_get_nonexistent_book(self, temp_db):
        """Test getting a book that doesn't exist."""
        book = temp_db.get_book("nonexistent-id")
        assert book is None


class TestChunkOperations:
    """Test chunk CRUD operations."""
    
    def test_create_and_get_chunk(self, temp_db):
        """Test creating and retrieving a chunk."""
        # First create a book
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create a chunk
        chunk_id = f"book_{book_id}_chunk_0"
        temp_db.create_chunk(
            chunk_id=chunk_id,
            book_id=book_id,
            text="This is a test chunk.",
            page_numbers=[1, 2],
            start_char=0,
            end_char=21,
            metadata={"section": "Introduction"}
        )
        
        chunk = temp_db.get_chunk(chunk_id)
        
        assert chunk is not None
        assert chunk["chunk_id"] == chunk_id
        assert chunk["book_id"] == book_id
        assert chunk["text"] == "This is a test chunk."
        assert chunk["page_numbers"] == [1, 2]
        assert chunk["start_char"] == 0
        assert chunk["end_char"] == 21
        assert chunk["metadata"]["section"] == "Introduction"
    
    def test_list_chunks_by_book(self, temp_db):
        """Test listing all chunks for a book."""
        # Create a book
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create multiple chunks
        for i in range(3):
            chunk_id = f"book_{book_id}_chunk_{i}"
            temp_db.create_chunk(
                chunk_id=chunk_id,
                book_id=book_id,
                text=f"Chunk {i} text",
                page_numbers=[i + 1],
                start_char=i * 100,
                end_char=(i + 1) * 100
            )
        
        chunks = temp_db.list_chunks_by_book(book_id)
        
        assert len(chunks) == 3
        # Should be ordered by start_char
        assert chunks[0]["start_char"] == 0
        assert chunks[1]["start_char"] == 100
        assert chunks[2]["start_char"] == 200
    
    def test_delete_chunks_by_book(self, temp_db):
        """Test deleting all chunks for a book."""
        # Create a book
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create chunks
        chunk_id = f"book_{book_id}_chunk_0"
        temp_db.create_chunk(
            chunk_id=chunk_id,
            book_id=book_id,
            text="Test chunk",
            page_numbers=[1],
            start_char=0,
            end_char=10
        )
        
        assert len(temp_db.list_chunks_by_book(book_id)) == 1
        
        temp_db.delete_chunks_by_book(book_id)
        
        assert len(temp_db.list_chunks_by_book(book_id)) == 0
    
    def test_get_nonexistent_chunk(self, temp_db):
        """Test getting a chunk that doesn't exist."""
        chunk = temp_db.get_chunk("nonexistent-chunk-id")
        assert chunk is None
    
    def test_chunks_cascade_delete_with_book(self, temp_db):
        """Test that chunks are deleted when their book is deleted."""
        # Create a book
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create a chunk
        chunk_id = f"book_{book_id}_chunk_0"
        temp_db.create_chunk(
            chunk_id=chunk_id,
            book_id=book_id,
            text="Test chunk",
            page_numbers=[1],
            start_char=0,
            end_char=10
        )
        
        assert temp_db.get_chunk(chunk_id) is not None
        
        # Delete the book
        temp_db.delete_book(book_id)
        
        # Chunk should also be deleted
        assert temp_db.get_chunk(chunk_id) is None


class TestChatSessionOperations:
    """Test chat session CRUD operations."""
    
    def test_create_and_get_chat_session(self, temp_db):
        """Test creating and retrieving a chat session."""
        # Create a book first
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create a chat session
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        session = temp_db.get_chat_session(session_id)
        
        assert session is not None
        assert session["session_id"] == session_id
        assert session["book_id"] == book_id
        assert session["user_age"] == 10
        assert "created_at" in session
    
    def test_list_chat_sessions_by_book(self, temp_db):
        """Test listing all chat sessions for a book."""
        # Create a book
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_id = str(uuid.uuid4())
            session_ids.append(session_id)
            temp_db.create_chat_session(
                session_id=session_id,
                book_id=book_id,
                user_age=8 + i
            )
        
        sessions = temp_db.list_chat_sessions_by_book(book_id)
        
        assert len(sessions) == 3
        # Should be ordered by created_at DESC (most recent first)
        assert sessions[0]["session_id"] == session_ids[2]
        assert sessions[1]["session_id"] == session_ids[1]
        assert sessions[2]["session_id"] == session_ids[0]
    
    def test_delete_chat_session(self, temp_db):
        """Test deleting a chat session."""
        # Create a book
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create a session
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        assert temp_db.get_chat_session(session_id) is not None
        
        temp_db.delete_chat_session(session_id)
        
        assert temp_db.get_chat_session(session_id) is None
    
    def test_get_nonexistent_chat_session(self, temp_db):
        """Test getting a chat session that doesn't exist."""
        session = temp_db.get_chat_session("nonexistent-session-id")
        assert session is None
    
    def test_chat_sessions_cascade_delete_with_book(self, temp_db):
        """Test that chat sessions are deleted when their book is deleted."""
        # Create a book
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create a session
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        assert temp_db.get_chat_session(session_id) is not None
        
        # Delete the book
        temp_db.delete_book(book_id)
        
        # Session should also be deleted
        assert temp_db.get_chat_session(session_id) is None


class TestMessageOperations:
    """Test message CRUD operations."""
    
    def test_create_and_get_message(self, temp_db):
        """Test creating and retrieving a message."""
        # Create a book and session
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        # Create a message
        message_id = str(uuid.uuid4())
        temp_db.create_message(
            message_id=message_id,
            session_id=session_id,
            role="user",
            content="What is this book about?",
            chunk_ids=None
        )
        
        message = temp_db.get_message(message_id)
        
        assert message is not None
        assert message["message_id"] == message_id
        assert message["session_id"] == session_id
        assert message["role"] == "user"
        assert message["content"] == "What is this book about?"
        assert message["chunk_ids"] == []
        assert "timestamp" in message
    
    def test_create_assistant_message_with_chunks(self, temp_db):
        """Test creating an assistant message with chunk IDs."""
        # Create a book and session
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        # Create an assistant message with chunk IDs
        message_id = str(uuid.uuid4())
        chunk_ids = [f"book_{book_id}_chunk_0", f"book_{book_id}_chunk_1"]
        temp_db.create_message(
            message_id=message_id,
            session_id=session_id,
            role="assistant",
            content="This book is about...",
            chunk_ids=chunk_ids
        )
        
        message = temp_db.get_message(message_id)
        
        assert message["role"] == "assistant"
        assert message["chunk_ids"] == chunk_ids
    
    def test_list_messages_by_session(self, temp_db):
        """Test listing all messages in a session."""
        # Create a book and session
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        # Create multiple messages
        message_ids = []
        for i in range(3):
            message_id = str(uuid.uuid4())
            message_ids.append(message_id)
            temp_db.create_message(
                message_id=message_id,
                session_id=session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}"
            )
        
        messages = temp_db.list_messages_by_session(session_id)
        
        assert len(messages) == 3
        # Should be ordered by timestamp (oldest first)
        assert messages[0]["message_id"] == message_ids[0]
        assert messages[1]["message_id"] == message_ids[1]
        assert messages[2]["message_id"] == message_ids[2]
    
    def test_delete_messages_by_session(self, temp_db):
        """Test deleting all messages in a session."""
        # Create a book and session
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        # Create a message
        message_id = str(uuid.uuid4())
        temp_db.create_message(
            message_id=message_id,
            session_id=session_id,
            role="user",
            content="Test message"
        )
        
        assert len(temp_db.list_messages_by_session(session_id)) == 1
        
        temp_db.delete_messages_by_session(session_id)
        
        assert len(temp_db.list_messages_by_session(session_id)) == 0
    
    def test_get_nonexistent_message(self, temp_db):
        """Test getting a message that doesn't exist."""
        message = temp_db.get_message("nonexistent-message-id")
        assert message is None
    
    def test_messages_cascade_delete_with_session(self, temp_db):
        """Test that messages are deleted when their session is deleted."""
        # Create a book and session
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        # Create a message
        message_id = str(uuid.uuid4())
        temp_db.create_message(
            message_id=message_id,
            session_id=session_id,
            role="user",
            content="Test message"
        )
        
        assert temp_db.get_message(message_id) is not None
        
        # Delete the session
        temp_db.delete_chat_session(session_id)
        
        # Message should also be deleted
        assert temp_db.get_message(message_id) is None


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_metadata(self, temp_db):
        """Test creating records with no metadata."""
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100,
            metadata=None
        )
        
        book = temp_db.get_book(book_id)
        assert book["metadata"] == {}
    
    def test_empty_chunk_ids(self, temp_db):
        """Test creating a message with no chunk IDs."""
        # Create a book and session
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        session_id = str(uuid.uuid4())
        temp_db.create_chat_session(
            session_id=session_id,
            book_id=book_id,
            user_age=10
        )
        
        # Create a message with no chunk IDs
        message_id = str(uuid.uuid4())
        temp_db.create_message(
            message_id=message_id,
            session_id=session_id,
            role="user",
            content="Test message",
            chunk_ids=None
        )
        
        message = temp_db.get_message(message_id)
        assert message["chunk_ids"] == []
    
    def test_multiple_page_numbers(self, temp_db):
        """Test chunk with multiple page numbers."""
        # Create a book
        book_id = str(uuid.uuid4())
        temp_db.create_book(
            book_id=book_id,
            title="Test Book",
            filename="test.pdf",
            page_count=100
        )
        
        # Create a chunk spanning multiple pages
        chunk_id = f"book_{book_id}_chunk_0"
        temp_db.create_chunk(
            chunk_id=chunk_id,
            book_id=book_id,
            text="This chunk spans multiple pages.",
            page_numbers=[5, 6, 7],
            start_char=1000,
            end_char=1050
        )
        
        chunk = temp_db.get_chunk(chunk_id)
        assert chunk["page_numbers"] == [5, 6, 7]
