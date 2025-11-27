"""
AI-Enhanced Choice Processor for Bookfix.

Extends the InteractiveChoiceProcessor with AI analysis capabilities
for automatic homograph disambiguation.
"""

import re
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import BookfixContext

from .choices import InteractiveChoiceProcessor
from ..ai.service import BookfixAIService
from ..ai.change_tracker import AIChangeTracker
from ..ai.choices_learning import ChoicesLearningStorage, ChoicesLearningAnalyzer
from ..ai.pos_tagger import get_pos_tagger
from ..ai.pos_dictionary import get_pos_dictionary
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
        self.show_reasoning = (
            show_reasoning  # Whether to request AI reasoning (verbose, slower)
        )

        # Change tracking
        self.change_tracker = change_tracker

        # Track AI decisions for review
        self.ai_decisions = []
        self.manual_decisions = []

        # Decision statistics
        self.decision_stats = Counter()

        # Log file for choices processing
        self.choices_log_path = None

        # Learning system
        self.learning_storage = ChoicesLearningStorage()
        self.learning_analyzer = ChoicesLearningAnalyzer(self.learning_storage)

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
                    f"AI service connection failed: {test_result.error_message}",
                    level="WARNING",
                )
                self.ai_enabled = False  # Disable AI if model fails to load
                return False
            else:
                log_message(
                    f"AI service initialized successfully: {test_result.content}"
                )
                self.ai_enabled = True
                return True

        except Exception as e:
            log_message(f"Failed to initialize AI service: {e}", level="ERROR")
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
                with open(self.choices_log_path, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {message}\n")
            except Exception as e:
                log_message(f"Failed to write to choices.log: {e}", level="WARNING")

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

    def _refresh_pos_dictionary(self):
        """Refresh the pos_dictionary reference to get latest instance from global singleton.

        Call this before processing if keyword dictionary has been updated.
        """
        if self.use_pos_tagging:
            self.pos_dictionary = get_pos_dictionary()
            log_message("POS dictionary reference refreshed from global singleton")

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
            self._refresh_pos_dictionary()

        self._setup_choices_log(ctx.current_file_path)
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

            for match in matches:
                detected_pos_tag = ""
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
                        continue  # Skip all other rules and AI for this match
                else:
                    log_message(
                        f"WARNING: context_full split failed for word '{word}'. Split returned {len(context_parts)} parts instead of 2.",
                        level="WARNING",
                    )

                # Run all local rules
                all_rules, detected_pos_tag = self._run_all_rules(
                    word, context_full, ctx
                )

                # Initialize ai_decision and decision_source before conditional assignment
                ai_decision = None
                decision_source = None

                # Check for consensus
                ai_decision, decision_source = self._get_consensus_from_rules(
                    all_rules, context_full
                )

                if ai_decision:
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
                elif self.ai_enabled and self.ai_service:
                    # No rule consensus, queue for AI batch
                    self._log_to_choices_log(f"Queuing '{word}' for AI batch analysis.")
                    item_id_counter += 1
                    log_message(
                        f"DEBUG: Queued item_id_counter: {item_id_counter}",
                        level="DEBUG",
                    )

                    batch_item = {
                        "id": item_id_counter,
                        "word": word,
                        "context": context_full,
                        "options": options,
                    }
                    items_for_ai_batch.append(batch_item)
                    match_map[item_id_counter] = (
                        match,
                        word,
                        options,
                        contextualized_options,
                        detected_pos_tag,
                    )
                else:
                    # No strong rules and no AI. Treat this as a low-confidence
                    # default that explicitly requires human review in the
                    # review window.
                    self.decision_stats["review_needed"] += 1
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

        # Now, process the batch of items that need AI analysis
        if items_for_ai_batch:
            BATCH_SIZE = 10  # Process in chunks to avoid payload size limits
            all_batch_results = {}

            log_message(
                f"Processing {len(items_for_ai_batch)} items in chunks of {BATCH_SIZE}."
            )

            for i in range(0, len(items_for_ai_batch), BATCH_SIZE):
                chunk = items_for_ai_batch[i : i + BATCH_SIZE]
                log_message(
                    f"Sending chunk {i//BATCH_SIZE + 1} ({len(chunk)} items) to AI for batch analysis. Item IDs: {[item['id'] for item in chunk]}",
                    level="DEBUG",
                )

                try:
                    # Note: The AIResponse class is imported from ..ai.service
                    from ..ai.service import AIResponse

                    chunk_results = self.ai_service.analyze_homographs_batch(chunk)
                    log_message(
                        f"DEBUG: Received chunk results. Item IDs: {list(chunk_results.keys())}",
                        level="DEBUG",
                    )
                    all_batch_results.update(chunk_results)
                except Exception as e:
                    log_message(
                        f"Error processing chunk {i//BATCH_SIZE + 1}: {e}",
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
                match, word, options, contextualized_options, detected_pos_tag = (
                    match_map[item_id]
                )
                decision_source = "llm"
                ai_decision = None

                if ai_response.success:
                    ai_decision = {
                        "choice": ai_response.content,
                        "confidence": ai_response.confidence,
                        "reason": ai_response.reasoning,
                    }
                    self.decision_stats[decision_source] += 1
                else:
                    decision_source = "default"
                    ai_decision = {
                        "choice": options[0],
                        "confidence": 0.5,
                        "reason": f"AI batch failed: {ai_response.error_message}",
                    }
                    self.decision_stats[decision_source] += 1

                self._log_change(
                    match,
                    word,
                    options,
                    ai_decision,
                    decision_source,
                    contextualized_options,
                    detected_pos_tag,
                )

        log_message(
            f"AI review mode complete: {len(self.change_tracker.changes)} decisions logged for review"
        )
        self._log_to_choices_log(f"\n=== AI CHOICES BATCH PROCESSING COMPLETED ===")
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

        parts = context_full.split(f"[{word}]")
        if len(parts) != 2:
            log_message(
                f"DEBUG: _run_all_rules: context_full split by '[{word}]' did not yield 2 parts. Parts: {parts}",
                level="DEBUG",
            )
            return {}, ""

        context_before, context_after = parts
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

        # Rule 1: Complex POS rules (e.g., imperative verbs)
        if self.pos_dictionary and pos_token and dep_info and doc:
            log_message(
                f"DEBUG: _run_all_rules: Checking complex POS rules for '{word}'",
                level="DEBUG",
            )
            try:
                complex_pos_result = (
                    self.pos_dictionary.get_pronunciation_by_complex_pos_rules(
                        word, pos_token, dep_info, doc
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
            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Error checking complex POS rules: {e}",
                    level="DEBUG",
                )

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
            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Error checking semantic rule: {e}",
                    level="DEBUG",
                )

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
                    pronunciation, explanation = entity_result
                    all_rules["entity"] = {
                        "choice": pronunciation,
                        "confidence": 0.92,
                        "reason": f"Entity: {explanation}",
                    }
                    log_message(
                        f"DEBUG: _run_all_rules: Entity rule matched: '{pronunciation}'",
                        level="DEBUG",
                    )
            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Error checking entity rule: {e}",
                    level="DEBUG",
                )

            # Rule 5: Context keywords
            log_message(
                f"DEBUG: _run_all_rules: Checking keyword rule for '{word}'",
                level="DEBUG",
            )
            try:
                keyword_result = self.pos_dictionary.get_pronunciation_by_keywords(
                    word, context_full
                )
                if keyword_result:
                    pronunciation, matched_keyword, confidence = keyword_result
                    all_rules["keyword"] = {
                        "choice": pronunciation,
                        "confidence": confidence,
                        "reason": f"Keyword: '{matched_keyword}'",
                    }
                    log_message(
                        f"DEBUG: _run_all_rules: Keyword rule matched: '{pronunciation}'",
                        level="DEBUG",
                    )
            except Exception as e:
                log_message(
                    f"DEBUG: _run_all_rules: Error checking keyword rule: {e}",
                    level="DEBUG",
                )

        log_message(
            f"DEBUG: Exiting _run_all_rules for word: '{word}'. Found rules: {list(all_rules.keys())}",
            level="DEBUG",
        )
        return all_rules, detected_pos_tag

    def _get_consensus_from_rules(
        self, all_rules: Dict, context_full: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Check for consensus among rule results.

        Strategy:
        1. If all rules agree on the same choice → consensus
        2. If rules disagree:
           - AI enabled → return None (send to AI)
           - AI disabled → fall back to strict priority
        3. If no rules matched → return None

        NOTE: We intentionally avoid allowing a lower-priority rule (e.g. plain
        'keyword') to win over higher-priority rules (complex_pos/entity/pos/
        semantic) based solely on a slightly higher numeric confidence.
        Additionally, **keyword-only** matches are treated as **no decision** so
        they are always surfaced as low-confidence items for review (or sent to
        AI), never as standalone rules.
        """
        if not all_rules:
            # No rules at all → no decision; caller will either send to AI or
            # treat as a low-confidence default that requires review.
            return None, None

        # Special case: only the keyword rule fired. Treat this as NO DECISION /
        # "Review Needed" rather than letting keyword act as a standalone rule.
        if set(all_rules.keys()) == {"keyword"}:
            log_message(
                "DEBUG: _get_consensus_from_rules: Only keyword rule fired; "
                "treating as NO DECISION (Review Needed)",
                level="DEBUG",
            )
            return None, None

        # Collect all choices from rules
        choices = [rule_data["choice"] for rule_data in all_rules.values()]

        # Check if all rules agree (unanimous consensus)
        if len(set(choices)) == 1:
            # All rules agree - use highest priority rule as the source
            priority_order = ["complex_pos", "entity", "pos", "semantic", "keyword"]
            for rule_name in priority_order:
                if rule_name in all_rules:
                    return all_rules[rule_name], rule_name

        # Rules disagree - check if we should use AI or strict priority fallback
        if self.ai_enabled and self.ai_service:
            # AI is available - let AI resolve the disagreement
            log_message(
                f"DEBUG: Rules disagree ({list(all_rules.keys())}), deferring to AI",
                level="DEBUG",
            )
            return None, None
        else:
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
        replacement = decision["choice"]
        confidence = decision["confidence"]
        reason = decision.get("reason", "")

        # Calculate context_before and context_after directly from original_text
        # This avoids issues with splitting context_full if the bracketed word is not found or malformed
        full_text = self.change_tracker.original_text
        match_start_in_full_text = match.start()
        match_end_in_full_text = match.end()

        # Extract context_before and context_after based on context_size
        # This is similar to what _extract_context does, but we need the raw text, not bracketed
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
                return tracker.get_current_text()
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
                    ctx.text, match.start(), match.end(), self.context_size
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

        return ctx.text

    def _analyze_with_ai(
        self,
        word: str,
        context: str,
        options: List[str],
        best_guess: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Analyze a word choice using AI.

        Args:
            word: The word to analyze
            context: Context around the word
            options: List of possible replacements
            best_guess: A preliminary guess from local rules to be verified by the AI

        Returns:
            Dictionary with AI decision or None if failed
        """
        try:
            # Call AI service - convert string options to tuples with empty descriptions
            contextualized_options = [(opt, "") for opt in options]
            response = self.ai_service.analyze_contextualized_homograph(
                word,
                context,
                contextualized_options,
                show_reasoning=False,  # Use default reasoning setting
                best_guess=best_guess,
            )

            if response.success:
                return {
                    "choice": response.content,
                    "confidence": response.confidence,
                    "reason": response.reasoning or f"AI chose {response.content}",
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

    def _extract_context(
        self, text: str, start: int, end: int, context_size: int = 100
    ) -> str:
        """
        Extract context around a match.

        Args:
            text: Full text
            start: Start position of match
            end: End position of match
            context_size: Characters to include before/after

        Returns:
            Context string with the target word highlighted
        """
        log_message(
            f"DEBUG: _extract_context - len(text): {len(text)}, start: {start}, end: {end}, context_size: {context_size}",
            level="DEBUG",
        )
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
    ) -> str:
        """
        Extract a short context showing N words before and after the match.

        Args:
            text: Full text
            start: Start position of match
            end: End position of match
            num_words: Number of words to include before/after (default: 10)
            replacement: Optional replacement word to show instead of matched word

        Returns:
            Short context string with the target word highlighted
        """
        import re

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
