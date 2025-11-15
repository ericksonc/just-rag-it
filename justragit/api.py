"""High-level Python API for Just RAG It.

This module provides the main RAG class that users interact with.

Example:
    >>> from justragit import RAG
    >>> rag = RAG(
    ...     base_path="/path/to/docs",
    ...     whitelist=["**/*.md", "**/*.py"],
    ...     api_key="voyage_key"
    ... )
    >>> await rag.initialize()
    >>> results = await rag.search("How do I authenticate?", top_k=5)
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, List

from .core.chunker import DocumentChunker, Chunk
from .core.embeddings import VoyageEmbeddingService, EmbeddingResult
from .core.vector_store import VectorStore, SearchResult
from .core.file_discovery import FileDiscovery
from .config import CollectionConfig


class RAG:
    """High-level RAG interface.

    Combines file discovery, chunking, embedding, and vector search
    into a simple API.

    Example (direct):
        >>> rag = RAG(
        ...     base_path="/path/to/docs",
        ...     whitelist=["**/*.md"],
        ...     api_key="voyage_key"
        ... )
        >>> await rag.initialize()
        >>> results = await rag.search("authentication")

    Example (from YAML):
        >>> rag = RAG.from_yaml("collections/my-docs.yaml")
        >>> await rag.initialize()
        >>> results = await rag.search("query")
    """

    def __init__(
        self,
        base_path: str,
        whitelist: list[str],
        blacklist: list[str] | None = None,
        chunk_min_tokens: int = 400,
        chunk_max_tokens: int = 600,
        top_k: int = 5,
        api_key: Optional[str] = None,
        respect_gitignore: bool = True,
        max_file_size: int = 1_000_000,
    ):
        """Initialize RAG system.

        Args:
            base_path: Base directory for file discovery
            whitelist: Patterns to include (e.g., ["docs/", "**/*.md"])
            blacklist: Patterns to exclude (e.g., ["*/archive/"])
            chunk_min_tokens: Minimum tokens per chunk
            chunk_max_tokens: Maximum tokens per chunk
            top_k: Default number of search results to return
            api_key: Voyage AI API key (defaults to VOYAGE_API_KEY env var)
            respect_gitignore: If True, respect .gitignore files
            max_file_size: Maximum file size in bytes (default: 1MB)
        """
        self.base_path = Path(base_path)
        self.whitelist = whitelist
        self.blacklist = blacklist or []
        self.chunk_min_tokens = chunk_min_tokens
        self.chunk_max_tokens = chunk_max_tokens
        self.top_k = top_k
        self.api_key = api_key
        self.respect_gitignore = respect_gitignore
        self.max_file_size = max_file_size

        # Components
        self.file_discovery = FileDiscovery(
            base_path=str(self.base_path),
            whitelist_paths=self.whitelist,
            blacklist_paths=self.blacklist,
            respect_gitignore=self.respect_gitignore,
            max_file_size=self.max_file_size,
        )
        self.chunker = DocumentChunker(
            target_min_tokens=chunk_min_tokens,
            target_max_tokens=chunk_max_tokens,
        )
        self.vector_store = VectorStore()
        self._embedding_service: Optional[VoyageEmbeddingService] = None

        # State
        self.documents: dict[str, str] = {}
        self.active_file_paths: list[str] = []
        self._initialized: bool = False

    @classmethod
    def from_yaml(cls, config_path: str) -> 'RAG':
        """Create RAG instance from YAML configuration.

        Args:
            config_path: Path to YAML config file

        Returns:
            RAG instance

        Example:
            >>> rag = RAG.from_yaml("collections/my-docs.yaml")
        """
        config = CollectionConfig.from_yaml(config_path)

        return cls(
            base_path=config.base_path,
            whitelist=config.whitelist_paths,
            blacklist=config.blacklist_paths,
            chunk_min_tokens=config.chunk_min_tokens,
            chunk_max_tokens=config.chunk_max_tokens,
            top_k=config.top_k,
            respect_gitignore=config.respect_gitignore,
            max_file_size=config.max_file_size,
        )

    async def _ensure_embedding_service(self) -> VoyageEmbeddingService:
        """Lazily create embedding service (needs async context)."""
        if self._embedding_service is None:
            self._embedding_service = VoyageEmbeddingService(api_key=self.api_key)
        return self._embedding_service

    def _compute_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of a single file's content.

        Args:
            file_path: Relative path to file

        Returns:
            SHA256 hex string (64 characters)
        """
        content = self.documents.get(file_path, "")
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def initialize(self) -> None:
        """Initialize RAG system: discover files and generate embeddings.

        This performs:
        1. File discovery (loads matching files from disk)
        2. Embedding generation (with incremental updates via file hashing)

        Only changed files are re-embedded, making this efficient for
        large document sets.

        Example:
            >>> await rag.initialize()
            ✓ 15/20 files unchanged (reusing embeddings)
            🔄 5/20 new files to embed
            ✓ RAG embeddings ready (20 files, 150 total chunks)
        """
        if self._initialized:
            return

        # Step 1: Discover files
        print(f"📂 Discovering files in {self.base_path}...")
        self.documents = self.file_discovery.discover()

        if not self.documents:
            print("⚠️ No documents found matching patterns")
            self._initialized = True
            return

        print(f"✓ Found {len(self.documents)} files ({sum(len(c) for c in self.documents.values()):,} chars)")

        # Step 2: Generate embeddings (with incremental updates)
        await self._initialize_embeddings()

    async def _initialize_embeddings(self) -> None:
        """Generate and store embeddings using per-file hashing (lazy loading).

        For each file:
        1. Check if file_hash matches what's in the database
        2. If hash matches: skip (embeddings already exist)
        3. If hash differs or file is new: re-chunk, re-embed, store
        """
        if not self.documents:
            print("⚠️ No documents to embed")
            self._initialized = True
            return

        base_path_str = str(self.base_path.resolve())

        # Get existing file hashes from database
        existing_file_hashes = self.vector_store.get_file_hashes(base_path_str)

        # Determine which files need embedding
        files_to_embed = []
        files_to_update = []
        files_unchanged = []

        for file_path in self.documents.keys():
            current_hash = self._compute_file_hash(file_path)
            existing_hash = existing_file_hashes.get(file_path)

            if existing_hash is None:
                # New file - needs embedding
                files_to_embed.append(file_path)
            elif existing_hash != current_hash:
                # File changed - needs re-embedding
                files_to_update.append(file_path)
            else:
                # File unchanged - skip
                files_unchanged.append(file_path)

        # Report status
        total_files = len(self.documents)
        if files_unchanged:
            print(f"✓ {len(files_unchanged)}/{total_files} files unchanged (reusing embeddings)")
        if files_to_embed:
            print(f"🔄 {len(files_to_embed)}/{total_files} new files to embed")
        if files_to_update:
            print(f"🔄 {len(files_to_update)}/{total_files} changed files to re-embed")

        # Process files that need embedding/updating
        files_needing_work = files_to_embed + files_to_update

        if not files_needing_work:
            # All files up to date
            self.active_file_paths = list(self.documents.keys())
            self._initialized = True
            return

        # Delete old chunks for updated files
        for file_path in files_to_update:
            deleted_count = self.vector_store.delete_file_chunks(base_path_str, file_path)
            print(f"  → Deleted {deleted_count} old chunks for {file_path}")

        # Chunk and embed files
        embedding_service = await self._ensure_embedding_service()

        # Collect all chunks across files for batch processing
        all_file_chunks = []  # List of (file_path, file_hash, chunks, metadatas)

        for file_path in files_needing_work:
            content = self.documents[file_path]
            file_hash = self._compute_file_hash(file_path)

            chunks = self.chunker.chunk_document(content, file_path)

            # Skip files with no chunks (too small or no content)
            if not chunks:
                print(f"  → {file_path}: 0 chunks (skipping - file too small)")
                continue

            chunk_texts = []
            chunk_metadatas = []

            for chunk in chunks:
                chunk_texts.append(chunk.content)
                chunk_metadatas.append({
                    "file_path": file_path,
                    "file_hash": file_hash,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char
                })

            all_file_chunks.append((file_path, file_hash, chunk_texts, chunk_metadatas))
            print(f"  → {file_path}: {len(chunks)} chunks")

        # If no files have chunks, we're done
        if not all_file_chunks:
            print("  ⚠️ No files generated chunks (all files too small)")
            self.active_file_paths = list(self.documents.keys())
            self._initialized = True
            return

        # Flatten for batch embedding
        all_chunks = []
        chunk_to_file_map = []  # Track which file each chunk belongs to

        for file_idx, (file_path, file_hash, chunk_texts, chunk_metadatas) in enumerate(all_file_chunks):
            for chunk_text in chunk_texts:
                all_chunks.append(chunk_text)
                chunk_to_file_map.append(file_idx)

        print(f"  → Total: {len(all_chunks)} chunks across {len(all_file_chunks)} files")

        # Batch process embeddings with token-aware batching
        max_batch_items = 128
        max_batch_tokens = 60_000
        all_embeddings = []

        current_batch = []
        current_batch_tokens = 0
        batch_num = 0

        for i, chunk in enumerate(all_chunks):
            file_idx = chunk_to_file_map[i]
            _, _, _, metadatas = all_file_chunks[file_idx]
            # Find the chunk metadata for this chunk within its file
            chunk_idx_in_file = sum(1 for j in range(i) if chunk_to_file_map[j] == file_idx)
            chunk_tokens = metadatas[chunk_idx_in_file]["token_count"]

            would_exceed_items = len(current_batch) >= max_batch_items
            would_exceed_tokens = current_batch_tokens + chunk_tokens > max_batch_tokens

            if current_batch and (would_exceed_items or would_exceed_tokens):
                batch_num += 1
                print(f"  → Batch {batch_num}: {len(current_batch)} chunks ({current_batch_tokens:,} tokens)...")
                result = await embedding_service.embed_texts(current_batch, input_type="document")
                all_embeddings.extend(result.embeddings)
                print(f"  ✓ Batch {batch_num} complete")

                import asyncio
                await asyncio.sleep(3)

                current_batch = [chunk]
                current_batch_tokens = chunk_tokens
            else:
                current_batch.append(chunk)
                current_batch_tokens += chunk_tokens

        # Final batch
        if current_batch:
            batch_num += 1
            print(f"  → Final batch {batch_num}: {len(current_batch)} chunks ({current_batch_tokens:,} tokens)...")
            result = await embedding_service.embed_texts(current_batch, input_type="document")
            all_embeddings.extend(result.embeddings)
            print(f"  ✓ Final batch {batch_num} complete")

        # Store embeddings per file
        embedding_idx = 0
        for file_path, file_hash, chunk_texts, chunk_metadatas in all_file_chunks:
            file_embeddings = all_embeddings[embedding_idx:embedding_idx + len(chunk_texts)]

            self.vector_store.store_file_chunks(
                base_path=base_path_str,
                file_path=file_path,
                file_hash=file_hash,
                chunks=chunk_texts,
                embeddings=file_embeddings,
                metadatas=chunk_metadatas
            )

            embedding_idx += len(chunk_texts)
            print(f"  ✓ Stored {len(chunk_texts)} chunks for {file_path}")

        # Set active file paths for query filtering
        self.active_file_paths = list(self.documents.keys())
        self._initialized = True
        print(f"✓ RAG embeddings ready ({len(self.documents)} files, {len(all_chunks)} total chunks)")

    async def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """Search documents using semantic similarity.

        Args:
            query: Natural language search query
            top_k: Number of results to return (default: use instance default)

        Returns:
            List of SearchResult objects, sorted by relevance

        Raises:
            RuntimeError: If RAG not initialized (call initialize() first)

        Example:
            >>> results = await rag.search("How do I authenticate?", top_k=3)
            >>> for result in results:
            ...     print(f"{result.metadata['file_path']} ({result.score:.2f})")
            ...     print(result.content)
        """
        if not self._initialized:
            raise RuntimeError("RAG not initialized. Call initialize() first.")

        if not self.active_file_paths:
            return []

        # Generate query embedding
        embedding_service = await self._ensure_embedding_service()
        query_embedding = await embedding_service.embed_single(
            query,
            input_type="query"
        )

        # Search vector store with file filtering
        base_path_str = str(self.base_path.resolve())
        k = top_k if top_k is not None else self.top_k

        results = self.vector_store.search(
            base_path=base_path_str,
            query_embedding=query_embedding,
            file_paths=self.active_file_paths,
            top_k=k
        )

        return results

    async def close(self):
        """Clean up resources (close embedding service)."""
        if self._embedding_service:
            await self._embedding_service.close()
