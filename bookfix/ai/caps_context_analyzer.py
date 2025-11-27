"""
Context-based analysis for all-caps sequences.

Uses rule engine pattern with multiple weighted signals to determine
if a caps word is likely an acronym or regular word before asking AI.
"""

import re
from typing import Optional, Tuple, Callable, List
from ..logging import log_message

try:
    from .spacy_caps_scorer import SpacyCapsScorer

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    SpacyCapsScorer = None

try:
    from .learning_storage import LearningStorage

    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    LearningStorage = None


class Rule:
    """Represents a decision rule for caps analysis."""

    def __init__(self, name: str, func: Callable, confidence: float):
        """
        Initialize a rule.

        Args:
            name: Rule name for logging
            func: Function that returns (decision, reasoning) or None
            confidence: Base confidence score for this rule
        """
        self.name = name
        self.func = func
        self.confidence = confidence

    def check(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, float, str]]:
        """
        Execute the rule.

        Returns:
            Tuple of (decision, confidence, reasoning) or None if rule doesn't match
        """
        result = self.func(caps_word, context_before, context_after, upper_to_lower)
        if result:
            decision, reasoning = result
            return (decision, self.confidence, reasoning)
        return None


class CapsContextAnalyzer:
    """Analyzes context to determine caps word usage before AI using rule engine."""

    def __init__(self):
        """Initialize analyzer with rule engine and learning storage."""
        self.spacy_scorer = None
        if SPACY_AVAILABLE:
            try:
                self.spacy_scorer = SpacyCapsScorer()
            except Exception as e:
                log_message(f"WARNING: Could not initialize spaCy scorer: {e}")

        # Initialize learning storage
        self.learning_storage = None
        if LEARNING_AVAILABLE:
            try:
                self.learning_storage = LearningStorage()
            except Exception as e:
                log_message(f"WARNING: Could not initialize learning storage: {e}")

        # Build rule engine
        self.rules: List[Rule] = []
        self._build_rules()

    def _build_rules(self):
        """Build the rule engine with new 5-step architecture.

        Processing order:
        1. Manual overrides (upper_to_lower_list)
        2. Deterministic rules (compound_designation, roman_numerals, all_consonants)
        3. Learned patterns check
        4. Simple POS check (function words)
        5. AI fallback (handled in analyze() when no rule matches)
        """
        # Rules are checked in priority order
        self.rules = [
            # Step 1: Manual overrides
            Rule("upper_to_lower_list", self._rule_upper_to_lower, 1.0),
            # Step 2: Deterministic rules
            Rule("compound_designation", self._rule_compound_designation, 1.0),
            Rule("roman_numerals", self._rule_roman_numerals, 1.0),
            Rule("all_consonants", self._rule_all_consonants, 0.95),
            # Step 3: Learned patterns from user history
            Rule("learned_patterns", self._rule_learned_patterns, 0.90),
            # Step 4: Simple POS check (function words)
            Rule("simple_pos_check", self._rule_simple_pos_check, 0.85),
            # Step 5: Explanatory patterns (rare cases)
            Rule("explanatory_pattern", self._rule_explanatory, 0.90),
        ]

    def analyze(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, str]]:
        """
        Analyze context using rule engine.

        Args:
            caps_word: The all-caps word to analyze
            context_before: Text before the word
            context_after: Text after the word
            upper_to_lower: List of words that should always be lowercased (from .data.txt)

        Returns:
            Tuple of (decision, reasoning) where decision is 'keep', 'lowercase', or None (ambiguous)
            If None, caller should ask AI.
        """
        log_message(f"DEBUG: Analyzing '{caps_word}'")
        log_message(f"DEBUG:   Context before: '{context_before}'")
        log_message(f"DEBUG:   Context after:  '{context_after}'")

        # Execute rules in priority order (5-step architecture)
        for rule in self.rules:
            result = rule.check(
                caps_word, context_before, context_after, upper_to_lower
            )
            if result:
                decision, confidence, reasoning = result
                log_message(
                    f"DEBUG:   {rule.name} (conf: {confidence:.2f}): {decision} - {reasoning}"
                )
                return (decision, reasoning)

        # No rule matched - ambiguous case, send to AI (step 5)
        log_message(f"DEBUG:   No rule matched - ambiguous, sending to AI for decision")
        return None

    # Rule functions
    def _rule_upper_to_lower(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, str]]:
        """Check if explicitly in UPPER_TO_LOWER list from .data.txt"""
        if upper_to_lower and caps_word in upper_to_lower:
            reason = f"'{caps_word}' is in UPPER_TO_LOWER list (from .data.txt)"
            return ("lowercase", reason)
        return None

    def _rule_compound_designation(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, str]]:
        """Check for compound designations like UH-60, FA-18."""
        # Pattern: 2-3 caps letters followed by hyphen and digit(s)
        if 2 <= len(caps_word) <= 3:
            after_sample = context_after.lstrip()[:20] if context_after else ""
            # Check if followed by hyphen and digits (UH-60, FA-18, C-3PO)
            if re.match(r"^-\d+", after_sample):
                return (
                    "keep",
                    f"'{caps_word}' is part of designation pattern (e.g., {caps_word}-60)",
                )
        return None

    def _rule_roman_numerals(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, str]]:
        """Check for Roman numerals - always keep uppercase.

        Supports numerals from I to MMMCMXCIX (1 to 3999).
        """
        # Pattern for Roman numerals: M{0,3} (C{1,3}|CD|D?C{0,3}) (X{1,3}|XL|L?X{0,3}) (I{1,3}|IV|V?I{0,3})
        # Simplified: check if word matches common Roman numeral patterns
        if not caps_word:
            return None

        # Valid Roman numeral characters
        if not all(c in "IVXLCDM" for c in caps_word):
            return None

        # Check using regex pattern for valid Roman numerals
        roman_pattern = r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
        if re.match(roman_pattern, caps_word):
            return ("keep", f"'{caps_word}' is a Roman numeral - always keep uppercase")

        return None

    def _rule_all_consonants(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, str]]:
        """Check for all consonants - likely acronym."""
        vowel_count = sum(1 for c in caps_word if c in "AEIOUY")
        if vowel_count == 0 and len(caps_word) >= 2:
            return (
                "keep",
                f"'{caps_word}' is all consonants, likely acronym (FYI, FBI, etc.)",
            )
        return None

    def _rule_learned_patterns(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, str]]:
        """Check learned patterns from user history (step 3)."""
        if not self.learning_storage:
            return None

        try:
            suggestion = self.learning_storage.get_best_suggestion(
                caps_word, context_before, context_after
            )
            if suggestion:
                action, confidence = suggestion
                # Map learned actions to decisions
                if action in ("lower", "lower_all"):
                    decision = "lowercase"
                elif action in ("skip", "ignore_all"):
                    decision = "keep"
                else:
                    return None

                reason = (
                    f"'{caps_word}' matches learned pattern (conf: {confidence:.2f})"
                )
                return (decision, reason)
        except Exception as e:
            log_message(f"DEBUG: Learned patterns check failed for '{caps_word}': {e}")

        return None

    def _rule_simple_pos_check(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, str]]:
        """Check POS tags for function words (step 4).

        Uses spaCy POS tagging for ALL word lengths.
        Only makes decisions for function words (VERB, ADV, CONJ, INTJ, AUX, PRON, ADP, DET).
        For NOUN/PROPN, returns None to let AI decide (context matters).
        """
        if not self.spacy_scorer:
            return None

        try:
            score_result = self.spacy_scorer.score(
                caps_word, context_before, context_after
            )
            if not score_result:
                return None

            score, confidence, reasoning, pos_tag = score_result

            # Decision based on POS tag
            # Function words should be lowercase
            function_word_tags = {
                "VERB",
                "ADV",
                "CCONJ",
                "SCONJ",
                "INTJ",
                "AUX",
                "PRON",
                "ADP",
                "DET",
            }
            if pos_tag in function_word_tags:
                reason = (
                    f"'{caps_word}' is {pos_tag} (function word), should be lowercase"
                )
                return ("lowercase", reason)

            # For NOUN and PROPN, let AI decide (context matters)
            # Single letters are pronouns - lowercase
            if pos_tag == "PRON" or len(caps_word) == 1:
                return ("lowercase", f"'{caps_word}' is single letter or pronoun")

            # Everything else falls through to AI
            return None

        except Exception as e:
            log_message(f"DEBUG: POS check failed for '{caps_word}': {e}")
            return None

    def _rule_explanatory(
        self,
        caps_word: str,
        context_before: str,
        context_after: str,
        upper_to_lower: list = None,
    ) -> Optional[Tuple[str, str]]:
        """Check for explanatory patterns like 'PO Box', 'FBI director'."""
        if len(caps_word) > 6:
            return None  # Only for shorter words
        after_sample = context_after.lstrip()[:50]
        match = re.match(r"^([A-Z][a-z]+)", after_sample)
        if match:
            following_word = match.group(1).lower()
            if following_word in (
                "box",
                "director",
                "agent",
                "number",
                "code",
                "system",
                "office",
                "department",
                "agency",
                "official",
                "member",
            ):
                return (
                    "keep",
                    f"'{caps_word} {following_word}' pattern suggests valid acronym",
                )
        return None
