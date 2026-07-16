"""Simple file-based storage for single-book demo."""

import json
import os
from typing import List
from src.models import Chunk


class SimpleStorage:
    """File-based storage for chunks."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.chunks_file = os.path.join(data_dir, "chunks.json")
    
    def save_chunks(self, chunks: List[Chunk]):
        """Save chunks to JSON."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        data = []
        for chunk in chunks:
            data.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "page_numbers": chunk.page_numbers,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "metadata": chunk.metadata
            })
        
        with open(self.chunks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_chunks(self) -> List[Chunk]:
        """Load chunks from JSON."""
        if not os.path.exists(self.chunks_file):
            return []
        
        with open(self.chunks_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        chunks = []
        for item in data:
            chunks.append(Chunk(
                chunk_id=item["chunk_id"],
                text=item["text"],
                page_numbers=item["page_numbers"],
                start_char=item["start_char"],
                end_char=item["end_char"],
                metadata=item.get("metadata", {})
            ))
        
        return chunks
