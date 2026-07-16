"""
Database module for storing book metadata and processing status.

This module provides a simple SQLite-based database layer for managing
book metadata, processing status, and basic CRUD operations.
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager


class Database:
    """
    Simple SQLite database for book metadata storage.
    
    This class provides CRUD operations for books and maintains
    processing status information.
    """
    
    def __init__(self, db_path: str = "data/books.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database schema
        self._init_schema()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_schema(self):
        """Initialize database schema if not exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Books table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    book_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    page_count INTEGER NOT NULL,
                    processing_status TEXT NOT NULL,
                    language TEXT,
                    metadata TEXT
                )
            """)
            
            # Chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    book_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    page_numbers TEXT NOT NULL,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                )
            """)
            
            # Chat sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    book_id TEXT NOT NULL,
                    user_age INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    chunk_ids TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
                )
            """)
    
    def create_book(
        self,
        book_id: str,
        title: str,
        filename: str,
        page_count: int,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a new book record.
        
        Args:
            book_id: Unique identifier for the book
            title: Book title
            filename: Original filename
            page_count: Number of pages in the book
            language: Primary language (en, ur, or mixed)
            metadata: Additional metadata as dictionary
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            upload_date = datetime.now().isoformat()
            metadata_json = json.dumps(metadata or {})
            
            cursor.execute("""
                INSERT INTO books (
                    book_id, title, filename, upload_date, page_count,
                    processing_status, language, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                book_id, title, filename, upload_date, page_count,
                "pending", language, metadata_json
            ))
    
    def update_book_status(self, book_id: str, status: str) -> None:
        """
        Update the processing status of a book.
        
        Args:
            book_id: Book identifier
            status: New status (pending, processing, completed, failed)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE books SET processing_status = ? WHERE book_id = ?
            """, (status, book_id))
    
    def get_book(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get book metadata by ID.
        
        Args:
            book_id: Book identifier
        
        Returns:
            Dictionary with book metadata, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "book_id": row["book_id"],
                "title": row["title"],
                "filename": row["filename"],
                "upload_date": row["upload_date"],
                "page_count": row["page_count"],
                "processing_status": row["processing_status"],
                "language": row["language"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            }
    
    def list_books(self) -> List[Dict[str, Any]]:
        """
        List all books in the database.
        
        Returns:
            List of book metadata dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books ORDER BY upload_date DESC")
            rows = cursor.fetchall()
            
            books = []
            for row in rows:
                books.append({
                    "book_id": row["book_id"],
                    "title": row["title"],
                    "filename": row["filename"],
                    "upload_date": row["upload_date"],
                    "page_count": row["page_count"],
                    "processing_status": row["processing_status"],
                    "language": row["language"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                })
            
            return books
    
    def delete_book(self, book_id: str) -> None:
        """
        Delete a book from the database.
        
        Args:
            book_id: Book identifier
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    
    def book_exists(self, book_id: str) -> bool:
        """
        Check if a book exists in the database.
        
        Args:
            book_id: Book identifier
        
        Returns:
            True if book exists, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM books WHERE book_id = ?", (book_id,))
            return cursor.fetchone() is not None
    
    # Chunk operations
    
    def create_chunk(
        self,
        chunk_id: str,
        book_id: str,
        text: str,
        page_numbers: List[int],
        start_char: int,
        end_char: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a new chunk record.
        
        Args:
            chunk_id: Unique identifier for the chunk
            book_id: Book this chunk belongs to
            text: Chunk text content
            page_numbers: List of page numbers this chunk spans
            start_char: Starting character position in the book
            end_char: Ending character position in the book
            metadata: Additional metadata as dictionary
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            page_numbers_json = json.dumps(page_numbers)
            metadata_json = json.dumps(metadata or {})
            
            cursor.execute("""
                INSERT INTO chunks (
                    chunk_id, book_id, text, page_numbers, start_char, end_char, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk_id, book_id, text, page_numbers_json, start_char, end_char, metadata_json
            ))
    
    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get chunk by ID.
        
        Args:
            chunk_id: Chunk identifier
        
        Returns:
            Dictionary with chunk data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "chunk_id": row["chunk_id"],
                "book_id": row["book_id"],
                "text": row["text"],
                "page_numbers": json.loads(row["page_numbers"]),
                "start_char": row["start_char"],
                "end_char": row["end_char"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            }
    
    def list_chunks_by_book(self, book_id: str) -> List[Dict[str, Any]]:
        """
        List all chunks for a specific book.
        
        Args:
            book_id: Book identifier
        
        Returns:
            List of chunk dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chunks WHERE book_id = ? ORDER BY start_char", (book_id,))
            rows = cursor.fetchall()
            
            chunks = []
            for row in rows:
                chunks.append({
                    "chunk_id": row["chunk_id"],
                    "book_id": row["book_id"],
                    "text": row["text"],
                    "page_numbers": json.loads(row["page_numbers"]),
                    "start_char": row["start_char"],
                    "end_char": row["end_char"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                })
            
            return chunks
    
    def delete_chunks_by_book(self, book_id: str) -> None:
        """
        Delete all chunks for a specific book.
        
        Args:
            book_id: Book identifier
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks WHERE book_id = ?", (book_id,))

    # Chat session operations
    
    def create_chat_session(
        self,
        session_id: str,
        book_id: str,
        user_age: int
    ) -> None:
        """
        Create a new chat session.
        
        Args:
            session_id: Unique identifier for the session
            book_id: Book this session is associated with
            user_age: Age of the user (4-15)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO chat_sessions (
                    session_id, book_id, user_age, created_at
                ) VALUES (?, ?, ?, ?)
            """, (session_id, book_id, user_age, created_at))
    
    def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get chat session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dictionary with session data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "session_id": row["session_id"],
                "book_id": row["book_id"],
                "user_age": row["user_age"],
                "created_at": row["created_at"]
            }
    
    def list_chat_sessions_by_book(self, book_id: str) -> List[Dict[str, Any]]:
        """
        List all chat sessions for a specific book.
        
        Args:
            book_id: Book identifier
        
        Returns:
            List of session dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chat_sessions WHERE book_id = ? ORDER BY created_at DESC",
                (book_id,)
            )
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                sessions.append({
                    "session_id": row["session_id"],
                    "book_id": row["book_id"],
                    "user_age": row["user_age"],
                    "created_at": row["created_at"]
                })
            
            return sessions
    
    def delete_chat_session(self, session_id: str) -> None:
        """
        Delete a chat session and all its messages.
        
        Args:
            session_id: Session identifier
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
    
    # Message operations
    
    def create_message(
        self,
        message_id: str,
        session_id: str,
        role: str,
        content: str,
        chunk_ids: Optional[List[str]] = None
    ) -> None:
        """
        Create a new message in a chat session.
        
        Args:
            message_id: Unique identifier for the message
            session_id: Session this message belongs to
            role: Message role ('user' or 'assistant')
            content: Message content
            chunk_ids: List of chunk IDs used (for assistant messages)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            chunk_ids_json = json.dumps(chunk_ids or [])
            
            cursor.execute("""
                INSERT INTO messages (
                    message_id, session_id, role, content, chunk_ids, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, session_id, role, content, chunk_ids_json, timestamp))
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get message by ID.
        
        Args:
            message_id: Message identifier
        
        Returns:
            Dictionary with message data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "message_id": row["message_id"],
                "session_id": row["session_id"],
                "role": row["role"],
                "content": row["content"],
                "chunk_ids": json.loads(row["chunk_ids"]) if row["chunk_ids"] else [],
                "timestamp": row["timestamp"]
            }
    
    def list_messages_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        List all messages in a chat session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of message dictionaries ordered by timestamp
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            )
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append({
                    "message_id": row["message_id"],
                    "session_id": row["session_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "chunk_ids": json.loads(row["chunk_ids"]) if row["chunk_ids"] else [],
                    "timestamp": row["timestamp"]
                })
            
            return messages
    
    def delete_messages_by_session(self, session_id: str) -> None:
        """
        Delete all messages in a chat session.
        
        Args:
            session_id: Session identifier
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
