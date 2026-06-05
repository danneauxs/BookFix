"""
AI Learning Data Storage for Numbers Formatting.

Stores user decisions and extracted patterns to improve number formatting
suggestions over time. Uses boosted entries (user-taught patterns) with
context-specific keywords.
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from ..logging import log_message


@dataclass
class NumberLearningEntry:
    """Single learning entry capturing user decision on number formatting."""

    timestamp: str
    original_number: str
    context_before: str  # 50 chars before
    context_after: str  # 50 chars after
    original_classification: str  # What AI/rules classified it as
    user_correction: str  # What user changed it to
    corrected_classification: str  # What it should have been classified as
    line_number: int
    boost: bool = False  # True if user explicitly set type + keywords (high priority)
    context_keywords: List[str] = None  # Keywords user marked as relevant context

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.context_keywords is None:
            self.context_keywords = []

    @classmethod
    def create(
        cls,
        original_number: str,
        context_before: str,
        context_after: str,
        original_classification: str,
        user_correction: str,
        corrected_classification: str,
        line_number: int,
        boost: bool = False,
        context_keywords: List[str] = None,
    ) -> "NumberLearningEntry":
        """Create a new learning entry with current timestamp."""
        return cls(
            timestamp=datetime.now().isoformat(),
            original_number=original_number,
            context_before=context_before,
            context_after=context_after,
            original_classification=original_classification,
            user_correction=user_correction,
            corrected_classification=corrected_classification,
            line_number=line_number,
            boost=boost,
            context_keywords=context_keywords or [],
        )


class NumbersLearningStorage:
    """Manages storage and retrieval of number formatting learning data."""

    def __init__(self, storage_dir: str = None):
        """Initialize numbers learning storage."""
        if storage_dir is None:
            # Default to main app directory
            app_dir = Path(__file__).parent.parent.parent
            storage_dir = app_dir / ".ai_learning"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.entries_file = self.storage_dir / "numbers_learning.json"

        # Load existing data (boosted entries only - old keyword/pattern system deprecated)
        self.entries: List[NumberLearningEntry] = self._load_entries()

    def _load_entries(self) -> List[NumberLearningEntry]:
        """Load learning entries from file."""
        if not self.entries_file.exists():
            return []

        try:
            with open(self.entries_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            entries = []
            for entry_dict in data.get("entries", []):
                entries.append(NumberLearningEntry(**entry_dict))

            log_message(f"Loaded {len(entries)} number learning entries")
            return entries

        except Exception as e:
            log_message(f"Error loading number learning entries: {e}", level="ERROR")
            return []

    def add_entry(
        self,
        original_number: str,
        context_before: str,
        context_after: str,
        original_classification: str,
        user_correction: str,
        corrected_classification: str,
        line_number: int,
    ) -> None:
        """Add a learning entry from user correction."""
        entry = NumberLearningEntry.create(
            original_number,
            context_before,
            context_after,
            original_classification,
            user_correction,
            corrected_classification,
            line_number,
        )
        self.entries.append(entry)
        log_message(
            f"Added number learning entry: '{original_number}' should be '{corrected_classification}' not '{original_classification}'"
        )

    def add_boosted_entry(
        self,
        original_number: str,
        context_before: str,
        context_after: str,
        user_correction: str,
        corrected_classification: str,
        context_keywords: List[str] = None,
        line_number: int = 0,
    ) -> None:
        """
        Add a BOOSTED learning entry from explicit user specification.

        Used when user clicks on a number and explicitly:
        1. Selects type (measurement, year, identifier, quantity, etc.)
        2. Marks context keywords (degrees, etc.)

        Boosted entries have highest priority in learning hierarchy.
        """
        if context_keywords is None:
            context_keywords = []

        entry = NumberLearningEntry.create(
            original_number,
            context_before,
            context_after,
            original_classification="user_specified",
            user_correction=user_correction,
            corrected_classification=corrected_classification,
            line_number=line_number,
            boost=True,
            context_keywords=context_keywords,
        )
        self.entries.append(entry)
        log_message(
            f"Added BOOSTED number learning entry: '{original_number}' → '{corrected_classification}' "
            f"with keywords: {context_keywords}"
        )

    def get_learned_classification(
        self, number: str, context_before: str, context_after: str
    ) -> Optional[str]:
        """
        Get learned classification from boosted entries (user-taught patterns).

        Boosted entries are created when user explicitly sets type + context keywords.
        Only returns a classification if all context keywords from a boosted entry
        are found in the current context.

        Returns classification if a matching boosted entry is found, or None.
        Never returns 'unknown' classifications (those are not meaningful).
        """
        context = (context_before + " " + context_after).lower()

        # Check for boosted entries (user explicitly taught this)
        # These have highest priority because user manually specified them
        for entry in self.entries:
            if entry.boost and entry.corrected_classification != "unknown":
                # Check if keywords from this entry are in current context
                if entry.context_keywords:
                    for keyword in entry.context_keywords:
                        # Use word boundary matching to avoid substring false positives
                        if re.search(
                            r"\b" + re.escape(keyword.lower()) + r"\b", context
                        ):
                            log_message(
                                f"Using BOOSTED learned classification: '{entry.corrected_classification}' "
                                f"(keyword: '{keyword}')"
                            )
                            return entry.corrected_classification

        return None

    def save_all(self) -> None:
        """Save all learning data (boosted entries only)."""
        self.save_entries()

    def save_entries(self) -> None:
        """Save learning entries to file."""
        try:
            data = {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "entries": [asdict(entry) for entry in self.entries],
            }

            with open(self.entries_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            log_message(f"Saved {len(self.entries)} number learning entries")

        except Exception as e:
            log_message(f"Error saving number learning entries: {e}", level="ERROR")


# Global singleton for numbers learning
_numbers_learning = None


def get_numbers_learning() -> NumbersLearningStorage:
    """Get global numbers learning instance (singleton)."""
    global _numbers_learning
    if _numbers_learning is None:
        _numbers_learning = NumbersLearningStorage()
    return _numbers_learning


def reset_numbers_learning() -> None:
    """Reset the global numbers learning singleton and reload from file."""
    global _numbers_learning
    if _numbers_learning is not None:
        _numbers_learning = NumbersLearningStorage()
    else:
        _numbers_learning = NumbersLearningStorage()
    log_message("Numbers learning reset and reloaded from file")
