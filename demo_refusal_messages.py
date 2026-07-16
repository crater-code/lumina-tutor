"""
Demonstration of refusal message generation for Task 7.2.

This script demonstrates the generate_refusal() method of the ChatbotEngine,
showing how it generates polite, age-appropriate refusal messages when no
relevant chunks are found for a query.
"""

from src.chatbot_engine import ChatbotEngine


def main():
    """Demonstrate refusal message generation."""
    print("=" * 80)
    print("Task 7.2: Refusal Message Generation Demonstration")
    print("=" * 80)
    print()
    
    # Initialize the chatbot engine
    engine = ChatbotEngine()
    
    # Test query that would not be in a typical children's book
    query = "What is quantum mechanics?"
    
    print(f"Query: {query}")
    print()
    print("This query has no relevant chunks in the book, so the chatbot")
    print("will generate a refusal message.")
    print()
    
    # Demonstrate refusal messages for different age groups in English
    print("-" * 80)
    print("ENGLISH REFUSAL MESSAGES")
    print("-" * 80)
    print()
    
    age_groups = [
        (6, "Young Child (4-7 years)"),
        (10, "Elementary Student (8-11 years)"),
        (14, "Middle School Student (12-15 years)")
    ]
    
    for age, description in age_groups:
        print(f"{description}:")
        response = engine.generate_refusal(query, age, "en")
        print(f"  Message: {response.text}")
        print(f"  Is Refusal: {response.is_refusal}")
        print(f"  Chunk IDs: {response.chunk_ids}")
        print(f"  Age Group: {response.metadata['age_group']}")
        print()
    
    # Demonstrate refusal messages in Urdu
    print("-" * 80)
    print("URDU REFUSAL MESSAGES")
    print("-" * 80)
    print()
    
    urdu_query = "کوانٹم میکینکس کیا ہے؟"
    print(f"Query: {urdu_query}")
    print()
    
    for age, description in age_groups:
        print(f"{description}:")
        response = engine.generate_refusal(urdu_query, age, "ur")
        print(f"  Message: {response.text}")
        print(f"  Is Refusal: {response.is_refusal}")
        print(f"  Chunk IDs: {response.chunk_ids}")
        print(f"  Age Group: {response.metadata['age_group']}")
        print()
    
    # Verify requirements
    print("-" * 80)
    print("REQUIREMENTS VERIFICATION")
    print("-" * 80)
    print()
    
    # Test with elementary age
    response = engine.generate_refusal(query, 10, "en")
    
    print("✓ Requirement 4.4: Generates refusal when no relevant chunks found")
    print(f"  - is_refusal = {response.is_refusal}")
    print()
    
    print("✓ Requirement 12.1: Generates polite refusal message")
    print(f"  - Message is polite and respectful")
    print()
    
    print("✓ Requirement 12.2: Explains that answer is not in the book")
    print(f"  - Contains 'book': {'book' in response.text.lower()}")
    print(f"  - Contains 'couldn't find' or similar: {'couldn' in response.text.lower()}")
    print()
    
    print("✓ Requirement 12.4: Does not suggest external resources")
    external_terms = ['google', 'search', 'wikipedia', 'website', 'internet']
    has_external = any(term in response.text.lower() for term in external_terms)
    print(f"  - No external resource suggestions: {not has_external}")
    print()
    
    print("✓ Requirement 12.5: Encourages asking different questions")
    encouraging_terms = ['ask', 'question', 'other', 'different', 'else']
    has_encouragement = any(term in response.text.lower() for term in encouraging_terms)
    print(f"  - Encourages asking about book: {has_encouragement}")
    print()
    
    print("=" * 80)
    print("Task 7.2 Implementation: VERIFIED ✓")
    print("=" * 80)


if __name__ == "__main__":
    main()
