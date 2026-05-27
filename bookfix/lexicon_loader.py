"""
LexiconLoader for BookFix Homograph Engine.

Loads and validates the choices.json lexicon file.
Provides access to homograph definitions, options, and metadata.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class LexiconLoader:
    """
    Loads and manages the homograph lexicon from choices.json.

    Provides validated access to homograph definitions, POS tags,
    examples, and context keywords for the scoring engine.
    """

    def __init__(self, lexicon_path: Optional[str] = None):
        """
        Initialize the lexicon loader.

        Args:
            lexicon_path: Path to choices.json. If None, uses default data/choices.json
        """
        if lexicon_path is None:
            # Default to data/choices.json relative to the project root
            project_root = Path(__file__).parent.parent
            lexicon_path = project_root / "data" / "choices.json"

        self.lexicon_path = Path(lexicon_path)
        self.lexicon_data: Dict[str, Any] = {}
        self._load_lexicon()

    def _load_lexicon(self) -> None:
        """Load and validate the lexicon file."""
        if not self.lexicon_path.exists():
            raise FileNotFoundError(f"Lexicon file not found: {self.lexicon_path}")

        try:
            with open(self.lexicon_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate structure
            if not isinstance(data, list):
                raise ValueError("Lexicon must be a list of homograph entries")

            # Convert to dict keyed by word (lowercase for case-insensitive lookup)
            for entry in data:
                if not isinstance(entry, dict) or 'word' not in entry:
                    raise ValueError(f"Invalid entry format: {entry}")

                word_key = entry['word'].lower()
                self.lexicon_data[word_key] = entry

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in lexicon file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading lexicon: {e}")

    def get_homograph(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Get the homograph entry for a word.

        Args:
            word: The homograph word (case-insensitive)

        Returns:
            Dict with word, options, etc., or None if not found
        """
        return self.lexicon_data.get(word.lower())

    def get_options(self, word: str) -> List[Dict[str, Any]]:
        """
        Get the pronunciation options for a word.

        Args:
            word: The homograph word

        Returns:
            List of option dicts with spelling, definition, pos, etc.
        """
        entry = self.get_homograph(word)
        return entry.get('options', []) if entry else []

    def has_word(self, word: str) -> bool:
        """Check if a word exists in the lexicon."""
        return word.lower() in self.lexicon_data

    def get_all_words(self) -> List[str]:
        """Get list of all homograph words in the lexicon."""
        return list(self.lexicon_data.keys())

    def reload(self) -> None:
        """Reload the lexicon from disk."""
        self.lexicon_data.clear()
        self._load_lexicon()