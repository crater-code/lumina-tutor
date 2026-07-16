"""
Demo script for ChunkingEngine.

This script demonstrates the ChunkingEngine's ability to:
1. Create chunks from book content
2. Respect sentence boundaries
3. Handle both English and Urdu text
4. Generate unique Chunk_IDs
5. Extract metadata
"""

from src.chunking_engine import ChunkingEngine
from src.models import PageContent


def demo_basic_chunking():
    """Demonstrate basic chunking functionality."""
    print("=" * 70)
    print("DEMO 1: Basic Chunking with English Text")
    print("=" * 70)
    
    engine = ChunkingEngine(chunk_size=100, overlap=20)
    
    pages = [
        PageContent(
            page_number=1,
            text="This is the first sentence. This is the second sentence. "
                 "This is the third sentence. This is the fourth sentence. "
                 "This is the fifth sentence.",
            metadata={}
        )
    ]
    
    chunks = engine.create_chunks(pages, book_id="demo_book")
    
    print(f"\nCreated {len(chunks)} chunk(s):\n")
    for chunk in chunks:
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Text: {chunk.text[:80]}...")
        print(f"Pages: {chunk.page_numbers}")
        print(f"Position: {chunk.start_char} - {chunk.end_char}")
        print(f"Language: {chunk.metadata['language']}")
        print(f"Character count: {chunk.metadata['char_count']}")
        print("-" * 70)


def demo_multilingual_chunking():
    """Demonstrate chunking with mixed English and Urdu text."""
    print("\n" + "=" * 70)
    print("DEMO 2: Multilingual Chunking (English and Urdu)")
    print("=" * 70)
    
    engine = ChunkingEngine(chunk_size=150, overlap=30)
    
    pages = [
        PageContent(
            page_number=1,
            text="This is English text. یہ اردو متن ہے۔ More English here. "
                 "مزید اردو یہاں ہے۔ Final English sentence.",
            metadata={}
        )
    ]
    
    chunks = engine.create_chunks(pages, book_id="multilingual_book")
    
    print(f"\nCreated {len(chunks)} chunk(s):\n")
    for chunk in chunks:
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Text: {chunk.text}")
        print(f"Language: {chunk.metadata['language']}")
        print("-" * 70)


def demo_multiple_pages():
    """Demonstrate chunking across multiple pages."""
    print("\n" + "=" * 70)
    print("DEMO 3: Chunking Across Multiple Pages")
    print("=" * 70)
    
    engine = ChunkingEngine(chunk_size=80, overlap=15)
    
    pages = [
        PageContent(
            page_number=1,
            text="Page one contains the introduction. It sets the stage for the story.",
            metadata={}
        ),
        PageContent(
            page_number=2,
            text="Page two continues the narrative. The plot thickens here.",
            metadata={}
        ),
        PageContent(
            page_number=3,
            text="Page three concludes the chapter. The end is near.",
            metadata={}
        )
    ]
    
    chunks = engine.create_chunks(pages, book_id="multipage_book")
    
    print(f"\nCreated {len(chunks)} chunk(s):\n")
    for chunk in chunks:
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Text: {chunk.text}")
        print(f"Pages: {chunk.page_numbers}")
        print(f"Position: {chunk.start_char} - {chunk.end_char}")
        print("-" * 70)


def demo_urdu_text():
    """Demonstrate chunking with pure Urdu text."""
    print("\n" + "=" * 70)
    print("DEMO 4: Pure Urdu Text Chunking")
    print("=" * 70)
    
    engine = ChunkingEngine(chunk_size=100, overlap=20)
    
    # Urdu text with proper sentence endings
    pages = [
        PageContent(
            page_number=1,
            text="یہ پہلا جملہ ہے۔ یہ دوسرا جملہ ہے۔ یہ تیسرا جملہ ہے۔ "
                 "یہ چوتھا جملہ ہے۔ یہ پانچواں جملہ ہے۔",
            metadata={}
        )
    ]
    
    chunks = engine.create_chunks(pages, book_id="urdu_book")
    
    print(f"\nCreated {len(chunks)} chunk(s):\n")
    for chunk in chunks:
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Text: {chunk.text}")
        print(f"Language: {chunk.metadata['language']}")
        print(f"Character count: {chunk.metadata['char_count']}")
        print("-" * 70)


def demo_sentence_boundary_preservation():
    """Demonstrate that chunks respect sentence boundaries."""
    print("\n" + "=" * 70)
    print("DEMO 5: Sentence Boundary Preservation")
    print("=" * 70)
    
    # Use small chunk size to force splitting
    engine = ChunkingEngine(chunk_size=50, overlap=10)
    
    pages = [
        PageContent(
            page_number=1,
            text="First sentence is here. Second sentence follows. "
                 "Third sentence comes next. Fourth sentence ends it.",
            metadata={}
        )
    ]
    
    chunks = engine.create_chunks(pages, book_id="boundary_test")
    
    print(f"\nCreated {len(chunks)} chunk(s):\n")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}:")
        print(f"  ID: {chunk.chunk_id}")
        print(f"  Text: {chunk.text}")
        print(f"  Ends with punctuation: {chunk.text.strip()[-1] in '.!?۔'}")
        print("-" * 70)


def main():
    """Run all demos."""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  ChunkingEngine Demonstration".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    demo_basic_chunking()
    demo_multilingual_chunking()
    demo_multiple_pages()
    demo_urdu_text()
    demo_sentence_boundary_preservation()
    
    print("\n" + "=" * 70)
    print("All demos completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
