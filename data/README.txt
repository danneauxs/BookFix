DATA DIRECTORY - Configuration Files
====================================

This directory contains the split configuration files for BookFix.
Previously all configuration was in the monolithic .data.txt file.

MIGRATION INSTRUCTIONS:
----------------------

1. Copy sections from .data.txt to the appropriate files:

   .data.txt section          → Target file
   -----------------            ------------
   # DEFAULT_FILE_DIR         → settings.txt
   # REPLACE                  → replace.txt
   # CHOICE                   → choice.txt
   # SKIP_CHOICE              → skip_choice.txt
   # UPPER_TO_LOWER           → upper_to_lower.txt
   # CAP_IGNORE               → cap_ignore.txt
   # ROMAN_IGNORE             → roman_ignore.txt

2. For each section:
   - Copy the section header (e.g., "# REPLACE")
   - Copy all entries under that section
   - Stop when you hit the next section header
   - Include commented-out entries (lines starting with #)

3. Settings file:
   - Copy DEFAULT_FILE_DIR and the path below it
   - Copy any other settings like "show_pattern_analyzer_prompt: true"

4. After migration is complete, notify Claude to update the code
   to load from these files instead of .data.txt

IMPORTANT NOTES:
---------------
- Preserve all comments and formatting
- Include commented-out patterns (like "#dived -> dove")
- Keep blank lines for readability
- The section headers (# REPLACE, etc.) should be included

FILE DESCRIPTIONS:
-----------------

settings.txt       - Application configuration and preferences
replace.txt        - Automatic text replacement rules (largest file)
choice.txt         - Heteronym pronunciation choices
skip_choice.txt    - Patterns to skip AI processing
upper_to_lower.txt - Words to convert to lowercase
cap_ignore.txt     - Capitalized words to ignore
roman_ignore.txt   - Acronyms that look like Roman numerals

After migration, the application will:
- Load from data/ directory if files exist
- Fall back to .data.txt if data/ not found
- Provide better organization and faster access
