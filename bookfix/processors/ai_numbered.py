"""
AI-Enhanced Numbered Line Processor for Bookfix.

Extends the NumberedLineProcessor with AI analysis capabilities
for intelligent number formatting decisions with change tracking.
"""

import re
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from num2words import num2words

if TYPE_CHECKING:
    from ..context import BookfixContext

from .numbered import NumberedLineProcessor
from ..ai.service import BookfixAIService
from ..ai.change_tracker import AIChangeTracker
from ..ai.numbers_learning import get_numbers_learning
from ..ai.pos_tagger import get_pos_tagger
from ..logging import log_message


class AINumberedLineProcessor(NumberedLineProcessor):
    """
    AI-enhanced numbered line processor that can intelligently format
    lines containing numbers based on context analysis.
    """

    def __init__(self, change_tracker: Optional[AIChangeTracker] = None):
        """Initializes a new instance of the class.
        Args:
        change_tracker (Optional[AIChangeTracker]): An optional AI change tracker for tracking changes.
        Returns:
        None
        """
        super().__init__()
        self.ai_service: Optional[BookfixAIService] = None
        self.ai_enabled = False
        self.confidence_threshold = 0.8
        self.fallback_to_manual = True

        # Change tracking
        self.change_tracker = change_tracker

        # Track AI decisions for review
        self.ai_decisions = []
        self.manual_decisions = []
        self.lines_processed = 0
        self.lines_modified = 0

        # Learning system for number formatting
        self.learning_storage = get_numbers_learning()

        # POS tagging for semantic context analysis
        # NOTE: Currently disabled - needs refinement to work as a confirmer/refiner rather than primary classifier
        # Set to False to disable POS-based pattern analysis
        self.use_pos_analysis = False
        self.pos_tagger = None
        if self.use_pos_analysis:
            try:
                self.pos_tagger = get_pos_tagger()
                log_message("POS tagger initialized for number classification")
            except Exception as e:
                log_message(f"Failed to initialize POS tagger: {e}", level="WARNING")
                self.pos_tagger = None

        # Log file for numbered analysis
        self.numbered_log_path = None

        # Flag to use rules-only mode (skip AI processing)
        self.rules_only_mode = False


    def initialize_ai(self, ai_config: Dict) -> bool:
        """
        Initialize AI service from configuration.

        Args:
            ai_config: Dictionary with AI configuration

        Returns:
            True if AI was successfully initialized
        """
        try:
            self.ai_enabled = ai_config.get("ai_enabled", False)

            if not self.ai_enabled:
                log_message("AI processing disabled in configuration")
                return False

            # Initialize AI service with full configuration.
            self.ai_service = BookfixAIService.from_config(ai_config)

            # Test AI connection
            test_result = self.ai_service.test_connection()
            if not test_result.success:
                log_message(
                    f"AI service connection failed: {test_result.error_message}",
                    level="WARNING",
                )
                # No fallback to manual if the model can't even load
                return False
            else:
                log_message(
                    f"AI service initialized successfully: {test_result.content}"
                )

            return True

        except Exception as e:
            log_message(f"Failed to initialize AI service: {e}", level="ERROR")
            self.ai_enabled = False
            return False

    def _analyze_text_context(self, text: str) -> Dict:
        """Analyze text to determine context (military, civilian, technical, etc.)."""

        # Keywords that indicate different contexts
        military_keywords = [
            "ship",
            "captain",
            "admiral",
            "fleet",
            "naval",
            "army",
            "marine",
            "base",
            "command",
            "orders",
            "mission",
            "deployment",
            "vessel",
            "bridge",
            "deck",
            "convoy",
            "regiment",
            "battalion",
            "squadron",
            "division",
            "corps",
            "soldier",
            "officer",
            "sergeant",
            "lieutenant",
            "colonel",
            "general",
            "major",
            "warrant",
            "enlisted",
        ]

        time_keywords = [
            "hours",
            "minutes",
            "o'clock",
            "am",
            "pm",
            "morning",
            "afternoon",
            "evening",
            "night",
            "dawn",
            "dusk",
            "midnight",
            "noon",
        ]

        date_keywords = [
            "year",
            "born",
            "since",
            "in",
            "during",
            "century",
            "decade",
            "era",
            "period",
        ]

        technical_keywords = [
            "model",
            "serial",
            "part",
            "version",
            "specification",
            "manual",
            "code",
            "identification",
            "number",
            "reference",
            "catalog",
        ]

        text_lower = text.lower()

        # Count keyword matches
        military_score = sum(1 for word in military_keywords if word in text_lower)
        time_score = sum(1 for word in time_keywords if word in text_lower)
        date_score = sum(1 for word in date_keywords if word in text_lower)
        technical_score = sum(1 for word in technical_keywords if word in text_lower)

        # Determine primary context
        scores = {
            "military": military_score,
            "time_focused": time_score,
            "date_focused": date_score,
            "technical": technical_score,
            "general": 1,  # baseline
        }

        primary_context = max(scores, key=scores.get)

        return {
            "primary_context": primary_context,
            "scores": scores,
            "is_military": military_score > 3,
            "has_time_focus": time_score > 2,
            "has_date_focus": date_score > 2,
            "is_technical": technical_score > 2,
        }

    def _find_all_numbers_for_ai(
        self, text: str
    ) -> List[Tuple[int, str, List[Tuple[int, int]]]]:
        """Find lines with numbers for AI analysis (more inclusive than base class)."""

        lines = text.splitlines()
        numbered_lines = []

        # Patterns: detect military time tokens first, then general numbers
        time_hhmm = re.compile(
            r"\b([01]\d|2[0-3])[0-5]\d\b"
        )  # 4-digit HHMM like 0800, 1430 (requires 2-digit hours)
        time_hh_col_mm = re.compile(
            r"\b([01]?\d|2[0-3]):[0-5]\d\b"
        )  # HH:MM like 08:00, 14:30
        time_with_hours = re.compile(
            r"\b((?:[01]?\d|2[0-3])[0-5]\d|(?:[01]?\d|2[0-3]):[0-5]\d)\s+hours\b",
            re.IGNORECASE,
        )
        # General numbers (keep modest breadth to avoid over-triggering on prose)
        number_pattern = re.compile(
            r"(?<![\w])"  # left boundary not word character (allow punctuation like dots before)
            r"(?:[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[+-]?\d{3,}(?:\.\d+)?)"  # Numbers with commas OR 3+ digits (both with optional decimals)
            r"(?:%|(?:st|nd|rd|th))?"  # optional percent or ordinal suffix
            r"(?![\w])"  # right boundary not word character (allow punctuation like dots after)
        )

        # Decimal pattern to catch small decimals (e.g., 3.14, 14.3) that number_pattern misses
        decimal_pattern = re.compile(
            r"(?<![\w])"  # left boundary
            r"\d+\.\d+"   # any number with decimal point
            r"(?![\w])"   # right boundary
        )

        for idx, line in enumerate(lines):
            spans = []
            # Prefer time matches only when strong local context suggests time usage
            time_context = bool(
                re.search(
                    r"\b(at|by|around|about|hrs|hours|o'clock|eta|etd|meet|meeting|arrive|arrival|leave|depart|departure|brief|briefing|watch|shift)\b",
                    line,
                    re.IGNORECASE,
                )
            )
            # 1) Explicit "HHMM hours" takes priority
            for m in time_with_hours.finditer(line):
                spans.append(m.span(1))
            # 2) HH:MM tokens
            for m in time_hh_col_mm.finditer(line):
                spans.append(m.span())
            # 3) 4-digit HHMM if the line looks like time context (do not treat 3-digit tokens like 110 as time)
            if time_context:
                for m in time_hhmm.finditer(line):
                    # Extra local gating: ensure nearby words indicate time within ~15 chars
                    s, e = m.span()
                    window_start = max(0, s - 15)
                    window_end = min(len(line), e + 15)
                    window = line[window_start:window_end]
                    if re.search(
                        r"\b(at|by|hrs|hours|o'clock)\b", window, re.IGNORECASE
                    ):
                        spans.append((s, e))

            # 4a) Multi-dot number chains (check BEFORE decimals so longer matches take priority)
            # e.g., "5.9.597", "1.2.3.4", any-length single/multi-digit groups
            dot_chain_pattern = re.compile(
                r"(?<![\w])"
                r"\d+(?:\.\d+)+"  # at least one digit, then dot-digit groups (e.g., 5.9, 5.9.597)
                r"(?![\w])"
            )
            dot_chain_spans = []
            for match in dot_chain_pattern.finditer(line):
                s, e = match.span()
                dot_text = match.group()

                # Skip if in ignored set
                if dot_text in self.session_ignored_numbers:
                    continue

                # Extend forward if more dots follow (e.g., "5.9.597" could extend further)
                extended_e = e
                while extended_e < len(line) and line[extended_e] == '.':
                    dot_pos = extended_e
                    extended_e += 1
                    found_digit = False
                    while extended_e < len(line) and line[extended_e].isdigit():
                        found_digit = True
                        extended_e += 1
                    # If no digits found after dot, revert
                    if not found_digit:
                        extended_e = dot_pos
                        break

                dot_chain_spans.append((s, extended_e))
                spans.append((s, extended_e))

            # 4b) Multi-hyphen number chains (similar to dot chains, but for hyphens)
            # e.g., "5-9-597", "487-29-3875", any-length single/multi-digit groups
            hyphen_chain_pattern = re.compile(
                r"(?<![\w])"
                r"\d+(?:-\d+)+"  # at least one digit, then hyphen-digit groups
                r"(?![\w])"
            )
            hyphen_chain_spans = []
            for match in hyphen_chain_pattern.finditer(line):
                s, e = match.span()
                hyphen_text = match.group()

                # Skip if in ignored set
                if hyphen_text in self.session_ignored_numbers:
                    continue

                # Extend forward if more hyphens follow (e.g., "5-9-597" could extend further)
                extended_e = e
                while extended_e < len(line) and line[extended_e] == '-':
                    dash_pos = extended_e
                    extended_e += 1
                    found_digit = False
                    while extended_e < len(line) and (line[extended_e].isdigit() or line[extended_e] == ','):
                        if line[extended_e].isdigit():
                            found_digit = True
                        extended_e += 1
                    # If no digits found after hyphen, revert
                    if not found_digit:
                        extended_e = dash_pos
                        break

                hyphen_chain_spans.append((s, extended_e))
                spans.append((s, extended_e))

            # 5) Decimal numbers (check after dot-chains, skip those already captured by dot-chains)
            decimal_spans = []
            for match in decimal_pattern.finditer(line):
                s, e = match.span()

                # Skip if already captured by a dot-chain
                overlaps_dot_chain = any(
                    (s >= dc[0] and s < dc[1]) or (e > dc[0] and e <= dc[1]) or (s <= dc[0] and e >= dc[1])
                    for dc in dot_chain_spans
                )
                if overlaps_dot_chain:
                    continue

                decimal_spans.append((s, e))
                spans.append((s, e))

            # 6) General numbers (skip if already captured as decimal, dot-chain, or hyphen-chain)
            for match in number_pattern.finditer(line):
                s, e = match.span()

                # Skip if this number overlaps with a decimal, dot-chain, or hyphen-chain we already captured
                overlaps = any(
                    (s >= sp[0] and s < sp[1]) or (e > sp[0] and e <= sp[1]) or (s <= sp[0] and e >= sp[1])
                    for sp in decimal_spans + dot_chain_spans + hyphen_chain_spans
                )
                if overlaps:
                    continue

                number_text = match.group()

                # Skip single and double-digit numbers (they're usually fine as-is)
                # Exclude times (contains colon), decimals, and ordinals from this rule
                if (
                    len(number_text) <= 2
                    and ":" not in number_text
                    and "." not in number_text
                    and not re.search(r"(?:st|nd|rd|th)$", number_text)
                ):
                    continue

                # Skip ordinals 1st-100th (handled by REPLACE section)
                ordinal_match = re.match(r"^(\d+)(st|nd|rd|th)$", number_text)
                if ordinal_match:
                    num = int(ordinal_match.group(1))
                    if num <= 100:
                        continue  # These are handled by REPLACE

                # Only include if not in ignored set
                if number_text not in self.session_ignored_numbers:
                    # Extend span to capture full dash-compound (e.g., "100-1", "15,000-20,000")
                    # This is legacy behavior; prefer the hyphen-chain pattern above for multi-segment numbers
                    # Check if dash immediately follows and more number follows the dash
                    extended_e = e
                    while extended_e < len(line) and line[extended_e] == '-':
                        # Scan past dash for digit run (with optional commas like in 20,000)
                        dash_pos = extended_e
                        extended_e += 1
                        found_digit = False
                        while extended_e < len(line) and (line[extended_e].isdigit() or line[extended_e] == ','):
                            if line[extended_e].isdigit():
                                found_digit = True
                            extended_e += 1
                        # If no digits found after dash, revert
                        if not found_digit:
                            extended_e = dash_pos
                            break

                    spans.append((s, extended_e))

            # Deduplicate identical spans but keep distinct occurrences; sort by start index
            if spans:
                seen = set()
                ordered = []
                for sp in sorted(spans):
                    if sp not in seen:
                        seen.add(sp)
                        ordered.append(sp)
                spans = ordered
                numbered_lines.append((idx, line, spans))

        return numbered_lines

    def _analyze_pos_pattern(
        self, context_before: str, number: str, context_after: str
    ) -> Optional[str]:
        """
        Analyze POS (Part-of-Speech) tags to identify number patterns semantically.

        Returns classification if pattern matches, else None.

        Patterns:
        - PROPN/NOUN before number = identifier (e.g., "Gliese 581")
        - NUMBER + NOUN (non-measurement) = quantity (e.g., "490 ships")
        - NUMBER + measurement unit = measurement (already handled by rules)
        """
        if not self.pos_tagger:
            return None

        try:
            # Reconstruct full context for analysis
            full_context = f"{context_before} {number} {context_after}"

            # Get POS tags for all words
            tokens = self.pos_tagger.tag_text(full_context)
            if not tokens:
                return None

            # Find the number token
            number_idx = None
            for i, token in enumerate(tokens):
                if token.text == number:
                    number_idx = i
                    break

            if number_idx is None:
                return None

            # Helper to skip SPACE and PUNCT tokens
            def get_next_meaningful_token(idx):
                """Get next token that isn't SPACE or PUNCT."""
                for i in range(idx + 1, len(tokens)):
                    if tokens[i].pos_category not in ["SPACE", "PUNCT"]:
                        return tokens[i]
                return None

            def get_prev_meaningful_token(idx):
                """Get previous token that isn't SPACE or PUNCT."""
                for i in range(idx - 1, -1, -1):
                    if tokens[i].pos_category not in ["SPACE", "PUNCT"]:
                        return tokens[i]
                return None

            # Check word BEFORE the number
            word_before = get_prev_meaningful_token(number_idx)
            if word_before:
                # PROPN (proper noun) or NOUN before number = identifier (e.g., "Gliese 581")
                if word_before.pos_category in ["PROPN", "NOUN"]:
                    log_message(
                        f"POS pattern: {word_before.pos_category} '{word_before.text}' before '{number}' → identifier"
                    )
                    return "identifier"

            # Check word AFTER the number
            word_after = get_next_meaningful_token(number_idx)
            if word_after:
                # NOUN after number = quantity (unless it's a measurement unit, which is handled by rules)
                # Skip measurement units which are already handled
                measurement_units = {
                    "meter",
                    "meters",
                    "kg",
                    "pound",
                    "pounds",
                    "joule",
                    "joules",
                    "hour",
                    "hours",
                    "second",
                    "seconds",
                    "day",
                    "days",
                    "percent",
                    "percent",
                    "mile",
                    "miles",
                    "foot",
                    "feet",
                    "dollar",
                    "dollars",
                    "euro",
                    "euros",
                }

                if (
                    word_after.pos_category == "NOUN"
                    and word_after.text.lower() not in measurement_units
                ):
                    log_message(
                        f"POS pattern: NUMBER + NOUN '{word_after.text}' → quantity"
                    )
                    return "quantity"

            return None
        except Exception as e:
            log_message(f"POS analysis failed: {e}", level="WARNING")
            return None

    def _get_number_type(
        self, number: str, context_before: str, context_after: str, text_context: Dict
    ) -> Tuple[str, str]:
        """Determine the type of a number using rules first, then learned patterns, then AI fallback.

        Returns:
            Tuple[str, str]: (classification_type, decision_source)
                - classification_type: ordinal, currency, measurement, identifier, year, military_time, general_number, etc.
                - decision_source: rule_pos, rule_ordinal, rule_currency, rule_measurement, rule_identifier,
                                  rule_year, rule_military_time, learned, llm, default
        """
        # Handle comma-separated numbers (e.g., "60,000" → "60000")
        number_digits = number.replace(",", "")

        ctx_lower = (context_before + " " + context_after).lower()
        is_military_ctx = text_context.get("is_military", False)

        # Check for LOCAL time context keywords (not just document-level military context)
        # Use word boundaries to avoid false positives (e.g., 'at' in 'water', 'by' in 'baby')
        has_time_keywords = any(
            re.search(r"\b" + re.escape(w) + r"\b", ctx_lower)
            for w in ["hours", "eta", "etd", "briefing", "at", "by", "o'clock"]
        )

        # POS-BASED PATTERN ANALYSIS: Use linguistic structure to classify
        # This catches semantic patterns that word lists can't cover
        # E.g., "Gliese 581" (PROPN + NUMBER) = identifier
        # E.g., "490 ships" (NUMBER + NOUN) = quantity
        pos_classification = self._analyze_pos_pattern(
            context_before, number, context_after
        )
        if pos_classification:
            log_message(
                f"Using POS-based classification for '{number}': {pos_classification}"
            )
            return (pos_classification, "rule_pos")

        # LEARNED PATTERN: Check if user has explicitly taught this pattern (BOOSTED entries)
        # Checked BEFORE rules to allow user corrections of rule mistakes
        # User-taught patterns have highest priority because they were explicitly specified
        learned_classification = None
        if self.learning_storage:
            learned_classification = self.learning_storage.get_learned_classification(
                number_digits, context_before, context_after
            )
        if learned_classification:
            log_message(
                f"Using BOOSTED learned classification for '{number}': {learned_classification}"
            )
            return (learned_classification, "learned")

        # Rule 1: Ordinal Numbers (101st and above) - Check FIRST as these are unambiguous
        if re.search(r"\d+(st|nd|rd|th)$", number):
            return ("ordinal", "rule_ordinal")

        # Rule 1.5: Currency Detection (explicit symbols or context-based)
        # Check for explicit currency symbols: $, £, €, ¢, ¥, etc.
        if re.match(r"[\$£€¢¥₹]", number):
            return ("currency", "rule_currency")

        # Check for decimal that looks like cents + currency context
        currency_keywords = [
            "cost",
            "price",
            "dollars",
            "dollar",
            "cents",
            "cent",
            "pay",
            "paid",
            "charge",
            "fee",
            "bill",
            "invoice",
            "total",
            "tax",
            "tip",
            "balance",
            "amount",
            "per",
            "each",
        ]
        # Use word boundaries to avoid false positives (e.g., 'per' in 'perfect', 'pay' in 'player')
        if re.match(r"^\d*\.\d{2}$", number) and any(
            re.search(r"\b" + re.escape(w) + r"\b", ctx_lower)
            for w in currency_keywords
        ):
            return ("currency", "rule_currency")

        # Rule 2: Measurements - Check BEFORE military time to avoid "1000 meters" → military_time
        # Must be actual measurement units, not "M-class" or similar
        # Check for explicit measurement units with proper spacing/punctuation
        # Allow for SI prefixes (mega, kilo, etc.) which may be separated by space
        # NOTE: Single-letter units like 'm' (meter) must NOT be followed by hyphen to avoid "M-class" false positives
        measurement_pattern = re.compile(
            r"(?:^|\s)(?:(?:micro|nano|pico|kilo|mega|giga|tera|milli|centi|deci)\s*)?"
            r"(kg|kgs|g(?!-)|gs|lbs|lb|ounces?|oz|pound|pounds|(?:m|in)(?!-)|meter|meters|"
            r"km|kilometer|kilometers|cm|centimeter|centimeters|mm|millimeter|millimeters|"
            r"ft|feet|foot|inches?|miles?|mile|yard|yards|"
            r"hours?|hour|minutes?|minute|seconds?|second|secs?|sec|days?|day|weeks?|week|months?|month|years?|year|"
            r"watts?|watt|kilowatts?|kilowatt|kw|joules?|joule|calories?|calorie|degrees?|degree|celsius|fahrenheit|"
            r"liters?|liter|gallons?|gallon|pints?|pint|cups?|cup|percent|%)\b",
            re.IGNORECASE,
        )
        # Also check for percentage signs
        meas_match = measurement_pattern.search(context_after)
        if meas_match or "%" in context_after:
            log_message(
                f"Classified '{number}' as measurement (matched: {meas_match.group() if meas_match else 'percent'})"
            )
            return ("measurement", "rule_measurement")

        # Rule 3: Identifier (part of scientific name, catalog ID, etc.)
        # Check BEFORE military/year to avoid proper nouns being formatted
        # Patterns:
        # - Preceded by hyphen: "Boeing-747" or "NGC-2020"
        # - Preceded by proper noun: "Gliese 581" or "Kepler 452"
        # - Followed by hyphen and name: "4179-Toutatis" or "2001-WN2"

        # Check if preceded by hyphen
        if context_before.endswith("-"):
            return ("identifier", "rule_identifier")

        # Check if preceded by proper noun (capitalized word), but EXCLUDE common English words
        # that often start sentences or appear before numbers (At, In, On, Already, etc.)
        common_words = {
            # Articles & prepositions
            "the",
            "a",
            "an",
            "at",
            "in",
            "on",
            "by",
            "to",
            "for",
            "with",
            "from",
            "and",
            "or",
            "but",
            "of",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            # Verbs
            "have",
            "has",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "can",
            "may",
            "might",
            "must",
            "shall",
            "get",
            "got",
            "got",
            "said",
            "say",
            "take",
            "took",
            "make",
            "made",
            "go",
            "goes",
            "went",
            "come",
            "comes",
            "came",
            # Pronouns
            "i",
            "he",
            "she",
            "it",
            "we",
            "you",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "this",
            "that",
            "these",
            "those",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            # Question words
            "what",
            "which",
            "who",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "every",
            # Adverbs & conjunctions
            "after",
            "before",
            "during",
            "since",
            "until",
            "while",
            "because",
            "already",
            "just",
            "only",
            "also",
            "about",
            "over",
            "under",
            "above",
            "below",
            "through",
            "easily",
            "almost",
            "nearly",
            "quite",
            "very",
            "so",
            "such",
            "as",
            "than",
            "then",
            # Common titles
            "captain",
            "commander",
            "general",
            "major",
            "doctor",
            "mr",
            "mrs",
            "ms",
            "sir",
            "admiral",
            "lieutenant",
            "sergeant",
            "colonel",
            "officer",
            "chief",
            # Numbers spelled out (0-10)
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            # Ordinals
            "first",
            "second",
            "third",
            "fourth",
            "fifth",
            "sixth",
            "seventh",
            "eighth",
            "ninth",
            "tenth",
            "last",
            "next",
            "new",
            "old",
            "same",
            "other",
            "another",
            # Common adjectives
            "good",
            "bad",
            "big",
            "small",
            "large",
            "great",
            "high",
            "low",
            "right",
            "wrong",
            "true",
            "false",
            "real",
            "full",
            "empty",
            "clear",
            "dark",
            "light",
            "hot",
            "cold",
            # Month names (dates often appear as "January 2013")
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
            "jan",
            "feb",
            "mar",
            "apr",
            "jun",
            "jul",
            "aug",
            "sept",
            "oct",
            "nov",
            "dec",
            # Day names
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "mon",
            "tue",
            "wed",
            "thu",
            "fri",
            "sat",
            "sun",
        }

        # Extract the last word before the number
        last_word_match = re.search(r"([A-Z][a-zA-Z]*)\s*$", context_before)
        if last_word_match:
            last_word = last_word_match.group(1).lower()
            # Only treat as identifier if it's NOT a common English word
            if last_word not in common_words:
                return ("identifier", "rule_identifier")

        # Check if followed by hyphen and more text (e.g., "4179-Toutatis")
        if re.match(r"^-\s*[A-Za-z]", context_after):
            return ("identifier", "rule_identifier")

        # Check if number looks like a catalog/designation number (common patterns)
        # Strategy: Look for CATALOG NAMES (Gliese, Kepler, NGC) which are strong indicators
        # When a catalog name is present, also check for OBJECT DESCRIPTORS (planet, star, etc.)
        # This combines context clues: "Gliese 581" + "planet" = definitely a catalog ID
        local_context = (
            context_before[-50:] + context_after[:50]
        ).lower()  # Only ~100 chars total

        # Strong catalog designation names (definitive indicators)
        catalog_names = [
            "kepler",
            "ngc",
            "koi",
            "gaia",
            "wasp",
            "proxima",
            "trappist",
            "gliese",
            "sdss",
            "catalogue",
            "catalog",
            "mpc",
        ]
        # Object descriptors (confirm it's a celestial designation when combined with catalog names)
        object_descriptors = ["planet", "star", "asteroid", "pulsar"]

        # Use word boundaries to avoid false positives
        has_catalog_name = any(
            re.search(r"\b" + re.escape(w) + r"\b", local_context)
            for w in catalog_names
        )
        has_object_descriptor = any(
            re.search(r"\b" + re.escape(w) + r"\b", local_context)
            for w in object_descriptors
        )

        # If catalog name found, it's definitely an identifier
        if has_catalog_name:
            return ("identifier", "rule_identifier")

        # If BOTH object descriptor AND catalog name would be needed, but only descriptor present, skip
        # (avoids false positives like "490 ships surrounding the planet")
        # This is checked only if no catalog name was found

        # Rule 4: Year (check BEFORE military time to avoid misclassification)
        # Years like 2067 would incorrectly match military time (hour 20, minute 67 invalid)
        # Strong indicators: 4 digits, 1000-9999 range (handles years from past to far future), context words
        if len(number_digits) == 4 and number_digits.isdigit():
            year_val = int(number_digits)
            if 1000 <= year_val <= 9999:
                # Check for date context keywords using word boundaries
                # CRITICAL: Use word boundaries to avoid false positives!
                # E.g., 'in' in 'inexorably', 'from' in 'from', 'during' in 'during'
                date_keywords = [
                    "year",
                    "born",
                    "since",
                    "in",
                    "during",
                    "january",
                    "february",
                    "march",
                    "april",
                    "may",
                    "june",
                    "july",
                    "august",
                    "september",
                    "october",
                    "november",
                    "december",
                    "century",
                    "decade",
                    "era",
                    "period",
                    "date",
                    "dated",
                    "from",
                ]
                has_date_keywords = any(
                    re.search(r"\b" + re.escape(w) + r"\b", ctx_lower)
                    for w in date_keywords
                )

                # If we have date context keywords, classify as year (not military time)
                if has_date_keywords:
                    log_message(
                        f"Classified '{number}' as year (date context detected)"
                    )
                    return ("year", "rule_year")

        # Rule 5: Military Time
        # Strong indicators: 4 digits with valid HHMM format, STRONG LOCAL time context
        # Must be valid military time (0000-2359, i.e., hours 00-23 and minutes 00-59)
        # DEBUG: Log all numbers with colons to trace why times aren't classified
        if ":" in number:
            log_message(
                f"DEBUG: Number with colon: '{number}', is_military_ctx={is_military_ctx}, has_time_keywords={has_time_keywords}"
            )

        # Only classify as military time if we have STRONG LOCAL time context or explicit military context
        if (
            len(number_digits) == 4
            and number_digits.isdigit()
            and (has_time_keywords or (is_military_ctx and has_time_keywords))
        ):
            # Validate it's actually a valid military time (0000-2359)
            # Hours: 00-23, Minutes: 00-59
            try:
                hour_value = int(number_digits[:2])
                minute_value = int(number_digits[2:])
                if 0 <= hour_value <= 23 and 0 <= minute_value <= 59:
                    log_message(
                        f"Classified '{number}' as military_time (valid HHMM format with time context)"
                    )
                    return ("military_time", "rule_military_time")
            except (ValueError, IndexError):
                pass

        if ":" in number and has_time_keywords:
            log_message(
                f"DEBUG: Colon rule matched for '{number}' - returning military_time"
            )
            return ("military_time", "rule_military_time")
        elif ":" in number:
            log_message(
                f"DEBUG: Colon rule FAILED for '{number}' - no local time context"
            )

        # Rule 6: Year (fallback - no date keywords but in year range)
        # If we get here, year check already happened but without date keywords
        # Extended range check for years without explicit date context
        if len(number_digits) == 4 and number_digits.isdigit():
            year_val = int(number_digits)
            if 1000 <= year_val <= 9999:
                # If it's in year range but didn't have explicit date keywords,
                # still classify as year since it failed military time validation
                if not (
                    0 <= int(number_digits[2:]) <= 59
                ):  # Invalid as military time minutes
                    log_message(
                        f"Classified '{number}' as year (invalid minute value {number_digits[2:]})"
                    )
                    return ("year", "rule_year")

        # Fallback to AI Classification if no rules match (unless rules_only_mode is enabled)
        if self.ai_service and not self.rules_only_mode:
            full_context = f"{context_before} **{number}** {context_after}"
            response = self.ai_service.classify_number(number, full_context)
            if response.success:
                # Extract the classification from the response (may include explanation)
                classification = self._extract_classification_from_response(
                    response.content
                )
                log_message(f"AI classified '{number}' as type: {classification}")
                return (classification, "llm")

        # Default fallback (used when no rules match and either AI is unavailable or rules_only_mode is enabled)
        if self.rules_only_mode:
            log_message(
                f"RULES-ONLY MODE: No rule matched for '{number}', defaulting to general_number"
            )
        return ("general_number", "default")

    def _extract_classification_from_response(self, response_text: str) -> str:
        """
        Extract the classification type from AI response.

        AI responses may include explanations like:
        - "answer: \"year\""
        - "answer: year"
        - "year"
        - "answer: \"general_number\"\n\nexplanation: ..."

        Returns just the classification (year, military_time, quantity, etc.)
        """
        # Handle different response formats
        response_lower = response_text.lower().strip()

        # Extract from "answer: ..." format
        if "answer:" in response_lower:
            # Get everything after "answer:" and before newline or quotes
            parts = response_lower.split("answer:", 1)[1].strip()
            # Remove quotes and extra whitespace
            parts = parts.strip("\"'\\n ").split()[0].strip("\"'")
            return parts

        # If response is just a classification word, use it
        valid_classifications = [
            "military_time",
            "year",
            "ordinal",
            "measurement",
            "identifier",
            "quantity",
            "general_number",
            "time",
        ]

        for classification in valid_classifications:
            if classification in response_lower:
                return classification

        # Default fallback
        return "general_number"

    def _digit_to_word(self, digit: str) -> str:
        """Convert a single digit character to its word representation."""
        digit_words = {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
            '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
        }
        return digit_words.get(digit, digit)

    def _format_number_by_type(self, number: str, number_type: str) -> str:
        """Formats a number string into a spoken-word string based on its classified type."""
        try:
            # Handle comma-separated numbers (e.g., "60,000" → "60000")
            number_digits = number.replace(",", "")

            # Check if this is a decimal number (digits.digits with no spaces)
            is_decimal = '.' in number_digits and re.match(r'^\d+\.\d+$', number_digits)

            # Handle decimals based on integer size and type
            if is_decimal:
                parts = number_digits.split('.')
                integer_part = parts[0]
                decimal_part = parts[1]

                # Format decimal part as individual digits
                decimal_words = " ".join([self._digit_to_word(d) for d in decimal_part])

                # Rule 1: Integer part has 1-2 digits → format ALL as digits
                # Examples: "3.14" → "three point one four", "14.3" → "one four point three"
                if len(integer_part) <= 2:
                    integer_words = " ".join([self._digit_to_word(d) for d in integer_part])
                    return f"{integer_words} point {decimal_words}"

                # Rule 2: Integer part has 3+ digits → check type
                # Identifier type → all digits
                if number_type == "identifier":
                    # "item 258.58" → "two five eight point five eight"
                    integer_words = " ".join([self._digit_to_word(d) for d in integer_part])
                    return f"{integer_words} point {decimal_words}"

                # Currency → let currency formatter handle it
                elif number_type == "currency":
                    pass  # Fall through to currency formatter

                # All other types (quantity, measurement, general_number, etc.) → natural + digits
                else:
                    # "1235.5 miles" → "one thousand two hundred thirty-five point five miles"
                    # "1234.567" → "one thousand two hundred thirty-four point five six seven"
                    integer_words = num2words(int(integer_part))
                    return f"{integer_words} point {decimal_words}"

            if number_type == "military_time":
                if ":" in number_digits:
                    parts = number_digits.split(":")
                    h, m = int(parts[0]), int(parts[1])
                else:
                    num_val = int(number_digits)
                    h, m = (
                        divmod(num_val, 100) if len(number_digits) > 2 else (num_val, 0)
                    )

                hour_text = "zero " + num2words(h) if h < 10 else num2words(h)
                minute_text = num2words(m)
                if m == 0:
                    minute_text = "hundred"
                elif m < 10:
                    minute_text = "zero " + minute_text

                return f"{hour_text} {minute_text}"

            elif number_type == "year":
                return num2words(int(number_digits), to="year")

            elif number_type == "ordinal":
                num_part = re.sub(r"(st|nd|rd|th)$", "", number_digits)
                return num2words(int(num_part), to="ordinal")

            elif number_type == "identifier":
                # For identifiers, speak only the digits (skip commas)
                return " ".join(list(number_digits))

            elif number_type == "dot_identifier":
                # For dot-separated compound numbers, split on dots and speak digit-by-digit with "point"
                parts = number_digits.split('.')
                formatted_parts = []
                for part in parts:
                    # Each part should be digits; speak individually
                    if part:
                        formatted_parts.append(" ".join(list(part)))
                return " point ".join(formatted_parts)

            elif number_type == "currency":
                return self._format_currency(number)

            elif number_type == "elapsed_time":
                return self._format_elapsed_time(number)

            elif number_type in ["quantity", "measurement", "general_number"]:
                return num2words(int(number_digits))

        except Exception as e:
            log_message(
                f"Failed to format number '{number}' of type '{number_type}': {e}",
                level="WARNING",
            )

        return number  # Fallback to original

    def _format_currency(self, currency_str: str) -> str:
        """Format currency amounts into spoken words."""
        try:
            # Remove spaces and extract symbol
            clean_str = currency_str.replace(" ", "")

            # Currency symbol mapping
            symbol_map = {
                "$": "dollars",
                "¢": "cents",
                "£": "pounds",
                "€": "euros",
                "¥": "yen",
                "₹": "rupees",
            }

            # Find currency symbol
            currency_symbol = None
            currency_name = None
            for symbol, name in symbol_map.items():
                if symbol in clean_str:
                    currency_symbol = symbol
                    currency_name = name
                    break

            # Extract numeric part (remove symbol)
            numeric_str = (
                clean_str.replace(currency_symbol, "") if currency_symbol else clean_str
            )

            # Parse the amount
            if "." in numeric_str:
                # Has decimal part
                parts = numeric_str.split(".")
                dollars = parts[0] if parts[0] else "0"
                cents = parts[1] if len(parts) > 1 else "00"

                dollars_int = int(dollars) if dollars else 0
                cents_int = int(cents) if cents else 0

                # Format with dollars and cents
                if dollars_int > 0 and cents_int > 0:
                    dollars_text = num2words(dollars_int)
                    cents_text = num2words(cents_int)
                    return f"{dollars_text} {currency_name} and {cents_text} cents"
                elif dollars_int > 0:
                    return f"{num2words(dollars_int)} {currency_name}"
                elif cents_int > 0:
                    return f"{num2words(cents_int)} cents"
                else:
                    return "zero dollars"
            else:
                # No decimal, just whole amount
                amount = int(numeric_str) if numeric_str else 0
                if currency_name == "cents":
                    return f"{num2words(amount)} cents"
                else:
                    return f"{num2words(amount)} {currency_name}"
        except Exception as e:
            log_message(
                f"Failed to format currency '{currency_str}': {e}", level="WARNING"
            )
            return currency_str

    def _format_elapsed_time(self, time_str: str) -> str:
        """Format elapsed time (HH:MM:SS or HH:MM) into spoken words."""
        try:
            # Handle colon-separated time format
            if ":" in time_str:
                parts = time_str.split(":")
                hours = int(parts[0]) if parts[0] else 0
                minutes = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                seconds = int(parts[2]) if len(parts) > 2 and parts[2] else 0

                # Build the spoken representation
                result_parts = []

                # Hours
                if hours > 0:
                    hour_text = num2words(hours)
                    result_parts.append(f"{hour_text} hour{'s' if hours != 1 else ''}")

                # Minutes
                if minutes > 0:
                    minute_text = num2words(minutes)
                    result_parts.append(
                        f"{minute_text} minute{'s' if minutes != 1 else ''}"
                    )

                # Seconds
                if seconds > 0:
                    second_text = num2words(seconds)
                    result_parts.append(
                        f"{second_text} second{'s' if seconds != 1 else ''}"
                    )

                # If nothing was specified, return "zero"
                if not result_parts:
                    return "zero"

                # Join with commas and "and"
                if len(result_parts) == 1:
                    return result_parts[0]
                elif len(result_parts) == 2:
                    return f"{result_parts[0]} and {result_parts[1]}"
                else:  # 3 parts
                    return (
                        f"{result_parts[0]}, {result_parts[1]}, and {result_parts[2]}"
                    )
            else:
                # Fallback if no colon format
                return num2words(int(time_str.replace(",", "")))

        except Exception as e:
            log_message(
                f"Failed to format elapsed time '{time_str}': {e}", level="WARNING"
            )
            return time_str

    def _strip_other_numbers(self, text: str) -> str:
        """
        Replace all numbers in text with [NUM] placeholder to avoid confusion.

        This prevents the AI from getting confused by nearby numbers when
        analyzing a specific target number.
        """
        # Pattern to match complete numbers - same as _find_all_numbers_for_ai
        patterns = [
            r"\b\d{1,2}:\d{2}\b",  # Time format
            r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b",  # Numbers with commas
            r"\b\d+\.\d+\b",  # Decimal numbers
            r"\b\d+\b",  # Plain digits
        ]
        combined_pattern = "|".join(f"({p})" for p in patterns)
        number_pattern = re.compile(combined_pattern)
        return number_pattern.sub("[NUM]", text)

    def _analyze_numbered_line_ai(
        self, line_content: str, spans: List[Tuple[int, int]], text_context: Dict,
        batch_classifications: Dict[str, Tuple[str, str]] = None
    ) -> Dict:
        """Use a rule-based, AI-assisted workflow to format numbers in a line.

        Args:
            line_content: The line text to analyze
            spans: List of (start, end) positions of numbers in the line
            text_context: Context dictionary with document-level info
            batch_classifications: Optional dict mapping "number|context" to (type, source) tuple
                                  If provided, uses these instead of calling _get_number_type for AI

        Returns:
            Dict with analysis results including proposed changes
        """
        proposed_changes = []
        all_types = []

        for start, end in spans:
            number = line_content[start:end]
            context_before = line_content[max(0, start - 50) : start]
            context_after = line_content[end : end + 50]

            # Step 1: Classify the number type using rules and AI fallback
            # If batch_classifications provided, check there first
            batch_key = f"{number}|{context_before + ' ' + context_after}"
            if batch_classifications and batch_key in batch_classifications:
                # Use pre-computed batch classification
                number_type, decision_source = batch_classifications[batch_key]
            else:
                # Fall back to individual classification (rules only, no AI)
                number_type, decision_source = self._get_number_type(
                    number, context_before, context_after, text_context
                )
            all_types.append(number_type)

            # Step 2: Format the number based on its classified type
            suggested_replacement = self._format_number_by_type(number, number_type)
            log_message(
                f"Formatted '{number}' as type '{number_type}' → '{suggested_replacement}'"
            )

            if suggested_replacement != number:
                proposed_changes.append(
                    {
                        "original": number,
                        "replacement": suggested_replacement,
                        "start": start,
                        "end": end,
                        "type": number_type,
                        "decision_source": decision_source,
                        "confidence": 0.9,  # Confidence is higher now due to rules
                        "reasoning": f"Classified as '{number_type}' and formatted.",
                    }
                )

        # Apply changes to create new line
        if not proposed_changes:
            return {
                "should_change": False,
                "new_line": line_content,
                "confidence": 1.0,
                "reasoning": "No changes needed",
                "number_types": all_types,
            }

        new_line = line_content
        for change in reversed(proposed_changes):
            new_line = (
                new_line[: change["start"]]
                + change["replacement"]
                + new_line[change["end"] :]
            )

        type_summary = ", ".join(set(all_types))
        reasoning = (
            f"Formatted {len(proposed_changes)} number(s) (types: {type_summary})"
        )

        return {
            "should_change": True,
            "new_line": new_line,
            "confidence": 0.9,
            "reasoning": reasoning,
            "changes": proposed_changes,
            "number_types": all_types,
        }
