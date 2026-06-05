"""
Keyword Learning Storage for Bookfix Choices.

Manages context keywords that help disambiguate heteronyms.
Learns from user corrections and AI extraction.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime

from ..logging import log_message


@dataclass
class ContextKeyword:
    """A single context keyword for a pronunciation."""

    word: str  # The keyword itself (e.g., "door")
    confidence: float  # 0.0-1.0 confidence score
    learned_from: int  # Number of corrections that reinforced this
    contradictions: int  # Times seen with OTHER pronunciations
    manual: bool  # True if added by user, False if AI-learned
    first_seen: str  # ISO timestamp
    last_seen: str  # ISO timestamp

    def reinforce(self):
        """Reinforce this keyword (seen again with same pronunciation)."""
        self.learned_from += 1
        self.last_seen = datetime.now().isoformat()

        # Increase confidence (cap at 0.95 for learned, 0.98 for manual)
        max_conf = 0.98 if self.manual else 0.95
        self.confidence = min(max_conf, self.confidence + 0.05)

    def contradict(self):
        """Mark contradiction (seen with different pronunciation)."""
        self.contradictions += 1
        self.last_seen = datetime.now().isoformat()

        # Decrease confidence
        if not self.manual:  # Don't penalize manual keywords
            self.confidence = max(0.40, self.confidence - 0.10)


class KeywordLearningStorage:
    """Manages storage and retrieval of context keywords."""

    def __init__(self, storage_dir: str = None):
        """Initialize keyword learning storage."""
        if storage_dir is None:
            # Default to .ai_learning directory
            from pathlib import Path

            app_dir = Path(__file__).parent.parent.parent
            storage_dir = app_dir / ".ai_learning"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.keywords_file = self.storage_dir / "context_keywords.json"

        # Structure: {word: {pronunciation: [ContextKeyword, ...]}}
        self.keywords: Dict[str, Dict[str, List[ContextKeyword]]] = {}

        self._load_keywords()

    def _load_keywords(self):
        """Load keywords from file."""
        if not self.keywords_file.exists():
            log_message("No existing context keywords file, starting fresh")
            return

        try:
            with open(self.keywords_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for word, pronunciations in data.items():
                self.keywords[word] = {}
                for pronunciation, keyword_list in pronunciations.items():
                    self.keywords[word][pronunciation] = [
                        ContextKeyword(**kw) for kw in keyword_list
                    ]

            total_keywords = sum(
                len(kw_list)
                for pron_dict in self.keywords.values()
                for kw_list in pron_dict.values()
            )
            log_message(
                f"Loaded {total_keywords} context keywords for {len(self.keywords)} words"
            )

        except Exception as e:
            log_message(f"Error loading context keywords: {e}", level="ERROR")
            self.keywords = {}

    def _save_keywords(self):
        """Save keywords to file."""
        try:
            # Convert to serializable format
            data = {}
            for word, pronunciations in self.keywords.items():
                data[word] = {}
                for pronunciation, keyword_list in pronunciations.items():
                    data[word][pronunciation] = [asdict(kw) for kw in keyword_list]

            with open(self.keywords_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            log_message(f"Saved context keywords to {self.keywords_file}")

        except Exception as e:
            log_message(f"Error saving context keywords: {e}", level="ERROR")

    def add_keywords(
        self,
        word: str,
        pronunciation: str,
        keywords: List[str],
        manual: bool = False,
        description: str = "",
    ):
        """
        Add or reinforce keywords for a word/pronunciation pair.

        Args:
            word: The heteronym (e.g., "close")
            pronunciation: The pronunciation (e.g., "klohz")
            keywords: List of keyword strings to add
            manual: True if user-added, False if AI-learned
            description: Optional description for logging
        """
        word_lower = word.lower()
        pronunciation_lower = pronunciation.lower()

        # Initialize structure if needed
        if word_lower not in self.keywords:
            self.keywords[word_lower] = {}
        if pronunciation_lower not in self.keywords[word_lower]:
            self.keywords[word_lower][pronunciation_lower] = []

        existing_keywords = {
            kw.word: kw for kw in self.keywords[word_lower][pronunciation_lower]
        }

        for keyword in keywords:
            keyword_lower = keyword.lower()

            if keyword_lower in existing_keywords:
                # Reinforce existing keyword
                existing_keywords[keyword_lower].reinforce()
                log_message(
                    f"Reinforced keyword '{keyword}' for {word}→{pronunciation} "
                    f"(confidence: {existing_keywords[keyword_lower].confidence:.2f})"
                )
            else:
                # Add new keyword
                base_confidence = 0.95 if manual else 0.60
                new_keyword = ContextKeyword(
                    word=keyword_lower,
                    confidence=base_confidence,
                    learned_from=1,
                    contradictions=0,
                    manual=manual,
                    first_seen=datetime.now().isoformat(),
                    last_seen=datetime.now().isoformat(),
                )
                self.keywords[word_lower][pronunciation_lower].append(new_keyword)
                log_message(
                    f"Added keyword '{keyword}' for {word}→{pronunciation} "
                    f"(manual={manual}, confidence: {base_confidence:.2f})"
                )

            # Check for contradictions (keyword appears with other pronunciations)
            self._check_contradictions(word_lower, pronunciation_lower, keyword_lower)

        self._save_keywords()

    def _check_contradictions(
        self, word: str, correct_pronunciation: str, keyword: str
    ):
        """Check if keyword appears with other pronunciations (contradiction)."""
        if word not in self.keywords:
            return

        for pronunciation, keyword_list in self.keywords[word].items():
            if pronunciation == correct_pronunciation:
                continue  # Skip the correct pronunciation

            # Check if this keyword exists in other pronunciation
            for kw in keyword_list:
                if kw.word == keyword:
                    # Contradiction found!
                    kw.contradict()
                    log_message(
                        f"⚠ Keyword '{keyword}' appears with multiple pronunciations "
                        f"of '{word}' - reduced confidence to {kw.confidence:.2f}"
                    )

    def remove_keyword(self, word: str, pronunciation: str, keyword: str):
        """Remove a keyword associated with a word and its pronunciation.
        Args:
        word (str): The original word.
        pronunciation (str): The pronunciation of the word.
        keyword (str): The keyword to remove.
        Returns:
        None
        """
        """Remove a keyword."""
        word_lower = word.lower()
        pronunciation_lower = pronunciation.lower()
        keyword_lower = keyword.lower()

        if word_lower not in self.keywords:
            return
        if pronunciation_lower not in self.keywords[word_lower]:
            return

        # Remove keyword from list
        self.keywords[word_lower][pronunciation_lower] = [
            kw
            for kw in self.keywords[word_lower][pronunciation_lower]
            if kw.word != keyword_lower
        ]

        log_message(f"Removed keyword '{keyword}' from {word}→{pronunciation}")
        self._save_keywords()

    def get_keywords(
        self, word: str, pronunciation: str, min_confidence: float = 0.70
    ) -> List[ContextKeyword]:
        """
        Get keywords for a word/pronunciation pair.

        Args:
            word: The heteronym
            pronunciation: The pronunciation
            min_confidence: Minimum confidence threshold (default: 0.70)

        Returns:
            List of ContextKeyword objects with confidence >= min_confidence
        """
        word_lower = word.lower()
        pronunciation_lower = pronunciation.lower()

        if word_lower not in self.keywords:
            return []
        if pronunciation_lower not in self.keywords[word_lower]:
            return []

        # Return keywords above confidence threshold, sorted by confidence
        keywords = [
            kw
            for kw in self.keywords[word_lower][pronunciation_lower]
            if kw.confidence >= min_confidence
        ]

        return sorted(keywords, key=lambda k: k.confidence, reverse=True)

    def get_all_keywords(self, word: str, pronunciation: str) -> List[ContextKeyword]:
        """Get ALL keywords for a word/pronunciation (no confidence filter)."""
        word_lower = word.lower()
        pronunciation_lower = pronunciation.lower()

        if word_lower not in self.keywords:
            return []
        if pronunciation_lower not in self.keywords[word_lower]:
            return []

        # Return all keywords, sorted by confidence
        return sorted(
            self.keywords[word_lower][pronunciation_lower],
            key=lambda k: k.confidence,
            reverse=True,
        )

    def get_stats(self) -> Dict:
        """Get statistics about learned keywords."""
        total_words = len(self.keywords)
        total_keywords = 0
        manual_keywords = 0
        high_conf_keywords = 0

        for word, pronunciations in self.keywords.items():
            for pronunciation, keyword_list in pronunciations.items():
                total_keywords += len(keyword_list)
                manual_keywords += sum(1 for kw in keyword_list if kw.manual)
                high_conf_keywords += sum(
                    1 for kw in keyword_list if kw.confidence >= 0.85
                )

        return {
            "total_words": total_words,
            "total_keywords": total_keywords,
            "manual_keywords": manual_keywords,
            "learned_keywords": total_keywords - manual_keywords,
            "high_confidence_keywords": high_conf_keywords,
        }


# Global singleton
_keyword_storage = None


def get_keyword_storage() -> KeywordLearningStorage:
    """
    Get global keyword storage instance (singleton).

    Returns:
        Shared KeywordLearningStorage instance
    """
    global _keyword_storage
    if _keyword_storage is None:
        _keyword_storage = KeywordLearningStorage()
    return _keyword_storage
