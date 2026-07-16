"""Test Gemini integration with the actual chatbot."""

from dotenv import load_dotenv
load_dotenv()

from src.bounded_chatbot import BoundedChatbotEngine
from src.models import Chunk

print("=" * 60)
print("🧪 Testing Gemini Integration")
print("=" * 60)
print()

# Initialize chatbot
print("Initializing chatbot...")
bot = BoundedChatbotEngine()

print(f"Provider: {bot.llm_provider}")
print(f"Model: {bot.gemini_model}")
print(f"Available: {bot.llm_available}")
print()

if not bot.llm_available:
    print("❌ Gemini is not available!")
    exit(1)

# Create a test chunk
test_chunk = Chunk(
    chunk_id="test_1",
    text="Photosynthesis is the process by which plants convert sunlight into energy. Plants use chlorophyll in their leaves to capture light energy.",
    page_numbers=[1],
    start_char=0,
    end_char=150
)

print("Testing content query with Gemini...")
print(f"Query: 'What is photosynthesis?'")
print()

try:
    response = bot._handle_content_query(
        query="What is photosynthesis?",
        chunks=[test_chunk],
        user_age=10,
        language="en"
    )
    
    print("✅ Response generated!")
    print()
    print("Response:")
    print("-" * 60)
    print(response.text)
    print("-" * 60)
    print()
    print(f"Chunk IDs: {response.chunk_ids}")
    print(f"Is Refusal: {response.is_refusal}")
    print()
    
    # Check if response looks like it came from Gemini (not mock)
    if "Based on the book" in response.text and len(response.text) < 100:
        print("⚠️  WARNING: Response looks like mock/fallback, not Gemini!")
    else:
        print("✅ Response appears to be from Gemini!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
