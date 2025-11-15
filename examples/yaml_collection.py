#!/usr/bin/env python3
"""Example: Using YAML collection configuration.

This demonstrates loading configuration from a YAML file,
similar to how Chimera's RAG CLI works.
"""

import asyncio
from justragit import RAG


async def main():
    """Load collection from YAML and search."""

    # Load from YAML file
    rag = RAG.from_yaml("collections/documentation.yaml")

    print("Initializing from YAML collection...")
    await rag.initialize()

    # Interactive search
    while True:
        query = input("\nEnter search query (or 'quit'): ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break

        if not query:
            continue

        results = await rag.search(query, top_k=3)

        if not results:
            print("No results found.")
            continue

        print(f"\n✓ Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            file_path = result.metadata.get("file_path", "unknown")
            score = result.score

            print(f"─" * 80)
            print(f"{i}. {file_path} (score: {score:.3f})")
            print(f"─" * 80)
            print(result.content[:200] + "..." if len(result.content) > 200 else result.content)
            print()

    await rag.close()
    print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
