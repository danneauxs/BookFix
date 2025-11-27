"""
AI Learning Data Storage for Bookfix All-Caps Processing.

Stores user decisions for all-caps sequences to improve AI suggestions over time.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from ..logging import log_message


@dataclass
class CapsLearningEntry:
    """Single learning entry capturing user's caps sequence decision."""

    timestamp: str
    caps_word: str  # The all-caps word (e.g., "TCE")
    decision: str  # User's decision: "keep", "lowercase", "title"
    context_before: str  # 50 chars before
    context_after: str  # 50 chars after
    ai_suggestion: str  # What AI suggested
    line_number: int  # Line in document
    document: str = ""  # Optional: document name/path

    @classmethod
    def create(
        cls,
        caps_word: str,
        decision: str,
        context_before: str,
        context_after: str,
        ai_suggestion: str,
        line_number: int,
        document: str = "",
    ) -> "CapsLearningEntry":
        """Create a new learning entry with current timestamp."""
        return cls(
            timestamp=datetime.now().isoformat(),
            caps_word=caps_word,
            decision=decision,
            context_before=context_before,
            context_after=context_after,
            ai_suggestion=ai_suggestion,
            line_number=line_number,
            document=document,
        )


class CapsLearningStorage:
    """Manages storage and retrieval of caps learning data."""

    def __init__(self, storage_dir: str = None):
        """Initialize caps learning storage."""
        if storage_dir is None:
            # Default to main app directory
            app_dir = Path(__file__).parent.parent.parent
            storage_dir = app_dir / ".ai_learning"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.entries_file = self.storage_dir / "caps_learning.json"

        # Load existing data
        self.entries: List[CapsLearningEntry] = self._load_entries()

    def _load_entries(self) -> List[CapsLearningEntry]:
        """Load learning entries from disk with version migration support."""
        if not self.entries_file.exists():
            log_message(f"No caps learning file found at {self.entries_file}")
            return []

        try:
            with open(self.entries_file, "r") as f:
                data = json.load(f)

                # Handle version migration
                if isinstance(data, list):
                    # Old format (no version) - migrate to v1
                    log_message("Migrating old caps learning format to v1")
                    entries = [CapsLearningEntry(**entry) for entry in data]
                elif isinstance(data, dict) and data.get("version") == 1:
                    # New format v1
                    entries = [
                        CapsLearningEntry(**entry) for entry in data.get("entries", [])
                    ]
                else:
                    # Unknown format
                    log_message(
                        f"Unknown caps learning format version: {data.get('version')}",
                        level="WARNING",
                    )
                    return []

                log_message(f"Loaded {len(entries)} caps learning entries")
                return entries
        except Exception as e:
            log_message(f"Error loading caps learning entries: {e}", level="WARNING")
            return []

    def _save_entries(self) -> None:
        """Save learning entries to disk with version metadata."""
        try:
            with open(self.entries_file, "w") as f:
                data = {
                    "version": 1,
                    "entries": [asdict(entry) for entry in self.entries],
                }
                json.dump(data, f, indent=2)
                log_message(f"Saved {len(self.entries)} caps learning entries")
        except Exception as e:
            log_message(f"Error saving caps learning entries: {e}", level="WARNING")

    def save(self) -> None:
        """Save learning entries to disk (public interface)."""
        self._save_entries()

    def add_decision(
        self,
        caps_word: str,
        decision: str,
        context_before: str,
        context_after: str,
        ai_suggestion: str,
        line_number: int,
        document: str = "",
    ) -> None:
        """Record a user decision for learning."""
        entry = CapsLearningEntry.create(
            caps_word=caps_word,
            decision=decision,
            context_before=context_before,
            context_after=context_after,
            ai_suggestion=ai_suggestion,
            line_number=line_number,
            document=document,
        )
        self.entries.append(entry)
        self._save_entries()
        log_message(f"Recorded caps learning: {caps_word} → {decision}")

    def get_learned_decision(
        self, caps_word: str, context_before: str, context_after: str
    ) -> Optional[str]:
        """
        Find a learned decision for this caps word based on context similarity.

        Returns the most common user decision if found, None otherwise.
        """
        # Find all entries for this caps word
        word_entries = [e for e in self.entries if e.caps_word == caps_word]

        if not word_entries:
            return None

        # If all past decisions are the same, use that
        decisions = [e.decision for e in word_entries]
        if len(set(decisions)) == 1:
            decision = decisions[0]
            log_message(
                f"Using learned decision for '{caps_word}': {decision} (consistent)"
            )
            return decision

        # If mixed decisions, return the most common one
        from collections import Counter

        counter = Counter(decisions)
        most_common = counter.most_common(1)[0][0]
        log_message(
            f"Using learned decision for '{caps_word}': {most_common} ({counter[most_common]}/{len(decisions)} times)"
        )
        return most_common

    def get_stats(self) -> Dict:
        """Get statistics about learning data."""
        if not self.entries:
            return {"total_entries": 0, "unique_words": 0}

        unique_words = set(e.caps_word for e in self.entries)
        decisions = [e.decision for e in self.entries]

        from collections import Counter

        decision_counts = Counter(decisions)

        return {
            "total_entries": len(self.entries),
            "unique_words": len(unique_words),
            "decisions": dict(decision_counts),
            "last_updated": self.entries[-1].timestamp if self.entries else None,
        }
