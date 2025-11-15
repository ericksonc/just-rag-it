# Just RAG It 🚀

**Zero-ceremony RAG. Bring your docs, get semantic search in 3 lines.**

Extracted from [Chimera](https://github.com/yourusername/chimera) and battle-tested in production.

---

## Why?

Most RAG libraries are either bloated (LangChain) or too basic. Just RAG It hits the sweet spot:

| Feature | Just RAG It | LangChain | LlamaIndex | Simple Wrappers |
|---------|-------------|-----------|------------|-----------------|
| **Setup** | 3 lines | 30+ lines | Medium | 1 line |
| **Weight** | Lightweight | Heavy | Medium | Minimal |
| **Incremental** | File-hash smart | Manual | Good | None |
| **Production** | Built-in patterns | Complex | Moderate | DIY |

---

## Install

```bash
pip install justragit
export VOYAGE_API_KEY="your-key"  # Get at voyageai.com
```

Python 3.10+ required.

---

## Quickstart

```python
import asyncio
from justragit import RAG

async def main():
    # 1. Point to docs
    rag = RAG(
        base_path="/path/to/docs",
        whitelist=["**/*.md", "**/*.py"],
        blacklist=["*/archive/"]
    )

    # 2. Build index (incremental by default)
    await rag.initialize()

    # 3. Search
    results = await rag.search("How do I authenticate?", top_k=5)

    for r in results:
        print(f"{r.metadata['file_path']} ({r.score:.2f})\n{r.content}\n")

asyncio.run(main())
```

That's it. No config files, no boilerplate, no surprises.

---

## Features in Action

### Smart Incremental Updates
```python
await rag.initialize()  # First run: embeds everything
await rag.initialize()  # Second run: only changed files
```

### YAML Persistence
```yaml
# my-docs.yaml
base_path: "/project"
whitelist: ["docs/", "**/*.py"]
blacklist: ["*/tests/*"]
chunk_min_tokens: 400
chunk_max_tokens: 600
```

```python
rag = RAG.from_yaml("my-docs.yaml")
```

### Code + Natural Language
```python
# Handles functions, classes, paragraphs intelligently
# Targets ~500 tokens/chunk, respects boundaries
```

---

## What You Get

- **Context-aware chunking** - Splits code and prose intelligently (400-600 tokens, configurable)
- **File-hash tracking** - Zero API waste on unchanged files
- **Gitignore-aware** - Respects `.gitignore` automatically
- **Production patterns** - Batching, rate limiting, error handling built-in
- **Provider-agnostic** - Voyage AI today, OpenAI/Cohere/local tomorrow (Phase 2)
- **ChromaDB backend** - Persistent, queryable, per-file metadata

---

## Advanced Patterns

### Batch Config
Embeddings auto-batch: 128 items max, 60K tokens max, 3s between batches.

### Programmatic Filtering
```python
rag = RAG(
    base_path="./project",
    whitelist=["core/**/*.py", "docs/*.md", "README.md"],
    blacklist=["*/archive/*", "*/tests/*", "*/__pycache__/*"],
    max_file_size=2_000_000  # 2MB limit
)
```

### Environment
```bash
VOYAGE_API_KEY=""        # Required
CHROMADB_DIR=""          # Optional: custom Chroma path
```

---

## Architecture

```
RAG (API)
├── FileDiscovery (whitelist/blacklist/gitignore)
├── DocumentChunker (tiktoken, context-aware)
├── VoyageEmbeddingService (async, batched)
└── VectorStore (ChromaDB, file-hash indexed)
```

---

## Roadmap

**✅ Phase 1 (Now)**: MVP extracted from Chimera - core features, Voyage AI, incremental updates, YAML config

**🚧 Phase 2 (Next)**: Multi-provider (OpenAI, Cohere, local), rich CLI, cookbook, progress bars

**🔮 Phase 3 (Future)**: Pluggable chunking, hybrid search (BM25), cross-encoder re-ranking, metrics

---

## Development & Contributing

```bash
git clone https://github.com/yourusername/justragit
cd justragit
pip install -e ".[dev]"
pytest                    # Run tests
black justragit/ && ruff justragit/  # Format/lint
```

**Help wanted**: Additional providers, specialized chunking (Tree-sitter), CLI polish, performance.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License & Support

MIT License. [GitHub Issues](https://github.com/yourusername/justragit/issues) for bugs, Discussions for Q&A.

**Built by developers tired of over-engineered RAG.**
