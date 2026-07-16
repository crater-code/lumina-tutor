"""
Demo script for the Database module.

This script demonstrates the database functionality including:
- Creating books
- Storing chunks
- Creating chat sessions
- Storing messages with citations
"""

import uuid
from src.database import Database


def main():
    """Demonstrate database functionality."""
    print("=" * 60)
    print("Database Module Demo")
    print("=" * 60)
    
    # Initialize database
    db = Database(db_path="data/demo.db")
    print("\n✓ Database initialized")
    
    # Create a book
    book_id = str(uuid.uuid4())
    db.create_book(
        book_id=book_id,
        title="The Adventures of Tom Sawyer",
        filename="tom_sawyer.pdf",
        page_count=250,
        language="en",
        metadata={"author": "Mark Twain", "year": 1876}
    )
    print(f"\n✓ Created book: {book_id}")
    
    # Update book status
    db.update_book_status(book_id, "processing")
    print("✓ Updated book status to 'processing'")
    
    # Create some chunks
    print("\n--- Creating chunks ---")
    chunk_ids = []
    for i in range(3):
        chunk_id = f"book_{book_id}_chunk_{i}"
        chunk_ids.append(chunk_id)
        
        db.create_chunk(
            chunk_id=chunk_id,
            book_id=book_id,
            text=f"This is chunk {i} from Tom Sawyer. It contains exciting adventures...",
            page_numbers=[i * 10 + 1, i * 10 + 2],
            start_char=i * 1000,
            end_char=(i + 1) * 1000,
            metadata={"chapter": i + 1}
        )
        print(f"✓ Created chunk {i}: {chunk_id}")
    
    # Update book status to completed
    db.update_book_status(book_id, "completed")
    print("\n✓ Updated book status to 'completed'")
    
    # List all books
    print("\n--- All books in database ---")
    books = db.list_books()
    for book in books:
        print(f"  • {book['title']} ({book['page_count']} pages) - Status: {book['processing_status']}")
    
    # List chunks for the book
    print(f"\n--- Chunks for '{books[0]['title']}' ---")
    chunks = db.list_chunks_by_book(book_id)
    print(f"  Total chunks: {len(chunks)}")
    for chunk in chunks[:2]:  # Show first 2
        print(f"  • {chunk['chunk_id']}: Pages {chunk['page_numbers']}")
    
    # Create a chat session
    session_id = str(uuid.uuid4())
    db.create_chat_session(
        session_id=session_id,
        book_id=book_id,
        user_age=10
    )
    print(f"\n✓ Created chat session: {session_id}")
    print(f"  User age: 10")
    
    # Create a conversation
    print("\n--- Creating conversation ---")
    
    # User message
    user_msg_id = str(uuid.uuid4())
    db.create_message(
        message_id=user_msg_id,
        session_id=session_id,
        role="user",
        content="What adventures does Tom Sawyer have?"
    )
    print("✓ User: What adventures does Tom Sawyer have?")
    
    # Assistant response with citations
    assistant_msg_id = str(uuid.uuid4())
    db.create_message(
        message_id=assistant_msg_id,
        session_id=session_id,
        role="assistant",
        content="Tom Sawyer has many exciting adventures including...",
        chunk_ids=[chunk_ids[0], chunk_ids[1]]
    )
    print(f"✓ Assistant: Tom Sawyer has many exciting adventures including...")
    print(f"  Citations: {chunk_ids[0]}, {chunk_ids[1]}")
    
    # Retrieve conversation history
    print("\n--- Conversation history ---")
    messages = db.list_messages_by_session(session_id)
    for msg in messages:
        role = msg['role'].capitalize()
        content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
        print(f"  {role}: {content}")
        if msg['chunk_ids']:
            print(f"    └─ Citations: {len(msg['chunk_ids'])} chunks")
    
    # Get a specific chunk
    print("\n--- Retrieving specific chunk ---")
    chunk = db.get_chunk(chunk_ids[0])
    if chunk:
        print(f"  Chunk ID: {chunk['chunk_id']}")
        print(f"  Pages: {chunk['page_numbers']}")
        print(f"  Text: {chunk['text'][:60]}...")
    
    # Database statistics
    print("\n--- Database statistics ---")
    all_books = db.list_books()
    all_chunks = db.list_chunks_by_book(book_id)
    all_sessions = db.list_chat_sessions_by_book(book_id)
    all_messages = db.list_messages_by_session(session_id)
    
    print(f"  Total books: {len(all_books)}")
    print(f"  Total chunks: {len(all_chunks)}")
    print(f"  Total sessions: {len(all_sessions)}")
    print(f"  Total messages: {len(all_messages)}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
