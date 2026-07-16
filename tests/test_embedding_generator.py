"""
Unit tests for the EmbeddingGenerator class.

These tests verify the functionality of embedding generation for both
single texts and batches, including support for English and Urdu text.
"""

import pytest
import numpy as np
from src.embedding_generator import EmbeddingGenerator


class TestEmbeddingGenerator:
    """Test suite for EmbeddingGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create an EmbeddingGenerator instance for testing."""
        return EmbeddingGenerator()
    
    def test_initialization_default_model(self):
        """Test that EmbeddingGenerator initializes with default model."""
        generator = EmbeddingGenerator()
        assert generator.model is not None
        assert generator.model_name == "paraphrase-multilingual-MiniLM-L12-v2"
    
    def test_initialization_custom_model(self):
        """Test that EmbeddingGenerator can initialize with a custom model."""
        # Using a smaller model for faster testing
        generator = EmbeddingGenerator(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        assert generator.model is not None
        assert generator.model_name == "paraphrase-multilingual-MiniLM-L12-v2"
    
    def test_initialization_invalid_model(self):
        """Test that initialization fails with an invalid model name."""
        with pytest.raises(Exception) as exc_info:
            EmbeddingGenerator(model_name="invalid-model-name-12345")
        assert "Failed to load sentence-transformers model" in str(exc_info.value)
    
    def test_generate_embedding_english_text(self, generator):
        """Test generating embedding for English text."""
        text = "This is a test sentence in English."
        embedding = generator.generate_embedding(text)
        
        # Check that embedding is a numpy array
        assert isinstance(embedding, np.ndarray)
        
        # Check that embedding has the correct dimension
        expected_dim = generator.get_embedding_dimension()
        assert embedding.shape == (expected_dim,)
        
        # Check that embedding contains valid numbers
        assert not np.isnan(embedding).any()
        assert not np.isinf(embedding).any()
    
    def test_generate_embedding_urdu_text(self, generator):
        """Test generating embedding for Urdu text."""
        text = "یہ اردو میں ایک ٹیسٹ جملہ ہے۔"
        embedding = generator.generate_embedding(text)
        
        # Check that embedding is a numpy array
        assert isinstance(embedding, np.ndarray)
        
        # Check that embedding has the correct dimension
        expected_dim = generator.get_embedding_dimension()
        assert embedding.shape == (expected_dim,)
        
        # Check that embedding contains valid numbers
        assert not np.isnan(embedding).any()
        assert not np.isinf(embedding).any()
    
    def test_generate_embedding_mixed_text(self, generator):
        """Test generating embedding for mixed English and Urdu text."""
        text = "This is English and یہ اردو ہے mixed text."
        embedding = generator.generate_embedding(text)
        
        # Check that embedding is generated successfully
        assert isinstance(embedding, np.ndarray)
        expected_dim = generator.get_embedding_dimension()
        assert embedding.shape == (expected_dim,)
    
    def test_generate_embedding_empty_string(self, generator):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generator.generate_embedding("")
        assert "Text cannot be empty or None" in str(exc_info.value)
    
    def test_generate_embedding_whitespace_only(self, generator):
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generator.generate_embedding("   \n\t  ")
        assert "Text cannot be empty or None" in str(exc_info.value)
    
    def test_generate_embedding_none(self, generator):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generator.generate_embedding(None)
        assert "Text cannot be empty or None" in str(exc_info.value)
    
    def test_generate_embedding_consistency(self, generator):
        """Test that same text produces same embedding."""
        text = "Consistency test sentence."
        embedding1 = generator.generate_embedding(text)
        embedding2 = generator.generate_embedding(text)
        
        # Embeddings should be identical for the same text
        np.testing.assert_array_almost_equal(embedding1, embedding2)
    
    def test_generate_embedding_different_texts(self, generator):
        """Test that different texts produce different embeddings."""
        text1 = "This is the first sentence."
        text2 = "This is a completely different sentence."
        
        embedding1 = generator.generate_embedding(text1)
        embedding2 = generator.generate_embedding(text2)
        
        # Embeddings should be different
        assert not np.array_equal(embedding1, embedding2)
    
    def test_generate_batch_embeddings_english(self, generator):
        """Test generating batch embeddings for English texts."""
        texts = [
            "First sentence in English.",
            "Second sentence in English.",
            "Third sentence in English."
        ]
        embeddings = generator.generate_batch_embeddings(texts)
        
        # Check shape
        expected_dim = generator.get_embedding_dimension()
        assert embeddings.shape == (len(texts), expected_dim)
        
        # Check that all embeddings are valid
        assert not np.isnan(embeddings).any()
        assert not np.isinf(embeddings).any()
    
    def test_generate_batch_embeddings_urdu(self, generator):
        """Test generating batch embeddings for Urdu texts."""
        texts = [
            "پہلا اردو جملہ۔",
            "دوسرا اردو جملہ۔",
            "تیسرا اردو جملہ۔"
        ]
        embeddings = generator.generate_batch_embeddings(texts)
        
        # Check shape
        expected_dim = generator.get_embedding_dimension()
        assert embeddings.shape == (len(texts), expected_dim)
        
        # Check that all embeddings are valid
        assert not np.isnan(embeddings).any()
        assert not np.isinf(embeddings).any()
    
    def test_generate_batch_embeddings_mixed(self, generator):
        """Test generating batch embeddings for mixed English and Urdu texts."""
        texts = [
            "English sentence.",
            "اردو جملہ۔",
            "Mixed English and اردو text."
        ]
        embeddings = generator.generate_batch_embeddings(texts)
        
        # Check shape
        expected_dim = generator.get_embedding_dimension()
        assert embeddings.shape == (len(texts), expected_dim)
    
    def test_generate_batch_embeddings_empty_list(self, generator):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generator.generate_batch_embeddings([])
        assert "Texts list cannot be empty" in str(exc_info.value)
    
    def test_generate_batch_embeddings_contains_empty_string(self, generator):
        """Test that list containing empty string raises ValueError."""
        texts = ["Valid text", "", "Another valid text"]
        with pytest.raises(ValueError) as exc_info:
            generator.generate_batch_embeddings(texts)
        assert "Texts list cannot contain empty strings" in str(exc_info.value)
    
    def test_generate_batch_embeddings_contains_whitespace(self, generator):
        """Test that list containing whitespace-only string raises ValueError."""
        texts = ["Valid text", "   \n\t  ", "Another valid text"]
        with pytest.raises(ValueError) as exc_info:
            generator.generate_batch_embeddings(texts)
        assert "Texts list cannot contain empty strings" in str(exc_info.value)
    
    def test_generate_batch_embeddings_consistency(self, generator):
        """Test that batch embeddings are consistent with single embeddings."""
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        
        # Generate batch embeddings
        batch_embeddings = generator.generate_batch_embeddings(texts)
        
        # Generate individual embeddings
        individual_embeddings = [generator.generate_embedding(text) for text in texts]
        
        # Compare each embedding
        for i, individual_embedding in enumerate(individual_embeddings):
            np.testing.assert_array_almost_equal(
                batch_embeddings[i],
                individual_embedding,
                decimal=5
            )
    
    def test_generate_batch_embeddings_large_batch(self, generator):
        """Test generating embeddings for a large batch of texts."""
        # Create 100 different texts
        texts = [f"This is test sentence number {i}." for i in range(100)]
        embeddings = generator.generate_batch_embeddings(texts)
        
        # Check shape
        expected_dim = generator.get_embedding_dimension()
        assert embeddings.shape == (100, expected_dim)
        
        # Check that all embeddings are unique (no duplicates)
        # This is a probabilistic check - embeddings should be different
        for i in range(len(embeddings) - 1):
            assert not np.array_equal(embeddings[i], embeddings[i + 1])
    
    def test_get_embedding_dimension(self, generator):
        """Test getting the embedding dimension."""
        dim = generator.get_embedding_dimension()
        
        # Check that dimension is a positive integer
        assert isinstance(dim, int)
        assert dim > 0
        
        # For the default model, dimension should be 384
        assert dim == 384
    
    def test_embedding_dimension_matches_output(self, generator):
        """Test that reported dimension matches actual embedding dimension."""
        text = "Test sentence for dimension check."
        embedding = generator.generate_embedding(text)
        reported_dim = generator.get_embedding_dimension()
        
        assert embedding.shape[0] == reported_dim
    
    def test_semantic_similarity_english(self, generator):
        """Test that semantically similar English texts have similar embeddings."""
        text1 = "The cat sits on the mat."
        text2 = "A cat is sitting on a mat."
        text3 = "The weather is sunny today."
        
        emb1 = generator.generate_embedding(text1)
        emb2 = generator.generate_embedding(text2)
        emb3 = generator.generate_embedding(text3)
        
        # Calculate cosine similarities
        sim_1_2 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        sim_1_3 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
        
        # Similar texts should have higher similarity than dissimilar texts
        assert sim_1_2 > sim_1_3
    
    def test_semantic_similarity_urdu(self, generator):
        """Test that semantically similar Urdu texts have similar embeddings."""
        text1 = "بلی چٹائی پر بیٹھی ہے۔"
        text2 = "ایک بلی چٹائی پر بیٹھی ہوئی ہے۔"
        text3 = "آج موسم دھوپ والا ہے۔"
        
        emb1 = generator.generate_embedding(text1)
        emb2 = generator.generate_embedding(text2)
        emb3 = generator.generate_embedding(text3)
        
        # Calculate cosine similarities
        sim_1_2 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        sim_1_3 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
        
        # Similar texts should have higher similarity than dissimilar texts
        assert sim_1_2 > sim_1_3
    
    def test_long_text_handling(self, generator):
        """Test that the generator can handle long texts."""
        # Create a long text (multiple sentences)
        long_text = " ".join([f"This is sentence number {i} in a very long text." for i in range(50)])
        
        embedding = generator.generate_embedding(long_text)
        
        # Check that embedding is generated successfully
        assert isinstance(embedding, np.ndarray)
        expected_dim = generator.get_embedding_dimension()
        assert embedding.shape == (expected_dim,)
    
    def test_special_characters_handling(self, generator):
        """Test that the generator handles special characters correctly."""
        text = "Text with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
        embedding = generator.generate_embedding(text)
        
        # Check that embedding is generated successfully
        assert isinstance(embedding, np.ndarray)
        expected_dim = generator.get_embedding_dimension()
        assert embedding.shape == (expected_dim,)
    
    def test_numbers_handling(self, generator):
        """Test that the generator handles numbers correctly."""
        text = "Text with numbers: 123 456 789 and 3.14159"
        embedding = generator.generate_embedding(text)
        
        # Check that embedding is generated successfully
        assert isinstance(embedding, np.ndarray)
        expected_dim = generator.get_embedding_dimension()
        assert embedding.shape == (expected_dim,)
