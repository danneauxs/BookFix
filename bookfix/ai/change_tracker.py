"""
AI Change Tracking System for Bookfix Review Window.

Tracks all AI-made changes with position tracking, module identification,
and support for user corrections and navigation.
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import datetime
import os


@dataclass
class AIChange:
    """Represents a single AI-made change."""

    id: int  # Unique ID for navigation
    module: str  # Which processor made the change
    original: str  # Original text
    replacement: str  # AI's replacement
    options: List[str]  # Available choices for this change
    start_pos: int  # Start position in current text
    end_pos: int  # End position in current text
    original_start: int  # Original start position (for reference)
    original_end: int  # Original end position (for reference)
    context_before: str  # Text before the change
    context_after: str  # Text after the change
    confidence: float  # AI confidence score (0.0-1.0)
    reasoning: str  # AI's reasoning for the change
    timestamp: datetime.datetime  # When change was made
    pos_tag: str = ""  # POS tag from spaCy (for choices)
    decision_source: str = ""  # Source of the decision ('pos', 'keyword', 'llm', etc.)
    type: str = ""  # Number type (for numbered module)

    # User interaction
    user_reviewed: bool = False  # User has seen this change
    user_accepted: bool = False  # User accepted AI change
    user_corrected: bool = False  # User made a correction
    user_correction: str = ""  # User's correction if different from AI

    # Navigation state
    is_current: bool = False  # Currently selected change


class AIChangeTracker:
    """
    Tracks all AI changes for the review window system.

    Provides navigation, position management, and user interaction tracking.
    """

    def __init__(self):
        self.changes: List[AIChange] = []
        self.current_index: int = -1  # Index of currently selected change
        self.next_id: int = 1  # Auto-incrementing ID counter

        # Text management
        self.original_text: str = ""
        self.current_text: str = ""

        # Debug logging
        self.debug_file = os.path.join(os.getcwd(), "bookfix_position_debug.log")
        self._debug_log("=== Change Tracker Initialized ===")

    def _debug_log(self, message: str):
        """Log debug message to file with timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.debug_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

        # Module color mapping for highlights
        self.module_colors = {
            "choices": "#FFE066",  # Yellow
            "roman": "#66B3FF",  # Light Blue
            "numbers": "#66FF66",  # Light Green
            "allcaps": "#FF9999",  # Light Pink
            "automatic": "#CC99FF",  # Light Purple
        }

    def set_text(self, original: str, current: str) -> None:
        """Set the original and current text."""
        self.original_text = original
        self.current_text = current

    def add_change(
        self,
        module_name: str,
        original: str,
        replacement: str,
        options: List[str],
        start_pos: int,
        end_pos: int,
        context_before: str,
        context_after: str,
        confidence: float,
        reasoning: str = "",
        pos_tag: str = "",
        decision_source: str = "",
        type: str = "",
    ) -> int:
        """
        Add an AI change to the tracker.

        Args:
            module_name: Name of the processor that made the change
            original: Original text that was changed
            replacement: AI's replacement text
            options: Available choices for this change
            start_pos: Start position in current text
            end_pos: End position in current text
            context_before: Text before the change for context
            context_after: Text after the change for context
            confidence: AI confidence score (0.0-1.0)
            reasoning: AI's reasoning for the change
            pos_tag: POS tag from spaCy (for choices module)
            decision_source: The source of the decision ('pos', 'llm', etc.)
            type: The type of number (for numbered module)

        Returns:
            Change ID for reference
        """
        change_id = self.next_id
        self.next_id += 1

        change = AIChange(
            id=change_id,
            module=module_name,
            original=original,
            replacement=replacement,
            options=options,
            start_pos=start_pos,
            end_pos=end_pos,
            original_start=start_pos,
            original_end=end_pos,
            context_before=context_before,
            context_after=context_after,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.datetime.now(),
            pos_tag=pos_tag,
            decision_source=decision_source,
            type=type,
        )

        self.changes.append(change)

        # Sort changes by position for proper navigation
        self.changes.sort(key=lambda c: c.start_pos)

        # Update indices after sorting
        self._update_indices()

        return change_id

    def _update_indices(self) -> None:
        """Update current_index after changes list is modified."""
        if self.changes and self.current_index >= 0:
            # Try to maintain current selection
            if self.current_index >= len(self.changes):
                self.current_index = len(self.changes) - 1
        elif self.changes:
            # Set to first change if none selected
            self.current_index = 0

    def get_current_change(self) -> Optional[AIChange]:
        """Get the currently selected change."""
        if 0 <= self.current_index < len(self.changes):
            return self.changes[self.current_index]
        return None

    def navigate_to_next(self) -> Optional[AIChange]:
        """Navigate to the next change."""
        if not self.changes:
            return None

        old_index = self.current_index

        # Clear current selection
        if self.current_index >= 0:
            self.changes[self.current_index].is_current = False

        # Move to next
        self.current_index = (self.current_index + 1) % len(self.changes)

        # Set new current
        current = self.changes[self.current_index]
        current.is_current = True

        self._debug_log(
            f"NAVIGATE: {old_index} → {self.current_index} | Change ID: {current.id} | Position: {current.start_pos}-{current.end_pos}"
        )

        return current

    def navigate_to_previous(self) -> Optional[AIChange]:
        """Navigate to the previous change."""
        if not self.changes:
            return None

        # Clear current selection
        if self.current_index >= 0:
            self.changes[self.current_index].is_current = False

        # Move to previous
        self.current_index = (self.current_index - 1) % len(self.changes)

        # Set new current
        current = self.changes[self.current_index]
        current.is_current = True

        return current

    def navigate_to_change(self, change_id: int) -> Optional[AIChange]:
        """Navigate directly to a specific change by ID."""
        for i, change in enumerate(self.changes):
            if change.id == change_id:
                # Clear current selection
                if self.current_index >= 0:
                    self.changes[self.current_index].is_current = False

                # Set new current
                self.current_index = i
                change.is_current = True

                return change
        return None

    def get_change_at_position(self, position: int) -> Optional[AIChange]:
        """Find the AI change at a specific text position."""
        for change in self.changes:
            if change.start_pos <= position <= change.end_pos:
                return change
        return None

    def get_change_by_id(self, change_id: int) -> Optional[AIChange]:
        """Find a change by its unique ID."""
        for change in self.changes:
            if change.id == change_id:
                return change
        return None

    def apply_user_correction(self, change_id: int, user_correction: str) -> bool:
        """
        Apply a user correction to a change.

        Args:
            change_id: ID of the change to correct
            user_correction: User's corrected text

        Returns:
            True if correction was applied successfully
        """
        change = self.get_change_by_id(change_id)
        if not change:
            return False

        # Update the change object's state
        change.user_corrected = True
        change.user_correction = user_correction
        change.user_reviewed = True
        change.user_accepted = True  # Corrected implies accepted

        self._debug_log(
            f"CORRECT: Change ID {change_id} corrected to '{user_correction}'"
        )
        return True

    def accept_change(self, change_id: int) -> bool:
        """Mark a change as accepted by the user."""
        change = self.get_change_by_id(change_id)
        if change:
            self._debug_log(
                f"ACCEPT: Change ID {change_id} | '{change.original}' → '{change.replacement}' | Position: {change.start_pos}-{change.end_pos}"
            )
            change.user_reviewed = True
            change.user_accepted = True
            change.user_corrected = (
                False  # Ensure this is reset if user accepts after correcting
            )
            return True
        self._debug_log(f"ACCEPT FAILED: Change ID {change_id} not found")
        return False

    def reject_change(self, change_id: int) -> bool:
        """Mark a change as rejected by the user (reverted to original)."""
        change = self.get_change_by_id(change_id)
        if not change:
            return False

        # Update the change state to reflect rejection
        change.user_reviewed = True
        change.user_accepted = False
        change.user_corrected = True  # A rejection is a correction back to the original
        change.user_correction = change.original

        self._debug_log(
            f"REJECT: Change ID {change_id} reverted to '{change.original}'"
        )
        return True

    def get_changes_by_module(self) -> Dict[str, List[AIChange]]:
        """Group changes by module name."""
        by_module = {}
        for change in self.changes:
            if change.module not in by_module:
                by_module[change.module] = []
            by_module[change.module].append(change)
        return by_module

    def get_unreviewed_changes(self) -> List[AIChange]:
        """Get all changes that haven't been reviewed by the user."""
        return [change for change in self.changes if not change.user_reviewed]

    def get_navigation_info(self) -> Dict[str, Any]:
        """Get current navigation state information."""
        total = len(self.changes)
        current_num = self.current_index + 1 if self.current_index >= 0 else 0

        return {
            "current_index": self.current_index,
            "current_number": current_num,
            "total_changes": total,
            "has_previous": self.current_index > 0,
            "has_next": self.current_index < total - 1,
            "navigation_text": (
                f"{current_num} of {total}" if total > 0 else "No changes"
            ),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics about the changes."""
        total_changes = len(self.changes)
        reviewed_changes = len([c for c in self.changes if c.user_reviewed])
        accepted_changes = len([c for c in self.changes if c.user_accepted])
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
            "reviewed_changes": reviewed_changes,
            "accepted_changes": accepted_changes,
            "corrected_changes": corrected_changes,
            "unreviewed_changes": total_changes - reviewed_changes,
            "module_counts": module_counts,
            "average_confidence": avg_confidence,
            "review_progress": round(
                (reviewed_changes / total_changes * 100) if total_changes > 0 else 0, 1
            ),
        }

    def build_final_text(self) -> str:
        """Build the final text from the original text and the change list."""
        if not self.original_text:
            return ""

        print("DEBUG: Starting build_final_text...")
        # Sort changes by original start position to apply them correctly
        sorted_changes = sorted(self.changes, key=lambda c: c.original_start)

        parts = []
        last_pos = 0

        for change in sorted_changes:
            print(
                f"DEBUG: Processing change ID: {change.id}, Original: '{change.original}', Replacement: '{change.replacement}', User Corrected: {change.user_corrected}, User Accepted: {change.user_accepted}, User Correction: '{change.user_correction}'"
            )

            # Append the original text segment before the current change
            segment_before = self.original_text[last_pos : change.original_start]
            parts.append(segment_before)
            print(
                f"DEBUG:   Appended segment before: '{segment_before[:50]}...'"
            )  # Truncate for readability

            # Determine which version of the text to use for the change
            if change.user_corrected:
                parts.append(change.user_correction)
                print(f"DEBUG:   Appended user_correction: '{change.user_correction}'")
            elif change.user_accepted:
                parts.append(change.replacement)
                print(f"DEBUG:   Appended replacement: '{change.replacement}'")
            else:  # Change was rejected or ignored
                parts.append(change.original)
                print(f"DEBUG:   Appended original: '{change.original}'")

            # Update the last position to the end of the change in the original text
            last_pos = change.original_end

        # Append the remainder of the original text after the last change
        segment_after = self.original_text[last_pos:]
        parts.append(segment_after)
        print(
            f"DEBUG: Appended final segment: '{segment_after[:50]}...'"
        )  # Truncate for readability

        final_text = "".join(parts)
        print(
            f"DEBUG: build_final_text completed. Final text length: {len(final_text)}"
        )
        return final_text

    def get_all_changes_by_original(self, original_text: str) -> List[AIChange]:
        """
        Get all changes with matching original text.

        Args:
            original_text: The original text to match

        Returns:
            List of AIChange objects with matching original text
        """
        return [
            change
            for change in self.changes
            if change.original.lower() == original_text.lower()
        ]

    def apply_bulk_decision(
        self, original_text: str, action: str, custom_text: str = None
    ) -> int:
        """
        Mark all changes matching original_text with the same decision.

        Args:
            original_text: The original text to match
            action: 'accept', 'reject', or 'custom'
            custom_text: Custom replacement text (only used if action='custom')

        Returns:
            Number of changes affected
        """
        matching_changes = self.get_all_changes_by_original(original_text)
        changes_affected = 0

        for change in matching_changes:
            if action == "accept":
                change.user_reviewed = True
                change.user_accepted = True
                change.user_corrected = False
                changes_affected += 1
                self._debug_log(
                    f"BULK ACCEPT: Change ID {change.id} | '{change.original}' → '{change.replacement}'"
                )

            elif action == "reject":
                change.user_reviewed = True
                change.user_accepted = False
                change.user_corrected = True
                change.user_correction = change.original
                changes_affected += 1
                self._debug_log(
                    f"BULK REJECT: Change ID {change.id} reverted to '{change.original}'"
                )

            elif action == "custom" and custom_text is not None:
                change.user_reviewed = True
                change.user_accepted = True
                change.user_corrected = True
                change.user_correction = custom_text
                changes_affected += 1
                self._debug_log(
                    f"BULK CUSTOM: Change ID {change.id} corrected to '{custom_text}'"
                )

        return changes_affected

    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        stats = self.get_statistics()

        report = []
        report.append("=== AI Changes Review Summary ===")
        report.append(f"Total Changes: {stats['total_changes']}")
        report.append(
            f"Review Progress: {stats['review_progress']}% ({stats['reviewed_changes']}/{stats['total_changes']})"
        )
        report.append(f"Accepted: {stats['accepted_changes']}")
        report.append(f"Corrected: {stats['corrected_changes']}")
        report.append(f"Average Confidence: {stats['average_confidence']:.2f}")
        report.append("")

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
