"""File discovery and loading for RAG.

This module handles discovering and loading text files based on patterns,
with support for gitignore, whitelists, and blacklists.

Extracted from Chimera's RAGWidget with improvements for standalone use.
"""

from pathlib import Path
from typing import Optional
import fnmatch
import mimetypes
import pathspec


class FileDiscovery:
    """Discover and load text files matching specified patterns.

    Features:
    - Whitelist/blacklist pattern matching
    - Gitignore support via pathspec
    - Smart text file detection
    - Automatic binary file skipping
    - Size limits (default: skip files > 1MB)

    Example:
        >>> discovery = FileDiscovery(
        ...     base_path="/path/to/project",
        ...     whitelist_paths=["docs/", "**/*.md"],
        ...     blacklist_paths=["*/archive/"]
        ... )
        >>> documents = discovery.discover()
        >>> print(f"Found {len(documents)} files")
    """

    def __init__(
        self,
        base_path: str,
        whitelist_paths: list[str],
        blacklist_paths: list[str] | None = None,
        respect_gitignore: bool = True,
        max_file_size: int = 1_000_000,  # 1MB default
    ):
        """Initialize file discovery.

        Args:
            base_path: Base directory to search from
            whitelist_paths: Patterns to include (e.g., "docs/", "**/*.py")
            blacklist_paths: Patterns to exclude (e.g., "*/archive/")
            respect_gitignore: If True, respect .gitignore files
            max_file_size: Maximum file size in bytes (default: 1MB)
        """
        self.base_path = Path(base_path)
        self.whitelist_paths = whitelist_paths
        self.blacklist_paths = blacklist_paths or []
        self.respect_gitignore = respect_gitignore
        self.max_file_size = max_file_size

        # Load .gitignore if it exists and respect_gitignore is True
        self._gitignore_spec: Optional[pathspec.PathSpec] = None
        if self.respect_gitignore:
            gitignore_path = self.base_path / '.gitignore'
            if gitignore_path.exists():
                try:
                    with open(gitignore_path, 'r') as f:
                        self._gitignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', f)
                except Exception as e:
                    print(f"⚠️ Could not load .gitignore: {e}")

    def discover(self) -> dict[str, str]:
        """Discover and load all matching files.

        Returns:
            Dict mapping relative_path -> file_content
        """
        documents: dict[str, str] = {}

        for pattern in self.whitelist_paths:
            if pattern.endswith('/'):
                # Directory pattern - get all files recursively
                search_path = self.base_path / pattern.rstrip('/')
                if search_path.exists() and search_path.is_dir():
                    for file_path in search_path.rglob('*'):
                        if file_path.is_file():
                            self._load_file_if_not_excluded(file_path, documents)
            else:
                # Glob pattern
                for file_path in self.base_path.glob(pattern):
                    if file_path.is_file():
                        self._load_file_if_not_excluded(file_path, documents)

        return documents

    def _load_file_if_not_excluded(self, file_path: Path, documents: dict[str, str]) -> None:
        """Load file if it passes all filters.

        Args:
            file_path: Absolute path to file
            documents: Dict to add file content to
        """
        try:
            rel_path = file_path.relative_to(self.base_path)
        except ValueError:
            return

        # Skip hidden files/directories
        if any(part.startswith('.') for part in rel_path.parts):
            return

        # Check gitignore
        rel_path_str = str(rel_path)
        if self._gitignore_spec and self._gitignore_spec.match_file(rel_path_str):
            return

        # Check blacklist
        for exclude_pattern in self.blacklist_paths:
            if fnmatch.fnmatch(rel_path_str, exclude_pattern):
                return

        # Check if text file
        if not self._is_text_file(file_path):
            return

        # Load the file
        try:
            # Handle PDF files with special extraction
            if file_path.suffix.lower() == '.pdf':
                from .pdf_extractor import extract_text_from_pdf
                content = extract_text_from_pdf(file_path)
            else:
                # Standard text file reading
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            documents[rel_path_str] = content

        except (UnicodeDecodeError, Exception) as e:
            # Skip files that can't be read
            print(f"⚠️ Could not load {rel_path_str}: {e}")

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file.

        Uses multiple heuristics:
        1. File size check (skip if > max_file_size)
        2. Common text file extensions
        3. Common text file names (Dockerfile, Makefile, etc.)
        4. MIME type detection

        Args:
            file_path: Path to file

        Returns:
            True if file appears to be a text file
        """
        # Skip files > max_file_size
        if file_path.exists() and file_path.stat().st_size > self.max_file_size:
            return False

        # Common text file extensions
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.sh',
            '.html', '.css', '.xml', '.svg',
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env',
            '.md', '.rst', '.txt',
            '.dockerfile', '.makefile', '.sql',
            '.pdf',
        }

        # Check common filenames without extensions
        filename = file_path.name.lower()
        if filename in {'dockerfile', 'makefile', 'readme', 'license', 'changelog'}:
            return True

        # Check extension
        if file_path.suffix.lower() in text_extensions:
            return True

        # Fallback to mime type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type and mime_type.startswith('text/')
