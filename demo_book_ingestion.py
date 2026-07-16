"""
Demo script for the BookIngestionPipeline.

This script demonstrates how to use the BookIngestionPipeline to ingest
a PDF book into the system.
"""

import os
import sys
from src.book_ingestion_pipeline import BookIngestionPipeline


def main():
    """Main demo function."""
    print("=" * 60)
    print("Book Ingestion Pipeline Demo")
    print("=" * 60)
    print()
    
    # Create pipeline instance
    print("Initializing BookIngestionPipeline...")
    pipeline = BookIngestionPipeline()
    print("✓ Pipeline initialized")
    print()
    
    # Check if a PDF path was provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Use sample PDF if available
        pdf_path = "test_data/sample.pdf"
        
        if not os.path.exists(pdf_path):
            print("No PDF file provided and sample PDF not found.")
            print()
            print("Usage: python demo_book_ingestion.py <path_to_pdf>")
            print()
            print("Example:")
            print("  python demo_book_ingestion.py my_book.pdf")
            return
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    print(f"PDF File: {pdf_path}")
    print()
    
    # Ingest the book
    print("Starting book ingestion...")
    print("-" * 60)
    
    result = pipeline.ingest_book(
        pdf_path=pdf_path,
        title=os.path.basename(pdf_path).replace(".pdf", "")
    )
    
    print("-" * 60)
    print()
    
    # Display results
    if result["status"] == "completed":
        print("✓ Book ingestion completed successfully!")
        print()
        print("Results:")
        print(f"  Book ID:      {result['book_id']}")
        print(f"  Status:       {result['status']}")
        print(f"  Pages:        {result['page_count']}")
        print(f"  Chunks:       {result['chunk_count']}")
        print(f"  Language:     {result['language']}")
        print()
        
        # Show book status
        print("Book Status:")
        book_status = pipeline.get_book_status(result['book_id'])
        if book_status:
            print(f"  Title:        {book_status['title']}")
            print(f"  Filename:     {book_status['filename']}")
            print(f"  Upload Date:  {book_status['upload_date']}")
            print(f"  Status:       {book_status['processing_status']}")
        print()
        
        # List all books
        print("All Books in System:")
        books = pipeline.list_books()
        for i, book in enumerate(books, 1):
            print(f"  {i}. {book['title']} (ID: {book['book_id']}, Status: {book['processing_status']})")
        print()
        
    else:
        print("✗ Book ingestion failed!")
        print()
        print("Error Details:")
        print(f"  Error Type:   {result.get('error_type', 'Unknown')}")
        print(f"  Error:        {result.get('error', 'No error message')}")
        print()
    
    print("=" * 60)
    print("Demo completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
