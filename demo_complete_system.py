"""Complete system demo - shows the refactored bounded chatbot in action."""

from src.models import Chunk
from src.bounded_chatbot import BoundedChatbotEngine
from src.strict_validator import StrictGroundingValidator
from src.hybrid_retrieval import HybridRetrievalSystem
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore

print("="*60)
print("BOUNDED CHATBOT SYSTEM - REFACTORED")
print("="*60)

# Initialize components
print("\n1. Initializing components...")
embedding_gen = EmbeddingGenerator()
vector_store = VectorStore()
retrieval = HybridRetrievalSystem(embedding_gen, vector_store)
chatbot = BoundedChatbotEngine()
validator = StrictGroundingValidator()
print("   ✓ All components initialized")

# Create sample book chunks
print("\n2. Creating sample book content...")
chunks = [
    Chunk(
        chunk_id="book_1_chunk_0",
        text="Photosynthesis is the process plants use to make their own food using sunlight, water, and air. During photosynthesis, plants take in carbon dioxide from the air and water from the soil.",
        page_numbers=[42],
        start_char=0,
        end_char=150,
        metadata={"language": "en"}
    ),
    Chunk(
        chunk_id="book_1_chunk_1",
        text="They use energy from sunlight to turn these into sugar, which is their food. This process also releases oxygen into the air, which animals need to breathe.",
        page_numbers=[42, 43],
        start_char=150,
        end_char=300,
        metadata={"language": "en"}
    ),
    Chunk(
        chunk_id="book_1_chunk_2",
        text="Chlorophyll is the green substance in leaves that captures sunlight. Without chlorophyll, plants cannot perform photosynthesis.",
        page_numbers=[43],
        start_char=300,
        end_char=400,
        metadata={"language": "en"}
    )
]
print(f"   ✓ Created {len(chunks)} sample chunks")

# Add to vector store
print("\n3. Adding chunks to vector store...")
embeddings = embedding_gen.generate_batch_embeddings([c.text for c in chunks])
vector_store.add_chunks("demo_book", chunks, embeddings)
print("   ✓ Chunks indexed in vector store")

# Test queries
print("\n4. Testing queries...")
print("-"*60)

test_cases = [
    {
        "query": "What is photosynthesis?",
        "age": 10,
        "language": "en",
        "expected": "Should return direct quote about photosynthesis"
    },
    {
        "query": "How do plants make food?",
        "age": 7,
        "language": "en",
        "expected": "Should return simplified quote"
    },
    {
        "query": "What is quantum mechanics?",
        "age": 10,
        "language": "en",
        "expected": "Should refuse (not in book)"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['query']}")
    print(f"Age: {test['age']}, Language: {test['language']}")
    print(f"Expected: {test['expected']}")
    
    # Retrieve chunks
    retrieved = retrieval.retrieve_chunks("demo_book", test['query'], top_k=3)
    print(f"Retrieved: {len(retrieved)} chunks")
    
    # Generate response
    response = chatbot.generate_response(
        test['query'],
        retrieved,
        test['age'],
        test['language']
    )
    
    # Validate
    validation = validator.validate_response(response, retrieved)
    
    print(f"\nResponse:")
    print(f"  {response.text}")
    print(f"\nMetadata:")
    print(f"  Is Refusal: {response.is_refusal}")
    print(f"  Chunk IDs: {response.chunk_ids}")
    print(f"  Valid: {validation.is_valid}")
    print(f"  Confidence: {validation.confidence}")
    if validation.issues:
        print(f"  Issues: {validation.issues}")
    
    print("-"*60)

print("\n" + "="*60)
print("DEMO COMPLETE")
print("="*60)
print("\nKey Features Demonstrated:")
print("  ✓ Template-based responses (no free-form generation)")
print("  ✓ Direct quotes from book content")
print("  ✓ Hybrid retrieval (keyword + semantic)")
print("  ✓ Strict validation (quote verification)")
print("  ✓ Age-appropriate simplification")
print("  ✓ Refusal when content not found")
print("\nThe system is now BOUNDED and VERIFIABLE!")
