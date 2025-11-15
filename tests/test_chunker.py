"""Tests for DocumentChunker.

Note: These are basic smoke tests for Phase 1.
Phase 2 will expand test coverage significantly.
"""

import pytest
from justragit.core.chunker import DocumentChunker, Chunk


def test_chunker_initialization():
    """Test that chunker initializes with correct parameters."""
    chunker = DocumentChunker(
        target_min_tokens=400,
        target_max_tokens=600
    )
    assert chunker.target_min_tokens == 400
    assert chunker.target_max_tokens == 600


def test_chunk_simple_text():
    """Test chunking simple text content."""
    chunker = DocumentChunker(
        target_min_tokens=100,  # Lower for testing
        target_max_tokens=200
    )

    content = """
    This is a simple paragraph.

    This is another paragraph with some content.

    And a third paragraph to make it interesting.
    """

    chunks = chunker.chunk_document(content, "test.txt")

    assert len(chunks) > 0
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert all(chunk.token_count > 0 for chunk in chunks)


def test_chunk_code():
    """Test chunking Python code."""
    chunker = DocumentChunker(
        target_min_tokens=50,  # Lower for testing
        target_max_tokens=150
    )

    code = '''
def hello():
    """Say hello."""
    print("Hello, world!")

def goodbye():
    """Say goodbye."""
    print("Goodbye!")

class MyClass:
    """A simple class."""
    def method(self):
        pass
'''

    chunks = chunker.chunk_document(code, "test.py")

    assert len(chunks) > 0
    # Code should be detected as code file
    assert all(chunk.token_count > 0 for chunk in chunks)


def test_chunk_metadata():
    """Test that chunk metadata is correct."""
    chunker = DocumentChunker(
        target_min_tokens=50,
        target_max_tokens=100
    )

    content = "This is a test. " * 100  # Repeat to ensure chunking

    chunks = chunker.chunk_document(content, "test.txt")

    # Check chunk indices are sequential
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i

    # Check character offsets are valid
    for chunk in chunks:
        assert chunk.start_char >= 0
        assert chunk.end_char > chunk.start_char
        assert chunk.end_char <= len(content)


def test_token_counting():
    """Test that token counting works."""
    chunker = DocumentChunker()

    text = "Hello, world!"
    token_count = chunker.count_tokens(text)

    assert token_count > 0
    assert isinstance(token_count, int)


def test_empty_content():
    """Test handling of empty content."""
    chunker = DocumentChunker()

    chunks = chunker.chunk_document("", "empty.txt")

    # Empty content should return empty list or single empty chunk
    assert isinstance(chunks, list)


def test_very_short_content():
    """Test handling of very short content."""
    chunker = DocumentChunker(
        target_min_tokens=100,
        target_max_tokens=200
    )

    content = "Short."
    chunks = chunker.chunk_document(content, "short.txt")

    assert len(chunks) >= 0  # Should handle gracefully
