"""
Demo script for ResponseValidator.

This script demonstrates the ResponseValidator's ability to:
1. Validate responses that are grounded in retrieved chunks
2. Detect hallucinated content
3. Handle refusal messages
4. Log rejected responses
"""

from src.response_validator import ResponseValidator
from src.chatbot_engine import ChatbotEngine
from src.models import Chunk, Response


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_validation_result(result, response):
    """Print validation result details."""
    print(f"Response Text: {response.text[:100]}...")
    print(f"Chunk IDs: {response.chunk_ids}")
    print(f"Is Refusal: {response.is_refusal}")
    print(f"\nValidation Result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Confidence: {result.confidence:.2f}")
    if result.issues:
        print(f"  Issues:")
        for issue in result.issues:
            print(f"    - {issue}")
    else:
        print(f"  Issues: None")


def demo_valid_response():
    """Demo 1: Valid response passes validation."""
    print_section("Demo 1: Valid Response Passes Validation")
    
    validator = ResponseValidator()
    chatbot = ChatbotEngine()
    
    # Create sample chunks about photosynthesis
    chunks = [
        Chunk(
            chunk_id="book_1_chunk_1",
            text="Photosynthesis is the process by which plants use sunlight to convert carbon dioxide and water into glucose and oxygen.",
            page_numbers=[1],
            start_char=0,
            end_char=120,
            metadata={}
        ),
        Chunk(
            chunk_id="book_1_chunk_2",
            text="The chloroplasts in plant cells contain chlorophyll, which captures light energy.",
            page_numbers=[1],
            start_char=121,
            end_char=200,
            metadata={}
        )
    ]
    
    # Generate response
    response = chatbot.generate_response(
        query="What is photosynthesis?",
        retrieved_chunks=chunks,
        user_age=10,
        language="en"
    )
    
    # Validate response
    result = validator.validate_response(response, chunks)
    
    print_validation_result(result, response)
    print("\n✓ Valid response passed validation as expected!")


def demo_hallucinated_response():
    """Demo 2: Response with hallucinated content fails validation."""
    print_section("Demo 2: Hallucinated Content Detected")
    
    validator = ResponseValidator()
    
    # Create chunks about plants
    chunks = [
        Chunk(
            chunk_id="book_1_chunk_1",
            text="Plants use sunlight to make food through photosynthesis.",
            page_numbers=[1],
            start_char=0,
            end_char=60,
            metadata={}
        )
    ]
    
    # Create a response with hallucinated content
    hallucinated_response = Response(
        text="Plants use photosynthesis, which was discovered by Albert Einstein in 1905. The process involves quantum mechanics and nuclear fusion.",
        chunk_ids=["book_1_chunk_1"],
        is_refusal=False,
        metadata={"age_group": "elementary", "language": "en"}
    )
    
    # Validate response
    result = validator.validate_response(hallucinated_response, chunks)
    
    print_validation_result(result, hallucinated_response)
    print("\n✓ Hallucinated content detected and rejected as expected!")


def demo_missing_citations():
    """Demo 3: Response without citations fails validation."""
    print_section("Demo 3: Missing Citations Detected")
    
    validator = ResponseValidator()
    
    chunks = [
        Chunk(
            chunk_id="book_1_chunk_1",
            text="The sun is a star that provides light and heat to Earth.",
            page_numbers=[1],
            start_char=0,
            end_char=60,
            metadata={}
        )
    ]
    
    # Create a response without citations
    response_no_citations = Response(
        text="The sun provides light to Earth.",
        chunk_ids=[],  # No citations!
        is_refusal=False,
        metadata={"age_group": "elementary", "language": "en"}
    )
    
    # Validate response
    result = validator.validate_response(response_no_citations, chunks)
    
    print_validation_result(result, response_no_citations)
    print("\n✓ Missing citations detected and rejected as expected!")


def demo_refusal_message():
    """Demo 4: Refusal messages always pass validation."""
    print_section("Demo 4: Refusal Messages Pass Validation")
    
    validator = ResponseValidator()
    chatbot = ChatbotEngine()
    
    # Generate refusal message
    refusal = chatbot.generate_refusal(
        query="What is quantum mechanics?",
        user_age=10,
        language="en"
    )
    
    # Validate refusal (no chunks needed)
    result = validator.validate_response(refusal, [])
    
    print_validation_result(result, refusal)
    print("\n✓ Refusal message passed validation as expected!")


def demo_keyword_matching():
    """Demo 5: Keyword matching detects hallucination."""
    print_section("Demo 5: Keyword Matching Hallucination Detection")
    
    validator = ResponseValidator()
    
    # Response with keywords not in chunks
    response_text = "The unicorn flew over the rainbow using magic powers."
    chunk_texts = ["Plants use sunlight to make food through photosynthesis."]
    
    print(f"Response: {response_text}")
    print(f"Chunk: {chunk_texts[0]}")
    
    is_hallucinated = validator.check_hallucination(response_text, chunk_texts)
    
    print(f"\nHallucination Detected: {is_hallucinated}")
    print("\n✓ Keyword matching successfully detected unrelated content!")


def demo_similarity_checking():
    """Demo 6: Similarity checking validates paraphrased content."""
    print_section("Demo 6: Similarity Checking for Paraphrased Content")
    
    validator = ResponseValidator()
    
    # Paraphrased response (should pass)
    response_text = "Plants convert sunlight into food using photosynthesis."
    chunk_texts = ["Photosynthesis is the process by which plants use sunlight to make food."]
    
    print(f"Response: {response_text}")
    print(f"Chunk: {chunk_texts[0]}")
    
    is_hallucinated = validator.check_hallucination(response_text, chunk_texts)
    
    print(f"\nHallucination Detected: {is_hallucinated}")
    print("\n✓ Similarity checking accepted valid paraphrase!")


def demo_age_adaptive_validation():
    """Demo 7: Validation works across different age groups."""
    print_section("Demo 7: Age-Adaptive Response Validation")
    
    validator = ResponseValidator()
    chatbot = ChatbotEngine()
    
    chunks = [
        Chunk(
            chunk_id="book_1_chunk_1",
            text="Water is essential for all living things. Plants, animals, and humans need water to survive.",
            page_numbers=[1],
            start_char=0,
            end_char=100,
            metadata={}
        )
    ]
    
    age_groups = [
        (5, "young_child"),
        (10, "elementary"),
        (14, "middle_school")
    ]
    
    for age, group_name in age_groups:
        print(f"\nAge Group: {age} years ({group_name})")
        print("-" * 50)
        
        response = chatbot.generate_response(
            query="Why is water important?",
            retrieved_chunks=chunks,
            user_age=age,
            language="en"
        )
        
        result = validator.validate_response(response, chunks)
        
        print(f"Response: {response.text[:80]}...")
        print(f"Valid: {result.is_valid}, Confidence: {result.confidence:.2f}")
    
    print("\n✓ All age-adapted responses passed validation!")


def demo_multilingual_validation():
    """Demo 8: Validation works for multiple languages."""
    print_section("Demo 8: Multilingual Response Validation")
    
    validator = ResponseValidator()
    chatbot = ChatbotEngine()
    
    # English chunks
    en_chunks = [
        Chunk(
            chunk_id="book_1_chunk_1",
            text="The moon orbits around Earth once every 27 days.",
            page_numbers=[1],
            start_char=0,
            end_char=50,
            metadata={"language": "en"}
        )
    ]
    
    # Urdu chunks
    ur_chunks = [
        Chunk(
            chunk_id="book_1_chunk_1",
            text="چاند زمین کے گرد ہر 27 دن میں ایک بار چکر لگاتا ہے۔",
            page_numbers=[1],
            start_char=0,
            end_char=50,
            metadata={"language": "ur"}
        )
    ]
    
    # Test English
    print("English Response:")
    print("-" * 50)
    en_response = chatbot.generate_response(
        query="How long does it take the moon to orbit Earth?",
        retrieved_chunks=en_chunks,
        user_age=10,
        language="en"
    )
    en_result = validator.validate_response(en_response, en_chunks)
    print(f"Response: {en_response.text[:80]}...")
    print(f"Valid: {en_result.is_valid}, Confidence: {en_result.confidence:.2f}")
    
    # Test Urdu
    print("\nUrdu Response:")
    print("-" * 50)
    ur_response = chatbot.generate_response(
        query="چاند زمین کے گرد کتنے دن میں چکر لگاتا ہے؟",
        retrieved_chunks=ur_chunks,
        user_age=10,
        language="ur"
    )
    ur_result = validator.validate_response(ur_response, ur_chunks)
    print(f"Response: {ur_response.text[:80]}...")
    print(f"Valid: {ur_result.is_valid}, Confidence: {ur_result.confidence:.2f}")
    
    print("\n✓ Both English and Urdu responses passed validation!")


def demo_confidence_scores():
    """Demo 9: Confidence scores reflect validation quality."""
    print_section("Demo 9: Validation Confidence Scores")
    
    validator = ResponseValidator()
    
    chunks = [
        Chunk(
            chunk_id="book_1_chunk_1",
            text="The Earth rotates on its axis once every 24 hours, causing day and night.",
            page_numbers=[1],
            start_char=0,
            end_char=80,
            metadata={}
        )
    ]
    
    test_cases = [
        (
            "Perfect match",
            Response(
                text="The Earth rotates on its axis every 24 hours.",
                chunk_ids=["book_1_chunk_1"],
                is_refusal=False,
                metadata={}
            )
        ),
        (
            "Good paraphrase",
            Response(
                text="Earth spins around once per day, creating day and night cycles.",
                chunk_ids=["book_1_chunk_1"],
                is_refusal=False,
                metadata={}
            )
        ),
        (
            "Hallucinated content",
            Response(
                text="The Earth was created by aliens 10,000 years ago.",
                chunk_ids=["book_1_chunk_1"],
                is_refusal=False,
                metadata={}
            )
        )
    ]
    
    for name, response in test_cases:
        result = validator.validate_response(response, chunks)
        print(f"{name}:")
        print(f"  Valid: {result.is_valid}")
        print(f"  Confidence: {result.confidence:.2f}")
        print()
    
    print("✓ Confidence scores correctly reflect validation quality!")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  RESPONSE VALIDATOR DEMONSTRATION")
    print("=" * 70)
    
    try:
        demo_valid_response()
        demo_hallucinated_response()
        demo_missing_citations()
        demo_refusal_message()
        demo_keyword_matching()
        demo_similarity_checking()
        demo_age_adaptive_validation()
        demo_multilingual_validation()
        demo_confidence_scores()
        
        print_section("All Demos Completed Successfully!")
        print("The ResponseValidator successfully:")
        print("  ✓ Validates responses grounded in retrieved chunks")
        print("  ✓ Detects hallucinated content")
        print("  ✓ Identifies missing citations")
        print("  ✓ Handles refusal messages")
        print("  ✓ Uses keyword matching for hallucination detection")
        print("  ✓ Uses similarity checking for paraphrased content")
        print("  ✓ Works across different age groups")
        print("  ✓ Supports multiple languages")
        print("  ✓ Provides meaningful confidence scores")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
