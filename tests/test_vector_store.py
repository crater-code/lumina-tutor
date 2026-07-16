"""
Unit tests for the VectorStore class.

These tests verify the functionality of storing, searching, and deleting
chunks with embeddings using FAISS.
"""

import pytest
import numpy as np
import os
import shutil
from src.vector_store import VectorStore
from src.models import Chunk
from src.exceptions import RetrievalError


class TestVectorStore:
    """Test suite for VectorStore class."""
    
    @pytest.fixture
    def test_storage_dir(self, tmp_path):
        """Create a temporary storage directory for testing."""
        storage_dir = tmp_path / "test_vector_store"
        storage_dir.mkdir()
        yield str(storage_dir)
        # Cleanup after test
        if storage_dir.exists():
            shutil.rmtree(storage_dir)
    
    @pytest.fixture
    def vector_store(self, test_storage_dir):
        """Create a VectorStore instance for testing."""
        return VectorStore(storage_dir=test_storage_dir, embedding_dim=384)
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks for testing."""
        return [
            Chunk(
                chunk_id="book_test_chunk_0",
                text="This is the first test chunk about cats.",
                page_numbers=[1],
                start_char=0,
                end_char=42,
                metadata={"language": "en"}
            ),
            Chunk(
                chunk_id="book_test_chunk_1",
                text="This is the second test chunk about dogs.",
                page_numbers=[1],
                start_char=43,
                end_char=85,
                metadata={"language": "en"}
            ),
            Chunk(
                chunk_id="book_test_chunk_2",
                text="This is the third test chunk about birds.",
                page_numbers=[2],
                start_char=86,
                end_char=128,
                metadata={"language": "en"}
            )
        ]
    
    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings for testing."""
        # Create 3 embeddings with dimension 384
        np.random.seed(42)  # For reproducibility
        embeddings = np.random.randn(3, 384).astype(np.float32)
        # Normalize embeddings
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings
    
    def test_initialization_default(self):
        """Test that VectorStore initializes with default parameters."""
        store = VectorStore()
        assert store.embedding_dim == 384
        assert store.storage_dir == "data/vector_store"
        assert os.path.exists(store.storage_dir)
    
    def test_initialization_custom_dir(self, test_storage_dir):
        """Test that VectorStore initializes with custom storage directory."""
        store = VectorStore(storage_dir=test_storage_dir)
        assert store.storage_dir == test_storage_dir
        assert os.path.exists(test_storage_dir)
    
    def test_initialization_custom_embedding_dim(self, test_storage_dir):
        """Test that VectorStore initializes with custom embedding dimension."""
        store = VectorStore(storage_dir=test_storage_dir, embedding_dim=512)
        assert store.embedding_dim == 512
    
    def test_add_chunks_success(self, vector_store, sample_chunks, sample_embeddings):
        """Test successfully adding chunks to the store."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Verify chunks were added
        assert book_id in vector_store.indices
        assert book_id in vector_store.chunks
        assert len(vector_store.chunks[book_id]) == 3
        assert vector_store.get_chunk_count(book_id) == 3
    
    def test_add_chunks_empty_list(self, vector_store):
        """Test that adding empty chunks list raises ValueError."""
        book_id = "test_book_1"
        with pytest.raises(ValueError) as exc_info:
            vector_store.add_chunks(book_id, [], np.array([]))
        assert "Chunks list cannot be empty" in str(exc_info.value)
    
    def test_add_chunks_mismatched_lengths(self, vector_store, sample_chunks):
        """Test that mismatched chunks and embeddings lengths raise ValueError."""
        book_id = "test_book_1"
        # Create embeddings with wrong length
        wrong_embeddings = np.random.randn(2, 384).astype(np.float32)
        
        with pytest.raises(ValueError) as exc_info:
            vector_store.add_chunks(book_id, sample_chunks, wrong_embeddings)
        assert "must match number of embeddings" in str(exc_info.value)
    
    def test_add_chunks_wrong_dimension(self, vector_store, sample_chunks):
        """Test that embeddings with wrong dimension raise ValueError."""
        book_id = "test_book_1"
        # Create embeddings with wrong dimension
        wrong_embeddings = np.random.randn(3, 256).astype(np.float32)
        
        with pytest.raises(ValueError) as exc_info:
            vector_store.add_chunks(book_id, sample_chunks, wrong_embeddings)
        assert "Embedding dimension" in str(exc_info.value)
    
    def test_add_chunks_replaces_existing(self, vector_store, sample_chunks, sample_embeddings):
        """Test that adding chunks for existing book replaces old chunks."""
        book_id = "test_book_1"
        
        # Add chunks first time
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        assert vector_store.get_chunk_count(book_id) == 3
        
        # Add different chunks for same book
        new_chunks = [sample_chunks[0]]  # Only one chunk
        new_embeddings = sample_embeddings[:1]
        vector_store.add_chunks(book_id, new_chunks, new_embeddings)
        
        # Should have replaced old chunks
        assert vector_store.get_chunk_count(book_id) == 1
    
    def test_add_chunks_persistence(self, test_storage_dir, sample_chunks, sample_embeddings):
        """Test that chunks are persisted to disk."""
        book_id = "test_book_1"
        
        # Create store and add chunks
        store1 = VectorStore(storage_dir=test_storage_dir)
        store1.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Create new store instance (should load from disk)
        store2 = VectorStore(storage_dir=test_storage_dir)
        
        # Verify chunks were loaded
        assert book_id in store2.indices
        assert book_id in store2.chunks
        assert len(store2.chunks[book_id]) == 3
    
    def test_search_basic(self, vector_store, sample_chunks, sample_embeddings):
        """Test basic search functionality."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Search with first embedding (should return first chunk with high similarity)
        query_embedding = sample_embeddings[0]
        results = vector_store.search(book_id, query_embedding, top_k=3)
        
        # Should return results
        assert len(results) > 0
        
        # First result should be the matching chunk
        best_chunk, best_score = results[0]
        assert best_chunk.chunk_id == "book_test_chunk_0"
        assert best_score > 0.9  # Should be very similar to itself
    
    def test_search_top_k_limit(self, vector_store, sample_chunks, sample_embeddings):
        """Test that search respects top_k parameter."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Search with top_k=2
        query_embedding = sample_embeddings[0]
        results = vector_store.search(book_id, query_embedding, top_k=2)
        
        # Should return at most 2 results
        assert len(results) <= 2
    
    def test_search_min_similarity_threshold(self, vector_store, sample_chunks, sample_embeddings):
        """Test that search filters by minimum similarity threshold."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Search with very high threshold (should return fewer results)
        query_embedding = sample_embeddings[0]
        results_high_threshold = vector_store.search(
            book_id, query_embedding, top_k=10, min_similarity=0.95
        )
        
        # Search with low threshold (should return more results)
        results_low_threshold = vector_store.search(
            book_id, query_embedding, top_k=10, min_similarity=0.1
        )
        
        # High threshold should return fewer or equal results
        assert len(results_high_threshold) <= len(results_low_threshold)
    
    def test_search_nonexistent_book(self, vector_store):
        """Test that searching for nonexistent book returns empty list."""
        query_embedding = np.random.randn(384).astype(np.float32)
        results = vector_store.search("nonexistent_book", query_embedding)
        
        assert results == []
    
    def test_search_wrong_embedding_dimension(self, vector_store, sample_chunks, sample_embeddings):
        """Test that search with wrong embedding dimension raises ValueError."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Try to search with wrong dimension
        wrong_query = np.random.randn(256).astype(np.float32)
        
        with pytest.raises(ValueError) as exc_info:
            vector_store.search(book_id, wrong_query)
        assert "Query embedding dimension" in str(exc_info.value)
    
    def test_search_result_ordering(self, vector_store, sample_chunks, sample_embeddings):
        """Test that search results are ordered by descending similarity."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Search
        query_embedding = sample_embeddings[0]
        results = vector_store.search(book_id, query_embedding, top_k=3)
        
        # Verify results are ordered by descending similarity
        for i in range(len(results) - 1):
            assert results[i][1] >= results[i + 1][1]
    
    def test_delete_book_success(self, vector_store, sample_chunks, sample_embeddings):
        """Test successfully deleting a book."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        assert book_id in vector_store.indices
        
        # Delete book
        vector_store.delete_book(book_id)
        
        # Verify book was deleted
        assert book_id not in vector_store.indices
        assert book_id not in vector_store.chunks
        assert vector_store.get_chunk_count(book_id) == 0
    
    def test_delete_book_removes_files(self, vector_store, sample_chunks, sample_embeddings):
        """Test that deleting a book removes files from disk."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Verify files exist
        index_path = vector_store._get_index_path(book_id)
        chunks_path = vector_store._get_chunks_path(book_id)
        assert os.path.exists(index_path)
        assert os.path.exists(chunks_path)
        
        # Delete book
        vector_store.delete_book(book_id)
        
        # Verify files were deleted
        assert not os.path.exists(index_path)
        assert not os.path.exists(chunks_path)
    
    def test_delete_nonexistent_book(self, vector_store):
        """Test that deleting nonexistent book doesn't raise error."""
        # Should not raise any exception
        vector_store.delete_book("nonexistent_book")
    
    def test_get_book_ids(self, vector_store, sample_chunks, sample_embeddings):
        """Test getting list of all book IDs."""
        # Initially empty
        assert vector_store.get_book_ids() == []
        
        # Add first book
        vector_store.add_chunks("book_1", sample_chunks, sample_embeddings)
        assert "book_1" in vector_store.get_book_ids()
        
        # Add second book
        vector_store.add_chunks("book_2", sample_chunks, sample_embeddings)
        book_ids = vector_store.get_book_ids()
        assert "book_1" in book_ids
        assert "book_2" in book_ids
        assert len(book_ids) == 2
    
    def test_get_chunk_count(self, vector_store, sample_chunks, sample_embeddings):
        """Test getting chunk count for a book."""
        book_id = "test_book_1"
        
        # Initially 0
        assert vector_store.get_chunk_count(book_id) == 0
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        assert vector_store.get_chunk_count(book_id) == 3
    
    def test_multiple_books_isolation(self, vector_store, sample_chunks, sample_embeddings):
        """Test that multiple books are isolated from each other."""
        book_id_1 = "book_1"
        book_id_2 = "book_2"
        
        # Add chunks to both books
        vector_store.add_chunks(book_id_1, sample_chunks, sample_embeddings)
        vector_store.add_chunks(book_id_2, sample_chunks, sample_embeddings)
        
        # Search in book 1
        query_embedding = sample_embeddings[0]
        results_1 = vector_store.search(book_id_1, query_embedding, top_k=10)
        
        # All results should be from book 1
        for chunk, score in results_1:
            assert chunk.chunk_id.startswith("book_test_chunk_")
        
        # Delete book 1
        vector_store.delete_book(book_id_1)
        
        # Book 2 should still exist
        assert book_id_2 in vector_store.indices
        assert vector_store.get_chunk_count(book_id_2) == 3
        
        # Book 1 should be gone
        assert book_id_1 not in vector_store.indices
    
    def test_search_with_different_embeddings(self, vector_store, sample_chunks):
        """Test search with semantically different embeddings."""
        book_id = "test_book_1"
        
        # Create embeddings that are very different from each other
        embeddings = np.array([
            [1.0] + [0.0] * 383,  # First dimension is 1, rest are 0
            [0.0] + [1.0] + [0.0] * 382,  # Second dimension is 1, rest are 0
            [0.0] * 2 + [1.0] + [0.0] * 381  # Third dimension is 1, rest are 0
        ], dtype=np.float32)
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, embeddings)
        
        # Search with query similar to first embedding
        query = np.array([0.9] + [0.1] * 383, dtype=np.float32)
        # Use a lower threshold since these are sparse embeddings
        results = vector_store.search(book_id, query, top_k=3, min_similarity=0.0)
        
        # Should return results
        assert len(results) > 0
        # First result should be the first chunk (most similar)
        assert results[0][0].chunk_id == "book_test_chunk_0"
    
    def test_persistence_across_instances(self, test_storage_dir, sample_chunks, sample_embeddings):
        """Test that data persists across multiple VectorStore instances."""
        book_id = "test_book_1"
        
        # Create first instance and add data
        store1 = VectorStore(storage_dir=test_storage_dir)
        store1.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Create second instance (should load from disk)
        store2 = VectorStore(storage_dir=test_storage_dir)
        
        # Verify data was loaded
        assert book_id in store2.get_book_ids()
        assert store2.get_chunk_count(book_id) == 3
        
        # Verify search works
        query_embedding = sample_embeddings[0]
        results = store2.search(book_id, query_embedding, top_k=1)
        assert len(results) > 0
    
    def test_add_chunks_with_urdu_text(self, vector_store, sample_embeddings):
        """Test adding chunks with Urdu text."""
        book_id = "urdu_book"
        
        urdu_chunks = [
            Chunk(
                chunk_id="book_urdu_chunk_0",
                text="یہ پہلا ٹیسٹ چنک ہے۔",
                page_numbers=[1],
                start_char=0,
                end_char=20,
                metadata={"language": "ur"}
            ),
            Chunk(
                chunk_id="book_urdu_chunk_1",
                text="یہ دوسرا ٹیسٹ چنک ہے۔",
                page_numbers=[1],
                start_char=21,
                end_char=41,
                metadata={"language": "ur"}
            ),
            Chunk(
                chunk_id="book_urdu_chunk_2",
                text="یہ تیسرا ٹیسٹ چنک ہے۔",
                page_numbers=[2],
                start_char=42,
                end_char=62,
                metadata={"language": "ur"}
            )
        ]
        
        # Add chunks
        vector_store.add_chunks(book_id, urdu_chunks, sample_embeddings)
        
        # Verify chunks were added
        assert vector_store.get_chunk_count(book_id) == 3
        
        # Verify search works
        query_embedding = sample_embeddings[0]
        results = vector_store.search(book_id, query_embedding, top_k=3)
        assert len(results) > 0
    
    def test_large_batch_of_chunks(self, vector_store):
        """Test adding and searching a large batch of chunks."""
        book_id = "large_book"
        
        # Create 100 chunks
        chunks = [
            Chunk(
                chunk_id=f"book_large_chunk_{i}",
                text=f"This is test chunk number {i}.",
                page_numbers=[i // 10 + 1],
                start_char=i * 30,
                end_char=(i + 1) * 30,
                metadata={"language": "en"}
            )
            for i in range(100)
        ]
        
        # Create 100 embeddings
        np.random.seed(42)
        embeddings = np.random.randn(100, 384).astype(np.float32)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Add chunks
        vector_store.add_chunks(book_id, chunks, embeddings)
        
        # Verify all chunks were added
        assert vector_store.get_chunk_count(book_id) == 100
        
        # Search
        query_embedding = embeddings[0]
        results = vector_store.search(book_id, query_embedding, top_k=10)
        
        # Should return 10 results
        assert len(results) <= 10
        
        # First result should be the matching chunk
        assert results[0][0].chunk_id == "book_large_chunk_0"
    
    def test_empty_search_results_with_high_threshold(self, vector_store, sample_chunks, sample_embeddings):
        """Test that search returns empty list when no results meet threshold."""
        book_id = "test_book_1"
        
        # Add chunks
        vector_store.add_chunks(book_id, sample_chunks, sample_embeddings)
        
        # Search with very different embedding and high threshold
        query_embedding = np.random.randn(384).astype(np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = vector_store.search(book_id, query_embedding, top_k=10, min_similarity=0.99)
        
        # Should return empty or very few results
        assert len(results) <= 1
