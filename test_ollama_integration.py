"""Test Ollama integration directly."""

from src.bounded_chatbot import BoundedChatbotEngine
from src.models import Chunk

# Create chatbot
bot = BoundedChatbotEngine()

print(f"Ollama available: {bot.llm_available}")
print(f"Ollama URL: {bot.ollama_url}")
print(f"Ollama model: {bot.ollama_model}")

# Create test chunks
chunks = [
    Chunk(
        chunk_id="test1",
        text="On one side are those who say that a college education is overpriced or, worse, a complete waste of money",
        page_numbers=[13],
        start_char=0,
        end_char=100
    )
]

# Test content query
print("\n=== Testing Content Query ===")
response = bot._handle_content_query(
    query="What does the book say about universities?",
    chunks=chunks,
    user_age=None,
    language="en"
)

print(f"\nResponse text:\n{response.text}")
print(f"\nIs refusal: {response.is_refusal}")
