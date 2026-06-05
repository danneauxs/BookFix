"""
Lowercase conversion processors for Bookfix.

This module provides functionality to convert text to lowercase and apply
uppercase-to-lowercase mappings.
"""

import re
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import BookfixContext


def convert_to_lowercase(ctx: "BookfixContext") -> "BookfixContext":
    """
    Converts the entire text to lowercase.

    Args:
        ctx: BookfixContext object containing text

    Returns:
        Updated BookfixContext with text converted to lowercase
    """
    # Import here to avoid circular imports
    from ..logging import log_message

    log_message("Starting converting to lowercase.")
    original_text = ctx.text
    ctx.text = ctx.text.lower()

    ctx.log_change(
        "convert_lowercase",
        "Converted entire text to lowercase",
        len(original_text),
        len(ctx.text),
    )

    log_message("Finished converting to lowercase.")
    return ctx


def apply_upper_to_lower(
    ctx: "BookfixContext", upper_to_lower: Dict[str, str]
) -> "BookfixContext":
    """
    Apply uppercase to title case mappings to the text.

    Args:
        ctx: BookfixContext object containing text
        upper_to_lower: Dictionary mapping UPPER → lower words (values ignored, title case applied)

    Returns:
        Updated BookfixContext with uppercase words converted to title case

    Note:
        All words in UPPER_TO_LOWER list are converted to title case for pronounceable acronyms.
        Examples:
        - NASA → Nasa
        - SCUBA → Scuba
        - LASER → Laser

        This applies to EVERY standalone occurrence of UPPER words,
        even when they're part of a longer all-caps phrase.
    """
    # Import here to avoid circular imports
    from ..logging import log_message

    original_text = ctx.text
    replacements_made = 0

    for up, low in upper_to_lower.items():
        # Convert to title case (ignore the 'low' value from dict)
        title_case = up.title()

        # Count occurrences before replacement
        pattern = re.compile(rf"\b{re.escape(up)}\b")
        matches = pattern.findall(ctx.text)
        replacements_made += len(matches)
        # \b ensures we replace whole words only
        ctx.text = pattern.sub(title_case, ctx.text)

    ctx.log_change(
        "apply_upper_to_lower",
        f"Applied {len(upper_to_lower)} title case rules, made {replacements_made} replacements",
        len(original_text),
        len(ctx.text),
    )

    return ctx
