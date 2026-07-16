"""
Demo script for the RetrievalSystem class.

This script demonstrates the functionality of the RetrievalSystem,
showing how it retrieves relevant chunks based on user queries.
"""

from src.retrieval_system import RetrievalSystem
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.models import Chunk


def main():
    print("=" * 70)
    print("RetrievalSystem Demo - Book-Bounded Tutoring Chatbot")
    print("=" * 70)
    print()
    
    # Initialize components
    print("1. Initializing components...")
    embedding_generator = EmbeddingGenerator()
    vector_store = VectorStore(storage_dir="data/demo_vector_store")
    retrieval_system = RetrievalSystem(embedding_generator, vector_store)
    print("   ✓ Components initialized")
    print()
    
    # Create sample book chunks
    print("2. Creating sample book chunks...")
    chunks = [
        Chunk(
            chunk_id="book_science_chunk_0",
            text="Photosynthesis is the process by which plants convert sunlight into energy. "
                 "Plants use chlorophyll in their leaves to absorb light energy from the sun.",
            page_numbers=[1],
            start_char=0,
            end_char=150,
            metadata={"section": "Biology", "topic": "Photosynthesis"}
        ),
        Chunk(
            chunk_id="book_science_chunk_1",
            text="The water cycle describes how water moves through the environment. "
                 "Water evaporates from oceans and lakes, forms clouds, and falls as rain.",
            page_numbers=[2],
            start_char=0,
            end_char=140,
            metadata={"section": "Earth Science", "topic": "Water Cycle"}
        ),
        Chunk(
            chunk_id="book_science_chunk_2",
            text="Gravity is the force that attracts objects toward each other. "
                 "The Earth's gravity keeps us on the ground and the Moon in orbit.",
            page_numbers=[3],
            start_char=0,
            end_char=125,
            metadata={"section": "Physics", "topic": "Gravity"}
        ),
        Chunk(
            chunk_id="book_science_chunk_3",
            text="The human heart pumps blood throughout the body. "
                 "It beats about 100,000 times per day, circulating oxygen and nutrients.",
            page_numbers=[4],
            start_char=0,
            end_char=120,
            metadata={"section": "Biology", "topic": "Human Body"}
        ),
    ]
    print(f"   ✓ Created {len(chunks)} sample chunks")
    print()
    
    # Generate embeddings and add to vector store
    print("3. Generating embeddings and storing chunks...")
    texts = [chunk.text for chunk in chunks]
    embeddings = embedding_generator.generate_batch_embeddings(texts)
    vector_store.add_chunks("book_science", chunks, embeddings)
    print(f"   ✓ Stored {len(chunks)} chunks in vector store")
    print()
    
    # Test queries
    queries = [
        ("How do plants make energy?", 3, 0.0),
        ("What is the water cycle?", 2, 0.0),
        ("Tell me about gravity", 2, 0.0),
        ("پودے کیسے توانائی بناتے ہیں؟", 2, 0.0),  # Urdu: "How do plants make energy?"
    ]
    
    print("4. Testing retrieval with different queries:")
    print("-" * 70)
    
    for i, (query, top_k, min_sim) in enumerate(queries, 1):
        print(f"\nQuery {i}: '{query}'")
        print(f"Requesting top-{top_k} chunks with min_similarity={min_sim}")
        print()
        
        try:
            # Retrieve chunks
            retrieved_chunks = retrieval_system.retrieve_chunks(
                book_id="book_science",
                query=query,
                top_k=top_k,
                min_similarity=min_sim
            )
            
            if retrieved_chunks:
                print(f"   Found {len(retrieved_chunks)} relevant chunk(s):")
                for j, chunk in enumerate(retrieved_chunks, 1):
                    print(f"\n   [{j}] Chunk ID: {chunk.chunk_id}")
                    print(f"       Page(s): {chunk.page_numbers}")
                    print(f"       Topic: {chunk.metadata.get('topic', 'N/A')}")
                    print(f"       Text: {chunk.text[:100]}...")
            else:
                print("   No relevant chunks found above threshold")
        
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        print()
    
    print("-" * 70)
    print()
    
    # Test edge cases
    print("5. Testing edge cases:")
    print()
    
    # Empty query
    print("   a) Empty query:")
    try:
        retrieval_system.retrieve_chunks("book_science", "", top_k=5)
        print("      ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"      ✓ Correctly raised ValueError: {str(e)}")
    print()
    
    # Non-existent book
    print("   b) Non-existent book:")
    try:
        results = retrieval_system.retrieve_chunks(
            "nonexistent_book",
            "test query",
            top_k=5
        )
        print(f"      ✓ Returned empty list: {results}")
    except Exception as e:
        print(f"      ✗ Unexpected error: {str(e)}")
    print()
    
    # High similarity threshold
    print("   c) Very high similarity threshold (0.99):")
    try:
        results = retrieval_system.retrieve_chunks(
            "book_science",
            "quantum mechanics",
            top_k=5,
            min_similarity=0.99
        )
        print(f"      ✓ Returned {len(results)} chunks (expected 0 or very few)")
    except Exception as e:
        print(f"      ✗ Unexpected error: {str(e)}")
    print()
    
    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
