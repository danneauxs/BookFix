"""
AI-Enhanced Choice Processor for Bookfix.

Extends the InteractiveChoiceProcessor with AI analysis capabilities
for automatic homograph disambiguation.
"""

import re
import nltk
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING, Any

# Ensure NLTK data is available for sentence tokenization
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

if TYPE_CHECKING:
    from ..context import BookfixContext

from .choices import InteractiveChoiceProcessor
from ..ai.service import BookfixAIService
from ..ai.change_tracker import AIChangeTracker

# Choices learning system retired — replaced by dep_rules (choices_pos_dictionary.json)
# and curated examples in choices.json. Files preserved at .ai_learning/ for reference.
from ..ai.pos_tagger import get_pos_tagger
from ..ai.pos_dictionary import get_pos_dictionary
from ..ai.hybrid_deciders import DECIDERS, NLI_WORDS
from ..lexicon_loader import LexiconLoader
from ..logging import log_message


class AIChoiceProcessor(InteractiveChoiceProcessor):
    """
    AI-enhanced choice processor that can automatically resolve homographs
    using context analysis, with fallback to manual processing.
    """

    def __init__(
        self,
        change_tracker: Optional[AIChangeTracker] = None,
        context_size: int = 250,
        show_reasoning: bool = False,
    ):
        """Initializes a new instance of the BookfixAI class.
        Args:
        change_tracker (Optional[AIChangeTracker]): An optional tracker for changes.
        context_size (int): The size of the context to consider.
        show_reasoning (bool): Whether to display reasoning.
        Returns: None
        """
        super().__init__()
        from collections import Counter

        self.ai_service: Optional[BookfixAIService] = None
        self.ai_enabled = False
        self.ai_verify_all = (
            False  # If True, AI verifies ALL decisions, not just uncertain ones
        )
        self.confidence_threshold = 0.8
        self.fallback_to_manual = True
        self.context_size = context_size  # Configurable context size for AI analysis
        self.rules_only_mode = False  # If True, disable AI and force rule application
        self.single_sentence_context = True  # Use single sentence context for rules
        self.show_reasoning = (
            show_reasoning  # Whether to request AI reasoning (verbose, slower)
        )

        # Initialize spaCy and lexicon
        import spacy

        try:
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            self.nlp = spacy.load("en_core_web_sm")
        self.lexicon_loader = LexiconLoader()
        self.word_choices = self.lexicon_loader.get_all_words()

        # Hybrid deciders for improved accuracy on 22 known homographs
        self.nli = None  # Lazy load RoBERTa-MNLI when needed

        # Load configuration
        self.config = self._load_config()

        # Change tracking
        self.change_tracker = change_tracker

        # Track AI decisions for review
        self.ai_decisions = []
        self.manual_decisions = []

        # Decision statistics
        self.decision_stats = Counter()

        # Log file for choices processing
        self.choices_log_path = None

        # POS tagging system (lazy loaded)
        self.pos_tagger = None
        self.pos_dictionary = None
        self.use_pos_tagging = True  # Enable POS-based decisions

    def initialize_ai(self, ai_config: Dict) -> bool:
        """
        Initialize AI service from configuration.

        Args:
            ai_config: Dictionary with AI configuration

        Returns:
            True if initialization was successful (AI enabled OR rules available)
        """
        try:
            self.ai_enabled = ai_config.get("ai_enabled", False)
            self.ai_verify_all = ai_config.get("ai_verify_all", False)

            if not self.ai_enabled:
                log_message(
                    "AI processing disabled - using rules-only mode (POS tagging, keywords, learned patterns)"
                )
                # CRITICAL: Set rules_only_mode flag for bypassing logic elsewhere
                self.rules_only_mode = True
                # Return True because review mode can still work with just rules
                # POS tagging, keywords, and learned patterns don't require AI
                return True

            if self.ai_verify_all:
                log_message(
                    "AI Verify ALL mode: AI will verify every decision, not just uncertain ones"
                )

            # Initialize AI service with full configuration
            # Supports both old (model_path) and new (provider/model/api_key) style configs
            self.ai_service = BookfixAIService(
                model_path=ai_config.get("model_path"),
                provider=ai_config.get("provider", "llama-cpp"),
                model=ai_config.get("model"),
                api_key=ai_config.get("api_key"),
                confidence_threshold=ai_config.get("confidence_threshold", 0.8),
                max_retries=ai_config.get("max_retries", 3),
                rate_limit=ai_config.get("rate_limit", 0.5),
            )

            # Test AI connection
            test_result = self.ai_service.test_connection()
            if not test_result.success:
                log_message(
                    f"AI service connection failed: {test_result.error_message} — degrading to rules-only mode",
                    level="WARNING",
                )
                self.ai_enabled = False
                self.rules_only_mode = True  # Review window still shows; no AI calls
                return True  # Don't fall back to traditional picker
            else:
                log_message(
                    f"AI service initialized successfully: {test_result.content}"
                )
                self.ai_enabled = True
                return True

        except Exception as e:
            import traceback

            log_message(f"Failed to initialize AI service: {e}", level="ERROR")
            log_message(traceback.format_exc(), level="ERROR")
            self.ai_enabled = False
            return False

    def _setup_choices_log(self, file_path: Optional[str]):
        """Setup choices.log in the same directory as the input file."""
        if file_path:
            import os

            file_dir = os.path.dirname(file_path)
            self.choices_log_path = os.path.join(file_dir, "choices.log")
        else:
            self.choices_log_path = "choices.log"  # Fallback to current directory

        # Create/overwrite the log file at the start of processing
        try:
            with open(self.choices_log_path, "w", encoding="utf-8") as f:
                f.write("")  # Start with empty file
        except Exception as e:
            log_message(f"Failed to create choices.log: {e}", level="WARNING")

    def _log_to_choices_log(self, message: str):
        """Log a message to choices.log."""
        if self.choices_log_path:
            try:
                import datetime

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.choices_log_path, "w", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {message}\n")
            except Exception as e:
                log_message(f"Failed to write to choices.log: {e}", level="WARNING")

    def _clear_all_logs(self, ctx: "BookfixContext"):
        """Delete all log files for a fresh start - NO archiving."""
        import os
        import datetime

        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mode = (
            "Rules-Only"
            if self.rules_only_mode
            else ("Hybrid" if self.ai_enabled else "Verify-All")
        )
        total_words = len(ctx.choices) if ctx and ctx.choices else 0

        for filename in ["rules_choices.log", "rule_reasoning.log"]:
            filepath = os.path.join(log_dir, "logs", filename)
            if os.path.exists(filepath):
                try:
                    os.unlink(filepath)
                    log_message(f"Deleted old log: {filename}")
                except Exception as e:
                    log_message(f"Failed to delete {filename}: {e}", level="WARNING")

        header = f"""=== NEW PROCESSING RUN STARTED: {timestamp} ===
Input file: {ctx.current_file_path if ctx and ctx.current_file_path else "unknown"}
Mode: {mode}
Total homographs configured: {total_words}
================================================
"""

        rules_choices_path = os.path.join(log_dir, "logs", "rules_choices.log")
        with open(rules_choices_path, "w", encoding="utf-8") as f:
            f.write(header)

        reason_path = os.path.join(log_dir, "logs", "rule_reasoning.log")
        legend = """RULE TYPE EXPLANATIONS:
  complex_pos - Uses spaCy dependency parsing for special syntactic patterns (imperatives, auxiliaries)
  pos        - Basic POS tag match from spaCy (VB, NN, JJ, etc.)
  semantic   - Domain-aware keyword matching (audio, aquatic, social, physical categories)
  entity     - Named entity context (PERSON, ORG, GPE tags or entity patterns)
  definition - Dictionary/definition-based rule from choices_pos_dictionary.json
  keyword    - Direct keyword match from context_keywords lists
  consensus - All rules that fired agree on the same choice
  Priority order (highest to lowest): complex_pos > entity > pos > semantic > definition > keyword
================================================================================
"""
        with open(reason_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write(legend)

        log_message(f"All logs cleared for new run: {timestamp}")

    def _write_end_of_run_summary(self):
        """Write end-of-run summary to both log files."""
        import os
        import datetime

        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_changes = (
            len(self.change_tracker.changes)
            if self.change_tracker and self.change_tracker.changes
            else 0
        )
        stats = dict(self.decision_stats)

        summary = f"""
================================================
PROCESSING COMPLETED: {timestamp}
Total changes processed: {total_changes}
Decision breakdown: {stats}
================================================
"""

        rules_choices_path = os.path.join(log_dir, "logs", "rules_choices.log")
        with open(rules_choices_path, "a", encoding="utf-8") as f:
            f.write(summary)

        reason_path = os.path.join(log_dir, "logs", "rule_reasoning.log")
        with open(reason_path, "a", encoding="utf-8") as f:
            f.write(summary)

    def _ensure_pos_services(self):
        """Lazy load POS tagger and dictionary (only once)."""
        if self.use_pos_tagging and self.pos_tagger is None:
            try:
                self.pos_tagger = get_pos_tagger()
                # Always get fresh reference to pos_dictionary from global singleton
                # This ensures we get updates when reset_pos_dictionary() is called
                self.pos_dictionary = get_pos_dictionary()
                log_message("POS tagging services initialized (using spaCy)")
            except Exception as e:
                log_message(f"Failed to initialize POS services: {e}", level="WARNING")
                self.use_pos_tagging = False

    def _ensure_nli_services(self):
        """Lazy load RoBERTa-MNLI NLI model (only when hybrid deciders need it)."""
        if self.nli is None:
            try:
                from transformers import pipeline as hf_pipeline
                import torch

                device = 0 if torch.cuda.is_available() else -1
                self.nli = hf_pipeline(
                    "zero-shot-classification",
                    model="roberta-large-mnli",
                    device=device,
                )
                log_message("RoBERTa-MNLI NLI model initialized for hybrid deciders")
            except Exception as e:
                log_message(f"Failed to initialize NLI model: {e}", level="WARNING")
                self.nli = None

    def _refresh_pos_dictionary(self):
        """Refresh the pos_dictionary reference to get latest instance from global singleton.

        This ensures we get updates when reset_pos_dictionary() is called.
        """
        self.pos_dictionary = get_pos_dictionary()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json."""
        import json
        from pathlib import Path

        config_path = Path(__file__).parent.parent / "config" / "config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    def _check_replace_rules(
        self, word: str, context_before: str, context_after: str, ctx: "BookfixContext"
    ) -> Optional[Tuple[str, str]]:
        """
        Check if word is part of a phrase in REPLACE rules.

        Args:
            word: The target word (e.g., "close")
            context_before: Text before the word
            context_after: Text after the word
            ctx: Context with replacements dict

        Returns:
            Tuple of (pronunciation, explanation) or None if no match
        """
        log_message(
            f"DEBUG: Entering _check_replace_rules for word: '{word}'", level="DEBUG"
        )
        log_message(
            f"DEBUG: _check_replace_rules context_before: '{context_before}', context_after: '{context_after}'",
            level="DEBUG",
        )

        if not hasattr(ctx, "replacements") or not ctx.replacements:
            log_message(
                f"DEBUG: _check_replace_rules: No replacements dict available",
                level="DEBUG",
            )
            log_message(
                f"DEBUG: Exiting _check_replace_rules (no replacements)", level="DEBUG"
            )
            return None

        log_message(
            f"DEBUG: _check_replace_rules: Checking word '{word}' with {len(ctx.replacements)} rules",
            level="DEBUG",
        )

        # Get words before and after
        words_before = context_before.strip().split()
        words_after = context_after.strip().split()
        log_message(
            f"DEBUG: _check_replace_rules: words_before: {words_before}, words_after: {words_after}",
            level="DEBUG",
        )

        # Build potential phrases (check longer phrases first for better matches):
        # 1. word + 2 next words (e.g., "close enough to")
        # 2. previous word + word + next word (e.g., "so close to")
        # 3. word + next word (e.g., "close to")
        # 4. previous word + word (e.g., "so close")

        phrases_to_check = []

        # word + 2 next words (longest first)
        if len(words_after) >= 2:
            phrase = f"{word} {words_after[0]} {words_after[1]}"
            phrases_to_check.append(phrase)
            log_message(
                f"DEBUG: _check_replace_rules: Adding phrase: '{phrase}'", level="DEBUG"
            )

        # 1 before + word + 1 after
        if words_before and words_after:
            phrase = f"{words_before[-1]} {word} {words_after[0]}"
            phrases_to_check.append(phrase)
            log_message(
                f"DEBUG: _check_replace_rules: Adding phrase: '{phrase}'", level="DEBUG"
            )

        # word + 1 next word
        if words_after:
            phrase = f"{word} {words_after[0]}"
            phrases_to_check.append(phrase)
            log_message(
                f"DEBUG: _check_replace_rules: Adding phrase: '{phrase}'", level="DEBUG"
            )

        # 1 before + word
        if words_before:
            phrase = f"{words_before[-1]} {word}"
            phrases_to_check.append(phrase)
            log_message(
                f"DEBUG: _check_replace_rules: Adding phrase: '{phrase}'", level="DEBUG"
            )

        # Check each phrase against REPLACE rules (ctx.replacements is a dict)
        # Need case-insensitive matching since keys might be any case
        log_message(
            f"DEBUG: _check_replace_rules: Checking phrases: {phrases_to_check}",
            level="DEBUG",
        )

        for phrase in phrases_to_check:
            phrase_lower = phrase.lower()

            # Check if this phrase exists as a key (case-insensitive)
            for original_key, replacement in ctx.replacements.items():
                if original_key.lower() == phrase_lower:
                    # Found a match!
                    log_message(
                        f"DEBUG: _check_replace_rules: REPLACE MATCH FOUND! '{phrase}' matches rule '{original_key}' → '{replacement}'",
                        level="DEBUG",
                    )
                    replacement_words = replacement.split()

                    # Find which word in replacement corresponds to our target word
                    original_words = phrase.split()
                    try:
                        # Ensure original_words is not empty before trying to find index
                        if not original_words:
                            log_message(
                                f"DEBUG: _check_replace_rules: original_words is empty, skipping index lookup.",
                                level="DEBUG",
                            )
                            continue

                        word_index = [w.lower() for w in original_words].index(
                            word.lower()
                        )
                        log_message(
                            f"DEBUG: _check_replace_rules: word_index for '{word.lower()}' in original_words: {word_index}",
                            level="DEBUG",
                        )

                        # --- CRITICAL LINE FOR ERROR ---
                        log_message(
                            f"DEBUG: _check_replace_rules: About to access replacement_words[{word_index}]",
                            level="DEBUG",
                        )

                        # Ensure replacement_words is not empty and word_index is valid
                        if not replacement_words:
                            log_message(
                                f"DEBUG: _check_replace_rules: replacement_words is empty, cannot access index {word_index}.",
                                level="DEBUG",
                            )
                            continue

                        # FIX: Handle cases where replacement has fewer words than original phrase
                        # Use the last word of replacement if word_index is out of bounds
                        if word_index >= len(replacement_words):
                            log_message(
                                f"DEBUG: _check_replace_rules: Word index {word_index} is >= len(replacement_words) ({len(replacement_words)}). Using last word of replacement.",
                                level="DEBUG",
                            )
                            pronunciation = replacement_words[-1]
                        else:
                            pronunciation = replacement_words[word_index]
                        # --- END CRITICAL LINE ---

                        explanation = f"REPLACE rule: '{original_key}' → '{replacement}' (user-defined)"
                        log_message(
                            f"DEBUG: _check_replace_rules: Extracted pronunciation: '{pronunciation}' from position {word_index}",
                            level="DEBUG",
                        )
                        log_message(
                            f"DEBUG: Exiting _check_replace_rules (match found)",
                            level="DEBUG",
                        )
                        return (pronunciation, explanation)
                    except (ValueError, IndexError) as e:
                        log_message(
                            f"DEBUG: _check_replace_rules: Failed to extract pronunciation from match or word not found in original_words. Error: {e}",
                            level="DEBUG",
                        )
                        continue

        log_message(
            f"DEBUG: _check_replace_rules: No REPLACE rule matches found", level="DEBUG"
        )
        log_message(f"DEBUG: Exiting _check_replace_rules (no match)", level="DEBUG")
        return None

    def _get_pos_based_choice(
        self, word: str, context_before: str, context_after: str
    ) -> Optional[Tuple[str, float, str]]:
        """
        Get pronunciation choice based on POS tagging.

        Args:
            word: The word to analyze
            context_before: Text before the word
            context_after: Text after the word

        Returns:
            Tuple of (pronunciation, confidence, explanation) or None if no POS match
        """
        if not self.use_pos_tagging:
            return None

        self._ensure_pos_services()

        if self.pos_tagger is None or self.pos_dictionary is None:
            return None

        # Check if word is in POS dictionary
        if not self.pos_dictionary.has_word(word):
            return None

        try:
            # Get POS tag for word in context
            pos_tag = self.pos_tagger.tag_with_context(
                context_before, word, context_after
            )

            if not pos_tag:
                return None

            # Look up pronunciation based on POS tag
            pronunciation = self.pos_dictionary.get_pronunciation_by_pos(word, pos_tag)

            if pronunciation:
                explanation = self.pos_dictionary.explain_choice(word, pos_tag)
                # Lower confidence for POS since it can be wrong (~5% error rate)
                # This allows semantic/keyword rules to override when they have strong matches
                base_confidence = 0.80
                return (pronunciation, base_confidence, explanation)

        except Exception as e:
            log_message(f"POS analysis error for '{word}': {e}", level="WARNING")

        return None

    def process_choices_ai_review_mode(
        self, ctx: "BookfixContext", force_all: bool = True
    ) -> Optional[AIChangeTracker]:
        """
        Process choices with AI, creating Change objects for later review.
        This version uses batching for AI calls to improve efficiency.
        """
        log_message("DEBUG: Entering process_choices_ai_review_mode", level="DEBUG")

        # Clear logs at start of processing
        import os

        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_files_to_clear = [
            "rule_reasoning.log",
            "rules_choices.log",
            "review_changes.log",
        ]
        for log_file in log_files_to_clear:
            log_path = os.path.join(log_dir, "logs", log_file)
            if os.path.exists(log_path):
                os.remove(log_path)

        if not self.change_tracker:
            log_message("Change tracker not set, cannot use review mode")
            log_message(
                "DEBUG: Exiting process_choices_ai_review_mode (change tracker not set)",
                level="DEBUG",
            )
            return None

        if not self.ai_enabled and not self.use_pos_tagging:
            log_message("Neither AI nor POS tagging available, cannot use review mode")
            log_message(
                "DEBUG: Exiting process_choices_ai_review_mode (AI/POS not available)",
                level="DEBUG",
            )
            return None

        if self.use_pos_tagging:
            self._ensure_pos_services()
            # Reload POS dictionary from disk to pick up manual edits
            from ..ai.pos_dictionary import reset_pos_dictionary

            reset_pos_dictionary()
            self._refresh_pos_dictionary()

        self._setup_choices_log(ctx.current_file_path)
        self._clear_all_logs(ctx)
        self._log_to_choices_log("=== AI CHOICES BATCH PROCESSING STARTED ===")
        log_message(
            f"DEBUG: Before len(ctx.choices) - type(ctx.choices): {type(ctx.choices)}, ctx.choices is None: {ctx.choices is None}",
            level="DEBUG",
        )
        log_message(
            f"Starting AI-first review mode with {len(ctx.choices)} choice rules (Batch Mode)"
        )
        log_message(
            f"DEBUG: Before set_text - type(ctx.text): {type(ctx.text)}, len(ctx.text): {len(ctx.text) if ctx.text is not None else 'None'}, change_tracker is None: {self.change_tracker is None}",
            level="DEBUG",
        )
        try:
            self.change_tracker.set_text(original=ctx.text, current=ctx.text)
        except IndexError as e:
            log_message(
                f"FATAL ERROR: IndexError during set_text for file {ctx.current_file_path}: {e}",
                level="ERROR",
            )
            log_message(
                f"DEBUG: ctx.text type: {type(ctx.text)}, ctx.text length: {len(ctx.text) if ctx.text is not None else 'None'}",
                level="ERROR",
            )
            log_message(
                f"DEBUG: ctx.text (first 100 chars): {ctx.text[:100] if ctx.text else 'N/A'}",
                level="ERROR",
            )
            log_message(
                "DEBUG: Exiting process_choices_ai_review_mode (IndexError during set_text)",
                level="DEBUG",
            )
            return None

        items_for_ai_batch = []
        item_id_counter = 0
        match_map = {}

        words_to_process = set(ctx.choices.keys())
        log_message(
            f"DEBUG: Total words to process: {len(words_to_process)}", level="DEBUG"
        )
        for word in words_to_process:
            log_message(f"DEBUG: Processing word: '{word}'", level="DEBUG")
            matches = self._find_matches(word, self.change_tracker.original_text)
            log_message(
                f"DEBUG: Found {len(matches)} matches for '{word}'", level="DEBUG"
            )
            if not matches:
                continue

            log_message(f"DEBUG: Getting options for word: '{word}'", level="DEBUG")
            contextualized_options = ctx.contextualized_choices.get(word)
            regular_options = ctx.choices.get(word, [])
            options = regular_options or [
                opt for opt, _ in (contextualized_options or [])
            ]
            if not options:
                continue

            for match_idx, match in enumerate(matches, 1):
                detected_pos_tag = ""
                log_message(
                    f"DEBUG: ─── '{word}' occurrence {match_idx}/{len(matches)} @ position {match.start()} ───",
                    level="DEBUG",
                )
                # Check if this match should be skipped based on context
                if hasattr(ctx, "skip_choice") and ctx.skip_choice:
                    is_skipped = False
                    # Create a small window of text around the match, normalized for whitespace and case
                    window_start = max(0, match.start() - 30)
                    window_end = min(
                        len(self.change_tracker.original_text), match.end() + 30
                    )
                    text_window = self.change_tracker.original_text[
                        window_start:window_end
                    ]
                    normalized_window = " ".join(text_window.lower().split())

                    for skip_phrase in ctx.skip_choice:
                        # Normalize the skip phrase as well
                        normalized_skip_phrase = " ".join(skip_phrase.lower().split())
                        if normalized_skip_phrase in normalized_window:
                            log_message(
                                f"Skipping choice for '{word}' at position {match.start()} due to skip phrase match: '{skip_phrase}'"
                            )
                            is_skipped = True
                            break

                    if is_skipped:
                        continue

                # --- Full Rule-Checking Logic ---
                context_full = self._extract_context(
                    self.change_tracker.original_text,
                    match.start(),
                    match.end(),
                    self.context_size,
                    single_sentence=self.single_sentence_context,
                )

                # --- Check for REPLACE rules first (highest priority) ---
                # Split context to extract before/after, checking that split succeeds
                context_parts = context_full.split(f"[{word}]")
                if len(context_parts) == 2:
                    replace_rule_decision = self._check_replace_rules(
                        word, context_parts[0], context_parts[1], ctx
                    )
                    if replace_rule_decision:
                        pronunciation, explanation = replace_rule_decision
                        self.decision_stats["replace_rule"] += 1

                        # Log REPLACE rule decision
                        short_ctx = self._extract_short_context(
                            self.change_tracker.original_text,
                            match.start(),
                            match.end(),
                            num_words=10,
                            replacement=pronunciation,
                        )
                        self._log_to_choices_log(
                            f"✓ DECISION: '{word}' → '{pronunciation}' | Rule: REPLACE (highest priority)"
                        )
                        self._log_to_choices_log(f"  Context: {short_ctx}")
                        self._log_to_choices_log(f"  Reason: {explanation}")
                        self._log_to_choices_log("")  # Blank line

                        self._log_change(
                            match,
                            word,
                            options,
                            {
                                "choice": pronunciation,
                                "confidence": 1.0,
                                "reason": explanation,
                            },
                            "replace_rule",
                            contextualized_options,
                            detected_pos_tag,
                        )
                        # Log comprehensive entry for REPLACE rule
                        replace_decision = {
                            "choice": pronunciation,
                            "confidence": 1.0,
                            "reason": explanation,
                        }
                        self._log_comprehensive_rule_entry(
                            word,
                            match,
                            {"replace_rule": replace_decision},
                            detected_pos_tag,
                            replace_decision,
                            "replace_rule",
                            options,
                        )
                        continue  # Skip all other rules and AI for this match
                else:
                    log_message(
                        f"WARNING: context_full split failed for word '{word}'. Split returned {len(context_parts)} parts instead of 2.",
                        level="WARNING",
                    )

                # Store the single sentence for _log_rule_choice display
                try:
                    _before, _w, _after = self._extract_sentence_context(
                        self.change_tracker.original_text, match.start(), match.end()
                    )
                    self._current_sentence = (_before + _w + _after).strip()
                except Exception:
                    self._current_sentence = ""

                # Run all local rules
                all_rules, detected_pos_tag = self._run_all_rules(
                    word, context_full, ctx
                )

                # Initialize ai_decision and decision_source before conditional assignment
                ai_decision = None
                decision_source = None

                # Check for consensus
                ai_decision, decision_source = self._get_consensus_from_rules(
                    all_rules, context_full, word, options
                )

                if ai_decision:
                    if self.ai_verify_all and self.ai_service:
                        # AI VERIFY ALL MODE: Rules produced a decision, but AI
                        # must verify EVERY decision per config. Queue the item
                        # for AI batch; store the rule decision as a safe fallback
                        # so we don't lose work if the AI call fails.
                        self._log_to_choices_log(
                            f"Queuing '{word}' for AI verification (Verify ALL mode)."
                        )
                        if all_rules:
                            _rules_summary = ", ".join(
                                f"{r}={v['choice']}({v['confidence']:.2f})"
                                for r, v in all_rules.items()
                            )
                            _ai_reason = f"rule consensus ({decision_source}); verify all — rules fired: {_rules_summary}"
                        else:
                            _ai_reason = (
                                f"rule consensus ({decision_source}); verify all"
                            )
                        self._log_rule_choice(
                            word, "→ AI verify", 0.0, f"queued [{_ai_reason}]"
                        )
                        item_id_counter += 1
                        log_message(
                            f"DEBUG: Queued (verify_all) item_id_counter: {item_id_counter}",
                            level="DEBUG",
                        )

                        meaning_map = {s: m for s, m in (contextualized_options or [])}
                        rich_options = [
                            {"spelling": s, "meaning": meaning_map.get(s, s)}
                            for s in options
                        ]
                        batch_item = {
                            "id": item_id_counter,
                            "word": word,
                            "context": context_full,
                            "options": rich_options,
                        }
                        items_for_ai_batch.append(batch_item)
                        # IMPORTANT: store the *original rule decision and source*
                        # so that if AI batch fails, we can fall back cleanly
                        # without changing the reported source.
                        match_map[item_id_counter] = (
                            match,
                            word,
                            options,
                            contextualized_options,
                            detected_pos_tag,
                            ai_decision,  # rule decision fallback dict
                            decision_source,  # e.g. "complex_pos", "hybrid", etc.
                        )
                    else:
                        # Rule-based decision was made, log it directly
                        self.decision_stats[decision_source] += 1

                        # Log the decision to the batch log with short context
                        short_ctx = self._extract_short_context(
                            self.change_tracker.original_text,
                            match.start(),
                            match.end(),
                            num_words=10,
                            replacement=ai_decision["choice"],
                        )
                        self._log_to_choices_log(
                            f"✓ DECISION: '{word}' → '{ai_decision['choice']}' | Rule: {decision_source}"
                        )
                        self._log_to_choices_log(f"  Context: {short_ctx}")
                        self._log_to_choices_log(f"  Reason: {ai_decision['reason']}")

                        # Log all rules that fired for transparency
                        if len(all_rules) > 1:
                            self._log_to_choices_log(f"  Other rules that fired:")
                            for rule_name, rule_data in all_rules.items():
                                if rule_name != decision_source:
                                    self._log_to_choices_log(
                                        f"    - {rule_name}: '{rule_data['choice']}' | {rule_data['reason']}"
                                    )
                        self._log_to_choices_log("")  # Blank line for readability

                        self._log_change(
                            match,
                            word,
                            options,
                            ai_decision,
                            decision_source,
                            contextualized_options,
                            detected_pos_tag,
                        )
                        # Log comprehensive entry for this word
                        self._log_comprehensive_rule_entry(
                            word,
                            match,
                            all_rules,
                            detected_pos_tag,
                            ai_decision,
                            decision_source,
                            options,
                        )
                elif self.ai_enabled and self.ai_service:
                    # No rule consensus, queue for AI batch
                    self._log_to_choices_log(f"Queuing '{word}' for AI batch analysis.")
                    if all_rules:
                        _rules_summary = ", ".join(
                            f"{r}={v['choice']}({v['confidence']:.2f})"
                            for r, v in all_rules.items()
                        )
                        _ai_reason = f"no consensus — rules fired: {_rules_summary}"
                    else:
                        _ai_reason = (
                            f"no rules fired (POS: {detected_pos_tag or 'unknown'})"
                        )
                    self._log_rule_choice(word, "→ AI", 0.0, f"queued [{_ai_reason}]")
                    item_id_counter += 1
                    log_message(
                        f"DEBUG: Queued item_id_counter: {item_id_counter}",
                        level="DEBUG",
                    )

                    meaning_map = {s: m for s, m in (contextualized_options or [])}
                    rich_options = [
                        {"spelling": s, "meaning": meaning_map.get(s, s)}
                        for s in options
                    ]
                    batch_item = {
                        "id": item_id_counter,
                        "word": word,
                        "context": context_full,
                        "options": rich_options,
                    }
                    items_for_ai_batch.append(batch_item)
                    match_map[item_id_counter] = (
                        match,
                        word,
                        options,
                        contextualized_options,
                        detected_pos_tag,
                        None,  # no rule fallback (no consensus existed)
                        None,
                    )
                else:
                    # RULES-ONLY MODE: Force decision with zero confidence
                    default_decision = None
                    if self.rules_only_mode:
                        # Use first option, force zero confidence
                        forced_choice = options[0] if options else "UNKNOWN"
                        forced_decision = {
                            "choice": forced_choice,
                            "confidence": 0.0,
                            "reason": "Rules-only forced: using first option",
                        }
                        self.decision_stats["rules_only_forced"] += 1
                        self._log_rule_choice(
                            word, forced_choice, 0.0, "rules_only_main_loop"
                        )
                        self._log_change(
                            match,
                            word,
                            options,
                            forced_decision,
                            "rules_only",
                            contextualized_options,
                            detected_pos_tag,
                        )
                        # Log comprehensive entry for this word
                        self._log_comprehensive_rule_entry(
                            word,
                            match,
                            all_rules,
                            detected_pos_tag,
                            forced_decision,
                            "rules_only",
                            options,
                        )
                    else:
                        # No strong rules and no AI. Treat this as a low-confidence
                        # default that explicitly requires human review in the
                        # review window.
                        self.decision_stats["review_needed"] += 1
                        self._log_rule_choice(word, options[0], 0.5, "review_needed")
                        default_decision = {
                            "choice": options[0],
                            "confidence": 0.5,
                            "reason": "Review needed (no strong rules matched, AI disabled)",
                        }

                        # Log default decision
                    short_ctx = self._extract_short_context(
                        self.change_tracker.original_text,
                        match.start(),
                        match.end(),
                        num_words=10,
                        replacement=options[0],
                    )
                    self._log_to_choices_log(
                        f"⚠️  DEFAULT: '{word}' → '{options[0]}' | No strong rules matched, using first option (Review Needed)"
                    )
                    self._log_to_choices_log(f"  Context: {short_ctx}")
                    self._log_to_choices_log(
                        f"  Available options: {', '.join(options)}"
                    )
                    self._log_to_choices_log("")  # Blank line

                    # Use a special decision_source so the GUI can show
                    # "Review Needed" instead of treating this as a strong rule.
                    self._log_change(
                        match,
                        word,
                        options,
                        default_decision,
                        "review_needed",
                        contextualized_options,
                        detected_pos_tag,
                    )
                    # Log comprehensive entry for this word
                    self._log_comprehensive_rule_entry(
                        word,
                        match,
                        all_rules,
                        detected_pos_tag,
                        default_decision,
                        "review_needed",
                        options,
                    )

        # Now, process the batch of items that need AI analysis
        if items_for_ai_batch:
            BATCH_SIZE = 10  # Process in chunks to avoid payload size limits
            all_batch_results = {}
            quota_exhausted = False

            log_message(
                f"Processing {len(items_for_ai_batch)} items in chunks of {BATCH_SIZE}."
            )

            for i in range(0, len(items_for_ai_batch), BATCH_SIZE):
                chunk = items_for_ai_batch[i : i + BATCH_SIZE]

                if quota_exhausted:
                    from ..ai.service import AIResponse

                    for item in chunk:
                        all_batch_results[item["id"]] = AIResponse(
                            False,
                            "",
                            0.0,
                            "Quota exhausted — skipping remaining AI batches",
                        )
                    continue

                log_message(
                    f"Sending chunk {i // BATCH_SIZE + 1} ({len(chunk)} items) to AI for batch analysis. Item IDs: {[item['id'] for item in chunk]}",
                    level="DEBUG",
                )

                try:
                    # Note: The AIResponse class is imported from ..ai.service
                    from ..ai.service import AIResponse

                    # Build example sentences for the unique words in this chunk
                    chunk_words = set(item["word"].lower() for item in chunk)
                    word_examples = {}
                    for w in chunk_words:
                        options = self.lexicon_loader.get_options(w)
                        if options:
                            word_examples[w] = {
                                opt["spelling"]: opt.get("examples", [])
                                for opt in options
                                if opt.get("examples")
                            }

                    chunk_results = self.ai_service.analyze_homographs_batch(
                        chunk, word_examples=word_examples
                    )
                    log_message(
                        f"DEBUG: Received chunk results. Item IDs: {list(chunk_results.keys())}",
                        level="DEBUG",
                    )
                    # Check if quota was exhausted in this batch
                    for resp in chunk_results.values():
                        if not resp.success and "Quota exhausted" in (
                            resp.error_message or ""
                        ):
                            quota_exhausted = True
                            break
                    all_batch_results.update(chunk_results)
                except Exception as e:
                    log_message(
                        f"Error processing chunk {i // BATCH_SIZE + 1}: {e}",
                        level="ERROR",
                    )
                    # Create failure responses for items in this chunk
                    for item in chunk:
                        all_batch_results[item["id"]] = AIResponse(
                            False, "", 0.0, f"Batch request failed: {e}"
                        )

            # Process the combined results from all chunks
            for item_id, ai_response in all_batch_results.items():
                log_message(f"DEBUG: Processing item_id: {item_id}", level="DEBUG")
                (
                    match,
                    word,
                    options,
                    contextualized_options,
                    detected_pos_tag,
                    rule_decision,
                    rule_source,
                ) = match_map[item_id]
                decision_source = "llm"
                ai_decision = None

                if ai_response.success:
                    ai_decision = {
                        "choice": ai_response.content,
                        "confidence": ai_response.confidence,
                        "reason": ai_response.reasoning,
                    }
                    self.decision_stats[decision_source] += 1
                    self._log_rule_choice(
                        word, ai_response.content, ai_response.confidence, "llm"
                    )
                else:
                    if rule_decision is not None and rule_source is not None:
                        # VERIFY_ALL MODE fallback: rule had a consensus, use it
                        # and preserve the original rule source tag.
                        ai_decision = rule_decision
                        decision_source = rule_source
                        self.decision_stats[decision_source] += 1
                        self._log_rule_choice(
                            word,
                            ai_decision["choice"],
                            ai_decision.get("confidence", 0.0),
                            f"ai_failed→{rule_source}",
                        )
                    else:
                        # Old behavior: no prior rule consensus, fall back to first option
                        decision_source = "default"
                        ai_decision = {
                            "choice": options[0],
                            "confidence": 0.5,
                            "reason": f"AI batch failed: {ai_response.error_message}",
                        }
                        self.decision_stats[decision_source] += 1
                        self._log_rule_choice(
                            word, options[0], 0.5, "ai_failed→default"
                        )

                self._log_change(
                    match,
                    word,
                    options,
                    ai_decision,
                    decision_source,
                    contextualized_options,
                    detected_pos_tag,
                )
                # Log comprehensive entry for this word
                self._log_comprehensive_rule_entry(
                    word,
                    match,
                    {},
                    detected_pos_tag,
                    ai_decision,
                    decision_source,
                    options,
                )

        log_message(
            f"AI review mode complete: {len(self.change_tracker.changes)} decisions logged for review"
        )
        self._log_to_choices_log(f"\n=== AI CHOICES BATCH PROCESSING COMPLETED ===")
        log_message(
            f"AI review mode complete: {len(self.change_tracker.changes)} changes processed for review"
        )
        self._write_end_of_run_summary()
        log_message("DEBUG: Exiting process_choices_ai_review_mode", level="DEBUG")
        return self.change_tracker

    def _run_all_rules(
        self, word: str, context_full: str, ctx: "BookfixContext"
    ) -> Tuple[Dict, str]:
        """Helper to run all local rules and return their results and the detected POS tag."""
        log_message(f"DEBUG: Entering _run_all_rules for word: '{word}'", level="DEBUG")
        log_message(
            f"DEBUG: _run_all_rules context_full: '{context_full}'", level="DEBUG"
        )

        all_rules = {}
        detected_pos_tag = ""
        pos_token = None
        dep_info = None
        doc = None

        # Extract bracket context using case-insensitive match
        import re

        match = re.search(r"\[" + re.escape(word) + r"\]", context_full, re.IGNORECASE)
        if not match:
            log_message(
                f"DEBUG: _run_all_rules: bracket '[{word}]' not found in context_full",
                level="DEBUG",
            )
            return {}, ""
        # Extract actual matched text to preserve original case (e.g., "Polish" not "polish")
        actual_word_text = match.group()[1:-1]
        bracket_start = match.start()
        context_before = context_full[:bracket_start]
        context_after = context_full[bracket_start + len(actual_word_text) + 2 :]
        log_message(
            f"DEBUG: _run_all_rules context_before: '{context_before}', context_after: '{context_after}'",
            level="DEBUG",
        )

        if self.use_pos_tagging and self.pos_tagger:
            log_message(
                f"DEBUG: _run_all_rules: Attempting POS tagging for '{word}'",
                level="DEBUG",
            )
            # Get rich spaCy context
            try:
                pos_token, dep_info, doc = self.pos_tagger.get_token_and_dependency(
                    context_before, word, context_after
                )
                if pos_token:
                    detected_pos_tag = pos_token.pos_tag
                    log_message(
                        f"DEBUG: _run_all_rules: Detected POS tag for '{word}': '{detected_pos_tag}'",
                        level="DEBUG",
                    )
                else:
                    log_message(
                        f"DEBUG: _run_all_rules: No POS token found for '{word}'",
                        level="DEBUG",
                    )
            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Error during POS tagging: {e}",
                    level="DEBUG",
                )

        # Hybrid decider check: if word has a specialized decider, use it
        if word.lower() in DECIDERS and pos_token and dep_info and doc:
            log_message(
                f"DEBUG: _run_all_rules: Using hybrid decider for '{word}'",
                level="DEBUG",
            )
            try:
                # Load NLI if needed for this word
                if word.lower() in NLI_WORDS:
                    self._ensure_nli_services()

                # Extract sentence from context
                sentence = (
                    context_before.rstrip()
                    + " "
                    + actual_word_text
                    + " "
                    + context_after.lstrip()
                )

                # Get parameters from spaCy structures
                tag = pos_token.pos_tag  # Fine-grained tag (VBN, NN, etc.)
                dep = dep_info.dep_relation  # Dependency relation (nsubj, dobj, etc.)
                head_text = dep_info.head_word.lower() if dep_info.head_word else ""

                # Check if word has a determiner child by checking the doc
                # Find the target token in the doc to check its children
                target_token_in_doc = None
                word_lower = word.lower()
                for token in doc:
                    if token.text.lower() == word_lower and token.i == pos_token.index:
                        target_token_in_doc = token
                        break
                has_det = (
                    any(c.dep_ == "det" for c in target_token_in_doc.children)
                    if target_token_in_doc
                    else False
                )

                # Call the hybrid decider
                decider_fn = DECIDERS[word.lower()]
                pronunciation, route = decider_fn(
                    tag, dep, head_text, has_det, self.nli, sentence
                )

                all_rules["hybrid"] = {
                    "choice": pronunciation,
                    "confidence": 0.95,  # High confidence for hand-tuned deciders
                    "reason": f"Hybrid decider ({route})",
                }
                log_message(
                    f"DEBUG: _run_all_rules: Hybrid decider matched '{word}' → '{pronunciation}' ({route})",
                    level="DEBUG",
                )
                self._log_rule_evaluation(
                    word,
                    "hybrid",
                    f"Tag: {tag}, Dep: {dep}",
                    f"Match: {pronunciation} ({route})",
                )

            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Hybrid decider error for '{word}': {e}",
                    level="DEBUG",
                )
                # Fall through to generic rules if hybrid fails

        # Rule 1: Complex POS rules (e.g., imperative verbs)
        if self.pos_dictionary and pos_token and dep_info and doc:
            log_message(
                f"DEBUG: _run_all_rules: Checking complex POS rules for '{word}'",
                level="DEBUG",
            )
            try:
                complex_pos_result = (
                    self.pos_dictionary.get_pronunciation_by_complex_pos_rules(
                        actual_word_text, pos_token, dep_info, doc
                    )
                )
                if complex_pos_result:
                    all_rules["complex_pos"] = {
                        "choice": complex_pos_result,
                        "confidence": 0.98,
                        "reason": f"Complex POS rule for '{word}'",
                    }
                    log_message(
                        f"DEBUG: _run_all_rules: Complex POS rule matched: '{complex_pos_result}'",
                        level="DEBUG",
                    )
                    self._log_rule_evaluation(
                        word,
                        "complex_pos",
                        f"POS: {detected_pos_tag}, Dep: {dep_info}",
                        "Match" if complex_pos_result else "No match",
                    )
                else:
                    self._log_rule_evaluation(
                        word,
                        "complex_pos",
                        f"POS: {detected_pos_tag}, Dep: {dep_info}",
                        "No match",
                    )
            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Error checking complex POS rules: {e}",
                    level="DEBUG",
                )
                self._log_rule_evaluation(word, "complex_pos", "Error", str(e))

        # Rule 2: Simple POS tagging (fallback if complex doesn't match)
        log_message(
            f"DEBUG: _run_all_rules: Checking simple POS rule for '{word}'",
            level="DEBUG",
        )
        pos_result = self._get_pos_based_choice(word, context_before, context_after)
        if pos_result:
            pronunciation, confidence, explanation = pos_result
            all_rules["pos"] = {
                "choice": pronunciation,
                "confidence": confidence,
                "reason": f"POS-based: {explanation} [Tag: {detected_pos_tag}]",
            }
            log_message(
                f"DEBUG: _run_all_rules: Simple POS rule matched: '{pronunciation}'",
                level="DEBUG",
            )
            self._log_rule_evaluation(
                word,
                "pos",
                f"POS: {detected_pos_tag}, Explanation: {explanation}",
                f"Match: {pronunciation}",
            )
        else:
            self._log_rule_evaluation(
                word, "pos", f"POS: {detected_pos_tag}", "No match"
            )

        if self.pos_dictionary:
            # Rule 3: Semantic matching
            log_message(
                f"DEBUG: _run_all_rules: Checking semantic rule for '{word}'",
                level="DEBUG",
            )
            before_tokens = re.findall(r"\b\w+\b", context_before.lower())[-10:]
            after_tokens = re.findall(r"\b\w+\b", context_after.lower())[:10]
            try:
                semantic_result = self.pos_dictionary.get_pronunciation_by_semantic(
                    word, before_tokens + after_tokens
                )
                if semantic_result:
                    pronunciation, matched_tag, confidence = semantic_result
                    all_rules["semantic"] = {
                        "choice": pronunciation,
                        "confidence": confidence,
                        "reason": f"Semantic: nearby word '{matched_tag}'",
                    }
                    log_message(
                        f"DEBUG: _run_all_rules: Semantic rule matched: '{pronunciation}'",
                        level="DEBUG",
                    )
                    self._log_rule_evaluation(
                        word,
                        "semantic",
                        f"Tokens: {before_tokens + after_tokens}",
                        f"Match: {pronunciation} (tag: {matched_tag})",
                    )
                else:
                    self._log_rule_evaluation(
                        word,
                        "semantic",
                        f"Tokens: {before_tokens + after_tokens}",
                        "No match",
                    )
            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Error checking semantic rule: {e}",
                    level="DEBUG",
                )
                self._log_rule_evaluation(word, "semantic", "Error", str(e))

            # Rule 4: Named entity context
            log_message(
                f"DEBUG: _run_all_rules: Checking entity rule for '{word}'",
                level="DEBUG",
            )
            try:
                entity_result = self.pos_dictionary.check_entity_context(
                    word, context_before, context_after
                )
                if entity_result:
                    all_rules["entity"] = {
                        "choice": entity_result,
                        "confidence": 0.85,
                        "reason": f"Entity context: '{entity_result}'",
                    }
                    log_message(
                        f"DEBUG: _run_all_rules: Entity rule matched: '{entity_result}'",
                        level="DEBUG",
                    )
                    self._log_rule_evaluation(
                        word,
                        "entity",
                        f"Context: {context_before} ... {context_after}",
                        f"Match: {entity_result}",
                    )
                else:
                    self._log_rule_evaluation(
                        word,
                        "entity",
                        f"Context: {context_before} ... {context_after}",
                        "No match",
                    )
            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Error checking entity rule: {e}",
                    level="DEBUG",
                )
                self._log_rule_evaluation(word, "entity", "Error", str(e))

        log_message(
            f"DEBUG: Exiting _run_all_rules for word: '{word}'. Found rules: {list(all_rules.keys())}",
            level="DEBUG",
        )
        return all_rules, detected_pos_tag

    def _log_comprehensive_rule_entry(
        self,
        word: str,
        match,
        all_rules: Dict,
        detected_pos_tag: str,
        decision: Dict,
        decision_source: str,
        options: List,
    ):
        """Log a comprehensive, readable entry for each word processed."""
        import os
        import datetime

        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
        log_path = os.path.join(log_dir, "logs", "rule_reasoning.log")

        # Get single sentence context
        full_text = self.change_tracker.original_text
        match_start = match.start()
        match_end = match.end()
        context_before, word_in_sent, context_after = self._extract_sentence_context(
            full_text, match_start, match_end
        )
        sentence = f"{context_before}[{word_in_sent}]{context_after}"

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        confidence = decision.get("confidence", 0.0) if decision else 0.0
        chosen = decision.get("choice", "UNKNOWN") if decision else "UNKNOWN"
        reason = decision.get("reason", "") if decision else ""

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f'=== ENTRY: "{word}" @ {timestamp} ===\n')
            f.write(f"Sentence: {sentence}\n")
            f.write(f"POS: {detected_pos_tag}\n")
            f.write(f"\nRULE RESULTS:\n")

            # Log each rule that fired
            if all_rules:
                for rule_name, rule_data in all_rules.items():
                    rule_choice = rule_data.get("choice", "none")
                    rule_conf = rule_data.get("confidence", 0.0)
                    rule_reason = rule_data.get("reason", "")
                    f.write(
                        f"  {rule_name}: {rule_choice} (conf: {rule_conf:.2f}) - {rule_reason}\n"
                    )
            else:
                f.write(f"  No rules fired\n")

            f.write(
                f"\nFINAL DECISION: {chosen} (confidence: {confidence:.2f}, source: {decision_source})\n"
            )
            f.write(f"  Reason: {reason}\n")
            f.write(f"  Available options: {options}\n")

            # Consensus explanation: show why winner beat runner-up
            if all_rules and len(all_rules) > 0:
                sorted_rules = sorted(
                    all_rules.items(),
                    key=lambda x: x[1].get("confidence", 0.0),
                    reverse=True,
                )
                winner_name, winner_data = sorted_rules[0]
                if all(r.get("choice") == chosen for _, r in all_rules.items()):
                    f.write(
                        f"  Consensus: unanimous — all {len(all_rules)} rules chose {chosen}\n"
                    )
                elif decision_source in ("complex_pos", "replace_rule"):
                    f.write(
                        f"  Consensus: {decision_source} override ({confidence:.2f}) — structural rule takes priority\n"
                    )
                elif len(sorted_rules) > 1:
                    runner_name, runner_data = sorted_rules[1]
                    margin = sorted_rules[0][1].get("confidence", 0.0) - sorted_rules[
                        1
                    ][1].get("confidence", 0.0)
                    winner_choice = winner_data.get("choice", "?")
                    runner_choice = runner_data.get("choice", "?")
                    if winner_choice != runner_choice:
                        f.write(
                            f"  Consensus: {decision_source}({confidence:.2f}) beat {runner_name}({runner_data.get('confidence', 0.0):.2f}) — margin: {margin:.2f} — DISAGREEMENT\n"
                        )
                    else:
                        f.write(
                            f"  Consensus: {decision_source}({confidence:.2f}) selected over {runner_name}({runner_data.get('confidence', 0.0):.2f}) — margin: {margin:.2f}\n"
                        )
                else:
                    f.write(
                        f"  Consensus: only rule — {decision_source}({confidence:.2f})\n"
                    )
            f.write("---\n")

    def _get_consensus_from_rules(
        self, all_rules: Dict, context_full: str, word: str = "", options: List = None
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Check for consensus among rule results.

        Args:
            all_rules: Dictionary of rule results
            context_full: Full context around the word
            word: The word being processed
            options: List of available replacement options for this word

        Strategy:
        1. If all rules agree on the same choice → consensus
        2. If rules disagree:
           - AI enabled → return None (send to AI)
           - AI disabled → fall back to strict priority
        3. If no rules matched → return None (or force in rules_only_mode)

        NOTE: We intentionally avoid allowing a lower-priority rule (e.g. plain
        'keyword') to win over higher-priority rules (complex_pos/entity/pos/
        semantic) based solely on a slightly higher numeric confidence.
        Additionally, **keyword-only** matches are treated as **no decision** so
        they are always surfaced as low-confidence items for review (or sent to
        AI), never as standalone rules.
        """
        # ===== RULES-ONLY MODE: Apply confidence floor, defer to review if below threshold =====
        if self.rules_only_mode:
            log_message(
                f"Rules-only mode: Checking decision for '{word}' (rules: {list(all_rules.keys()) if all_rules else 'none'})",
                level="DEBUG",
            )
            min_confidence = self.config.get("Thresholds", {}).get(
                "MIN_CONFIDENCE_THRESHOLD", 0.75
            )
            # Log to rule_choice log for tracking
            if not all_rules:
                forced_choice = (
                    options[0] if options and len(options) > 0 else "UNKNOWN"
                )
                self._log_rule_choice(word, forced_choice, 0.0, "rules_only_no_rules")
                return {
                    "choice": forced_choice,
                    "confidence": 0.0,
                    "reason": "Rules-only: no rules",
                }, "rules_only"
            # Check if any rule meets confidence threshold
            if all_rules:
                best_name = max(all_rules, key=lambda r: all_rules[r]["confidence"])
                best = all_rules[best_name]
                if best["confidence"] >= min_confidence:
                    # Meets threshold - use with actual confidence
                    best_copy = best.copy()
                    best_copy["reason"] = f"Rules-only: {best['reason']}"
                    self._log_rule_choice(
                        word,
                        best_copy["choice"],
                        best_copy["confidence"],
                        f"rules_only_{best_name}",
                    )
                    return best_copy, best_name
                else:
                    # Below threshold - defer to review
                    log_message(
                        f"Rules-only mode: Confidence {best['confidence']:.2f} below threshold {min_confidence:.2f}, deferring to review",
                        level="DEBUG",
                    )
                    return None, None
            # Fallback
            forced_choice = options[0] if options and len(options) > 0 else "UNKNOWN"
            self._log_rule_choice(word, forced_choice, 0.0, "rules_only_fallback")
            return {
                "choice": forced_choice,
                "confidence": 0.0,
                "reason": "Rules-only fallback",
            }, "rules_only"

        # ===== HYBRID/VERIFY MODES: complex_pos > hybrid > pos; all others → AI =====
        if not all_rules:
            return None, None

        # Rule 1: complex_pos (dep_rules) always wins — 0.98 confidence structural rule
        if "complex_pos" in all_rules:
            rule_decision = all_rules["complex_pos"]
            self._log_rule_choice(
                word,
                rule_decision["choice"],
                rule_decision["confidence"],
                "complex_pos",
            )
            return rule_decision, "complex_pos"

        # Rule 2: hybrid deciders — hand-tuned per-word logic, 0.95 confidence
        if "hybrid" in all_rules:
            rule_decision = all_rules["hybrid"]
            self._log_rule_choice(
                word, rule_decision["choice"], rule_decision["confidence"], "hybrid"
            )
            return rule_decision, "hybrid"

        # Rule 3: POS tag — reliable only when pronunciations differ by part of speech
        if "pos" in all_rules:
            rule_decision = all_rules["pos"]
            if rule_decision["confidence"] >= 0.80:
                self._log_rule_choice(
                    word, rule_decision["choice"], rule_decision["confidence"], "pos"
                )
                return rule_decision, "pos"

        # Rules 4–7 (semantic, entity, definition, keyword) are not trusted to decide.
        # Log which rules fired for diagnostics, then queue for AI.
        fired = ", ".join(
            f"{k}={v['choice']}({v['confidence']:.2f})" for k, v in all_rules.items()
        )
        log_message(
            f"DEBUG: no autonomous decision — queuing for AI. Rules fired: {fired}",
            level="DEBUG",
        )
        return None, None

    def _log_rule_choice(
        self, word: str, choice: str, confidence: float, rule_type: str
    ):
        """Log rule choices to separate file."""
        import os, re

        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
        log_path = os.path.join(log_dir, "logs", "rules_choices.log")
        sentence = getattr(self, "_current_sentence", "")
        log_line = (
            f"{word} -> {choice} (confidence {confidence:.2f}, rule: {rule_type})"
        )
        if sentence:
            log_line += f" | {sentence}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

    def _log_rule_evaluation(self, word: str, rule: str, details: str, result: str):
        """Log each rule evaluation attempt."""
        import os
        import datetime

        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
        log_path = os.path.join(
            log_dir, "logs", "rule_evaluation.log"
        )  # Changed to separate file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"[{timestamp}] Word: '{word}' | Rule: {rule} | {details} | Result: {result}\n"
            )

    def _log_ai_choice(self, word: str, choice: str, confidence: float, reason: str):
        """Log AI choices to separate file."""
        import os

        log_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(log_dir, "ai_choices.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(
                f"{word} -> {choice} (confidence {confidence:.2f}, reason: {reason})\n"
            )
            # AI disabled - use a simple majority if there is one, otherwise
            # fall back to strict priority (no confidence-based tie-breaking).
            from collections import Counter

            vote_counts = Counter(choices)
            most_common_choice, vote_count = vote_counts.most_common(1)[0]

            total_votes = len(choices)
            if vote_count > total_votes / 2:
                # Clear majority - find which rule suggested it (prefer higher priority)
                priority_order = ["complex_pos", "entity", "pos", "semantic", "keyword"]
                for rule_name in priority_order:
                    if (
                        rule_name in all_rules
                        and all_rules[rule_name]["choice"] == most_common_choice
                    ):
                        consensus_decision = all_rules[rule_name].copy()
                        consensus_decision["reason"] = (
                            f"Consensus ({vote_count}/{total_votes} rules agree): {consensus_decision['reason']}"
                        )
                        return consensus_decision, f"consensus_{rule_name}"

            # No clear majority (tie or even split) - fall back purely to
            # strict priority order, ignoring confidence.
            log_message(
                f"DEBUG: No clear consensus, using strict priority fallback",
                level="DEBUG",
            )
            priority_order = ["complex_pos", "entity", "pos", "semantic", "keyword"]
            for rule_name in priority_order:
                if rule_name in all_rules:
                    return all_rules[rule_name], rule_name

        # Should never reach here, but safety fallback
        return None, None

    def _log_change(
        self,
        match,
        word,
        options,
        decision,
        decision_source,
        contextualized_options,
        detected_pos_tag: str,
    ):
        """Helper function to log a change to the change tracker."""
        # This helper centralizes the logic for adding a change to the tracker
        if decision is None:
            log_message(
                f"WARNING: _log_change called with None decision for word '{word}'",
                level="WARNING",
            )
            return
        replacement = decision["choice"]
        confidence = decision["confidence"]
        reason = decision.get("reason", "")

        # Calculate context_before and context_after directly from original_text
        # This avoids issues with splitting context_full if the bracketed word is not found or malformed
        full_text = self.change_tracker.original_text
        match_start_in_full_text = match.start()
        match_end_in_full_text = match.end()

        # Always extract 250-character context for review window display
        context_start_raw = max(0, match_start_in_full_text - self.context_size)
        context_end_raw = min(
            len(full_text), match_end_in_full_text + self.context_size
        )

        log_message(
            f"DEBUG: _log_change - len(full_text): {len(full_text)}, match.start(): {match.start()}, match.end(): {match.end()}, context_start_raw: {context_start_raw}, match_start_in_full_text: {match_start_in_full_text}, match_end_in_full_text: {match_end_in_full_text}, context_end_raw: {context_end_raw}",
            level="DEBUG",
        )
        # The actual context_before and context_after for logging should be the raw text around the match
        # up to the match boundaries, within the context_size window.
        # This is the text *before* the matched word, within the context window
        actual_context_before = full_text[context_start_raw:match_start_in_full_text]
        # This is the text *after* the matched word, within the context window
        actual_context_after = full_text[match_end_in_full_text:context_end_raw]

        # Also extract single sentence context for learning storage
        sentence_before, _, sentence_after = self._extract_sentence_context(
            full_text, match_start_in_full_text, match_end_in_full_text
        )
        sentence_context = f"{sentence_before} {sentence_after}".strip()

        self.change_tracker.add_change(
            module_name="choices",
            original=match.group(0),
            replacement=replacement,
            options=options,
            start_pos=match.start(),
            end_pos=match.end(),
            context_before=actual_context_before,
            context_after=actual_context_after,
            confidence=confidence,
            reasoning=reason,
            pos_tag=detected_pos_tag,
            decision_source=decision_source,
            sentence_context=sentence_context,
        )

    def get_decision_statistics(self) -> Dict:
        """Get statistics about decision sources."""
        return self.decision_stats

    def process_choices_ai(self, ctx: "BookfixContext") -> str:
        """
        Process choices using AI analysis with rules-only fallback (review mode).

        Args:
            ctx: BookfixContext with text and choices to process

        Returns:
            Processed text
        """
        if not self.ai_enabled or not self.ai_service:
            log_message("AI not available, using rules-only mode (review window)")
            log_message(
                f"DEBUG: ai_enabled={self.ai_enabled}, ai_service={self.ai_service is not None}"
            )
            # Use review mode with rules (POS tagging, keywords, etc.) instead of manual fallback
            tracker = self.process_choices_ai_review_mode(ctx, force_all=False)
            log_message(
                f"DEBUG: process_choices_ai_review_mode returned tracker={tracker is not None}"
            )
            if tracker:
                log_message(
                    f"DEBUG: Returning text from tracker, changes={len(tracker.changes)}"
                )
                return (
                    tracker.current_text
                    if hasattr(tracker, "current_text")
                    else ctx.text
                )
            else:
                log_message("Review mode failed, falling back to manual processing")
                return self.process_choices(ctx)

        # Initialize POS services BEFORE processing any words (needed for contextual analysis)
        if self.use_pos_tagging:
            self._ensure_pos_services()
            # Refresh dictionary reference in case keywords were updated via keyword dialog
            self._refresh_pos_dictionary()

        log_message(
            f"Starting AI choice processing with {len(ctx.choices)} choice rules"
        )

        # Reset tracking
        self.ai_decisions = []
        self.manual_decisions = []

        # Process each choice rule - prioritize contextualized choices
        words_to_process = set(ctx.choices.keys())

        for word in words_to_process:
            log_message(f"Processing word '{word}' with AI analysis")

            # Find all matches of this word in the text
            matches = self._find_matches(word, ctx.text)

            if not matches:
                continue

            # Get options (prioritize contextualized if available)
            contextualized_options = ctx.contextualized_choices.get(word)
            regular_options = ctx.choices.get(word, [])
            # Build options list: prefer regular options, fall back to contextualized options
            if regular_options:
                options = regular_options
            elif contextualized_options:
                options = [opt for opt, _ in contextualized_options]
            else:
                options = []

            # Process matches in reverse order (rightmost first) to avoid position corruption
            for match in reversed(matches):
                context = self._extract_context(
                    ctx.text,
                    match.start(),
                    match.end(),
                    self.context_size,
                    single_sentence=self.single_sentence_context,
                )

                # Try AI analysis - use contextualized method if available
                if contextualized_options:
                    ai_decision = self._analyze_with_contextualized_ai(
                        word, context, contextualized_options
                    )
                else:
                    ai_decision = self._analyze_with_ai(word, context, regular_options)

                if (
                    ai_decision
                    and ai_decision["confidence"] >= self.confidence_threshold
                ):
                    # Apply AI decision
                    original_word = ctx.text[match.start() : match.end()]
                    replacement = ai_decision["choice"]

                    # Replace in text
                    ctx.text = (
                        ctx.text[: match.start()]
                        + replacement
                        + ctx.text[match.end() :]
                    )

                    log_message(
                        f"AI replaced '{original_word}' with '{replacement}' (confidence: {ai_decision['confidence']:.2f})"
                    )

                    self.ai_decisions.append(
                        {
                            "word": word,
                            "match": match,
                            "context": context,
                            "decision": ai_decision,
                            "position": match.start(),
                        }
                    )
                else:
                    # Queue for manual processing
                    if self.fallback_to_manual:
                        self.manual_decisions.append(
                            {
                                "word": word,
                                "match": match,
                                "context": context,
                                "options": options,
                                "ai_reason": (
                                    ai_decision.get("reason", "Low confidence")
                                    if ai_decision
                                    else "AI analysis failed"
                                ),
                            }
                        )
                    else:
                        log_message(
                            f"Skipping '{word}' - AI confidence too low and manual fallback disabled"
                        )

        log_message(
            f"AI processing complete: {len(self.ai_decisions)} automatic, {len(self.manual_decisions)} manual"
        )

        # If there are manual decisions to make, process them
        if self.manual_decisions and self.fallback_to_manual:
            self._process_manual_decisions(ctx)

        # Update positions for any remaining changes after text modifications
        self.change_tracker.update_positions_after_text_change(ctx.text)

        return ctx.text

    def _analyze_with_ai(
        self,
        word: str,
        context: str,
        options: List[str],
        best_guess: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Analyze a word choice using AI, enriched with definitions/POS/examples from choices.json when available.

        Args:
            word: The word to analyze
            context: Context around the word
            options: List of possible replacements
            best_guess: A preliminary guess from local rules to be verified by the AI

        Returns:
            Dictionary with AI decision or None if failed
        """
        try:
            # Enrich with definitions, POS, and examples from ctx.choice_definitions
            definitions = []
            if (
                hasattr(self, "ctx")
                and self.ctx
                and word.lower() in getattr(self.ctx, "choice_definitions", {})
            ):
                entry = self.ctx.choice_definitions[word.lower()]
                for opt in entry.get("options", []):
                    definitions.append(
                        f"{opt['spelling']} ({opt.get('definition', '')}) [{opt.get('pos', 'UNKNOWN')}]"
                    )

            # Call AI service with enriched contextualized options
            contextualized_options = []
            for opt in options:
                desc = ""
                if definitions:
                    # Find matching definition
                    for d in definitions:
                        if opt.lower() in d.lower():
                            desc = d
                            break
                contextualized_options.append((opt, desc))

            response = self.ai_service.analyze_contextualized_homograph(
                word,
                context,
                contextualized_options,
                show_reasoning=True,
                best_guess=best_guess,
            )

            if response.success:
                # Log AI decision
                self._log_ai_choice(
                    word,
                    response.content,
                    response.confidence,
                    response.reasoning or "AI decision",
                )
                return {
                    "choice": response.content,
                    "confidence": response.confidence,
                    "reason": response.reasoning
                    or f"AI chose {response.content} using definition",
                }
            else:
                log_message(
                    f"AI analysis failed for '{word}': {response.error_message}"
                )
                return None

        except Exception as e:
            log_message(f"AI analysis error for '{word}': {e}", level="ERROR")
            return None

    def _analyze_with_contextualized_ai(
        self,
        word: str,
        context: str,
        contextualized_options: List[Tuple[str, str]],
        show_reasoning: Optional[bool] = None,
        best_guess: Optional[str] = None,
        detected_pos_tag: Optional[str] = None,
        context_keywords: Optional[Dict[str, List[str]]] = None,
    ) -> Optional[Dict]:
        """
        Analyze a word choice using AI with context definitions.

        Args:
            word: The word to analyze
            context: Context around the word
            contextualized_options: List of (spelling, meaning) tuples
            show_reasoning: Override for self.show_reasoning if provided
            best_guess: A preliminary guess from local rules to be verified by the AI
            detected_pos_tag: POS tag from spaCy (VB, NN, etc.) - optional clue for AI
            context_keywords: Dict mapping spelling to keywords indicating that pronunciation - optional clues

        Returns:
            Dictionary with AI decision or None if failed
        """
        try:
            # Determine whether to show reasoning for this specific call
            use_reasoning = (
                self.show_reasoning if show_reasoning is None else show_reasoning
            )

            # If POS tag not provided, try to detect it
            if detected_pos_tag is None and self.pos_tagger is not None:
                context_before = (
                    context[: context.rfind(word)] if word in context else ""
                )
                context_after = (
                    context[context.rfind(word) + len(word) :]
                    if word in context
                    else ""
                )
                detected_pos_tag = self.pos_tagger.tag_with_context(
                    context_before, word, context_after
                )
                if detected_pos_tag:
                    log_message(
                        f"DEBUG: Extracted POS tag for '{word}': {detected_pos_tag}",
                        level="DEBUG",
                    )

            # If keywords not provided, try to extract them from dictionary
            if context_keywords is None and self.pos_dictionary is not None:
                context_keywords = {}
                for spelling, _ in contextualized_options:
                    option_info = self.pos_dictionary.get_option_info(word, spelling)
                    if option_info:
                        keywords = option_info.get("context_keywords", [])
                        context_keywords[spelling] = keywords
                        if keywords:
                            log_message(
                                f"DEBUG: Found keywords for '{word}' → '{spelling}': {keywords}",
                                level="DEBUG",
                            )
                    else:
                        context_keywords[spelling] = []

            # Call AI service
            response = self.ai_service.analyze_contextualized_homograph(
                word,
                context,
                contextualized_options,
                use_reasoning,
                best_guess=best_guess,
                detected_pos_tag=detected_pos_tag,
                context_keywords=context_keywords,
            )

            if response.success:
                return {
                    "choice": response.content,
                    "confidence": response.confidence,
                    "reason": response.reasoning
                    or f"AI chose {response.content} based on context",
                }
            else:
                log_message(
                    f"Contextualized AI analysis failed for '{word}': {response.error_message}"
                )
                return None

        except Exception as e:
            log_message(
                f"Contextualized AI analysis error for '{word}': {e}", level="ERROR"
            )
            return None

    def _apply_ai_decision(self, ctx: "BookfixContext", match, decision: Dict) -> None:
        """Apply an AI decision to the text."""
        original_word = ctx.text[match.start() : match.end()]
        replacement = decision["choice"]

        # Replace in text
        ctx.text = ctx.text[: match.start()] + replacement + ctx.text[match.end() :]

        log_message(
            f"AI replaced '{original_word}' with '{replacement}' (confidence: {decision['confidence']:.2f})"
        )

    def _process_manual_decisions(self, ctx: "BookfixContext") -> None:
        """Process remaining decisions manually using the interactive processor."""
        log_message(f"Processing {len(self.manual_decisions)} manual decisions")

        # Create a temporary context with only the manual decisions
        manual_ctx = type(ctx)()  # Create new context of same type
        manual_ctx.text = ctx.text
        manual_ctx.choices = {}

        # Group manual decisions by word
        for decision in self.manual_decisions:
            word = decision["word"]
            if word not in manual_ctx.choices:
                manual_ctx.choices[word] = decision["options"]

        # Process using parent class
        manual_result = super().process_choices(manual_ctx)
        ctx.text = manual_result.text

    def _extract_sentence_context(
        self, text: str, start: int, end: int
    ) -> Tuple[str, str, str]:
        """
        Extract ONLY the sentence containing the match using NLTK sentence tokenization.

        Args:
            text: Full text
            start: Start position of match
            end: End position of match

        Returns:
            Tuple of (context_before, word, context_after) for the single sentence
        """
        from nltk.tokenize import sent_tokenize

        try:
            sentences = sent_tokenize(text)
        except Exception as e:
            log_message(
                f"NLTK sentence tokenization failed: {e}, falling back to character-based",
                level="WARNING",
            )
            # Fallback to character-based
            before = text[max(0, start - 100) : start]
            after = text[end : min(len(text), end + 100)]
            return before, text[start:end], after

        # Find which sentence contains the match
        current_pos = 0
        for sent in sentences:
            sent_start = text.find(sent, current_pos)
            if sent_start == -1:
                continue
            sent_end = sent_start + len(sent)

            # Check if match is within this sentence
            if sent_start <= start < sent_end:
                word = text[start:end]
                # Get context before and after within this sentence
                sent_before = text[sent_start:start]
                sent_after = text[end:sent_end]
                log_message(
                    f"DEBUG: Single sentence context: '{sent_before}[{word}]{sent_after}'",
                    level="DEBUG",
                )
                return sent_before, word, sent_after

            current_pos = sent_end

        # Fallback: no sentence found, use character-based
        log_message(
            f"Could not find sentence containing match at {start}-{end}, using fallback",
            level="WARNING",
        )
        before = text[max(0, start - 100) : start]
        after = text[end : min(len(text), end + 100)]
        return before, text[start:end], after

    def _extract_context(
        self,
        text: str,
        start: int,
        end: int,
        context_size: int = 100,
        single_sentence: bool = False,
    ) -> str:
        """
        Extract context around a match.

        Args:
            text: Full text
            start: Start position of match
            end: End position of match
            context_size: Characters to include before/after
            single_sentence: If True, use NLTK to extract only the containing sentence

        Returns:
            Context string with the target word highlighted
        """
        log_message(
            f"DEBUG: _extract_context - len(text): {len(text)}, start: {start}, end: {end}, context_size: {context_size}, single_sentence: {single_sentence}",
            level="DEBUG",
        )

        if single_sentence:
            context_before, word, context_after = self._extract_sentence_context(
                text, start, end
            )
            return f"{context_before}[{word}]{context_after}"

        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)

        before = text[context_start:start]
        word = text[start:end]
        after = text[end:context_end]

        return f"{before}[{word}]{after}"

    def _extract_short_context(
        self,
        text: str,
        start: int,
        end: int,
        num_words: int = 10,
        replacement: str = None,
        single_sentence: bool = False,
    ) -> str:
        """
        Extract a short context showing N words before and after the match.

        Args:
            text: Full text
            start: Start position of match
            end: End position of match
            num_words: Number of words to include before/after (default: 10)
            replacement: Optional replacement word to show instead of matched word
            single_sentence: If True, extract only the containing sentence

        Returns:
            Short context string with the target word highlighted
        """
        import re

        # Use single sentence mode if requested
        if single_sentence:
            context_before, word, context_after = self._extract_sentence_context(
                text, start, end
            )
            display_word = replacement if replacement else word
            return f"...{context_before}[{display_word}]{context_after}..."

        # Get text before and after the match
        before_text = text[:start]
        after_text = text[end:]
        matched_word = text[start:end]

        # Split into words and take last N before, first N after
        words_before = re.findall(r"\S+", before_text)
        words_after = re.findall(r"\S+", after_text)

        context_before = " ".join(words_before[-num_words:]) if words_before else ""
        context_after = " ".join(words_after[:num_words]) if words_after else ""

        # Use replacement if provided, otherwise use matched word
        display_word = replacement if replacement else matched_word

        return f"...{context_before} [{display_word}] {context_after}..."

    def _find_matches(self, word: str, text: str):
        """Find all matches of a word in text, considering word boundaries."""
        # Create word boundary pattern
        pattern = r"\b" + re.escape(word) + r"\b"

        return list(re.finditer(pattern, text, re.IGNORECASE))

    def get_ai_statistics(self) -> Dict:
        """Get statistics about AI processing."""
        total_decisions = len(self.ai_decisions) + len(self.manual_decisions)

        if total_decisions == 0:
            return {"ai_percentage": 0, "total": 0, "ai_count": 0, "manual_count": 0}

        ai_percentage = (len(self.ai_decisions) / total_decisions) * 100

        return {
            "total": total_decisions,
            "ai_count": len(self.ai_decisions),
            "manual_count": len(self.manual_decisions),
            "ai_percentage": round(ai_percentage, 1),
        }

    def generate_ai_report(self) -> str:
        """Generate a report of AI processing results."""
        stats = self.get_ai_statistics()
        learning_stats = self.learning_storage.get_learning_stats()

        report = []
        report.append("=== AI Choice Processing Report ===")
        report.append(f"Total decisions: {stats['total']}")
        report.append(f"AI automatic: {stats['ai_count']} ({stats['ai_percentage']}%)")
        report.append(f"Manual review: {stats['manual_count']}")
        report.append("")

        report.append("=== Learning Statistics ===")
        report.append(f"Total learned entries: {learning_stats['total_entries']}")
        report.append(f"Words with patterns: {learning_stats['words_learned']}")
        report.append(f"Active patterns: {learning_stats['total_patterns']}")
        if learning_stats["words_list"]:
            report.append(
                f"Learned words: {', '.join(learning_stats['words_list'][:10])}"
            )
        report.append("")

        if self.ai_decisions:
            report.append("AI Decisions:")
            for decision in self.ai_decisions[:10]:  # Show first 10
                report.append(
                    f"  '{decision['word']}' → '{decision['decision']['choice']}' "
                    f"(confidence: {decision['decision']['confidence']:.2f})"
                )

            if len(self.ai_decisions) > 10:
                report.append(f"  ... and {len(self.ai_decisions) - 10} more")

        return "\n".join(report)

    def record_manual_choice(
        self,
        word: str,
        options: List[str],
        context_before: str,
        context_after: str,
        user_choice: str,
        line_number: int = 0,
    ):
        """
        Record a manual user choice for learning.

        This should be called when the user manually selects a choice.
        """
        log_message(f"Recording manual choice: '{word}' → '{user_choice}'")
        self.learning_analyzer.add_user_decision(
            word=word,
            options=options,
            context_before=context_before,
            context_after=context_after,
            user_choice=user_choice,
            line_number=line_number,
        )

    def handle_choice(self, choice: str, ctx: "BookfixContext") -> bool:
        """
        Override parent's handle_choice to capture learning from manual selections.

        Args:
            choice: The selected replacement text
            ctx: BookfixContext to modify

        Returns:
            True if more choices needed, False if word is complete
        """
        # Capture context BEFORE applying the choice
        if self.matches and self.current_match < len(self.matches):
            match = self.matches[self.current_match]
            start, end = match.span()

            # Extract context for learning (50 chars before/after)
            context_start = max(0, start - 50)
            context_end = min(len(self.current_text), end + 50)
            context_before = self.current_text[context_start:start]
            context_after = self.current_text[end:context_end]

            matched_text = self.current_text[start:end]

            # Only record if actual choice was made (not skip)
            if choice.lower() != matched_text.lower():
                # Get options from context
                options = ctx.choices.get(self.current_word, [choice])

                # Record the learning entry
                self.record_manual_choice(
                    word=self.current_word,
                    options=options,
                    context_before=context_before,
                    context_after=context_after,
                    user_choice=choice,
                    line_number=0,  # Could track actual line if needed
                )

                log_message(f"Learned: '{self.current_word}' → '{choice}' in context")

        # Call parent implementation to handle the actual replacement
        return super().handle_choice(choice, ctx)
