"""
Data file loading and parsing for Bookfix.

This module handles loading and parsing the .data.txt configuration file
which contains replacement rules, choice options, and other settings.
"""

import os
import re
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import BookfixContext

from .logging import log_message


def load_data_file(ctx: "BookfixContext" = None) -> "BookfixContext":
    """
    Load and parse configuration files.

    Checks for data/ directory with split files first, falls back to .data.txt

    Args:
        ctx: Existing BookfixContext to populate, or None to create new one

    Returns:
        BookfixContext with loaded configuration
    """
    from .context import BookfixContext

    if ctx is None:
        ctx = BookfixContext()

    # Check for data/ directory (new split file structure)
    data_dir = os.path.join(os.getcwd(), "data")

    if os.path.exists(data_dir) and os.path.isdir(data_dir):
        log_message(f"Loading configuration from data/ directory: {data_dir}")
        try:
            _load_from_data_directory(data_dir, ctx)
            return ctx
        except Exception as e:
            log_message(f"Error loading from data/ directory: {e}", level="ERROR")
            log_message("Falling back to .data.txt", level="WARNING")

    # Fall back to .data.txt file (legacy monolithic file)
    data_file_path = os.path.join(os.getcwd(), ".data.txt")

    if not os.path.exists(data_file_path):
        log_message(f"Data file not found: {data_file_path}", level="WARNING")
        return ctx

    log_message(f"Attempting to load data file: {data_file_path}")

    try:
        with open(data_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        _parse_data_file_lines(lines, ctx)

    except Exception as e:
        log_message(f"Error loading data file: {e}", level="ERROR")

    return ctx


def _load_from_data_directory(data_dir: str, ctx: "BookfixContext") -> None:
    """Load configuration from split data/ directory files."""
    from pathlib import Path

    data_path = Path(data_dir)

    # Initialize context dictionaries
    ctx.choices = {}
    ctx.tagged_choices = {}
    ctx.replacements = {}
    ctx.periods = {}
    ctx.upper_to_lower = []
    ctx.cap_ignore = []
    ctx.roman_ignore = []
    ctx.skip_choice = []
    ctx.ai_config = {}

    # Load each section from its own file
    _load_settings_file(data_path / "settings.txt", ctx)
    _load_replace_file(data_path / "replace.txt", ctx)
    _load_choice_file(data_path / "choice.txt", ctx)
    _load_skip_choice_file(data_path / "skip_choice.txt", ctx)
    _load_simple_list_file(data_path / "upper_to_lower.txt", ctx.upper_to_lower)
    _load_simple_list_file(data_path / "cap_ignore.txt", ctx.cap_ignore)
    _load_simple_list_file(data_path / "roman_ignore.txt", ctx.roman_ignore)


def _load_settings_file(file_path, ctx: "BookfixContext") -> None:
    """Load settings from settings.txt"""
    if not file_path.exists():
        return

    current_section = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                if line.startswith("# DEFAULT_FILE_DIR"):
                    current_section = "default_file_dir"
                elif line.startswith("# AI_CONFIG"):
                    current_section = "ai_config"
                elif line.startswith("# FONT_SETTINGS"):
                    current_section = "font_settings"
                continue

            if current_section == "default_file_dir":
                ctx.default_directory = line
                current_section = None
            elif current_section == "font_settings":
                # Parse font settings (key: value format)
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "font_family":
                        ctx.font_family = value
                    elif key == "font_size":
                        try:
                            ctx.font_size = int(value)
                        except ValueError:
                            pass  # Keep default if invalid
            elif current_section == "ai_config" or ":" in line:
                # Parse AI config settings (key: value format)
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Convert boolean strings
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                    # Try to convert to float
                    elif value.replace(".", "", 1).isdigit():
                        value = float(value) if "." in value else int(value)

                    ctx.ai_config[key] = value


def _load_replace_file(file_path, ctx: "BookfixContext") -> None:
    """Load REPLACE rules from replace.txt"""
    if not file_path.exists():
        return

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines, comments, and section headers
            if not line or line.startswith("#"):
                continue

            # Parse replacement rules (pattern -> pronunciation)
            if "->" in line:
                parts = line.split("->", 1)
                if len(parts) == 2:
                    pattern = parts[0].strip()
                    replacement = parts[1].strip()
                    ctx.replacements[pattern] = replacement


def _load_choice_file(file_path, ctx: "BookfixContext") -> None:
    """Load CHOICE definitions from choice.txt"""
    if not file_path.exists():
        return

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines, comments, and section headers
            if not line or line.startswith("#"):
                continue

            # Parse choice definitions (word -> option1 ; option2)
            if "->" in line:
                parts = line.split("->", 1)
                if len(parts) == 2:
                    word = parts[0].strip()
                    options_str = parts[1].strip()

                    # Check for POS tags
                    raw_options = [opt.strip() for opt in options_str.split(";")]

                    # Check if first option has POS tags
                    if raw_options and ":" in raw_options[0]:
                        # Tagged choices (advanced format)
                        tagged_options = {}
                        for option in raw_options:
                            if ":" in option:
                                spelling, tags = option.split(":", 1)
                                tag_list = [t.strip() for t in tags.split(",")]
                                tagged_options[spelling.strip()] = tag_list
                            else:
                                tagged_options[option.strip()] = []
                        ctx.tagged_choices[word] = tagged_options
                    else:
                        # Simple format: word -> option1 ; option2
                        if raw_options:
                            ctx.choices[word] = raw_options


def _load_skip_choice_file(file_path, ctx: "BookfixContext") -> None:
    """Load SKIP_CHOICE patterns from skip_choice.txt"""
    if not file_path.exists():
        return

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines, comments, and section headers
            if not line or line.startswith("#"):
                continue

            # Add pattern to skip list
            ctx.skip_choice.append(line)


def _load_simple_list_file(file_path, target_list: List[str]) -> None:
    """Load simple word list files (one word per line)"""
    if not file_path.exists():
        return

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines, comments, and section headers
            if not line or line.startswith("#"):
                continue

            # Add word to list
            target_list.append(line)


def _parse_data_file_lines(lines: List[str], ctx: "BookfixContext") -> None:
    """Parse the lines from the data file and populate the context."""

    log_message("DEBUG: Starting data file parsing line by line.")

    # Initialize context dictionaries
    ctx.choices = {}
    ctx.tagged_choices = {}
    ctx.replacements = {}
    ctx.periods = {}
    ctx.upper_to_lower = []
    ctx.cap_ignore = []
    ctx.roman_ignore = []
    ctx.skip_choice = []

    current_section = None

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        log_message(f"DEBUG: Line {line_num}: '{line}'")

        # Skip empty lines
        if not line:
            if current_section:
                log_message(
                    f"DEBUG: Skipping empty line within section '{current_section}'"
                )
            continue

        # Check for section markers
        if line.startswith("#"):
            if line.startswith("# "):
                section_name = line[2:].strip()
                if section_name in [
                    "DEFAULT_FILE_DIR",
                    "REPLACE",
                    "CHOICE",
                    "UPPER_TO_LOWER",
                    "CAP_IGNORE",
                    "ROMAN_IGNORE",
                    "AI_CONFIG",
                    "SKIP_CHOICE",
                ]:
                    current_section = section_name.lower()
                    log_message(f"DEBUG: Found section marker: {line}")
                    continue
            else:
                # Comment line within a section
                if current_section:
                    log_message(
                        f"DEBUG: Skipping comment line within section '{current_section}': '{line}'"
                    )
                continue

        # Process content based on current section
        if current_section:
            log_message(
                f"DEBUG: Processing content for section '{current_section}': '{line}'"
            )

            if current_section == "default_file_dir":
                ctx.default_directory = line
                log_message(f"DEBUG: Loaded default directory: '{line}'")

            elif current_section == "replace":
                _parse_replacement_line(line, ctx)

            elif current_section == "choice":
                _parse_choice_line(line, ctx)

            elif current_section == "upper_to_lower":
                ctx.upper_to_lower.append(line)
                log_message(f"DEBUG: Added upper_to_lower: '{line}'")

            elif current_section == "cap_ignore":
                ctx.cap_ignore.append(line)
                log_message(f"DEBUG: Added cap_ignore: '{line}'")

            elif current_section == "roman_ignore":
                ctx.roman_ignore.append(line)
                log_message(f"DEBUG: Added roman_ignore: '{line}'")

            elif current_section == "skip_choice":
                ctx.skip_choice.append(line)
                log_message(f"DEBUG: Added skip_choice: '{line}'")

            elif current_section == "ai_config":
                _parse_ai_config_line(line, ctx)

    log_message(
        f"Loaded {len(ctx.choices)} choice rules, {len(ctx.replacements)} replacement rules, {len(ctx.periods)} period rules."
    )


def _parse_ai_config_line(line: str, ctx: "BookfixContext") -> None:
    """Parse an AI configuration line."""
    log_message(f"DEBUG: Parsing AI config line: '{line}'")
    if ":" in line:
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        # Initialize ai_config dictionary if it doesn't exist
        if not hasattr(ctx, "ai_config"):
            ctx.ai_config = {}

        # Convert string values to appropriate types
        if key == "ai_enabled":
            ctx.ai_config[key] = value.lower() in ["true", "yes", "1"]
        elif key == "confidence_threshold":
            ctx.ai_config[key] = float(value) if value else 0.8
        elif key == "rate_limit":
            ctx.ai_config[key] = float(value) if value else 0.5
        elif key == "max_retries":
            ctx.ai_config[key] = int(value) if value else 3
        elif key == "fallback_to_manual":
            ctx.ai_config[key] = value.lower() in ["true", "yes", "1"]
        elif key == "show_ai_reasoning":
            ctx.ai_config[key] = value.lower() in ["true", "yes", "1"]
        elif key == "context_size":
            ctx.ai_config[key] = int(value) if value else 250
        elif key == "show_pattern_analyzer_prompt":
            ctx.ai_config[key] = value.lower() in ["true", "yes", "1"]
        else:
            ctx.ai_config[key] = value

        log_message(f"DEBUG: Added AI config: '{key}' = '{ctx.ai_config[key]}'")
    else:
        log_message(f"WARNING: Malformed AI config line: '{line}'", level="WARNING")


def _parse_replacement_line(line: str, ctx: "BookfixContext") -> None:
    """Parse a replacement rule line."""
    if " -> " in line:
        parts = line.split(" -> ", 1)
        if len(parts) == 2:
            original = parts[0]
            replacement = parts[1]  # Can be empty string for deletion

            # Handle quoted empty strings: -> "" becomes empty string
            if replacement == '""' or replacement == "''":
                replacement = ""
                log_message(f"DEBUG: Added replacement (deletion): '{original}' -> ''")
            else:
                log_message(
                    f"DEBUG: Added replacement: '{original}' -> '{replacement}'"
                )

            ctx.replacements[original] = replacement
        elif len(parts) == 1:
            # Handle case where replacement is empty (deletion)
            # Example: "… ->" means delete the ellipsis
            original = parts[0]
            replacement = ""
            ctx.replacements[original] = replacement
            log_message(f"DEBUG: Added replacement (deletion): '{original}' -> ''")
        else:
            log_message(
                f"WARNING: Malformed replacement line: '{line}'", level="WARNING"
            )
    else:
        log_message(
            f"WARNING: DEBUG: Skipping malformed replacement line: '{line}'",
            level="WARNING",
        )


def _parse_choice_line(line: str, ctx: "BookfixContext") -> None:
    """Parse a choice rule line with flexible separators."""
    # Ignore commented out lines
    if line.startswith("#"):
        return

    # Find the first occurrence of either separator
    idx_arrow = line.find(" -> ")
    idx_colon = line.find(":")

    separator_idx = -1
    separator_len = 0

    if idx_arrow != -1 and idx_colon != -1:
        # Both found, use the one that appears first
        if idx_arrow < idx_colon:
            separator_idx = idx_arrow
            separator_len = len(" -> ")
        else:
            separator_idx = idx_colon
            separator_len = 1
    elif idx_arrow != -1:
        separator_idx = idx_arrow
        separator_len = len(" -> ")
    elif idx_colon != -1:
        separator_idx = idx_colon
        separator_len = 1

    if separator_idx == -1:
        log_message(
            f"WARNING: Malformed choice line (no '->' or ':' separator): '{line}'",
            level="WARNING",
        )
        return

    word = line[:separator_idx].strip()
    options_str = line[separator_idx + separator_len :].strip()

    # New, preferred format: word -> option1 (def1) => option2 (def2)
    if " => " in options_str:
        option_parts = [p.strip() for p in options_str.split(" => ")]
        contextualized_options = []
        raw_options = []

        for part in option_parts:
            match = re.match(r"(.+?)\s*\((.*?)\)", part)
            if match:
                spelling, context = match.groups()
                spelling = spelling.strip()
                context = context.strip()
                contextualized_options.append((spelling, context))
                raw_options.append(spelling)
            else:
                contextualized_options.append((part, ""))
                raw_options.append(part)

        if contextualized_options:
            ctx.contextualized_choices[word] = contextualized_options
            ctx.choices[word] = raw_options
            log_message(
                f"DEBUG: Added definition-based choice: '{word}' -> {contextualized_options}"
            )

    # Spacy-style tagged format: word -> option1:tag1,tag2 ; option2:tag3
    elif ":" in options_str:
        tagged_options = []
        option_parts = options_str.split(" ; ")
        for option_part in option_parts:
            if ":" in option_part:
                spelling, tags_str = option_part.split(":", 1)
                tags = [tag.strip() for tag in tags_str.split(",")]
                tagged_options.append((spelling.strip(), tags))
            else:
                tagged_options.append((option_part.strip(), []))

        if tagged_options:
            ctx.tagged_choices[word] = tagged_options
            log_message(f"DEBUG: Added tagged choice: '{word}' -> {tagged_options}")

    # Simple format: word -> option1 ; option2
    else:
        raw_options = [opt.strip() for opt in options_str.split(" ; ")]
        if raw_options:
            ctx.choices[word] = raw_options
            log_message(f"DEBUG: Added simple choice: '{word}' -> {raw_options}")


def save_cap_ignore_to_data_file(cap_ignore_list: List[str]) -> bool:
    """
    Save the CAP_IGNORE list to data/cap_ignore.txt or .data.txt

    Args:
        cap_ignore_list: List of words to add to CAP_IGNORE section

    Returns:
        bool: True if successful, False otherwise
    """
    from pathlib import Path

    try:
        root_dir = Path(__file__).parent.parent
        data_dir = root_dir / "data"

        # Check if using data/ directory structure
        if data_dir.exists() and data_dir.is_dir():
            cap_ignore_file = data_dir / "cap_ignore.txt"

            # Write to data/cap_ignore.txt (overwrite with full list)
            with open(cap_ignore_file, "w", encoding="utf-8") as f:
                # Write header
                f.write("# CAP_IGNORE\n")
                f.write(
                    "# Capitalized words and acronyms to ignore during caps processing\n"
                )
                f.write("# Format: WORD (one per line)\n\n")
                # Write sorted list
                for item in sorted(cap_ignore_list):
                    f.write(f"{item}\n")

            log_message(
                f"Successfully saved {len(cap_ignore_list)} items to {cap_ignore_file}"
            )
            return True

        # Fall back to legacy .data.txt file
        data_file_path = root_dir / ".data.txt"

        # Read existing file
        lines = []
        if data_file_path.exists():
            with open(data_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Find CAP_IGNORE section and replace it
        new_lines = []
        in_cap_ignore_section = False
        cap_ignore_section_found = False

        for line in lines:
            line_stripped = line.strip()

            if line_stripped == "# CAP_IGNORE":
                # Start of CAP_IGNORE section
                new_lines.append(line)
                in_cap_ignore_section = True
                cap_ignore_section_found = True

                # Add all cap ignore items
                for item in sorted(cap_ignore_list):
                    new_lines.append(f"{item}\n")
                continue

            if in_cap_ignore_section:
                # Check if we've reached the next section
                if line_stripped.startswith("# ") and line_stripped != "# CAP_IGNORE":
                    # End of CAP_IGNORE section, add this line and continue
                    new_lines.append(line)
                    in_cap_ignore_section = False
                    continue
                # Skip lines in CAP_IGNORE section (they're being replaced)
                continue

            # Add non-CAP_IGNORE lines
            new_lines.append(line)

        # If CAP_IGNORE section wasn't found, add it at the end
        if not cap_ignore_section_found:
            if new_lines and not new_lines[-1].endswith("\n"):
                new_lines.append("\n")
            new_lines.append("# CAP_IGNORE\n")
            for item in sorted(cap_ignore_list):
                new_lines.append(f"{item}\n")

        # Write back to file
        with open(data_file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log_message(
            f"Successfully saved {len(cap_ignore_list)} items to CAP_IGNORE section"
        )
        return True

    except Exception as e:
        log_message(f"Error saving CAP_IGNORE to data file: {e}", level="ERROR")
        return False


def save_upper_to_lower_to_data_file(upper_to_lower_list: List[str]) -> bool:
    """
    Save the UPPER_TO_LOWER list to data/upper_to_lower.txt or .data.txt

    Args:
        upper_to_lower_list: List of words to add to UPPER_TO_LOWER section

    Returns:
        bool: True if successful, False otherwise
    """
    from pathlib import Path

    try:
        root_dir = Path(__file__).parent.parent
        data_dir = root_dir / "data"

        # Check if using data/ directory structure
        if data_dir.exists() and data_dir.is_dir():
            upper_to_lower_file = data_dir / "upper_to_lower.txt"

            # Write to data/upper_to_lower.txt (overwrite with full list)
            with open(upper_to_lower_file, "w", encoding="utf-8") as f:
                # Write header
                f.write("# UPPER_TO_LOWER\n")
                f.write(
                    "# Pronounceable acronyms to convert to title case\n"
                )
                f.write("# Format: WORD (one per line)\n\n")
                # Write sorted list
                for item in sorted(upper_to_lower_list):
                    f.write(f"{item}\n")

            log_message(
                f"Successfully saved {len(upper_to_lower_list)} items to {upper_to_lower_file}"
            )
            return True

        # Fall back to legacy .data.txt file
        data_file_path = root_dir / ".data.txt"

        # Read existing file
        lines = []
        if data_file_path.exists():
            with open(data_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Find UPPER_TO_LOWER section and replace it
        new_lines = []
        in_upper_to_lower_section = False
        upper_to_lower_section_found = False

        for line in lines:
            line_stripped = line.strip()

            if line_stripped == "# UPPER_TO_LOWER":
                # Start of UPPER_TO_LOWER section
                new_lines.append(line)
                in_upper_to_lower_section = True
                upper_to_lower_section_found = True

                # Add all upper_to_lower items
                for item in sorted(upper_to_lower_list):
                    new_lines.append(f"{item}\n")
                continue

            if in_upper_to_lower_section:
                # Check if we've reached the next section
                if line_stripped.startswith("# ") and line_stripped != "# UPPER_TO_LOWER":
                    # End of UPPER_TO_LOWER section, add this line and continue
                    new_lines.append(line)
                    in_upper_to_lower_section = False
                    continue
                # Skip lines in UPPER_TO_LOWER section (they're being replaced)
                continue

            # Add non-UPPER_TO_LOWER lines
            new_lines.append(line)

        # If UPPER_TO_LOWER section wasn't found, add it at the end
        if not upper_to_lower_section_found:
            if new_lines and not new_lines[-1].endswith("\n"):
                new_lines.append("\n")
            new_lines.append("# UPPER_TO_LOWER\n")
            for item in sorted(upper_to_lower_list):
                new_lines.append(f"{item}\n")

        # Write back to file
        with open(data_file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log_message(
            f"Successfully saved {len(upper_to_lower_list)} items to UPPER_TO_LOWER section"
        )
        return True

    except Exception as e:
        log_message(f"Error saving UPPER_TO_LOWER to data file: {e}", level="ERROR")
        return False


def save_default_directory_to_data_file(directory: str) -> bool:
    """
    Save the default directory to data/settings.txt or .data.txt

    Args:
        directory: Directory path to save

    Returns:
        True if saved successfully, False otherwise
    """
    from pathlib import Path

    # Check if using data/ directory structure
    data_dir = Path.cwd() / "data"

    if data_dir.exists() and data_dir.is_dir():
        settings_file = data_dir / "settings.txt"

        # Read existing settings
        lines = []
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Update DEFAULT_FILE_DIR value
        updated = False
        in_default_section = False
        new_lines = []

        for line in lines:
            stripped = line.strip()

            if stripped == "# DEFAULT_FILE_DIR":
                in_default_section = True
                new_lines.append(line)
                continue
            elif stripped.startswith("#") and in_default_section:
                # New section started
                in_default_section = False
                if not updated:
                    new_lines.append(f"{directory}\n\n")
                    updated = True
                new_lines.append(line)
                continue
            elif in_default_section and not stripped.startswith("#") and stripped:
                # Replace existing directory
                new_lines.append(f"{directory}\n\n")
                updated = True
                continue

            new_lines.append(line)

        # If no DEFAULT_FILE_DIR section exists, add it
        if not updated:
            new_lines.insert(0, "# DEFAULT_FILE_DIR\n")
            new_lines.insert(1, f"{directory}\n\n")

        # Write back to file
        with open(settings_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log_message(f"Saved default directory to {settings_file}: {directory}")
        return True

    # Fall back to legacy .data.txt
    data_file_path = os.path.join(os.getcwd(), ".data.txt")

    try:
        # Read existing file
        lines = []
        if os.path.exists(data_file_path):
            with open(data_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Find and update DEFAULT_FILE_DIR section
        updated = False
        in_default_section = False
        new_lines = []

        for line in lines:
            stripped = line.strip()

            if stripped == "# DEFAULT_FILE_DIR":
                in_default_section = True
                new_lines.append(line)
                continue
            elif stripped.startswith("#") and in_default_section:
                # New section started
                in_default_section = False
                if not updated:
                    new_lines.append(f"{directory}\n")
                    updated = True
                new_lines.append(line)
                continue
            elif in_default_section and not stripped.startswith("#") and stripped:
                # Replace existing directory
                new_lines.append(f"{directory}\n")
                updated = True
                continue

            new_lines.append(line)

        # If no DEFAULT_FILE_DIR section exists, add it
        if not updated:
            new_lines.insert(0, f"# DEFAULT_FILE_DIR\n{directory}\n")

        # Write back to file
        with open(data_file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log_message(f"Saved default directory to data file: {directory}")
        return True

    except Exception as e:
        log_message(f"Error saving default directory: {e}", level="ERROR")
        return False


def save_ai_config_to_data_file(config_key: str, config_value) -> bool:
    """
    Save a single AI config setting to data/settings.txt or .data.txt

    Args:
        config_key: The config key (e.g., 'show_ai_reasoning', 'context_size')
        config_value: The value to save

    Returns:
        True if saved successfully, False otherwise
    """
    from pathlib import Path

    # Check if using data/ directory structure
    data_dir = Path.cwd() / "data"

    if data_dir.exists() and data_dir.is_dir():
        settings_file = data_dir / "settings.txt"

        # Read existing settings
        lines = []
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Convert value to string format
        if isinstance(config_value, bool):
            value_str = "true" if config_value else "false"
        else:
            value_str = str(config_value)

        # Update or add the config value
        updated = False
        new_lines = []

        for line in lines:
            stripped = line.strip()

            # Check if this line is the config we're updating
            if ":" in stripped and stripped.split(":", 1)[0].strip() == config_key:
                new_lines.append(f"{config_key}: {value_str}\n")
                updated = True
                continue

            new_lines.append(line)

        # If not found, append at the end
        if not updated:
            new_lines.append(f"{config_key}: {value_str}\n")

        # Write back to file
        with open(settings_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log_message(f"Saved AI config to {settings_file}: {config_key} = {value_str}")
        return True

    # Fall back to legacy .data.txt
    data_file_path = os.path.join(os.getcwd(), ".data.txt")

    try:
        # Read existing file
        lines = []
        if os.path.exists(data_file_path):
            with open(data_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Find and update AI_CONFIG section
        updated = False
        in_ai_config_section = False
        new_lines = []

        # Convert value to string format
        if isinstance(config_value, bool):
            value_str = "true" if config_value else "false"
        else:
            value_str = str(config_value)

        for line in lines:
            stripped = line.strip()

            if stripped == "# AI_CONFIG":
                in_ai_config_section = True
                new_lines.append(line)
                continue
            elif stripped.startswith("#") and in_ai_config_section:
                # New section started - add our setting if not already updated
                if not updated:
                    new_lines.append(f"{config_key}: {value_str}\n")
                    updated = True
                in_ai_config_section = False
                new_lines.append(line)
                continue
            elif in_ai_config_section and stripped.startswith(config_key + ":"):
                # Replace existing value
                new_lines.append(f"{config_key}: {value_str}\n")
                updated = True
                continue

            new_lines.append(line)

        # If in AI_CONFIG section at end of file and not updated
        if in_ai_config_section and not updated:
            new_lines.append(f"{config_key}: {value_str}\n")
            updated = True

        # If no AI_CONFIG section exists, add it at the end
        if not updated:
            new_lines.append("\n# AI_CONFIG\n")
            new_lines.append(f"{config_key}: {value_str}\n")

        # Write back to file
        with open(data_file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log_message(f"Saved AI config to data file: {config_key} = {value_str}")
        return True

    except Exception as e:
        log_message(f"Error saving AI config: {e}", level="ERROR")
        return False


def append_replace_rule(data_file_path: str, from_text: str, to_text: str) -> bool:
    """
    Append a replacement rule to data/replace.txt or .data.txt

    Args:
        data_file_path: Path to .data.txt configuration file (legacy parameter, may be ignored)
        from_text: Text to replace
        to_text: Replacement text

    Returns:
        True if successful, False otherwise
    """
    from pathlib import Path

    try:
        # Check if using data/ directory structure
        root_dir = Path(data_file_path).parent if data_file_path else Path.cwd()
        data_dir = root_dir / "data"

        if data_dir.exists() and data_dir.is_dir():
            replace_file = data_dir / "replace.txt"

            # Append to data/replace.txt
            with open(replace_file, "a", encoding="utf-8") as f:
                f.write(f"{from_text} -> {to_text}\n")

            log_message(
                f"Added replacement rule to {replace_file}: '{from_text}' -> '{to_text}'"
            )
            return True

        # Fall back to legacy .data.txt
        # Read the file
        with open(data_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find # REPLACE section
        replace_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "# REPLACE":
                replace_idx = i
                break

        if replace_idx == -1:
            # Section doesn't exist, create it
            lines.append("\n# REPLACE\n")
            replace_idx = len(lines) - 1
            insert_idx = len(lines)
        else:
            # Find where to insert (before next # section or at end of section)
            insert_idx = replace_idx + 1
            for i in range(replace_idx + 1, len(lines)):
                if lines[i].strip().startswith("#") and lines[i].strip() != "#":
                    insert_idx = i
                    break
                else:
                    insert_idx = i + 1

        # Create the new rule line
        rule_line = f"{from_text} -> {to_text}\n"

        # Insert the rule
        lines.insert(insert_idx, rule_line)

        # Write back to file
        with open(data_file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        log_message(f"Added replacement rule: '{from_text}' -> '{to_text}'")
        return True

    except Exception as e:
        log_message(f"Error appending replacement rule: {e}", level="ERROR")
        return False


def append_skip_choice_rule(data_file_path: str, phrase: str) -> bool:
    """
    Append a skip choice rule to data/skip_choice.txt or .data.txt

    Args:
        data_file_path: Path to .data.txt configuration file (legacy parameter, may be ignored)
        phrase: The phrase to add to the skip list.

    Returns:
        True if successful, False otherwise
    """
    from pathlib import Path

    try:
        # Check if using data/ directory structure
        root_dir = Path(data_file_path).parent if data_file_path else Path.cwd()
        data_dir = root_dir / "data"

        if data_dir.exists() and data_dir.is_dir():
            skip_file = data_dir / "skip_choice.txt"

            # Check if phrase already exists
            if skip_file.exists():
                with open(skip_file, "r", encoding="utf-8") as f:
                    existing_phrases = {line.strip() for line in f if line.strip()}
                if phrase in existing_phrases:
                    log_message(f"Skip choice phrase '{phrase}' already exists.")
                    return True  # Not an error, just no action needed

            # Append to data/skip_choice.txt
            with open(skip_file, "a", encoding="utf-8") as f:
                f.write(f"{phrase}\n")

            log_message(f"Added skip choice rule to {skip_file}: '{phrase}'")
            return True

        # Fall back to legacy .data.txt
        # Read the file
        with open(data_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find # SKIP_CHOICE section
        section_marker = "# SKIP_CHOICE"
        section_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == section_marker:
                section_idx = i
                break

        if section_idx == -1:
            # Section doesn't exist, create it
            lines.append("\n" + section_marker + "\n")
            insert_idx = len(lines)
        else:
            # Find where to insert (before next # section or at end of section)
            insert_idx = section_idx + 1
            for i in range(section_idx + 1, len(lines)):
                if lines[i].strip().startswith("#") and lines[i].strip() != "#":
                    insert_idx = i
                    break
                else:
                    insert_idx = i + 1

        # Check if phrase already exists
        existing_phrases = {l.strip() for l in lines[section_idx + 1 : insert_idx]}
        if phrase in existing_phrases:
            log_message(f"Skip choice phrase '{phrase}' already exists.")
            return True  # Not an error, just no action needed

        # Create the new rule line
        rule_line = f"{phrase}\n"

        # Insert the rule
        lines.insert(insert_idx, rule_line)

        # Write back to file
        with open(data_file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        log_message(f"Added skip choice rule: '{phrase}'")
        return True

    except Exception as e:
        log_message(f"Error appending skip choice rule: {e}", level="ERROR")
        return False


def save_font_settings(font_family: str, font_size: int) -> bool:
    """
    Save font settings to data/settings.txt or .data.txt

    Args:
        font_family: The font family name
        font_size: The font size in points

    Returns:
        True if saved successfully, False otherwise
    """
    from pathlib import Path

    # Check if using data/ directory structure
    data_dir = Path.cwd() / "data"

    if data_dir.exists() and data_dir.is_dir():
        settings_file = data_dir / "settings.txt"

        # Read existing settings
        lines = []
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Find or create FONT_SETTINGS section
        in_font_section = False
        font_family_updated = False
        font_size_updated = False
        new_lines = []
        font_section_exists = False

        for line in lines:
            stripped = line.strip()

            # Track if we're in font settings section
            if stripped == "# FONT_SETTINGS":
                in_font_section = True
                font_section_exists = True
                new_lines.append(line)
                continue
            elif stripped.startswith("#") and in_font_section:
                # Entering a new section
                in_font_section = False

            # Update font settings if in the section
            if in_font_section and ":" in stripped:
                key = stripped.split(":", 1)[0].strip()
                if key == "font_family":
                    new_lines.append(f"font_family: {font_family}\n")
                    font_family_updated = True
                    continue
                elif key == "font_size":
                    new_lines.append(f"font_size: {font_size}\n")
                    font_size_updated = True
                    continue

            new_lines.append(line)

        # If font section doesn't exist, create it
        if not font_section_exists:
            new_lines.append("\n# FONT_SETTINGS\n")
            new_lines.append(f"font_family: {font_family}\n")
            new_lines.append(f"font_size: {font_size}\n")
        else:
            # Add missing keys if not updated
            if not font_family_updated:
                # Insert after FONT_SETTINGS header
                for i, line in enumerate(new_lines):
                    if line.strip() == "# FONT_SETTINGS":
                        new_lines.insert(i + 1, f"font_family: {font_family}\n")
                        break
            if not font_size_updated:
                for i, line in enumerate(new_lines):
                    if line.strip() == "# FONT_SETTINGS" or (
                        i > 0 and new_lines[i - 1].strip().startswith("font_family")
                    ):
                        insert_pos = i + 1
                        if new_lines[i].strip().startswith("font_family"):
                            insert_pos = i + 1
                        new_lines.insert(insert_pos, f"font_size: {font_size}\n")
                        break

        # Write back to file
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            log_message(f"Saved font settings: {font_family}, {font_size}pt")
            return True
        except Exception as e:
            log_message(f"Error saving font settings: {e}", level="ERROR")
            return False

    return False
