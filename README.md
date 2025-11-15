# Just RAG It 🚀

**Zero-ceremony RAG for your documents.**

A lightweight, production-ready RAG (Retrieval-Augmented Generation) library that lets you bring your documents and "just RAG it" - no complex setup, no heavy dependencies, just semantic search that works.

Extracted from the [Chimera Multi-Agent System](https://github.com/yourusername/chimera) and battle-tested in production.

---

## Why Just RAG It?

**Most RAG libraries are either too complex or too basic.** Just RAG It sits in the sweet spot:

- **Zero Ceremony**: 3 lines of code to working RAG
- **Production Ready**: Error handling, batching, incremental updates built-in
- **Smart Incremental Updates**: Per-file hashing means only changed files get re-embedded
- **Provider Agnostic**: Start with Voyage AI, swap to OpenAI/Cohere/local later (Phase 2)
- **Developer First**: Built by developers who use RAG daily

### vs LangChain
- 100x simpler (3 lines vs 30)
- Focused on one use case, done well
- No hidden abstractions

### vs LlamaIndex
- Lighter weight
- Better incremental updates
- Simpler mental model

### vs Simple Wrappers
- Production patterns built-in
- Incremental updates via file hashing
- Smart chunking strategies

---

## Installation

```bash
pip install justragit
```

Or from source:

```bash
git clone https://github.com/yourusername/justragit
cd justragit
pip install -e .
```

### Requirements

- Python 3.10+
- Voyage AI API key (set `VOYAGE_API_KEY` environment variable)
  - Get one at [voyageai.com](https://www.voyageai.com/)

---

## Quickstart (5 Minutes)

```python
import asyncio
from justragit import RAG

async def main():
    # 1. Create RAG instance
    rag = RAG(
        base_path="/path/to/your/docs",
        whitelist=["**/*.md", "**/*.py"],
        blacklist=["*/archive/"]
    )

    # 2. Initialize (discover files, generate embeddings)
    await rag.initialize()

    # 3. Search!
    results = await rag.search("How do I authenticate?", top_k=5)

    # 4. Use results
    for result in results:
        print(f"{result.metadata['file_path']} ({result.score:.2f})")
        print(result.content)
        print()

asyncio.run(main())
```

**That's it!** You're now doing semantic search over your documents.

---

## Features

### 🎯 Smart Chunking

- Context-aware splitting (respects functions, classes, paragraphs)
- Handles both code and natural language
- Target: 400-600 tokens per chunk (configurable)
- Uses `tiktoken` for accurate token counting

### 🔄 Incremental Updates

Per-file hash tracking means:
- Unchanged files reuse existing embeddings (fast!)
- Only changed files get re-embedded
- No wasted API calls
- Perfect for large codebases

```python
# First run: embeds all files
await rag.initialize()

# Later: only changed files are re-embedded
await rag.initialize()
```

### 🎨 YAML Configuration

Save your collection config and reuse it:

```yaml
# collections/my-docs.yaml
name: "My Documentation"
description: "Project docs and guides"
base_path: "/path/to/project"
whitelist_paths:
  - "docs/"
  - "**/*.md"
blacklist_paths:
  - "*/archive/"
chunk_min_tokens: 400
chunk_max_tokens: 600
top_k: 5
```

```python
from justragit import RAG

rag = RAG.from_yaml("collections/my-docs.yaml")
await rag.initialize()
results = await rag.search("authentication")
```

### 📁 Smart File Discovery

- Whitelist/blacklist pattern matching
- Automatic `.gitignore` support
- Binary file detection
- Size limits (skip files > 1MB by default)
- Common exclusions built-in (node_modules, __pycache__, etc.)

### 🗄️ ChromaDB Vector Store

- Persistent storage on disk
- Per-file hash tracking
- Global collections (share embeddings across runs)
- Query-time filtering
- Automatic cleanup of old collections

---

## Examples

### Search Documentation

```python
from justragit import RAG

rag = RAG(
    base_path="./docs",
    whitelist=["**/*.md"],
    top_k=3
)

await rag.initialize()
results = await rag.search("How do I deploy?")

for r in results:
    print(f"📄 {r.metadata['file_path']} (relevance: {r.score:.2f})")
    print(r.content)
    print()
```

### Search Codebase

```python
rag = RAG(
    base_path="./src",
    whitelist=["**/*.py", "**/*.js"],
    blacklist=["*/tests/", "*/__pycache__/"]
)

await rag.initialize()
results = await rag.search("authentication middleware")
```

### Custom Configuration

```python
rag = RAG(
    base_path="/path/to/project",
    whitelist=["src/", "docs/"],
    blacklist=["*/archive/"],
    chunk_min_tokens=300,  # Smaller chunks
    chunk_max_tokens=500,
    top_k=10,  # More results
    respect_gitignore=True,
    max_file_size=2_000_000  # 2MB limit
)
```

---

## Advanced Usage

### Batch Processing

Embeddings are automatically batched with token-aware limits:
- Max 128 items per batch
- Max 60,000 tokens per batch
- Automatic rate limiting (3s between batches)

### Programmatic File Filtering

```python
from justragit import RAG

rag = RAG(
    base_path="./project",
    whitelist=[
        "core/**/*.py",      # All Python in core/
        "docs/*.md",         # Top-level docs
        "README.md"          # Specific file
    ],
    blacklist=[
        "*/archive/*",       # Archived files
        "*/tests/*",         # Test files
        "*/__pycache__/*"    # Python cache
    ]
)
```

### Environment Variables

```bash
# Voyage AI API key (required)
export VOYAGE_API_KEY="your-api-key-here"

# Optional: Custom ChromaDB directory
export CHROMADB_DIR="/path/to/chromadb"
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              RAG (High-level API)            │
└─────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌────────┐ ┌────────────┐
│FileDiscovery │ │Chunker │ │VectorStore │
└──────────────┘ └────────┘ └────────────┘
        │            │            │
        ▼            ▼            ▼
   Whitelist/   Tiktoken     ChromaDB
   Blacklist   (Tokens)   (Embeddings)
   Gitignore

        ┌────────────┐
        │ Embeddings │
        └────────────┘
             │
             ▼
        Voyage AI
      (voyage-3-large)
```

### Components

- **FileDiscovery**: Pattern-based file discovery with gitignore support
- **DocumentChunker**: Context-aware chunking (code + natural language)
- **VoyageEmbeddingService**: Async embedding generation via Voyage AI
- **VectorStore**: ChromaDB-based vector storage with incremental updates
- **RAG**: High-level API that ties it all together

---

## Roadmap

### ✅ Phase 1 (Current - MVP)
- [x] Core components extracted from Chimera
- [x] Voyage AI embeddings
- [x] Incremental updates via file hashing
- [x] YAML configuration
- [x] Basic Python API
- [x] Examples and documentation

### 🚧 Phase 2 (Production Ready)
- [ ] Multi-provider support (OpenAI, Cohere, local)
- [ ] Rich CLI experience
- [ ] Cookbook with common recipes
- [ ] Advanced file discovery patterns
- [ ] Progress bars and better UX

### 🔮 Phase 3 (Advanced)
- [ ] Pluggable chunking strategies
- [ ] Hybrid search (semantic + keyword BM25)
- [ ] Re-ranking with cross-encoders
- [ ] Monitoring and metrics

---

## Development

### Setup

```bash
# Clone repo
git clone https://github.com/yourusername/justragit
cd justragit

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black justragit/
ruff justragit/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=justragit

# Run specific test
pytest tests/test_chunker.py
```

---

## Contributing

Contributions welcome! This is an early-stage project with lots of room for improvement.

**Areas we'd love help with**:
- Additional embedding providers (OpenAI, Cohere, local)
- Specialized chunking strategies (Markdown, Tree-sitter)
- CLI improvements
- Documentation and examples
- Performance optimizations

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Acknowledgments

Extracted from the [Chimera Multi-Agent System](https://github.com/yourusername/chimera), where it's been battle-tested in production.

Built with:
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Voyage AI](https://www.voyageai.com/) - Embeddings
- [tiktoken](https://github.com/openai/tiktoken) - Tokenization

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/justragit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/justragit/discussions)
- **Email**: your.email@example.com

---

**Made with ❤️ by developers who got tired of complex RAG libraries.**
