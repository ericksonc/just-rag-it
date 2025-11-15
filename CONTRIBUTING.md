# Contributing to Just RAG It

Thank you for your interest in contributing! This is an early-stage project with lots of room for improvement.

## Areas We'd Love Help With

- **Embedding Providers**: Add support for OpenAI, Cohere, HuggingFace, local models
- **Chunking Strategies**: Markdown-aware, Tree-sitter for code, custom delimiters
- **CLI Experience**: Beautiful output with `rich`, progress bars, interactive mode
- **Documentation**: More examples, cookbook recipes, tutorials
- **Performance**: Optimizations for large document sets
- **Testing**: Expand test coverage

## Development Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/justragit
cd justragit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black justragit/
ruff justragit/
```

## Code Style

We use:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking (gradual typing, not strict)
- **Pytest** for testing

Before submitting a PR:

```bash
# Format
black justragit/

# Lint
ruff justragit/

# Type check
mypy justragit/

# Test
pytest
```

## Project Structure

```
justragit/
├── core/              # Core components
│   ├── chunker.py     # Document chunking
│   ├── embeddings.py  # Embedding service
│   ├── vector_store.py  # ChromaDB wrapper
│   └── file_discovery.py  # File loading
├── providers/         # Embedding providers (Phase 2)
├── api.py            # High-level RAG API
└── config.py         # YAML configuration
```

## Testing

We use pytest with async support:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=justragit --cov-report=html

# Run specific test file
pytest tests/test_chunker.py

# Run specific test
pytest tests/test_chunker.py::test_chunk_code
```

## Pull Request Process

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** with clear, focused commits
3. **Add tests** for new functionality
4. **Update documentation** (README, docstrings, examples)
5. **Run the test suite** and ensure it passes
6. **Format your code** (black, ruff)
7. **Submit a PR** with a clear description

### PR Title Format

Use conventional commits:
- `feat: Add OpenAI embedding provider`
- `fix: Handle empty documents in chunker`
- `docs: Add FastAPI integration example`
- `test: Add tests for file discovery`
- `refactor: Extract provider protocol`

## Adding a New Embedding Provider

Create a new file in `justragit/providers/`:

```python
# providers/openai.py
from typing import List
import openai
from .base import EmbeddingProvider, EmbeddingResult

class OpenAIProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model

    async def embed_texts(self, texts: List[str]) -> EmbeddingResult:
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        embeddings = [item.embedding for item in response.data]
        return EmbeddingResult(
            embeddings=embeddings,
            model=self.model,
            total_tokens=response.usage.total_tokens
        )

    async def embed_single(self, text: str) -> List[float]:
        result = await self.embed_texts([text])
        return result.embeddings[0]

    @property
    def dimension(self) -> int:
        return 1536  # text-embedding-3-small
```

## Questions?

- Open an [issue](https://github.com/yourusername/justragit/issues)
- Start a [discussion](https://github.com/yourusername/justragit/discussions)
- Email: your.email@example.com

## Code of Conduct

Be kind, respectful, and constructive. We're all here to build something useful together.
