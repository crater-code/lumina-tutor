"""
Unit tests for the ChatbotEngine class.
"""

import pytest
import os
from src.chatbot_engine import ChatbotEngine
from src.models import Chunk, Response
from src.exceptions import LLMError


@pytest.fixture
def chatbot_engine():
    """Create a ChatbotEngine instance for testing."""
    # Use mock LLM for testing
    os.environ["USE_MOCK_LLM"] = "true"
    return ChatbotEngine()


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    return [
        Chunk(
            chunk_id="book_1_chunk_0",
            text="Photosynthesis is the process by which plants convert sunlight into energy. Plants use chlorophyll to absorb light.",
            page_numbers=[1],
            start_char=0,
            end_char=110,
            metadata={"section": "Biology"}
        ),
        Chunk(
            chunk_id="book_1_chunk_1",
            text="The water cycle describes how water moves through the environment. Water evaporates, condenses, and precipitates.",
            page_numbers=[2],
            start_char=0,
            end_char=112,
            metadata={"section": "Earth Science"}
        ),
    ]


class TestChatbotEngineInitialization:
    """Tests for ChatbotEngine initialization."""
    
    def test_initialization_default(self):
        """Test that ChatbotEngine initializes with default settings."""
        engine = ChatbotEngine()
        
        assert engine.model_name == "mistralai/Mistral-7B-Instruct-v0.2"
        assert engine.use_mock_llm is True
    
    def test_initialization_custom_model(self):
        """Test initialization with custom model name."""
        engine = ChatbotEngine(model_name="custom-model")
        
        assert engine.model_name == "custom-model"
    
    def test_initialization_with_api_key(self):
        """Test initialization with API key."""
        engine = ChatbotEngine(api_key="test_key")
        
        assert engine.api_key == "test_key"


class TestGenerateResponse:
    """Tests for the generate_response method."""
    
    def test_generate_response_basic(self, chatbot_engine, sample_chunks):
        """Test basic response generation with valid inputs."""
        response = chatbot_engine.generate_response(
            query="What is photosynthesis?",
            retrieved_chunks=sample_chunks,
            user_age=10,
            language="en"
        )
        
        # Verify response structure
        assert isinstance(response, Response)
        assert isinstance(response.text, str)
        assert len(response.text) > 0
        assert response.is_refusal is False
        
        # Verify chunk IDs are included
        assert len(response.chunk_ids) == len(sample_chunks)
        assert "book_1_chunk_0" in response.chunk_ids
        assert "book_1_chunk_1" in response.chunk_ids
        
        # Verify metadata
        assert response.metadata["language"] == "en"
        assert response.metadata["age_group"] == "elementary"
        assert response.metadata["num_chunks_used"] == 2
    
    def test_generate_response_young_child(self, chatbot_engine, sample_chunks):
        """Test response generation for young children (4-7)."""
        response = chatbot_engine.generate_response(
            query="What is photosynthesis?",
            retrieved_chunks=sample_chunks,
            user_age=6,
            language="en"
        )
        
        assert isinstance(response, Response)
        assert response.metadata["age_group"] == "young_child"
        assert response.is_refusal is False
    
    def test_generate_response_middle_school(self, chatbot_engine, sample_chunks):
        """Test response generation for middle school students (12-15)."""
        response = chatbot_engine.generate_response(
            query="What is photosynthesis?",
            retrieved_chunks=sample_chunks,
            user_age=14,
            language="en"
        )
        
        assert isinstance(response, Response)
        assert response.metadata["age_group"] == "middle_school"
        assert response.is_refusal is False
    
    def test_generate_response_urdu_language(self, chatbot_engine, sample_chunks):
        """Test response generation in Urdu."""
        response = chatbot_engine.generate_response(
            query="فوٹو سنتھیسس کیا ہے؟",
            retrieved_chunks=sample_chunks,
            user_age=10,
            language="ur"
        )
        
        assert isinstance(response, Response)
        assert response.metadata["language"] == "ur"
        assert response.is_refusal is False
    
    def test_generate_response_single_chunk(self, chatbot_engine):
        """Test response generation with a single chunk."""
        single_chunk = [
            Chunk(
                chunk_id="book_1_chunk_0",
                text="The Earth orbits around the Sun.",
                page_numbers=[1],
                start_char=0,
                end_char=33,
                metadata={}
            )
        ]
        
        response = chatbot_engine.generate_response(
            query="What does Earth orbit?",
            retrieved_chunks=single_chunk,
            user_age=10,
            language="en"
        )
        
        assert isinstance(response, Response)
        assert len(response.chunk_ids) == 1
        assert response.chunk_ids[0] == "book_1_chunk_0"
    
    def test_generate_response_empty_query(self, chatbot_engine, sample_chunks):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            chatbot_engine.generate_response(
                query="",
                retrieved_chunks=sample_chunks,
                user_age=10,
                language="en"
            )
    
    def test_generate_response_whitespace_query(self, chatbot_engine, sample_chunks):
        """Test that whitespace-only query raises ValueError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            chatbot_engine.generate_response(
                query="   ",
                retrieved_chunks=sample_chunks,
                user_age=10,
                language="en"
            )
    
    def test_generate_response_empty_chunks(self, chatbot_engine):
        """Test that empty chunks list raises ValueError."""
        with pytest.raises(ValueError, match="Retrieved chunks cannot be empty"):
            chatbot_engine.generate_response(
                query="What is photosynthesis?",
                retrieved_chunks=[],
                user_age=10,
                language="en"
            )
    
    def test_generate_response_invalid_age_too_young(self, chatbot_engine, sample_chunks):
        """Test that age below 4 raises ValueError."""
        with pytest.raises(ValueError, match="User age must be between 4 and 15"):
            chatbot_engine.generate_response(
                query="What is photosynthesis?",
                retrieved_chunks=sample_chunks,
                user_age=3,
                language="en"
            )
    
    def test_generate_response_invalid_age_too_old(self, chatbot_engine, sample_chunks):
        """Test that age above 15 raises ValueError."""
        with pytest.raises(ValueError, match="User age must be between 4 and 15"):
            chatbot_engine.generate_response(
                query="What is photosynthesis?",
                retrieved_chunks=sample_chunks,
                user_age=16,
                language="en"
            )
    
    def test_generate_response_invalid_language(self, chatbot_engine, sample_chunks):
        """Test that invalid language raises ValueError."""
        with pytest.raises(ValueError, match="Language must be 'en' or 'ur'"):
            chatbot_engine.generate_response(
                query="What is photosynthesis?",
                retrieved_chunks=sample_chunks,
                user_age=10,
                language="fr"
            )
    
    def test_generate_response_all_ages(self, chatbot_engine, sample_chunks):
        """Test response generation for all valid ages."""
        for age in range(4, 16):
            response = chatbot_engine.generate_response(
                query="What is photosynthesis?",
                retrieved_chunks=sample_chunks,
                user_age=age,
                language="en"
            )
            
            assert isinstance(response, Response)
            assert response.is_refusal is False
            assert len(response.chunk_ids) > 0


class TestGenerateRefusal:
    """Tests for the generate_refusal method."""
    
    def test_generate_refusal_basic(self, chatbot_engine):
        """Test basic refusal message generation."""
        response = chatbot_engine.generate_refusal(
            query="What is quantum mechanics?",
            user_age=10,
            language="en"
        )
        
        # Verify response structure
        assert isinstance(response, Response)
        assert isinstance(response.text, str)
        assert len(response.text) > 0
        assert response.is_refusal is True
        
        # Verify no chunk IDs
        assert response.chunk_ids == []
        
        # Verify metadata
        assert response.metadata["language"] == "en"
        assert response.metadata["age_group"] == "elementary"
    
    def test_generate_refusal_young_child(self, chatbot_engine):
        """Test refusal message for young children (4-7)."""
        response = chatbot_engine.generate_refusal(
            query="What is quantum mechanics?",
            user_age=6,
            language="en"
        )
        
        assert isinstance(response, Response)
        assert response.is_refusal is True
        assert response.metadata["age_group"] == "young_child"
        
        # Verify message is simple and encouraging
        assert "sorry" in response.text.lower() or "can't" in response.text.lower()
        assert "book" in response.text.lower()
    
    def test_generate_refusal_elementary(self, chatbot_engine):
        """Test refusal message for elementary students (8-11)."""
        response = chatbot_engine.generate_refusal(
            query="What is quantum mechanics?",
            user_age=10,
            language="en"
        )
        
        assert isinstance(response, Response)
        assert response.is_refusal is True
        assert response.metadata["age_group"] == "elementary"
        
        # Verify message explains the limitation
        assert "book" in response.text.lower()
        assert "couldn't find" in response.text.lower() or "can't find" in response.text.lower()
    
    def test_generate_refusal_middle_school(self, chatbot_engine):
        """Test refusal message for middle school students (12-15)."""
        response = chatbot_engine.generate_refusal(
            query="What is quantum mechanics?",
            user_age=14,
            language="en"
        )
        
        assert isinstance(response, Response)
        assert response.is_refusal is True
        assert response.metadata["age_group"] == "middle_school"
        
        # Verify message is more formal
        assert "book" in response.text.lower()
        assert "couldn't find" in response.text.lower() or "can't find" in response.text.lower()
    
    def test_generate_refusal_urdu(self, chatbot_engine):
        """Test refusal message in Urdu."""
        response = chatbot_engine.generate_refusal(
            query="کوانٹم میکینکس کیا ہے؟",
            user_age=10,
            language="ur"
        )
        
        assert isinstance(response, Response)
        assert response.is_refusal is True
        assert response.metadata["language"] == "ur"
        
        # Verify message contains Urdu text
        assert any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in response.text)
    
    def test_generate_refusal_no_external_resources(self, chatbot_engine):
        """Test that refusal message doesn't suggest external resources."""
        response = chatbot_engine.generate_refusal(
            query="What is quantum mechanics?",
            user_age=10,
            language="en"
        )
        
        # Verify no external resource suggestions
        text_lower = response.text.lower()
        assert "google" not in text_lower
        assert "search" not in text_lower
        assert "wikipedia" not in text_lower
        assert "website" not in text_lower
    
    def test_generate_refusal_encourages_book_questions(self, chatbot_engine):
        """Test that refusal message encourages asking about the book."""
        response = chatbot_engine.generate_refusal(
            query="What is quantum mechanics?",
            user_age=10,
            language="en"
        )
        
        # Verify message encourages asking about book content
        text_lower = response.text.lower()
        assert "book" in text_lower
        assert any(word in text_lower for word in ["ask", "question", "other", "different"])
    
    def test_generate_refusal_empty_query(self, chatbot_engine):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            chatbot_engine.generate_refusal(
                query="",
                user_age=10,
                language="en"
            )
    
    def test_generate_refusal_invalid_age(self, chatbot_engine):
        """Test that invalid age raises ValueError."""
        with pytest.raises(ValueError, match="User age must be between 4 and 15"):
            chatbot_engine.generate_refusal(
                query="What is quantum mechanics?",
                user_age=3,
                language="en"
            )
    
    def test_generate_refusal_invalid_language(self, chatbot_engine):
        """Test that invalid language raises ValueError."""
        with pytest.raises(ValueError, match="Language must be 'en' or 'ur'"):
            chatbot_engine.generate_refusal(
                query="What is quantum mechanics?",
                user_age=10,
                language="fr"
            )
    
    def test_generate_refusal_all_ages_english(self, chatbot_engine):
        """Test refusal generation for all valid ages in English."""
        for age in range(4, 16):
            response = chatbot_engine.generate_refusal(
                query="What is quantum mechanics?",
                user_age=age,
                language="en"
            )
            
            assert isinstance(response, Response)
            assert response.is_refusal is True
            assert len(response.text) > 0
            assert response.chunk_ids == []
    
    def test_generate_refusal_all_ages_urdu(self, chatbot_engine):
        """Test refusal generation for all valid ages in Urdu."""
        for age in range(4, 16):
            response = chatbot_engine.generate_refusal(
                query="کوانٹم میکینکس کیا ہے؟",
                user_age=age,
                language="ur"
            )
            
            assert isinstance(response, Response)
            assert response.is_refusal is True
            assert len(response.text) > 0
            assert response.chunk_ids == []


class TestPromptBuilding:
    """Tests for prompt building functionality."""
    
    def test_build_prompt_structure(self, chatbot_engine, sample_chunks):
        """Test that prompt has correct structure."""
        prompt = chatbot_engine._build_prompt(
            query="What is photosynthesis?",
            chunks=sample_chunks,
            age=10,
            language="en"
        )
        
        # Verify prompt contains key sections
        assert "RULES:" in prompt
        assert "BOOK EXCERPTS:" in prompt
        assert "QUESTION:" in prompt
        assert "ANSWER:" in prompt
        
        # Verify chunks are included
        assert "book_1_chunk_0" in prompt
        assert "book_1_chunk_1" in prompt
        assert "Photosynthesis" in prompt
        
        # Verify query is included
        assert "What is photosynthesis?" in prompt
    
    def test_build_prompt_age_adaptation(self, chatbot_engine, sample_chunks):
        """Test that prompt includes age-appropriate guidance."""
        # Young child
        prompt_young = chatbot_engine._build_prompt(
            query="What is photosynthesis?",
            chunks=sample_chunks,
            age=6,
            language="en"
        )
        assert "simple" in prompt_young.lower()
        
        # Middle school
        prompt_middle = chatbot_engine._build_prompt(
            query="What is photosynthesis?",
            chunks=sample_chunks,
            age=14,
            language="en"
        )
        assert "middle school" in prompt_middle.lower() or "complex" in prompt_middle.lower()
    
    def test_build_prompt_language_instruction(self, chatbot_engine, sample_chunks):
        """Test that prompt includes language instruction."""
        # English
        prompt_en = chatbot_engine._build_prompt(
            query="What is photosynthesis?",
            chunks=sample_chunks,
            age=10,
            language="en"
        )
        assert "English" in prompt_en
        
        # Urdu
        prompt_ur = chatbot_engine._build_prompt(
            query="فوٹو سنتھیسس کیا ہے؟",
            chunks=sample_chunks,
            age=10,
            language="ur"
        )
        assert "Urdu" in prompt_ur or "اردو" in prompt_ur


class TestAgeGroupHelpers:
    """Tests for age group helper methods."""
    
    def test_get_age_group_name(self, chatbot_engine):
        """Test age group name retrieval."""
        assert chatbot_engine._get_age_group_name(5) == "young_child"
        assert chatbot_engine._get_age_group_name(9) == "elementary"
        assert chatbot_engine._get_age_group_name(13) == "middle_school"
    
    def test_get_age_guidance(self, chatbot_engine):
        """Test age guidance retrieval."""
        guidance_young = chatbot_engine._get_age_guidance(5)
        assert "simple" in guidance_young.lower()
        
        guidance_elementary = chatbot_engine._get_age_guidance(9)
        assert "elementary" in guidance_elementary.lower()
        
        guidance_middle = chatbot_engine._get_age_guidance(13)
        assert "middle school" in guidance_middle.lower() or "complex" in guidance_middle.lower()


class TestMockLLM:
    """Tests for mock LLM functionality."""
    
    def test_mock_llm_response(self, chatbot_engine):
        """Test that mock LLM generates reasonable responses."""
        prompt = """
        RULES:
        1. Answer ONLY using the book excerpts provided below.
        
        BOOK EXCERPTS:
        
        [Excerpt 1 - ID: book_1_chunk_0]
        Photosynthesis is the process by which plants convert sunlight into energy.
        
        QUESTION:
        What is photosynthesis?
        
        ANSWER:
        """
        
        response = chatbot_engine._mock_llm_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Mock response should reference the book content
        assert "book" in response.lower() or "photosynthesis" in response.lower()
    
    def test_mock_llm_response_no_excerpt(self, chatbot_engine):
        """Test mock LLM with prompt that has no excerpts."""
        prompt = """
        QUESTION:
        What is photosynthesis?
        
        ANSWER:
        """
        
        response = chatbot_engine._mock_llm_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0


class TestIntegration:
    """Integration tests for ChatbotEngine."""
    
    def test_end_to_end_response_generation(self, chatbot_engine):
        """Test complete flow from query to response."""
        chunks = [
            Chunk(
                chunk_id="book_test_chunk_0",
                text="The mitochondria is the powerhouse of the cell. It produces energy through cellular respiration.",
                page_numbers=[1],
                start_char=0,
                end_char=95,
                metadata={}
            ),
        ]
        
        response = chatbot_engine.generate_response(
            query="What is the function of mitochondria?",
            retrieved_chunks=chunks,
            user_age=10,
            language="en"
        )
        
        # Verify complete response
        assert isinstance(response, Response)
        assert len(response.text) > 0
        assert response.is_refusal is False
        assert len(response.chunk_ids) == 1
        assert response.chunk_ids[0] == "book_test_chunk_0"
        assert response.metadata["language"] == "en"
        assert response.metadata["age_group"] == "elementary"
    
    def test_end_to_end_refusal_generation(self, chatbot_engine):
        """Test complete flow for refusal message."""
        response = chatbot_engine.generate_refusal(
            query="What is quantum mechanics?",
            user_age=10,
            language="en"
        )
        
        # Verify complete refusal
        assert isinstance(response, Response)
        assert len(response.text) > 0
        assert response.is_refusal is True
        assert response.chunk_ids == []
        assert "book" in response.text.lower()
        assert response.metadata["language"] == "en"
        assert response.metadata["age_group"] == "elementary"
