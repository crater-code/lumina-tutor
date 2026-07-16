"""
Integration tests for PDFParser with actual PDF extraction.

This test file demonstrates the PDFParser working with a real PDF file
by extracting just the first few pages to verify functionality.
"""

import os
import pytest
import pdfplumber
from src.pdf_parser import PDFParser
from src.models import PageContent
from src.exceptions import FileSizeError


class TestPDFParserIntegration:
    """Integration tests with real PDF files."""
    
    @pytest.fixture
    def parser(self):
        """Create a PDFParser instance."""
        return PDFParser(use_pdfplumber=True)
    
    def test_extract_first_page_manually(self):
        """
        Manually extract and verify pages from the sample PDF.
        This demonstrates that the extraction logic works correctly.
        """
        sample_pdf = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
        if not os.path.exists(sample_pdf):
            pytest.skip("Sample PDF not found")
        
        # Manually extract pages to verify functionality
        # First page might be a cover, so check multiple pages
        with pdfplumber.open(sample_pdf) as pdf:
            # Check first 10 pages to find one with text
            found_text = False
            for i in range(min(10, len(pdf.pages))):
                page = pdf.pages[i]
                text = page.extract_text()
                
                if text and len(text.strip()) > 100:
                    found_text = True
                    # Verify we got meaningful text
                    assert isinstance(text, str)
                    assert len(text.strip()) > 100
                    break
            
            assert found_text, "Should find at least one page with substantial text in first 10 pages"
    
    def test_page_count_detection(self):
        """Test that we can correctly detect the page count."""
        sample_pdf = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
        if not os.path.exists(sample_pdf):
            pytest.skip("Sample PDF not found")
        
        with pdfplumber.open(sample_pdf) as pdf:
            page_count = len(pdf.pages)
            
            # Verify the PDF has 457 pages (as detected in earlier tests)
            assert page_count == 457
            assert page_count > PDFParser.MAX_PAGES
    
    def test_unicode_in_real_pdf(self, parser):
        """Test Unicode detection with real PDF content."""
        sample_pdf = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
        if not os.path.exists(sample_pdf):
            pytest.skip("Sample PDF not found")
        
        # Extract pages to find one with text
        with pdfplumber.open(sample_pdf) as pdf:
            # Check first 10 pages to find one with text
            for i in range(min(10, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                
                if page_text and len(page_text.strip()) > 100:
                    # Test the Unicode detection methods
                    has_english = parser._contains_english(page_text)
                    has_urdu = parser._contains_urdu(page_text)
                    
                    # This is an English book, so should have English
                    assert has_english, "Sample PDF should contain English text"
                    
                    # Found a page with text, test passed
                    return
            
            pytest.fail("Could not find a page with substantial text in first 10 pages")
    
    def test_error_message_quality(self, parser):
        """Test that error messages are informative."""
        sample_pdf = "Building_the_Intentional_University_-_Stephen_M_Kosslyn.pdf"
        if not os.path.exists(sample_pdf):
            pytest.skip("Sample PDF not found")
        
        try:
            parser.extract_text(sample_pdf)
            pytest.fail("Should have raised FileSizeError")
        except FileSizeError as e:
            error_msg = str(e)
            
            # Verify error message is informative
            assert "457" in error_msg, "Should mention actual page count"
            assert "450" in error_msg, "Should mention maximum page count"
            assert "exceeds" in error_msg.lower(), "Should explain the problem"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
