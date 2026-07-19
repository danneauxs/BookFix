"""
AI-Enhanced All-Caps Processor for Bookfix.

Extends the AllCapsProcessor with AI analysis capabilities
for intelligent all-caps sequence processing with change tracking.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING, Set

if TYPE_CHECKING:
    from ..context import BookfixContext

from .allcaps import AllCapsProcessor
from ..ai.service import BookfixAIService
from ..ai.change_tracker import AIChangeTracker
from ..ai.caps_learning import CapsLearningStorage
from ..logging import log_message
from ..loggers.processor_logger import ProcessorLogger
from ..widgets.caps_review_editor import CapsReviewEditor

# Batch processing configuration
CAPS_BATCH_SIZE = 20  # Process caps words in batches of 20

# Sound effect detection patterns
SOUND_EFFECT_PATTERNS = [
    r'(.)\1{2,}',  # 3+ identical letters: "aaa", "zzz"
]

# Letters that rarely/never appear doubled in English
RARE_DOUBLES = ['hh', 'jj', 'qq', 'vv', 'ww', 'xx']

# Known compound words that contain rare doubles (not sound effects)
KNOWN_COMPOUNDS = ['withhold', 'fishhook', 'bathhouse', 'powwow']


class AIAllCapsProcessor(AllCapsProcessor):
    """
    AI-enhanced all-caps processor that can intelligently decide
    whether to lowercase all-caps sequences based on context analysis.
    """

    def __init__(self, change_tracker: Optional[AIChangeTracker] = None):
        """Initialize a new instance of the class.
        Args:
        change_tracker (Optional[AIChangeTracker]): An optional change tracker for AI-driven changes.
        Returns: None
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
        self.sequences_processed = 0
        self.sequences_lowercased = 0
        self.sequences_ignored = 0

        # Per-file logger
        self.logger: Optional[ProcessorLogger] = None

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

            self.confidence_threshold = ai_config.get("confidence_threshold", 0.8)
            self.fallback_to_manual = ai_config.get("fallback_to_manual", True)

            # Test AI connection
            test_result = self.ai_service.test_connection()
            if not test_result.success:
                log_message(
                    f"AI service connection failed: {test_result.error_message}",
                    level="WARNING",
                )
                if not self.fallback_to_manual:
                    return False
                log_message("Will fallback to manual processing")
            else:
                log_message(
                    f"AI service initialized successfully: {test_result.content}"
                )

            return True

        except Exception as e:
            log_message(f"Failed to initialize AI service: {e}", level="ERROR")
            self.ai_enabled = False
            return False

    def _is_sound_effect(self, word: str, cap_ignore_list: List[str]) -> bool:
        """
        Detect if a word is likely a sound effect/onomatopoeia.

        Patterns:
        - 3+ identical letters (e.g., "caaawww", "shhhh")
        - Rare letter doubles (e.g., "hh" in non-compound words)

        Args:
            word: The capitalized word to check
            cap_ignore_list: List of words to ignore (from CAP_IGNORE)

        Returns:
            True if likely a sound effect, False otherwise
        """
        # Check if word is in CAP_IGNORE list - if so, NOT a sound effect
        if word.upper() in [item.upper() for item in cap_ignore_list]:
            return False

        word_lower = word.lower()

        # Pattern 1: 3+ identical letters
        for pattern in SOUND_EFFECT_PATTERNS:
            if re.search(pattern, word_lower):
                return True

        # Pattern 2: Rare doubles (but exclude known compound words)
        for rare_double in RARE_DOUBLES:
            if rare_double in word_lower:
                # Check if it's NOT a known compound word
                if word_lower not in KNOWN_COMPOUNDS:
                    return True

        return False

    def _process_no_ai(self, ctx: "BookfixContext", output_file_path: Optional[str] = None) -> "BookfixContext":
        """
        Manual review path when AI is disabled. Detects caps sequences and opens
        CapsReviewEditor with no AI suggestions so the user decides each one.
        """
        cap_ignore_list = list(ctx.cap_ignore) if hasattr(ctx, "cap_ignore") else []
        upper_to_lower_list = list(ctx.upper_to_lower) if hasattr(ctx, "upper_to_lower") else []

        # Apply upper_to_lower auto-lowercasing
        for word in upper_to_lower_list:
            ctx.text = re.sub(rf"\b{re.escape(word)}\b", word.lower(), ctx.text)

        # Auto-lowercase consecutive caps groups (title blocks, etc.)
        ctx.text = self._lowercase_caps_groups(ctx.text, cap_ignore_list)

        # Find remaining isolated caps sequences
        sequence_pattern = re.compile(r"\b[A-Z]{2,}(?:\'[A-Z]+)?\b")
        matches = list(sequence_pattern.finditer(ctx.text))

        # Add single roman numeral letters (V, X, L, C, D, M)
        roman_single_pattern = re.compile(r"\b([VXLCDM])\b")
        single_letter_candidates = list(roman_single_pattern.finditer(ctx.text))
        single_letter_matches = []
        for match in single_letter_candidates:
            start = match.start()
            end = match.end()
            before_char = ctx.text[start - 1] if start > 0 else " "
            after_char = ctx.text[end] if end < len(ctx.text) else " "
            if before_char != "-" and after_char != "-":
                single_letter_matches.append(match)
        matches.extend(single_letter_matches)
        matches.sort(key=lambda m: m.start())

        caps_sequences = []
        for match in matches:
            caps = match.group(0)
            if caps in cap_ignore_list:
                continue
            context_before = ctx.text[max(0, match.start() - 50): match.start()]
            context_after = ctx.text[match.end(): min(len(ctx.text), match.end() + 50)]
            caps_sequences.append({
                "caps": caps,
                "original": caps,
                "suggestion": "keep",
                "position": match.start(),
                "context_before": context_before,
                "context_after": context_after,
                "confidence": 0.0,
                "reasoning": "Manual review — AI disabled",
                "accept": False,
                "is_sound_effect": self._is_sound_effect(caps, cap_ignore_list),
            })

        log_message(f"Manual review: {len(caps_sequences)} caps sequences found")

        if not caps_sequences:
            log_message("No caps sequences to review")
            return ctx

        review_dialog = CapsReviewEditor(ctx.text, caps_sequences, cap_ignore_list)
        if output_file_path:
            review_dialog.output_file_path = output_file_path

        def on_changes_applied(final_text, learning_data):
            """Process all-caps sequences using AI analysis with a review window.
            Args:
            ctx (BookfixContext): The context for the book fixing process.
            output_file_path (Optional[str]): Path to save the processed output file.
            Returns:
            BookfixContext: The updated context after processing.
            """
            ctx.text = final_text

        review_dialog.changes_applied.connect(on_changes_applied)
        review_dialog.exec_()

        return ctx

    def process_all_caps_sequences_ai(self, ctx: "BookfixContext", output_file_path: Optional[str] = None) -> "BookfixContext":
        """
        Process all-caps sequences using AI analysis with review window.

        Rules:
        1. Groups of consecutive caps words → auto lowercase (no review)
        2. Common emphasis words (THE, A, BIG, etc.) → auto lowercase (no review)
        3. Isolated caps words (possible acronyms) → AI analysis + review if uncertain

        Args:
            ctx: BookfixContext with text and all-caps sequences to process
            output_file_path: Optional path where output should be saved

        Returns:
            Updated BookfixContext
        """
        if not self.ai_enabled or not self.ai_service:
            log_message("AI not available, using manual review dialog")
            return self._process_no_ai(ctx, output_file_path)

        log_message("Starting AI all-caps sequence processing")

        # Initialize per-file logger
        self.logger = ProcessorLogger(ctx.current_file_path, "caps")
        self.logger.log_info("Starting all-caps processing")

        # Get CAP_IGNORE and UPPER_TO_LOWER lists (initialize BEFORE use)
        cap_ignore_list = list(ctx.cap_ignore) if hasattr(ctx, "cap_ignore") else []
        upper_to_lower_list = (
            list(ctx.upper_to_lower) if hasattr(ctx, "upper_to_lower") else []
        )

        # Step 0: Learn document-specific acronyms before processing
        log_message("Step 0: Learning document-specific acronyms from context")
        learned_acronyms = self._learn_document_acronyms(ctx.text)
        if learned_acronyms:
            log_message(
                f"Learned {len(learned_acronyms)} document-specific acronyms: {list(learned_acronyms.keys())}"
            )
            if self.logger:
                self.logger.log_info(
                    f"Learned document-specific acronyms: {', '.join(learned_acronyms.keys())}"
                )
            # Add learned acronyms to CAP_IGNORE for this session
            cap_ignore_list.extend(learned_acronyms.keys())

        # Initialize ignore_set if not present (used for saving user decisions)
        if not hasattr(ctx, "ignore_set"):
            ctx.ignore_set = (
                set(ctx.cap_ignore) if hasattr(ctx, "cap_ignore") else set()
            )

        # Initialize lowercase_set if not present
        if not hasattr(ctx, "lowercase_set"):
            ctx.lowercase_set = set()

        # Pre-pass: auto-lowercase words from UPPER_TO_LOWER
        log_message(
            f"Pre-pass: applying UPPER_TO_LOWER auto-lowercasing ({len(upper_to_lower_list)} words)"
        )
        for word in upper_to_lower_list:
            # Find and log all replacements
            pattern = rf"\b{re.escape(word)}\b"
            if re.search(pattern, ctx.text):
                self.logger.log_change(
                    word, word.lower(), None, "UPPER_TO_LOWER auto-lowercase"
                )
            ctx.text = re.sub(pattern, word.lower(), ctx.text)

        # Common emphasis words that should auto-lowercase (not acronyms)
        # Note: Single letters (A, AN) removed - let AI handle these as they could be valid references
        # (e.g., "group A", "vitamin B", "plan C")
        emphasis_words = {
            "THE",
            "AND",
            "OR",
            "BUT",
            "FOR",
            "NOR",
            "SO",
            "YET",
            "BIG",
            "SMALL",
            "ALL",
            "SOME",
            "NONE",
            "EACH",
            "EVERY",
            "ANY",
            "NEVER",
            "ALWAYS",
            "NOW",
            "THEN",
            "HERE",
            "THERE",
            "WHERE",
            "YES",
            "NO",
            "NOT",
            "VERY",
            "TOO",
            "WELL",
            "JUST",
            "THANK",
            "YOU",
            "PLEASE",
            "SORRY",
            "HELLO",
            "GOODBYE",
            "ONE",
            "TWO",
            "THREE",
            "FOUR",
            "FIVE",
            "SIX",
            "SEVEN",
            "EIGHT",
            "NINE",
            "TEN",
            "TWENTY",
            "THIRTY",
            "FORTY",
            "FIFTY",
            "SIXTY",
            "SEVENTY",
            "EIGHTY",
            "NINETY",
            "HUNDRED",
            "THOUSAND",
            "MILLION",
            "BILLION",
        }

        # Step 1: Auto-lowercase groups of consecutive caps words
        log_message("Step 1: Auto-lowercasing groups of consecutive caps words")
        ctx.text = self._lowercase_caps_groups(ctx.text, cap_ignore_list)

        # Step 2: Auto-lowercase common emphasis words
        log_message("Step 2: Auto-lowercasing common emphasis words")
        for emphasis_word in emphasis_words:
            # Only lowercase if it's isolated (surrounded by lowercase)
            pattern = rf"(?<=[a-z\s,.])\b{re.escape(emphasis_word)}\b(?=[a-z\s,.])"
            if re.search(pattern, ctx.text):
                self.logger.log_change(
                    emphasis_word,
                    emphasis_word.lower(),
                    None,
                    "Auto-lowercased emphasis word",
                )
            ctx.text = re.sub(pattern, emphasis_word.lower(), ctx.text)

        # Step 3: Find remaining isolated caps words for review
        log_message("Step 3: Finding isolated caps words for AI review")
        sequence_pattern = re.compile(r"\b[A-Z]{2,}(?:\'[A-Z]+)?\b")
        matches = list(sequence_pattern.finditer(ctx.text))

        # Add single roman numeral letters (V, X, L, C, D, M)
        roman_single_pattern = re.compile(r"\b([VXLCDM])\b")
        single_letter_candidates = list(roman_single_pattern.finditer(ctx.text))
        single_letter_matches = []
        for match in single_letter_candidates:
            start = match.start()
            end = match.end()
            before_char = ctx.text[start - 1] if start > 0 else " "
            after_char = ctx.text[end] if end < len(ctx.text) else " "
            if before_char != "-" and after_char != "-":
                single_letter_matches.append(match)
        matches.extend(single_letter_matches)
        matches.sort(key=lambda m: m.start())

        log_message(f"Found {len(matches)} isolated caps sequences for AI analysis")

        # Collect all caps sequences with their context for batch processing
        # Store all instances of each word, not just first occurrence
        caps_info = (
            {}
        )  # caps word -> [{position, context_before, context_after, match}, ...]
        seen_caps = set()  # Track unique caps words for learning/AI (sent to AI once)

        for match in matches:
            caps = match.group(0)

            # Skip if already in CAP_IGNORE
            if caps in cap_ignore_list:
                log_message(f"Skipping CAP_IGNORE sequence '{caps}'")
                continue

            # Extract context
            context_before = ctx.text[max(0, match.start() - 50) : match.start()]
            context_after = ctx.text[match.end() : min(len(ctx.text), match.end() + 50)]

            # Store all instances (even if we've seen this caps word before)
            # This ensures every instance gets reviewed and processed
            if caps not in caps_info:
                caps_info[caps] = []

            caps_info[caps].append(
                {
                    "position": match.start(),
                    "context_before": context_before,
                    "context_after": context_after,
                    "match": match,
                }
            )

        log_message(
            f"Collected {len(caps_info)} unique caps words for batch AI analysis"
        )

        # Batch process all caps words with learning integration
        caps_sequences = []
        if caps_info:
            import tempfile
            import os

            # Load learning storage first
            learning_storage = CapsLearningStorage()
            learned_decisions = {}  # caps -> decision
            words_needing_ai = []  # caps words without learned decisions

            # Check learning storage for each caps word
            log_message("Checking learning storage for prior decisions...")
            for caps, instances in caps_info.items():
                # Use first instance for learning lookup (all instances have same word, just different positions)
                first_instance = instances[0]
                learned_decision = learning_storage.get_learned_decision(
                    caps,
                    first_instance["context_before"],
                    first_instance["context_after"],
                )

                if learned_decision:
                    learned_decisions[caps] = learned_decision
                    log_message(
                        f"Using learned decision for '{caps}': {learned_decision}"
                    )
                else:
                    words_needing_ai.append(caps)

            # Separate sound effects from regular caps
            sound_effects = []  # caps words that are sound effects
            regular_caps = []   # caps words for AI processing

            for caps in words_needing_ai:
                if self._is_sound_effect(caps, cap_ignore_list):
                    sound_effects.append(caps)
                    log_message(f"Detected sound effect: '{caps}'")
                else:
                    regular_caps.append(caps)

            # Update words_needing_ai to only include regular caps for AI
            words_needing_ai = regular_caps

            # Log learning summary
            if learned_decisions:
                log_message(
                    f"Found {len(learned_decisions)} learned decisions: {list(learned_decisions.keys())}"
                )
            if words_needing_ai:
                log_message(
                    f"Need AI analysis for {len(words_needing_ai)} words: {words_needing_ai}"
                )
            if sound_effects:
                log_message(
                    f"Detected {len(sound_effects)} sound effects (will show in review): {sound_effects}"
                )

            # Batch process only the words that need AI analysis
            batch_results = {}  # caps -> decision
            if words_needing_ai:
                # Process in batches of CAPS_BATCH_SIZE
                total_batches = (len(words_needing_ai) + CAPS_BATCH_SIZE - 1) // CAPS_BATCH_SIZE

                for batch_idx in range(total_batches):
                    start_idx = batch_idx * CAPS_BATCH_SIZE
                    end_idx = min(start_idx + CAPS_BATCH_SIZE, len(words_needing_ai))
                    batch_words = words_needing_ai[start_idx:end_idx]
                    batch_num = batch_idx + 1

                    log_message(
                        f"Processing batch {batch_num}/{total_batches} ({len(batch_words)} words)..."
                    )

                    temp_file = tempfile.NamedTemporaryFile(
                        mode="w", suffix=".txt", delete=False, encoding="utf-8"
                    )
                    try:
                        # Write structured format: word + context for each caps word in this batch
                        # This matches what the batch analyzer expects, not the entire book
                        for caps in batch_words:
                            info = caps_info[caps][0]  # Use the first instance for context
                            context_before = info["context_before"]
                            context_after = info["context_after"]

                            # Format: WORD followed by context (same format as review window shows)
                            temp_file.write(f"{caps}\n")
                            temp_file.write(
                                f"Context: ...{context_before} {caps} {context_after}...\n\n"
                            )

                        temp_file.close()

                        # Call batch analysis - returns dict of {word: decision}
                        batch_chunk_results = self.ai_service.caps.analyze_batch(
                            temp_file.name, cap_ignore_list
                        )
                        if batch_chunk_results is None:
                            batch_chunk_results = {}

                        if batch_chunk_results:
                            log_message(
                                f"Batch {batch_num}/{total_batches}: Received results for {len(batch_chunk_results)} words"
                            )
                            batch_results.update(batch_chunk_results)
                        else:
                            log_message(
                                f"Batch {batch_num}/{total_batches}: AI analysis failed, falling back to sequential processing",
                                level="WARNING",
                            )
                            # Fallback: process batch words individually (use first instance for context)
                            for caps in batch_words:
                                first_instance = caps_info[caps][
                                    0
                                ]  # Use first instance for fallback
                                ai_response = self.ai_service.analyze_caps_sequence(
                                    caps,
                                    first_instance["context_before"]
                                    + caps
                                    + first_instance["context_after"],
                                    cap_ignore_list,
                                )
                                batch_results[caps] = (
                                    ai_response.content if ai_response.success else "keep"
                                )
                    finally:
                        # Clean up temp file
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass

            # Merge learned decisions with AI results and build caps_sequences list
            # Create one entry per instance (not just one per unique word)
            # Also separate regular caps from sound effects for proper ordering
            regular_sequences = []
            sound_effect_sequences = []

            for caps, instances in caps_info.items():
                # Check if this is a sound effect
                is_sound_effect = caps in sound_effects

                # Use learned decision if available, otherwise use AI result
                if caps in learned_decisions:
                    suggestion = learned_decisions[caps]
                    confidence = 0.95  # High confidence for learned decisions
                    reasoning = f"Learned from prior decision"
                else:
                    suggestion = batch_results.get(caps, "keep")
                    confidence = (
                        0.8 if suggestion != "keep" else 0.5
                    )  # Conservative confidence for batch
                    reasoning = f"Batch AI analysis: {suggestion}"

                # Log AI decision to caps.log (once per unique word)
                if self.logger and not is_sound_effect:  # Don't log sound effects to AI log
                    source = "learned" if caps in learned_decisions else "AI"
                    decision_text = f"{source.title()} decision: {suggestion} (confidence: {confidence:.1%})"
                    self.logger.log_info(f"Analyzing '{caps}': {decision_text}")

                # Add entry for EACH instance of this caps word
                for instance in instances:
                    sequence_entry = {
                        "caps": caps,
                        "original": caps,
                        "suggestion": suggestion,
                        "position": instance["position"],
                        "context_before": instance["context_before"],
                        "context_after": instance["context_after"],
                        "confidence": confidence,
                        "reasoning": reasoning,
                        "accept": True,  # Default to accepting AI suggestions
                        "is_sound_effect": is_sound_effect,  # NEW FLAG
                    }

                    # Separate into two lists for proper ordering
                    if is_sound_effect:
                        sound_effect_sequences.append(sequence_entry)
                    else:
                        regular_sequences.append(sequence_entry)

            # Combine with sound effects at the end
            caps_sequences = regular_sequences + sound_effect_sequences
            log_message(
                f"Review list: {len(regular_sequences)} regular caps, {len(sound_effect_sequences)} sound effects (at end)"
            )

        log_message(
            f"Collected {len(caps_sequences)} caps sequences with AI suggestions for review"
        )

        # Show review window for all AI decisions
        if caps_sequences:
            log_message("Opening caps review window with all AI decisions...")

            review_dialog = CapsReviewEditor(ctx.text, caps_sequences, cap_ignore_list)
            # Set output file path if provided
            if output_file_path:
                review_dialog.output_file_path = output_file_path

            # Connect signal to handle results
            def on_changes_applied(final_text, learning_data):
                """Updates the text context and logs user decisions for ignored caps and lowercased words.
                Args:
                final_text (str): The updated text after changes.
                learning_data (dict): Data containing information about items to be ignored or lowercased.
                Returns: None
                """
                ctx.text = final_text

                # Log user decisions to caps.log
                if self.logger:
                    self.logger.log_info(f"\n=== User Review Decisions ===")

                    # Log items kept (added to CAP_IGNORE)
                    if learning_data["to_add_cap_ignore"]:
                        for caps in learning_data["to_add_cap_ignore"]:
                            self.logger.log_info(
                                f"User KEPT: '{caps}' (added to CAP_IGNORE)"
                            )

                    # Log items lowercased (added to UPPER_TO_LOWER)
                    if learning_data["to_add_upper_to_lower"]:
                        for caps in learning_data["to_add_upper_to_lower"]:
                            self.logger.log_info(
                                f"User LOWERCASED: '{caps}' (added to UPPER_TO_LOWER)"
                            )

                    # Log changes made to specific instances
                    if learning_data.get("changes_made"):
                        for change in learning_data["changes_made"]:
                            self.logger.log_change(
                                change["original"],
                                change["new"],
                                change.get("context", ""),
                                f"User decision: {change.get('action', 'modified')}",
                            )

                # Update CAP_IGNORE list
                if learning_data["to_add_cap_ignore"]:
                    log_message(
                        f"Adding to CAP_IGNORE: {learning_data['to_add_cap_ignore']}"
                    )
                    ctx.cap_ignore.extend(learning_data["to_add_cap_ignore"])

                # Update UPPER_TO_LOWER list
                if learning_data["to_add_upper_to_lower"]:
                    log_message(
                        f"Adding to UPPER_TO_LOWER: {learning_data['to_add_upper_to_lower']}"
                    )
                    ctx.upper_to_lower.extend(learning_data["to_add_upper_to_lower"])

                # Save updates to .data2.txt
                self._save_caps_data_file(ctx, learning_data)

            review_dialog.changes_applied.connect(on_changes_applied)

            # Show modal dialog
            if review_dialog.exec_() == CapsReviewEditor.Accepted:
                log_message("Caps review completed successfully")
            else:
                log_message("Caps review cancelled by user")

        else:
            log_message("No caps sequences to review")

        # Log final summary to caps.log
        if self.logger:
            self.logger.log_info("\n=== All-Caps Processing Summary ===")
            self.logger.log_info(f"Total sequences analyzed: {len(caps_sequences)}")
            self.logger.log_info(f"Auto-lowercased groups: {self.sequences_lowercased}")
            self.logger.log_info(f"Kept as caps: {self.sequences_ignored}")
            self.logger.log_info("Processing complete\n")

        return ctx

    def _lowercase_caps_groups(self, text: str, cap_ignore_list: List[str]) -> str:
        """
        Find and lowercase groups of consecutive caps words.

        A group is 2+ consecutive caps words (e.g., "CHAPTER ONE", "BY THE GODS").
        Also handles chapter/section titles (e.g., "36. LOST", "Chapter 5: THE BEGINNING").
        Preserves words in CAP_IGNORE list.

        Args:
            text: Input text
            cap_ignore_list: List of caps words to preserve

        Returns:
            Text with caps groups lowercased
        """
        # Pattern: Find sequences of 2+ caps words with spaces between them
        # But not if they're in CAP_IGNORE (including contractions like MUSTN'T)
        caps_word_pattern = r"\b[A-Z]{2,}(?:\'[A-Z]+)?\b"

        # Pattern: Chapter/section title (number/roman + optional punct + caps)
        # Examples: "36. LOST", "Chapter 5: THE BEGINNING", "V. INTRODUCTION"
        chapter_pattern = r"^\s*(?:\d+|[IVXLCDM]+)[\.\:\-\s]+([A-Z\s]+)\s*$"

        lines = text.split("\n")
        modified_lines = []

        for line in lines:
            # First check if this is a chapter/section title
            chapter_match = re.match(chapter_pattern, line)
            if chapter_match:
                caps_part = chapter_match.group(1).strip()
                # Check if caps part contains only caps words (not in CAP_IGNORE)
                caps_words = re.findall(caps_word_pattern, caps_part)
                if caps_words and not any(w in cap_ignore_list for w in caps_words):
                    # Lowercase the entire caps portion
                    lowercased_caps = caps_part.lower()
                    new_line = line.replace(caps_part, lowercased_caps)
                    modified_lines.append(new_line)
                    log_message(
                        f"Auto-lowercased chapter/section title: '{line.strip()}' → '{new_line.strip()}'"
                    )
                    if self.logger:
                        self.logger.log_change(
                            line.strip(),
                            new_line.strip(),
                            None,
                            "Auto-lowercased chapter/section title",
                        )
                    continue
            # Find all caps words in this line (excluding CAP_IGNORE words)
            # This allows CAP_IGNORE words to act as transparent connectors
            caps_matches = [
                match
                for match in re.finditer(caps_word_pattern, line)
                if match.group(0) not in cap_ignore_list
            ]

            if len(caps_matches) < 2:
                # No groups possible
                modified_lines.append(line)
                continue

            # Find groups of consecutive caps words
            # Single-letter connective words (I, A, etc.) don't break groups
            connective_words = {
                "i",
                "a",
                "an",
                "or",
                "of",
                "to",
                "by",
                "in",
                "on",
                "at",
            }
            groups = []
            current_group = [caps_matches[0]]

            for i in range(1, len(caps_matches)):
                prev_match = caps_matches[i - 1]
                curr_match = caps_matches[i]

                # Check if they're consecutive (only whitespace/connectives between)
                between_text = line[prev_match.end() : curr_match.start()]
                between_words = between_text.strip().split()

                # Check if gap contains only connective words
                is_connective_gap = all(
                    w.lower() in connective_words for w in between_words
                )

                if (
                    between_text.strip() == "" or is_connective_gap
                ):  # Only spaces/tabs OR connective words
                    current_group.append(curr_match)
                else:
                    # Gap found, save current group if it has 2+ words
                    if len(current_group) >= 2:
                        groups.append(current_group)
                    current_group = [curr_match]

            # Don't forget the last group
            if len(current_group) >= 2:
                groups.append(current_group)

            # Lowercase groups (in reverse order to maintain positions)
            for group in reversed(groups):
                # Lowercase the entire group
                group_start = group[0].start()
                group_end = group[-1].end()
                group_text = line[group_start:group_end]
                lowercased = group_text.lower()

                line = line[:group_start] + lowercased + line[group_end:]
                log_message(
                    f"Auto-lowercased caps group: '{group_text}' → '{lowercased}'"
                )

                # Log to per-file logger
                if self.logger:
                    self.logger.log_change(
                        group_text, lowercased, None, "Auto-lowercased caps group"
                    )

            modified_lines.append(line)

        return "\n".join(modified_lines)

    def _save_caps_data_file(self, ctx: "BookfixContext", learning_data: Dict):
        """
        Persist ADD, LOWER ADD, and HYPHEN ADD decisions to their respective data files.

        ADD → cap_ignore.txt (keep as all-caps forever)
        LOWER ADD → upper_to_lower.txt (always lowercase)
        HYPHEN ADD → mode-selected replacement file as regex word-boundary rule.
        """
        data_dir = Path(__file__).parent.parent.parent / 'data'

        cap_ignore_additions = learning_data.get('to_add_cap_ignore', [])
        upper_to_lower_additions = learning_data.get('to_add_upper_to_lower', [])
        hyphenate_additions = learning_data.get('to_hyphenate_add', [])

        if cap_ignore_additions:
            cap_ignore_path = data_dir / 'cap_ignore.txt'
            # Read existing to avoid duplicates
            existing = set()
            if cap_ignore_path.exists():
                with open(cap_ignore_path, 'r', encoding='utf-8') as f:
                    existing = {line.strip() for line in f if line.strip()}
            with open(cap_ignore_path, 'a', encoding='utf-8') as f:
                for word in cap_ignore_additions:
                    if word not in existing:
                        f.write(f"{word}\n")
                        log_message(f"Saved '{word}' to cap_ignore.txt")

        if upper_to_lower_additions:
            upper_to_lower_path = data_dir / 'upper_to_lower.txt'
            existing = set()
            if upper_to_lower_path.exists():
                with open(upper_to_lower_path, 'r', encoding='utf-8') as f:
                    existing = {line.strip() for line in f if line.strip()}
            with open(upper_to_lower_path, 'a', encoding='utf-8') as f:
                for word in upper_to_lower_additions:
                    if word not in existing:
                        f.write(f"{word}\n")
                        log_message(f"Saved '{word}' to upper_to_lower.txt")

        if hyphenate_additions:
            replace_name = (
                'replace.dev.txt'
                if getattr(ctx, "dev_mode", False)
                else 'replace.txt'
            )
            replace_path = data_dir / replace_name
            existing_lines = set()
            if replace_path.exists():
                with open(replace_path, 'r', encoding='utf-8') as f:
                    existing_lines = {line.strip() for line in f}
            with open(replace_path, 'a', encoding='utf-8') as f:
                for word in hyphenate_additions:
                    hyphenated = '-'.join(list(word))
                    entry = f"regex:\\b{word}\\b -> {hyphenated}"
                    if entry not in existing_lines:
                        f.write(f"\n{entry}")
                        log_message(f"Saved hyphenation rule to {replace_name}: {entry}")

    def _learn_document_acronyms(self, text: str) -> Dict[str, str]:
        """
        Scan text for acronym definitions and learn document-specific acronyms.

        Patterns detected:
        - "World Spy Organization (WSO)"
        - "WSO, or World Spy Organization,"
        - "the WSO (World Spy Organization)"
        - "WSO, the intelligence arm"

        Args:
            text: Full document text

        Returns:
            Dictionary mapping acronym → full definition
        """
        learned = {}

        # Pattern 1: "Full Name (ACRONYM)" or "Full Name (acronym)"
        # Matches: 2-5 capitalized words followed by parenthetical acronym
        pattern1 = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\s*\(([A-Z]{2,6})\)"
        for match in re.finditer(pattern1, text):
            full_name = match.group(1)
            acronym = match.group(2)

            # Verify: acronym should be first letters of words
            words = full_name.split()
            expected_acronym = "".join(w[0].upper() for w in words)

            if acronym == expected_acronym or acronym in full_name.upper():
                learned[acronym] = full_name
                log_message(f"Learned acronym: {acronym} = {full_name}")

        # Pattern 2: "ACRONYM, or Full Name" or "ACRONYM (Full Name)"
        pattern2 = (
            r"\b([A-Z]{2,6})[,\s]+(?:or|the)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})"
        )
        for match in re.finditer(pattern2, text):
            acronym = match.group(1)
            full_name = match.group(2)

            # Only if acronym matches first letters
            words = full_name.split()
            expected_acronym = "".join(w[0].upper() for w in words)

            if acronym == expected_acronym:
                learned[acronym] = full_name
                log_message(f"Learned acronym: {acronym} = {full_name}")

        # Pattern 3: "ACRONYM, the [description]" - weaker signal but useful
        # Example: "WSO, the intelligence arm of..."
        pattern3 = r"\b([A-Z]{2,6}),\s+the\s+([a-z]+(?:\s+[a-z]+){1,3})"
        for match in re.finditer(pattern3, text):
            acronym = match.group(1)
            description = match.group(2)

            # Only if we haven't learned this yet
            if acronym not in learned:
                learned[acronym] = f"the {description}"
                log_message(f"Learned acronym (weak): {acronym} = the {description}")

        return learned
