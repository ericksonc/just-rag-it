"""Core RAG components.

This package contains the fundamental building blocks:
- DocumentChunker: Context-aware document chunking
- VoyageEmbeddingService: Embedding generation via Voyage AI
- VectorStore: ChromaDB-based vector storage and retrieval
- FileDiscovery: File discovery and loading with pattern matching
"""

from .chunker import DocumentChunker, Chunk
from .embeddings import VoyageEmbeddingService, EmbeddingResult
from .vector_store import VectorStore, SearchResult
from .file_discovery import FileDiscovery

__all__ = [
    "DocumentChunker",
    "Chunk",
    "VoyageEmbeddingService",
    "EmbeddingResult",
    "VectorStore",
    "SearchResult",
    "FileDiscovery",
]
