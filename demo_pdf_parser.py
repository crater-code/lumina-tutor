"""
Demonstration script for PDFParser functionality.

This script demonstrates the PDFParser class extracting text from PDF files,
handling Unicode characters, and validating page counts.
"""

from src.pdf_parser import PDFParser
from src.exceptions import FileSizeError, PDFParseError, NoTextError


def main():
    """Demonstrate PDFParser functionality."""
    print("=" * 70)
    print("PDF Parser Demonstration")
    print("=" * 70)
    print()
    
    # Create parser instance
    parser = PDFParser(use_pdfplumber=True)
    print(f"✓ Created PDFParser (max pages: {PDFParser.MAX_PAGES})")
    print()
    
    # Test with the sample PDF
    sample_pdf = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
    
    print(f"Testing with: {sample_pdf}")
    print("-" * 70)
    
    try:
        print("Attempting to extract text...")
        pages = parser.extract_text(sample_pdf)
        
        # If we get here, extraction succeeded
        print(f"✓ Successfully extracted {len(pages)} pages")
        print()
        
        # Show statistics
        total_chars = sum(len(page.text) for page in pages)
        pages_with_text = sum(1 for page in pages if len(page.text) > 0)
        
        print("Statistics:")
        print(f"  - Total pages: {len(pages)}")
        print(f"  - Pages with text: {pages_with_text}")
        print(f"  - Total characters: {total_chars:,}")
        print()
        
        # Show first page with text
        for page in pages[:10]:
            if len(page.text) > 100:
                print(f"Sample from page {page.page_number}:")
                print(f"  - Language: {page.metadata.get('language', 'unknown')}")
                print(f"  - Character count: {page.metadata.get('char_count', 0)}")
                print(f"  - Text preview: {page.text[:200]}...")
                break
        
    except FileSizeError as e:
        print(f"✗ File size error: {e}")
        print()
        print("This is expected! The sample PDF has 457 pages,")
        print(f"which exceeds the maximum of {PDFParser.MAX_PAGES} pages.")
        print()
        print("This demonstrates that the page count validation is working correctly.")
        
    except NoTextError as e:
        print(f"✗ No text error: {e}")
        print("The PDF contains no extractable text.")
        
    except PDFParseError as e:
        print(f"✗ Parse error: {e}")
        print("Failed to parse the PDF file.")
    
    print()
    print("=" * 70)
    print("Demonstration of Unicode Detection")
    print("=" * 70)
    print()
    
    # Test Unicode detection
    test_texts = [
        ("English text", "Hello, this is a test."),
        ("Urdu text", "سلام، یہ ایک ٹیسٹ ہے۔"),
        ("Mixed text", "Hello سلام World"),
        ("Numbers only", "123456789"),
        ("Empty text", ""),
    ]
    
    for label, text in test_texts:
        has_english = parser._contains_english(text)
        has_urdu = parser._contains_urdu(text)
        
        print(f"{label}:")
        print(f"  Text: {text}")
        print(f"  Has English: {has_english}")
        print(f"  Has Urdu: {has_urdu}")
        print()
    
    print("=" * 70)
    print("PDFParser demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
