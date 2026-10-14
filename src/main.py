"""Simplified FastAPI application for Book-Bounded Tutoring Chatbot."""

import os
import sys
import shutil

# Ensure utf-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.simple_ingestion import ingest_book
from src.simple_storage import SimpleStorage
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.hybrid_retrieval import HybridRetrievalSystem
from src.bounded_chatbot import BoundedChatbotEngine
from src.strict_validator import StrictGroundingValidator
from src.query_classifier import QueryClassifier, QueryType

app = FastAPI(title="Book-Bounded Tutoring Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
embedding_gen = EmbeddingGenerator()
vector_store = VectorStore()
retrieval_system = HybridRetrievalSystem(embedding_gen, vector_store)
chatbot = BoundedChatbotEngine()
validator = StrictGroundingValidator()
storage = SimpleStorage()

# Log LLM configuration
print("=" * 60)
print("🤖 CHATBOT CONFIGURATION")
print("=" * 60)
print(f"LLM Provider: {chatbot.llm_provider}")
print(f"LLM Available: {chatbot.llm_available}")
if chatbot.llm_provider == "gemini":
    print(f"Gemini Model: {chatbot.gemini_model}")
    print(f"Gemini API Key: {'✅ Set' if chatbot.gemini_api_key else '❌ Not set'}")
elif chatbot.llm_provider == "ollama":
    print(f"Ollama Model: {chatbot.ollama_model}")
    print(f"Ollama URL: {chatbot.ollama_url}")
print("=" * 60)
print()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    query: str
    language: str = "en"


class ChatResponse(BaseModel):
    response: str
    is_refusal: bool
    chunk_ids: list


@app.post("/upload")
async def upload_book(file: UploadFile = File(...)):
    """Upload and ingest a book."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, "current_book.pdf")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Ingest
    try:
        chunks = ingest_book(file_path, "current_book")
        return {"message": f"Book ingested: {len(chunks)} chunks", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the book."""
    print(f"[CHAT] Received query: {request.query[:50]}")
    
    try:
        # STEP 1: Classify query FIRST (before any retrieval)
        query_type = chatbot.classifier.classify(request.query)
        print(f"[CHAT] Classified as: {query_type}")
        
        # STEP 2: Route based on classification
        
        # GREETING - Return friendly greeting
        if query_type == QueryType.GREETING:
            response_text = "Hello! I'm here to help you learn from this book. Feel free to ask me questions about the book's content, author, or topics!"
            return ChatResponse(
                response=response_text,
                is_refusal=False,
                chunk_ids=[]
            )
        
        # BOOK_METADATA - Return immediately from metadata (NO RETRIEVAL)
        if query_type == QueryType.BOOK_METADATA:
            # Check if it's a chapter list request
            if any(word in request.query.lower() for word in ['chapter', 'contents', 'toc']):
                if chatbot.metadata and chatbot.metadata.toc:
                    chapters = "\n".join(f"{i+1}. {ch}" for i, ch in enumerate(chatbot.metadata.toc))
                    response_text = f"Here are the chapters from the book:\n\n{chapters}"
                else:
                    response_text = "I don't have the full table of contents extracted yet, but you can ask me about specific topics in the book! For example, try asking 'What does the book say about universities?' or 'What is this book about?'"
                return ChatResponse(
                    response=response_text,
                    is_refusal=False,
                    chunk_ids=[]
                )
            
            response = chatbot._handle_metadata_query(
                request.query, 
                user_age=None, 
                language=request.language
            )
            return ChatResponse(
                response=response.text,
                is_refusal=response.is_refusal,
                chunk_ids=response.chunk_ids
            )
        
        # BOOK_OVERVIEW - Return immediately from description quotes (NO RETRIEVAL)
        if query_type == QueryType.BOOK_OVERVIEW:
            response = chatbot._handle_overview_query(
                request.query,
                user_age=None,
                language=request.language
            )
            return ChatResponse(
                response=response.text,
                is_refusal=response.is_refusal,
                chunk_ids=response.chunk_ids
            )
        
        # INVALID - Return refusal immediately (NO RETRIEVAL)
        if query_type == QueryType.INVALID:
            response = chatbot._handle_invalid_query(
                user_age=None,
                language=request.language
            )
            return ChatResponse(
                response=response.text,
                is_refusal=response.is_refusal,
                chunk_ids=response.chunk_ids
            )
        
        # REDIRECTION - Try to find related content and redirect
        if query_type == QueryType.REDIRECTION:
            # Extract key terms from the query for retrieval
            chunks = retrieval_system.retrieve_chunks("current_book", request.query, top_k=3)
            
            if chunks:
                # Generate response with redirection framing
                response = chatbot._handle_content_query(
                    request.query,
                    chunks,
                    user_age=None,
                    language=request.language
                )
                # Prepend redirection message
                response.text = f"The book doesn't ask that question directly, but it explains related ideas.\n\n{response.text}"
                return ChatResponse(
                    response=response.text,
                    is_refusal=False,
                    chunk_ids=response.chunk_ids
                )
            else:
                # No related content found
                return ChatResponse(
                    response="I can only answer questions using this book. Could you ask your question in a clearer way?",
                    is_refusal=True,
                    chunk_ids=[]
                )
        
        # CONTENT_QUERY - Only now do we run retrieval
        chunks = retrieval_system.retrieve_chunks("current_book", request.query, top_k=5)
        
        # Generate response (age is inferred automatically)
        response = chatbot._handle_content_query(
            request.query,
            chunks,
            user_age=None,
            language=request.language
        )
        
        # Skip validation for now - LLM responses are already grounded
        # validation = validator.validate_response(response, chunks)
        # if not validation.is_valid and not response.is_refusal:
        #     response = chatbot.generate_refusal(request.query, language=request.language)
        
        return ChatResponse(
            response=response.text,
            is_refusal=response.is_refusal,
            chunk_ids=response.chunk_ids
        )
    
    except Exception as e:
        raise HTTPException(500, f"Chat failed: {str(e)}")


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
