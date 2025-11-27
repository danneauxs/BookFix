"""
AI-Enhanced Caps Processor for Bookfix.

Processes ALL CAPS text with AI analysis for intelligent capitalization decisions
with change tracking and review capabilities.
"""

import re
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import BookfixContext

from ..ai.service import BookfixAIService
from ..ai.change_tracker import AIChangeTracker
from ..ai.learning_storage import LearningStorage
from ..ai.learning_analyzer import LearningAnalyzer
from ..logging import log_message


class AICapsProcessor:
    """
    AI-enhanced caps processor that can intelligently fix capitalization
    based on context analysis.
    """

    def __init__(self, change_tracker: Optional[AIChangeTracker] = None):
        self.ai_service: Optional[BookfixAIService] = None
        self.ai_enabled = False
        self.confidence_threshold = 0.8
        self.fallback_to_manual = True

        # Change tracking
        self.change_tracker = change_tracker

        # CAP_IGNORE list from data.txt
        self.cap_ignore_list = set()

        # Track AI decisions for review
        self.ai_decisions = []
        self.lines_processed = 0
        self.lines_modified = 0

        # Learning system
        self.learning_storage = LearningStorage()
        self.learning_analyzer = LearningAnalyzer(self.learning_storage)

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

    def load_cap_ignore_list(self, cap_ignore_list: List[str]):
        """Load CAP_IGNORE list from data.txt."""
        # Debug: Check what type we're getting
        log_message(
            f"DEBUG: cap_ignore_list type: {type(cap_ignore_list)}, value: {cap_ignore_list[:5] if cap_ignore_list else 'empty'}"
        )

        # Ensure it's a list
        if isinstance(cap_ignore_list, list):
            self.cap_ignore_list = set(cap_ignore_list)
        else:
            log_message(
                f"WARNING: Expected list for cap_ignore_list, got {type(cap_ignore_list)}",
                level="WARNING",
            )
            self.cap_ignore_list = set()

        log_message(f"Loaded {len(self.cap_ignore_list)} items in CAP_IGNORE list")

    def process_caps_ai(self, ctx: "BookfixContext") -> "BookfixContext":
        """
        Process ALL CAPS text using AI analysis with context understanding.

        Args:
            ctx: BookfixContext with text and caps to process

        Returns:
            Updated BookfixContext
        """
        if not self.ai_enabled or not self.ai_service:
            log_message("AI not available for caps processing")
            return ctx

        log_message("Starting AI caps processing")
        original_text = ctx.text

        # Find ALL CAPS words
        caps_words = self._find_caps_words(ctx.text)
        if not caps_words:
            log_message("No ALL CAPS words found")
            return ctx

        log_message(f"Found {len(caps_words)} ALL CAPS words to process")

        # Process text with AI
        processed_text = self._process_text_with_ai(ctx.text)

        # Debug: Check if AI made changes
        if processed_text != original_text:
            log_message(
                f"AI made changes to text (original: {len(original_text)} chars, processed: {len(processed_text)} chars)"
            )
            # Show a sample of changes
            if len(original_text) > 100:
                orig_sample = original_text[:100] + "..."
                proc_sample = processed_text[:100] + "..."
                log_message(f"Sample - Original: '{orig_sample}'")
                log_message(f"Sample - Processed: '{proc_sample}'")
        else:
            log_message("AI returned identical text - no changes made")

        # Update context text
        ctx.text = processed_text

        # Track changes for review
        if self.change_tracker:
            self._track_caps_changes(original_text, processed_text, caps_words)

        log_message(f"AI caps processing complete")
        return ctx

    def _find_caps_words(
        self, text: str
    ) -> List[Tuple[int, str, List[Tuple[int, int]]]]:
        """Find ALL CAPS words for processing."""
        lines = text.splitlines()
        caps_lines = []

        # Pattern to find ALL CAPS words (2+ letters, not single letters, including contractions like MUSTN'T)
        caps_pattern = re.compile(r"\b[A-Z]{2,}(?:\'[A-Z]+)?\b")

        for idx, line in enumerate(lines):
            spans = []
            for match in caps_pattern.finditer(line):
                caps_word = match.group()
                # Skip if in ignore list
                if caps_word not in self.cap_ignore_list:
                    spans.append(match.span())

            if spans:
                caps_lines.append((idx, line, spans))

        return caps_lines

    def _process_text_with_ai(self, text: str) -> str:
        """Process entire text with AI for capitalization fixes using learned preferences."""

        # Generate learning-enhanced prompt
        prompt = self._generate_learning_enhanced_prompt(text)

        try:
            # Use the AI service to process the text
            result = self.ai_service._make_request(prompt)
            if result.success and result.content:
                processed_text = result.content.strip()
                log_message(f"AI caps processing successful")
                return processed_text
            else:
                log_message(
                    f"AI caps processing failed: {result.error_message}",
                    level="WARNING",
                )
                return text

        except Exception as e:
            log_message(f"AI caps processing error: {e}", level="ERROR")
            return text

    def _generate_learning_enhanced_prompt(self, text: str) -> str:
        """Generate AI prompt enhanced with learned user preferences."""

        # Get learned preferences
        learned_examples = self._get_learned_examples()
        learned_patterns = self._get_learned_patterns()

        # Base prompt
        prompt = f"""You are a text processing specialist tasked with fixing capitalization in text that has inconsistent ALL CAPS usage. Your job is to convert improperly capitalized text to natural, readable format suitable for text-to-speech.

STANDARD RULES:
1. PROPER NAMES & TITLES: Keep proper capitalization (Commander Thorne, Dr. Aris, General Sterling)
2. ORGANIZATIONS & ACRONYMS: Keep as-is (NASA, FBI, CIA, Galactic Federation)  
3. PLACE NAMES: Use proper case (Earth, Mars, Orion Nebula, Vallis Marineris)
4. DIALOGUE & SPEECH: Convert to sentence case, even if originally shouted
5. COMPUTER DISPLAYS/SIGNS/LISTS: Convert to lowercase (like directory listings)
6. OPERATIONAL CODES: Use sentence case (Operation Nightfall, Code Red)
7. TECHNICAL TERMS: Use sentence case unless proper noun (gravitational forces, Life Support)

IGNORE LIST (keep as-is): {', '.join(self.cap_ignore_list) if self.cap_ignore_list else 'None'}"""

        # Add learned preferences if available
        if learned_examples:
            prompt += f"""

LEARNED USER PREFERENCES (follow these patterns):
{learned_examples}"""

        if learned_patterns:
            prompt += f"""

LEARNED CONTEXT PATTERNS:
{learned_patterns}"""

        prompt += f"""

STANDARD EXAMPLES:
- "THE ANCIENT SCROLL" → "The ancient scroll"
- "HALT! YOU DARE TRESPASS!" → "Halt! You dare trespass!"
- "Commander Thorne" → "Commander Thorne" (keep as-is)
- "GENERAL STERLING" → "General Sterling"  
- "NASA" → "NASA" (keep as-is)
- "EMERGENCY SUPPLIES" (sign/list) → "emergency supplies"
- "WE NEED MORE DATA!" (dialogue) → "We need more data!"

INPUT TEXT:
{text}

OUTPUT INSTRUCTIONS:
- Respond with ONLY the corrected text
- Maintain all original formatting, spacing, and punctuation
- Do not add explanations or comments
- Follow learned user preferences when applicable
- Process the entire text maintaining story flow and context

CORRECTED TEXT:"""

        return prompt

    def _get_learned_examples(self) -> str:
        """Get examples based on learned user decisions."""
        examples = []

        # Get high-confidence word patterns
        for pattern in self.learning_storage.patterns:
            if pattern.pattern_type == "word_exact" and pattern.confidence > 0.8:
                word = pattern.pattern_value
                action = pattern.preferred_action

                if action == "lower":
                    examples.append(
                        f'- "{word}" → "{word.lower()}" (user prefers lowercase)'
                    )
                elif action == "skip":
                    examples.append(
                        f'- "{word}" → "{word}" (user prefers to keep as-is)'
                    )
                elif action in ["ignore_all", "add"]:
                    examples.append(
                        f'- "{word}" → "{word}" (user always keeps this word uppercase)'
                    )

        return "\n".join(examples[:10])  # Limit to top 10 examples

    def _get_learned_patterns(self) -> str:
        """Get context patterns based on learned user decisions."""
        patterns = []

        # Get high-confidence context patterns
        for pattern in self.learning_storage.patterns:
            if pattern.pattern_type == "context_pattern" and pattern.confidence > 0.7:
                context = pattern.pattern_value
                action = pattern.preferred_action

                if context.startswith("after_"):
                    preceding_word = context[6:]
                    if action == "lower":
                        patterns.append(
                            f'- Words after "{preceding_word}" → usually lowercase'
                        )
                    elif action == "skip":
                        patterns.append(
                            f'- Words after "{preceding_word}" → usually keep as-is'
                        )
                elif context == "sentence_start":
                    if action == "lower":
                        patterns.append(f"- Sentence-starting caps → usually lowercase")
                    elif action == "skip":
                        patterns.append(
                            f"- Sentence-starting caps → usually keep as-is"
                        )

        return "\n".join(patterns[:5])  # Limit to top 5 patterns

    def _track_caps_changes(
        self, original_text: str, processed_text: str, caps_words: List
    ):
        """Track changes made by AI for review."""
        if not self.change_tracker:
            return

        # Find all caps words in both texts and track changes
        original_lines = original_text.splitlines()
        processed_lines = processed_text.splitlines()

        # Calculate absolute positions
        original_line_positions = [0]
        for line in original_lines:
            original_line_positions.append(original_line_positions[-1] + len(line) + 1)

        processed_line_positions = [0]
        for line in processed_lines:
            processed_line_positions.append(
                processed_line_positions[-1] + len(line) + 1
            )

        # Track changes for each caps word found (including contractions like MUSTN'T)
        caps_pattern = re.compile(r"\b[A-Z]{2,}(?:\'[A-Z]+)?\b")

        for line_no, line_content, spans in caps_words:
            if line_no < len(processed_lines):
                processed_line = processed_lines[line_no]
                line_start_pos = processed_line_positions[line_no]

                for start, end in spans:
                    original_word = line_content[start:end]

                    # Find what this word became in the processed line
                    # This is approximate - the AI might have changed word boundaries
                    if start < len(processed_line) and end <= len(processed_line):
                        processed_word = processed_line[start:end]
                    else:
                        processed_word = original_word  # Fallback

                    # Track the change
                    self.change_tracker.add_change(
                        module_name="allcaps",
                        original=original_word,
                        replacement=processed_word,
                        start_pos=line_start_pos + start,
                        end_pos=line_start_pos + end,
                        context_before=line_content[max(0, start - 30) : start],
                        context_after=line_content[end : end + 30],
                        confidence=0.8,  # Default confidence for AI processing
                        reasoning=f'AI caps processing of "{original_word}" to "{processed_word}"',
                    )
