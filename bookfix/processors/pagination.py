"""
Pagination removal and line-reflow processor for Bookfix.

Rules for plain-text (.txt) files:
1. Remove page numbers that are alone on a line, and join the text
   before and after into one continuous sentence.
2. Remove page numbers that appear at the end of a line, and join that
   line with the next real text line.
3. Reflow broken lines where a single logical sentence has been split
   across many physical lines (e.g. one word per line), while keeping
   blank-line paragraph breaks.

HTML/XHTML files still use BeautifulSoup to strip common pagination
nodes.
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import BookfixContext

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


# ---------------------------------------------------------------------------
# Core helpers operating on raw text
# ---------------------------------------------------------------------------


def _remove_digit_only_lines_and_join(text: str, pagination_log: list[str]) -> str:
    """Remove lines that are just digits and join surrounding text.

    Example:
        some text before
        119

        more text after

    becomes:
        "some text before more text after"
    """
    lines = text.splitlines()
    filtered: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Line is just digits → treat as page number
        if line.strip().isdigit():
            pagination_log.append(f"Removed digit-only line: {line}")

            # Find next non-blank line after the page number block
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            # If we have text before and after, always join with a space
            if filtered and j < len(lines):
                filtered[-1] = filtered[-1].rstrip() + " " + lines[j].lstrip()
                j += 1

            # Skip over the page number and any blank lines (and the joined line)
            i = j
            continue

        # Normal content line
        filtered.append(line)
        i += 1

    return "\n".join(filtered)


def _remove_inline_page_numbers_and_join(text: str, pagination_log: list[str]) -> str:
    """Remove page numbers at line ends and join with the following line.

    Handles patterns like:
        "...making him 119" + blank lines + "sweaty and uncomfortable".

    After processing, this becomes:
        "...making him sweaty and uncomfortable".
    """

    lines = text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        if not stripped or stripped.isdigit():
            i += 1
            continue

        # Skip common headings like "Chapter 1" so we don't strip real structure
        heading_pattern = r"^\s*(Chapter|Section|Part|Book|Volume|Act|Scene)\s+\d+\s*$"
        if re.match(heading_pattern, stripped, re.IGNORECASE):
            i += 1
            continue

        # Bracketed page number at end: ... [117] or ... [1 1 7]
        bracket_match = re.search(r"\s*\[[\d\s]+\]\s*$", stripped)
        if bracket_match:
            page_number = bracket_match.group().strip()
            line_without_number = stripped[: bracket_match.start()].rstrip()
            pagination_log.append(
                f"Removed bracketed page number: {page_number} from line ending with: ...{line_without_number[-30:]}"
            )

            # Replace current line without the number
            lines[i] = line_without_number

            # Find next non-blank line and always join
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            if j < len(lines) and line_without_number:
                lines[i] = lines[i] + " " + lines[j].lstrip()
                del lines[i + 1 : j + 1]
            else:
                i += 1

            continue

        # Plain inline page number at end: ... 119
        match = re.search(r"\s+\d+$", stripped)
        if match:
            page_number = match.group().strip()
            line_without_number = stripped[: match.start()].rstrip()
            pagination_log.append(
                f"Removed inline page number: {page_number} from line ending with: ...{line_without_number[-30:]}"
            )

            lines[i] = line_without_number

            # Find next non-blank line and always join
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            if j < len(lines) and line_without_number:
                lines[i] = lines[i] + " " + lines[j].lstrip()
                del lines[i + 1 : j + 1]
            else:
                i += 1

            continue

        i += 1

    return "\n".join(lines)


def _reflow_broken_lines(text: str) -> str:
    """Reflow sentences that were split across many lines.

    - Blank lines stay as paragraph breaks.
    - Inside a paragraph, newlines become spaces and extra spaces are collapsed.
    - If a paragraph chunk does not end in sentence-ending punctuation, it
      is joined with the next chunk.
    """

    # Normalize newlines first
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split on blank lines
    chunks = re.split(r"\n\s*\n", text)
    fixed_paragraphs: list[str] = []
    current: str | None = None

    sentence_enders = (".", "!", "?", '"', "'", "\u201d", "\u2019")

    for raw_chunk in chunks:
        chunk = raw_chunk.strip()
        if not chunk:
            continue

        # Remove internal single newlines inside the chunk
        chunk = chunk.replace("\n", " ")
        chunk = re.sub(r" +", " ", chunk)

        if current is None:
            current = chunk
            continue

        last_char = current[-1]
        if last_char in sentence_enders:
            fixed_paragraphs.append(current)
            current = chunk
        else:
            current = current + " " + chunk

    if current:
        fixed_paragraphs.append(current)

    return "\n\n".join(fixed_paragraphs)


class PaginationProcessor:
    """Processor for removing pagination elements and fixing broken lines."""

    def process_pagination(self, ctx: "BookfixContext") -> "BookfixContext":
        """Main entry: update ctx.text in-place and return ctx."""
        return remove_pagination(ctx)


def remove_pagination(ctx: "BookfixContext") -> "BookfixContext":
    """Apply HTML or TXT pagination removal and line reflow to ctx.text."""
    from ..logging import log_message

    log_message("Starting removing pagination.")
    original_text = ctx.text
    pagination_log: list[str] = []

    try:
        # Check if the file is HTML or XHTML
        if ctx.filepath and ctx.filepath.lower().endswith((".xhtml", ".html")):
            if BeautifulSoup is None:
                log_message(
                    "BeautifulSoup not available, skipping HTML pagination removal",
                    level="WARNING",
                )
                return ctx

            soup = BeautifulSoup(ctx.text, "xml")

            # Find elements commonly used for pagination based on class or ID
            page_number_elements = soup.find_all(
                class_=re.compile(r"page-number", re.IGNORECASE)
            )
            page_number_elements.extend(
                soup.find_all(id=re.compile(r"page-number", re.IGNORECASE))
            )
            # Find <p> tags containing only digits (common for simple page numbers)
            page_number_elements.extend(
                soup.find_all(
                    name=re.compile(r"p", re.IGNORECASE),
                    string=re.compile(r"^\s*\d+\s*$", re.IGNORECASE),
                )
            )

            # Iterate through found elements
            for element in page_number_elements:
                pagination_log.append(f"Removed: {element}")
                element.decompose()

            ctx.text = str(soup)

            # Remove any completely empty lines
            lines = ctx.text.splitlines()
            filtered_lines = [line for line in lines if line.strip()]
            ctx.text = "\n".join(filtered_lines)

        # Check if the file is a plain text file
        elif ctx.filepath and ctx.filepath.lower().endswith(".txt"):
            text = ctx.text
            text = _remove_digit_only_lines_and_join(text, pagination_log)
            text = _remove_inline_page_numbers_and_join(text, pagination_log)
            text = _reflow_broken_lines(text)
            ctx.text = text

    except Exception as e:  # pragma: no cover - defensive logging
        log_message(f"Error removing pagination: {e}", level="ERROR")

    # Save the log of removed pagination to a file
    try:
        with open("pagination_debug.txt", "w", encoding="utf-8") as log_file:
            log_file.write("\n".join(pagination_log))
        log_message("Pagination removal log saved to pagination_debug.txt.")
    except Exception as e:  # pragma: no cover - defensive logging
        log_message(f"Error saving pagination debug log: {e}", level="ERROR")

    ctx.log_change(
        "remove_pagination",
        f"Removed {len(pagination_log)} pagination elements",
        len(original_text),
        len(ctx.text),
    )

    log_message("Finished removing pagination.")
    return ctx
