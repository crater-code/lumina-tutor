"""
Embedding Generator for the Book-Bounded Tutoring Chatbot system.

This module provides functionality to generate vector embeddings for text chunks
and queries using sentence-transformers models. It supports multilingual text
(English and Urdu).
"""

import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """
    Generates vector embeddings for text using sentence-transformers.
    
    This class uses a multilingual sentence-transformers model to create
    embeddings for both English and Urdu text, enabling semantic search
    across book chunks.
    
    Attributes:
        model: The loaded sentence-transformers model
        model_name: Name of the model being used
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the EmbeddingGenerator with a sentence-transformers model.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       Default is paraphrase-multilingual-MiniLM-L12-v2 which
                       supports both English and Urdu.
        
        Raises:
            Exception: If the model cannot be loaded
        """
        self.model_name = model_name
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise Exception(f"Failed to load sentence-transformers model '{model_name}': {str(e)}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding vector for a single text.
        
        This method creates a dense vector representation of the input text
        that captures its semantic meaning. The resulting embedding can be
        used for similarity search and retrieval.
        
        Args:
            text: Input text to generate embedding for (English or Urdu)
        
        Returns:
            Embedding vector as a numpy array
        
        Raises:
            ValueError: If text is empty or None
            Exception: If embedding generation fails
        
        Example:
            >>> generator = EmbeddingGenerator()
            >>> embedding = generator.generate_embedding("Hello world")
            >>> print(embedding.shape)
            (384,)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty or None")
        
        try:
            # Generate embedding using the model
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def generate_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        
        This method processes multiple texts in a batch, which is more efficient
        than calling generate_embedding() multiple times. It's particularly useful
        when processing all chunks from a book.
        
        Args:
            texts: List of input texts to generate embeddings for
        
        Returns:
            2D numpy array where each row is an embedding vector
            Shape: (num_texts, embedding_dimension)
        
        Raises:
            ValueError: If texts list is empty or contains empty strings
            Exception: If embedding generation fails
        
        Example:
            >>> generator = EmbeddingGenerator()
            >>> texts = ["First text", "Second text", "Third text"]
            >>> embeddings = generator.generate_batch_embeddings(texts)
            >>> print(embeddings.shape)
            (3, 384)
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Check for empty strings in the list
        if any(not text or not text.strip() for text in texts):
            raise ValueError("Texts list cannot contain empty strings")
        
        try:
            # Generate embeddings in batch for efficiency
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings
        except Exception as e:
            raise Exception(f"Failed to generate batch embeddings: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors produced by this model.
        
        Returns:
            Integer representing the embedding dimension
        
        Example:
            >>> generator = EmbeddingGenerator()
            >>> dim = generator.get_embedding_dimension()
            >>> print(dim)
            384
        """
        return self.model.get_sentence_embedding_dimension()
