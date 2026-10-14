# 📚 BookBounded — Bounded Educational Tutoring Chatbot System

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18_%7C_Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![LLM](https://img.shields.io/badge/LLM-Google_Gemini_2.5_Flash-8E75C2?logo=google-gemini&logoColor=white)](https://ai.google.dev/)
[![Vector Store](https://img.shields.io/badge/Vector_DB-FAISS-0A84FF)](https://github.com/facebookresearch/faiss)
[![Embeddings](https://img.shields.io/badge/Embeddings-Sentence--Transformers-FFD21E)](https://sbert.net/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

An enterprise-grade, pedagogically bounded AI tutoring chatbot platform engineered for children and students aged **4 to 15**. BookBounded ingests full-length educational books (PDF format), performs structural and semantic chunking, and guarantees **100% grounded, hallucination-free responses** strictly derived from the book's verifiable text with explicit chunk and page citations.

---

## 📑 Table of Contents

- [Vision & Problem Statement](#-vision--problem-statement)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Core Processing Pipeline](#-core-processing-pipeline)
- [Project Directory Layout](#-project-directory-layout)
- [Tech Stack](#-tech-stack)
- [Local Setup & Execution](#-local-setup--execution)
- [API Reference](#-api-reference)
- [Deployment Guide (Vercel & Cloud)](#-deployment-guide-vercel--cloud)
- [System Verification & Audit Status](#-system-verification--audit-status)
- [👥 Contributors](#-contributors)
- [📄 License](#-license)

---

## 🌟 Vision & Problem Statement

### The Problem
Traditional generative LLMs frequently hallucinate facts, invent external metaphors, and produce answers beyond a textbook's curriculum. In early education (ages 4–15), ungrounded responses cause confusion, undermine classroom authority, and risk exposing students to unvetted external information.

### The BookBounded Solution
BookBounded introduces a **Strict Boundary Verification Framework**:
- 🛑 **Strict Domain Boundedness**: Out-of-bounds questions (e.g., asking about pop culture or unrelated topics) are politely rejected with explicit guidance back to the uploaded textbook.
- 📖 **100% Textual Grounding**: Every answer is verified against exact paragraphs extracted from the source PDF.
- 🎯 **Verifiable Citations**: Every response references the exact chunk IDs and page numbers where the concept originates.
- 🧒 **Age-Adaptive Pedagogy**: Explanations adapt automatically to the cognitive level of learners aged 4–15 without losing factual rigor.
- 🌐 **Multilingual Competency**: Full bilingual text extraction, vectorization, and pedagogical explanation in both **English** and **Urdu**.

---

## 🚀 Key Features

- 📑 **High-Throughput PDF Parsing**: Deep document structure extraction extracting headers, paragraphs, and page numbers (tested up to 450+ pages).
- 🧩 **Structural & Semantic Chunking**: Hybrid chunking preserving thematic paragraphs, tables, and section hierarchies instead of blind character slicing.
- 🔍 **3-Stage Hybrid Retrieval Engine**:
  1. *Lexical & Keyword Filtering*: Validates minimum keyword overlap to block semantic guessing.
  2. *Dense Vector Search*: Ranks candidate chunks via multilingual MiniLM vector embeddings and FAISS index.
  3. *Overlap Verification*: Ensures direct grounding in retrieved context before generation.
- 🤖 **Gemini 2.5 Flash & Dual Generation Engine**:
  - *Pedagogical Synthesis*: Generates interactive, conversational tutoring responses powered by Google Gemini.
  - *Template Fallback*: Assembles verifiable quote templates if offline or strict quote mode is requested.
- 🛡️ **Anti-Hallucination Strict Grounding Validator**: Evaluates every generated answer to ensure zero external facts or ungrounded claims are returned.
- 💻 **Modern React + Vite Frontend**: Clean, responsive interactive web UI featuring real-time chat, error handling, and backend proxying.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   REACT 18 WEB INTERFACE               │
│                (Vite • Responsive Chat UI)             │
└───────────────────────────┬────────────────────────────┘
                            │ [HTTP / REST :3000 -> :8000]
                            ▼
┌────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                     │
│  ┌──────────────────┐           ┌──────────────────┐  │
│  │   /upload (PDF)  │           │   /chat (Query)  │  │
│  └────────┬─────────┘           └────────┬─────────┘  │
└───────────┼──────────────────────────────┼─────────────┘
            │                              │
            ▼                              ▼
┌───────────────────────┐      ┌─────────────────────────┐
│ PDF INGESTION ENGINE  │      │    QUERY CLASSIFIER     │
│ - Structure Extractor │      │ - Definition / Concept  │
│ - Paragraph Chunking  │      │ - Example / Explanation │
│ - Page Mapping        │      │ - Out-of-Bounds Rejection│
└───────────┬───────────┘      └───────────┬─────────────┘
            │                              │
            ▼                              ▼
┌───────────────────────┐      ┌─────────────────────────┐
│ VECTOR & DATA STORAGE │      │ 3-STAGE HYBRID RETRIEVAL│
│ - FAISS Vector Index  │◄─────┤ 1. Keyword Overlap      │
│ - MiniLM Embeddings   │      │ 2. Dense Vector Ranking │
│ - SQLite / JSON Meta  │      │ 3. Textual Verification │
└───────────────────────┘      └───────────┬─────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │  BOUNDED CHATBOT ENGINE │
                               │  - Google Gemini API    │
                               │  - Age Adaptation (4-15)│
                               │  - Strict Citation Link │
                               └───────────┬─────────────┘
                                           │
                                           ▼
                               ┌─────────────────────────┐
                               │ STRICT GROUNDING CHECK  │
                               │ - Verifies Book Quotes  │
                               │ - Discards Hallucination│
                               └─────────────────────────┘
```

---

## 📁 Project Directory Layout

```text
BookBounded_Tutoring_Chatbot/
├── data/                               # Local data storage
│   ├── uploads/                        # Uploaded textbook PDFs
│   └── vector_store/                   # Serialized FAISS indices & chunk mapping
├── frontend/                           # React 18 frontend application
│   ├── src/
│   │   ├── App.jsx                     # Interactive chat application
│   │   ├── App.css                     # Component styles & animations
│   │   ├── index.css                   # Global styles
│   │   └── main.jsx                    # React entrypoint
│   ├── package.json                    # Frontend dependencies (React, Vite, Axios)
│   └── vite.config.js                  # Vite server & API proxy config (:3000 -> :8000)
├── src/                                # FastAPI backend core modules
│   ├── main.py                         # FastAPI REST application & endpoint routes
│   ├── bounded_chatbot.py              # LLM integration (Google Gemini / Ollama)
│   ├── pdf_parser.py                   # Structure-aware PDF text extraction
│   ├── chunking_engine.py              # Paragraph and semantic chunking
│   ├── embedding_generator.py          # Multilingual sentence transformer embeddings
│   ├── vector_store.py                 # FAISS vector database management
│   ├── hybrid_retrieval.py             # 3-stage hybrid search & overlap filter
│   ├── query_classifier.py             # Intent and domain-boundary classifier
│   ├── strict_validator.py             # Anti-hallucination quote validator
│   ├── age_inference.py                # Age-adaptive pedagogical language filter
│   ├── simple_storage.py               # JSON storage engine
│   └── database.py                     # SQLite metadata engine
├── tests/                              # Automated test suites
├── requirements.txt                    # Python dependencies
├── start_backend.bat                   # 1-click Windows backend runner
└── README.md                           # Master documentation
```

---

## 💻 Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 5, JavaScript (ES6+), Vanilla CSS |
| **Backend** | Python 3.12, FastAPI, Uvicorn, Pydantic v2 |
| **AI / LLM** | Google Gemini 2.5 Flash / 1.5 Flash (`google-generativeai`), Ollama fallback |
| **Embeddings** | `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`) |
| **Vector DB** | FAISS CPU (`faiss-cpu`) |
| **Document Processing** | PyPDF2, pdfplumber, pdfminer.six |
| **Persistence** | SQLite, Structured JSON |

---

## 🚀 Local Setup & Execution

### Prerequisites
- **Python**: v3.10+ (Tested on **Python 3.12.10**)
- **Node.js**: v18+ (Tested on **Node.js v26.7.0** with npm)

---

### Step 1: Backend Setup & Launch

1. **Configure Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000
   DATABASE_URL=sqlite:///./data/books.db
   VECTOR_STORE_TYPE=faiss
   VECTOR_STORE_PATH=./data/vector_store
   EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   CHUNK_SIZE=500
   CHUNK_OVERLAP=50
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the FastAPI Server**:
   ```bash
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   * The backend will start on **`http://localhost:8000`**.
   * Interactive Swagger documentation: **`http://localhost:8000/docs`**.

---

### Step 2: Frontend Setup & Launch

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install NPM dependencies**:
   ```bash
   npm install
   ```

3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   * Open **`http://localhost:3000`** in your browser.
   * Requests to `/api/*` are automatically proxied to the backend on `http://localhost:8000`.

---

## 📡 API Reference

### 1. Ingest Textbook
```http
POST /upload
Content-Type: multipart/form-data
```
| Parameter | Type | Description |
|---|---|---|
| `file` | `UploadFile (PDF)` | Educational textbook PDF file to vectorize and bind |

**Response**:
```json
{
  "message": "Book ingested: 142 chunks",
  "chunks": 142
}
```

### 2. Query Chatbot
```http
POST /chat
Content-Type: application/json
```
```json
{
  "query": "What is intentional learning?",
  "language": "en"
}
```

**Response**:
```json
{
  "response": "According to page 14 of the book, intentional learning refers to...",
  "is_refusal": false,
  "chunk_ids": ["chunk_0014_02"]
}
```

### 3. Service Health Check
```http
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## ☁️ Deployment Guide (Vercel & Cloud)

### 1. Frontend Deployment to Vercel

The application is pre-configured with `vercel.json` for seamless deployment to [Vercel](https://vercel.com):

1. **Push your code to GitHub**.
2. **Import repository on Vercel**:
   - Framework Preset: **Vite**
   - Root Directory: `./` (or `frontend`)
   - Build Command: `npm run build`
   - Output Directory: `dist` (or `frontend/dist`)
3. **Environment Variables**:
   - `VITE_API_URL`: URL of your deployed FastAPI backend (e.g., `https://your-api.up.railway.app`)
4. **Deploy**:
   - Vercel will build and serve the React application with full SPA routing rewrites.
   - If accessed standalone without a live backend, the UI includes an automatic interactive demo fallback so visitors and evaluators never encounter broken views.

---

### 2. Backend Cloud Deployment (Railway / Render / Docker)

The FastAPI backend can be deployed to any Python container service:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Set environment variables in your cloud provider dashboard:
- `GEMINI_API_KEY`: Your Google Gemini API Key
- `LLM_PROVIDER`: `gemini`
- `GEMINI_MODEL`: `gemini-2.5-flash`

---

## ✅ System Verification & Audit Status

| Component | Test Executed | Result |
|---|---|---|
| **PDF Ingestion** | Ingestion of 457-page *Building the Intentional University* | ✅ **1,841 Chunks Extracted & Vectorized** |
| **Vector Store** | FAISS Dense Indexing (`paraphrase-multilingual-MiniLM-L12-v2`) | ✅ **1,841 Vector Embeddings Generated** |
| **Grounded Retrieval** | Content queries (e.g. *What is intentional learning?*) | ✅ **Page 179 Verified Citation with Quote** |
| **Metadata Inquiries** | Book info (e.g. *Who is the author?*) | ✅ **Stephen M. Kosslyn correctly returned** |
| **Strict Refusal** | Out-of-bounds questions (e.g. *How to bake a cake?*) | ✅ **100% Out-of-Scope Refusal Enforced** |
| **Vercel Build** | `npm run build` production bundling | ✅ **Passed (696ms, 0 errors)** |

---

## 👥 Contributors

- **Lead Developer**: [Muhammad Abdullah Wasim](https://www.linkedin.com/in/muhammad-abdullah-92b50a304/)
- **Co Developer**: [Muhammad Siraj Munir](https://www.linkedin.com/in/siraj-munir-10furc/?isSelfProfile=false)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
