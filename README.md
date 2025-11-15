# Just RAG It 🚀  
**Zero-ceremony semantic search over your docs.**

---

## TL;DR  
```bash
pip install justragit
export VOYAGE_API_KEY=your_key
```

```python
from justragit import RAG
rag = RAG("docs/", whitelist=["**/*.md", "**/*.pdf"])
await rag.initialize()
results = await rag.search("thing i want to search for")
```

Done.
Incremental updates, smart chunking, PDF support, gitignore respect, and production-grade error handling are all baked in.

---

## Install
```bash
pip install justragit          # PyPI
# or
pip install -e .               # repo
```
Python ≥3.10, `VOYAGE_API_KEY` env var.

---

## One-file script
```python
import asyncio, justragit as jr

async def main():
    r = jr.RAG("src/", whitelist=["**/*.py"])
    await r.initialize()
    for hit in await r.search("auth middleware"):
        print(hit.metadata['file_path'], hit.score, hit.content[:200])

asyncio.run(main())
```

---

## YAML for reuse
```yaml
# my-docs.yaml
base_path: ./docs
whitelist: ["**/*.md"]
top_k: 5
```
```python
rag = RAG.from_yaml("my-docs.yaml")
```

---

## knobs you’ll actually touch
| param | default | what it does |
|-------|---------|--------------|
| `chunk_min_tokens` | 400 | smallest chunk |
| `chunk_max_tokens` | 600 | largest chunk |
| `top_k` | 5 | hits per query |
| `max_file_size` | 1 MB | skip big blobs |
| `respect_gitignore` | True | honour `.gitignore` |

---

## how it works
1. **Discover** – whitelist/blacklist + gitignore
2. **Chunk** – code-aware, tiktoken-counted
3. **Hash** – per-file, skip unchanged
4. **Embed** – Voyage AI (batched, rate-limited)
5. **Store** – ChromaDB on disk
6. **Search** – cosine similarity, return top-k

### supported file types
- **Code**: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rs`, etc.
- **Docs**: `.md`, `.txt`, `.rst`
- **Data**: `.json`, `.yaml`, `.toml`, `.xml`
- **PDFs**: `.pdf` (text extraction via pypdf)

---

## roadmap (PRs welcome)
Phase 2 – OpenAI/Cohere/local providers, rich CLI  
Phase 3 – BM25 hybrid, re-rankers, metrics

---

## licence
MIT