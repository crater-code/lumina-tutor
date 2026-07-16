"""
Integration tests for ChatbotEngine with other system components.
"""

import pytest
import os
from src.chatbot_engine import ChatbotEngine
from src.retrieval_system import RetrievalSystem
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.models import Chunk, Response


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
def chatbot_engine():
    """Create a ChatbotEngine instance for testing."""
    os.environ["USE_MOCK_LLM"] = "true"
    return ChatbotEngine()


@pytest.fixture
def sample_book_chunks():
    """Create sample book chunks for testing."""
    return [
        Chunk(
            chunk_id="book_bio_chunk_0",
            text="Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water. Photosynthesis in plants generally involves the green pigment chlorophyll and generates oxygen as a by-product.",
            page_numbers=[1],
            start_char=0,
            end_char=250,
            metadata={"section": "Biology", "topic": "Photosynthesis"}
        ),
        Chunk(
            chunk_id="book_bio_chunk_1",
            text="Cellular respiration is a set of metabolic reactions that take place in the cells of organisms to convert biochemical energy from nutrients into adenosine triphosphate (ATP), and then release waste products.",
            page_numbers=[2],
            start_char=0,
            end_char=210,
            metadata={"section": "Biology", "topic": "Cellular Respiration"}
        ),
        Chunk(
            chunk_id="book_bio_chunk_2",
            text="DNA, or deoxyribonucleic acid, is the hereditary material in humans and almost all other organisms. Nearly every cell in a person's body has the same DNA. Most DNA is located in the cell nucleus.",
            page_numbers=[3],
            start_char=0,
            end_char=200,
            metadata={"section": "Biology", "topic": "DNA"}
        ),
        Chunk(
            chunk_id="book_bio_chunk_3",
            text="The water cycle, also known as the hydrologic cycle, describes the continuous movement of water on, above and below the surface of the Earth. Water evaporates from the surface, condenses in clouds, and falls back as precipitation.",
            page_numbers=[4],
            start_char=0,
            end_char=235,
            metadata={"section": "Earth Science", "topic": "Water Cycle"}
        ),
    ]


class TestChatbotWithRetrieval:
    """Integration tests for ChatbotEngine with RetrievalSystem."""
    
    def test_end_to_end_query_response_flow(
        self,
        chatbot_engine,
        retrieval_system,
        embedding_generator,
        vector_store,
        sample_book_chunks
    ):
        """Test complete flow: add chunks → retrieve → generate response."""
        # Step 1: Add chunks to vector store
        texts = [chunk.text for chunk in sample_book_chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        vector_store.add_chunks("book_bio", sample_book_chunks, embeddings)
        
        # Step 2: Retrieve relevant chunks
        retrieved_chunks = retrieval_system.retrieve_chunks(
            book_id="book_bio",
            query="How do plants make energy?",
            top_k=3,
            min_similarity=0.0
        )
        
        # Should retrieve at least one chunk
        assert len(retrieved_chunks) > 0
        
        # Step 3: Generate response using retrieved chunks
        response = chatbot_engine.generate_response(
            query="How do plants make energy?",
            retrieved_chunks=retrieved_chunks,
            user_age=10,
            language="en"
        )
        
        # Verify response
        assert isinstance(response, Response)
        assert len(response.text) > 0
        assert response.is_refusal is False
        assert len(response.chunk_ids) > 0
        
        # Verify chunk IDs match retrieved chunks
        for chunk_id in response.chunk_ids:
            assert any(chunk.chunk_id == chunk_id for chunk in retrieved_chunks)
    
    def test_query_with_no_relevant_chunks(
        self,
        chatbot_engine,
        retrieval_system,
        embedding_generator,
        vector_store,
        sample_book_chunks
    ):
        """Test flow when no relevant chunks are found."""
        # Add chunks to vector store
        texts = [chunk.text for chunk in sample_book_chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        vector_store.add_chunks("book_bio", sample_book_chunks, embeddings)
        
        # Retrieve with very high similarity threshold
        retrieved_chunks = retrieval_system.retrieve_chunks(
            book_id="book_bio",
            query="What is quantum entanglement?",
            top_k=3,
            min_similarity=0.99  # Very high threshold
        )
        
        # Should retrieve no chunks
        assert len(retrieved_chunks) == 0
        
        # Generate refusal message
        response = chatbot_engine.generate_refusal(
            query="What is quantum entanglement?",
            user_age=10,
            language="en"
        )
        
        # Verify refusal
        assert isinstance(response, Response)
        assert response.is_refusal is True
        assert len(response.chunk_ids) == 0
        assert "book" in response.text.lower()
    
    def test_age_adaptive_responses(
        self,
        chatbot_engine,
        retrieval_system,
        embedding_generator,
        vector_store,
        sample_book_chunks
    ):
        """Test that responses adapt to different age groups."""
        # Add chunks to vector store
        texts = [chunk.text for chunk in sample_book_chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        vector_store.add_chunks("book_bio", sample_book_chunks, embeddings)
        
        # Retrieve chunks
        retrieved_chunks = retrieval_system.retrieve_chunks(
            book_id="book_bio",
            query="What is photosynthesis?",
            top_k=2,
            min_similarity=0.0
        )
        
        assert len(retrieved_chunks) > 0
        
        # Generate responses for different age groups
        response_young = chatbot_engine.generate_response(
            query="What is photosynthesis?",
            retrieved_chunks=retrieved_chunks,
            user_age=6,
            language="en"
        )
        
        response_middle = chatbot_engine.generate_response(
            query="What is photosynthesis?",
            retrieved_chunks=retrieved_chunks,
            user_age=14,
            language="en"
        )
        
        # Verify both responses are valid
        assert response_young.metadata["age_group"] == "young_child"
        assert response_middle.metadata["age_group"] == "middle_school"
        assert response_young.is_refusal is False
        assert response_middle.is_refusal is False
    
    def test_multilingual_query_and_response(
        self,
        chatbot_engine,
        retrieval_system,
        embedding_generator,
        vector_store,
        sample_book_chunks
    ):
        """Test multilingual support (English and Urdu)."""
        # Add chunks to vector store
        texts = [chunk.text for chunk in sample_book_chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        vector_store.add_chunks("book_bio", sample_book_chunks, embeddings)
        
        # English query
        retrieved_chunks_en = retrieval_system.retrieve_chunks(
            book_id="book_bio",
            query="What is DNA?",
            top_k=2,
            min_similarity=0.0
        )
        
        response_en = chatbot_engine.generate_response(
            query="What is DNA?",
            retrieved_chunks=retrieved_chunks_en,
            user_age=10,
            language="en"
        )
        
        # Urdu query
        retrieved_chunks_ur = retrieval_system.retrieve_chunks(
            book_id="book_bio",
            query="ڈی این اے کیا ہے؟",  # "What is DNA?" in Urdu
            top_k=2,
            min_similarity=0.0
        )
        
        response_ur = chatbot_engine.generate_response(
            query="ڈی این اے کیا ہے؟",
            retrieved_chunks=retrieved_chunks_ur,
            user_age=10,
            language="ur"
        )
        
        # Verify both responses
        assert response_en.metadata["language"] == "en"
        assert response_ur.metadata["language"] == "ur"
        assert response_en.is_refusal is False
        assert response_ur.is_refusal is False
    
    def test_multiple_books_isolation(
        self,
        chatbot_engine,
        retrieval_system,
        embedding_generator,
        vector_store
    ):
        """Test that responses only use chunks from the selected book."""
        # Create chunks for two different books
        book1_chunks = [
            Chunk(
                chunk_id="book_1_chunk_0",
                text="Cats are domesticated mammals that are often kept as pets. They are known for their independence and hunting skills.",
                page_numbers=[1],
                start_char=0,
                end_char=110,
                metadata={"book": "Animals"}
            ),
        ]
        
        book2_chunks = [
            Chunk(
                chunk_id="book_2_chunk_0",
                text="Dogs are domesticated mammals that are often kept as pets. They are known for their loyalty and companionship.",
                page_numbers=[1],
                start_char=0,
                end_char=110,
                metadata={"book": "Pets"}
            ),
        ]
        
        # Add chunks for both books
        embeddings1 = embedding_generator.generate_batch_embeddings([c.text for c in book1_chunks])
        vector_store.add_chunks("book_1", book1_chunks, embeddings1)
        
        embeddings2 = embedding_generator.generate_batch_embeddings([c.text for c in book2_chunks])
        vector_store.add_chunks("book_2", book2_chunks, embeddings2)
        
        # Query book 1
        retrieved_chunks_1 = retrieval_system.retrieve_chunks(
            book_id="book_1",
            query="Tell me about cats",
            top_k=5,
            min_similarity=0.0
        )
        
        response_1 = chatbot_engine.generate_response(
            query="Tell me about cats",
            retrieved_chunks=retrieved_chunks_1,
            user_age=10,
            language="en"
        )
        
        # Verify only book 1 chunks are used
        assert all(chunk_id.startswith("book_1_") for chunk_id in response_1.chunk_ids)
        
        # Query book 2
        retrieved_chunks_2 = retrieval_system.retrieve_chunks(
            book_id="book_2",
            query="Tell me about dogs",
            top_k=5,
            min_similarity=0.0
        )
        
        response_2 = chatbot_engine.generate_response(
            query="Tell me about dogs",
            retrieved_chunks=retrieved_chunks_2,
            user_age=10,
            language="en"
        )
        
        # Verify only book 2 chunks are used
        assert all(chunk_id.startswith("book_2_") for chunk_id in response_2.chunk_ids)
    
    def test_chunk_citation_traceability(
        self,
        chatbot_engine,
        retrieval_system,
        embedding_generator,
        vector_store,
        sample_book_chunks
    ):
        """Test that all chunk IDs in response are traceable to retrieved chunks."""
        # Add chunks to vector store
        texts = [chunk.text for chunk in sample_book_chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        vector_store.add_chunks("book_bio", sample_book_chunks, embeddings)
        
        # Retrieve chunks
        retrieved_chunks = retrieval_system.retrieve_chunks(
            book_id="book_bio",
            query="What is cellular respiration?",
            top_k=3,
            min_similarity=0.0
        )
        
        # Generate response
        response = chatbot_engine.generate_response(
            query="What is cellular respiration?",
            retrieved_chunks=retrieved_chunks,
            user_age=10,
            language="en"
        )
        
        # Verify all chunk IDs in response are from retrieved chunks
        retrieved_chunk_ids = {chunk.chunk_id for chunk in retrieved_chunks}
        for chunk_id in response.chunk_ids:
            assert chunk_id in retrieved_chunk_ids, f"Chunk ID {chunk_id} not in retrieved chunks"
    
    def test_response_with_single_chunk(
        self,
        chatbot_engine,
        retrieval_system,
        embedding_generator,
        vector_store
    ):
        """Test response generation with only one retrieved chunk."""
        # Create a single chunk
        single_chunk = [
            Chunk(
                chunk_id="book_single_chunk_0",
                text="The Earth is the third planet from the Sun and the only astronomical object known to harbor life.",
                page_numbers=[1],
                start_char=0,
                end_char=100,
                metadata={}
            ),
        ]
        
        # Add to vector store
        embeddings = embedding_generator.generate_batch_embeddings([c.text for c in single_chunk])
        vector_store.add_chunks("book_single", single_chunk, embeddings)
        
        # Retrieve
        retrieved_chunks = retrieval_system.retrieve_chunks(
            book_id="book_single",
            query="What is Earth?",
            top_k=1,
            min_similarity=0.0
        )
        
        assert len(retrieved_chunks) == 1
        
        # Generate response
        response = chatbot_engine.generate_response(
            query="What is Earth?",
            retrieved_chunks=retrieved_chunks,
            user_age=10,
            language="en"
        )
        
        # Verify response uses the single chunk
        assert len(response.chunk_ids) == 1
        assert response.chunk_ids[0] == "book_single_chunk_0"
        assert response.is_refusal is False


class TestRefusalScenarios:
    """Integration tests for refusal scenarios."""
    
    def test_refusal_for_off_topic_query(
        self,
        chatbot_engine,
        retrieval_system,
        embedding_generator,
        vector_store,
        sample_book_chunks
    ):
        """Test refusal when query is completely off-topic."""
        # Add biology chunks
        texts = [chunk.text for chunk in sample_book_chunks]
        embeddings = embedding_generator.generate_batch_embeddings(texts)
        vector_store.add_chunks("book_bio", sample_book_chunks, embeddings)
        
        # Query about unrelated topic with high threshold
        retrieved_chunks = retrieval_system.retrieve_chunks(
            book_id="book_bio",
            query="How do I bake a cake?",
            top_k=3,
            min_similarity=0.8
        )
        
        # If no chunks retrieved, generate refusal
        if len(retrieved_chunks) == 0:
            response = chatbot_engine.generate_refusal(
                query="How do I bake a cake?",
                user_age=10,
                language="en"
            )
            
            assert response.is_refusal is True
            assert len(response.chunk_ids) == 0
            assert "book" in response.text.lower()
    
    def test_refusal_messages_for_all_ages(self, chatbot_engine):
        """Test that refusal messages work for all age groups."""
        for age in range(4, 16):
            response = chatbot_engine.generate_refusal(
                query="What is quantum mechanics?",
                user_age=age,
                language="en"
            )
            
            assert response.is_refusal is True
            assert len(response.text) > 0
            assert "book" in response.text.lower()
            assert len(response.chunk_ids) == 0
