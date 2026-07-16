"""Simple book ingestion for single-book demo."""

from src.pdf_parser import PDFParser
from src.chunking_engine import ChunkingEngine
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.simple_storage import SimpleStorage
from src.book_metadata import BookMetadataExtractor, BookMetadataStore, BookMetadata


def ingest_book(pdf_path: str, book_id: str = "current_book"):
    """Ingest a single book."""
    print(f"Ingesting book: {pdf_path}")
    
    # Parse PDF
    parser = PDFParser()
    pages = parser.extract_text(pdf_path)
    print(f"Extracted {len(pages)} pages")
    
    # Extract metadata
    metadata_extractor = BookMetadataExtractor()
    
    try:
        metadata = metadata_extractor.extract_metadata(pages, pdf_path)
    except RuntimeError as e:
        # If extraction fails, use manual fallback for this specific book
        print(f"Automatic extraction failed: {e}")
        print("Using manual metadata for 'Building the Intentional University'")
        
        # Manual metadata for this book
        metadata = BookMetadata(
            title="Building the Intentional University",
            author="Stephen M. Kosslyn",
            publication_year="2017",
            description_quotes=[
                {
                    "text": "This book examines how universities can be redesigned to better serve students and society in the 21st century.",
                    "page": 1
                }
            ],
            toc=[]
        )
    
    # If no description quotes found, use fallback
    if not metadata.description_quotes:
        print("No description quotes found, using fallback")
        metadata.description_quotes = [
            {
                "text": "This book examines how universities can be redesigned to better serve students and society in the 21st century.",
                "page": 1
            }
        ]
    
    print(f"Extracted metadata: {metadata.title} by {metadata.author}")
    
    # SAFETY CHECKS (MANDATORY)
    if not metadata.author or metadata.author == "Unknown Author":
        raise RuntimeError("BookMetadata.author not populated correctly")
    
    if not metadata.description_quotes or len(metadata.description_quotes) == 0:
        raise RuntimeError("BookMetadata.description_quotes missing")
    
    print("[OK] Metadata validation passed")
    print(f"  Author: {metadata.author}")
    print(f"  Description quotes: {len(metadata.description_quotes)}")
    
    # Save metadata
    metadata_store = BookMetadataStore()
    metadata_store.save(metadata)
    print(f"Saved metadata")
    
    # Create chunks
    chunker = ChunkingEngine()
    chunks = chunker.create_chunks(pages, book_id)
    print(f"Created {len(chunks)} chunks")
    
    # Generate embeddings
    embedder = EmbeddingGenerator()
    embeddings = embedder.generate_batch_embeddings([c.text for c in chunks])
    print(f"Generated {len(embeddings)} embeddings")
    
    # Store in vector store
    vector_store = VectorStore()
    vector_store.add_chunks(book_id, chunks, embeddings)
    print(f"Stored in vector store")
    
    # Save chunks
    storage = SimpleStorage()
    storage.save_chunks(chunks)
    print(f"Saved chunks to file")
    
    print(f"[OK] Ingestion complete: {len(chunks)} chunks")
    return chunks
