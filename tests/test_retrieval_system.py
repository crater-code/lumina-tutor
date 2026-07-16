"""
Unit tests for the RetrievalSystem class.
"""

import pytest
import numpy as np
from src.retrieval_system import RetrievalSystem
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.models import Chunk
from src.exceptions import RetrievalError


@pytest.fixture
def embedding_generator():
    """Create an EmbeddingGenerator instance for testing."""
    return EmbeddingGenerator()


@pytest.fixture
def vector_store(tmp_path):
    """Create a VectorStore instance with temporary storage."""
    storage_dir = str(tmp_path / "vector_store")
    return VectorStore(storage_dir=storage_dir)


@pytest.fixture
def retrieval_system(embedding_generator, vector_store):
    """Create a RetrievalSystem instance for testing."""
    return RetrievalSystem(embedding_generator, vector_store)


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    return [
        Chunk(
            chunk_id="book_1_chunk_0",
            text="Photosynthesis is the process by which plants convert sunlight into energy.",
            page_numbers=[1],
            start_char=0,
            end_char=75,
            metadata={"section": "Biology"}
        ),
        Chunk(
            chunk_id="book_1_chunk_1",
            text="Plants use chlorophyll to absorb light energy during photosynthesis.",
            page_numbers=[1],
            start_char=76,
            end_char=145,
            metadata={"section": "Biology"}
        ),
        Chunk(
            chunk_id="book_1_chunk_2",
            text="The water cycle describes how water moves through the environment.",
            page_numbers=[2],
            start_char=0,
            end_char=67,
            metadata={"section": "Earth Science"}
        ),
        Chunk(
            chunk_id="book_1_chunk_3",
            text="Gravity is the force that attracts objects toward each other.",
            page_numbers=[3],
            start_char=0,
            end_char=62,
            metadata={"section": "Physics"}
        ),
    ]


@pytest.fixture
def populated_vector_store(vector_store, embedding_generator, sample_chunks):
    """Create a vector store populated with sample chunks."""
    # Generate embeddings for sample chunks
    texts = [chunk.text for chunk in sample_chunks]
    embeddings = embedding_generator.generate_batch_embeddings(texts)
    
    # Add chunks to vector store
    vector_store.add_chunks("book_1", sample_chunks, embeddings)
    
    return vector_store


class TestRetrievalSystemInitialization:
    """Tests for RetrievalSystem initialization."""
    
    def test_initialization(self, embedding_generator, vector_store):
        """Test that RetrievalSystem initializes correctly."""
        retrieval_system = RetrievalSystem(embedding_generator, vector_store)
        
        assert retrieval_system.embedding_generator is embedding_generator
        assert retrieval_system.vector_store is vector_store


class TestRetrieveChunks:
    """Tests for the retrieve_chunks method."""
    
    def test_retrieve_chunks_basic(self, embedding_generator, populated_vector_store):
        """Test basic chunk retrieval with a relevant query."""
        retrieval_system = RetrievalSystem(embedding_generator, populated_vector_store)
        
        # Query about photosynthesis should return relevant chunks
        chunks = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="How do plants make energy?",
            top_k=2
        )
        
        # Should return chunks (may be 1 or 2 depending on similarity threshold)
        assert isinstance(chunks, list)
        assert len(chunks) <= 2
        
        # All returned items should be Chunk objects
        for chunk in chunks:
            assert isinstance(chunk, Chunk)
            assert chunk.chunk_id.startswith("book_1_chunk_")
    
    def test_retrieve_chunks_returns_top_k(self, embedding_generator, populated_vector_store):
        """Test that retrieve_chunks respects the top_k parameter."""
        retrieval_system = RetrievalSystem(embedding_generator, populated_vector_store)
        
        # Request only 1 chunk
        chunks = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="photosynthesis",
            top_k=1,
            min_similarity=0.0  # Accept all results
        )
        
        # Should return at most 1 chunk
        assert len(chunks) <= 1
    
    def test_retrieve_chunks_ranked_by_relevance(self, embedding_generator, populated_vector_store):
        """Test that results are ranked by relevance (descending)."""
        retrieval_system = RetrievalSystem(embedding_generator, populated_vector_store)
        
        # Query about photosynthesis
        chunks = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="photosynthesis in plants",
            top_k=4,
            min_similarity=0.0
        )
        
        # Should return multiple chunks
        assert len(chunks) >= 2
        
        # The first chunks should be about photosynthesis
        # (more relevant to the query)
        assert "photosynthesis" in chunks[0].text.lower() or "plants" in chunks[0].text.lower()
    
    def test_retrieve_chunks_empty_results(self, embedding_generator, populated_vector_store):
        """Test retrieval when no relevant chunks are found."""
        retrieval_system = RetrievalSystem(embedding_generator, populated_vector_store)
        
        # Query with very high similarity threshold
        chunks = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="quantum mechanics",
            top_k=5,
            min_similarity=0.99  # Very high threshold
        )
        
        # Should return empty list
        assert chunks == []
    
    def test_retrieve_chunks_nonexistent_book(self, embedding_generator, populated_vector_store):
        """Test retrieval for a book that doesn't exist."""
        retrieval_system = RetrievalSystem(embedding_generator, populated_vector_store)
        
        # Query for non-existent book
        chunks = retrieval_system.retrieve_chunks(
            book_id="nonexistent_book",
            query="test query",
            top_k=5
        )
        
        # Should return empty list (not raise an error)
        assert chunks == []
    
    def test_retrieve_chunks_empty_query(self, retrieval_system):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            retrieval_system.retrieve_chunks(
                book_id="book_1",
                query="",
                top_k=5
            )
    
    def test_retrieve_chunks_whitespace_query(self, retrieval_system):
        """Test that whitespace-only query raises ValueError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            retrieval_system.retrieve_chunks(
                book_id="book_1",
                query="   ",
                top_k=5
            )
    
    def test_retrieve_chunks_none_query(self, retrieval_system):
        """Test that None query raises ValueError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            retrieval_system.retrieve_chunks(
                book_id="book_1",
                query=None,
                top_k=5
            )
    
    def test_retrieve_chunks_invalid_top_k(self, retrieval_system):
        """Test that invalid top_k raises ValueError."""
        with pytest.raises(ValueError, match="top_k must be at least 1"):
            retrieval_system.retrieve_chunks(
                book_id="book_1",
                query="test query",
                top_k=0
            )
        
        with pytest.raises(ValueError, match="top_k must be at least 1"):
            retrieval_system.retrieve_chunks(
                book_id="book_1",
                query="test query",
                top_k=-1
            )
    
    def test_retrieve_chunks_invalid_min_similarity(self, retrieval_system):
        """Test that invalid min_similarity raises ValueError."""
        with pytest.raises(ValueError, match="min_similarity must be in range"):
            retrieval_system.retrieve_chunks(
                book_id="book_1",
                query="test query",
                top_k=5,
                min_similarity=-0.1
            )
        
        with pytest.raises(ValueError, match="min_similarity must be in range"):
            retrieval_system.retrieve_chunks(
                book_id="book_1",
                query="test query",
                top_k=5,
                min_similarity=1.5
            )
    
    def test_retrieve_chunks_multilingual_query(self, embedding_generator, populated_vector_store):
        """Test retrieval with Urdu query (multilingual support)."""
        retrieval_system = RetrievalSystem(embedding_generator, populated_vector_store)
        
        # Urdu query (should not raise an error)
        chunks = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="پودے کیسے توانائی بناتے ہیں؟",  # "How do plants make energy?" in Urdu
            top_k=5,
            min_similarity=0.0
        )
        
        # Should return results (even if not perfectly matched)
        assert isinstance(chunks, list)
    
    def test_retrieve_chunks_with_custom_threshold(self, embedding_generator, populated_vector_store):
        """Test retrieval with custom similarity threshold."""
        retrieval_system = RetrievalSystem(embedding_generator, populated_vector_store)
        
        # Get results with low threshold
        chunks_low = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="photosynthesis",
            top_k=10,
            min_similarity=0.1
        )
        
        # Get results with high threshold
        chunks_high = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="photosynthesis",
            top_k=10,
            min_similarity=0.5
        )
        
        # High threshold should return fewer or equal results
        assert len(chunks_high) <= len(chunks_low)


class TestRetrievalSystemIntegration:
    """Integration tests for RetrievalSystem with real components."""
    
    def test_end_to_end_retrieval(self, embedding_generator, vector_store):
        """Test complete retrieval flow from adding chunks to retrieving them."""
        retrieval_system = RetrievalSystem(embedding_generator, vector_store)
        
        # Create and add chunks
        chunks = [
            Chunk(
                chunk_id="book_test_chunk_0",
                text="The mitochondria is the powerhouse of the cell.",
                page_numbers=[1],
                start_char=0,
                end_char=48,
                metadata={}
            ),
            Chunk(
                chunk_id="book_test_chunk_1",
                text="DNA contains genetic information for all living organisms.",
                page_numbers=[1],
                start_char=49,
                end_char=108,
                metadata={}
            ),
        ]
        
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        vector_store.add_chunks("book_test", chunks, embeddings)
        
        # Retrieve chunks with lower threshold to ensure we get results
        results = retrieval_system.retrieve_chunks(
            book_id="book_test",
            query="What is the function of mitochondria?",
            top_k=2,
            min_similarity=0.0  # Accept all results
        )
        
        # Should find relevant chunk
        assert len(results) > 0
        assert any("mitochondria" in chunk.text.lower() for chunk in results)
    
    def test_multiple_books_isolation(self, embedding_generator, vector_store):
        """Test that retrieval only returns chunks from the specified book."""
        retrieval_system = RetrievalSystem(embedding_generator, vector_store)
        
        # Add chunks for book 1
        chunks_book1 = [
            Chunk(
                chunk_id="book_1_chunk_0",
                text="Book 1 content about cats.",
                page_numbers=[1],
                start_char=0,
                end_char=27,
                metadata={}
            ),
        ]
        embeddings1 = embedding_generator.generate_batch_embeddings([c.text for c in chunks_book1])
        vector_store.add_chunks("book_1", chunks_book1, embeddings1)
        
        # Add chunks for book 2
        chunks_book2 = [
            Chunk(
                chunk_id="book_2_chunk_0",
                text="Book 2 content about dogs.",
                page_numbers=[1],
                start_char=0,
                end_char=27,
                metadata={}
            ),
        ]
        embeddings2 = embedding_generator.generate_batch_embeddings([c.text for c in chunks_book2])
        vector_store.add_chunks("book_2", chunks_book2, embeddings2)
        
        # Query book 1
        results_book1 = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="cats",
            top_k=5,
            min_similarity=0.0
        )
        
        # Should only return chunks from book 1
        assert len(results_book1) > 0
        for chunk in results_book1:
            assert chunk.chunk_id.startswith("book_1_")
        
        # Query book 2
        results_book2 = retrieval_system.retrieve_chunks(
            book_id="book_2",
            query="dogs",
            top_k=5,
            min_similarity=0.0
        )
        
        # Should only return chunks from book 2
        assert len(results_book2) > 0
        for chunk in results_book2:
            assert chunk.chunk_id.startswith("book_2_")
