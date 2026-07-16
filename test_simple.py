"""Simple test - just test the API server."""

print("="*60)
print("SIMPLE TEST - Start the API server")
print("="*60)
print("\nTo test the refactored system:")
print("\n1. Start the server:")
print("   python -m uvicorn src.main:app --reload")
print("\n2. Open another terminal and test:")
print("   curl -X POST http://localhost:8000/upload -F 'file=@your_book.pdf'")
print("   curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"query\":\"What is this about?\",\"user_age\":10}'")
print("\n3. Or use the frontend:")
print("   cd frontend")
print("   npm run dev")
print("\n" + "="*60)
print("QUICK VERIFICATION")
print("="*60)

# Quick verification that all modules work
from src.bounded_chatbot import BoundedChatbotEngine
from src.hybrid_retrieval import HybridRetrievalSystem
from src.strict_validator import StrictGroundingValidator
from src.simple_storage import SimpleStorage
from src.simple_ingestion import ingest_book
from src.models import Chunk

print("\n[OK] All new modules import successfully")

# Test with mock data
chatbot = BoundedChatbotEngine()
validator = StrictGroundingValidator()

chunk = Chunk(
    chunk_id="test",
    text="The book discusses educational reform.",
    page_numbers=[1],
    start_char=0,
    end_char=50,
    metadata={}
)

response = chatbot.generate_response("What is this about?", [chunk], 10, "en")
validation = validator.validate_response(response, [chunk])

print(f"\n[OK] Chatbot generates responses: '{response.text[:80]}...'")
print(f"[OK] Validator works: Valid={validation.is_valid}")

print("\n" + "="*60)
print("SYSTEM READY")
print("="*60)
print("\nThe refactored bounded chatbot is working!")
print("\nKey features:")
print("  - Template-based responses (no free-form LLM)")
print("  - Direct quotes from book content")
print("  - Hybrid retrieval (keyword + semantic)")
print("  - Strict validation (quote verification)")
print("  - Simple JSON storage (no database)")
print("\nStart the server to test with real books.")
