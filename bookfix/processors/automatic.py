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

    for old, new in ctx.replacements.items():
        try:
            # Check if pattern contains regex metacharacters that should be preserved
            # Patterns like \b, \d, \w, \s are treated as regex, not literal
            if re.search(r'\[bBdDsSwWAZ]', old):
                # User wants regex - use pattern as-is (do not escape)
                try:
                    pattern = re.compile(old, re.IGNORECASE)
                except re.error as e:
                    log_message(f"Invalid regex pattern '{old}': {e}", level="WARNING")
                    continue  # Skip this invalid pattern
            else:
                # Literal replacement - escape special regex chars like . * + ? etc.
                # This prevents periods, asterisks, etc. from acting as wildcards
                pattern = re.compile(re.escape(old), re.IGNORECASE)

            # Define case-preserving replacement function
            def preserve_case(match):
                """Preserve the case pattern of the matched text in the replacement."""
                matched_text = match.group(0)

                # If empty match, return replacement as-is
                if not matched_text:
                    return new

                # Check case pattern of matched text
                if matched_text.isupper():  # ALL CAPS (e.g., "HER BREATH")
                    return new.upper()
                elif matched_text[0].isupper():  # Title Case (e.g., "Her breath")
                    # Capitalize first letter of replacement, keep rest as-is
                    return new[0].upper() + new[1:] if len(new) > 1 else new.upper()
                else:  # lowercase (e.g., "her breath")
                    return new

            # Find matches before replacement (for counting)
            matches = list(pattern.finditer(ctx.text))

            # Apply replacement with case preservation
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
