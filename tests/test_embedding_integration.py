"""
Integration tests for EmbeddingGenerator with other system components.

These tests verify that the EmbeddingGenerator works correctly with
the PDFParser and ChunkingEngine components.
"""

import pytest
import numpy as np
from src.embedding_generator import EmbeddingGenerator
from src.chunking_engine import ChunkingEngine
from src.pdf_parser import PDFParser
from src.models import PageContent


class TestEmbeddingIntegration:
    """Integration tests for EmbeddingGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create an EmbeddingGenerator instance."""
        return EmbeddingGenerator()
    
    @pytest.fixture
    def chunking_engine(self):
        """Create a ChunkingEngine instance."""
        return ChunkingEngine()
    
    def test_embedding_generation_for_chunks(self, generator, chunking_engine):
        """Test generating embeddings for chunks created by ChunkingEngine."""
        # Create sample pages
        pages = [
            PageContent(
                page_number=1,
                text="This is the first page of the book. It contains an introduction to the topic.",
                metadata={}
            ),
            PageContent(
                page_number=2,
                text="This is the second page. It continues the discussion with more details.",
                metadata={}
            )
        ]
        
        # Create chunks
        chunks = chunking_engine.create_chunks(pages, book_id="test_book")
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = generator.generate_batch_embeddings(chunk_texts)
        
        # Verify embeddings were generated
        assert embeddings.shape[0] == len(chunks)
        assert embeddings.shape[1] == generator.get_embedding_dimension()
        
        # Verify all embeddings are valid
        assert not np.isnan(embeddings).any()
        assert not np.isinf(embeddings).any()
    
    def test_query_chunk_similarity(self, generator, chunking_engine):
        """Test that query embeddings can be compared with chunk embeddings."""
        # Create sample pages with specific content (longer to ensure multiple chunks)
        pages = [
            PageContent(
                page_number=1,
                text="Python is a high-level programming language. " * 20 + 
                     "It is widely used for web development and data science.",
                metadata={}
            ),
            PageContent(
                page_number=2,
                text="JavaScript is a scripting language for web browsers. " * 20 +
                     "It enables interactive web pages and dynamic content.",
                metadata={}
            ),
            PageContent(
                page_number=3,
                text="The weather today is sunny and warm. " * 20 +
                     "It's a great day for outdoor activities and recreation.",
                metadata={}
            )
        ]
        
        # Create chunks
        chunks = chunking_engine.create_chunks(pages, book_id="test_book")
        
        # Generate chunk embeddings
        chunk_texts = [chunk.text for chunk in chunks]
        chunk_embeddings = generator.generate_batch_embeddings(chunk_texts)
        
        # Create a query about Python
        query = "What is Python programming language?"
        query_embedding = generator.generate_embedding(query)
        
        # Calculate similarities
        similarities = []
        for chunk_emb in chunk_embeddings:
            similarity = np.dot(query_embedding, chunk_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_emb)
            )
            similarities.append(similarity)
        
        # Find the chunk with highest similarity
        most_similar_idx = np.argmax(similarities)
        
        # The most similar chunk should contain Python content
        assert "Python" in chunks[most_similar_idx].text or "python" in chunks[most_similar_idx].text.lower()
    
    def test_multilingual_chunk_retrieval(self, generator, chunking_engine):
        """Test that Urdu queries can match Urdu chunks."""
        # Create pages with Urdu content (longer to ensure multiple chunks)
        pages = [
            PageContent(
                page_number=1,
                text="پائتھون ایک اعلیٰ سطح کی پروگرامنگ زبان ہے۔ " * 20 +
                     "یہ ویب ڈیولپمنٹ کے لیے وسیع پیمانے پر استعمال ہوتی ہے۔",
                metadata={"language": "ur"}
            ),
            PageContent(
                page_number=2,
                text="جاوا اسکرپٹ ویب براؤزرز کے لیے ایک اسکرپٹنگ زبان ہے۔ " * 20 +
                     "یہ انٹرایکٹو ویب صفحات کو فعال کرتی ہے۔",
                metadata={"language": "ur"}
            )
        ]
        
        # Create chunks
        chunks = chunking_engine.create_chunks(pages, book_id="test_book")
        
        # Generate chunk embeddings
        chunk_texts = [chunk.text for chunk in chunks]
        chunk_embeddings = generator.generate_batch_embeddings(chunk_texts)
        
        # Create an Urdu query about Python
        query = "پائتھون کیا ہے؟"
        query_embedding = generator.generate_embedding(query)
        
        # Calculate similarities
        similarities = []
        for chunk_emb in chunk_embeddings:
            similarity = np.dot(query_embedding, chunk_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_emb)
            )
            similarities.append(similarity)
        
        # Find the most similar chunk
        most_similar_idx = np.argmax(similarities)
        
        # The most similar chunk should contain Python content
        assert "پائتھون" in chunks[most_similar_idx].text
    
    def test_embedding_consistency_across_chunks(self, generator, chunking_engine):
        """Test that identical chunk texts produce identical embeddings."""
        # Create pages with duplicate content
        duplicate_text = "This is a test sentence that appears multiple times."
        pages = [
            PageContent(page_number=1, text=duplicate_text, metadata={}),
            PageContent(page_number=2, text=duplicate_text, metadata={}),
            PageContent(page_number=3, text="Different content here.", metadata={})
        ]
        
        # Create chunks
        chunks = chunking_engine.create_chunks(pages, book_id="test_book")
        
        # Generate embeddings
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = generator.generate_batch_embeddings(chunk_texts)
        
        # Find chunks with identical text
        identical_indices = [i for i, text in enumerate(chunk_texts) if duplicate_text in text]
        
        if len(identical_indices) >= 2:
            # Embeddings for identical text should be very similar
            emb1 = embeddings[identical_indices[0]]
            emb2 = embeddings[identical_indices[1]]
            
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            assert similarity > 0.99, "Identical texts should have very high similarity"
    
    def test_large_book_embedding_generation(self, generator, chunking_engine):
        """Test embedding generation for a large number of chunks."""
        # Create many pages
        pages = [
            PageContent(
                page_number=i,
                text=f"This is page {i} of the book. It contains content about topic {i}. " * 10,
                metadata={}
            )
            for i in range(1, 51)  # 50 pages
        ]
        
        # Create chunks
        chunks = chunking_engine.create_chunks(pages, book_id="test_book")
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = generator.generate_batch_embeddings(chunk_texts)
        
        # Verify embeddings were generated
        assert embeddings.shape[0] == len(chunks)
        assert embeddings.shape[1] == generator.get_embedding_dimension()
        
        # Verify all embeddings are valid
        assert not np.isnan(embeddings).any()
        assert not np.isinf(embeddings).any()
        
        # Verify embeddings are diverse (not all the same)
        # Check that not all embeddings are identical
        unique_embeddings = np.unique(embeddings, axis=0)
        assert len(unique_embeddings) > 1, "Embeddings should be diverse"
    
    def test_mixed_language_chunks(self, generator, chunking_engine):
        """Test embedding generation for chunks with mixed English and Urdu."""
        # Create pages with mixed content
        pages = [
            PageContent(
                page_number=1,
                text="Python is a programming language. پائتھون ایک پروگرامنگ زبان ہے۔",
                metadata={"language": "mixed"}
            ),
            PageContent(
                page_number=2,
                text="JavaScript enables web interactivity. جاوا اسکرپٹ ویب انٹرایکٹیویٹی کو فعال کرتی ہے۔",
                metadata={"language": "mixed"}
            )
        ]
        
        # Create chunks
        chunks = chunking_engine.create_chunks(pages, book_id="test_book")
        
        # Generate embeddings
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = generator.generate_batch_embeddings(chunk_texts)
        
        # Verify embeddings were generated successfully
        assert embeddings.shape[0] == len(chunks)
        assert not np.isnan(embeddings).any()
        assert not np.isinf(embeddings).any()
    
    def test_empty_chunk_handling(self, generator):
        """Test that empty chunks are handled appropriately."""
        # Try to generate embedding for empty text
        with pytest.raises(ValueError):
            generator.generate_embedding("")
        
        # Try to generate batch embeddings with empty text
        with pytest.raises(ValueError):
            generator.generate_batch_embeddings(["Valid text", "", "Another text"])
    
    def test_chunk_metadata_preservation(self, generator, chunking_engine):
        """Test that chunk metadata is preserved during embedding generation."""
        # Create pages with metadata
        pages = [
            PageContent(
                page_number=1,
                text="First page content.",
                metadata={"section": "Introduction"}
            ),
            PageContent(
                page_number=2,
                text="Second page content.",
                metadata={"section": "Chapter 1"}
            )
        ]
        
        # Create chunks
        chunks = chunking_engine.create_chunks(pages, book_id="test_book")
        
        # Generate embeddings
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = generator.generate_batch_embeddings(chunk_texts)
        
        # Verify that we can still access chunk metadata after embedding generation
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id is not None
            assert chunk.page_numbers is not None
            assert len(chunk.page_numbers) > 0
            # Embedding generation shouldn't modify chunk objects
            assert hasattr(chunk, 'text')
            assert hasattr(chunk, 'metadata')
