"""Hybrid retrieval: keyword filtering + semantic ranking."""

import re
from typing import List, Set
from src.embedding_generator import EmbeddingGenerator
from src.vector_store import VectorStore
from src.models import Chunk


class HybridRetrievalSystem:
    """Hybrid retrieval with keyword filtering and semantic ranking."""
    
    def __init__(self, embedding_generator: EmbeddingGenerator, vector_store: VectorStore):
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
    
    def retrieve_chunks(self, book_id: str, query: str, top_k: int = 5) -> List[Chunk]:
        """Retrieve using hybrid approach: keywords + semantic."""
        # Extract keywords
        keywords = self._extract_keywords(query)
        
        # Get semantic candidates first
        all_results = self.vector_store.search(
            book_id=book_id,
            query_embedding=self.embedding_generator.generate_embedding(query),
            top_k=50,  # Get more candidates
            min_similarity=0.0
        )
        
        if not all_results:
            return []
        
        # Filter by keyword overlap (more lenient)
        filtered = []
        for chunk, score in all_results:
            chunk_keywords = self._extract_keywords(chunk.text)
            overlap = len(keywords.intersection(chunk_keywords))
            # Accept if ANY keyword matches OR high semantic similarity
            if overlap >= 1 or score > 0.5:
                filtered.append((chunk, score))
        
        # If no results match keywords or sufficient similarity, return empty (triggers refusal)
        if not filtered:
            return []
        
        # Return top-k by semantic score
        filtered.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in filtered[:top_k]]
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                     'has', 'he', 'in', 'is', 'it', 'of', 'on', 'that', 'the', 'to',
                     'was', 'will', 'with', 'this', 'but', 'they', 'have', 'what',
                     'when', 'where', 'who', 'how', 'can', 'i', 'you', 'we'}
        
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return {w for w in words if w not in stop_words and len(w) > 2}
