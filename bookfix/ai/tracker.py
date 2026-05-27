"""
AI Change Tracking System for Bookfix.

Tracks all AI-made changes with position tracking, module identification,
and support for user corrections.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import datetime


@dataclass
class AIChange:
    """Represents a single AI-made change."""

    module: str  # Which processor made the change
    original: str  # Original text
    replacement: str  # AI's replacement
    start_pos: int  # Start position in text
    end_pos: int  # End position in text
    context_before: str  # Text before the change
    context_after: str  # Text after the change
    confidence: float  # AI confidence score (0.0-1.0)
    timestamp: datetime.datetime  # When change was made
    user_verified: bool = False  # User has reviewed this change
    user_corrected: bool = False  # User made a correction
    user_correction: str = ""  # User's correction if different from AI


class AIChangeTracker:
    """
    Tracks all AI changes made during processing.

    Maintains position-based tracking and handles text updates
    when user makes corrections.
    """

    def __init__(self):
        """Logs a change made to the current text.
        Args:
        module_name (str): The name of the module making the change.
        original (str): The original text before the change.
        replacement (str): The new text after the change.
        position (int): The position where the change occurred.
        context_before (str): Text from before the change.
        context_after (str): Text from after the change.
        confidence (float): Confidence level of the change.
        """
        self.changes: List[AIChange] = []
        self.current_text: str = ""
        self._position_offset: int = 0

    def log_change(
        self,
        module_name: str,
        original: str,
        replacement: str,
        position: int,
        context_before: str,
        context_after: str,
        confidence: float,
    ) -> None:
        """
        Log an AI-made change.

        Args:
            module_name: Name of the processor that made the change
            original: Original text that was changed
            replacement: AI's replacement text
            position: Start position in the original text
            context_before: Text before the change for context
            context_after: Text after the change for context
            confidence: AI confidence score (0.0-1.0)
        """
        change = AIChange(
            module=module_name,
            original=original,
            replacement=replacement,
            start_pos=position + self._position_offset,
            end_pos=position + self._position_offset + len(replacement),
            context_before=context_before,
            context_after=context_after,
            confidence=confidence,
            timestamp=datetime.datetime.now(),
        )

        self.changes.append(change)

        # Update position offset for subsequent changes
        length_difference = len(replacement) - len(original)
        self._position_offset += length_difference

    def get_change_at_position(self, position: int) -> Optional[AIChange]:
        """
        Find the AI change at a specific text position.

        Args:
            position: Character position in the text

        Returns:
            AIChange if found, None otherwise
        """
        for change in self.changes:
            if change.start_pos <= position <= change.end_pos:
                return change
        return None

    def update_change_positions_after_edit(
        self, edit_position: int, old_length: int, new_length: int
    ) -> None:
        """
        Update all change positions after a user edit.

        Args:
            edit_position: Position where edit occurred
            old_length: Length of text that was replaced
            new_length: Length of new text
        """
        length_delta = new_length - old_length

        for change in self.changes:
            # Only adjust changes that come after the edit
            if change.start_pos > edit_position:
                change.start_pos += length_delta
                change.end_pos += length_delta

    def apply_user_correction(self, change: AIChange, user_correction: str) -> None:
        """
        Apply a user correction to a change.

        Args:
            change: The AIChange to correct
            user_correction: User's corrected text
        """
        change.user_corrected = True
        change.user_correction = user_correction
        change.user_verified = True

        # Update positions of subsequent changes
        old_length = change.end_pos - change.start_pos
        new_length = len(user_correction)
        self.update_change_positions_after_edit(
            change.start_pos, old_length, new_length
        )

        # Update the change's end position
        change.end_pos = change.start_pos + new_length

    def mark_verified(self, change: AIChange) -> None:
        """Mark a change as verified by the user."""
        change.user_verified = True

    def get_changes_by_module(self) -> Dict[str, List[AIChange]]:
        """Group changes by module name."""
        by_module = {}
        for change in self.changes:
            if change.module not in by_module:
                by_module[change.module] = []
            by_module[change.module].append(change)
        return by_module

    def get_unverified_changes(self) -> List[AIChange]:
        """Get all changes that haven't been verified by the user."""
        return [change for change in self.changes if not change.user_verified]

    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics about the changes."""
        total_changes = len(self.changes)
        verified_changes = len([c for c in self.changes if c.user_verified])
        corrected_changes = len([c for c in self.changes if c.user_corrected])

        by_module = self.get_changes_by_module()
        module_counts = {module: len(changes) for module, changes in by_module.items()}

        avg_confidence = (
            sum(c.confidence for c in self.changes) / total_changes
            if total_changes > 0
            else 0
        )

        return {
            "total_changes": total_changes,
            "verified_changes": verified_changes,
            "corrected_changes": corrected_changes,
            "unverified_changes": total_changes - verified_changes,
            "module_counts": module_counts,
            "average_confidence": avg_confidence,
        }

    def generate_report(self) -> str:
        """Generate a human-readable summary report."""
        stats = self.get_statistics()

        report = []
        report.append("=== AI Processing Summary ===\n")
        report.append(f"Total Changes: {stats['total_changes']}")
        report.append(f"User Verified: {stats['verified_changes']}")
        report.append(f"User Corrected: {stats['corrected_changes']}")
        report.append(f"Average Confidence: {stats['average_confidence']:.2f}\n")

        report.append("Changes by Module:")
        for module, count in stats["module_counts"].items():
            report.append(f"  {module}: {count} changes")

        if stats["corrected_changes"] > 0:
            report.append("\nUser Corrections:")
            for change in self.changes:
                if change.user_corrected:
                    report.append(
                        f"  {change.module}: '{change.replacement}' → '{change.user_correction}'"
                    )

        return "\n".join(report)
