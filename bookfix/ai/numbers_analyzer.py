"""
Numbers Learning Analyzer - Extracts patterns from number formatting decisions.

Analyzes user corrections to learn context patterns, keywords, and
classification preferences over time.
"""

from typing import Dict, List, Tuple
import re

from ..logging import log_message
from .numbers_learning import NumbersLearningStorage, get_numbers_learning


class NumbersLearningAnalyzer:
    """Analyzes number formatting learning data to extract patterns."""

    def __init__(self, learning_storage: NumbersLearningStorage = None):
        """Initialize the analyzer."""
        self.learning = learning_storage or get_numbers_learning()

    def analyze_all_entries(self) -> Dict:
        """
        Analyze all learning entries to extract patterns.

        Returns:
            Dictionary with pattern analysis results
        """
        if not self.learning.entries:
            log_message("No learning entries to analyze")
            return {}

        # Extract context keywords from entries
        keyword_patterns = self._extract_context_keywords()

        # Extract grammatical patterns
        grammatical_patterns = self._extract_grammatical_patterns()

        # Extract number range patterns
        range_patterns = self._extract_number_range_patterns()

        analysis = {
            "total_entries": len(self.learning.entries),
            "context_keywords": keyword_patterns,
            "grammatical_patterns": grammatical_patterns,
            "range_patterns": range_patterns,
        }

        log_message(f"Analyzed {len(self.learning.entries)} number entries")
        return analysis

    def _extract_context_keywords(self) -> List[Dict]:
        """Extract keywords that appear before numbers and their effect."""
        keyword_map: Dict[str, Dict] = {}  # keyword -> {classification -> count}

        for entry in self.learning.entries:
            # Look for capitalized words in context_before (likely nouns)
            words = re.findall(r"\b([A-Z][a-z]*)\b", entry.context_before)

            for word in words:
                word_lower = word.lower()

                if word_lower not in keyword_map:
                    keyword_map[word_lower] = {}

                classification = entry.corrected_classification
                if classification not in keyword_map[word_lower]:
                    keyword_map[word_lower][classification] = 0

                keyword_map[word_lower][classification] += 1

        # Convert to pattern format
        patterns = []
        for keyword, classifications in keyword_map.items():
            # Get the most common classification for this keyword
            most_common = max(classifications.items(), key=lambda x: x[1])
            preferred_classification = most_common[0]
            count = most_common[1]
            confidence = min(0.95, 0.5 + (count * 0.1))  # Build confidence with usage

            patterns.append(
                {
                    "keyword": keyword,
                    "preferred_classification": preferred_classification,
                    "usage_count": count,
                    "confidence": confidence,
                }
            )

        # Sort by usage count
        patterns.sort(key=lambda x: x["usage_count"], reverse=True)

        if patterns:
            log_message(f"Extracted {len(patterns)} context keywords: {patterns[:5]}")

        return patterns

    def _extract_grammatical_patterns(self) -> List[Dict]:
        """Extract grammatical patterns (word + number combinations)."""
        patterns: Dict[str, int] = {}  # pattern -> count

        for entry in self.learning.entries:
            # Look for capitalized word immediately before number
            # Pattern: "[Capitalized Word] [number]"
            match = re.search(r"\b([A-Z][a-z]*)\s*$", entry.context_before)

            if match:
                word = match.group(1).lower()
                pattern = f"{word}_number"
                patterns[pattern] = patterns.get(pattern, 0) + 1

        # Convert to analysis format
        results = []
        for pattern, count in sorted(
            patterns.items(), key=lambda x: x[1], reverse=True
        ):
            results.append(
                {
                    "pattern": pattern,
                    "usage_count": count,
                    "preferred_classification": "quantity",  # Capitalized word + number usually means quantity
                }
            )

        if results:
            log_message(f"Extracted {len(results)} grammatical patterns")

        return results

    def _extract_number_range_patterns(self) -> List[Dict]:
        """Extract patterns based on number ranges and their typical classifications."""
        range_map: Dict[str, Dict] = {}

        for entry in self.learning.entries:
            try:
                num = int(entry.original_number)

                # Categorize by range
                if 0 <= num <= 59:
                    range_key = "0-59_minutes_seconds"
                elif 60 <= num <= 2359:
                    range_key = "60-2359_time_or_count"
                elif 2360 <= num <= 9999:
                    range_key = "2360-9999_building_levels"
                else:
                    range_key = "10000+_large_numbers"

                if range_key not in range_map:
                    range_map[range_key] = {}

                classification = entry.corrected_classification
                if classification not in range_map[range_key]:
                    range_map[range_key][classification] = 0

                range_map[range_key][classification] += 1

            except ValueError:
                # Skip non-numeric entries
                continue

        # Convert to pattern format
        results = []
        for range_key, classifications in range_map.items():
            most_common = max(classifications.items(), key=lambda x: x[1])
            preferred_classification = most_common[0]
            count = sum(classifications.values())

            results.append(
                {
                    "range": range_key,
                    "preferred_classification": preferred_classification,
                    "usage_count": count,
                }
            )

        if results:
            log_message(f"Extracted {len(results)} number range patterns")

        return results

    def learn_from_correction(
        self,
        original_number: str,
        context_before: str,
        context_after: str,
        original_classification: str,
        user_correction: str,
        corrected_classification: str,
        line_number: int,
    ) -> None:
        """
        Learn from a user correction and update patterns.

        This is called when user corrects a number's formatting.

        NOTE: 'unknown' classifications are never learned because they're not meaningful.
        """
        # Don't learn 'unknown' classifications - they're fallback defaults, not useful patterns
        if corrected_classification == "unknown":
            log_message(
                f"Skipping learning for 'unknown' classification: '{original_number}' → '{user_correction}'"
            )
            return

        # Add to learning entries
        self.learning.add_entry(
            original_number,
            context_before,
            context_after,
            original_classification,
            user_correction,
            corrected_classification,
            line_number,
        )

        # Save updated learning data
        self.learning.save_all()

        log_message(
            f"Learned from correction: '{original_number}' → '{user_correction}' "
            + f"({original_classification} → {corrected_classification})"
        )
