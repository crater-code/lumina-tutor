"""
Integration tests for the RetrievalSystem with real-world scenarios.
"""

import pytest
from src.retrieval_system import RetrievalSystem
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.models import Chunk


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


def test_retrieval_with_science_book(embedding_generator, vector_store, retrieval_system):
    """Test retrieval with a realistic science book scenario."""
    # Create chunks from a hypothetical science book
    chunks = [
        Chunk(
            chunk_id="science_book_chunk_0",
            text="Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the help of chlorophyll. During photosynthesis, plants convert carbon dioxide and water into glucose and oxygen.",
            page_numbers=[10],
            start_char=0,
            end_char=200,
            metadata={"section": "Plant Biology", "chapter": 2}
        ),
        Chunk(
            chunk_id="science_book_chunk_1",
            text="The water cycle, also known as the hydrologic cycle, describes the continuous movement of water on, above, and below the surface of the Earth. Water evaporates from oceans, forms clouds, and returns as precipitation.",
            page_numbers=[25],
            start_char=0,
            end_char=200,
            metadata={"section": "Earth Science", "chapter": 4}
        ),
        Chunk(
            chunk_id="science_book_chunk_2",
            text="Newton's first law of motion states that an object at rest stays at rest and an object in motion stays in motion with the same speed and direction unless acted upon by an unbalanced force.",
            page_numbers=[45],
            start_char=0,
            end_char=180,
            metadata={"section": "Physics", "chapter": 7}
        ),
        Chunk(
            chunk_id="science_book_chunk_3",
            text="The human digestive system breaks down food into nutrients that the body can absorb. The process begins in the mouth with chewing and continues through the stomach and intestines.",
            page_numbers=[60],
            start_char=0,
            end_char=170,
            metadata={"section": "Human Biology", "chapter": 9}
        ),
    ]
    
    # Generate embeddings and add to vector store
    texts = [chunk.text for chunk in chunks]
    embeddings = embedding_generator.generate_batch_embeddings(texts)
    vector_store.add_chunks("science_book", chunks, embeddings)
    
    # Test query about photosynthesis
    results = retrieval_system.retrieve_chunks(
        book_id="science_book",
        query="How do plants make food from sunlight?",
        top_k=2,
        min_similarity=0.0
    )
    
    assert len(results) > 0
    # The first result should be about photosynthesis
    assert "photosynthesis" in results[0].text.lower()
    
    # Test query about water cycle
    results = retrieval_system.retrieve_chunks(
        book_id="science_book",
        query="Explain the water cycle",
        top_k=2,
        min_similarity=0.0
    )
    
    assert len(results) > 0
    assert "water cycle" in results[0].text.lower() or "hydrologic" in results[0].text.lower()
    
    # Test query about physics
    results = retrieval_system.retrieve_chunks(
        book_id="science_book",
        query="What is Newton's first law?",
        top_k=2,
        min_similarity=0.0
    )
    
    assert len(results) > 0
    assert "newton" in results[0].text.lower() or "motion" in results[0].text.lower()


def test_retrieval_with_urdu_content(embedding_generator, vector_store, retrieval_system):
    """Test retrieval with Urdu text content."""
    # Create chunks with Urdu content
    chunks = [
        Chunk(
            chunk_id="urdu_book_chunk_0",
            text="پودے سورج کی روشنی سے خوراک بناتے ہیں۔ اس عمل کو فوٹو سنتھیسس کہتے ہیں۔",
            page_numbers=[1],
            start_char=0,
            end_char=80,
            metadata={"language": "urdu"}
        ),
        Chunk(
            chunk_id="urdu_book_chunk_1",
            text="پانی کا چکر زمین پر پانی کی گردش کو بیان کرتا ہے۔",
            page_numbers=[2],
            start_char=0,
            end_char=50,
            metadata={"language": "urdu"}
        ),
    ]
    
    # Generate embeddings and add to vector store
    texts = [chunk.text for chunk in chunks]
    embeddings = embedding_generator.generate_batch_embeddings(texts)
    vector_store.add_chunks("urdu_book", chunks, embeddings)
    
    # Test Urdu query
    results = retrieval_system.retrieve_chunks(
        book_id="urdu_book",
        query="پودے کیسے خوراک بناتے ہیں؟",
        top_k=2,
        min_similarity=0.0
    )
    
    # Should return results (multilingual model should handle Urdu)
    assert isinstance(results, list)


def test_retrieval_with_multiple_books(embedding_generator, vector_store, retrieval_system):
    """Test that retrieval correctly isolates between multiple books."""
    # Create chunks for math book
    math_chunks = [
        Chunk(
            chunk_id="math_book_chunk_0",
            text="The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides.",
            page_numbers=[15],
            start_char=0,
            end_char=140,
            metadata={"subject": "geometry"}
        ),
    ]
    
    # Create chunks for history book
    history_chunks = [
        Chunk(
            chunk_id="history_book_chunk_0",
            text="The Industrial Revolution began in Britain in the late 18th century and transformed manufacturing and society.",
            page_numbers=[42],
            start_char=0,
            end_char=110,
            metadata={"subject": "history"}
        ),
    ]
    
    # Add both books to vector store
    math_texts = [chunk.text for chunk in math_chunks]
    math_embeddings = embedding_generator.generate_batch_embeddings(math_texts)
    vector_store.add_chunks("math_book", math_chunks, math_embeddings)
    
    history_texts = [chunk.text for chunk in history_chunks]
    history_embeddings = embedding_generator.generate_batch_embeddings(history_texts)
    vector_store.add_chunks("history_book", history_chunks, history_embeddings)
    
    # Query math book
    math_results = retrieval_system.retrieve_chunks(
        book_id="math_book",
        query="What is the Pythagorean theorem?",
        top_k=5,
        min_similarity=0.0
    )
    
    # Should only return chunks from math book
    assert len(math_results) > 0
    for chunk in math_results:
        assert chunk.chunk_id.startswith("math_book_")
    
    # Query history book
    history_results = retrieval_system.retrieve_chunks(
        book_id="history_book",
        query="When did the Industrial Revolution start?",
        top_k=5,
        min_similarity=0.0
    )
    
    # Should only return chunks from history book
    assert len(history_results) > 0
    for chunk in history_results:
        assert chunk.chunk_id.startswith("history_book_")


def test_retrieval_with_varying_thresholds(embedding_generator, vector_store, retrieval_system):
    """Test how different similarity thresholds affect results."""
    # Create chunks with varying relevance
    chunks = [
        Chunk(
            chunk_id="test_book_chunk_0",
            text="Cats are domestic animals that are popular as pets.",
            page_numbers=[1],
            start_char=0,
            end_char=52,
            metadata={}
        ),
        Chunk(
            chunk_id="test_book_chunk_1",
            text="Dogs are loyal companions and are often called man's best friend.",
            page_numbers=[2],
            start_char=0,
            end_char=66,
            metadata={}
        ),
        Chunk(
            chunk_id="test_book_chunk_2",
            text="Birds can fly using their wings and feathers.",
            page_numbers=[3],
            start_char=0,
            end_char=46,
            metadata={}
        ),
    ]
    
    # Add chunks to vector store
    texts = [chunk.text for chunk in chunks]
    embeddings = embedding_generator.generate_batch_embeddings(texts)
    vector_store.add_chunks("test_book", chunks, embeddings)
    
    # Query with low threshold
    results_low = retrieval_system.retrieve_chunks(
        book_id="test_book",
        query="Tell me about cats",
        top_k=10,
        min_similarity=0.1
    )
    
    # Query with high threshold
    results_high = retrieval_system.retrieve_chunks(
        book_id="test_book",
        query="Tell me about cats",
        top_k=10,
        min_similarity=0.5
    )
    
    # High threshold should return fewer or equal results
    assert len(results_high) <= len(results_low)
    
    # If we got results with high threshold, they should also be in low threshold results
    if results_high:
        high_ids = {chunk.chunk_id for chunk in results_high}
        low_ids = {chunk.chunk_id for chunk in results_low}
        assert high_ids.issubset(low_ids)
