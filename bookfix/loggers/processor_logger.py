"""Per-file logging utility for all Bookfix processors."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class ProcessorLogger:
    """
    Logger that creates module-specific log files in the input file's directory.

    Usage:
        logger = ProcessorLogger(input_file_path, "numbered")
        logger.log_change("183rd", "one hundred eighty third", "the 183rd division", "AI ordinal conversion")
    """

    def __init__(self, input_file_path: Optional[str], module_name: str):
        """
        Initialize logger for a specific module and input file.

        Args:
            input_file_path: Path to the input file being processed (can be None)
            module_name: Name of the processor module (e.g., "numbered", "caps", "page")
        """
        self.input_file_path = input_file_path
        self.module_name = module_name

        # Create log file in same directory as input file
        if input_file_path:
            input_dir = os.path.dirname(os.path.abspath(input_file_path))
        else:
            # Fallback to current working directory if no input file path
            input_dir = os.getcwd()

        self.log_file = os.path.join(input_dir, f"{module_name}.log")

        # Create log file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"# {module_name.upper()} Processing Log\n")
                f.write(
                    f"# Input file: {os.path.basename(input_file_path) if input_file_path else 'Unknown'}\n"
                )
                f.write(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")

    def log_change(
        self,
        original: str,
        replacement: str,
        context: Optional[str] = None,
        reasoning: Optional[str] = None,
    ):
        """
        Log a single change made by the processor.

        Args:
            original: Original text before change
            replacement: Text after change
            context: Optional surrounding context where change occurred
            reasoning: Optional explanation of why change was made
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}]\n")
            f.write(f"ORIGINAL:    {original}\n")
            f.write(f"REPLACEMENT: {replacement}\n")

            if context:
                f.write(f"CONTEXT:     {context}\n")

            if reasoning:
                f.write(f"REASONING:   {reasoning}\n")

            f.write("\n")

    def log_removal(
        self,
        removed_text: str,
        context: Optional[str] = None,
        reasoning: Optional[str] = None,
    ):
        """
        Log text that was removed.

        Args:
            removed_text: Text that was removed
            context: Optional surrounding context where removal occurred
            reasoning: Optional explanation of why text was removed
        """
        self.log_change(removed_text, "[REMOVED]", context, reasoning)

    def log_info(self, message: str):
        """
        Log an informational message.

        Args:
            message: Information message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [INFO] {message}\n")

    def log_skip(self, text: str, reason: str):
        """
        Log text that was skipped (not processed).

        Args:
            text: Text that was skipped
            reason: Reason for skipping
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [SKIP] {text} - {reason}\n")

    def log_error(self, message: str, error: Optional[Exception] = None):
        """
        Log an error that occurred during processing.

        Args:
            message: Error message
            error: Optional exception object
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [ERROR] {message}\n")
            if error:
                f.write(f"           {type(error).__name__}: {str(error)}\n")
            f.write("\n")

    def log_summary(self, stats: dict):
        """
        Log summary statistics at end of processing.

        Args:
            stats: Dictionary of statistics (e.g., {"changes": 42, "skips": 15})
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"SUMMARY [{timestamp}]\n")
            for key, value in stats.items():
                f.write(f"  {key}: {value}\n")
            f.write("=" * 80 + "\n\n")
