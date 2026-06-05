"""
Period removal processor for Bookfix.

This module provides functionality to remove periods from abbreviations
(e.g., 'S.C.E.' -> 'SCE') for better TTS pronunciation.
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import BookfixContext


class PeriodProcessor:
    """Processor for removing periods from abbreviations."""

    def process_periods(self, ctx: "BookfixContext") -> "BookfixContext":
        """Process periods using the function."""
        return remove_periods_from_abbreviations(ctx)


def remove_periods_from_abbreviations(ctx: "BookfixContext") -> "BookfixContext":
    """
    Removes periods from abbreviations like 'S.C.E.' to 'SCE'.

    This uses a regular expression to find acronyms of two or more
    capital letters separated by periods and removes the periods between them,
    while preserving sentence-ending periods.

    Args:
        ctx: BookfixContext object containing text to process

    Returns:
        Updated BookfixContext with periods removed from abbreviations
    """
    from ..logging import log_message

    log_message("Starting removing periods from abbreviations.")
    original_text = ctx.text

    # This pattern finds sequences of 2 or more capital letters separated by periods.
    # It captures the full sequence (e.g., "S.C.E") without the final period,
    # which allows preserving sentence-ending punctuation.
    pattern = r"\b([A-Z](?:\.[A-Z])+)\b"

    def replacement_func(match):
        """Replaces periods in abbreviations matched by a regular expression pattern in the given context.
        Args:
        match (Match object): The match object containing the matched abbreviation.
        Returns:
        str: The abbreviation with periods removed.
        """
        # Get the matched string (e.g., "S.C.E")
        abbreviation = match.group(1)
        # Remove the periods from it
        return abbreviation.replace(".", "")

    # Use re.sub with the replacement function
    new_text, replacements_made = re.subn(pattern, replacement_func, ctx.text)

    ctx.text = new_text

    if replacements_made > 0:
        ctx.log_change(
            "remove_periods",
            f"Removed periods from {replacements_made} abbreviations.",
            len(original_text),
            len(ctx.text),
        )

    log_message(f"Finished removing periods. Made {replacements_made} replacements.")
    return ctx
