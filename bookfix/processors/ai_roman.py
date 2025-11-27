"""
AI-Enhanced Roman Numeral Processor for Bookfix.

Extends the RomanNumeralProcessor with AI analysis capabilities
for intelligent roman numeral conversion decisions with change tracking.
"""

import re
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..context import BookfixContext

from .roman import RomanNumeralProcessor, roman_to_arabic
from ..ai.service import BookfixAIService
from ..ai.change_tracker import AIChangeTracker
from ..logging import log_message


class AIRomanProcessor(RomanNumeralProcessor):
    """
    AI-enhanced roman numeral processor that can intelligently decide
    whether to convert roman numerals based on context analysis.
    """

    def __init__(self, change_tracker: Optional[AIChangeTracker] = None):
        super().__init__()
        self.ai_service: Optional[BookfixAIService] = None
        self.ai_enabled = False
        self.confidence_threshold = 0.8
        self.fallback_to_automatic = True

        # Change tracking
        self.change_tracker = change_tracker

        # Track AI decisions for review
        self.ai_decisions = []
        self.automatic_decisions = []
        self.conversions_made = 0
        self.abbreviations_preserved = 0

        # Track conversions during regex processing for batch AI validation
        self.tracked_conversions = []

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

            self.confidence_threshold = ai_config.get("confidence_threshold", 0.8)
            self.fallback_to_automatic = ai_config.get("fallback_to_automatic", True)

            # Test AI connection
            test_result = self.ai_service.test_connection()
            if not test_result.success:
                log_message(
                    f"AI service connection failed: {test_result.error_message}",
                    level="WARNING",
                )
                if not self.fallback_to_automatic:
                    return False
                log_message("Will fallback to automatic processing")
            else:
                log_message(
                    f"AI service initialized successfully: {test_result.content}"
                )

            return True

        except Exception as e:
            log_message(f"Failed to initialize AI service: {e}", level="ERROR")
            self.ai_enabled = False
            return False

    def process_roman_numerals(self, ctx: "BookfixContext") -> "BookfixContext":
        """
        Process roman numerals with AI batch validation.

        New approach:
        1. Regex runs first and makes all conversions (tracking them during callback)
        2. AI validates ALL conversions in a single batch call
        3. Apply corrections for any false positives

        Args:
            ctx: BookfixContext with text and roman numerals to process

        Returns:
            Updated BookfixContext with AI-validated conversions
        """
        if not self.ai_enabled or not self.ai_service:
            log_message("AI not available, falling back to automatic processing")
            return super().process_roman_numerals(ctx)

        log_message("Starting regex + batch AI validation processing")

        # Store original text
        original_text = ctx.text
        log_message(
            f"ORIGINAL TEXT ({len(original_text)} chars, {len(original_text.split(chr(10)))} lines)"
        )

        # Step 1: Run regex conversion with conversion tracking
        self.tracked_conversions = []
        ctx_regex = self._process_roman_with_tracking(ctx)
        regex_text = ctx_regex.text

        log_message(f"Regex made {len(self.tracked_conversions)} conversions")

        if not self.tracked_conversions:
            log_message("No conversions made, no AI review needed")
            return ctx_regex

        # Step 2: Batch AI validation of all conversions
        log_message(
            f"Sending {len(self.tracked_conversions)} conversions for batch AI validation"
        )
        ai_decisions = self._ai_batch_validate(self.tracked_conversions)

        if not ai_decisions:
            log_message("Batch validation failed, keeping regex results")
            ctx.text = regex_text
            self.conversions_made = len(self.tracked_conversions)
            return ctx

        # Step 3: Apply AI corrections (reversions only)
        corrected_text = regex_text
        ai_reversions = []

        for idx, decision in enumerate(ai_decisions):
            if decision.get("action") == "REVERT" and idx < len(
                self.tracked_conversions
            ):
                conversion = self.tracked_conversions[idx]
                original_roman = conversion["original"]
                converted_value = conversion["converted"]

                # Revert this conversion by replacing the number back with Roman numeral
                corrected_text = corrected_text.replace(
                    converted_value, original_roman, 1
                )
                ai_reversions.append(
                    {
                        "original_roman": original_roman,
                        "conversion_attempted": converted_value,
                        "reason": decision.get("reason", "AI validation"),
                    }
                )
                log_message(f"REVERTED: '{original_roman}' (was '{converted_value}')")

        ctx.text = corrected_text
        log_message(
            f"Batch validation complete: {len(self.tracked_conversions)} conversions, {len(ai_reversions)} reversions"
        )

        # Step 4: Track changes for review
        if self.change_tracker:
            for conversion in self.tracked_conversions:
                # Check if this conversion was reverted
                was_reverted = any(
                    r["original_roman"] == conversion["original"] for r in ai_reversions
                )
                if not was_reverted:
                    # Track the kept conversion
                    context_start = max(0, conversion["position"] - 50)
                    context_end = min(
                        len(original_text),
                        conversion["position"] + len(conversion["original"]) + 50,
                    )
                    context = original_text[context_start:context_end]

                    self.change_tracker.add_change(
                        module_name="roman",
                        original=conversion["original"],
                        replacement=conversion["converted"],
                        options=["KEEP", "REVERT"],
                        start_pos=conversion["position"],
                        end_pos=conversion["position"] + len(conversion["original"]),
                        context_before="",
                        context_after="",
                        confidence=0.9,
                        reasoning="Regex conversion (approved by AI batch validation)",
                    )

        self.conversions_made = len(self.tracked_conversions) - len(ai_reversions)
        self.abbreviations_preserved = len(ai_reversions)

        return ctx

    def _process_roman_with_tracking(self, ctx: "BookfixContext") -> "BookfixContext":
        """
        Run regex conversion with direct tracking of each conversion.
        Avoids the broken difflib approach by capturing conversions during callback.
        """
        # Ensure roman_ignore_set exists (convert list to set for fast lookup)
        if not hasattr(ctx, "roman_ignore_set"):
            ctx.roman_ignore_set = (
                set(ctx.roman_ignore) if hasattr(ctx, "roman_ignore") else set()
            )

        self.tracked_conversions = []
        roman_pattern = r"(?<![A-Za-z&\-+:;/\\'`´''])\b([VXLCDM]|[MDCLXVI]{2,})\b(?![A-Za-z&\-+:;/\\]|['`´''][a-rtuvwxyzA-RTUVWXYZ])"

        def _replace_with_tracking(m):
            token = m.group(1) if m.lastindex and m.lastindex >= 1 else m.group(0)
            start_pos = m.start()
            end_pos = m.end()

            # Additional context checks for edge cases (from parent class)
            before_char = ctx.text[start_pos - 1] if start_pos > 0 else " "
            after_char = ctx.text[end_pos] if end_pos < len(ctx.text) else " "

            # Skip version numbers like "X.V1" or "II.5"
            # Only skip if followed by alphanumeric (not whitespace/newline)
            if (
                after_char == "."
                and end_pos + 1 < len(ctx.text)
                and ctx.text[end_pos + 1].isalnum()
            ) or (
                before_char == "."
                and start_pos > 1
                and ctx.text[start_pos - 2] in "VXLCDMI"
            ):
                return token

            # Skip if it's a common English word that happens to be Roman
            if token.upper() in ["MIX"]:
                context_before = ctx.text[max(0, start_pos - 20) : start_pos].lower()
                if not any(
                    word in context_before
                    for word in ["chapter", "section", "part", "volume", "book"]
                ):
                    return token

            # Check ignore list
            if token.upper() in ctx.roman_ignore_set:
                return token

            val = roman_to_arabic(token)

            if isinstance(val, int) and val > 0:
                # Track this conversion with context
                context_start = max(0, start_pos - 100)
                context_end = min(len(ctx.text), end_pos + 100)
                context = ctx.text[context_start:context_end]

                self.tracked_conversions.append(
                    {
                        "original": token,
                        "converted": str(val),
                        "position": start_pos,
                        "context": context,
                    }
                )

                return str(val)

            return token

        # Perform substitution
        ctx.text = re.sub(roman_pattern, _replace_with_tracking, ctx.text)
        return ctx

    def _clean_context(self, text: str) -> str:
        """
        Clean context text by normalizing whitespace.

        Replaces multiple newlines/spaces with single space to reduce
        token usage and provide cleaner context to AI models.

        Args:
            text: Raw context text with excessive whitespace

        Returns:
            Cleaned text with normalized spacing
        """
        # Replace multiple newlines, tabs, and spaces with single space
        cleaned = re.sub(r"\s+", " ", text)
        return cleaned.strip()

    def _ai_batch_validate(self, conversions: List[Dict]) -> Optional[List[Dict]]:
        """
        Validate all conversions in batch API calls with chunking for large batches.

        Args:
            conversions: List of dicts with 'original', 'converted', 'context'

        Returns:
            List of decisions: [{'index': 0, 'action': 'KEEP'|'REVERT', 'reason': '...'}]
            or None if API call fails
        """
        if not conversions:
            return []

        # Chunk large batches to avoid token limits (50 conversions per chunk)
        chunk_size = 50
        all_decisions = []

        if len(conversions) > chunk_size:
            log_message(
                f"Splitting {len(conversions)} conversions into chunks of {chunk_size}"
            )
            for chunk_idx, i in enumerate(range(0, len(conversions), chunk_size)):
                chunk = conversions[i : i + chunk_size]
                chunk_num = chunk_idx + 1
                total_chunks = (len(conversions) + chunk_size - 1) // chunk_size
                log_message(
                    f"Processing chunk {chunk_num}/{total_chunks} ({len(chunk)} conversions)"
                )

                chunk_decisions = self._process_batch_chunk(chunk)
                if chunk_decisions is None:
                    return None
                all_decisions.extend(chunk_decisions)

            return all_decisions
        else:
            # Single batch for small number of conversions
            return self._process_batch_chunk(conversions)

    def _process_batch_chunk(self, conversions: List[Dict]) -> Optional[List[Dict]]:
        """
        Process a single batch chunk.

        Args:
            conversions: List of dicts with 'original', 'converted', 'context'

        Returns:
            List of decisions with adjusted indices, or None if API call fails
        """
        # Build batch prompt with cleaned context
        conversions_text = "\n".join(
            [
                f"{i+1}. Context: ...{self._clean_context(c['context'])}...\n   Conversion: \"{c['original']}\" → \"{c['converted']}\""
                for i, c in enumerate(conversions)
            ]
        )

        # Load prompt template from file
        prompt_template = self.ai_service._load_prompt("roman_conversion_batch")
        if not prompt_template:
            log_message(
                "Failed to load roman_conversion_batch.txt, using fallback prompt",
                level="WARNING",
            )
            # Fallback to a minimal prompt if file not found
            prompt_template = """Review these Roman numeral conversions. For each, decide if it should be KEPT or REVERTED.

CONVERSIONS TO REVIEW:
{conversions_text}

RESPOND WITH JSON ARRAY (one decision per conversion):
[
  {{"index": 1, "action": "KEEP"}},
  {{"index": 2, "action": "REVERT"}}
]

Output ONLY the JSON array, no other text."""

        # Format the prompt with conversions
        prompt = prompt_template.format(conversions_text=conversions_text)

        try:
            response = self.ai_service._make_request(prompt)
            if response.success:
                return self._parse_batch_validation_response(response.content)
            else:
                log_message(
                    f"Batch validation failed: {response.error_message}",
                    level="WARNING",
                )
                return None
        except Exception as e:
            log_message(f"Error in batch validation: {e}", level="ERROR")
            return None

    def _parse_batch_validation_response(
        self, response_text: str
    ) -> Optional[List[Dict]]:
        """
        Parse JSON array response from batch validation.

        Returns list of decisions or None if parsing fails.
        """
        try:
            import json

            content = response_text.strip()

            # Remove markdown code fences if present
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            decisions = json.loads(content)

            if not isinstance(decisions, list):
                log_message(
                    f"Batch response is not a list: {type(decisions)}", level="WARNING"
                )
                return None

            return decisions

        except json.JSONDecodeError as e:
            log_message(f"Failed to parse batch validation JSON: {e}", level="WARNING")
            log_message(
                f"Response (first 500 chars): {response_text[:500]}", level="DEBUG"
            )
            return None
        except Exception as e:
            log_message(f"Error parsing batch validation response: {e}", level="ERROR")
            return None

    def _apply_replacements(
        self, ctx: "BookfixContext", replacements: List[Dict]
    ) -> None:
        """Apply all replacements in batch to avoid position corruption."""
        if not replacements:
            return

        # Sort by position (rightmost first) to avoid position corruption
        replacements.sort(key=lambda x: x["start"], reverse=True)

        log_message(f"Applying {len(replacements)} roman numeral replacements")

        # Store original text for final position calculation
        original_text = ctx.text

        # Apply replacements in reverse order
        for replacement in replacements:
            start_pos = replacement["start"]
            end_pos = replacement["end"]
            original = replacement["original"]
            new_text = replacement["replacement"]

            # Verify the text at this position matches what we expect
            actual_text = ctx.text[start_pos:end_pos]
            if actual_text != original:
                log_message(
                    f"Position mismatch for '{original}': expected '{original}', found '{actual_text}' at {start_pos}-{end_pos}",
                    level="WARNING",
                )
                continue

            # Apply the conversion
            ctx.text = ctx.text[:start_pos] + new_text + ctx.text[end_pos:]

            self.conversions_made += 1
            log_message(
                f"{replacement['source']} converted '{original}' to '{new_text}' at position {start_pos}-{end_pos}"
            )

        # Now calculate final positions and track changes
        if self.change_tracker:
            self._track_final_changes(original_text, ctx.text, replacements)

        log_message(f"Completed {self.conversions_made} roman numeral conversions")

    def _track_final_changes(
        self, original_text: str, final_text: str, replacements: List[Dict]
    ) -> None:
        """Track changes with correct final text positions."""
        # Simple approach: find each replacement text in the final text
        # We'll track them in the order they appear in final text

        tracked_positions = []  # Keep track of positions already used

        for replacement in reversed(replacements):  # Process in original order
            original = replacement["original"]
            new_text = replacement["replacement"]

            # Find the replacement text in final text, avoiding already tracked positions
            search_start = 0
            found_pos = -1

            while True:
                pos = final_text.find(new_text, search_start)
                if pos == -1:
                    break

                # Check if this position conflicts with already tracked positions
                conflicts = False
                for tracked_start, tracked_end in tracked_positions:
                    if not (pos >= tracked_end or pos + len(new_text) <= tracked_start):
                        conflicts = True
                        break

                if not conflicts:
                    found_pos = pos
                    break

                search_start = pos + 1

            if found_pos >= 0:
                final_start_pos = found_pos
                final_end_pos = found_pos + len(new_text)

                # Mark this position as used
                tracked_positions.append((final_start_pos, final_end_pos))

                # Get context around the final position
                context_start = max(0, final_start_pos - 50)
                context_end = min(len(final_text), final_end_pos + 50)
                full_context = final_text[context_start:context_end]

                relative_start = final_start_pos - context_start
                relative_end = final_end_pos - context_start

                context_before = (
                    full_context[:relative_start] if relative_start > 0 else ""
                )
                context_after = (
                    full_context[relative_end:]
                    if relative_end < len(full_context)
                    else ""
                )

                self.change_tracker.add_change(
                    module_name="roman",
                    original=original,
                    replacement=new_text,
                    options=["KEEP", "REVERT"],
                    start_pos=final_start_pos,
                    end_pos=final_end_pos,
                    context_before=context_before,
                    context_after=context_after,
                    confidence=replacement["confidence"],
                    reasoning=replacement["reasoning"],
                )

                log_message(
                    f"Tracked change '{original}' → '{new_text}' at final position {final_start_pos}-{final_end_pos}"
                )
            else:
                log_message(
                    f"Could not locate final position for '{original}' → '{new_text}'",
                    level="WARNING",
                )

    def _get_replacement_text(self, token: str, arabic_value: int, context: str) -> str:
        """
        Determine the appropriate replacement text based on context.

        Args:
            token: Original Roman numeral
            arabic_value: Arabic number equivalent
            context: Surrounding context

        Returns:
            Replacement text (number, ordinal word, or original)
        """
        context_lower = context.lower()

        # Check for royal/pope names that should use ordinal words
        # Look for specific patterns where names are followed by Roman numerals
        royal_patterns = [
            r"henry\s+" + token.lower(),
            r"john\s+" + token.lower(),
            r"charles\s+" + token.lower(),
            r"james\s+" + token.lower(),
            r"william\s+" + token.lower(),
            r"edward\s+" + token.lower(),
            r"richard\s+" + token.lower(),
            r"george\s+" + token.lower(),
            r"pope\s+\w+\s+" + token.lower(),  # Pope John V
        ]

        for pattern in royal_patterns:
            if re.search(pattern, context_lower):
                return self._number_to_ordinal_word(arabic_value)

        # Default to number conversion
        return str(arabic_value)

    def _number_to_ordinal_word(self, number: int) -> str:
        """
        Convert number to ordinal word form.

        Args:
            number: Integer to convert

        Returns:
            Ordinal word (e.g., 1 -> "the First", 8 -> "the Eighth")
        """
        ordinal_words = {
            1: "the First",
            2: "the Second",
            3: "the Third",
            4: "the Fourth",
            5: "the Fifth",
            6: "the Sixth",
            7: "the Seventh",
            8: "the Eighth",
            9: "the Ninth",
            10: "the Tenth",
            11: "the Eleventh",
            12: "the Twelfth",
            13: "the Thirteenth",
            14: "the Fourteenth",
            15: "the Fifteenth",
            16: "the Sixteenth",
            17: "the Seventeenth",
            18: "the Eighteenth",
            19: "the Nineteenth",
            20: "the Twentieth",
        }

        return ordinal_words.get(number, f"the {number}th")

    def _find_roman_conversions(
        self, original_text: str, converted_text: str
    ) -> List[Dict]:
        """
        Find Roman numeral conversions by matching against the original pattern.
        This is smarter than difflib as it focuses on actual Roman numerals.
        """
        from .roman import roman_to_arabic

        changes = []

        # Use the same pattern as the original processor
        roman_pattern = r"(?<![A-Za-z&\-+:;/\\'`´''])\b([VXLCDM]|[MDCLXVI]{2,})\b(?![A-Za-z&\-+:;/\\]|['`´''][a-rtuvwxyzA-RTUVWXYZ])"

        # Find all Roman numerals in original text
        for match in re.finditer(roman_pattern, original_text):
            token = (
                match.group(1)
                if match.lastindex and match.lastindex >= 1
                else match.group(0)
            )
            start_pos = match.start()
            end_pos = match.end()

            # Check if this Roman numeral was converted
            arabic_value = roman_to_arabic(token)
            if isinstance(arabic_value, int) and arabic_value > 0:
                # Look for the arabic equivalent in the converted text at the same position
                # (accounting for length differences from previous conversions)
                arabic_str = str(arabic_value)

                # Check if this position in converted text contains the arabic number
                if start_pos < len(converted_text):
                    # Find what's at this position in converted text
                    # This is a simplified check - in a perfect implementation we'd track position shifts
                    surrounding_text = converted_text[
                        max(0, start_pos - 10) : start_pos + 20
                    ]

                    if arabic_str in surrounding_text:
                        changes.append(
                            {
                                "original": token,
                                "replacement": arabic_str,
                                "start_pos": start_pos,
                                "end_pos": end_pos,
                                "context": self._extract_context(
                                    original_text, start_pos, end_pos, 150
                                ),
                            }
                        )

        return changes

    def _find_changes_between_texts(self, original: str, converted: str) -> List[Dict]:
        """
        Find what changed between original and converted text.

        Returns list of changes with original, replacement, and position info.
        """
        import difflib

        changes = []

        # Use difflib to find differences
        matcher = difflib.SequenceMatcher(None, original, converted)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "replace":
                # Found a replacement
                original_text = original[i1:i2]
                replacement_text = converted[j1:j2]

                # Only track if it looks like a Roman numeral conversion
                if self._looks_like_roman_conversion(original_text, replacement_text):
                    changes.append(
                        {
                            "original": original_text,
                            "replacement": replacement_text,
                            "start_pos": i1,
                            "end_pos": i2,
                            "context": self._extract_context(original, i1, i2, 150),
                        }
                    )

        return changes

    def _looks_like_roman_conversion(self, original: str, replacement: str) -> bool:
        """Check if this looks like a Roman numeral conversion."""
        # Check if original contains Roman numeral characters
        roman_chars = set("IVXLCDM")
        if not any(c in roman_chars for c in original.upper()):
            return False

        # Check if replacement is numeric or contains numbers
        if not any(c.isdigit() for c in replacement):
            return False

        # Additional validation: original should be mostly Roman numeral characters
        original_upper = original.upper()
        roman_char_count = sum(1 for c in original_upper if c in roman_chars)

        # At least 70% of characters should be Roman numeral characters
        if len(original_upper) > 0 and roman_char_count / len(original_upper) >= 0.7:
            return True

        return False

    def _ai_review_conversion(self, change: Dict, original_text: str) -> Dict:
        """
        Ask AI to review a specific Roman numeral conversion.

        Args:
            change: Dict with original, replacement, start_pos, end_pos, context
            original_text: The original full text for broader context

        Returns:
            AI decision dict with keep_conversion, suggested_replacement, reasoning, confidence
        """
        original = change["original"]
        replacement = change["replacement"]
        context = change["context"]

        # Get sentence containing this change for better context
        sentence = self._extract_sentence_context(original_text, change["start_pos"])

        prompt = f"""You are reviewing an automatic Roman numeral conversion.

CONTEXT: "{sentence}"
PROPOSED CHANGE: "{original}" → "{replacement}"

DEFAULT: KEEP most conversions unless there's a clear reason not to.

ONLY REVERT if the Roman numeral is clearly:
- Personal initial: "Mrs. C" or "Dr. V" (single letters after titles)
- Geographic abbreviation: "Washington, DC" 
- Brand/product code: "DVD player" or "CD-ROM"

MODIFY if:
- Royal names: "Henry VIII" → "Henry the Eighth"
- Pope names: "Pope John V" → "Pope John the Fifth"  

KEEP (default for):
- All dates/years: "MCMLXXXIV" → "1984", "MMXXV" → "2025"
- All numbers in context: "DCLXVI" → "666", "LXII" → "62" 
- Sequential names: "Jimmy IV" → "Jimmy 4"
- All other legitimate Roman numerals

If unsure, KEEP the conversion - it's better to convert a legitimate Roman numeral than miss it.

RESPOND WITH:
DECISION: [KEEP/REVERT/MODIFY]  
REPLACEMENT: [if MODIFY, provide the better replacement]
REASONING: [brief explanation]
CONFIDENCE: [0.0-1.0]"""

        try:
            response = self.ai_service._make_request(prompt)

            if response.success:
                return self._parse_ai_review_response(response.content)
            else:
                log_message(
                    f"AI review failed for '{original}': {response.error_message}",
                    level="WARNING",
                )
                return {
                    "keep_conversion": True,
                    "confidence": 0.5,
                    "reasoning": "AI review failed, keeping conversion",
                }

        except Exception as e:
            log_message(f"Error in AI review for '{original}': {e}", level="ERROR")
            return {
                "keep_conversion": True,
                "confidence": 0.5,
                "reasoning": "AI review error, keeping conversion",
            }

    def _extract_sentence_context(self, text: str, position: int) -> str:
        """Extract the sentence containing the given position."""
        # For now, just return a larger context window since sentence detection is tricky
        # This gives the AI more context to make better decisions
        context_size = 100
        start = max(0, position - context_size)
        end = min(len(text), position + context_size)

        return text[start:end].strip()

    def _parse_ai_review_response(self, response_text: str) -> Dict:
        """Parse AI review response into structured decision."""
        lines = response_text.strip().split("\n")
        decision_info = {
            "keep_conversion": True,  # Default
            "confidence": 0.5,
            "reasoning": "Could not parse AI response",
        }

        for line in lines:
            line = line.strip()
            if line.startswith("DECISION:"):
                decision = line.split(":", 1)[1].strip().upper()
                if decision == "REVERT":
                    decision_info["keep_conversion"] = False
                elif decision == "KEEP":
                    decision_info["keep_conversion"] = True
                elif decision == "MODIFY":
                    decision_info["keep_conversion"] = True

            elif line.startswith("REPLACEMENT:"):
                replacement = line.split(":", 1)[1].strip()
                if replacement and replacement != "N/A":
                    decision_info["suggested_replacement"] = replacement

            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
                decision_info["reasoning"] = reasoning

            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                    decision_info["confidence"] = confidence
                except ValueError:
                    pass  # Keep default

        return decision_info

    def _apply_ai_reviewed_changes(
        self, original_text: str, reviewed_changes: List[Dict]
    ) -> str:
        """Apply AI-reviewed changes to get final text."""
        final_text = original_text

        # Sort changes by position (rightmost first) to avoid position corruption
        reviewed_changes.sort(key=lambda x: x["change"]["start_pos"], reverse=True)

        for review in reviewed_changes:
            change = review["change"]

            if not review["keep_conversion"]:
                # AI said to revert - keep original Roman numeral
                continue

            # Apply the conversion (either original or AI-suggested replacement)
            start_pos = change["start_pos"]
            end_pos = change["end_pos"]

            if review.get("suggested_replacement"):
                # AI provided a better replacement
                replacement = review["suggested_replacement"]
            else:
                # Keep the original regex conversion
                replacement = change["replacement"]

            final_text = final_text[:start_pos] + replacement + final_text[end_pos:]

        return final_text

    def _track_ai_reviewed_changes(
        self, reviewed_changes: List[Dict], final_text: str
    ) -> None:
        """Track AI-reviewed changes for review window."""
        for review in reviewed_changes:
            if not review["keep_conversion"]:
                continue  # Don't track reverted changes

            change = review["change"]
            original = change["original"]

            if review.get("suggested_replacement"):
                replacement = review["suggested_replacement"]
            else:
                replacement = change["replacement"]

            # Find the replacement in final text
            pos = final_text.find(replacement)
            if pos >= 0:
                self.change_tracker.add_change(
                    module_name="roman",
                    original=original,
                    replacement=replacement,
                    options=["KEEP", "REVERT"],
                    start_pos=pos,
                    end_pos=pos + len(replacement),
                    context_before="",  # Will be calculated by change tracker
                    context_after="",
                    confidence=review["confidence"],
                    reasoning=review["reasoning"],
                )

    def _is_protected_single_letter(
        self, ctx: "BookfixContext", match: re.Match, token: str
    ) -> bool:
        """
        Check if this is a single letter that should be protected from conversion.

        Args:
            ctx: BookfixContext
            match: Regex match object
            token: The roman numeral token

        Returns:
            True if this single letter should be protected
        """
        # Only check single letters
        if len(token) > 1:
            return False

        start_pos = match.start()
        end_pos = match.end()

        # Get extended context for pattern matching
        context_start = max(0, start_pos - 15)
        context_end = min(len(ctx.text), end_pos + 15)
        context = ctx.text[context_start:context_end].upper()

        # Get position within context
        relative_pos = start_pos - context_start

        # Patterns that indicate a single letter should be protected
        protected_patterns = [
            # Personal titles
            r"MRS\.?\s+" + token,
            r"MR\.?\s+" + token,
            r"MS\.?\s+" + token,
            r"DR\.?\s+" + token,
            # Initials in names (C. M. Jones, etc.)
            r"\b" + token + r"\.\s+[A-Z]\.",  # C. M.
            r"\b[A-Z]\.\s+" + token + r"\.",  # A. C.
            r"\b" + token + r"\.\s+[A-Z]+\b",  # C. JONES
            # Geographic abbreviations
            r"WASHINGTON,?\s+D" if token == "C" else None,
            r"WASHINGTON\s+D" + token,
            # Common abbreviations
            r"\bD" + token + r"\b" if token in ["C", "V"] else None,  # DC, DV
            r"\b" + token + r"D\b" if token in ["C", "V"] else None,  # CD, VD
        ]

        # Remove None patterns
        protected_patterns = [p for p in protected_patterns if p is not None]

        # Check if any pattern matches
        for pattern in protected_patterns:
            try:
                if re.search(pattern, context):
                    return True
            except re.error:
                continue  # Skip invalid patterns

        return False

    def _should_consider_conversion(
        self, ctx: "BookfixContext", match: re.Match, token: str
    ) -> bool:
        """
        Apply basic checks to determine if a roman numeral should be considered for conversion.

        Args:
            ctx: BookfixContext
            match: Regex match object
            token: The roman numeral token

        Returns:
            True if the token should be considered for conversion
        """
        start_pos = match.start()
        end_pos = match.end()

        # Additional context checks for edge cases
        before_char = ctx.text[start_pos - 1] if start_pos > 0 else " "
        after_char = ctx.text[end_pos] if end_pos < len(ctx.text) else " "

        # Skip if it's like "X.V" (version number) - check both before and after period
        if (
            after_char == "."
            and end_pos + 1 < len(ctx.text)
            and ctx.text[end_pos + 1] in "VXLCDMI"
        ) or (
            before_char == "."
            and start_pos > 1
            and ctx.text[start_pos - 2] in "VXLCDMI"
        ):
            return False

        # Skip common English words that happen to be Roman numerals
        if token.upper() in ["MIX"]:  # Add other problematic words as needed
            # Only convert if it looks like a chapter/section context
            context_before = ctx.text[max(0, start_pos - 20) : start_pos].lower()
            if not any(
                word in context_before
                for word in ["chapter", "section", "part", "volume", "book"]
            ):
                return False

        return True

    def _extract_context(
        self, text: str, start: int, end: int, context_size: int = 200
    ) -> str:
        """
        Extract context around a match position.

        Args:
            text: Full text
            start: Start position of match
            end: End position of match
            context_size: Total context size to extract

        Returns:
            Context string with the match in the middle
        """
        half_context = context_size // 2
        context_start = max(0, start - half_context)
        context_end = min(len(text), end + half_context)
        return text[context_start:context_end]

    def _analyze_roman_with_ai(
        self, roman: str, arabic: str, context: str
    ) -> Optional[Dict]:
        """
        Analyze whether a roman numeral should be converted using AI.

        Args:
            roman: The roman numeral
            arabic: The arabic equivalent
            context: Context around the roman numeral

        Returns:
            Dictionary with AI decision or None if failed
        """
        try:
            log_message(
                f"Calling AI service for '{roman}' → '{arabic}' in context: {context[:100]}...",
                level="DEBUG",
            )
            response = self.ai_service.analyze_roman_conversion(roman, arabic, context)

            if response.success:
                decision = {
                    "should_convert": response.content.lower()
                    in ["yes", "true", "convert"],
                    "confidence": response.confidence,
                    "reason": getattr(response, "reasoning", ""),
                }
                log_message(f"AI decision for '{roman}': {decision}", level="DEBUG")
                return decision
            else:
                log_message(
                    f"AI analysis failed for '{roman}': {response.error_message}",
                    level="WARNING",
                )
                return None

        except Exception as e:
            log_message(f"Error in AI roman analysis for '{roman}': {e}", level="ERROR")
            return None

    def get_ai_statistics(self) -> Dict:
        """Get statistics about AI Roman processing."""
        total_processed = self.conversions_made + self.abbreviations_preserved

        return {
            "total_processed": total_processed,
            "conversions_made": self.conversions_made,
            "abbreviations_preserved": self.abbreviations_preserved,
            "ai_decisions": len(self.ai_decisions),
        }

    def generate_ai_report(self) -> str:
        """Generate a report of AI Roman processing results."""
        stats = self.get_ai_statistics()

        report = []
        report.append("=== AI Roman Numeral Processing Report ===")
        report.append(f"Total processed: {stats['total_processed']}")
        report.append(f"Converted to numbers: {stats['conversions_made']}")
        report.append(f"Preserved as abbreviations: {stats['abbreviations_preserved']}")
        report.append("")

        if self.ai_decisions:
            report.append("AI Decisions:")
            for decision in self.ai_decisions[:10]:  # Show first 10
                action = (
                    "converted"
                    if decision["decision"]["should_convert"]
                    else "preserved"
                )
                report.append(
                    f"  '{decision['token']}' → {action} "
                    f"(confidence: {decision['decision']['confidence']:.2f})"
                )

            if len(self.ai_decisions) > 10:
                report.append(f"  ... and {len(self.ai_decisions) - 10} more")

        return "\n".join(report)
