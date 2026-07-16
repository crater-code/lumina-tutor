"""
Book Ingestion Pipeline for the Book-Bounded Tutoring Chatbot system.

This module provides the BookIngestionPipeline class that orchestrates the
complete process of ingesting a PDF book: parsing, chunking, embedding generation,
and storage.
"""

import os
import uuid
import logging
from typing import Optional, Dict, Any
from src.pdf_parser import PDFParser
from src.chunking_engine import ChunkingEngine
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.database import Database
from src.exceptions import (
    PDFParseError,
    FileSizeError,
    NoTextError,
    RetrievalError
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BookIngestionPipeline:
    """
    Orchestrates the complete book ingestion process.
    
    This class coordinates the PDF parsing, chunking, embedding generation,
    and storage operations. It handles errors at each stage and updates
    processing status accordingly.
    
    Attributes:
        pdf_parser: PDFParser instance for text extraction
        chunking_engine: ChunkingEngine instance for creating chunks
        embedding_generator: EmbeddingGenerator instance for embeddings
        vector_store: VectorStore instance for storing embeddings
        database: Database instance for metadata storage
    """
    
    def __init__(
        self,
        pdf_parser: Optional[PDFParser] = None,
        chunking_engine: Optional[ChunkingEngine] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        vector_store: Optional[VectorStore] = None,
        database: Optional[Database] = None
    ):
        """
        Initialize the BookIngestionPipeline.
        
        Args:
            pdf_parser: PDFParser instance (creates default if None)
            chunking_engine: ChunkingEngine instance (creates default if None)
            embedding_generator: EmbeddingGenerator instance (creates default if None)
            vector_store: VectorStore instance (creates default if None)
            database: Database instance (creates default if None)
        """
        self.pdf_parser = pdf_parser or PDFParser(use_pdfplumber=True)
        self.chunking_engine = chunking_engine or ChunkingEngine()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.vector_store = vector_store or VectorStore()
        self.database = database or Database()
    
    def ingest_book(
        self,
        pdf_path: str,
        title: Optional[str] = None,
        book_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate the complete book ingestion pipeline.
        
        This method performs the following steps:
        1. Extract text from PDF using PDFParser
        2. Create chunks using ChunkingEngine
        3. Generate embeddings using EmbeddingGenerator
        4. Store chunks and embeddings in VectorStore
        5. Store book metadata in Database
        
        Errors at each stage are caught and the processing status is updated.
        
        Args:
            pdf_path: Path to the PDF file to ingest
            title: Book title (uses filename if not provided)
            book_id: Unique book identifier (generates UUID if not provided)
        
        Returns:
            Dictionary containing:
                - book_id: The book identifier
                - status: Processing status (completed or failed)
                - page_count: Number of pages processed
                - chunk_count: Number of chunks created
                - error: Error message if failed (optional)
        
        Raises:
            PDFParseError: If PDF cannot be parsed
            FileSizeError: If PDF exceeds 450 pages
            NoTextError: If PDF contains no extractable text
            RetrievalError: If storage operations fail
        """
        # Generate book_id if not provided
        if book_id is None:
            book_id = str(uuid.uuid4())
        
        # Use filename as title if not provided
        if title is None:
            title = os.path.basename(pdf_path)
        
        filename = os.path.basename(pdf_path)
        
        logger.info(f"Starting ingestion for book: {title} (ID: {book_id})")
        
        try:
            # Step 1: Extract text from PDF
            logger.info(f"Step 1/5: Extracting text from PDF: {pdf_path}")
            pages = self.pdf_parser.extract_text(pdf_path)
            page_count = len(pages)
            
            # Detect primary language
            language = self._detect_primary_language(pages)
            
            logger.info(f"Extracted {page_count} pages, language: {language}")
            
            # Create book record in database with pending status
            self.database.create_book(
                book_id=book_id,
                title=title,
                filename=filename,
                page_count=page_count,
                language=language,
                metadata={"pdf_path": pdf_path}
            )
            
            # Update status to processing
            self.database.update_book_status(book_id, "processing")
            
            # Step 2: Create chunks
            logger.info(f"Step 2/5: Creating chunks for book {book_id}")
            chunks = self.chunking_engine.create_chunks(pages, book_id=book_id)
            chunk_count = len(chunks)
            
            logger.info(f"Created {chunk_count} chunks")
            
            if chunk_count == 0:
                raise ValueError("No chunks were created from the PDF content")
            
            # Step 3: Generate embeddings
            logger.info(f"Step 3/5: Generating embeddings for {chunk_count} chunks")
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_generator.generate_batch_embeddings(chunk_texts)
            
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            
            # Step 4: Store chunks and embeddings in vector store
            logger.info(f"Step 4/5: Storing chunks and embeddings in vector store")
            self.vector_store.add_chunks(book_id, chunks, embeddings)
            
            logger.info(f"Stored {chunk_count} chunks in vector store")
            
            # Step 5: Update book status to completed
            logger.info(f"Step 5/5: Updating book status to completed")
            self.database.update_book_status(book_id, "completed")
            
            logger.info(f"Successfully completed ingestion for book {book_id}")
            
            return {
                "book_id": book_id,
                "status": "completed",
                "page_count": page_count,
                "chunk_count": chunk_count,
                "language": language
            }
            
        except (PDFParseError, FileSizeError, NoTextError) as e:
            # PDF-related errors
            error_msg = f"PDF processing error: {str(e)}"
            logger.error(f"Ingestion failed for book {book_id}: {error_msg}")
            
            # Update status to failed if book was created
            if self.database.book_exists(book_id):
                self.database.update_book_status(book_id, "failed")
            
            return {
                "book_id": book_id,
                "status": "failed",
                "error": error_msg,
                "error_type": type(e).__name__
            }
            
        except RetrievalError as e:
            # Vector store errors
            error_msg = f"Storage error: {str(e)}"
            logger.error(f"Ingestion failed for book {book_id}: {error_msg}")
            
            # Update status to failed
            if self.database.book_exists(book_id):
                self.database.update_book_status(book_id, "failed")
            
            # Clean up vector store if chunks were partially added
            try:
                self.vector_store.delete_book(book_id)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up vector store: {cleanup_error}")
            
            return {
                "book_id": book_id,
                "status": "failed",
                "error": error_msg,
                "error_type": type(e).__name__
            }
            
        except Exception as e:
            # Unexpected errors
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Ingestion failed for book {book_id}: {error_msg}", exc_info=True)
            
            # Update status to failed
            if self.database.book_exists(book_id):
                self.database.update_book_status(book_id, "failed")
            
            # Clean up vector store
            try:
                self.vector_store.delete_book(book_id)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up vector store: {cleanup_error}")
            
            return {
                "book_id": book_id,
                "status": "failed",
                "error": error_msg,
                "error_type": "UnexpectedError"
            }
    
    def _detect_primary_language(self, pages) -> str:
        """
        Detect the primary language of the book from pages.
        
        Args:
            pages: List of PageContent objects
        
        Returns:
            Language code: "en", "ur", or "mixed"
        """
        if not pages:
            return "en"
        
        # Count language occurrences
        language_counts = {"en": 0, "ur": 0, "mixed": 0}
        
        for page in pages:
            lang = page.metadata.get("language", "en")
            if lang in language_counts:
                language_counts[lang] += 1
        
        # If any page is mixed, consider the whole book mixed
        if language_counts["mixed"] > 0:
            return "mixed"
        
        # Otherwise, return the most common language
        if language_counts["ur"] > language_counts["en"]:
            return "ur"
        else:
            return "en"
    
    def delete_book(self, book_id: str) -> None:
        """
        Delete a book and all its associated data.
        
        This method removes:
        - Book metadata from database
        - Chunks and embeddings from vector store
        
        Args:
            book_id: Book identifier
        """
        logger.info(f"Deleting book {book_id}")
        
        try:
            # Delete from vector store
            self.vector_store.delete_book(book_id)
            logger.info(f"Deleted chunks from vector store for book {book_id}")
        except Exception as e:
            logger.warning(f"Failed to delete from vector store: {e}")
        
        try:
            # Delete from database
            self.database.delete_book(book_id)
            logger.info(f"Deleted metadata from database for book {book_id}")
        except Exception as e:
            logger.warning(f"Failed to delete from database: {e}")
    
    def get_book_status(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a book.
        
        Args:
            book_id: Book identifier
        
        Returns:
            Dictionary with book metadata and status, or None if not found
        """
        return self.database.get_book(book_id)
    
    def list_books(self) -> list:
        """
        List all books in the system.
        
        Returns:
            List of book metadata dictionaries
        """
        return self.database.list_books()
