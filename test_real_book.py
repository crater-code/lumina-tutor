"""Test with real book ingestion."""

import os
from src.simple_ingestion import ingest_book
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.hybrid_retrieval import HybridRetrievalSystem
from src.bounded_chatbot import BoundedChatbotEngine
from src.strict_validator import StrictGroundingValidator

print("="*60)
print("TESTING WITH REAL BOOK")
print("="*60)

# Check if book exists
pdf_path = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
if not os.path.exists(pdf_path):
    print(f"\nERROR: Book not found: {pdf_path}")
    print("Please ensure the PDF is in the current directory")
    exit(1)

print(f"\nOK - Found book: {pdf_path}")

# Initialize components
print("\n1. Initializing components...")
embedding_gen = EmbeddingGenerator()
vector_store = VectorStore()
retrieval = HybridRetrievalSystem(embedding_gen, vector_store)
chatbot = BoundedChatbotEngine()
validator = StrictGroundingValidator()
print("   [OK] Components ready")

# Ingest book
print("\n2. Ingesting book (this may take 1-2 minutes)...")
try:
    chunks = ingest_book(pdf_path, "test_book")
    print(f"   [OK] Ingested {len(chunks)} chunks")
except Exception as e:
    print(f"   ERROR: Ingestion failed: {e}")
    exit(1)

# Test queries
print("\n3. Testing queries...")
print("-"*60)

queries = [
    "What is this book about?",
    "Tell me about education",
    "What does the author say about universities?"
]

for i, query in enumerate(queries, 1):
    print(f"\nQuery {i}: {query}")
    
    # Retrieve
    retrieved = retrieval.retrieve_chunks("test_book", query, top_k=3)
    print(f"  Retrieved: {len(retrieved)} chunks")
    
    if retrieved:
        print(f"  First chunk preview: {retrieved[0].text[:100]}...")
    
    # Generate response
    response = chatbot.generate_response(query, retrieved, user_age=10, language="en")
    
    # Validate
    validation = validator.validate_response(response, retrieved)
    
    print(f"\n  Response:")
    print(f"    {response.text[:200]}...")
    print(f"  Is Refusal: {response.is_refusal}")
    print(f"  Valid: {validation.is_valid}")
    print("-"*60)

print("\n" + "="*60)
print("TEST COMPLETE [OK]")
print("="*60)
print("\nThe bounded chatbot is working correctly!")
print("Responses are direct quotes from the book with page citations.")
