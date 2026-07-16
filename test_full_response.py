"""Test full Gemini response length."""

from dotenv import load_dotenv
load_dotenv()

from src.bounded_chatbot import BoundedChatbotEngine
from src.models import Chunk

print("Testing full response length...")
print()

bot = BoundedChatbotEngine()

test_chunk = Chunk(
    chunk_id="test_1",
    text="Photosynthesis is the process by which plants convert sunlight into energy. Plants use chlorophyll in their leaves to capture light energy from the sun. This energy is then used to convert carbon dioxide and water into glucose (sugar) and oxygen.",
    page_numbers=[1],
    start_char=0,
    end_char=250
)

response = bot._handle_content_query(
    query="What is photosynthesis?",
    chunks=[test_chunk],
    user_age=10,
    language="en"
)

print("FULL RESPONSE:")
print("=" * 80)
print(response.text)
print("=" * 80)
print()
print(f"Response length: {len(response.text)} characters")
print(f"Response words: {len(response.text.split())} words")
