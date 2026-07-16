"""
Demo script for the ChatbotEngine class.

This script demonstrates:
1. Creating a ChatbotEngine instance
2. Generating responses with retrieved chunks
3. Age-adaptive language prompting
4. Multilingual support (English and Urdu)
5. Refusal message generation
"""

import os
from src.chatbot_engine import ChatbotEngine
from src.models import Chunk


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def demo_basic_response():
    """Demonstrate basic response generation."""
    print("DEMO 1: Basic Response Generation")
    print("-" * 80)
    
    # Create ChatbotEngine
    engine = ChatbotEngine()
    
    # Create sample chunks
    chunks = [
        Chunk(
            chunk_id="book_1_chunk_0",
            text="Photosynthesis is the process by which green plants convert sunlight into energy. Plants use chlorophyll, a green pigment, to absorb light energy from the sun.",
            page_numbers=[1],
            start_char=0,
            end_char=160,
            metadata={"section": "Biology"}
        ),
        Chunk(
            chunk_id="book_1_chunk_1",
            text="During photosynthesis, plants take in carbon dioxide from the air and water from the soil. They use sunlight to convert these into glucose (sugar) and oxygen.",
            page_numbers=[1],
            start_char=161,
            end_char=310,
            metadata={"section": "Biology"}
        ),
    ]
    
    # Generate response
    query = "How do plants make energy?"
    response = engine.generate_response(
        query=query,
        retrieved_chunks=chunks,
        user_age=10,
        language="en"
    )
    
    print(f"Query: {query}")
    print(f"\nResponse: {response.text}")
    print(f"\nChunk IDs used: {', '.join(response.chunk_ids)}")
    print(f"Age group: {response.metadata['age_group']}")
    print(f"Language: {response.metadata['language']}")
    print(f"Is refusal: {response.is_refusal}")


def demo_age_adaptation():
    """Demonstrate age-adaptive language prompting."""
    print("DEMO 2: Age-Adaptive Language")
    print("-" * 80)
    
    engine = ChatbotEngine()
    
    chunk = [
        Chunk(
            chunk_id="book_1_chunk_0",
            text="The water cycle is the continuous movement of water on Earth. Water evaporates from oceans and lakes, rises into the atmosphere, condenses into clouds, and falls back to Earth as rain or snow.",
            page_numbers=[5],
            start_char=0,
            end_char=200,
            metadata={"section": "Earth Science"}
        ),
    ]
    
    query = "What is the water cycle?"
    
    # Generate responses for different age groups
    ages = [6, 10, 14]
    age_names = ["Young Child (6)", "Elementary (10)", "Middle School (14)"]
    
    for age, age_name in zip(ages, age_names):
        response = engine.generate_response(
            query=query,
            retrieved_chunks=chunk,
            user_age=age,
            language="en"
        )
        
        print(f"\n{age_name}:")
        print(f"Response: {response.text}")
        print(f"Age group: {response.metadata['age_group']}")


def demo_multilingual_support():
    """Demonstrate multilingual support (English and Urdu)."""
    print("DEMO 3: Multilingual Support")
    print("-" * 80)
    
    engine = ChatbotEngine()
    
    chunk = [
        Chunk(
            chunk_id="book_1_chunk_0",
            text="DNA, or deoxyribonucleic acid, is the hereditary material in humans and almost all other organisms. It contains the instructions needed for an organism to develop, survive, and reproduce.",
            page_numbers=[10],
            start_char=0,
            end_char=190,
            metadata={"section": "Biology"}
        ),
    ]
    
    # English query
    print("\nEnglish Query:")
    query_en = "What is DNA?"
    response_en = engine.generate_response(
        query=query_en,
        retrieved_chunks=chunk,
        user_age=12,
        language="en"
    )
    print(f"Query: {query_en}")
    print(f"Response: {response_en.text}")
    print(f"Language: {response_en.metadata['language']}")
    
    # Urdu query
    print("\nUrdu Query:")
    query_ur = "ڈی این اے کیا ہے؟"
    response_ur = engine.generate_response(
        query=query_ur,
        retrieved_chunks=chunk,
        user_age=12,
        language="ur"
    )
    print(f"Query: {query_ur}")
    print(f"Response: {response_ur.text}")
    print(f"Language: {response_ur.metadata['language']}")


def demo_refusal_messages():
    """Demonstrate refusal message generation."""
    print("DEMO 4: Refusal Messages")
    print("-" * 80)
    
    engine = ChatbotEngine()
    
    query = "What is quantum mechanics?"
    
    # Generate refusal messages for different age groups
    print("\nRefusal messages for different age groups:")
    
    ages = [6, 10, 14]
    age_names = ["Young Child (6)", "Elementary (10)", "Middle School (14)"]
    
    for age, age_name in zip(ages, age_names):
        response = engine.generate_refusal(
            query=query,
            user_age=age,
            language="en"
        )
        
        print(f"\n{age_name}:")
        print(f"Response: {response.text}")
        print(f"Is refusal: {response.is_refusal}")
        print(f"Chunk IDs: {response.chunk_ids}")


def demo_refusal_multilingual():
    """Demonstrate refusal messages in multiple languages."""
    print("DEMO 5: Multilingual Refusal Messages")
    print("-" * 80)
    
    engine = ChatbotEngine()
    
    # English refusal
    print("\nEnglish Refusal:")
    response_en = engine.generate_refusal(
        query="What is quantum entanglement?",
        user_age=10,
        language="en"
    )
    print(f"Response: {response_en.text}")
    
    # Urdu refusal
    print("\nUrdu Refusal:")
    response_ur = engine.generate_refusal(
        query="کوانٹم الجھاؤ کیا ہے؟",
        user_age=10,
        language="ur"
    )
    print(f"Response: {response_ur.text}")


def demo_chunk_citations():
    """Demonstrate chunk citation tracking."""
    print("DEMO 6: Chunk Citation Tracking")
    print("-" * 80)
    
    engine = ChatbotEngine()
    
    chunks = [
        Chunk(
            chunk_id="book_science_chunk_5",
            text="The mitochondria is often called the powerhouse of the cell because it produces most of the cell's energy in the form of ATP.",
            page_numbers=[15],
            start_char=0,
            end_char=130,
            metadata={"section": "Cell Biology"}
        ),
        Chunk(
            chunk_id="book_science_chunk_6",
            text="Cellular respiration occurs in the mitochondria, where glucose is broken down to release energy.",
            page_numbers=[15],
            start_char=131,
            end_char=230,
            metadata={"section": "Cell Biology"}
        ),
    ]
    
    query = "What is the function of mitochondria?"
    response = engine.generate_response(
        query=query,
        retrieved_chunks=chunks,
        user_age=13,
        language="en"
    )
    
    print(f"Query: {query}")
    print(f"\nResponse: {response.text}")
    print(f"\nCitations:")
    for chunk_id in response.chunk_ids:
        # Find the chunk with this ID
        chunk = next(c for c in chunks if c.chunk_id == chunk_id)
        print(f"  - {chunk_id} (Page {chunk.page_numbers[0]})")
        print(f"    Content: {chunk.text[:80]}...")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("ChatbotEngine Demo")
    print("=" * 80)
    
    # Set environment variable to use mock LLM
    os.environ["USE_MOCK_LLM"] = "true"
    
    try:
        demo_basic_response()
        print_separator()
        
        demo_age_adaptation()
        print_separator()
        
        demo_multilingual_support()
        print_separator()
        
        demo_refusal_messages()
        print_separator()
        
        demo_refusal_multilingual()
        print_separator()
        
        demo_chunk_citations()
        print_separator()
        
        print("All demos completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
