#!/usr/bin/env python3
"""Quickstart example for Just RAG It.

This demonstrates the simplest possible usage:
1. Create a RAG instance
2. Initialize (discover files, generate embeddings)
3. Search

Run this after installing: pip install justragit
"""

import asyncio
from justragit import RAG


async def main():
    """5-minute quickstart example."""

    # Create RAG instance
    # Note: Set VOYAGE_API_KEY environment variable first
    rag = RAG(
        base_path="/path/to/your/docs",  # Change this to your directory
        whitelist=["**/*.md", "**/*.py"],  # File patterns to include
        blacklist=["*/archive/"],  # Patterns to exclude
        top_k=5  # Number of results to return
    )

    # Initialize: discover files and generate embeddings
    print("Initializing RAG system...")
    await rag.initialize()

    # Search
    print("\nSearching for 'authentication'...")
    results = await rag.search("authentication")

    # Display results
    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        file_path = result.metadata.get("file_path", "unknown")
        chunk_idx = result.chunk_index
        score = result.score

        print(f"{'=' * 80}")
        print(f"Result {i} | {file_path}:{chunk_idx} | Score: {score:.3f}")
        print(f"{'=' * 80}")
        print(result.content)
        print()

    # Clean up
    await rag.close()


if __name__ == "__main__":
    asyncio.run(main())
