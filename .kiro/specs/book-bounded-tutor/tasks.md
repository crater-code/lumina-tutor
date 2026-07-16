# Implementation Plan: Book-Bounded Tutoring Chatbot

## Overview

This implementation plan breaks down the book-bounded tutoring chatbot system into discrete, incremental coding tasks. The system will be built using Python for the backend (PDF processing, chunking, retrieval, chatbot logic) and React for the frontend (web interface). Each task builds on previous work, with testing integrated throughout to validate functionality early.

The implementation follows a bottom-up approach: core data processing first (PDF → chunks → embeddings), then retrieval and response generation, then validation and UI, and finally integration and refinement.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python virtual environment and install core dependencies (PyPDF2/pdfplumber, sentence-transformers, FAISS/ChromaDB, Flask/FastAPI, hypothesis for testing)
  - Create project directory structure: `src/`, `tests/`, `data/`, `frontend/`
  - Set up basic Flask/FastAPI application with health check endpoint
  - Initialize React frontend with create-react-app or Vite
  - Create requirements.txt and package.json with all dependencies
  - _Requirements: 10.1, 10.2_

- [ ] 2. Implement PDF Parser
  - [x] 2.1 Create PDFParser class with text extraction
    - Implement `extract_text()` method using PyPDF2 or pdfplumber
    - Extract text content and page numbers from PDF files
    - Handle Unicode characters (English and Urdu)
    - Implement page count validation (max 450 pages)
    - Raise appropriate exceptions for invalid PDFs
    - _Requirements: 1.1, 1.2, 1.6, 1.7_
  
  - [ ]* 2.2 Write property test for PDF text extraction
    - **Property 2: Multilingual Text Extraction Preservation**
    - **Validates: Requirements 1.2**
  
  - [ ]* 2.3 Write unit tests for PDF Parser edge cases
    - Test with empty PDFs (should raise NoTextError)
    - Test with oversized PDFs (451+ pages, should raise FileSizeError)
    - Test with corrupted PDFs (should raise PDFParseError)
    - Test with mixed English/Urdu content
    - _Requirements: 1.6, 1.7_

- [ ] 3. Implement Chunking Engine
  - [x] 3.1 Create ChunkingEngine class with automatic chunking
    - Implement `create_chunks()` method with fixed-size chunking and overlap
    - Use sentence boundary detection to avoid mid-sentence splits
    - Generate unique Chunk_IDs (format: "book_{book_id}_chunk_{index}")
    - Extract metadata (page numbers, start/end character positions)
    - Handle both English and Urdu text correctly
    - _Requirements: 1.3, 1.4, 2.1, 2.2, 2.3_
  
  - [ ]* 3.2 Write property test for chunk ID uniqueness
    - **Property 4: Chunk ID Uniqueness**
    - **Validates: Requirements 1.4**
  
  - [ ]* 3.3 Write property test for semantic boundary preservation
    - **Property 6: Semantic Boundary Preservation**
    - **Validates: Requirements 2.2**
  
  - [ ]* 3.4 Write property test for chunk metadata completeness
    - **Property 7: Chunk Metadata Completeness**
    - **Validates: Requirements 2.3**
  
  - [ ]* 3.5 Write unit tests for chunking edge cases
    - Test with very short text (< chunk size)
    - Test with text exactly at chunk size boundary
    - Test with text containing only whitespace
    - _Requirements: 1.3, 2.2_

- [ ] 4. Implement Embedding Generator and Vector Store
  - [x] 4.1 Create EmbeddingGenerator class
    - Initialize sentence-transformers model (paraphrase-multilingual-MiniLM-L12-v2)
    - Implement `generate_embedding()` for single text
    - Implement `generate_batch_embeddings()` for multiple texts
    - Handle both English and Urdu text
    - _Requirements: 3.1, 3.2, 8.1, 8.2_
  
  - [x] 4.2 Create VectorStore class using FAISS or ChromaDB
    - Implement `add_chunks()` to store chunks with embeddings
    - Implement `search()` for similarity search with top-k and threshold
    - Implement `delete_book()` to remove all chunks for a book
    - Maintain book-to-chunks mapping for isolation
    - _Requirements: 1.5, 11.4_
  
  - [ ]* 4.3 Write property test for chunk storage round-trip
    - **Property 5: Chunk Storage and Retrieval Round-Trip**
    - **Validates: Requirements 1.5**
  
  - [ ]* 4.4 Write property test for book-specific chunk isolation
    - **Property 27: Book-Specific Chunk Isolation**
    - **Validates: Requirements 11.4**
  
  - [ ]* 4.5 Write unit tests for vector store operations
    - Test adding chunks and verifying storage
    - Test searching with various similarity thresholds
    - Test deleting a book and verifying chunks are removed
    - _Requirements: 1.5, 11.4_

- [ ] 5. Implement Retrieval System
  - [x] 5.1 Create RetrievalSystem class
    - Implement `retrieve_chunks()` method
    - Generate query embedding using EmbeddingGenerator
    - Search VectorStore for similar chunks
    - Rank results by relevance score (descending)
    - Return top-k chunks above minimum threshold
    - Handle empty results (return empty list)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 5.2 Write property test for multilingual query retrieval
    - **Property 8: Multilingual Query Retrieval**
    - **Validates: Requirements 3.1, 3.2**
  
  - [ ]* 5.3 Write property test for retrieval result ranking
    - **Property 9: Retrieval Result Ranking**
    - **Validates: Requirements 3.3**
  
  - [ ]* 5.4 Write property test for top-K retrieval limit
    - **Property 10: Top-K Retrieval Limit**
    - **Validates: Requirements 3.4**
  
  - [ ]* 5.5 Write property test for query-book binding
    - **Property 28: Query-Book Binding**
    - **Validates: Requirements 11.5**
  
  - [ ]* 5.6 Write unit tests for retrieval edge cases
    - Test with empty query (should handle gracefully)
    - Test with query that has no matches (should return empty list)
    - Test with multiple books (should only return chunks from selected book)
    - _Requirements: 3.5, 11.5_

- [-] 6. Checkpoint - Ensure core pipeline works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Chatbot Engine
  - [x] 7.1 Create ChatbotEngine class with response generation
    - Implement `generate_response()` method
    - Build prompt with system instructions, age adaptation, and retrieved chunks
    - Use free LLM API (Ollama with local model, or Hugging Face Inference API)
    - Include Chunk_IDs in response
    - Implement age-adaptive language prompting (4-7, 8-11, 12-15 age groups)
    - Generate responses in same language as query
    - _Requirements: 4.1, 4.3, 7.1, 7.2, 8.5_
  
  - [x] 7.2 Implement refusal message generation
    - Create `generate_refusal()` method
    - Generate polite, age-appropriate refusal messages
    - Explain that answer is not in the book
    - Encourage asking different questions
    - Do not suggest external resources
    - _Requirements: 4.4, 12.1, 12.2, 12.4, 12.5_
  
  - [ ]* 7.3 Write property test for response citation requirement
    - **Property 12: Response Citation Requirement**
    - **Validates: Requirements 4.3**
  
  - [ ]* 7.4 Write property test for refusal message purity
    - **Property 13: Refusal Message Purity**
    - **Validates: Requirements 4.5**
  
  - [ ]* 7.5 Write property test for response language matching
    - **Property 20: Response Language Matching**
    - **Validates: Requirements 8.5**
  
  - [ ]* 7.6 Write property test for comprehensive refusal message
    - **Property 29: Comprehensive Refusal Message**
    - **Validates: Requirements 12.2, 12.4, 12.5**
  
  - [ ]* 7.7 Write unit tests for chatbot engine
    - Test response generation with various chunk sets
    - Test refusal generation with empty chunk list
    - Test age adaptation (verify different prompts for different ages)
    - Test multilingual response generation
    - _Requirements: 4.1, 4.4, 7.2, 8.5_

- [ ] 8. Implement Response Validator
  - [x] 8.1 Create ResponseValidator class
    - Implement `validate_response()` method
    - Check that response content is traceable to retrieved chunks
    - Implement `check_hallucination()` using keyword matching and similarity
    - Return ValidationResult with is_valid flag and issues list
    - Log rejected responses with timestamp and reason
    - _Requirements: 4.6, 6.1, 6.2, 6.4_
  
  - [ ]* 8.2 Write property test for response validation enforcement
    - **Property 14: Response Validation Enforcement**
    - **Validates: Requirements 6.1**
  
  - [ ]* 8.3 Write property test for hallucination detection
    - **Property 15: Hallucination Detection**
    - **Validates: Requirements 6.2**
  
  - [ ]* 8.4 Write property test for validation failure recovery
    - **Property 16: Validation Failure Recovery**
    - **Validates: Requirements 6.3**
  
  - [ ]* 8.5 Write property test for rejected response logging
    - **Property 17: Rejected Response Logging**
    - **Validates: Requirements 6.4**
  
  - [ ]* 8.6 Write unit tests for response validator
    - Test with valid responses (should pass validation)
    - Test with responses containing hallucinated content (should fail)
    - Test with responses missing citations (should fail)
    - Verify logging of rejected responses
    - _Requirements: 6.1, 6.2, 6.4_

- [ ] 9. Implement Book Ingestion Pipeline
  - [x] 9.1 Create BookIngestionPipeline orchestrator class
    - Implement `ingest_book()` method that orchestrates full pipeline
    - Call PDFParser to extract text
    - Call ChunkingEngine to create chunks
    - Call EmbeddingGenerator to create embeddings
    - Call VectorStore to store chunks and embeddings
    - Store book metadata in database
    - Handle errors at each stage and update processing status
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 9.2 Write property test for sequential multi-book upload
    - **Property 25: Sequential Multi-Book Upload**
    - **Validates: Requirements 11.1**
  
  - [ ]* 9.3 Write property test for book processing isolation
    - **Property 26: Book Processing Isolation**
    - **Validates: Requirements 11.2**
  
  - [ ]* 9.4 Write integration tests for book ingestion
    - Test end-to-end ingestion with sample PDF
    - Test ingestion failure handling (corrupted PDF)
    - Test multiple book uploads (verify isolation)
    - _Requirements: 1.1, 1.2, 1.3, 11.1, 11.2_

- [ ] 10. Implement Database Models and Storage
  - [x] 10.1 Set up SQLite database with schema
    - Create books table (book_id, title, filename, upload_date, page_count, processing_status, language, metadata)
    - Create chunks table (chunk_id, book_id, text, page_numbers, start_char, end_char, metadata)
    - Create chat_sessions table (session_id, book_id, user_age, created_at)
    - Create messages table (message_id, session_id, role, content, chunk_ids, timestamp)
    - _Requirements: 1.5, 11.4_
  
  - [x] 10.2 Create database access layer
    - Implement CRUD operations for books
    - Implement CRUD operations for chunks
    - Implement CRUD operations for chat sessions and messages
    - _Requirements: 1.5, 7.1_
  
  - [ ]* 10.3 Write unit tests for database operations
    - Test creating, reading, updating, deleting books
    - Test storing and retrieving chunks
    - Test chat session and message storage
    - _Requirements: 1.5_

- [ ] 11. Checkpoint - Ensure backend components work together
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement Backend API Endpoints
  - [ ] 12.1 Create Flask/FastAPI application with routes
    - POST /api/books/upload - Handle PDF upload and trigger ingestion
    - GET /api/books - List all uploaded books with metadata
    - DELETE /api/books/{book_id} - Delete book and all associated data
    - POST /api/chat - Handle chat messages and return responses
    - GET /api/chat/history/{session_id} - Retrieve chat history
    - GET /api/chunks/{chunk_id} - Get chunk content for citation viewing
    - _Requirements: 1.1, 11.1, 11.3_
  
  - [ ] 12.2 Implement query handler logic
    - Validate user input (query, book_id, user_age)
    - Call RetrievalSystem to get relevant chunks
    - Call ChatbotEngine to generate response
    - Call ResponseValidator to validate response
    - Handle validation failures (regenerate or return refusal)
    - Store message in database
    - Return response with citations to frontend
    - _Requirements: 3.1, 4.1, 4.4, 6.1, 6.3_
  
  - [ ]* 12.3 Write integration tests for API endpoints
    - Test book upload endpoint with valid and invalid PDFs
    - Test chat endpoint with various queries
    - Test book listing and deletion
    - Test chunk retrieval for citations
    - _Requirements: 1.1, 3.1, 4.1_

- [ ] 13. Implement Frontend Web Interface
  - [ ] 13.1 Create React components for book management
    - BookUpload component with file input and upload button
    - BookList component showing uploaded books
    - BookSelector dropdown for selecting active book
    - Display upload progress and processing status
    - _Requirements: 9.6, 11.3_
  
  - [ ] 13.2 Create React components for chat interface
    - ChatWindow component displaying message history
    - MessageInput component with text area and send button
    - Message component for rendering user/bot messages
    - CitationDisplay component for showing chunk IDs and content
    - LoadingIndicator component for processing state
    - AgeInput component for setting user age (4-15)
    - _Requirements: 9.1, 9.2, 9.3, 9.7, 7.1_
  
  - [ ] 13.3 Implement API integration in frontend
    - Create API client functions for all backend endpoints
    - Handle file upload with progress tracking
    - Send chat messages and receive responses
    - Fetch and display chunk content when citation clicked
    - Handle errors and display user-friendly messages
    - _Requirements: 9.1, 9.3, 5.3_
  
  - [ ] 13.4 Add multilingual UI support
    - Ensure text input supports Urdu characters
    - Use appropriate fonts for Urdu text rendering
    - Test display of mixed English/Urdu content
    - _Requirements: 9.5, 8.1, 8.2_
  
  - [ ]* 13.5 Write unit tests for React components
    - Test BookUpload component (file selection, upload trigger)
    - Test ChatWindow component (message display, scrolling)
    - Test MessageInput component (text input, send action)
    - Test CitationDisplay component (chunk ID display, expansion)
    - _Requirements: 9.1, 9.2, 9.3, 5.1_

- [ ] 14. Implement Age Preference Persistence
  - [ ] 14.1 Add age storage and retrieval
    - Store user age in chat session
    - Retrieve age when generating responses
    - Validate age is in range 4-15
    - _Requirements: 7.1_
  
  - [ ]* 14.2 Write property test for age preference persistence
    - **Property 18: Age Preference Persistence**
    - **Validates: Requirements 7.1**

- [ ] 15. Implement Citation Display and Viewing
  - [ ] 15.1 Add citation rendering in frontend
    - Display Chunk_IDs in response messages
    - Make citations clickable to view chunk content
    - Fetch chunk content from backend when clicked
    - Display chunk content in modal or expandable section
    - _Requirements: 5.1, 5.3_
  
  - [ ]* 15.2 Write property test for citation display in UI
    - **Property 21: Citation Display in UI**
    - **Validates: Requirements 5.1**
  
  - [ ]* 15.3 Write unit test for citation viewing
    - Test clicking citation triggers chunk content fetch
    - Test chunk content is displayed correctly
    - _Requirements: 5.3_

- [ ] 16. Implement Processing Indicator
  - [ ] 16.1 Add loading state management
    - Show loading indicator when query is sent
    - Hide loading indicator when response received
    - Show loading indicator during book upload
    - _Requirements: 9.7_
  
  - [ ]* 16.2 Write property test for processing indicator display
    - **Property 24: Processing Indicator Display**
    - **Validates: Requirements 9.7**

- [ ] 17. End-to-End Integration and Testing
  - [ ] 17.1 Perform end-to-end testing
    - Test complete flow: upload PDF → ask question → receive bounded response with citations
    - Test with multiple books (verify isolation)
    - Test with English and Urdu queries
    - Test with different age groups (verify language adaptation)
    - Test refusal messages (queries with no relevant chunks)
    - Test citation viewing (click citation → see chunk content)
    - _Requirements: 1.1, 3.1, 4.1, 4.4, 5.1, 7.2, 8.5, 11.1, 11.5_
  
  - [ ]* 17.2 Write integration tests for critical paths
    - Test hallucination prevention (verify validator rejects invalid responses)
    - Test multi-book isolation (verify queries only use selected book)
    - Test multilingual support (English and Urdu end-to-end)
    - _Requirements: 4.1, 6.2, 8.4, 11.5_

- [ ] 18. Final checkpoint and documentation
  - Ensure all tests pass, ask the user if questions arise.
  - Verify all requirements are met
  - Document setup instructions (README.md)
  - Document API endpoints
  - Document testing procedures

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- The implementation uses Python for backend and React for frontend
- All dependencies are free and open-source (zero-cost requirement)
- Testing is integrated throughout to catch issues early

