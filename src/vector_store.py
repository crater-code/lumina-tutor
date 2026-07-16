"""
Vector Store for storing and retrieving chunk embeddings.

This module provides the VectorStore class that uses FAISS for efficient
similarity search of chunk embeddings. It maintains book-to-chunks mapping
for isolation between different books.
"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Tuple, Dict, Optional
from src.models import Chunk
from src.exceptions import RetrievalError


class VectorStore:
    """
    Stores and retrieves chunk embeddings using FAISS for similarity search.
    
    This class maintains separate FAISS indices for each book to ensure
    isolation between books. It supports adding chunks, searching for similar
    chunks, and deleting entire books.
    
    Attributes:
        storage_dir: Directory where indices and metadata are stored
        indices: Dictionary mapping book_id to FAISS index
        chunks: Dictionary mapping book_id to list of chunks
        embedding_dim: Dimension of embedding vectors
    """
    
    def __init__(self, storage_dir: str = "data/vector_store", embedding_dim: int = 384):
        """
        Initialize the VectorStore.
        
        Args:
            storage_dir: Directory to store FAISS indices and metadata
            embedding_dim: Dimension of embedding vectors (default: 384 for MiniLM)
        """
        self.storage_dir = storage_dir
        self.embedding_dim = embedding_dim
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # In-memory storage for indices and chunks
        self.indices: Dict[str, faiss.Index] = {}
        self.chunks: Dict[str, List[Chunk]] = {}
        
        # Load existing indices and chunks from disk
        self._load_all_books()
    
    def add_chunks(
        self,
        book_id: str,
        chunks: List[Chunk],
        embeddings: np.ndarray
    ) -> None:
        """
        Add chunks and their embeddings to the store.
        
        This method creates or updates a FAISS index for the specified book
        and stores the chunks with their embeddings.
        
        Args:
            book_id: Unique identifier for the book
            chunks: List of Chunk objects to store
            embeddings: Corresponding embedding vectors (shape: [num_chunks, embedding_dim])
        
        Raises:
            ValueError: If chunks and embeddings have mismatched lengths
            ValueError: If embeddings have wrong dimension
            RetrievalError: If storage operation fails
        """
        if not chunks:
            raise ValueError("Chunks list cannot be empty")
        
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})"
            )
        
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension ({embeddings.shape[1]}) must match "
                f"expected dimension ({self.embedding_dim})"
            )
        
        try:
            # Create a new FAISS index for this book (or replace existing)
            # Using IndexFlatL2 for exact search with L2 distance
            index = faiss.IndexFlatL2(self.embedding_dim)
            
            # Ensure embeddings are float32 (required by FAISS)
            embeddings_float32 = embeddings.astype(np.float32)
            
            # Add embeddings to the index
            index.add(embeddings_float32)
            
            # Store index and chunks in memory
            self.indices[book_id] = index
            self.chunks[book_id] = chunks
            
            # Persist to disk
            self._save_book(book_id)
            
        except Exception as e:
            raise RetrievalError(f"Failed to add chunks to vector store: {str(e)}")
    
    def search(
        self,
        book_id: str,
        query_embedding: np.ndarray,
        top_k: int = 5,
        min_similarity: float = 0.0
    ) -> List[Tuple[Chunk, float]]:
        """
        Search for similar chunks using similarity search.
        
        This method performs k-nearest neighbor search in the FAISS index
        and returns chunks with similarity scores above the threshold.
        
        Args:
            book_id: Book to search within
            query_embedding: Query vector (shape: [embedding_dim])
            top_k: Number of results to return (default: 5)
            min_similarity: Minimum similarity threshold (default: 0.0)
                          Note: This is converted from L2 distance
        
        Returns:
            List of (Chunk, similarity_score) tuples, sorted by descending similarity
            Returns empty list if no chunks meet the threshold or book not found
        
        Raises:
            ValueError: If query_embedding has wrong dimension
            RetrievalError: If search operation fails
        """
        # Check if book exists
        if book_id not in self.indices:
            return []
        
        # Validate query embedding dimension
        if query_embedding.shape[0] != self.embedding_dim:
            raise ValueError(
                f"Query embedding dimension ({query_embedding.shape[0]}) must match "
                f"expected dimension ({self.embedding_dim})"
            )
        
        try:
            index = self.indices[book_id]
            book_chunks = self.chunks[book_id]
            
            # Ensure query is 2D array with float32 type (required by FAISS)
            query_float32 = query_embedding.astype(np.float32).reshape(1, -1)
            
            # Perform search
            # FAISS returns L2 distances, we need to convert to similarity scores
            distances, indices = index.search(query_float32, min(top_k, len(book_chunks)))
            
            # Convert L2 distances to similarity scores
            # Using: similarity = 1 / (1 + distance)
            # This maps distance 0 -> similarity 1, and larger distances -> smaller similarities
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                # idx == -1 means no result found (shouldn't happen with our setup)
                if idx == -1:
                    continue
                
                # Convert L2 distance to similarity score
                similarity = 1.0 / (1.0 + float(distance))
                
                # Filter by minimum similarity threshold
                if similarity >= min_similarity:
                    chunk = book_chunks[idx]
                    results.append((chunk, similarity))
            
            # Results are already sorted by distance (ascending), which means
            # sorted by similarity (descending) after conversion
            return results
            
        except Exception as e:
            raise RetrievalError(f"Failed to search vector store: {str(e)}")
    
    def delete_book(self, book_id: str) -> None:
        """
        Remove all chunks for a book.
        
        This method deletes the FAISS index and all chunks associated with
        the specified book from both memory and disk.
        
        Args:
            book_id: Unique identifier for the book to delete
        
        Raises:
            RetrievalError: If deletion operation fails
        """
        try:
            # Remove from memory
            if book_id in self.indices:
                del self.indices[book_id]
            
            if book_id in self.chunks:
                del self.chunks[book_id]
            
            # Remove from disk
            index_path = self._get_index_path(book_id)
            chunks_path = self._get_chunks_path(book_id)
            
            if os.path.exists(index_path):
                os.remove(index_path)
            
            if os.path.exists(chunks_path):
                os.remove(chunks_path)
                
        except Exception as e:
            raise RetrievalError(f"Failed to delete book from vector store: {str(e)}")
    
    def get_book_ids(self) -> List[str]:
        """
        Get list of all book IDs in the store.
        
        Returns:
            List of book IDs
        """
        return list(self.indices.keys())
    
    def get_chunk_count(self, book_id: str) -> int:
        """
        Get the number of chunks for a specific book.
        
        Args:
            book_id: Book identifier
        
        Returns:
            Number of chunks, or 0 if book not found
        """
        if book_id not in self.chunks:
            return 0
        return len(self.chunks[book_id])
    
    def _save_book(self, book_id: str) -> None:
        """
        Save a book's index and chunks to disk.
        
        Args:
            book_id: Book identifier
        """
        if book_id not in self.indices or book_id not in self.chunks:
            return
        
        # Save FAISS index
        index_path = self._get_index_path(book_id)
        faiss.write_index(self.indices[book_id], index_path)
        
        # Save chunks using pickle
        chunks_path = self._get_chunks_path(book_id)
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks[book_id], f)
    
    def _load_all_books(self) -> None:
        """
        Load all books from disk into memory.
        """
        if not os.path.exists(self.storage_dir):
            return
        
        # Find all index files
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.index'):
                book_id = filename[:-6]  # Remove '.index' suffix
                self._load_book(book_id)
    
    def _load_book(self, book_id: str) -> None:
        """
        Load a specific book from disk into memory.
        
        Args:
            book_id: Book identifier
        """
        index_path = self._get_index_path(book_id)
        chunks_path = self._get_chunks_path(book_id)
        
        # Check if both files exist
        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            return
        
        try:
            # Load FAISS index
            index = faiss.read_index(index_path)
            self.indices[book_id] = index
            
            # Load chunks
            with open(chunks_path, 'rb') as f:
                chunks = pickle.load(f)
            self.chunks[book_id] = chunks
            
        except Exception as e:
            # If loading fails, skip this book
            print(f"Warning: Failed to load book {book_id}: {str(e)}")
    
    def _get_index_path(self, book_id: str) -> str:
        """
        Get the file path for a book's FAISS index.
        
        Args:
            book_id: Book identifier
        
        Returns:
            Path to index file
        """
        return os.path.join(self.storage_dir, f"{book_id}.index")
    
    def _get_chunks_path(self, book_id: str) -> str:
        """
        Get the file path for a book's chunks.
        
        Args:
            book_id: Book identifier
        
        Returns:
            Path to chunks file
        """
        return os.path.join(self.storage_dir, f"{book_id}.chunks")
