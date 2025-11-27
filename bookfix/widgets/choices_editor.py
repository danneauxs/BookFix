"""
Choices Review Editor Widget for Bookfix.

Review window for AI homograph decisions with correction and learning capabilities.
"""

import re
from typing import List, Dict, Tuple, Optional
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QLabel,
    QMessageBox,
    QProgressBar,
    QFrame,
    QComboBox,
    QGridLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor

from ..logging import log_message
from ..ai.choices_learning import ChoicesLearningStorage, ChoicesLearningAnalyzer
from ..datafile import save_font_settings
from .font_controls import FontControlsWidget


class ChoicesReviewEditor(QDialog):
    """
    Interactive choices review editor for AI homograph decisions.
    Shows AI choices with ability to accept or correct them.
    """

    changes_applied = pyqtSignal(str)  # Signal emitted when changes are applied

    def __init__(
        self,
        processed_text: str,
        ai_decisions: List[Dict],
        choices_map: Dict[str, List[str]],
        parent=None,
    ):
        """
        Initialize choices review editor.

        Args:
            processed_text: The text AFTER AI processing (what AI produced)
            ai_decisions: List of AI decision dicts with keys:
                         'word', 'original', 'choice', 'position_in_processed', 'options', 'confidence', 'reason'
            choices_map: Map of word -> available options
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_text = processed_text  # Text is ALREADY processed by AI
        self.original_text = processed_text  # Store original for rebuilding on undo
        self.ai_decisions = ai_decisions
        self.choices_map = choices_map

        # Track current selection
        self.current_decision_index = 0
        self.corrections = []  # Track user corrections for learning

        # Initialize learning system
        self.learning_storage = ChoicesLearningStorage()
        self.learning_analyzer = ChoicesLearningAnalyzer(self.learning_storage)

        self.setup_ui()
        self.populate_decisions_list()
        self.highlight_current_decision()

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Choices Review - AI Processing Results")
        self.setModal(True)
        self.resize(1200, 700)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Info label
        info_text = (
            f"Review AI homograph choices. {len(self.ai_decisions)} decisions made. "
            "Select to accept or correct."
        )
        self.info_label = QLabel(info_text)
        main_layout.addWidget(self.info_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.ai_decisions))
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Main splitter (left/right panels)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Text view
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)

        # Header with title and font controls
        header_layout = QHBoxLayout()
        left_label = QLabel("Text with AI Changes (highlighted):")
        header_layout.addWidget(left_label)

        # Add font controls
        self.font_controls = FontControlsWidget(initial_family="Arial", initial_size=12)
        self.font_controls.font_changed.connect(self._on_font_changed)
        header_layout.addWidget(self.font_controls)

        left_layout.addLayout(header_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Arial", 12))
        self.text_edit.setPlainText(self.current_text)
        left_layout.addWidget(self.text_edit)

        splitter.addWidget(left_frame)

        # Right panel - Decisions list and controls
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)

        right_label = QLabel("AI Decisions:")
        right_layout.addWidget(right_label)

        # Decisions list
        self.decisions_list = QListWidget()
        self.decisions_list.itemClicked.connect(self.on_decision_item_clicked)
        right_layout.addWidget(self.decisions_list)

        # Current decision details
        details_label = QLabel("Selected Decision:")
        right_layout.addWidget(details_label)

        self.decision_info = QLabel("Click a decision to review")
        self.decision_info.setWordWrap(True)
        self.decision_info.setStyleSheet(
            "padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;"
        )
        right_layout.addWidget(self.decision_info)

        # Alternative choices dropdown
        choice_label = QLabel("Change to:")
        right_layout.addWidget(choice_label)

        self.alternatives_combo = QComboBox()
        self.alternatives_combo.setEnabled(False)
        right_layout.addWidget(self.alternatives_combo)

        # All buttons in 2x4 grid layout (40% smaller with padding: 6px)
        button_grid = QGridLayout()
        button_style = "padding: 6px;"

        # Row 0: Accept, Change, Undo, Previous
        self.accept_btn = QPushButton("✓ Accept")
        self.accept_btn.setEnabled(False)
        self.accept_btn.setStyleSheet(button_style)
        self.accept_btn.clicked.connect(self.accept_current)
        button_grid.addWidget(self.accept_btn, 0, 0)

        self.change_btn = QPushButton("✎ Change")
        self.change_btn.setEnabled(False)
        self.change_btn.setStyleSheet(button_style)
        self.change_btn.clicked.connect(self.change_current)
        button_grid.addWidget(self.change_btn, 0, 1)

        self.undo_btn = QPushButton("↶ Undo")
        self.undo_btn.setEnabled(False)
        self.undo_btn.setStyleSheet(button_style)
        self.undo_btn.clicked.connect(self.undo_current)
        button_grid.addWidget(self.undo_btn, 0, 2)

        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setStyleSheet(button_style)
        self.prev_btn.clicked.connect(self.previous_decision)
        button_grid.addWidget(self.prev_btn, 0, 3)

        # Row 1: Next, Apply All, Cancel, (empty)
        self.next_btn = QPushButton("Next →")
        self.next_btn.setStyleSheet(button_style)
        self.next_btn.clicked.connect(self.next_decision)
        button_grid.addWidget(self.next_btn, 1, 0)

        self.apply_btn = QPushButton("Apply All Changes")
        self.apply_btn.setStyleSheet(button_style)
        self.apply_btn.clicked.connect(self.apply_changes)
        button_grid.addWidget(self.apply_btn, 1, 1)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(button_style)
        self.cancel_btn.clicked.connect(self.reject)
        button_grid.addWidget(self.cancel_btn, 1, 2)

        right_layout.addLayout(button_grid)

        splitter.addWidget(right_frame)
        splitter.setSizes([600, 600])

    def populate_decisions_list(self):
        """Populate the decisions list widget."""
        self.decisions_list.clear()

        for i, decision in enumerate(self.ai_decisions):
            word = decision["original"]
            choice = decision["choice"]
            conf = decision.get("confidence", 0.0)

            item_text = f"{i+1}. '{word}' → '{choice}' ({conf:.0%})"
            item = QListWidgetItem(item_text)

            # Mark if corrected
            if decision.get("corrected"):
                item.setBackground(QColor(255, 200, 200))  # Light red

            self.decisions_list.addItem(item)

        # Select first item
        if self.ai_decisions:
            self.decisions_list.setCurrentRow(0)
            self.update_decision_details(0)

    def on_decision_item_clicked(self, item):
        """Handle decision item click."""
        index = self.decisions_list.row(item)
        self.current_decision_index = index
        self.update_decision_details(index)
        self.highlight_current_decision()

    def update_decision_details(self, index: int):
        """Update the decision details panel."""
        if index < 0 or index >= len(self.ai_decisions):
            return

        decision = self.ai_decisions[index]

        # Update info label
        word = decision["original"]
        choice = decision["choice"]
        conf = decision.get("confidence", 0.0)
        reason = decision.get("reason", "No reason provided")

        info = f"<b>Word:</b> '{word}'<br>"
        info += f"<b>AI Chose:</b> '{choice}' <i>({conf:.0%} confidence)</i><br>"
        info += f"<b>Reason:</b> {reason}<br>"

        if decision.get("corrected"):
            info += f"<br><span style='color: red;'><b>Corrected to:</b> '{decision['correction']}'</span>"

        self.decision_info.setText(info)

        # Update alternatives dropdown
        options = decision.get("options", [])
        self.alternatives_combo.clear()

        # Add "(current)" indicator to show what AI chose
        current_choice = decision.get("correction", choice)
        labeled_options = []
        for opt in options:
            if opt == current_choice:
                labeled_options.append(f"{opt} (current)")
            else:
                labeled_options.append(opt)

        self.alternatives_combo.addItems(labeled_options)

        # Select current choice in dropdown
        idx = self.alternatives_combo.findText(f"{current_choice} (current)")
        if idx >= 0:
            self.alternatives_combo.setCurrentIndex(idx)

        # Enable controls
        self.accept_btn.setEnabled(True)
        self.change_btn.setEnabled(True)
        self.alternatives_combo.setEnabled(True)
        self.undo_btn.setEnabled(decision.get("corrected", False))

        # Update progress
        self.progress_bar.setValue(index + 1)

    def highlight_current_decision(self):
        """Highlight the current decision in text (matches caps_editor pattern)."""
        if self.current_decision_index >= len(self.ai_decisions):
            return

        decision = self.ai_decisions[self.current_decision_index]

        # Clear previous highlighting
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        format_normal = QTextCharFormat()
        cursor.setCharFormat(format_normal)

        # Position is in CURRENT (processed) text - use 'position' key like caps does
        pos = decision.get("position_in_processed", decision.get("position", 0))
        current_word = decision.get("correction", decision["choice"])
        end_pos = pos + len(current_word)

        cursor.setPosition(pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)

        format_highlight = QTextCharFormat()
        if decision.get("corrected"):
            format_highlight.setBackground(
                QColor(255, 200, 200)
            )  # Light red for corrected
        else:
            format_highlight.setBackground(
                QColor(255, 255, 150)
            )  # Yellow for AI choice

        cursor.setCharFormat(format_highlight)

        # Center in viewport
        cursor.setPosition(pos)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def _on_font_changed(self, font_family: str, font_size: int):
        """Handle font change from font controls."""
        # Update text edit widget font
        self.text_edit.setFont(QFont(font_family, font_size))

        # Save to config file
        save_font_settings(font_family, font_size)

        log_message(f"Font changed to {font_family} {font_size}pt in choices editor")

    def accept_current(self):
        """Accept the current AI decision (no learning needed)."""
        decision = self.ai_decisions[self.current_decision_index]
        decision["accepted"] = True

        log_message(
            f"Accepted AI choice: '{decision['original']}' → '{decision['choice']}'"
        )

        self.next_decision()

    def change_current(self):
        """Change the current decision to selected alternative."""
        decision = self.ai_decisions[self.current_decision_index]
        new_choice_raw = self.alternatives_combo.currentText()

        # Strip "(current)" label if present
        new_choice = new_choice_raw.replace(" (current)", "").strip()

        if not new_choice:
            QMessageBox.information(
                self, "No Selection", "Please select an option from the dropdown."
            )
            return

        # Check if it's actually different from current
        current_value = decision.get("correction", decision["choice"])
        if new_choice == current_value:
            QMessageBox.information(
                self,
                "No Change",
                f"The selected option '{new_choice}' is already the current choice.\n\n"
                "Please select a different option to make a correction.",
            )
            return

        # Record the correction
        decision["corrected"] = True
        decision["correction"] = new_choice

        # Update text directly (like caps_editor does)
        pos = decision.get("position_in_processed", decision.get("position", 0))
        old_word = decision["choice"]
        end_pos = pos + len(old_word)

        self.current_text = (
            self.current_text[:pos] + new_choice + self.current_text[end_pos:]
        )
        self.text_edit.setPlainText(self.current_text)

        # Update position for next word if length changed
        len_diff = len(new_choice) - len(old_word)
        if len_diff != 0:
            # Update positions of following decisions
            for other_decision in self.ai_decisions:
                other_pos = other_decision.get(
                    "position_in_processed", other_decision.get("position", 0)
                )
                if other_pos > pos:
                    if "position_in_processed" in other_decision:
                        other_decision["position_in_processed"] += len_diff
                    elif "position" in other_decision:
                        other_decision["position"] += len_diff

        # Record for learning (use original position from AI processing)
        self.corrections.append(
            {
                "word": decision["original"],
                "original_choice": decision["choice"],
                "correction": new_choice,
                "options": decision.get("options", []),
                "position": decision.get("original_position", 0),
            }
        )

        log_message(
            f"Corrected: '{decision['original']}' from '{decision['choice']}' to '{new_choice}'"
        )

        # Update display
        self.populate_decisions_list()
        self.decisions_list.setCurrentRow(self.current_decision_index)
        self.update_decision_details(self.current_decision_index)
        self.highlight_current_decision()

    def undo_current(self):
        """Undo correction for current decision."""
        decision = self.ai_decisions[self.current_decision_index]

        if not decision.get("corrected"):
            return

        decision["corrected"] = False
        decision.pop("correction", None)

        # Remove from corrections list
        self.corrections = [
            c
            for c in self.corrections
            if not (
                c["word"] == decision["original"]
                and c["position"] == decision["position"]
            )
        ]

        # Rebuild text
        self._rebuild_text()

        # Recalculate display positions after text change
        self._calculate_display_positions()

        # Update display
        self.populate_decisions_list()
        self.decisions_list.setCurrentRow(self.current_decision_index)
        self.update_decision_details(self.current_decision_index)
        self.highlight_current_decision()

        log_message(f"Undone correction for '{decision['original']}'")

    def _rebuild_text(self):
        """Rebuild text with all current decisions and corrections."""
        # Start with original text
        text = self.original_text

        # Sort by position (reverse to maintain indices)
        sorted_decisions = sorted(
            self.ai_decisions, key=lambda d: d["position"], reverse=True
        )

        for decision in sorted_decisions:
            pos = decision["position"]
            original = decision["original"]
            # Use correction if available, otherwise AI choice
            choice = decision.get("correction", decision["choice"])
            end_pos = pos + len(original)

            text = text[:pos] + choice + text[end_pos:]

            # Update end position
            decision["end_position"] = pos + len(choice)

        self.current_text = text
        self.text_edit.setPlainText(text)

    def _calculate_display_positions(self):
        """Recalculate display positions in current text after rebuilding."""
        # Start with original text to track position changes
        text = self.original_text

        # Sort by position to process in order
        sorted_decisions = sorted(
            self.ai_decisions, key=lambda d: d["position"]
        )

        offset = 0  # Track cumulative position offset

        for decision in sorted_decisions:
            original_pos = decision["position"]
            original_word = decision["original"]
            current_word = decision.get("correction", decision["choice"])

            # Calculate new position in current text
            new_pos = original_pos + offset
            decision["position_in_processed"] = new_pos

            # Update offset for next decision
            offset += len(current_word) - len(original_word)

    def previous_decision(self):
        """Navigate to previous decision."""
        if self.current_decision_index > 0:
            self.current_decision_index -= 1
            self.decisions_list.setCurrentRow(self.current_decision_index)
            self.update_decision_details(self.current_decision_index)
            self.highlight_current_decision()

    def next_decision(self):
        """Navigate to next decision."""
        if self.current_decision_index < len(self.ai_decisions) - 1:
            self.current_decision_index += 1
            self.decisions_list.setCurrentRow(self.current_decision_index)
            self.update_decision_details(self.current_decision_index)
            self.highlight_current_decision()

    def apply_changes(self):
        """Apply all changes and save learning data."""
        # Process corrections for learning
        if self.corrections:
            log_message(f"Processing {len(self.corrections)} corrections for learning")

            for correction in self.corrections:
                # Extract context from original text
                pos = correction["position"]
                context_start = max(0, pos - 50)
                context_end = min(
                    len(self.original_text), pos + len(correction["word"]) + 50
                )

                context_before = self.original_text[context_start:pos]
                word_end = pos + len(correction["word"])
                context_after = self.original_text[word_end:context_end]

                # Record learning
                self.learning_analyzer.add_user_decision(
                    word=correction["word"],
                    options=correction["options"],
                    context_before=context_before,
                    context_after=context_after,
                    user_choice=correction["correction"],
                    line_number=0,
                )

            QMessageBox.information(
                self,
                "Learning Saved",
                f"Saved {len(self.corrections)} corrections for future learning!",
            )

        # Emit signal with final text
        self.changes_applied.emit(self.current_text)
        self.accept()

    def get_updated_text(self) -> str:
        """Get the final updated text."""
        return self.current_text

    def get_corrections_count(self) -> int:
        """Get number of corrections made."""
        return len(self.corrections)
