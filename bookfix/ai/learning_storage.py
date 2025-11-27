"""
AI Learning Data Storage for Bookfix Caps Processing.

Stores user decisions and extracted patterns to improve AI suggestions over time.
Cross-AI compatible format that survives model changes.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from ..logging import log_message


@dataclass
class LearningEntry:
    """Single learning entry capturing user decision."""

    timestamp: str
    original_word: str
    context_before: str  # 30 chars before
    context_after: str  # 30 chars after
    sentence_position: str  # "start", "middle", "end"
    user_action: str  # "lower", "lower_all", "skip", "ignore_all", "add"
    final_result: str  # What the word became
    line_number: int  # Line in document

    @classmethod
    def create(
        cls,
        original_word: str,
        context_before: str,
        context_after: str,
        sentence_position: str,
        user_action: str,
        final_result: str,
        line_number: int,
    ) -> "LearningEntry":
        """Create a new learning entry with current timestamp."""
        return cls(
            timestamp=datetime.now().isoformat(),
            original_word=original_word,
            context_before=context_before,
            context_after=context_after,
            sentence_position=sentence_position,
            user_action=user_action,
            final_result=final_result,
            line_number=line_number,
        )


@dataclass
class LearnedPattern:
    """Extracted pattern from user behavior."""

    pattern_type: str  # "word_exact", "word_prefix", "context_pattern"
    pattern_value: str  # The actual pattern
    preferred_action: str  # What user typically does
    confidence: float  # 0.0 to 1.0 based on consistency
    usage_count: int  # How many times this pattern was observed
    last_used: str  # Last timestamp this pattern was reinforced

    def update_usage(self, action: str) -> None:
        """Update pattern usage and confidence."""
        self.usage_count += 1
        self.last_used = datetime.now().isoformat()

        if action == self.preferred_action:
            # Reinforcement - increase confidence
            self.confidence = min(0.95, self.confidence + 0.05)
        else:
            # Contradiction - decrease confidence
            self.confidence = max(0.1, self.confidence - 0.1)


class LearningStorage:
    """Manages storage and retrieval of AI learning data."""

    def __init__(self, storage_dir: str = None):
        """Initialize learning storage."""
        if storage_dir is None:
            # Default to main app directory
            app_dir = Path(__file__).parent.parent.parent
            storage_dir = app_dir / ".ai_learning"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.entries_file = self.storage_dir / "caps_learning.json"
        self.patterns_file = self.storage_dir / "caps_patterns.json"

        # Load existing data
        self.entries: List[LearningEntry] = self._load_entries()
        self.patterns: List[LearnedPattern] = self._load_patterns()

    def _load_entries(self) -> List[LearningEntry]:
        """Load learning entries from file."""
        if not self.entries_file.exists():
            return []

        try:
            with open(self.entries_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            entries = []
            for entry_dict in data.get("entries", []):
                entries.append(LearningEntry(**entry_dict))

            log_message(f"Loaded {len(entries)} learning entries")
            return entries

        except Exception as e:
            log_message(f"Error loading learning entries: {e}", level="ERROR")
            return []

    def _load_patterns(self) -> List[LearnedPattern]:
        """Load learned patterns from file."""
        if not self.patterns_file.exists():
            return []

        try:
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            patterns = []
            for pattern_dict in data.get("patterns", []):
                patterns.append(LearnedPattern(**pattern_dict))

            log_message(f"Loaded {len(patterns)} learned patterns")
            return patterns

        except Exception as e:
            log_message(f"Error loading learned patterns: {e}", level="ERROR")
            return []

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

            log_message(f"Saved {len(self.entries)} learning entries")

        except Exception as e:
            log_message(f"Error saving learning entries: {e}", level="ERROR")

    def save_patterns(self) -> None:
        """Save learned patterns to file."""
        try:
            data = {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "patterns": [asdict(pattern) for pattern in self.patterns],
            }

            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            log_message(f"Saved {len(self.patterns)} learned patterns")

        except Exception as e:
            log_message(f"Error saving learned patterns: {e}", level="ERROR")

    def add_learning_entry(self, entry: LearningEntry) -> None:
        """Add a new learning entry."""
        self.entries.append(entry)
        log_message(
            f"Added learning entry: {entry.original_word} -> {entry.user_action}"
        )

    def get_patterns_for_word(
        self, word: str, context_before: str = "", context_after: str = ""
    ) -> List[LearnedPattern]:
        """Get relevant patterns for a word and context."""
        relevant_patterns = []

        for pattern in self.patterns:
            if pattern.pattern_type == "word_exact" and pattern.pattern_value == word:
                relevant_patterns.append(pattern)
            elif pattern.pattern_type == "word_prefix" and word.startswith(
                pattern.pattern_value
            ):
                relevant_patterns.append(pattern)
            elif pattern.pattern_type == "context_pattern":
                # Simple context matching - could be made more sophisticated
                full_context = context_before + " " + word + " " + context_after
                if pattern.pattern_value.lower() in full_context.lower():
                    relevant_patterns.append(pattern)

        # Sort by confidence and usage
        relevant_patterns.sort(
            key=lambda p: (p.confidence, p.usage_count), reverse=True
        )
        return relevant_patterns

    def get_best_suggestion(
        self, word: str, context_before: str = "", context_after: str = ""
    ) -> Optional[Tuple[str, float]]:
        """Get best action suggestion for a word based on learned patterns."""
        patterns = self.get_patterns_for_word(word, context_before, context_after)

        if not patterns:
            return None

        best_pattern = patterns[0]
        if best_pattern.confidence > 0.5:  # Minimum confidence threshold
            return (best_pattern.preferred_action, best_pattern.confidence)

        return None

    def get_learning_stats(self) -> Dict:
        """Get statistics about learning data."""
        return {
            "total_entries": len(self.entries),
            "total_patterns": len(self.patterns),
            "high_confidence_patterns": len(
                [p for p in self.patterns if p.confidence > 0.8]
            ),
            "recent_entries": len(
                [
                    e
                    for e in self.entries
                    if datetime.fromisoformat(e.timestamp)
                    > datetime.now().replace(day=datetime.now().day - 7)
                ]
            ),
            "storage_location": str(self.storage_dir),
        }
