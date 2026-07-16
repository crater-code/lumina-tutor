# Requirements Document

## Introduction

This document specifies the requirements for a web-based bounded tutoring chatbot system that transforms uploaded books (PDF format) into strictly bounded educational chatbots for children aged 4-15. The system enforces strict content boundaries, ensuring all responses derive exclusively from the uploaded book content with explicit citations, while preventing any external knowledge injection or hallucination.

## Glossary

- **System**: The complete book-bounded tutoring chatbot application
- **Book_Ingestion_Pipeline**: The automated subsystem that processes PDF files into structured, retrievable chunks
- **PDF_Parser**: The component that extracts text and metadata from PDF files
- **Chunking_Engine**: The component that divides book content into semantically meaningful, retrievable segments
- **Retrieval_System**: The component that searches and ranks book chunks based on user queries
- **Chatbot_Engine**: The component that generates responses based on retrieved chunks
- **Response_Validator**: The component that enforces content boundaries and prevents hallucination
- **Web_Interface**: The user-facing chat application
- **Chunk**: A discrete segment of book content with associated metadata and unique identifier
- **Chunk_ID**: A unique identifier assigned to each chunk for citation purposes
- **Bounded_Response**: A response generated exclusively from retrieved book content
- **Hallucination**: Any content in a response that does not originate from the uploaded book
- **Age_Adaptive_Language**: Language complexity adjusted to the user's age group (4-15 years)

## Requirements

### Requirement 1: PDF Book Ingestion

**User Story:** As a tutor or parent, I want to upload a PDF book, so that the system can automatically create a tutoring chatbot from its content.

#### Acceptance Criteria

1. WHEN a user uploads a PDF file, THE Book_Ingestion_Pipeline SHALL accept files up to 450 pages
2. WHEN a PDF file is uploaded, THE PDF_Parser SHALL extract all text content including English and Urdu characters
3. WHEN text extraction completes, THE Chunking_Engine SHALL divide the content into semantically meaningful chunks without manual intervention
4. WHEN chunking completes, THE System SHALL assign a unique Chunk_ID to each chunk
5. WHEN chunk processing completes, THE System SHALL store chunks with their metadata in a retrievable format
6. IF a PDF file exceeds 450 pages, THEN THE System SHALL reject the upload and display an error message
7. IF a PDF file contains no extractable text, THEN THE System SHALL reject the upload and display an error message

### Requirement 2: Automated Chunk Creation

**User Story:** As a system operator, I want the system to automatically chunk any uploaded book, so that I don't need to manually prepare content.

#### Acceptance Criteria

1. THE Chunking_Engine SHALL process any uploaded book without manual configuration
2. WHEN creating chunks, THE Chunking_Engine SHALL preserve semantic coherence within each chunk
3. WHEN creating chunks, THE Chunking_Engine SHALL generate metadata including page numbers and section context
4. WHEN creating chunks, THE Chunking_Engine SHALL handle both English and Urdu text correctly
5. THE Chunking_Engine SHALL create chunks that are suitable for retrieval and citation

### Requirement 3: Query-Based Chunk Retrieval

**User Story:** As a student, I want to ask questions about the book, so that I can learn from its content.

#### Acceptance Criteria

1. WHEN a user submits a query in English, THE Retrieval_System SHALL identify relevant chunks from the uploaded book
2. WHEN a user submits a query in Urdu, THE Retrieval_System SHALL identify relevant chunks from the uploaded book
3. WHEN retrieving chunks, THE Retrieval_System SHALL rank results by relevance to the query
4. WHEN retrieval completes, THE Retrieval_System SHALL return the top-ranked chunks to the Chatbot_Engine
5. IF no relevant chunks are found above a minimum relevance threshold, THEN THE Retrieval_System SHALL return an empty result set

### Requirement 4: Strictly Bounded Response Generation

**User Story:** As a parent, I want the chatbot to only use content from the uploaded book, so that my child receives accurate information without external additions.

#### Acceptance Criteria

1. WHEN generating a response, THE Chatbot_Engine SHALL use only the content from retrieved chunks
2. WHEN generating a response, THE Chatbot_Engine SHALL NOT add external knowledge, examples, or facts
3. WHEN generating a response, THE Chatbot_Engine SHALL include the Chunk_ID for every chunk used
4. IF no relevant chunks are retrieved, THEN THE Chatbot_Engine SHALL generate a polite refusal message
5. WHEN a refusal message is generated, THE System SHALL NOT attempt to answer from external knowledge
6. THE Response_Validator SHALL verify that all response content originates from retrieved chunks

### Requirement 5: Explicit Citation Requirements

**User Story:** As an educator, I want every answer to cite its source chunks, so that I can verify the information and trace it back to the book.

#### Acceptance Criteria

1. WHEN displaying a response, THE Web_Interface SHALL show the Chunk_ID for each chunk used
2. THE System SHALL display citations in a clear, readable format
3. WHEN a user views a citation, THE System SHALL allow the user to see the original chunk content
4. THE Chatbot_Engine SHALL NOT generate responses without including at least one Chunk_ID citation
5. IF multiple chunks are used, THEN THE System SHALL display all relevant Chunk_IDs

### Requirement 6: Hallucination Prevention

**User Story:** As a parent, I want the system to prevent made-up information, so that my child only learns from the actual book content.

#### Acceptance Criteria

1. THE Response_Validator SHALL check each response against retrieved chunks before display
2. IF a response contains content not found in retrieved chunks, THEN THE Response_Validator SHALL reject the response
3. WHEN a response is rejected, THE System SHALL generate a new response or display a refusal message
4. THE System SHALL log all rejected responses for monitoring and improvement
5. THE Chatbot_Engine SHALL be configured to minimize hallucination risk through prompt engineering and constraints

### Requirement 7: Age-Adaptive Language

**User Story:** As a parent, I want the chatbot to adjust its language complexity based on my child's age, so that the explanations are appropriate and understandable.

#### Acceptance Criteria

1. WHEN a user specifies their age (4-15 years), THE System SHALL store the age preference
2. WHEN generating responses, THE Chatbot_Engine SHALL adapt language complexity to the specified age group
3. WHILE explaining content to users aged 4-7, THE Chatbot_Engine SHALL use simple vocabulary and short sentences
4. WHILE explaining content to users aged 8-11, THE Chatbot_Engine SHALL use intermediate vocabulary and moderate sentence complexity
5. WHILE explaining content to users aged 12-15, THE Chatbot_Engine SHALL use age-appropriate vocabulary while maintaining clarity
6. THE Chatbot_Engine SHALL simplify complex book content while preserving accuracy and meaning

### Requirement 8: Multilingual Support

**User Story:** As a student, I want to ask questions in English or Urdu, so that I can learn in my preferred language.

#### Acceptance Criteria

1. WHEN a user submits a query in English, THE System SHALL process and respond appropriately
2. WHEN a user submits a query in Urdu, THE System SHALL process and respond appropriately
3. THE PDF_Parser SHALL correctly extract and preserve Urdu text from uploaded PDFs
4. THE Retrieval_System SHALL handle queries in both English and Urdu with equivalent effectiveness
5. THE Chatbot_Engine SHALL generate responses in the same language as the user's query

### Requirement 9: Web-Based Chat Interface

**User Story:** As a student, I want to interact with the chatbot through a simple web interface, so that I can easily ask questions and read responses.

#### Acceptance Criteria

1. THE Web_Interface SHALL display a chat conversation view with user messages and bot responses
2. WHEN a user types a message, THE Web_Interface SHALL provide a text input field and send button
3. WHEN a user sends a message, THE Web_Interface SHALL display the message in the conversation view
4. WHEN the chatbot responds, THE Web_Interface SHALL display the response with visible citations
5. THE Web_Interface SHALL support both English and Urdu text input and display
6. THE Web_Interface SHALL provide a way to upload PDF books
7. THE Web_Interface SHALL indicate when the system is processing a query

### Requirement 10: Zero-Cost Implementation

**User Story:** As a project implementer, I want to build the system without paid tools or services, so that the project remains accessible and cost-free.

#### Acceptance Criteria

1. THE System SHALL use only free and open-source libraries and frameworks
2. THE System SHALL NOT require paid API services for core functionality
3. THE System SHALL NOT require paid hosting services for basic operation
4. WHERE cloud services are used, THE System SHALL use free-tier options
5. THE System SHALL document all dependencies and their licensing

### Requirement 11: Multi-Book Support

**User Story:** As a tutor, I want to upload different books at different times, so that I can create multiple tutoring chatbots for different subjects.

#### Acceptance Criteria

1. THE System SHALL support uploading multiple books sequentially
2. WHEN a new book is uploaded, THE System SHALL process it independently from previous books
3. WHEN a user starts a chat session, THE System SHALL allow selection of which book to use
4. THE System SHALL maintain separate chunk databases for each uploaded book
5. THE Chatbot_Engine SHALL only retrieve chunks from the currently selected book

### Requirement 12: Response Refusal Mechanism

**User Story:** As a parent, I want the chatbot to politely refuse questions it cannot answer from the book, so that my child understands the system's limitations.

#### Acceptance Criteria

1. WHEN no relevant chunks are found for a query, THE Chatbot_Engine SHALL generate a polite refusal message
2. THE refusal message SHALL explain that the answer is not found in the current book
3. THE refusal message SHALL be age-appropriate based on the user's specified age
4. THE refusal message SHALL NOT suggest external resources or knowledge
5. THE refusal message SHALL encourage the user to ask different questions about the book content

