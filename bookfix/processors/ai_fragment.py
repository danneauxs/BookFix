"""AI-powered line fragment rejoining processor."""

import re
from typing import List, Dict
from ..ai.service import AIService
from ..context import Context
from ..loggers.processor_logger import ProcessorLogger


class AIFragmentProcessor:
    """
    Detects and rejoins broken line fragments using AI.

    Fixes issues like:
    - Broken hyphenation: "re-\nactor" → "reactor"
    - Split sentences: "Frank\nchuckled\nagain" → "Frank chuckled again"
    - OCR artifacts with improper line breaks
    """

    def __init__(self, ai_service: AIService):
        """
        Initialize the fragment processor.

        Args:
            ai_service: AI service for analyzing and rejoining fragments
        """
        self.ai_service = ai_service

    def process_fragments(self, ctx: Context) -> Context:
        """
        Detect and rejoin line fragments in text.

        Args:
            ctx: Processing context with text to fix

        Returns:
            Updated context with fragments rejoined
        """
        # Initialize logger
        logger = ProcessorLogger(ctx.current_file_path, "fragment")
        logger.log_info("Starting line fragment detection and rejoining")

        # Find potential fragment blocks
        fragment_blocks = self._find_fragment_blocks(ctx.text)

        if not fragment_blocks:
            logger.log_info("No fragment blocks found")
            return ctx

        logger.log_info(
            f"Found {len(fragment_blocks)} potential fragment blocks to analyze"
        )

        # Process each block with AI
        changes_made = 0

        for block in fragment_blocks:
            original_text = block["text"]

            # Ask AI to rejoin fragments
            response = self.ai_service.analyze_line_fragment(original_text)

            if response.success and response.suggestion != original_text:
                # Replace in text
                ctx.text = ctx.text.replace(original_text, response.suggestion, 1)

                # Log the change
                logger.log_change(
                    original_text.replace("\n", "\\n"),
                    response.suggestion.replace("\n", "\\n"),
                    None,
                    response.reasoning,
                )

                changes_made += 1

        # Log summary
        logger.log_summary(
            {
                "blocks_analyzed": len(fragment_blocks),
                "fragments_rejoined": changes_made,
            }
        )

        return ctx

    def _find_fragment_blocks(self, text: str) -> List[Dict[str, any]]:
        """
        Find blocks of text that might contain line fragments.

        Args:
            text: Text to scan

        Returns:
            List of dicts with 'text', 'position' for each suspicious block
        """
        blocks = []

        # Pattern 1: Word ending with hyphen followed by newline and word
        # e.g., "re-\nactor"
        hyphen_pattern = r"\b\w+-\n\w+\b"

        for match in re.finditer(hyphen_pattern, text):
            # Get surrounding context (previous and next sentence)
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)

            blocks.append(
                {"text": text[start:end], "position": match.start(), "type": "hyphen"}
            )

        # Pattern 2: Short lines (< 40 chars) followed by another short line
        # These might be sentence fragments
        # e.g., "Frank\nchuckled\nagain"
        lines = text.split("\n")
        i = 0

        while i < len(lines) - 2:
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip()
            line3 = lines[i + 2].strip()

            # Check if we have 3 short lines that might be fragments
            if (
                len(line1) < 40
                and len(line2) < 40
                and len(line3) < 40
                and line1
                and line2
                and line3
                and not line1.endswith(".")
                and not line1.endswith("!")
                and not line1.endswith("?")
            ):

                # This might be a fragment - include context
                # Get up to 5 lines before and after
                start_idx = max(0, i - 2)
                end_idx = min(len(lines), i + 5)

                block_text = "\n".join(lines[start_idx:end_idx])

                # Calculate position in original text
                position = sum(len(line) + 1 for line in lines[:i])

                blocks.append(
                    {"text": block_text, "position": position, "type": "short_lines"}
                )

                i += 3  # Skip ahead
            else:
                i += 1

        # Deduplicate blocks (some might overlap)
        unique_blocks = []
        seen_positions = set()

        for block in blocks:
            if block["position"] not in seen_positions:
                unique_blocks.append(block)
                seen_positions.add(block["position"])

        return unique_blocks
