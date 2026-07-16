"""
Unit tests for the ResponseValidator class.

These tests verify:
1. Valid responses pass validation
2. Responses with hallucinated content fail validation
3. Responses without citations fail validation
4. Refusal messages always pass validation
5. Logging of rejected responses
"""

import pytest
from src.response_validator import ResponseValidator
from src.models import Response, Chunk, ValidationResult


class TestResponseValidator:
    """Test suite for ResponseValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a ResponseValidator instance for testing."""
        return ResponseValidator(
            similarity_threshold=0.3,
            keyword_match_threshold=0.5
        )
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks for testing."""
        return [
            Chunk(
                chunk_id="book_1_chunk_1",
                text="Photosynthesis is the process by which plants use sunlight to convert carbon dioxide and water into glucose and oxygen.",
                page_numbers=[1],
                start_char=0,
                end_char=120,
                metadata={}
            ),
            Chunk(
                chunk_id="book_1_chunk_2",
                text="The chloroplasts in plant cells contain chlorophyll, which captures light energy. This energy is used to power the chemical reactions of photosynthesis.",
                page_numbers=[1],
                start_char=121,
                end_char=260,
                metadata={}
            )
        ]
    
    def test_valid_response_passes_validation(self, validator, sample_chunks):
        """Test that a valid response passes validation."""
        response = Response(
            text="Plants use sunlight to convert carbon dioxide and water into glucose through photosynthesis.",
            chunk_ids=["book_1_chunk_1", "book_1_chunk_2"],
            is_refusal=False,
            metadata={"age_group": "elementary", "language": "en"}
        )
        
        result = validator.validate_response(response, sample_chunks)
        
        assert result.is_valid is True
        assert result.confidence > 0.5
        assert len(result.issues) == 0
    
    def test_response_without_citations_fails(self, validator, sample_chunks):
        """Test that a response without citations fails validation."""
        response = Response(
            text="Plants use sunlight to make food.",
            chunk_ids=[],  # No citations
            is_refusal=False,
            metadata={"age_group": "elementary", "language": "en"}
        )
        
        result = validator.validate_response(response, sample_chunks)
        
        assert result.is_valid is False
        assert "no chunk citations" in result.issues[0].lower()
    
    def test_response_with_hallucinated_content_fails(self, validator, sample_chunks):
        """Test that a response with hallucinated content fails validation."""
        response = Response(
            text="Plants use photosynthesis, which was discovered by Albert Einstein in 1905. The process involves quantum mechanics and relativity theory.",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={"age_group": "elementary", "language": "en"}
        )
        
        result = validator.validate_response(response, sample_chunks)
        
        assert result.is_valid is False
        assert any("hallucination" in issue.lower() for issue in result.issues)
    
    def test_refusal_message_always_passes(self, validator, sample_chunks):
        """Test that refusal messages always pass validation."""
        response = Response(
            text="I couldn't find information about that in this book.",
            chunk_ids=[],
            is_refusal=True,
            metadata={"age_group": "elementary", "language": "en"}
        )
        
        result = validator.validate_response(response, sample_chunks)
        
        assert result.is_valid is True
        assert result.confidence == 1.0
        assert len(result.issues) == 0
    
    def test_validation_without_chunks_fails(self, validator):
        """Test that validation fails when no chunks are provided."""
        response = Response(
            text="Plants use sunlight to make food.",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={"age_group": "elementary", "language": "en"}
        )
        
        result = validator.validate_response(response, [])
        
        assert result.is_valid is False
        assert any("no retrieved chunks" in issue.lower() for issue in result.issues)
    
    def test_check_hallucination_with_matching_content(self, validator):
        """Test hallucination check with content that matches chunks."""
        response_text = "Plants use sunlight to convert carbon dioxide into glucose."
        chunk_texts = [
            "Photosynthesis is the process by which plants use sunlight to convert carbon dioxide and water into glucose and oxygen."
        ]
        
        is_hallucinated = validator.check_hallucination(response_text, chunk_texts)
        
        assert is_hallucinated is False
    
    def test_check_hallucination_with_unmatched_content(self, validator):
        """Test hallucination check with content not in chunks."""
        response_text = "Albert Einstein discovered photosynthesis in 1905 using quantum mechanics."
        chunk_texts = [
            "Photosynthesis is the process by which plants use sunlight to convert carbon dioxide and water into glucose and oxygen."
        ]
        
        is_hallucinated = validator.check_hallucination(response_text, chunk_texts)
        
        assert is_hallucinated is True
    
    def test_check_hallucination_with_paraphrased_content(self, validator):
        """Test that closely paraphrased content from chunks is not flagged as hallucination."""
        response_text = "Plants use sunlight to convert carbon dioxide and water into glucose."
        chunk_texts = [
            "Photosynthesis is the process by which plants use sunlight to convert carbon dioxide and water into glucose and oxygen."
        ]
        
        is_hallucinated = validator.check_hallucination(response_text, chunk_texts)
        
        # Should not be flagged as hallucination since it's a close paraphrase with matching keywords
        assert is_hallucinated is False
    
    def test_extract_keywords(self, validator):
        """Test keyword extraction."""
        text = "Photosynthesis is the process by which plants use sunlight."
        
        keywords = validator._extract_keywords(text)
        
        assert "photosynthesis" in keywords
        assert "process" in keywords
        assert "plants" in keywords
        assert "sunlight" in keywords
        # Stop words should be filtered out
        assert "the" not in keywords
        assert "is" not in keywords
        assert "by" not in keywords
    
    def test_split_into_sentences(self, validator):
        """Test sentence splitting."""
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        
        sentences = validator._split_into_sentences(text)
        
        assert len(sentences) == 3
        assert "This is sentence one" in sentences[0]
        assert "This is sentence two" in sentences[1]
        assert "Is this sentence three" in sentences[2]
    
    def test_calculate_similarity(self, validator):
        """Test similarity calculation."""
        text1 = "Plants use sunlight to make food."
        text2 = "Plants use sunlight to make food."
        text3 = "The sky is blue."
        
        # Identical texts should have high similarity
        similarity_identical = validator._calculate_similarity(text1, text2)
        assert similarity_identical > 0.9
        
        # Different texts should have low similarity
        similarity_different = validator._calculate_similarity(text1, text3)
        assert similarity_different < 0.3
    
    def test_extract_entities(self, validator):
        """Test entity extraction."""
        text = "Albert Einstein discovered the theory in 1905. The value is 42."
        
        entities = validator._extract_entities(text)
        
        assert "Einstein" in entities
        assert "1905" in entities
        assert "42" in entities
    
    def test_validation_with_multiple_chunks(self, validator):
        """Test validation with multiple chunks."""
        chunks = [
            Chunk(
                chunk_id="book_1_chunk_1",
                text="The sun is a star that provides light and heat to Earth.",
                page_numbers=[1],
                start_char=0,
                end_char=60,
                metadata={}
            ),
            Chunk(
                chunk_id="book_1_chunk_2",
                text="Earth orbits around the sun once every 365 days.",
                page_numbers=[1],
                start_char=61,
                end_char=110,
                metadata={}
            )
        ]
        
        response = Response(
            text="The sun provides light to Earth, which orbits the sun every 365 days.",
            chunk_ids=["book_1_chunk_1", "book_1_chunk_2"],
            is_refusal=False,
            metadata={"age_group": "elementary", "language": "en"}
        )
        
        result = validator.validate_response(response, chunks)
        
        assert result.is_valid is True
        assert result.confidence > 0.5
    
    def test_validation_confidence_score(self, validator, sample_chunks):
        """Test that validation confidence score is calculated correctly."""
        # Valid response should have high confidence
        valid_response = Response(
            text="Plants use sunlight for photosynthesis.",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={}
        )
        
        valid_result = validator.validate_response(valid_response, sample_chunks)
        assert valid_result.confidence > 0.7
        
        # Invalid response should have lower confidence than valid response
        invalid_response = Response(
            text="Quantum mechanics explains photosynthesis.",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={}
        )
        
        invalid_result = validator.validate_response(invalid_response, sample_chunks)
        # Invalid response should be marked as invalid
        assert invalid_result.is_valid is False
        # And should have lower confidence than valid response
        assert invalid_result.confidence < valid_result.confidence
    
    def test_short_sentences_ignored_in_hallucination_check(self, validator):
        """Test that very short sentences are ignored in hallucination check."""
        response_text = "Yes. I see. Plants use sunlight for photosynthesis."
        chunk_texts = [
            "Photosynthesis is the process by which plants use sunlight to convert carbon dioxide and water into glucose."
        ]
        
        # Should not fail due to short sentences like "Yes." and "I see."
        is_hallucinated = validator.check_hallucination(response_text, chunk_texts)
        
        assert is_hallucinated is False
    
    def test_validation_with_urdu_text(self, validator):
        """Test validation with Urdu text."""
        chunks = [
            Chunk(
                chunk_id="book_1_chunk_1",
                text="سورج ایک ستارہ ہے جو زمین کو روشنی اور حرارت فراہم کرتا ہے۔",
                page_numbers=[1],
                start_char=0,
                end_char=60,
                metadata={"language": "ur"}
            )
        ]
        
        response = Response(
            text="سورج زمین کو روشنی فراہم کرتا ہے۔",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={"age_group": "elementary", "language": "ur"}
        )
        
        result = validator.validate_response(response, chunks)
        
        # Should pass validation (Urdu text is handled)
        assert result.is_valid is True
    
    def test_logging_of_rejected_responses(self, validator, sample_chunks, caplog):
        """Test that rejected responses are logged."""
        import logging
        caplog.set_level(logging.WARNING)
        
        response = Response(
            text="This is completely made up content about unicorns and dragons.",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={}
        )
        
        result = validator.validate_response(response, sample_chunks)
        
        assert result.is_valid is False
        # Check that a warning was logged
        assert len(caplog.records) > 0
        assert any("validation failed" in record.message.lower() for record in caplog.records)


class TestResponseValidatorEdgeCases:
    """Test edge cases for ResponseValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a ResponseValidator instance for testing."""
        return ResponseValidator()
    
    def test_empty_response_text(self, validator):
        """Test validation with empty response text."""
        chunks = [
            Chunk(
                chunk_id="book_1_chunk_1",
                text="Some content here.",
                page_numbers=[1],
                start_char=0,
                end_char=20,
                metadata={}
            )
        ]
        
        response = Response(
            text="",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={}
        )
        
        # Should handle empty text gracefully
        result = validator.validate_response(response, chunks)
        assert isinstance(result, ValidationResult)
    
    def test_very_long_response(self, validator):
        """Test validation with very long response."""
        chunks = [
            Chunk(
                chunk_id="book_1_chunk_1",
                text="Plants use photosynthesis. " * 100,  # Long chunk
                page_numbers=[1],
                start_char=0,
                end_char=2800,
                metadata={}
            )
        ]
        
        response = Response(
            text="Plants use photosynthesis. " * 50,  # Long response
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={}
        )
        
        # Should handle long text efficiently
        result = validator.validate_response(response, chunks)
        assert result.is_valid is True
    
    def test_special_characters_in_text(self, validator):
        """Test validation with special characters."""
        chunks = [
            Chunk(
                chunk_id="book_1_chunk_1",
                text="The formula is: H₂O + CO₂ → C₆H₁₂O₆ + O₂",
                page_numbers=[1],
                start_char=0,
                end_char=50,
                metadata={}
            )
        ]
        
        response = Response(
            text="The formula involves H₂O and CO₂.",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={}
        )
        
        # Should handle special characters
        result = validator.validate_response(response, chunks)
        assert result.is_valid is True
    
    def test_custom_thresholds(self):
        """Test validator with custom thresholds."""
        # Very strict validator
        strict_validator = ResponseValidator(
            similarity_threshold=0.8,
            keyword_match_threshold=0.9
        )
        
        # Very lenient validator
        lenient_validator = ResponseValidator(
            similarity_threshold=0.1,
            keyword_match_threshold=0.1
        )
        
        chunks = [
            Chunk(
                chunk_id="book_1_chunk_1",
                text="Plants use sunlight.",
                page_numbers=[1],
                start_char=0,
                end_char=20,
                metadata={}
            )
        ]
        
        response = Response(
            text="Vegetation utilizes solar energy.",
            chunk_ids=["book_1_chunk_1"],
            is_refusal=False,
            metadata={}
        )
        
        # Strict validator might fail
        strict_result = strict_validator.validate_response(response, chunks)
        
        # Lenient validator should pass
        lenient_result = lenient_validator.validate_response(response, chunks)
        
        # Lenient should be more permissive
        assert lenient_result.confidence >= strict_result.confidence
