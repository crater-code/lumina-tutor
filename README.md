# Book-Bounded Tutoring Chatbot

A web-based bounded tutoring chatbot system that transforms uploaded books (PDF format) into strictly bounded educational chatbots for children aged 4-15. The system enforces strict content boundaries, ensuring all responses derive exclusively from the uploaded book content with explicit citations.

## Features

- **PDF Book Ingestion**: Upload PDF books (up to 450 pages) and automatically process them
- **Semantic Chunking**: Automatically divide books into semantically meaningful chunks
- **Multilingual Support**: Support for both English and Urdu text
- **Bounded Responses**: All chatbot responses are strictly derived from book content
- **Explicit Citations**: Every response includes chunk IDs for verification
- **Age-Adaptive Language**: Adjust language complexity for ages 4-15
- **Hallucination Prevention**: Validation layer prevents made-up information
- **Multi-Book Support**: Upload and manage multiple books

## Project Structure

```
.
├── src/                    # Python backend source code
│   ├── __init__.py
│   └── main.py            # FastAPI application
├── tests/                 # Test files
│   └── __init__.py
├── frontend/              # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── data/                  # Data storage (PDFs, vector stores, database)
├── requirements.txt       # Python dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
python src/main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Health Check
- `GET /health` - Check backend service health
- `GET /` - Root endpoint with API information

### Books (Coming Soon)
- `POST /api/books/upload` - Upload a PDF book
- `GET /api/books` - List all uploaded books
- `DELETE /api/books/{book_id}` - Delete a book

### Chat (Coming Soon)
- `POST /api/chat` - Send a chat message
- `GET /api/chat/history/{session_id}` - Get chat history

### Chunks (Coming Soon)
- `GET /api/chunks/{chunk_id}` - Get chunk content for citations

## Testing

Run tests with pytest:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

Run property-based tests:
```bash
pytest tests/ -m property
```

## Technology Stack

### Backend
- **Python 3.9+**
- **FastAPI** - Web framework
- **PyPDF2/pdfplumber** - PDF processing
- **sentence-transformers** - Embeddings generation
- **FAISS/ChromaDB** - Vector storage
- **SQLAlchemy** - Database ORM
- **Hypothesis** - Property-based testing

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client

## License

This project uses only free and open-source libraries and frameworks.

## Development Status

This project is currently in development. Task 1 (project structure and dependencies) is complete.
