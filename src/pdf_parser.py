"""
PDF Parser for extracting text from PDF files.

This module provides the PDFParser class that extracts text content from PDF files,
handling Unicode characters (English and Urdu) and validating page counts.
"""

import os
from typing import List
import PyPDF2
import pdfplumber
from src.models import PageContent
from src.exceptions import PDFParseError, FileSizeError, NoTextError


class PDFParser:
    """
    Extracts text content from PDF files with Unicode support.
    
    This parser handles both English and Urdu text, validates page counts,
    and raises appropriate exceptions for invalid PDFs.
    """
    
    MAX_PAGES = 500
    
    def __init__(self, use_pdfplumber: bool = True):
        """
        Initialize the PDF parser.
        
        Args:
            use_pdfplumber: If True, use pdfplumber (better Unicode support).
                          If False, use PyPDF2 (faster but less accurate).
        """
        self.use_pdfplumber = use_pdfplumber
    
    def extract_text(self, pdf_path: str) -> List[PageContent]:
        """
        Extracts text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PageContent objects containing text and page numbers
            
        Raises:
            PDFParseError: If PDF cannot be parsed or contains no text
            FileSizeError: If PDF exceeds 450 pages
            NoTextError: If PDF contains no extractable text
        """
        # Validate file exists
        if not os.path.exists(pdf_path):
            raise PDFParseError(f"PDF file not found: {pdf_path}")
        
        # Validate file is readable
        if not os.path.isfile(pdf_path):
            raise PDFParseError(f"Path is not a file: {pdf_path}")
        
        try:
            if self.use_pdfplumber:
                return self._extract_with_pdfplumber(pdf_path)
            else:
                return self._extract_with_pypdf2(pdf_path)
        except (FileSizeError, NoTextError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise PDFParseError(f"Failed to parse PDF: {str(e)}")
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> List[PageContent]:
        """
        Extract text using pdfplumber (better Unicode support).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PageContent objects
            
        Raises:
            FileSizeError: If PDF exceeds max pages
            NoTextError: If PDF contains no text
            PDFParseError: If extraction fails
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Validate page count
                page_count = len(pdf.pages)
                if page_count > self.MAX_PAGES:
                    raise FileSizeError(
                        f"PDF exceeds maximum page count. "
                        f"Found {page_count} pages, maximum is {self.MAX_PAGES}"
                    )
                
                # Extract text from each page
                pages = []
                total_text_length = 0
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    
                    # Handle None or empty text
                    if text is None:
                        text = ""
                    
                    # Clean up text (remove excessive whitespace)
                    text = text.strip()
                    
                    # Detect language (simple heuristic)
                    has_urdu = self._contains_urdu(text)
                    has_english = self._contains_english(text)
                    
                    language = "mixed" if (has_urdu and has_english) else (
                        "ur" if has_urdu else "en"
                    )
                    
                    metadata = {
                        "language": language,
                        "has_images": len(page.images) > 0 if hasattr(page, 'images') else False,
                        "char_count": len(text)
                    }
                    
                    pages.append(PageContent(
                        page_number=page_num,
                        text=text,
                        metadata=metadata
                    ))
                    
                    total_text_length += len(text)
                
                # Check if PDF contains any text
                if total_text_length == 0:
                    raise NoTextError("PDF contains no extractable text")
                
                return pages
                
        except (FileSizeError, NoTextError):
            raise
        except Exception as e:
            raise PDFParseError(f"pdfplumber extraction failed: {str(e)}")
    
    def _extract_with_pypdf2(self, pdf_path: str) -> List[PageContent]:
        """
        Extract text using PyPDF2 (faster but less accurate).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PageContent objects
            
        Raises:
            FileSizeError: If PDF exceeds max pages
            NoTextError: If PDF contains no text
            PDFParseError: If extraction fails
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Validate page count
                page_count = len(pdf_reader.pages)
                if page_count > self.MAX_PAGES:
                    raise FileSizeError(
                        f"PDF exceeds maximum page count. "
                        f"Found {page_count} pages, maximum is {self.MAX_PAGES}"
                    )
                
                # Extract text from each page
                pages = []
                total_text_length = 0
                
                for page_num in range(page_count):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Handle None or empty text
                    if text is None:
                        text = ""
                    
                    # Clean up text
                    text = text.strip()
                    
                    # Detect language
                    has_urdu = self._contains_urdu(text)
                    has_english = self._contains_english(text)
                    
                    language = "mixed" if (has_urdu and has_english) else (
                        "ur" if has_urdu else "en"
                    )
                    
                    metadata = {
                        "language": language,
                        "char_count": len(text)
                    }
                    
                    pages.append(PageContent(
                        page_number=page_num + 1,  # 1-indexed
                        text=text,
                        metadata=metadata
                    ))
                    
                    total_text_length += len(text)
                
                # Check if PDF contains any text
                if total_text_length == 0:
                    raise NoTextError("PDF contains no extractable text")
                
                return pages
                
        except (FileSizeError, NoTextError):
            raise
        except Exception as e:
            raise PDFParseError(f"PyPDF2 extraction failed: {str(e)}")
    
    def _contains_urdu(self, text: str) -> bool:
        """
        Check if text contains Urdu characters.
        
        Urdu uses Arabic script with Unicode range U+0600 to U+06FF.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains Urdu characters
        """
        if not text:
            return False
        
        # Check for Arabic/Urdu Unicode range
        for char in text:
            if '\u0600' <= char <= '\u06FF':
                return True
        return False
    
    def _contains_english(self, text: str) -> bool:
        """
        Check if text contains English characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains English characters
        """
        if not text:
            return False
        
        # Check for ASCII letters
        for char in text:
            if 'a' <= char.lower() <= 'z':
                return True
        return False
