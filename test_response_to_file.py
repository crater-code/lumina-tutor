"""Test Gemini response and save to file."""

from dotenv import load_dotenv
load_dotenv()

from src.bounded_chatbot import BoundedChatbotEngine
from src.models import Chunk

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

# Write to file
with open("gemini_response_test.txt", "w", encoding="utf-8") as f:
    f.write("FULL RESPONSE:\n")
    f.write("=" * 80 + "\n")
    f.write(response.text)
    f.write("\n" + "=" * 80 + "\n")
    f.write(f"\nLength: {len(response.text)} characters\n")
    f.write(f"Words: {len(response.text.split())} words\n")

print("Response saved to gemini_response_test.txt")
print(f"Length: {len(response.text)} characters")
