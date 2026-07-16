"""Book metadata extraction and storage."""

import json
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class DescriptionQuote:
    text: str
    page: int


@dataclass
class BookMetadata:
    title: str
    author: str
    publication_year: Optional[str]
    description_quotes: List[Dict[str, any]]
    toc: List[str]


class BookMetadataExtractor:
    """Extract metadata from PDF."""
    
    def extract_metadata(self, pages: List, pdf_path: str) -> BookMetadata:
        """Extract book metadata from pages."""
        # Extract from first few pages
        first_pages = pages[:10] if len(pages) >= 10 else pages
        
        title = self._extract_title(first_pages, pdf_path)
        author = self._extract_author(first_pages)
        year = self._extract_year(first_pages)
        desc_quotes = self._extract_description_quotes(pages)
        toc = self._extract_toc(pages)
        
        return BookMetadata(
            title=title,
            author=author,
            publication_year=year,
            description_quotes=[{"text": q.text, "page": q.page} for q in desc_quotes],
            toc=toc
        )
    
    def _extract_title(self, first_pages, pdf_path: str) -> str:
        """Extract title from first pages or filename."""
        # Try to find title in first 3 pages
        for page in first_pages[:3]:
            lines = page.text.split('\n')
            for i, line in enumerate(lines[:15]):  # Check first 15 lines
                line = line.strip()
                # Look for substantial title-like text
                if 10 < len(line) < 200 and not line.startswith(('Copyright', '©', 'ISBN')):
                    # Check if it looks like a title (mostly capitalized words)
                    words = line.split()
                    if len(words) >= 2:
                        cap_words = sum(1 for w in words if w and w[0].isupper())
                        if cap_words / len(words) > 0.5:  # More than half capitalized
                            return line
        
        # Fallback to filename
        filename = os.path.basename(pdf_path)
        title = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        # Clean up common patterns
        title = re.sub(r'\s+', ' ', title).strip()
        return title
    
    def _extract_author(self, first_pages) -> str:
        """Extract author from first pages."""
        # Look for common author patterns in first 5 pages
        for page in first_pages[:5]:
            text = page.text
            
            # Pattern 1: "by AuthorName" or "By AuthorName"
            match = re.search(r'[Bb]y\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)+)', text)
            if match:
                author = match.group(1).strip()
                # Clean up extra spaces
                author = re.sub(r'\s+', ' ', author)
                return author
            
            # Pattern 2: "Author: Name" or "AUTHOR: Name"
            match = re.search(r'[Aa]uthor[:\s]+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+)+)', text)
            if match:
                author = match.group(1).strip()
                author = re.sub(r'\s+', ' ', author)
                return author
            
            # Pattern 3: Look for name-like patterns on early pages (2-3 capitalized words)
            lines = text.split('\n')
            for line in lines[:20]:
                line = line.strip()
                # Match 2-4 capitalized words (typical name format)
                match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]+){1,2})$', line)
                if match and 10 < len(line) < 50:
                    # Avoid common false positives
                    if not any(word in line.lower() for word in ['university', 'press', 'edition', 'chapter', 'contents']):
                        author = match.group(1).strip()
                        author = re.sub(r'\s+', ' ', author)
                        return author
        
        # If still not found, raise error to force manual check
        raise RuntimeError(
            "Could not extract author from PDF. Please manually set BookMetadata.author "
            "in the ingestion script."
        )
    
    def _extract_year(self, first_pages) -> Optional[str]:
        """Extract publication year."""
        for page in first_pages[:5]:
            # Look for copyright or publication year
            match = re.search(r'(19|20)\d{2}', page.text)
            if match:
                return match.group(0)
        return None
    
    def _extract_description_quotes(self, pages) -> List[DescriptionQuote]:
        """Extract description quotes from preface/intro."""
        quotes = []
        
        # Look in first 30 pages for intro/preface/first chapter
        for page in pages[:30]:
            text = page.text
            text_lower = text.lower()
            
            # Check if this is intro/preface/about section
            is_intro_page = any(keyword in text_lower for keyword in [
                'introduction', 'preface', 'foreword', 'about this book', 
                'this book', 'chapter 1', 'chapter one'
            ])
            
            if is_intro_page:
                # Split into paragraphs (double newline or single newline with indent)
                paragraphs = re.split(r'\n\s*\n|\n(?=[A-Z])', text)
                
                for para in paragraphs:
                    para = para.strip()
                    
                    # Keep substantial paragraphs
                    if 100 < len(para) < 800:
                        # Validate paragraph
                        if self._is_valid_description_paragraph(para):
                            # Clean up the paragraph
                            para = re.sub(r'\s+', ' ', para)  # Normalize whitespace
                            quotes.append(DescriptionQuote(text=para, page=page.page_number))
                            
                            if len(quotes) >= 3:
                                return quotes
        
        # Return what we found (may be empty)
        return quotes
    
    def _is_valid_description_paragraph(self, text: str) -> bool:
        """Check if paragraph is valid book description (not copyright/legal)."""
        text_lower = text.lower()
        
        # Forbidden phrases (copyright, legal, front-matter, dedications, acknowledgments)
        forbidden_phrases = [
            'all rights reserved',
            'no part of this book',
            'isbn',
            'library of congress',
            'printed in',
            'copyright',
            'may be reproduced',
            'without permission',
            'publisher',
            'cataloging-in-publication',
            'is dedicated to',
            'dedicated to',
            'acknowledgment',
            'acknowledgement',
            'would like to thank',
            'grateful to',
            'special thanks'
        ]
        
        # Check for forbidden content
        if any(phrase in text_lower for phrase in forbidden_phrases):
            return False
        
        # Required indicators (semantic book description)
        required_indicators = [
            'this book is grounded',
            'this book is an attempt',
            'this book examines',
            'this book explores',
            'this book discusses',
            'this book presents',
            'this book offers',
            'this book provides',
            'this book describes',
            'this book focuses',
            'in this book',
            'the purpose of this book',
            'this volume',
            'we explore',
            'we examine',
            'this text',
            'how would you'
        ]
        
        # Must contain at least one indicator
        return any(indicator in text_lower for indicator in required_indicators)
    
    def _extract_toc(self, pages) -> List[str]:
        """Extract table of contents."""
        toc = []
        
        # Look for TOC in first 30 pages
        for page in pages[:30]:
            text_lower = page.text.lower()
            
            if 'contents' in text_lower or 'table of contents' in text_lower:
                lines = page.text.split('\n')
                for line in lines:
                    line = line.strip()
                    # Chapter/section patterns
                    if re.match(r'^(chapter|section|\d+\.)\s+', line, re.IGNORECASE):
                        toc.append(line)
                
                if len(toc) > 0:
                    return toc[:20]  # Max 20 entries
        
        return toc


class BookMetadataStore:
    """Store and load book metadata."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.metadata_file = os.path.join(data_dir, "book_metadata.json")
    
    def save(self, metadata: BookMetadata):
        """Save metadata to file."""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)
    
    def load(self) -> Optional[BookMetadata]:
        """Load metadata from file."""
        if not os.path.exists(self.metadata_file):
            return None
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return BookMetadata(**data)
