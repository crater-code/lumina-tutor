"""
Integration tests for VectorStore with EmbeddingGenerator.

These tests verify that the VectorStore works correctly with real embeddings
from the EmbeddingGenerator, testing the full flow of adding chunks and
performing semantic search.
"""

import pytest
import shutil
from src.vector_store import VectorStore
from src.embedding_generator import EmbeddingGenerator
from src.models import Chunk


class TestVectorStoreIntegration:
    """Integration test suite for VectorStore with EmbeddingGenerator."""
    
    @pytest.fixture
    def test_storage_dir(self, tmp_path):
        """Create a temporary storage directory for testing."""
        storage_dir = tmp_path / "test_vector_store_integration"
        storage_dir.mkdir()
        yield str(storage_dir)
        # Cleanup after test
        if storage_dir.exists():
            shutil.rmtree(storage_dir)
    
    @pytest.fixture
    def embedding_generator(self):
        """Create an EmbeddingGenerator instance for testing."""
        return EmbeddingGenerator()
    
    @pytest.fixture
    def vector_store(self, test_storage_dir, embedding_generator):
        """Create a VectorStore instance with correct embedding dimension."""
        embedding_dim = embedding_generator.get_embedding_dimension()
        return VectorStore(storage_dir=test_storage_dir, embedding_dim=embedding_dim)
    
    def test_add_and_search_english_chunks(self, vector_store, embedding_generator):
        """Test adding English chunks and searching with English query."""
        book_id = "english_book"
        
        # Create chunks about different topics
        chunks = [
            Chunk(
                chunk_id="book_en_chunk_0",
                text="The cat sat on the mat. Cats are wonderful pets that love to play.",
                page_numbers=[1],
                start_char=0,
                end_char=70,
                metadata={"language": "en"}
            ),
            Chunk(
                chunk_id="book_en_chunk_1",
                text="Dogs are loyal companions. They enjoy walks and playing fetch.",
                page_numbers=[1],
                start_char=71,
                end_char=135,
                metadata={"language": "en"}
            ),
            Chunk(
                chunk_id="book_en_chunk_2",
                text="Birds can fly in the sky. Many birds migrate during winter.",
                page_numbers=[2],
                start_char=136,
                end_char=196,
                metadata={"language": "en"}
            )
        ]
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        
        # Add chunks to vector store
        vector_store.add_chunks(book_id, chunks, embeddings)
        
        # Search for cat-related content
        query = "Tell me about cats"
        query_embedding = embedding_generator.generate_embedding(query)
        results = vector_store.search(book_id, query_embedding, top_k=3)
        
        # Should return results
        assert len(results) > 0
        
        # First result should be about cats
        best_chunk, best_score = results[0]
        assert "cat" in best_chunk.text.lower()
        # Similarity score should be positive (L2 distance converted to similarity)
        assert best_score > 0.0
    
    def test_add_and_search_urdu_chunks(self, vector_store, embedding_generator):
        """Test adding Urdu chunks and searching with Urdu query."""
        book_id = "urdu_book"
        
        # Create Urdu chunks
        chunks = [
            Chunk(
                chunk_id="book_ur_chunk_0",
                text="بلی چٹائی پر بیٹھی ہے۔ بلیاں بہترین پالتو جانور ہیں۔",
                page_numbers=[1],
                start_char=0,
                end_char=50,
                metadata={"language": "ur"}
            ),
            Chunk(
                chunk_id="book_ur_chunk_1",
                text="کتے وفادار ساتھی ہیں۔ وہ سیر اور کھیلنا پسند کرتے ہیں۔",
                page_numbers=[1],
                start_char=51,
                end_char=100,
                metadata={"language": "ur"}
            ),
            Chunk(
                chunk_id="book_ur_chunk_2",
                text="پرندے آسمان میں اڑ سکتے ہیں۔ بہت سے پرندے سردیوں میں ہجرت کرتے ہیں۔",
                page_numbers=[2],
                start_char=101,
                end_char=160,
                metadata={"language": "ur"}
            )
        ]
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        
        # Add chunks to vector store
        vector_store.add_chunks(book_id, chunks, embeddings)
        
        # Search with Urdu query
        query = "بلی کے بارے میں بتائیں"  # Tell me about cats
        query_embedding = embedding_generator.generate_embedding(query)
        results = vector_store.search(book_id, query_embedding, top_k=3)
        
        # Should return results
        assert len(results) > 0
        
        # First result should be about cats
        best_chunk, best_score = results[0]
        assert "بلی" in best_chunk.text  # "cat" in Urdu
        assert best_score > 0.0
    
    def test_semantic_search_quality(self, vector_store, embedding_generator):
        """Test that semantic search returns relevant results."""
        book_id = "test_book"
        
        # Create chunks with different topics
        chunks = [
            Chunk(
                chunk_id="chunk_0",
                text="Python is a programming language used for web development and data science.",
                page_numbers=[1],
                start_char=0,
                end_char=77,
                metadata={"language": "en"}
            ),
            Chunk(
                chunk_id="chunk_1",
                text="Machine learning is a subset of artificial intelligence that learns from data.",
                page_numbers=[1],
                start_char=78,
                end_char=157,
                metadata={"language": "en"}
            ),
            Chunk(
                chunk_id="chunk_2",
                text="Cooking pasta requires boiling water and adding salt for flavor.",
                page_numbers=[2],
                start_char=158,
                end_char=223,
                metadata={"language": "en"}
            ),
            Chunk(
                chunk_id="chunk_3",
                text="Neural networks are computational models inspired by the human brain.",
                page_numbers=[2],
                start_char=224,
                end_char=294,
                metadata={"language": "en"}
            )
        ]
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        
        # Add chunks
        vector_store.add_chunks(book_id, chunks, embeddings)
        
        # Search for AI-related content
        query = "What is artificial intelligence?"
        query_embedding = embedding_generator.generate_embedding(query)
        results = vector_store.search(book_id, query_embedding, top_k=2)
        
        # Should return AI-related chunks (chunks 1 and 3)
        assert len(results) >= 1
        
        # Top results should be about AI/ML, not cooking
        top_chunk_ids = [chunk.chunk_id for chunk, score in results]
        assert "chunk_1" in top_chunk_ids or "chunk_3" in top_chunk_ids
        assert "chunk_2" not in top_chunk_ids[:1]  # Cooking should not be first
    
    def test_multiple_books_isolation(self, vector_store, embedding_generator):
        """Test that searches are isolated to specific books."""
        book_id_1 = "book_cats"
        book_id_2 = "book_dogs"
        
        # Create cat chunks
        cat_chunks = [
            Chunk(
                chunk_id="cat_chunk_0",
                text="Cats are independent animals that enjoy solitude.",
                page_numbers=[1],
                start_char=0,
                end_char=51,
                metadata={"language": "en"}
            )
        ]
        
        # Create dog chunks
        dog_chunks = [
            Chunk(
                chunk_id="dog_chunk_0",
                text="Dogs are social animals that love companionship.",
                page_numbers=[1],
                start_char=0,
                end_char=50,
                metadata={"language": "en"}
            )
        ]
        
        # Generate embeddings and add to store
        cat_embeddings = embedding_generator.generate_batch_embeddings([c.text for c in cat_chunks])
        dog_embeddings = embedding_generator.generate_batch_embeddings([c.text for c in dog_chunks])
        
        vector_store.add_chunks(book_id_1, cat_chunks, cat_embeddings)
        vector_store.add_chunks(book_id_2, dog_chunks, dog_embeddings)
        
        # Search in cat book
        query = "Tell me about pets"
        query_embedding = embedding_generator.generate_embedding(query)
        
        cat_results = vector_store.search(book_id_1, query_embedding, top_k=10)
        dog_results = vector_store.search(book_id_2, query_embedding, top_k=10)
        
        # Each search should only return chunks from its own book
        assert len(cat_results) > 0
        assert all("cat" in chunk.chunk_id for chunk, score in cat_results)
        
        assert len(dog_results) > 0
        assert all("dog" in chunk.chunk_id for chunk, score in dog_results)
    
    def test_no_results_for_irrelevant_query(self, vector_store, embedding_generator):
        """Test that irrelevant queries return few or no results with high threshold."""
        book_id = "science_book"
        
        # Create science-related chunks
        chunks = [
            Chunk(
                chunk_id="science_chunk_0",
                text="Photosynthesis is the process by which plants convert sunlight into energy.",
                page_numbers=[1],
                start_char=0,
                end_char=76,
                metadata={"language": "en"}
            ),
            Chunk(
                chunk_id="science_chunk_1",
                text="The water cycle describes how water moves through the environment.",
                page_numbers=[1],
                start_char=77,
                end_char=144,
                metadata={"language": "en"}
            )
        ]
        
        # Generate embeddings and add to store
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        vector_store.add_chunks(book_id, chunks, embeddings)
        
        # Search with completely unrelated query
        query = "How do I bake a chocolate cake?"
        query_embedding = embedding_generator.generate_embedding(query)
        results = vector_store.search(book_id, query_embedding, top_k=5, min_similarity=0.5)
        
        # Should return few or no results due to low similarity
        assert len(results) <= 1
    
    def test_persistence_with_real_embeddings(self, test_storage_dir, embedding_generator):
        """Test that vector store persists and loads correctly with real embeddings."""
        book_id = "persistent_book"
        
        # Create chunks
        chunks = [
            Chunk(
                chunk_id="persist_chunk_0",
                text="This is a test chunk for persistence.",
                page_numbers=[1],
                start_char=0,
                end_char=38,
                metadata={"language": "en"}
            )
        ]
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        
        # Create first store instance and add data
        embedding_dim = embedding_generator.get_embedding_dimension()
        store1 = VectorStore(storage_dir=test_storage_dir, embedding_dim=embedding_dim)
        store1.add_chunks(book_id, chunks, embeddings)
        
        # Create second store instance (should load from disk)
        store2 = VectorStore(storage_dir=test_storage_dir, embedding_dim=embedding_dim)
        
        # Search in second instance
        query = "test persistence"
        query_embedding = embedding_generator.generate_embedding(query)
        results = store2.search(book_id, query_embedding, top_k=1)
        
        # Should find the chunk
        assert len(results) > 0
        assert results[0][0].chunk_id == "persist_chunk_0"
    
    def test_large_scale_search(self, vector_store, embedding_generator):
        """Test search performance with a larger number of chunks."""
        book_id = "large_book"
        
        # Create 50 chunks with different content
        chunks = []
        for i in range(50):
            chunk = Chunk(
                chunk_id=f"large_chunk_{i}",
                text=f"This is chunk number {i} about topic {i % 10}. It contains unique content.",
                page_numbers=[i // 10 + 1],
                start_char=i * 80,
                end_char=(i + 1) * 80,
                metadata={"language": "en"}
            )
            chunks.append(chunk)
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        
        # Add chunks
        vector_store.add_chunks(book_id, chunks, embeddings)
        
        # Search
        query = "Tell me about topic 5"
        query_embedding = embedding_generator.generate_embedding(query)
        results = vector_store.search(book_id, query_embedding, top_k=5)
        
        # Should return results
        assert len(results) > 0
        assert len(results) <= 5
        
        # Results should be ordered by similarity
        for i in range(len(results) - 1):
            assert results[i][1] >= results[i + 1][1]
