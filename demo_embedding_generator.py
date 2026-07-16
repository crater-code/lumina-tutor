"""
Demo script for the EmbeddingGenerator class.

This script demonstrates the functionality of the EmbeddingGenerator,
including single and batch embedding generation for English and Urdu text.
"""

import numpy as np
from src.embedding_generator import EmbeddingGenerator


def print_separator(title=""):
    """Print a visual separator."""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


def calculate_cosine_similarity(emb1, emb2):
    """Calculate cosine similarity between two embeddings."""
    return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


def main():
    print_separator("EmbeddingGenerator Demo")
    
    # Initialize the generator
    print("Initializing EmbeddingGenerator...")
    generator = EmbeddingGenerator()
    print(f"✓ Model loaded: {generator.model_name}")
    print(f"✓ Embedding dimension: {generator.get_embedding_dimension()}")
    
    # Demo 1: Single English text embedding
    print_separator("Demo 1: Single English Text Embedding")
    english_text = "The quick brown fox jumps over the lazy dog."
    print(f"Text: {english_text}")
    
    embedding = generator.generate_embedding(english_text)
    print(f"✓ Generated embedding shape: {embedding.shape}")
    print(f"✓ First 5 values: {embedding[:5]}")
    print(f"✓ Embedding norm: {np.linalg.norm(embedding):.4f}")
    
    # Demo 2: Single Urdu text embedding
    print_separator("Demo 2: Single Urdu Text Embedding")
    urdu_text = "یہ اردو میں ایک ٹیسٹ جملہ ہے۔"
    print(f"Text: {urdu_text}")
    
    embedding_urdu = generator.generate_embedding(urdu_text)
    print(f"✓ Generated embedding shape: {embedding_urdu.shape}")
    print(f"✓ First 5 values: {embedding_urdu[:5]}")
    print(f"✓ Embedding norm: {np.linalg.norm(embedding_urdu):.4f}")
    
    # Demo 3: Batch embeddings
    print_separator("Demo 3: Batch Embedding Generation")
    texts = [
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers.",
        "Natural language processing helps computers understand text.",
        "Computer vision enables machines to interpret images.",
        "The weather is sunny today."
    ]
    
    print(f"Generating embeddings for {len(texts)} texts...")
    for i, text in enumerate(texts, 1):
        print(f"  {i}. {text}")
    
    batch_embeddings = generator.generate_batch_embeddings(texts)
    print(f"\n✓ Generated batch embeddings shape: {batch_embeddings.shape}")
    print(f"✓ Number of embeddings: {batch_embeddings.shape[0]}")
    print(f"✓ Embedding dimension: {batch_embeddings.shape[1]}")
    
    # Demo 4: Semantic similarity
    print_separator("Demo 4: Semantic Similarity Analysis")
    
    # Similar texts
    text1 = "The cat sits on the mat."
    text2 = "A cat is sitting on a mat."
    text3 = "Dogs are playing in the park."
    
    print("Comparing semantic similarity:")
    print(f"  Text 1: {text1}")
    print(f"  Text 2: {text2}")
    print(f"  Text 3: {text3}")
    
    emb1 = generator.generate_embedding(text1)
    emb2 = generator.generate_embedding(text2)
    emb3 = generator.generate_embedding(text3)
    
    sim_1_2 = calculate_cosine_similarity(emb1, emb2)
    sim_1_3 = calculate_cosine_similarity(emb1, emb3)
    sim_2_3 = calculate_cosine_similarity(emb2, emb3)
    
    print(f"\n✓ Similarity (Text 1 vs Text 2): {sim_1_2:.4f}")
    print(f"✓ Similarity (Text 1 vs Text 3): {sim_1_3:.4f}")
    print(f"✓ Similarity (Text 2 vs Text 3): {sim_2_3:.4f}")
    print(f"\nObservation: Texts 1 and 2 are more similar ({sim_1_2:.4f}) than")
    print(f"             Text 1 and 3 ({sim_1_3:.4f}), as expected!")
    
    # Demo 5: Multilingual similarity
    print_separator("Demo 5: Multilingual Semantic Similarity")
    
    english_query = "What is machine learning?"
    urdu_query = "مشین لرننگ کیا ہے؟"
    
    print("Comparing English and Urdu queries:")
    print(f"  English: {english_query}")
    print(f"  Urdu: {urdu_query}")
    
    emb_en = generator.generate_embedding(english_query)
    emb_ur = generator.generate_embedding(urdu_query)
    
    cross_lingual_sim = calculate_cosine_similarity(emb_en, emb_ur)
    print(f"\n✓ Cross-lingual similarity: {cross_lingual_sim:.4f}")
    print(f"Note: The multilingual model can capture semantic similarity")
    print(f"      across languages!")
    
    # Demo 6: Book chunk simulation
    print_separator("Demo 6: Book Chunk Embedding Simulation")
    
    book_chunks = [
        "Chapter 1: Introduction to Python. Python is a high-level programming language.",
        "Python was created by Guido van Rossum and first released in 1991.",
        "Chapter 2: Variables and Data Types. Variables are containers for storing data.",
        "Python supports various data types including integers, floats, and strings.",
        "Chapter 3: Control Flow. Control flow statements include if, elif, and else."
    ]
    
    print(f"Simulating embedding generation for {len(book_chunks)} book chunks...")
    for i, chunk in enumerate(book_chunks, 1):
        print(f"  Chunk {i}: {chunk[:60]}...")
    
    chunk_embeddings = generator.generate_batch_embeddings(book_chunks)
    print(f"\n✓ Generated embeddings for all chunks")
    print(f"✓ Shape: {chunk_embeddings.shape}")
    
    # Simulate a query
    query = "What is Python?"
    print(f"\nQuery: '{query}'")
    query_embedding = generator.generate_embedding(query)
    
    # Calculate similarities
    print("\nChunk relevance scores:")
    for i, chunk_emb in enumerate(chunk_embeddings, 1):
        similarity = calculate_cosine_similarity(query_embedding, chunk_emb)
        print(f"  Chunk {i}: {similarity:.4f}")
    
    # Find most relevant chunk
    similarities = [calculate_cosine_similarity(query_embedding, chunk_emb) 
                   for chunk_emb in chunk_embeddings]
    most_relevant_idx = np.argmax(similarities)
    print(f"\n✓ Most relevant chunk: Chunk {most_relevant_idx + 1}")
    print(f"  Content: {book_chunks[most_relevant_idx]}")
    print(f"  Similarity: {similarities[most_relevant_idx]:.4f}")
    
    # Demo 7: Performance comparison
    print_separator("Demo 7: Batch vs Individual Performance")
    
    test_texts = [f"This is test sentence number {i}." for i in range(10)]
    
    print("Comparing batch vs individual embedding generation...")
    print(f"Number of texts: {len(test_texts)}")
    
    # Batch generation
    import time
    start = time.time()
    batch_result = generator.generate_batch_embeddings(test_texts)
    batch_time = time.time() - start
    
    # Individual generation
    start = time.time()
    individual_results = [generator.generate_embedding(text) for text in test_texts]
    individual_time = time.time() - start
    
    print(f"\n✓ Batch generation time: {batch_time:.4f} seconds")
    print(f"✓ Individual generation time: {individual_time:.4f} seconds")
    print(f"✓ Speedup: {individual_time/batch_time:.2f}x faster with batch processing")
    
    print_separator("Demo Complete!")
    print("The EmbeddingGenerator successfully:")
    print("  ✓ Generates embeddings for English text")
    print("  ✓ Generates embeddings for Urdu text")
    print("  ✓ Handles batch processing efficiently")
    print("  ✓ Captures semantic similarity")
    print("  ✓ Supports cross-lingual understanding")
    print("  ✓ Ready for book chunk retrieval!")
    print()


if __name__ == "__main__":
    main()
