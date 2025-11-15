"""Just RAG It - Zero-ceremony RAG for your documents.

A lightweight, production-ready RAG library extracted from the Chimera project.

Basic usage:
    >>> from justragit import RAG
    >>> rag = RAG(
    ...     base_path="/path/to/docs",
    ...     whitelist=["**/*.md", "**/*.py"]
    ... )
    >>> await rag.initialize()
    >>> results = await rag.search("How do I authenticate?")

From YAML:
    >>> rag = RAG.from_yaml("collections/my-docs.yaml")
    >>> await rag.initialize()
    >>> results = await rag.search("query")
"""

__version__ = "0.1.0"

from .api import RAG
from .core.chunker import DocumentChunker, Chunk
from .core.embeddings import VoyageEmbeddingService, EmbeddingResult
from .core.vector_store import VectorStore, SearchResult
from .config import CollectionConfig

__all__ = [
    "RAG",
    "DocumentChunker",
    "Chunk",
    "VoyageEmbeddingService",
    "EmbeddingResult",
    "VectorStore",
    "SearchResult",
    "CollectionConfig",
]
