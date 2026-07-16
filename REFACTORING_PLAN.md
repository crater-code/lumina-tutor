# Refactoring Plan: Aligning with Bounded Chatbot Goals

## Executive Summary

This document outlines the refactoring needed to align the current implementation with the original goal of a **minimal, inspectable, bounded chatbot** that strictly operates within book content boundaries.

## Current State Analysis

### What's Over-Engineered

1. **Testing Infrastructure**
   - Property-based testing with Hypothesis (100+ iterations per test)
   - Extensive test coverage across 20+ test files
   - Complex integration tests
   - **Issue**: Adds complexity without immediate value for MVP

2. **Database Schema**
   - Multi-book management with sessions
   - Chat history tracking
   - Complex book metadata
   - **Issue**: Over-designed for single-book demo use case

3. **Chunking Strategy**
   - Pure embedding-based semantic search
   - No structural awareness (chapters, sections)
   - **Issue**: Doesn't leverage document structure for better grounding

4. **Response Generation**
   - Allows free-form LLM explanations
   - Weak grounding constraints
   - **Issue**: Too permissive, allows semantic drift from source

5. **Validation Layer**
   - Heuristic-based hallucination detection
   - Keyword matching with thresholds
   - **Issue**: Not strict enough, allows paraphrasing that loses grounding

## Refactoring Goals

### 1. Reduce Over-Engineering

**Actions:**
- Remove property-based tests (keep only unit and integration tests)
- Simplify test suite to focus on core functionality
- Remove hypothesis dependency
- Keep test coverage minimal but meaningful

**Rationale:** MVP should be inspectable and debuggable, not exhaustively tested

### 2. Change Chunking Strategy

**Current:** Fixed-size chunks with sentence boundaries
**New:** Structural + semantic hybrid

**Actions:**
- Extract document structure (chapters, sections, paragraphs)
- Create chunks that respect structural boundaries
- Use embeddings ONLY for ranking within structural candidates
- Require textual overlap between query and chunks

**Implementation:**
```python
class StructuralChunkingEngine:
    def create_chunks(self, pages: List[PageContent]) -> List[Chunk]:
        # 1. Extract structure (headings, paragraphs)
        # 2. Create chunks at paragraph/section level
        # 3. Preserve hierarchy metadata
        # 4. Ensure chunks have clear structural context
```

**Rationale:** Structural chunking provides better grounding and traceability

### 3. Restrict Response Generation

**Current:** LLM generates free-form explanations
**New:** Template-based assembly from chunks

**Actions:**
- Define pedagogical templates:
  - **Definition**: "According to the book, [term] means [direct quote]"
  - **Example**: "The book gives this example: [direct quote]"
  - **Question-back**: "The book doesn't directly answer that, but it says: [related quote]"
- Responses must be:
  - Direct quotes (with citation)
  - Light rephrasing (preserving exact meaning)
  - Template-based assembly
- NO new examples, metaphors, or external facts

**Implementation:**
```python
class BoundedChatbotEngine:
    TEMPLATES = {
        "definition": "According to the book, {term} means: {quote}",
        "example": "The book provides this example: {quote}",
        "explanation": "The book explains: {quote}",
        "question_back": "The book doesn't directly answer that, but it mentions: {quote}"
    }
    
    def generate_response(self, query, chunks):
        # 1. Select appropriate template
        # 2. Extract relevant quotes from chunks
        # 3. Assemble response using template
        # 4. Include explicit citations
```

**Rationale:** Eliminates semantic drift and hallucination risk

### 4. Strengthen Boundedness

**Current:** Heuristic validation after generation
**New:** Strict grounding before generation

**Actions:**
- Require textual overlap between query and chunks
- If no direct overlap, refuse immediately
- No semantic guessing or inference
- Validation checks for exact quote preservation

**Implementation:**
```python
class StrictGroundingValidator:
    def check_textual_overlap(self, query: str, chunks: List[Chunk]) -> bool:
        # Check if query keywords appear in chunks
        # Require minimum overlap threshold
        # Return False if no direct connection
    
    def validate_quote_preservation(self, response: str, chunks: List[Chunk]) -> bool:
        # Verify quotes are exact or minimally paraphrased
        # Check that no new information was added
```

**Rationale:** Prevents the system from "guessing" answers

### 5. Simplify System Architecture

**Current:** Multi-book system with complex DB schema
**New:** Single-book demo with minimal storage

**Actions:**
- Remove multi-book management
- Remove chat session tracking
- Simplify to: PDF → Chunks → Vector Store → Chat
- Use simple file-based storage for demo

**Rationale:** Focus on core functionality, not infrastructure

## Component Changes

### Components to KEEP (with modifications)

1. **PDF Parser** ✓
   - Keep as-is
   - Already handles text extraction well

2. **Embedding Generator** ✓
   - Keep for ranking chunks
   - Use ONLY for ranking, not primary retrieval

3. **Vector Store** ✓
   - Keep for similarity search
   - Use as secondary filter after structural retrieval

4. **Web Interface** ✓
   - Keep basic chat UI
   - Simplify to single-book mode

### Components to REFACTOR

1. **Chunking Engine** → **StructuralChunkingEngine**
   - Add structure extraction
   - Preserve document hierarchy
   - Create larger, more meaningful chunks

2. **Retrieval System** → **HybridRetrievalSystem**
   - First: Structural retrieval (keyword + structure)
   - Second: Semantic ranking (embeddings)
   - Third: Textual overlap validation

3. **Chatbot Engine** → **BoundedChatbotEngine**
   - Remove free-form generation
   - Add template-based assembly
   - Enforce quote-based responses

4. **Response Validator** → **StrictGroundingValidator**
   - Strengthen validation rules
   - Check quote preservation
   - Verify no new information added

### Components to REMOVE

1. **Book Ingestion Pipeline** (complex multi-book version)
   - Replace with simple single-book processor

2. **Database** (SQLAlchemy with complex schema)
   - Replace with simple file-based storage

3. **Models** (complex ORM models)
   - Replace with simple dataclasses

4. **Property-based tests**
   - Remove hypothesis tests
   - Keep only essential unit tests

## New Minimal Architecture

```
┌─────────────────┐
│  Web Interface  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     Simple API Layer (FastAPI)      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Single-Book Processing Pipeline    │
│  - PDF Parser                       │
│  - Structural Chunking Engine       │
│  - Embedding Generator              │
│  - Vector Store (FAISS)             │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Hybrid Retrieval System            │
│  1. Structural retrieval            │
│  2. Semantic ranking                │
│  3. Textual overlap check           │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Bounded Chatbot Engine             │
│  - Template-based assembly          │
│  - Quote extraction                 │
│  - Citation generation              │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Strict Grounding Validator         │
│  - Quote preservation check         │
│  - No new information check         │
│  - Textual overlap verification     │
└─────────────────────────────────────┘
```

## Implementation Strategy

### Phase 1: Simplification (Remove Over-Engineering)

1. Remove property-based tests
2. Remove hypothesis dependency
3. Simplify database to file-based storage
4. Remove multi-book management code
5. Remove complex ORM models

**Files to modify:**
- `requirements.txt` - remove hypothesis
- `tests/*` - remove property tests
- `src/database.py` - simplify or remove
- `src/models.py` - keep only dataclasses
- `src/book_ingestion_pipeline.py` - simplify

### Phase 2: Structural Chunking

1. Implement structure extraction from PDF
2. Create StructuralChunkingEngine
3. Add hierarchy metadata to chunks
4. Update chunk storage to include structure

**Files to create/modify:**
- `src/structural_chunking_engine.py` - new
- `src/pdf_parser.py` - add structure extraction
- `src/models.py` - add structure metadata

### Phase 3: Hybrid Retrieval

1. Implement keyword-based structural retrieval
2. Add semantic ranking layer
3. Add textual overlap validation
4. Update retrieval system

**Files to create/modify:**
- `src/hybrid_retrieval_system.py` - new
- `src/retrieval_system.py` - refactor or replace

### Phase 4: Bounded Response Generation

1. Define pedagogical templates
2. Implement quote extraction
3. Implement template-based assembly
4. Remove free-form LLM generation

**Files to create/modify:**
- `src/bounded_chatbot_engine.py` - new
- `src/chatbot_engine.py` - refactor or replace

### Phase 5: Strict Validation

1. Implement quote preservation check
2. Implement textual overlap verification
3. Strengthen refusal logic
4. Update validation system

**Files to create/modify:**
- `src/strict_grounding_validator.py` - new
- `src/response_validator.py` - refactor or replace

### Phase 6: Integration and Testing

1. Update API endpoints
2. Update web interface
3. Create minimal test suite
4. Test end-to-end flow

**Files to modify:**
- `src/main.py` - update API
- `frontend/src/App.jsx` - update UI
- `tests/*` - create minimal tests

## File Structure After Refactoring

```
src/
├── __init__.py
├── main.py                          # Simplified API
├── models.py                        # Simple dataclasses only
├── pdf_parser.py                    # + structure extraction
├── structural_chunking_engine.py    # NEW: structural chunking
├── embedding_generator.py           # Keep as-is
├── vector_store.py                  # Keep as-is
├── hybrid_retrieval_system.py       # NEW: hybrid retrieval
├── bounded_chatbot_engine.py        # NEW: template-based
├── strict_grounding_validator.py    # NEW: strict validation
└── exceptions.py                    # Keep as-is

tests/
├── __init__.py
├── test_pdf_parser.py              # Minimal unit tests
├── test_structural_chunking.py     # Minimal unit tests
├── test_hybrid_retrieval.py        # Minimal unit tests
├── test_bounded_chatbot.py         # Minimal unit tests
├── test_strict_validation.py       # Minimal unit tests
└── test_integration.py             # End-to-end test

data/
├── current_book.pdf                # Single book
├── chunks.json                     # Simple JSON storage
└── vector_store/                   # FAISS index

frontend/                           # Keep as-is, simplify
demo_*.py                          # Update demos
```

## Success Criteria

After refactoring, the system should:

1. ✓ Be minimal and inspectable (< 2000 lines of core code)
2. ✓ Use structural chunking with semantic ranking
3. ✓ Generate responses only from direct quotes or light rephrasing
4. ✓ Refuse when no textual overlap exists
5. ✓ Have no property-based tests (only essential unit tests)
6. ✓ Support single-book demo mode
7. ✓ Be easy to understand and debug
8. ✓ Maintain strict content boundaries

## Timeline Estimate

- Phase 1 (Simplification): 2-3 hours
- Phase 2 (Structural Chunking): 3-4 hours
- Phase 3 (Hybrid Retrieval): 2-3 hours
- Phase 4 (Bounded Generation): 3-4 hours
- Phase 5 (Strict Validation): 2-3 hours
- Phase 6 (Integration): 2-3 hours

**Total: 14-20 hours**

## Next Steps

1. Review and approve this plan
2. Begin Phase 1 (Simplification)
3. Iterate through phases sequentially
4. Test after each phase
5. Document changes in code comments
