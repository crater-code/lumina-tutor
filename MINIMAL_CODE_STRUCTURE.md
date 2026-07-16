# Minimal Code Structure After Refactoring

## Overview

This document shows the complete file structure and key code snippets for the refactored minimal bounded chatbot system.

---

## File Structure

```
book-bounded-tutor/
├── data/                           # Simple file-based storage
│   ├── current_book.pdf           # Currently loaded book
│   ├── chunks.json                # Structural chunks
│   └── vector_store/              # FAISS index
│       └── faiss.index
│
├── src/                           # Core application code
│   ├── __init__.py
│   ├── main.py                    # FastAPI application (200 LOC)
│   ├── models.py                  # Simple dataclasses (150 LOC)
│   ├── exceptions.py              # Custom exceptions (50 LOC)
│   │
│   ├── pdf_parser.py              # PDF parsing + structure (300 LOC)
│   ├── structural_chunking_engine.py  # Structural chunking (250 LOC)
│   ├── embedding_generator.py     # Embeddings (100 LOC) [unchanged]
│   ├── vector_store.py            # FAISS storage (150 LOC) [unchanged]
│   │
│   ├── hybrid_retrieval_system.py # Hybrid retrieval (300 LOC)
│   ├── bounded_chatbot_engine.py  # Template-based generation (500 LOC)
│   └── strict_grounding_validator.py  # Quote validation (200 LOC)
│
├── tests/                         # Minimal unit tests
│   ├── __init__.py
│   ├── test_pdf_parser.py         # 50 LOC
│   ├── test_structural_chunking.py # 80 LOC
│   ├── test_hybrid_retrieval.py   # 80 LOC
│   ├── test_bounded_chatbot.py    # 100 LOC
│   ├── test_strict_validation.py  # 50 LOC
│   └── test_integration.py        # 40 LOC
│
├── frontend/                      # React frontend (simplified)
│   ├── src/
│   │   ├── App.jsx                # Main app (200 LOC)
│   │   ├── main.jsx               # Entry point (20 LOC)
│   │   ├── App.css                # Styles
│   │   └── index.css              # Global styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── demo_*.py                      # Demo scripts (updated)
├── requirements.txt               # Simplified dependencies
├── README.md                      # Updated documentation
└── .env.example                   # Environment variables

Total Core Code: ~2,300 LOC (down from 4,200)
Total Test Code: ~400 LOC (down from 2,000)
```

---

## Core Components

### 1. Models (`src/models.py`)

```python
"""
Data models for the bounded chatbot system.
Simple dataclasses only - no ORM complexity.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class PageContent:
    """Content from a single PDF page."""
    page_number: int
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Heading:
    """A heading in the document structure."""
    level: int  # 1=chapter, 2=section, 3=subsecti