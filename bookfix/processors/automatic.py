"""
Automatic text replacement processor for Bookfix.

This module provides functionality to apply automatic find-and-replace rules
loaded from the data file using regex patterns.
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import BookfixContext


def apply_automatic_replacements(ctx: "BookfixContext") -> "BookfixContext":
    """
    Applies all find and replace rules loaded from the data file using regex.

    Args:
        ctx: BookfixContext object containing text and replacement rules

    Returns:
        Updated BookfixContext with replacements applied
    """
    # Import here to avoid circular imports
    from ..logging import log_message

    log_message("Starting automatic replacements.")
    original_text = ctx.text
    replacement_count = 0

    # Normalize problematic whitespace (prevents invisible mismatch bugs)
    ctx.text = ctx.text.replace('\u00A0', ' ')

    for old, new in ctx.replacements.items():
        try:
            # --- NEW: explicit rule handling ---
            if old.startswith("regex:"):
                pattern_str = old[6:]
                try:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                except re.error as e:
                    log_message(f"Invalid regex pattern '{pattern_str}': {e}", level="WARNING")
                    continue

            elif old.startswith("literal:"):
                pattern_str = old[8:]
                escaped = re.escape(pattern_str)
                # Keep literal rules from matching inside longer words while allowing punctuation rules.
                prefix_boundary = r"(?<!\w)" if pattern_str and pattern_str[0].isalnum() else ""
                suffix_boundary = r"(?!\w)" if pattern_str and pattern_str[-1].isalnum() else ""
                pattern = re.compile(
                    prefix_boundary + escaped + suffix_boundary,
                    re.IGNORECASE,
                )

            else:
                # Default to literal if no prefix is provided
                escaped = re.escape(old)
                # Preserve legacy unprefixed rules but prevent partial final-word matches.
                suffix_boundary = r"(?!\w)" if old and old[-1].isalnum() else ""
                pattern = re.compile(escaped + suffix_boundary, re.IGNORECASE)

            # Define case-preserving replacement function
            def preserve_case(match):
                """Preserve the case pattern of the matched text in the replacement."""
                matched_text = match.group(0)

                if not matched_text:
                    return new

                if matched_text.isupper():
                    return new.upper()
                elif matched_text[0].isupper():
                    return new[0].upper() + new[1:] if len(new) > 1 else new.upper()
                else:
                    return new

            # Count matches before replacement
            matches = list(pattern.finditer(ctx.text))

            # Apply replacement
            ctx.text = pattern.sub(preserve_case, ctx.text)

            replacement_count += len(matches)

        except re.error as e:
            log_message(f"Regex error in pattern '{old}': {e}", level="ERROR")

    ctx.log_change(
        "automatic_replacements",
        f"Applied {len(ctx.replacements)} rules, made {replacement_count} replacements",
        len(original_text),
        len(ctx.text),
    )

    log_message("Finished automatic replacements.")
    return ctx


class AutomaticReplacementProcessor:
    """Processor for applying automatic text replacements."""

    def process_replacements(self, ctx: "BookfixContext") -> "BookfixContext":
        """Process automatic replacements using the function."""
        return apply_automatic_replacements(ctx)
