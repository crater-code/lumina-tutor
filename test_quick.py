"""Quick test of refactored system."""

from src.models import Chunk
from src.bounded_chatbot import BoundedChatbotEngine
from src.strict_validator import StrictGroundingValidator

# Create test chunks
chunks = [
    Chunk(
        chunk_id="test_1",
        text="Photosynthesis is the process plants use to make food. Plants take in sunlight, water, and carbon dioxide.",
        page_numbers=[42],
        start_char=0,
        end_char=100,
        metadata={}
    ),
    Chunk(
        chunk_id="test_2",
        text="During photosynthesis, chlorophyll in leaves captures light energy. This energy converts water and CO2 into glucose.",
        page_numbers=[43],
        start_char=100,
        end_char=200,
        metadata={}
    )
]

# Test chatbot
chatbot = BoundedChatbotEngine()
validator = StrictGroundingValidator()

query = "What is photosynthesis?"
response = chatbot.generate_response(query, chunks, user_age=10, language="en")

print(f"Query: {query}")
print(f"Response: {response.text}")
print(f"Is refusal: {response.is_refusal}")
print(f"Chunk IDs: {response.chunk_ids}")

# Validate
validation = validator.validate_response(response, chunks)
print(f"\nValidation:")
print(f"  Valid: {validation.is_valid}")
print(f"  Confidence: {validation.confidence}")
if validation.issues:
    print(f"  Issues: {validation.issues}")

# Test refusal
print("\n" + "="*50)
query2 = "What is quantum mechanics?"
response2 = chatbot.generate_response(query2, [], user_age=10, language="en")
print(f"Query: {query2}")
print(f"Response: {response2.text}")
print(f"Is refusal: {response2.is_refusal}")
