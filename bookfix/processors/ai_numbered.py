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
from ..ai.numbers_analyzer import NumbersLearningAnalyzer
from ..ai.pos_tagger import get_pos_tagger
from ..logging import log_message


class AINumberedLineProcessor(NumberedLineProcessor):
    """
    AI-enhanced numbered line processor that can intelligently format
    lines containing numbers based on context analysis.
    """

    def __init__(self, change_tracker: Optional[AIChangeTracker] = None):
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
        self.learning_analyzer = NumbersLearningAnalyzer(self.learning_storage)

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

    def _setup_numbered_log(self, file_path: str):
        """Set up the numbered analysis log file in the same directory as the input file."""
        if not file_path:
            return

        # Get directory of input file
        input_dir = os.path.dirname(file_path)

        # Create log file paths
        self.numbered_log_path = os.path.join(input_dir, "numbered_analysis.log")
        detection_log_path = os.path.join(input_dir, "numbered_detection.log")

        # Clear any existing logs
        try:
            with open(self.numbered_log_path, "w", encoding="utf-8") as f:
                f.write(f"=== NUMBERED ANALYSIS LOG ===\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Input file: {file_path}\n")
                f.write(f"{'=' * 80}\n\n")
            log_message(f"Created numbered analysis log: {self.numbered_log_path}")

            # Also create detection log
            with open(detection_log_path, "w", encoding="utf-8") as f:
                f.write(f"=== NUMBERED DETECTION LOG ===\n")
                f.write(f"(Shows ALL numbers detected, before analysis/formatting)\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Input file: {file_path}\n")
                f.write(f"{'=' * 80}\n\n")
            log_message(f"Created numbered detection log: {detection_log_path}")
            self.detection_log_path = detection_log_path
        except Exception as e:
            log_message(f"Failed to create numbered logs: {e}", level="ERROR")
            self.numbered_log_path = None
            self.detection_log_path = None

    def _log_to_numbered_log(self, message: str):
        """Append a message to the numbered analysis log."""
        if not self.numbered_log_path:
            return

        try:
            with open(self.numbered_log_path, "a", encoding="utf-8") as f:
                f.write(message)
                if not message.endswith("\n"):
                    f.write("\n")
        except Exception as e:
            log_message(f"Failed to write to numbered log: {e}", level="ERROR")

    def _log_detection(
        self, line_no: int, line_content: str, spans: List[Tuple[int, int]]
    ):
        """Log detected numbers before any analysis."""
        if not hasattr(self, "detection_log_path") or not self.detection_log_path:
            return

        try:
            with open(self.detection_log_path, "a", encoding="utf-8") as f:
                f.write(f"Line {line_no + 1}:\n")
                f.write(f"  Text: {line_content}\n")
                f.write(f"  Numbers found: {len(spans)}\n")
                for idx, (start, end) in enumerate(spans, 1):
                    number = line_content[start:end]
                    context_before = line_content[max(0, start - 30) : start]
                    context_after = line_content[end : end + 30]
                    f.write(
                        f"    #{idx}: '{number}' | ...{context_before}[{number}]{context_after}...\n"
                    )
                f.write("\n")
        except Exception as e:
            log_message(f"Failed to write to detection log: {e}", level="ERROR")

    def _log_number_analysis(
        self,
        analysis_num: int,
        line_content: str,
        spans: List[Tuple[int, int]],
        ai_result: Dict,
        text_context: Dict,
    ):
        """Log concise analysis of a numbered line."""
        if not self.numbered_log_path:
            return

        # Extract numbers and their context
        numbers_info = []
        for start, end in spans:
            number_text = line_content[start:end]
            context_before = line_content[max(0, start - 30) : start]
            context_after = line_content[end : min(len(line_content), end + 30)]
            numbers_info.append(
                {
                    "number": number_text,
                    "before": context_before,
                    "after": context_after,
                }
            )

        # Build log entry - simplified format
        log_entry = []
        log_entry.append(f"\n{'=' * 80}\n")
        log_entry.append(f"ANALYSIS #{analysis_num}\n")
        log_entry.append(f"{'=' * 80}\n\n")

        # Numbers found with context
        log_entry.append(f"Numbers Found: {len(numbers_info)}\n")
        for i, num_info in enumerate(numbers_info, 1):
            log_entry.append(f"  #{i}: '{num_info['number']}'\n")
            log_entry.append(
                f"      Context: ...{num_info['before']}[{num_info['number']}]{num_info['after']}...\n"
            )
        log_entry.append("\n")

        # Formatted result (if changed) - show same context length as Numbers Found
        should_change = ai_result.get("should_change", False)
        if should_change:
            new_line = ai_result.get("new_line", line_content)
            # Extract same context window as the first number for comparison
            if numbers_info:
                first_num = numbers_info[0]
                # Find where the number was in the original line
                num_pos = line_content.find(first_num["number"])
                if num_pos >= 0:
                    # Get same 30-char window before/after in the new line
                    # Estimate position in new line (may have shifted slightly)
                    context_start = max(0, num_pos - 30)
                    context_end = min(
                        len(new_line), num_pos + len(first_num["number"]) + 30
                    )
                    formatted_context = new_line[context_start:context_end]
                    log_entry.append(f"Formatted Result:\n")
                    log_entry.append(f"      Context: ...{formatted_context}...\n\n")
                else:
                    # Fallback if we can't find position
                    log_entry.append(f"Formatted Result:\n")
                    log_entry.append(f"      Context: {new_line[:100]}...\n\n")
            else:
                log_entry.append(f"Formatted Result:\n")
                log_entry.append(f"      Context: {new_line}\n\n")

        # AI Decision
        log_entry.append(f"AI Decision: {'CHANGE' if should_change else 'NO CHANGE'}\n")
        log_entry.append(f"    confidence {ai_result.get('confidence', 0.0):.2f}\n\n")

        # Context indicators (simplified)
        log_entry.append(f"Context Indicators:\n")
        log_entry.append(
            f"  Primary Context: {text_context.get('primary_context', 'general')}\n"
        )
        if text_context.get("is_military"):
            log_entry.append(f"  - Military context detected\n")
        if text_context.get("has_time_focus"):
            log_entry.append(f"  - Time-focused text\n")
        if text_context.get("has_date_focus"):
            log_entry.append(f"  - Date-focused text\n")
        if text_context.get("is_technical"):
            log_entry.append(f"  - Technical context\n")
        log_entry.append("\n")

        # Number types
        number_types = ai_result.get("number_types", [])
        if number_types:
            log_entry.append(
                f"Number Types Detected: {', '.join(set(number_types))}\n\n"
            )

        # Specific changes
        if should_change and "changes" in ai_result and ai_result["changes"]:
            log_entry.append(f"Specific Changes:\n")
            for change in ai_result["changes"]:
                change_type = change.get("type", "unknown")
                log_entry.append(
                    f"  '{change['original']}' → '{change['replacement']}' (type: {change_type})\n"
                )
                if "reasoning" in change:
                    log_entry.append(f"    Reason: {change['reasoning']}\n")

        # Write the entry
        self._log_to_numbered_log("".join(log_entry))

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

    def process_numbers_ai(self, ctx: "BookfixContext") -> "BookfixContext":
        """
        Process numbered lines using AI analysis with context understanding.

        Args:
            ctx: BookfixContext with text and numbered lines to process

        Returns:
            Updated BookfixContext
        """
        if not self.ai_enabled or not self.ai_service:
            log_message("AI not available for numbered processing")
            return ctx

        log_message("Starting AI numbered line processing")

        # Set up numbered analysis log
        if hasattr(ctx, "current_file_path") and ctx.current_file_path:
            self._setup_numbered_log(ctx.current_file_path)
            self._log_to_numbered_log(f"Starting AI numbered analysis\n")
            self._log_to_numbered_log(f"AI Provider: {self.ai_service.provider}\n")
            self._log_to_numbered_log(f"AI Model: {self.ai_service.model}\n")
            self._log_to_numbered_log(
                f"Confidence Threshold: {self.confidence_threshold}\n\n"
            )

        original_text = ctx.text

        # Step 1: Analyze text context to determine domain (military, civilian, technical, etc.)
        text_context = self._analyze_text_context(ctx.text)
        log_message(f"Text context analysis: {text_context}")

        if self.numbered_log_path:
            self._log_to_numbered_log(f"Text Context Analysis:\n")
            self._log_to_numbered_log(
                f"  Primary Context: {text_context['primary_context']}\n"
            )
            self._log_to_numbered_log(
                f"  Is Military: {text_context.get('is_military', False)}\n"
            )
            self._log_to_numbered_log(
                f"  Has Time Focus: {text_context.get('has_time_focus', False)}\n"
            )
            self._log_to_numbered_log(
                f"  Has Date Focus: {text_context.get('has_date_focus', False)}\n"
            )
            self._log_to_numbered_log(
                f"  Is Technical: {text_context.get('is_technical', False)}\n\n"
            )

        # Step 2: Find numbered lines (more inclusive for AI analysis)
        numbered_lines = self._find_all_numbers_for_ai(ctx.text)
        if not numbered_lines:
            log_message("No numbered lines found")
            return ctx

        log_message(f"Found {len(numbered_lines)} numbered lines to process")

        # Debug: Show what lines were found
        for i, (line_no, line_content, spans) in enumerate(
            numbered_lines[:5]
        ):  # Show first 5
            numbers = [line_content[start:end] for start, end in spans]
            log_message(
                f"Line {line_no + 1}: {line_content[:100]}... (numbers: {numbers})"
            )
        log_message(
            f"Detected number spans total: {sum(len(sp) for _,_,sp in numbered_lines)}"
        )

        # Step 3: PRE-CLASSIFY numbers with batching
        # First pass: collect all numbers that need AI classification
        # Always initialize batch_classifications, even if empty (for rules-only mode)
        batch_classifications = {}

        # Only do batching if AI is available and not in rules-only mode
        if self.ai_service and not self.rules_only_mode:
            numbers_for_batch = []
            batch_id = 0
            batch_key_map = {}  # Maps batch_id to (number, batch_key)

            log_message("First pass: Collecting numbers that need AI classification...")

            for line_no, line_content, spans in numbered_lines:
                for start, end in spans:
                    number = line_content[start:end]
                    context_before = line_content[max(0, start - 50) : start]
                    context_after = line_content[end : end + 50]

                    # Try rules first (without AI fallback)
                    number_digits = number.replace(",", "")
                    ctx_lower = (context_before + " " + context_after).lower()

                    # Check learned patterns first
                    learned_classification = self.learning_storage.get_learned_classification(
                        number_digits, context_before, context_after
                    )
                    if learned_classification:
                        # Use learned classification, skip AI
                        batch_key = f"{number}|{context_before + ' ' + context_after}"
                        batch_classifications[batch_key] = (learned_classification, "learned")
                        continue

                    # Try rules (simplified check - just see if rules would match)
                    # We'll do full rule check later, this is just to filter out obvious rule matches
                    has_ordinal = bool(re.search(r"\d+(st|nd|rd|th)$", number))
                    has_currency_symbol = bool(re.match(r"[\$£€¢¥₹]", number))

                    if has_ordinal or has_currency_symbol:
                        # Rules will handle this, don't need AI
                        continue

                    # This number needs AI classification - add to batch
                    batch_id += 1
                    batch_key = f"{number}|{context_before + ' ' + context_after}"
                    full_context = f"{context_before} **{number}** {context_after}"

                    numbers_for_batch.append({
                        "id": batch_id,
                        "number": number,
                        "context": full_context
                    })
                    batch_key_map[batch_id] = (number, batch_key)

            # Send batches to AI
            if numbers_for_batch:
                log_message(f"Sending {len(numbers_for_batch)} numbers to AI in batches...")
                BATCH_SIZE = 20
                all_batch_results = {}

                for i in range(0, len(numbers_for_batch), BATCH_SIZE):
                    chunk = numbers_for_batch[i : i + BATCH_SIZE]
                    log_message(
                        f"Batch {i//BATCH_SIZE + 1}: Processing {len(chunk)} numbers (IDs: {chunk[0]['id']}-{chunk[-1]['id']})"
                    )

                    try:
                        chunk_results = self.ai_service.classify_numbers_batch(chunk)
                        all_batch_results.update(chunk_results)
                    except Exception as e:
                        import traceback
                        log_message(f"Error in batch {i//BATCH_SIZE + 1}: {type(e).__name__}: {e}", level="ERROR")
                        log_message(f"Traceback:\n{traceback.format_exc()}", level="DEBUG")
                        # Create failure responses for this chunk
                        for item in chunk:
                            all_batch_results[item["id"]] = type('obj', (object,), {
                                'success': False,
                                'content': 'general_number',
                                'reasoning': f"Batch failed: {e}"
                            })()

                # Store results for later use
                for batch_id, ai_response in all_batch_results.items():
                    number, batch_key = batch_key_map[batch_id]
                    if ai_response.success:
                        batch_classifications[batch_key] = (ai_response.content, "llm")
                        log_message(
                            f"AI classified '{number}' as '{ai_response.content}'"
                        )
                    else:
                        batch_classifications[batch_key] = ("general_number", "default")

                log_message(f"Batch classification complete: {len(batch_classifications)} numbers classified")

        # Step 4: Process each numbered line using batch classifications
        lines = ctx.text.splitlines()
        changes_made = 0
        line_changes = {}  # Store changes per line for later tracking
        analysis_count = 0

        for line_no, line_content, spans in numbered_lines:
            try:
                # Get AI analysis for this line (with pre-computed batch classifications)
                ai_result = self._analyze_numbered_line_ai(
                    line_content, spans, text_context, batch_classifications
                )
                log_message(
                    f"AI analysis for line {line_no + 1}: should_change={ai_result.get('should_change', False)}, confidence={ai_result.get('confidence', 0)}"
                )

                # Log this analysis
                analysis_count += 1
                if self.numbered_log_path:
                    self._log_number_analysis(
                        analysis_count, line_content, spans, ai_result, text_context
                    )

                if ai_result.get("should_change", False):
                    new_line = ai_result["new_line"]
                    if new_line != line_content:
                        lines[line_no] = new_line
                        changes_made += 1
                        log_message(
                            f"AI changed line {line_no + 1}: '{line_content}' → '{new_line}'"
                        )

                        # Store line change info for later tracking
                        line_changes[line_no] = {
                            "original_line": line_content,
                            "new_line": new_line,
                            "original_spans": spans,
                            "ai_result": ai_result,
                            "changed": True,
                        }
                    else:
                        log_message(f"AI suggested same content for line {line_no + 1}")
                        line_changes[line_no] = {
                            "original_line": line_content,
                            "new_line": new_line,
                            "original_spans": spans,
                            "ai_result": ai_result,
                            "changed": False,
                        }
                else:
                    # No AI change suggested - still track for review screen
                    log_message(f"AI suggested no change for line {line_no + 1}")
                    no_change_result = {
                        "should_change": False,
                        "confidence": 1.0,
                        "reasoning": "No change needed",
                    }
                    line_changes[line_no] = {
                        "original_line": line_content,
                        "new_line": line_content,
                        "original_spans": spans,
                        "ai_result": no_change_result,
                        "changed": False,
                    }

            except Exception as e:
                log_message(f"Failed to process line {line_no + 1}: {e}", level="ERROR")
                if self.numbered_log_path:
                    self._log_to_numbered_log(f"\n{'=' * 80}\n")
                    self._log_to_numbered_log(f"ANALYSIS #{analysis_count} - ERROR\n")
                    self._log_to_numbered_log(f"{'=' * 80}\n")
                    self._log_to_numbered_log(f"Original text: {line_content}\n")
                    self._log_to_numbered_log(f"Error: {e}\n\n")

        # Update context text
        ctx.text = "\n".join(lines)

        # Now track all changes using actual changes made
        if self.change_tracker:
            self._track_actual_changes(ctx.text, line_changes)

        # Write summary to log
        if self.numbered_log_path:
            self._log_to_numbered_log(f"\n{'=' * 80}\n")
            self._log_to_numbered_log(f"PROCESSING SUMMARY\n")
            self._log_to_numbered_log(f"{'=' * 80}\n\n")
            self._log_to_numbered_log(f"Total analyses: {analysis_count}\n")
            self._log_to_numbered_log(f"Lines changed: {changes_made}\n")
            self._log_to_numbered_log(
                f"Lines unchanged: {analysis_count - changes_made}\n"
            )
            self._log_to_numbered_log(
                f"\nProcessing completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            log_message(f"Numbered analysis log saved to: {self.numbered_log_path}")

        log_message(f"AI numbered processing complete: {changes_made} changes made")
        return ctx

    def process_numbers_ai_review_mode(
        self, ctx: "BookfixContext"
    ) -> Optional[AIChangeTracker]:
        """
        Process numbered lines using AI analysis but track changes for review instead of auto-applying.
        Can also run in rules-only mode if ai_enabled is False.

        Args:
            ctx: BookfixContext with text and numbered lines to process

        Returns:
            AIChangeTracker with all changes ready for review, or None if no changes
        """
        # Allow rules-only mode or full AI mode, but reject if neither AI nor rules_only is configured
        if not self.ai_enabled and not self.rules_only_mode:
            log_message(
                "AI not available and rules_only_mode not enabled for numbered processing"
            )
            return None

        if not self.change_tracker:
            log_message("No change tracker provided for review mode")
            return None

        if self.rules_only_mode:
            log_message("Starting RULES-ONLY numbered line processing (review mode)")
        else:
            log_message("Starting AI numbered line processing (review mode)")

        # Set up numbered analysis log
        if hasattr(ctx, "current_file_path") and ctx.current_file_path:
            self._setup_numbered_log(ctx.current_file_path)
            if self.rules_only_mode:
                self._log_to_numbered_log(
                    f"Starting RULES-ONLY numbered analysis (REVIEW MODE)\n"
                )
            else:
                self._log_to_numbered_log(
                    f"Starting AI numbered analysis (REVIEW MODE)\n"
                )
                self._log_to_numbered_log(f"AI Provider: {self.ai_service.provider}\n")
                self._log_to_numbered_log(f"AI Model: {self.ai_service.model}\n")
            self._log_to_numbered_log(
                f"Confidence Threshold: {self.confidence_threshold}\n\n"
            )

        # Step 1: Analyze text context
        text_context = self._analyze_text_context(ctx.text)
        log_message(f"Text context analysis: {text_context}")

        if self.numbered_log_path:
            self._log_to_numbered_log(f"Text Context Analysis:\n")
            self._log_to_numbered_log(
                f"  Primary Context: {text_context['primary_context']}\n"
            )
            self._log_to_numbered_log(
                f"  Is Military: {text_context.get('is_military', False)}\n"
            )
            self._log_to_numbered_log(
                f"  Has Time Focus: {text_context.get('has_time_focus', False)}\n"
            )
            self._log_to_numbered_log(
                f"  Has Date Focus: {text_context.get('has_date_focus', False)}\n"
            )
            self._log_to_numbered_log(
                f"  Is Technical: {text_context.get('is_technical', False)}\n\n"
            )

        # Step 2: Find numbered lines
        numbered_lines = self._find_all_numbers_for_ai(ctx.text)
        if not numbered_lines:
            log_message("No numbered lines found")
            return None

        log_message(f"Found {len(numbered_lines)} numbered lines to analyze")

        # Log all detected numbers (before analysis) to detection log
        if hasattr(self, "detection_log_path") and self.detection_log_path:
            total_numbers_detected = sum(len(spans) for _, _, spans in numbered_lines)
            with open(self.detection_log_path, "a", encoding="utf-8") as f:
                f.write(f"DETECTION SUMMARY\n")
                f.write(f"Total lines with numbers: {len(numbered_lines)}\n")
                f.write(f"Total numbers detected: {total_numbers_detected}\n")
                f.write(f"{'=' * 80}\n\n")

            for line_no, line_content, spans in numbered_lines:
                self._log_detection(line_no, line_content, spans)

        # Step 3: PRE-CLASSIFY numbers with batching
        # First pass: collect all numbers that need AI classification
        # Always initialize batch_classifications, even if empty (for rules-only mode)
        batch_classifications = {}

        # Only do batching if AI is available and not in rules-only mode
        if self.ai_service and not self.rules_only_mode:
            numbers_for_batch = []
            batch_id = 0
            batch_key_map = {}  # Maps batch_id to (number, batch_key)

            log_message("First pass: Collecting numbers that need AI classification...")

            for line_no, line_content, spans in numbered_lines:
                for start, end in spans:
                    number = line_content[start:end]
                    context_before = line_content[max(0, start - 50) : start]
                    context_after = line_content[end : end + 50]

                    # Try rules first (without AI fallback)
                    number_digits = number.replace(",", "")
                    ctx_lower = (context_before + " " + context_after).lower()

                    # Check learned patterns first
                    learned_classification = self.learning_storage.get_learned_classification(
                        number_digits, context_before, context_after
                    )
                    if learned_classification:
                        # Use learned classification, skip AI
                        batch_key = f"{number}|{context_before + ' ' + context_after}"
                        batch_classifications[batch_key] = (learned_classification, "learned")
                        continue

                    # Try rules (simplified check - just see if rules would match)
                    # We'll do full rule check later, this is just to filter out obvious rule matches
                    has_ordinal = bool(re.search(r"\d+(st|nd|rd|th)$", number))
                    has_currency_symbol = bool(re.match(r"[\$£€¢¥₹]", number))

                    if has_ordinal or has_currency_symbol:
                        # Rules will handle this, don't need AI
                        continue

                    # This number needs AI classification - add to batch
                    batch_id += 1
                    batch_key = f"{number}|{context_before + ' ' + context_after}"
                    full_context = f"{context_before} **{number}** {context_after}"

                    numbers_for_batch.append({
                        "id": batch_id,
                        "number": number,
                        "context": full_context
                    })
                    batch_key_map[batch_id] = (number, batch_key)

            # Send batches to AI
            if numbers_for_batch:
                log_message(f"Sending {len(numbers_for_batch)} numbers to AI in batches...")
                BATCH_SIZE = 20
                all_batch_results = {}

                for i in range(0, len(numbers_for_batch), BATCH_SIZE):
                    chunk = numbers_for_batch[i : i + BATCH_SIZE]
                    log_message(
                        f"Batch {i//BATCH_SIZE + 1}: Processing {len(chunk)} numbers (IDs: {chunk[0]['id']}-{chunk[-1]['id']})"
                    )

                    try:
                        chunk_results = self.ai_service.classify_numbers_batch(chunk)
                        all_batch_results.update(chunk_results)
                    except Exception as e:
                        import traceback
                        log_message(f"Error in batch {i//BATCH_SIZE + 1}: {type(e).__name__}: {e}", level="ERROR")
                        log_message(f"Traceback:\n{traceback.format_exc()}", level="DEBUG")
                        # Create failure responses for this chunk
                        for item in chunk:
                            all_batch_results[item["id"]] = type('obj', (object,), {
                                'success': False,
                                'content': 'general_number',
                                'reasoning': f"Batch failed: {e}"
                            })()

                # Store results for later use
                for batch_id, ai_response in all_batch_results.items():
                    number, batch_key = batch_key_map[batch_id]
                    if ai_response.success:
                        batch_classifications[batch_key] = (ai_response.content, "llm")
                        log_message(
                            f"AI classified '{number}' as '{ai_response.content}'"
                        )
                    else:
                        batch_classifications[batch_key] = ("general_number", "default")
                        log_message(
                            f"AI classification failed for '{number}', using default"
                        )

                log_message(f"Batch classification complete. {len(batch_classifications)} numbers pre-classified.")

        # Step 4: Analyze each numbered line and track changes
        analysis_count = 0
        changes_made = 0
        temp_text = ctx.text  # Work with temporary text for calculating positions
        line_changes = {}  # Store changes per line for tracking (even no-change lines)

        for line_no, line_content, spans in numbered_lines:
            try:
                # Get AI analysis for this line (with pre-computed batch classifications)
                ai_result = self._analyze_numbered_line_ai(
                    line_content, spans, text_context, batch_classifications
                )
                log_message(
                    f"AI analysis for line {line_no + 1}: should_change={ai_result.get('should_change', False)}, confidence={ai_result.get('confidence', 0)}"
                )

                # Log this analysis
                analysis_count += 1
                if self.numbered_log_path:
                    self._log_number_analysis(
                        analysis_count, line_content, spans, ai_result, text_context
                    )

                # If the AI determined a change should be made, iterate through the specific changes
                if ai_result.get("should_change", False) and ai_result.get("changes"):
                    # Calculate line position in text once for this line
                    lines_before = temp_text.splitlines()[:line_no]
                    line_start_pos = sum(len(l) + 1 for l in lines_before)  # +1 for \n

                    # Iterate directly over the changes the analyzer found
                    for change in ai_result["changes"]:
                        original_number = change["original"]
                        new_number = change["replacement"]
                        start_in_line = change["start"]
                        end_in_line = change["end"]

                        # Calculate absolute position in full text
                        abs_position = line_start_pos + start_in_line
                        abs_end = line_start_pos + end_in_line

                        # Extract context from the original full text for an accurate review display
                        context_before = temp_text[
                            max(0, abs_position - 100) : abs_position
                        ]
                        context_after = temp_text[
                            abs_end : min(len(temp_text), abs_end + 100)
                        ]

                        # Add the identified change to the tracker for review
                        self.change_tracker.add_change(
                            module_name="numbered",
                            original=original_number,
                            replacement=new_number,
                            options=[original_number, new_number],
                            start_pos=abs_position,
                            end_pos=abs_end,
                            context_before=context_before,
                            context_after=context_after,
                            confidence=change.get("confidence", 0.8),
                            reasoning=change.get(
                                "reasoning",
                                "AI determined this number should be formatted differently",
                            ),
                            type=change.get("type", "general_number"),
                            decision_source=change.get("decision_source", "unknown"),
                        )
                        changes_made += 1
                        log_message(
                            f"Tracked change for line {line_no + 1}: '{original_number}' → '{new_number}'"
                        )
                else:
                    # Log if AI suggested no changes for this line
                    log_message(f"AI suggested no change for line {line_no + 1}")

            except Exception as e:
                log_message(f"Failed to analyze line {line_no + 1}: {e}", level="ERROR")
                if self.numbered_log_path:
                    self._log_to_numbered_log(f"\n{'=' * 80}\n")
                    self._log_to_numbered_log(f"ANALYSIS #{analysis_count} - ERROR\n")
                    self._log_to_numbered_log(f"{'=' * 80}\n")
                    self._log_to_numbered_log(f"Original text: {line_content}\n")
                    self._log_to_numbered_log(f"Error: {e}\n\n")

        # Write summary to log
        if self.numbered_log_path:
            self._log_to_numbered_log(f"\n{'=' * 80}\n")
            self._log_to_numbered_log(f"PROCESSING SUMMARY (REVIEW MODE)\n")
            self._log_to_numbered_log(f"{'=' * 80}\n\n")
            self._log_to_numbered_log(f"Total analyses: {analysis_count}\n")
            self._log_to_numbered_log(f"Changes tracked for review: {changes_made}\n")
            self._log_to_numbered_log(
                f"\nAnalysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            log_message(f"Numbered analysis log saved to: {self.numbered_log_path}")

        log_message(
            f"AI numbered analysis complete: {len(self.change_tracker.changes)} changes ready for review"
        )

        if len(self.change_tracker.changes) == 0:
            return None

        return self.change_tracker

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

            # 4) Decimal numbers (check first to catch small decimals like 3.14, 14.3)
            decimal_spans = []
            for match in decimal_pattern.finditer(line):
                decimal_spans.append((match.start(), match.end()))
                spans.append((match.start(), match.end()))

            # 5) General numbers (skip if already captured as decimal)
            for match in number_pattern.finditer(line):
                s, e = match.span()

                # Skip if this number overlaps with a decimal we already captured
                overlaps_decimal = any(
                    (s >= ds and s < de) or (e > ds and e <= de) or (s <= ds and e >= de)
                    for ds, de in decimal_spans
                )
                if overlaps_decimal:
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
                    spans.append((s, e))

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

    def _apply_number_rules(
        self, number: str, context_before: str, context_after: str, text_context: Dict
    ) -> str:
        """Apply learned rules to format numbers based on context."""

        # Rule 1: Military time (4 digits starting with 0, military context)
        if (
            len(number) == 4
            and number.startswith("0")
            and (text_context.get("is_military", False) or "hours" in context_after)
        ):
            return f"zero {number[1:]}"

        # Rule 2: Military time (4 digits for hundreds like 2100)
        if (
            len(number) == 4
            and number.endswith("00")
            and (text_context.get("is_military", False) or "hours" in context_after)
        ):
            hundreds = int(number[:2])
            if 10 <= hundreds <= 23:  # Valid military hours
                return f"{hundreds} hundred"

        # Rule 3: Years - break into spoken digits
        if len(number) == 4 and (
            number.startswith("19")
            or number.startswith("20")
            or number.startswith("24")
        ):
            combined_context = context_before + context_after
            date_words = [
                "since",
                "in",
                "year",
                "born",
                "during",
                "april",
                "january",
                "february",
                "march",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
            ]
            found_date_word = any(word in combined_context for word in date_words)
            log_message(
                f"Year rule check for '{number}': combined_context='{combined_context}', found_date_word={found_date_word}"
            )
            if found_date_word:
                return f"{number[:2]} {number[2:]}"

        # Rule 4: Model numbers and technical codes - usually keep as-is
        if any(
            word in context_before
            for word in ["model", "serial", "part", "version", "code"]
        ):
            return number

        # Rule 5: Ship/vessel numbers - usually keep as spoken digits
        if any(
            word in context_before
            for word in ["ship", "vessel", "destroyer", "cruiser", "submarine"]
        ):
            if len(number) == 4:
                return f"{number[0]} {number[1]} {number[2]} {number[3]}"

        # Rule 6: General 4-digit numbers in military context - be conservative
        if len(number) == 4 and text_context.get("is_military", False):
            # If it looks like a year, break it up
            if 1800 <= int(number) <= 2100:
                return f"{number[:2]} {number[2:]}"

        # Default: no change
        return number

    def _get_rule_reasoning(
        self, original: str, replacement: str, before: str, after: str, context: Dict
    ) -> str:
        """Generate reasoning for why a number was changed."""

        if replacement.startswith("zero "):
            return "Military time format (0XXX → zero XXX)"
        elif "hundred" in replacement:
            return "Military time format (XXXX → XX hundred)"
        elif " " in replacement and len(original) == 4:
            if original.startswith("19"):
                return "Year format for TTS (19XX → 19 XX)"
            else:
                return "Spoken digit format for clarity"
        else:
            return "Applied formatting rule"

    def _track_actual_changes(self, final_text: str, line_changes: Dict):
        """Track actual changes made by AI, not individual numbers."""
        if not self.change_tracker:
            return

        final_lines = final_text.splitlines()

        # Calculate absolute line start positions
        line_start_positions = [0]
        for line in final_lines:
            line_start_positions.append(
                line_start_positions[-1] + len(line) + 1
            )  # +1 for newline

        # Process each line that had changes or numbers
        for line_no, change_info in line_changes.items():
            if change_info["changed"]:
                # Line was actually changed - track the specific changes made
                self._track_line_changes(
                    final_text, line_no, change_info, line_start_positions[line_no]
                )
            else:
                # Line wasn't changed but has numbers - track individual unchanged numbers
                self._track_unchanged_numbers(
                    final_text, line_no, change_info, line_start_positions[line_no]
                )

    def _track_line_changes(
        self, final_text: str, line_no: int, change_info: Dict, line_start_pos: int
    ):
        """Track actual changes made to a line."""
        original_line = change_info["original_line"]
        new_line = change_info["new_line"]
        original_spans = change_info["original_spans"]
        ai_result = change_info["ai_result"]

        # If ai_result has detailed changes with decision_source, use those
        if "changes" in ai_result and ai_result["changes"]:
            for change in ai_result["changes"]:
                original_number = change["original"]
                replacement_text = change["replacement"]

                # Calculate position in final text
                orig_start = change["start"]
                final_start_pos, final_end_pos = self._find_replacement_position(
                    new_line, replacement_text, orig_start, line_start_pos
                )

                # Track this change with decision_source
                self.change_tracker.add_change(
                    module_name="numbered",
                    original=original_number,
                    replacement=replacement_text,
                    start_pos=final_start_pos,
                    end_pos=final_end_pos,
                    context_before=original_line[max(0, orig_start - 30) : orig_start],
                    context_after=original_line[change["end"] : change["end"] + 30],
                    confidence=change.get("confidence", 0.8),
                    reasoning=change.get(
                        "reasoning",
                        f'AI changed "{original_number}" to "{replacement_text}"',
                    ),
                    decision_source=change.get("decision_source", "unknown"),
                )
        else:
            # Fallback for older code path without detailed changes
            for orig_start, orig_end in original_spans:
                original_number = original_line[orig_start:orig_end]

                # Find where this number ended up in the final line
                # This handles cases like "2472" -> "24 72"
                replacement_text = self._find_replacement_in_line(
                    original_number, original_line, new_line, orig_start
                )

                # Calculate position of the replacement in final text
                final_start_pos, final_end_pos = self._find_replacement_position(
                    new_line, replacement_text, orig_start, line_start_pos
                )

                # Track this change (without decision_source)
                self.change_tracker.add_change(
                    module_name="numbered",
                    original=original_number,
                    replacement=replacement_text,
                    start_pos=final_start_pos,
                    end_pos=final_end_pos,
                    context_before=original_line[max(0, orig_start - 30) : orig_start],
                    context_after=original_line[orig_end : orig_end + 30],
                    confidence=ai_result.get("confidence", 0.8),
                    reasoning=ai_result.get(
                        "reasoning",
                        f'AI changed "{original_number}" to "{replacement_text}"',
                    ),
                    decision_source="unknown",
                )

    def _track_unchanged_numbers(
        self, final_text: str, line_no: int, change_info: Dict, line_start_pos: int
    ):
        """Track individual numbers that weren't changed."""
        line_content = change_info["new_line"]
        spans = change_info["original_spans"]
        ai_result = change_info["ai_result"]

        for start, end in spans:
            number_text = line_content[start:end]
            absolute_start = line_start_pos + start
            absolute_end = line_start_pos + end

            self.change_tracker.add_change(
                module_name="numbered_unchanged",
                original=number_text,
                replacement=number_text,
                start_pos=absolute_start,
                end_pos=absolute_end,
                context_before=line_content[max(0, start - 30) : start],
                context_after=line_content[end : end + 30],
                confidence=ai_result.get("confidence", 1.0),
                reasoning=ai_result.get(
                    "reasoning", f'No change needed for "{number_text}"'
                ),
            )

    def _find_replacement_in_line(
        self, original_number: str, original_line: str, new_line: str, orig_pos: int
    ) -> str:
        """Find what the original number became in the new line."""
        # Get the changes from ai_result if available
        # For now, simple approach: find the text that replaced the original number

        # Get the context around the original number
        before_orig = original_line[:orig_pos]
        after_orig = original_line[orig_pos + len(original_number) :]

        # Find the same context in the new line
        if before_orig in new_line and after_orig in new_line:
            before_pos = new_line.find(before_orig) + len(before_orig)
            after_pos = new_line.find(after_orig, before_pos)
            if after_pos > before_pos:
                return new_line[before_pos:after_pos]

        # Fallback: assume it's the same
        return original_number

    def _find_replacement_position(
        self, new_line: str, replacement_text: str, approx_pos: int, line_start_pos: int
    ) -> tuple:
        """Find the position of replacement text in the new line."""
        # Try to find the replacement text near the original position
        search_start = max(0, approx_pos - 10)
        search_end = min(len(new_line), approx_pos + 20)
        search_area = new_line[search_start:search_end]

        pos_in_search = search_area.find(replacement_text)
        if pos_in_search >= 0:
            actual_pos = search_start + pos_in_search
            return (
                line_start_pos + actual_pos,
                line_start_pos + actual_pos + len(replacement_text),
            )

        # Fallback to approximate position
        return (
            line_start_pos + approx_pos,
            line_start_pos + approx_pos + len(replacement_text),
        )
