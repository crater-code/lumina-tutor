"""
Demo script for the Book-Bounded Tutoring Chatbot API.

This script demonstrates how to use the API endpoints:
1. Upload a PDF book
2. List uploaded books
3. Chat with the book
4. View chat history
5. Get chunk content for citations
6. Delete a book

To run this demo:
1. Start the API server: python src/main.py
2. Run this script: python demo_api.py
"""

import requests
import json
import time
from pathlib import Path


# API base URL
BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def check_health():
    """Check if the API is running"""
    print_section("1. Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API is healthy")
            print(f"  Status: {data['status']}")
            print(f"  Service: {data['service']}")
            print(f"  Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running:")
        print("  python src/main.py")
        return False


def list_books():
    """List all uploaded books"""
    print_section("2. List Books")
    
    response = requests.get(f"{BASE_URL}/api/books")
    
    if response.status_code == 200:
        books = response.json()
        if books:
            print(f"Found {len(books)} book(s):")
            for book in books:
                print(f"\n  Book ID: {book['book_id']}")
                print(f"  Title: {book['title']}")
                print(f"  Pages: {book['page_count']}")
                print(f"  Status: {book['processing_status']}")
                print(f"  Language: {book['language']}")
        else:
            print("No books uploaded yet.")
        return books
    else:
        print(f"✗ Failed to list books: {response.status_code}")
        return []


def upload_book(pdf_path, title=None):
    """Upload a PDF book"""
    print_section("3. Upload Book")
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"✗ File not found: {pdf_path}")
        return None
    
    print(f"Uploading: {pdf_path}")
    if title:
        print(f"Title: {title}")
    
    # Prepare the file
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        data = {'title': title} if title else {}
        
        response = requests.post(
            f"{BASE_URL}/api/books/upload",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Upload successful!")
        print(f"  Book ID: {result['book_id']}")
        print(f"  Status: {result['status']}")
        if result['status'] == 'completed':
            print(f"  Pages: {result.get('page_count', 'N/A')}")
            print(f"  Chunks: {result.get('chunk_count', 'N/A')}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
        return result['book_id']
    else:
        print(f"✗ Upload failed: {response.status_code}")
        print(f"  {response.json()}")
        return None


def chat_with_book(book_id, query, user_age=10, language="en", session_id=None):
    """Send a chat message"""
    print_section(f"4. Chat: '{query}'")
    
    payload = {
        "query": query,
        "book_id": book_id,
        "user_age": user_age,
        "language": language
    }
    
    if session_id:
        payload["session_id"] = session_id
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Response received:")
        print(f"\n  {result['response']}")
        print(f"\n  Citations: {', '.join(result['chunk_ids']) if result['chunk_ids'] else 'None'}")
        print(f"  Is Refusal: {result['is_refusal']}")
        print(f"  Session ID: {result['session_id']}")
        return result
    else:
        print(f"✗ Chat failed: {response.status_code}")
        print(f"  {response.json()}")
        return None


def get_chunk(chunk_id):
    """Get chunk content"""
    print_section(f"5. Get Chunk: {chunk_id}")
    
    response = requests.get(f"{BASE_URL}/api/chunks/{chunk_id}")
    
    if response.status_code == 200:
        chunk = response.json()
        print(f"\n✓ Chunk content:")
        print(f"  Chunk ID: {chunk['chunk_id']}")
        print(f"  Pages: {chunk['page_numbers']}")
        print(f"  Text: {chunk['text'][:200]}...")
        return chunk
    else:
        print(f"✗ Failed to get chunk: {response.status_code}")
        return None


def get_chat_history(session_id):
    """Get chat history"""
    print_section(f"6. Chat History: {session_id}")
    
    response = requests.get(f"{BASE_URL}/api/chat/history/{session_id}")
    
    if response.status_code == 200:
        messages = response.json()
        print(f"\n✓ Found {len(messages)} message(s):")
        for msg in messages:
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            print(f"\n  {role_icon} {msg['role'].upper()}: {msg['content'][:100]}...")
            if msg['chunk_ids']:
                print(f"     Citations: {', '.join(msg['chunk_ids'])}")
        return messages
    else:
        print(f"✗ Failed to get chat history: {response.status_code}")
        return []


def delete_book(book_id):
    """Delete a book"""
    print_section(f"7. Delete Book: {book_id}")
    
    response = requests.delete(f"{BASE_URL}/api/books/{book_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ {result['message']}")
        return True
    else:
        print(f"✗ Failed to delete book: {response.status_code}")
        return False


def main():
    """Run the demo"""
    print("\n" + "=" * 60)
    print("  Book-Bounded Tutoring Chatbot API Demo")
    print("=" * 60)
    
    # Check if API is running
    if not check_health():
        return
    
    # List existing books
    existing_books = list_books()
    
    # Check if we have a test PDF
    test_pdf = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
    
    if Path(test_pdf).exists():
        # Upload a book
        book_id = upload_book(test_pdf, "Building the Intentional University")
        
        if book_id:
            # Wait a moment for processing
            time.sleep(1)
            
            # Chat with the book
            result1 = chat_with_book(
                book_id,
                "What is this book about?",
                user_age=12,
                language="en"
            )
            
            if result1:
                session_id = result1['session_id']
                
                # Ask another question in the same session
                result2 = chat_with_book(
                    book_id,
                    "Tell me more about universities.",
                    user_age=12,
                    language="en",
                    session_id=session_id
                )
                
                # Get chunk content if we have citations
                if result1['chunk_ids']:
                    get_chunk(result1['chunk_ids'][0])
                
                # Get chat history
                get_chat_history(session_id)
            
            # Ask if user wants to delete the book
            print("\n" + "=" * 60)
            user_input = input("\nDelete the uploaded book? (y/n): ")
            if user_input.lower() == 'y':
                delete_book(book_id)
    else:
        print(f"\n⚠ Test PDF not found: {test_pdf}")
        print("  Please provide a PDF file to test the upload functionality.")
        
        # If there are existing books, demonstrate chat with them
        if existing_books:
            book_id = existing_books[0]['book_id']
            print(f"\n  Using existing book: {existing_books[0]['title']}")
            
            result = chat_with_book(
                book_id,
                "What is this book about?",
                user_age=10,
                language="en"
            )
            
            if result and result['chunk_ids']:
                get_chunk(result['chunk_ids'][0])
    
    print("\n" + "=" * 60)
    print("  Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
