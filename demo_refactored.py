"""Demo of refactored bounded chatbot system."""

from src.simple_ingestion import ingest_book
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.hybrid_retrieval import HybridRetrievalSystem
from src.bounded_chatbot import BoundedChatbotEngine
from src.strict_validator import StrictGroundingValidator

# Initialize
embedding_gen = EmbeddingGenerator()
vector_store = VectorStore()
retrieval = HybridRetrievalSystem(embedding_gen, vector_store)
chatbot = BoundedChatbotEngine()
validator = StrictGroundingValidator()

# Ingest book
print("=== Ingesting Book ===")
pdf_path = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
chunks = ingest_book(pdf_path, "demo_book")

# Test queries
queries = [
    "What is the main topic of this book?",
    "Tell me about education",
    "What does the author say about learning?"
]

print("\n=== Testing Queries ===")
for query in queries:
    print(f"\nQuery: {query}")
    
    # Retrieve
    retrieved = retrieval.retrieve_chunks("demo_book", query, top_k=3)
    print(f"Retrieved {len(retrieved)} chunks")
    
    # Generate response
    response = chatbot.generate_response(query, retrieved, user_age=10, language="en")
    
    # Validate
    validation = validator.validate_response(response, retrieved)
    
    print(f"Response: {response.text}")
    print(f"Valid: {validation.is_valid}")
    if validation.issues:
        print(f"Issues: {validation.issues}")
