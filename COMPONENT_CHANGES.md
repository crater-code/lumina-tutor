# Component-by-Component Change Analysis

## Overview

This document provides a detailed breakdown of what changes, what stays, and what gets removed in the refactoring to align with the bounded chatbot goals.

## Components Summary

| Component | Status | Action | Reason |
|-----------|--------|--------|--------|
| PDF Parser | ✓ KEEP | Add structure extraction | Core functionality needed |
| Chunking Engine | ⚠️ REFACTOR | Replace with structural chunking | Need document structure awareness |
| Embedding Generator | ✓ KEEP | No changes | Still needed for ranking |
| Vector Store | ✓ KEEP | No changes | Still needed for similarity search |
| Retrieval System | ⚠️ REFACTOR | Add hybrid approach | Need structural + semantic |
| Chatbot Engine | ⚠️ REFACTOR | Replace with template-based | Too permissive currently |
| Response Validator | ⚠️ REFACTOR | Strengthen validation | Not strict enough |
| Database | ✗ REMOVE | Replace with file storage | Over-engineered for demo |
| Book Ingestion Pipeline | ⚠️ SIMPLIFY | Single-book version | Multi-book not needed |
| Property-based Tests | ✗ REMOVE | Keep only unit tests | Over-engineered for MVP |

---

## Detailed Component Analysis

### 1. PDF Parser (`src/pdf_parser.py`)

**Status:** ✓ KEEP with enhancements

**Current Functionality:**
- Extracts text from PDF files
- Handles page numbers
- Supports English and Urdu text
- Validates file size (450 pages max)

**Changes Needed:**
```python
# ADD: Structure extraction
class PDFParser:
    def extract_text_with_structure(self, pdf_path: str) -> StructuredDocument:
        """
        Extract text AND structure (headings, paragraphs, sections).
        
        Returns:
            StructuredDocument with:
            - pages: List[PageContent]
            - structure: DocumentStructure (chapters, sections, paragraphs)
        """
        pass
    
    def _detect_headings(self, page: PageContent) -> List[Heading]:
        """Detect headings based on font size, bold, etc."""
        pass
    
    def _extract_paragraphs(self, page: PageContent) -> List[Paragraph]:
        """Extract paragraph boundaries."""
        pass
```

**Why Keep:**
- Core functionality is solid
- Text extraction works well
- Just needs structure awareness added

**Estimated Changes:** 20% new code, 80% unchanged

---

### 2. Chunking Engine (`src/chunking_engine.py`)

**Status:** ⚠️ MAJOR REFACTOR

**Current Approach:**
- Fixed-size chunks (500 chars)
- Sentence boundary detection
- No structural awareness
- Pure character-based positioning

**Problems:**
- Chunks can split across sections/topics
- No awareness of document hierarchy
- Loses semantic context
- Hard to trace back to source

**New Approach: Structural Chunking**

```python
class StructuralChunkingEngine:
    """
    Creates chunks that respect document structure.
    
    Strategy:
    1. Use document structure as primary chunking guide
    2. Create chunks at paragraph/section level
    3. Preserve hierarchy (chapter → section → paragraph)
    4. Include structural metadata for better grounding
    """
    
    def create_chunks(
        self,
        structured_doc: StructuredDocument,
        book_id: str = "default"
    ) -> List[StructuralChunk]:
        """
        Create chunks respecting document structure.
        
        Chunking rules:
        - Prefer paragraph-level chunks
        - Keep section context in metadata
        - Include chapter/section headings
        - Maintain hierarchy information
        """
        chunks = []
        
        for chapter in structured_doc.chapters:
            for section in chapter.sections:
                for paragraph in section.paragraphs:
                    chunk = StructuralChunk(
                        chunk_id=f"book_{book_id}_ch{chapter.num}_sec{section.num}_p{paragraph.num}",
                        text=paragraph.text,
                        page_numbers=paragraph.page_numbers,
                        hierarchy={
                            "chapter": chapter.title,
                            "chapter_num": chapter.num,
                            "section": section.title,
                            "section_num": section.num,
                            "paragraph_num": paragraph.num
                        },
                        context={
                            "preceding_heading": section.title,
                            "chapter_context": chapter.title
                        }
                    )
                    chunks.append(chunk)
        
        return chunks
```

**Key Differences:**

| Aspect | Old | New |
|--------|-----|-----|
| Chunking basis | Character count | Document structure |
| Boundaries | Sentence | Paragraph/Section |
| Metadata | Page numbers only | Full hierarchy |
| Context | None | Chapter/section context |
| Traceability | Character positions | Structural path |

**Why Change:**
- Better grounding in source material
- Easier to verify responses
- Preserves semantic coherence
- Enables structural retrieval

**Estimated Changes:** 70% rewrite, 30% reusable

---

### 3. Embedding Generator (`src/embedding_generator.py`)

**Status:** ✓ KEEP unchanged

**Current Functionality:**
- Generates embeddings using sentence-transformers
- Supports multilingual models
- Batch processing
- Works well for both English and Urdu

**Why Keep:**
- Still needed for semantic ranking
- Works well as-is
- No changes needed

**Role Change:**
- **Old role:** Primary retrieval mechanism
- **New role:** Secondary ranking mechanism (after structural retrieval)

**Estimated Changes:** 0% (no changes)

---

### 4. Vector Store (`src/vector_store.py`)

**Status:** ✓ KEEP unchanged

**Current Functionality:**
- Stores chunk embeddings
- Performs similarity search
- Uses FAISS for efficient search
- Supports book-specific searches

**Why Keep:**
- Still needed for semantic ranking
- FAISS is efficient and works well
- No changes needed

**Role Change:**
- **Old role:** Primary retrieval mechanism
- **New role:** Secondary ranking after structural filtering

**Estimated Changes:** 0% (no changes)

---

### 5. Retrieval System (`src/retrieval_system.py`)

**Status:** ⚠️ MAJOR REFACTOR

**Current Approach:**
- Pure embedding-based retrieval
- Similarity search only
- No structural awareness
- No textual overlap check

**Problems:**
- Can retrieve semantically similar but contextually wrong chunks
- No grounding in actual query terms
- Allows "semantic guessing"

**New Approach: Hybrid Retrieval**

```python
class HybridRetrievalSystem:
    """
    Hybrid retrieval combining structural and semantic approaches.
    
    Three-stage retrieval:
    1. Structural filtering (keyword + hierarchy)
    2. Semantic ranking (embeddings)
    3. Textual overlap validation
    """
    
    def retrieve_chunks(
        self,
        book_id: str,
        query: str,
        top_k: int = 5
    ) -> List[StructuralChunk]:
        """
        Retrieve chunks using hybrid approach.
        
        Process:
        1. Extract query keywords
        2. Filter chunks with keyword overlap (structural)
        3. Rank filtered chunks by embedding similarity (semantic)
        4. Validate textual overlap
        5. Return top-k chunks or refuse if no overlap
        """
        # Stage 1: Structural filtering
        query_keywords = self._extract_keywords(query)
        structural_candidates = self._filter_by_keywords(
            book_id, query_keywords, min_overlap=0.3
        )
        
        if not structural_candidates:
            return []  # No textual overlap → refuse
        
        # Stage 2: Semantic ranking
        query_embedding = self.embedding_generator.generate_embedding(query)
        ranked_chunks = self._rank_by_similarity(
            structural_candidates, query_embedding
        )
        
        # Stage 3: Textual overlap validation
        validated_chunks = self._validate_textual_overlap(
            query, ranked_chunks, min_overlap=0.2
        )
        
        return validated_chunks[:top_k]
    
    def _filter_by_keywords(
        self,
        book_id: str,
        keywords: Set[str],
        min_overlap: float
    ) -> List[StructuralChunk]:
        """Filter chunks that contain query keywords."""
        pass
    
    def _validate_textual_overlap(
        self,
        query: str,
        chunks: List[StructuralChunk],
        min_overlap: float
    ) -> List[StructuralChunk]:
        """Ensure chunks have actual textual overlap with query."""
        pass
```

**Key Differences:**

| Aspect | Old | New |
|--------|-----|-----|
| Retrieval method | Pure semantic | Hybrid (structural + semantic) |
| Filtering | Similarity threshold | Keyword overlap required |
| Ranking | Embedding similarity | Embedding similarity (after filtering) |
| Validation | None | Textual overlap check |
| Refusal logic | Low similarity | No keyword overlap |

**Why Change:**
- Prevents semantic guessing
- Requires actual textual connection
- Better grounding in source
- More inspectable and debuggable

**Estimated Changes:** 60% rewrite, 40% reusable

---

### 6. Chatbot Engine (`src/chatbot_engine.py`)

**Status:** ⚠️ MAJOR REFACTOR

**Current Approach:**
- Free-form LLM generation
- Prompt engineering for boundaries
- Age-adaptive language
- Weak grounding constraints

**Problems:**
- LLM can paraphrase too freely
- Allows semantic drift from source
- Hard to verify responses
- Can add implicit knowledge

**New Approach: Template-Based Assembly**

```python
class BoundedChatbotEngine:
    """
    Generates responses using template-based assembly from chunks.
    
    Response types:
    1. Direct quote with citation
    2. Light rephrasing (preserving exact meaning)
    3. Pedagogical templates (definition, example, question-back)
    
    NO free-form generation, NO new examples, NO external facts.
    """
    
    # Pedagogical templates
    TEMPLATES = {
        "definition": {
            "en": "According to the book (page {pages}): \"{quote}\"",
            "ur": "کتاب کے مطابق (صفحہ {pages}): \"{quote}\""
        },
        "example": {
            "en": "The book provides this example (page {pages}): \"{quote}\"",
            "ur": "کتاب یہ مثال دیتی ہے (صفحہ {pages}): \"{quote}\""
        },
        "explanation": {
            "en": "The book explains (page {pages}): \"{quote}\"",
            "ur": "کتاب وضاحت کرتی ہے (صفحہ {pages}): \"{quote}\""
        },
        "question_back": {
            "en": "The book doesn't directly answer that, but it mentions (page {pages}): \"{quote}\"",
            "ur": "کتاب براہ راست جواب نہیں دیتی، لیکن یہ ذکر کرتی ہے (صفحہ {pages}): \"{quote}\""
        }
    }
    
    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[StructuralChunk],
        user_age: int,
        language: str = "en"
    ) -> Response:
        """
        Generate bounded response using templates.
        
        Process:
        1. Analyze query to determine response type
        2. Extract relevant quotes from chunks
        3. Select appropriate template
        4. Assemble response with explicit citations
        5. Apply age-appropriate simplification (if needed)
        """
        # Determine response type
        response_type = self._classify_query(query)
        
        # Extract quotes
        quotes = self._extract_relevant_quotes(query, retrieved_chunks)
        
        if not quotes:
            return self.generate_refusal(query, user_age, language)
        
        # Select template
        template = self.TEMPLATES[response_type][language]
        
        # Assemble response
        response_text = self._assemble_from_template(
            template, quotes, user_age, language
        )
        
        return Response(
            text=response_text,
            chunk_ids=[chunk.chunk_id for chunk in retrieved_chunks],
            is_refusal=False,
            metadata={
                "response_type": response_type,
                "num_quotes": len(quotes),
                "age_group": self._get_age_group(user_age),
                "language": language
            }
        )
    
    def _classify_query(self, query: str) -> str:
        """
        Classify query to determine response type.
        
        Types:
        - "definition": What is X? Define X.
        - "example": Give an example. Show me how.
        - "explanation": Why? How? Explain.
        - "question_back": Unclear or indirect questions
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["what is", "define", "meaning of"]):
            return "definition"
        elif any(word in query_lower for word in ["example", "show", "demonstrate"]):
            return "example"
        elif any(word in query_lower for word in ["why", "how", "explain"]):
            return "explanation"
        else:
            return "question_back"
    
    def _extract_relevant_quotes(
        self,
        query: str,
        chunks: List[StructuralChunk]
    ) -> List[Quote]:
        """
        Extract relevant quotes from chunks.
        
        Rules:
        - Prefer sentences containing query keywords
        - Keep quotes short (1-3 sentences)
        - Preserve exact wording
        - Include page numbers
        """
        quotes = []
        query_keywords = set(query.lower().split())
        
        for chunk in chunks:
            sentences = self._split_into_sentences(chunk.text)
            for sentence in sentences:
                # Check if sentence contains query keywords
                sentence_words = set(sentence.lower().split())
                overlap = query_keywords.intersection(sentence_words)
                
                if len(overlap) >= 2:  # At least 2 keyword matches
                    quotes.append(Quote(
                        text=sentence,
                        chunk_id=chunk.chunk_id,
                        pages=chunk.page_numbers,
                        context=chunk.hierarchy
                    ))
        
        return quotes
    
    def _assemble_from_template(
        self,
        template: str,
        quotes: List[Quote],
        age: int,
        language: str
    ) -> str:
        """
        Assemble response from template and quotes.
        
        Process:
        1. Select best quote(s)
        2. Apply age-appropriate simplification if needed
        3. Fill template
        4. Add citations
        """
        # Select best quote (first one for now)
        quote = quotes[0]
        
        # Simplify if needed for young children
        quote_text = self._simplify_for_age(quote.text, age, language)
        
        # Format pages
        pages_str = ", ".join(str(p) for p in quote.pages)
        
        # Fill template
        response = template.format(
            quote=quote_text,
            pages=pages_str
        )
        
        return response
    
    def _simplify_for_age(self, text: str, age: int, language: str) -> str:
        """
        Simplify text for younger children if needed.
        
        Rules:
        - Ages 4-7: Break long sentences, simplify vocabulary
        - Ages 8-11: Minor simplification
        - Ages 12-15: No simplification
        
        IMPORTANT: Preserve meaning exactly, only simplify structure
        """
        if age >= 12:
            return text  # No simplification
        
        if age >= 8:
            # Minor simplification: break very long sentences
            if len(text.split()) > 30:
                # Split at commas or semicolons
                text = text.replace(", ", ". ").replace("; ", ". ")
            return text
        
        # Ages 4-7: More aggressive simplification
        # Break long sentences, simplify structure
        # But PRESERVE exact meaning
        sentences = text.split(".")
        simplified = []
        for sentence in sentences:
            if len(sentence.split()) > 15:
                # Break at "and", "but", "because"
                parts = sentence.replace(" and ", ". ").replace(" but ", ". ").replace(" because ", ". ")
                simplified.append(parts)
            else:
                simplified.append(sentence)
        
        return ". ".join(simplified)
```

**Key Differences:**

| Aspect | Old | New |
|--------|-----|-----|
| Generation method | Free-form LLM | Template-based assembly |
| Content source | LLM paraphrasing | Direct quotes |
| Flexibility | High (too high) | Low (intentionally restricted) |
| Verifiability | Hard | Easy (quotes are exact) |
| Hallucination risk | Medium | Very low |
| Age adaptation | Prompt engineering | Text simplification |

**Why Change:**
- Eliminates semantic drift
- Makes responses verifiable
- Reduces hallucination risk to near-zero
- More aligned with "bounded" goal

**Estimated Changes:** 80% rewrite, 20% reusable

---

### 7. Response Validator (`src/response_validator.py`)

**Status:** ⚠️ REFACTOR

**Current Approach:**
- Heuristic-based validation
- Keyword matching
- Sentence similarity
- Named entity checking

**Problems:**
- Thresholds are arbitrary
- Can miss subtle hallucinations
- Allows too much paraphrasing

**New Approach: Strict Quote Validation**

```python
class StrictGroundingValidator:
    """
    Validates that responses contain only direct quotes or minimal rephrasing.
    
    Validation rules:
    1. All factual content must be direct quotes
    2. Rephrasing must preserve exact meaning
    3. No new information added
    4. Citations must be accurate
    """
    
    def validate_response(
        self,
        response: Response,
        retrieved_chunks: List[StructuralChunk]
    ) -> ValidationResult:
        """
        Validate response against strict grounding rules.
        
        Checks:
        1. Response contains quotes from chunks
        2. Quotes are exact or minimally paraphrased
        3. No new information added
        4. Citations are accurate
        """
        issues = []
        
        # Check 1: Extract quotes from response
        quotes = self._extract_quotes_from_response(response.text)
        
        if not quotes:
            issues.append("Response contains no direct quotes")
        
        # Check 2: Verify quotes exist in chunks
        for quote in quotes:
            if not self._verify_quote_in_chunks(quote, retrieved_chunks):
                issues.append(f"Quote not found in chunks: '{quote[:50]}...'")
        
        # Check 3: Check for added information
        non_quote_text = self._extract_non_quote_text(response.text)
        if self._contains_factual_claims(non_quote_text):
            issues.append("Response contains factual claims outside quotes")
        
        # Check 4: Verify citations
        for chunk_id in response.chunk_ids:
            if not self._chunk_id_exists(chunk_id, retrieved_chunks):
                issues.append(f"Invalid chunk citation: {chunk_id}")
        
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=1.0 if is_valid else 0.0,
            issues=issues
        )
    
    def _verify_quote_in_chunks(
        self,
        quote: str,
        chunks: List[StructuralChunk]
    ) -> bool:
        """
        Verify that a quote exists in the chunks.
        
        Allows for:
        - Exact matches
        - Minor punctuation differences
        - Whitespace differences
        
        Does NOT allow:
        - Word changes
        - Meaning changes
        - Added/removed content
        """
        quote_normalized = self._normalize_text(quote)
        
        for chunk in chunks:
            chunk_normalized = self._normalize_text(chunk.text)
            if quote_normalized in chunk_normalized:
                return True
        
        return False
    
    def _contains_factual_claims(self, text: str) -> bool:
        """
        Check if text contains factual claims.
        
        Allowed non-quote text:
        - "According to the book"
        - "The book explains"
        - "On page X"
        - Age-appropriate simplifications
        
        Not allowed:
        - New facts
        - External examples
        - Interpretations
        """
        # Remove template phrases
        template_phrases = [
            "according to the book",
            "the book explains",
            "the book provides",
            "on page",
            "page"
        ]
        
        text_lower = text.lower()
        for phrase in template_phrases:
            text_lower = text_lower.replace(phrase, "")
        
        # Check if remaining text has factual content
        # (nouns, verbs, specific claims)
        words = text_lower.split()
        
        # If only connector words remain, it's OK
        connector_words = {"this", "that", "it", "is", "are", "was", "were", "the", "a", "an"}
        content_words = [w for w in words if w not in connector_words]
        
        return len(content_words) > 3  # Threshold for factual content
```

**Key Differences:**

| Aspect | Old | New |
|--------|-----|-----|
| Validation method | Heuristic similarity | Exact quote matching |
| Paraphrasing allowed | Yes (with thresholds) | Minimal only |
| New information | Detected heuristically | Strictly forbidden |
| Validation strictness | Medium | Very high |

**Why Change:**
- Aligns with template-based generation
- Easier to verify (exact quotes)
- Eliminates ambiguity
- Stronger guarantees

**Estimated Changes:** 60% rewrite, 40% reusable

---

### 8. Database (`src/database.py`)

**Status:** ✗ REMOVE

**Current Functionality:**
- SQLAlchemy ORM
- Multi-book management
- Chat session tracking
- Complex schema

**Why Remove:**
- Over-engineered for single-book demo
- Adds complexity without value
- File-based storage is simpler

**Replacement:**

```python
# Simple file-based storage
class SimpleStorage:
    """
    Simple file-based storage for single-book demo.
    
    Storage structure:
    data/
    ├── current_book.pdf
    ├── chunks.json
    └── vector_store/
        └── faiss.index
    """
    
    def save_chunks(self, chunks: List[StructuralChunk]):
        """Save chunks to JSON file."""
        with open("data/chunks.json", "w") as f:
            json.dump([chunk.to_dict() for chunk in chunks], f)
    
    def load_chunks(self) -> List[StructuralChunk]:
        """Load chunks from JSON file."""
        with open("data/chunks.json", "r") as f:
            data = json.load(f)
            return [StructuralChunk.from_dict(d) for d in data]
```

**Estimated Changes:** 100% removal, replace with 50 lines of simple code

---

### 9. Book Ingestion Pipeline (`src/book_ingestion_pipeline.py`)

**Status:** ⚠️ SIMPLIFY

**Current Functionality:**
- Multi-book orchestration
- Database integration
- Complex state management

**Why Simplify:**
- Single-book demo doesn't need orchestration
- Can be a simple function

**Replacement:**

```python
def ingest_book(pdf_path: str) -> None:
    """
    Simple book ingestion for single-book demo.
    
    Steps:
    1. Parse PDF with structure extraction
    2. Create structural chunks
    3. Generate embeddings
    4. Store in vector store
    5. Save chunks to JSON
    """
    # Parse PDF
    parser = PDFParser()
    structured_doc = parser.extract_text_with_structure(pdf_path)
    
    # Create chunks
    chunker = StructuralChunkingEngine()
    chunks = chunker.create_chunks(structured_doc)
    
    # Generate embeddings
    embedder = EmbeddingGenerator()
    embeddings = embedder.generate_batch_embeddings([c.text for c in chunks])
    
    # Store in vector store
    vector_store = VectorStore()
    vector_store.add_chunks("current_book", chunks, embeddings)
    
    # Save chunks
    storage = SimpleStorage()
    storage.save_chunks(chunks)
    
    print(f"Ingested book: {len(chunks)} chunks created")
```

**Estimated Changes:** 90% simplification, 10% reusable

---

### 10. Property-Based Tests

**Status:** ✗ REMOVE

**Current Functionality:**
- Hypothesis-based property tests
- 100+ iterations per test
- Complex test generation

**Why Remove:**
- Over-engineered for MVP
- Adds complexity
- Hard to debug
- Not needed for inspectable system

**Replacement:**
- Keep only essential unit tests
- Focus on core functionality
- Use simple, readable test cases

**Example:**

```python
# OLD: Property-based test
@given(st.lists(st.text(min_size=100, max_size=1000), min_size=5, max_size=50))
def test_chunk_id_uniqueness(texts):
    """Property: All chunk IDs must be unique."""
    chunking_engine = ChunkingEngine()
    pages = [PageContent(i, text, {}) for i, text in enumerate(texts)]
    chunks = chunking_engine.create_chunks(pages)
    chunk_ids = [chunk.chunk_id for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))

# NEW: Simple unit test
def test_chunk_id_uniqueness():
    """Test that chunk IDs are unique."""
    chunker = StructuralChunkingEngine()
    doc = create_test_document()  # Simple fixture
    chunks = chunker.create_chunks(doc)
    chunk_ids = [chunk.chunk_id for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))
```

**Estimated Changes:** 100% removal of property tests, keep 20% as simple unit tests

---

## Summary of Changes

### Code Volume Changes

| Component | Current LOC | New LOC | Change |
|-----------|-------------|---------|--------|
| PDF Parser | 200 | 300 | +50% (structure extraction) |
| Chunking Engine | 300 | 250 | -17% (simpler logic) |
| Embedding Generator | 100 | 100 | 0% (unchanged) |
| Vector Store | 150 | 150 | 0% (unchanged) |
| Retrieval System | 150 | 300 | +100% (hybrid approach) |
| Chatbot Engine | 400 | 500 | +25% (templates) |
| Response Validator | 300 | 200 | -33% (simpler validation) |
| Database | 400 | 50 | -88% (file-based) |
| Book Ingestion | 200 | 50 | -75% (simplified) |
| Tests | 2000 | 400 | -80% (remove property tests) |
| **TOTAL** | **4200** | **2300** | **-45%** |

### Complexity Changes

| Aspect | Before | After | Change |
|--------|--------|-------|--------|
| Total files | 30+ | 15 | -50% |
| Dependencies | 15+ | 8 | -47% |
| Test complexity | High (property-based) | Low (unit tests) | -70% |
| Database complexity | High (ORM) | Low (JSON files) | -90% |
| Response generation | Medium (LLM) | Low (templates) | -60% |
| **Overall Complexity** | **High** | **Low** | **-65%** |

---

## Migration Path

### Step 1: Remove Over-Engineering
- Remove property-based tests
- Remove database ORM
- Simplify book ingestion

### Step 2: Add Structure
- Enhance PDF parser
- Implement structural chunking
- Update data models

### Step 3: Implement Hybrid Retrieval
- Add keyword filtering
- Add textual overlap validation
- Update retrieval system

### Step 4: Implement Template-Based Generation
- Define templates
- Implement quote extraction
- Update chatbot engine

### Step 5: Strengthen Validation
- Implement quote verification
- Update validation rules
- Test end-to-end

---

## Conclusion

The refactoring will:
- **Reduce code by 45%** (4200 → 2300 LOC)
- **Reduce complexity by 65%**
- **Improve inspectability** (simpler, more transparent)
- **Strengthen boundedness** (stricter grounding)
- **Maintain core functionality** (PDF → Chunks → Chat)

The result will be a minimal, inspectable, bounded chatbot that strictly operates within book content boundaries.
