"""AI-powered page number detection and removal processor."""

import re
from typing import List, Dict, Set
from ..ai.service import AIService
from ..context import Context
from ..loggers.processor_logger import ProcessorLogger


class AIPageProcessor:
    """
    Detects and removes page numbers using AI pattern analysis.

    Identifies sequential numbers that appear to be page numbers (e.g., 42, 46, 47)
    and removes them from the text.
    """

    def __init__(self, ai_service: AIService):
        """
        Initialize the page number processor.

        Args:
            ai_service: AI service for analyzing potential page numbers
        """
        self.ai_service = ai_service

    def process_page_numbers(self, ctx: Context) -> Context:
        """
        Detect and remove page numbers from text.

        Args:
            ctx: Processing context with text to clean

        Returns:
            Updated context with page numbers removed
        """
        # Initialize logger
        logger = ProcessorLogger(ctx.current_file_path, "page")
        logger.log_info("Starting page number detection and removal")

        # Find all standalone numbers with context
        number_candidates = self._find_number_candidates(ctx.text)

        if not number_candidates:
            logger.log_info("No number candidates found")
            return ctx

        logger.log_info(f"Found {len(number_candidates)} number candidates to analyze")

        # Analyze with AI to identify page numbers
        page_numbers = self._identify_page_numbers(number_candidates, logger)

        if not page_numbers:
            logger.log_info("No page numbers identified by AI")
            return ctx

        logger.log_info(f"Identified {len(page_numbers)} page numbers for removal")

        # Remove identified page numbers
        ctx.text = self._remove_page_numbers(ctx.text, page_numbers, logger)

        # Log summary
        logger.log_summary(
            {
                "candidates_analyzed": len(number_candidates),
                "page_numbers_removed": len(page_numbers),
            }
        )

        return ctx

    def _find_number_candidates(self, text: str) -> List[Dict[str, any]]:
        """
        Find all standalone numbers that could be page numbers.

        Args:
            text: Text to scan

        Returns:
            List of dicts with 'number', 'position', 'context_before', 'context_after'
        """
        candidates = []

        # Pattern: standalone numbers (not part of dates, times, or other contexts)
        # Look for numbers on their own line or with minimal surrounding text
        pattern = r"(?:^|\n)\s*(\d{1,4})\s*(?:\n|$)"

        for match in re.finditer(pattern, text):
            number = match.group(1)
            position = match.start()

            # Get context (100 chars before and after)
            context_start = max(0, position - 100)
            context_end = min(len(text), position + len(number) + 100)

            context_before = text[context_start:position]
            context_after = text[position + len(number) : context_end]

            candidates.append(
                {
                    "number": number,
                    "position": position,
                    "context_before": context_before,
                    "context_after": context_after,
                    "full_match": match.group(0),
                }
            )

        return candidates

    def _identify_page_numbers(
        self, candidates: List[Dict[str, any]], logger: ProcessorLogger
    ) -> Set[str]:
        """
        Use AI to identify which candidates are actual page numbers.

        Args:
            candidates: List of number candidates
            logger: Logger for tracking decisions

        Returns:
            Set of position indices that are page numbers
        """
        page_numbers = set()

        # Group candidates by proximity to check for sequential patterns
        sequences = self._find_sequential_patterns(candidates)

        # If we find sequential patterns, those are likely page numbers
        if sequences:
            for seq in sequences:
                logger.log_info(
                    f"Found sequential pattern: {', '.join(seq['numbers'])}"
                )
                for candidate in seq["candidates"]:
                    page_numbers.add(candidate["position"])

        # For remaining isolated numbers, ask AI
        isolated = [c for c in candidates if c["position"] not in page_numbers]

        for candidate in isolated:
            # Build context for AI
            context = (
                f"{candidate['context_before']}"
                f"[{candidate['number']}]"
                f"{candidate['context_after']}"
            )

            # Ask AI if this looks like a page number
            response = self.ai_service.analyze_page_number(candidate["number"], context)

            if response.success and response.suggestion:
                if response.suggestion.lower() == "page_number":
                    page_numbers.add(candidate["position"])
                    logger.log_info(
                        f"AI identified '{candidate['number']}' as page number "
                        f"(confidence: {response.confidence})"
                    )
                else:
                    logger.log_skip(
                        candidate["number"],
                        f"AI identified as {response.suggestion}, not page number",
                    )

        return page_numbers

    def _find_sequential_patterns(
        self, candidates: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Find sequences of increasing numbers that likely represent page numbers.

        Args:
            candidates: List of number candidates

        Returns:
            List of sequences, each with 'numbers' and 'candidates'
        """
        sequences = []

        # Sort by position in text
        sorted_candidates = sorted(candidates, key=lambda c: c["position"])

        # Look for sequences of 3+ increasing numbers
        current_seq = []

        for i, candidate in enumerate(sorted_candidates):
            num = int(candidate["number"])

            if not current_seq:
                current_seq.append(candidate)
            else:
                prev_num = int(current_seq[-1]["number"])

                # Check if this continues the sequence (within reasonable gap)
                if 0 < num - prev_num <= 10:
                    current_seq.append(candidate)
                else:
                    # Sequence broken - save if 3+ numbers
                    if len(current_seq) >= 3:
                        sequences.append(
                            {
                                "numbers": [c["number"] for c in current_seq],
                                "candidates": current_seq[:],
                            }
                        )
                    current_seq = [candidate]

        # Check final sequence
        if len(current_seq) >= 3:
            sequences.append(
                {
                    "numbers": [c["number"] for c in current_seq],
                    "candidates": current_seq[:],
                }
            )

        return sequences

    def _remove_page_numbers(
        self, text: str, page_number_positions: Set[str], logger: ProcessorLogger
    ) -> str:
        """
        Remove identified page numbers from text.

        Args:
            text: Original text
            page_number_positions: Set of positions to remove
            logger: Logger for tracking removals

        Returns:
            Text with page numbers removed
        """
        # Sort positions in reverse order to remove from end to start
        positions = sorted(page_number_positions, reverse=True)

        for pos in positions:
            # Find the number at this position
            # Look for number pattern starting at or near this position
            match = re.search(r"(?:^|\n)\s*(\d{1,4})\s*(?:\n|$)", text[pos : pos + 20])

            if match:
                number = match.group(1)

                # Get context for logging
                context_start = max(0, pos - 50)
                context_end = min(len(text), pos + 70)
                context = text[context_start:context_end]

                # Remove the number and surrounding whitespace
                text = text[:pos] + text[pos + len(match.group(0)) :]

                logger.log_removal(number, context, "Identified as page number")

        return text
