"""
AI Learning Pattern Analyzer for Bookfix.

Analyzes user decisions to extract patterns and improve AI suggestions.
"""

import re
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from .learning_storage import LearningEntry, LearnedPattern, LearningStorage
from ..logging import log_message


class LearningAnalyzer:
    """Analyzes user behavior to extract patterns for better AI suggestions."""

    def __init__(self, storage: LearningStorage):
        """Initialize with learning storage."""
        self.storage = storage
        self.min_pattern_count = 3  # Minimum occurrences to create a pattern
        self.min_confidence = 0.6  # Minimum confidence to suggest pattern

    def analyze_and_update_patterns(self) -> None:
        """Analyze all learning entries and update patterns."""
        log_message("Starting pattern analysis...")

        # Clear existing patterns for fresh analysis
        self.storage.patterns.clear()

        # Extract different types of patterns
        self._extract_exact_word_patterns()
        self._extract_prefix_patterns()
        self._extract_context_patterns()

        # Save updated patterns
        self.storage.save_patterns()

        log_message(
            f"Pattern analysis complete. Generated {len(self.storage.patterns)} patterns"
        )

    def _extract_exact_word_patterns(self) -> None:
        """Extract patterns for exact word matches."""
        word_actions = defaultdict(list)

        # Group actions by word
        for entry in self.storage.entries:
            word_actions[entry.original_word].append(entry.user_action)

        # Create patterns for words with consistent behavior
        for word, actions in word_actions.items():
            if len(actions) >= self.min_pattern_count:
                action_counts = Counter(actions)
                most_common_action, count = action_counts.most_common(1)[0]
                confidence = count / len(actions)

                if confidence >= self.min_confidence:
                    pattern = LearnedPattern(
                        pattern_type="word_exact",
                        pattern_value=word,
                        preferred_action=most_common_action,
                        confidence=confidence,
                        usage_count=len(actions),
                        last_used=datetime.now().isoformat(),
                    )
                    self.storage.patterns.append(pattern)
                    log_message(
                        f"Created exact word pattern: {word} -> {most_common_action} ({confidence:.2f})"
                    )

    def _extract_prefix_patterns(self) -> None:
        """Extract patterns for word prefixes (e.g., Dr., Mr., etc.)."""
        prefix_actions = defaultdict(list)

        # Look for common prefixes
        common_prefixes = ["DR", "MR", "MS", "PROF", "GEN", "COL", "LT", "SGT", "CAPT"]

        for entry in self.storage.entries:
            word = entry.original_word
            for prefix in common_prefixes:
                if word.startswith(prefix) and len(word) > len(prefix):
                    prefix_actions[prefix].append(entry.user_action)

        # Create patterns for prefixes with consistent behavior
        for prefix, actions in prefix_actions.items():
            if len(actions) >= self.min_pattern_count:
                action_counts = Counter(actions)
                most_common_action, count = action_counts.most_common(1)[0]
                confidence = count / len(actions)

                if confidence >= self.min_confidence:
                    pattern = LearnedPattern(
                        pattern_type="word_prefix",
                        pattern_value=prefix,
                        preferred_action=most_common_action,
                        confidence=confidence,
                        usage_count=len(actions),
                        last_used=datetime.now().isoformat(),
                    )
                    self.storage.patterns.append(pattern)
                    log_message(
                        f"Created prefix pattern: {prefix}* -> {most_common_action} ({confidence:.2f})"
                    )

    def _extract_context_patterns(self) -> None:
        """Extract patterns based on context around words."""
        context_actions = defaultdict(list)

        # Look for context patterns
        for entry in self.storage.entries:
            contexts = []

            # Before context patterns
            before = entry.context_before.strip().lower()
            if before:
                # Look for common words that precede caps
                before_words = before.split()
                if before_words:
                    last_word = before_words[-1]
                    if last_word in [
                        "the",
                        "dr.",
                        "mr.",
                        "ms.",
                        "prof.",
                        "general",
                        "colonel",
                    ]:
                        contexts.append(f"after_{last_word}")

            # After context patterns
            after = entry.context_after.strip().lower()
            if after:
                after_words = after.split()
                if after_words:
                    first_word = after_words[0]
                    if first_word in ["said", "announced", "declared", "stated"]:
                        contexts.append(f"before_{first_word}")

            # Position patterns
            if entry.sentence_position == "start":
                contexts.append("sentence_start")
            elif entry.sentence_position == "end":
                contexts.append("sentence_end")

            # Add actions for each context
            for context in contexts:
                context_actions[context].append(entry.user_action)

        # Create patterns for contexts with consistent behavior
        for context, actions in context_actions.items():
            if len(actions) >= self.min_pattern_count:
                action_counts = Counter(actions)
                most_common_action, count = action_counts.most_common(1)[0]
                confidence = count / len(actions)

                if confidence >= self.min_confidence:
                    pattern = LearnedPattern(
                        pattern_type="context_pattern",
                        pattern_value=context,
                        preferred_action=most_common_action,
                        confidence=confidence,
                        usage_count=len(actions),
                        last_used=datetime.now().isoformat(),
                    )
                    self.storage.patterns.append(pattern)
                    log_message(
                        f"Created context pattern: {context} -> {most_common_action} ({confidence:.2f})"
                    )

    def get_suggestion_for_word(
        self,
        word: str,
        context_before: str = "",
        context_after: str = "",
        sentence_position: str = "middle",
    ) -> Optional[Dict]:
        """Get AI suggestion for a word based on learned patterns."""
        suggestions = []

        # Check exact word patterns
        for pattern in self.storage.patterns:
            if pattern.pattern_type == "word_exact" and pattern.pattern_value == word:
                suggestions.append(
                    {
                        "action": pattern.preferred_action,
                        "confidence": pattern.confidence,
                        "reason": f"Exact match (used {pattern.usage_count} times)",
                        "pattern_type": "word_exact",
                    }
                )

        # Check prefix patterns
        for pattern in self.storage.patterns:
            if pattern.pattern_type == "word_prefix" and word.startswith(
                pattern.pattern_value
            ):
                suggestions.append(
                    {
                        "action": pattern.preferred_action,
                        "confidence": pattern.confidence
                        * 0.8,  # Slightly lower confidence for prefix
                        "reason": f"Prefix match '{pattern.pattern_value}*' (used {pattern.usage_count} times)",
                        "pattern_type": "word_prefix",
                    }
                )

        # Check context patterns
        contexts_to_check = []

        # Before context
        before = context_before.strip().lower()
        if before:
            before_words = before.split()
            if before_words:
                last_word = before_words[-1]
                contexts_to_check.append(f"after_{last_word}")

        # After context
        after = context_after.strip().lower()
        if after:
            after_words = after.split()
            if after_words:
                first_word = after_words[0]
                contexts_to_check.append(f"before_{first_word}")

        # Position context
        if sentence_position == "start":
            contexts_to_check.append("sentence_start")
        elif sentence_position == "end":
            contexts_to_check.append("sentence_end")

        for context in contexts_to_check:
            for pattern in self.storage.patterns:
                if (
                    pattern.pattern_type == "context_pattern"
                    and pattern.pattern_value == context
                ):
                    suggestions.append(
                        {
                            "action": pattern.preferred_action,
                            "confidence": pattern.confidence
                            * 0.7,  # Lower confidence for context
                            "reason": f"Context match '{context}' (used {pattern.usage_count} times)",
                            "pattern_type": "context_pattern",
                        }
                    )

        # Return best suggestion
        if suggestions:
            best = max(suggestions, key=lambda x: x["confidence"])
            if best["confidence"] > 0.5:  # Minimum threshold
                return best

        return None

    def add_user_decision(
        self,
        word: str,
        context_before: str,
        context_after: str,
        sentence_position: str,
        user_action: str,
        final_result: str,
        line_number: int,
    ) -> None:
        """Add a user decision and update patterns."""
        # Create learning entry
        entry = LearningEntry.create(
            original_word=word,
            context_before=context_before,
            context_after=context_after,
            sentence_position=sentence_position,
            user_action=user_action,
            final_result=final_result,
            line_number=line_number,
        )

        # Add to storage
        self.storage.add_learning_entry(entry)

        # Update existing patterns if they match
        self._update_existing_patterns(
            word, context_before, context_after, sentence_position, user_action
        )

        # Save entries
        self.storage.save_entries()

        log_message(f"Recorded user decision: {word} -> {user_action}")

    def _update_existing_patterns(
        self,
        word: str,
        context_before: str,
        context_after: str,
        sentence_position: str,
        user_action: str,
    ) -> None:
        """Update existing patterns with new user decision."""
        # Update exact word patterns
        for pattern in self.storage.patterns:
            if pattern.pattern_type == "word_exact" and pattern.pattern_value == word:
                pattern.update_usage(user_action)

        # Update prefix patterns
        for pattern in self.storage.patterns:
            if pattern.pattern_type == "word_prefix" and word.startswith(
                pattern.pattern_value
            ):
                pattern.update_usage(user_action)

        # Update context patterns
        contexts = []
        before = context_before.strip().lower()
        if before:
            before_words = before.split()
            if before_words:
                contexts.append(f"after_{before_words[-1]}")

        after = context_after.strip().lower()
        if after:
            after_words = after.split()
            if after_words:
                contexts.append(f"before_{after_words[0]}")

        if sentence_position == "start":
            contexts.append("sentence_start")
        elif sentence_position == "end":
            contexts.append("sentence_end")

        for context in contexts:
            for pattern in self.storage.patterns:
                if (
                    pattern.pattern_type == "context_pattern"
                    and pattern.pattern_value == context
                ):
                    pattern.update_usage(user_action)
