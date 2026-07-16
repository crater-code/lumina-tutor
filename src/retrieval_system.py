"""
Retrieval System for the Book-Bounded Tutoring Chatbot.

This module provides the RetrievalSystem class that orchestrates the retrieval
of relevant book chunks based on user queries. It uses the EmbeddingGenerator
to create query embeddings and the VectorStore to perform similarity search.
"""

from typing import List
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.models import Chunk
from src.exceptions import RetrievalError


class RetrievalSystem:
    """
    Retrieves relevant chunks for user queries using semantic search.
    
    This class orchestrates the retrieval process by:
    1. Generating embeddings for user queries
    2. Searching the vector store for similar chunks
    3. Ranking and filtering results by relevance
    
    Attributes:
        embedding_generator: EmbeddingGenerator instance for creating query embeddings
        vector_store: VectorStore instance for similarity search
    """
    
    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        vector_store: VectorStore
    ):
        """
        Initialize the RetrievalSystem.
        
        Args:
            embedding_generator: EmbeddingGenerator instance for creating embeddings
            vector_store: VectorStore instance for storing and searching chunks
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
    
    def retrieve_chunks(
        self,
        book_id: str,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> List[Chunk]:
        """
        Retrieve relevant chunks for a query.
        
        This method performs the following steps:
        1. Validates the query input
        2. Generates an embedding for the query using EmbeddingGenerator
        3. Searches the VectorStore for similar chunks
        4. Filters results by minimum similarity threshold
        5. Returns top-k chunks ranked by relevance (descending)
        
        Args:
            book_id: Unique identifier for the book to search within
            query: User query text (English or Urdu)
            top_k: Maximum number of chunks to retrieve (default: 5)
            min_similarity: Minimum similarity threshold for results (default: 0.3)
                          Chunks with similarity below this value are filtered out
        
        Returns:
            List of Chunk objects ranked by relevance (descending order)
            Returns empty list if:
            - No relevant chunks found above minimum threshold
            - Book not found
            - Query is empty
        
        Raises:
            ValueError: If query is empty or None
            ValueError: If top_k is less than 1
            ValueError: If min_similarity is not in range [0, 1]
            RetrievalError: If retrieval operation fails
        
        Example:
            >>> retrieval_system = RetrievalSystem(embedding_gen, vector_store)
            >>> chunks = retrieval_system.retrieve_chunks(
            ...     book_id="book_123",
            ...     query="What is photosynthesis?",
            ...     top_k=3
            ... )
            >>> for chunk in chunks:
            ...     print(f"Chunk {chunk.chunk_id}: {chunk.text[:50]}...")
        """
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty or None")
        
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        
        if not (0.0 <= min_similarity <= 1.0):
            raise ValueError("min_similarity must be in range [0, 1]")
        
        try:
            # Step 1: Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Step 2: Search vector store for similar chunks
            # The vector store returns results sorted by similarity (descending)
            results = self.vector_store.search(
                book_id=book_id,
                query_embedding=query_embedding,
                top_k=top_k,
                min_similarity=min_similarity
            )
            
            # Step 3: Extract chunks from results (already ranked by relevance)
            # Results are tuples of (Chunk, similarity_score)
            chunks = [chunk for chunk, score in results]
            
            return chunks
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Wrap other exceptions in RetrievalError
            raise RetrievalError(f"Failed to retrieve chunks: {str(e)}")
