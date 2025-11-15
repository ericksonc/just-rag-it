"""Configuration management for Just RAG It.

Handles YAML-based collection configuration, similar to Chimera's
cli/rag/collections/ pattern.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class CollectionConfig:
    """Configuration for a RAG collection.

    This mirrors the YAML format used in Chimera's RAG CLI.

    Example YAML:
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
    """

    name: str
    description: str
    base_path: str
    whitelist_paths: list[str]
    blacklist_paths: list[str]
    chunk_min_tokens: int = 400
    chunk_max_tokens: int = 600
    top_k: int = 5
    respect_gitignore: bool = True
    max_file_size: int = 1_000_000  # 1MB

    @classmethod
    def from_yaml(cls, path: str) -> 'CollectionConfig':
        """Load collection configuration from YAML file.

        Args:
            path: Path to YAML config file

        Returns:
            CollectionConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)

        # Required fields
        required = ['name', 'description', 'base_path', 'whitelist_paths']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return cls(
            name=data['name'],
            description=data['description'],
            base_path=data['base_path'],
            whitelist_paths=data['whitelist_paths'],
            blacklist_paths=data.get('blacklist_paths', []),
            chunk_min_tokens=data.get('chunk_min_tokens', 400),
            chunk_max_tokens=data.get('chunk_max_tokens', 600),
            top_k=data.get('top_k', 5),
            respect_gitignore=data.get('respect_gitignore', True),
            max_file_size=data.get('max_file_size', 1_000_000)
        )

    def to_yaml(self, path: str) -> None:
        """Save collection configuration to YAML file.

        Args:
            path: Path to save YAML config file
        """
        data = {
            'name': self.name,
            'description': self.description,
            'base_path': self.base_path,
            'whitelist_paths': self.whitelist_paths,
            'blacklist_paths': self.blacklist_paths,
            'chunk_min_tokens': self.chunk_min_tokens,
            'chunk_max_tokens': self.chunk_max_tokens,
            'top_k': self.top_k,
            'respect_gitignore': self.respect_gitignore,
            'max_file_size': self.max_file_size,
        }

        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
