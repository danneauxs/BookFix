"""
Caps Review Editor Widget for Bookfix.

Review window for AI all-caps decisions with multiple action options and learning capabilities.
"""

import re
from typing import List, Dict, Tuple, Optional, TYPE_CHECKING
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
    QGroupBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor

if TYPE_CHECKING:
    from ..context import BookfixContext

from ..logging import log_message
from ..ai.caps_learning import CapsLearningStorage
from ..datafile import save_font_settings
from .font_controls import FontControlsWidget


class CapsReviewEditor(QDialog):
    """
    Interactive caps review editor for AI all-caps decisions.

    Provides 8 action options:
    - ADD: Add to CAP_IGNORE (keep as-is forever)
    - SKIP: Skip this occurrence
    - SKIP ALL: Skip all occurrences in document
    - LOWER: Lowercase this occurrence
    - LOWER ALL: Lowercase all occurrences in document
    - TITLE: Title case this occurrence
    - TITLE ALL: Title case all occurrences in document
    - LOWER ADD: Add to UPPER_TO_LOWER (always lowercase)
    """

    changes_applied = pyqtSignal(str, dict)  # (final_text, learning_data)

    def __init__(
        self,
        text: str,
        caps_sequences: List[Dict],
        cap_ignore_list: List[str],
        parent=None,
    ):
        """
        Initialize caps review editor.

        Args:
            text: The original text with all-caps sequences
            caps_sequences: List of caps decision dicts with keys:
                          'caps', 'original', 'suggestion', 'position', 'context_before',
                          'context_after', 'confidence', 'reasoning'
            cap_ignore_list: Current CAP_IGNORE list
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_text = text
        self.caps_sequences = caps_sequences
        self.cap_ignore_list = set(cap_ignore_list)

        # Track decisions
        self.current_index = 0
        self.decisions = {}  # caps_word -> decision_dict
        self.skip_all_set = set()  # Words to skip all occurrences

        # Learning data to return
        self.to_add_cap_ignore = []  # ADD choices
        self.to_add_upper_to_lower = []  # LOWER ADD choices

        # Initialize learning storage for tracking decisions
        self.learning_storage = CapsLearningStorage()

        self.setup_ui()
        self.populate_sequences_list()
        if self.caps_sequences:
            self.show_sequence(0)

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("All-Caps Sequences Review")
        self.setModal(True)
        self.resize(1400, 800)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Info label
        info_text = (
            f"Review {len(self.caps_sequences)} all-caps sequences. "
            "Choose action for each."
        )
        self.info_label = QLabel(info_text)
        self.info_label.setStyleSheet("font-size: 12pt; padding: 10px;")
        main_layout.addWidget(self.info_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.caps_sequences))
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Main splitter (left/right panels)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Text view
        left_frame = self._create_text_panel()
        splitter.addWidget(left_frame)

        # Right panel - Sequence info and action buttons
        right_frame = self._create_control_panel()
        splitter.addWidget(right_frame)

        splitter.setSizes([800, 600])

        # Bottom buttons
        bottom_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply All Decisions and Continue")
        self.apply_btn.setStyleSheet(
            "font-size: 11pt; padding: 10px; background-color: #4CAF50; color: white;"
        )
        self.apply_btn.clicked.connect(self.apply_changes)
        bottom_layout.addWidget(self.apply_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("font-size: 11pt; padding: 10px;")
        self.cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(bottom_layout)

    def _create_text_panel(self) -> QFrame:
        """Create left panel with text view."""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Header with title and font controls
        header_layout = QHBoxLayout()
        label = QLabel("Text with Caps Highlighted:")
        label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(label)

        # Add font controls
        self.font_controls = FontControlsWidget(initial_family="Arial", initial_size=12)
        self.font_controls.font_changed.connect(self._on_font_changed)
        header_layout.addWidget(self.font_controls)

        layout.addLayout(header_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Arial", 12))
        layout.addWidget(self.text_edit)

        return frame

    def _create_control_panel(self) -> QFrame:
        """Create right panel with controls."""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Sequences list
        list_label = QLabel("Caps Sequences:")
        list_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(list_label)

        self.sequences_list = QListWidget()
        self.sequences_list.itemClicked.connect(self.on_sequence_item_clicked)
        layout.addWidget(self.sequences_list)

        # Current sequence info
        self.sequence_info_box = QGroupBox("Current Sequence")
        info_layout = QVBoxLayout()

        self.caps_label = QLabel()
        self.caps_label.setStyleSheet(
            "font-size: 16pt; font-weight: bold; color: #2196F3;"
        )
        info_layout.addWidget(self.caps_label)

        self.context_label = QTextEdit()
        self.context_label.setReadOnly(True)
        self.context_label.setMaximumHeight(80)
        self.context_label.setStyleSheet(
            "padding: 5px; background-color: #f5f5f5; border: 1px solid #ddd;"
        )
        info_layout.addWidget(self.context_label)

        self.ai_suggestion_label = QTextEdit()
        self.ai_suggestion_label.setReadOnly(True)
        self.ai_suggestion_label.setMaximumHeight(100)
        self.ai_suggestion_label.setStyleSheet(
            "padding: 5px; background-color: #fff3cd; border: 1px solid #ffc107;"
        )
        info_layout.addWidget(self.ai_suggestion_label)

        self.sequence_info_box.setLayout(info_layout)
        layout.addWidget(self.sequence_info_box)

        # Action buttons
        actions_label = QLabel("Choose Action:")
        actions_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(actions_label)

        layout.addWidget(self._create_action_buttons())

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self.previous_sequence)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.next_sequence)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        return frame

    def _create_action_buttons(self) -> QGroupBox:
        """Create action buttons group - 9 buttons with Accept AI integrated."""
        group = QGroupBox()
        layout = QVBoxLayout()

        # Row 0: Accept AI, ADD, SKIP, SKIP ALL
        row0 = QHBoxLayout()

        self.accept_ai_btn = QPushButton("Accept AI")
        self.accept_ai_btn.setStyleSheet(
            "padding: 4px; background-color: #27AE60; color: white; font-weight: bold;"
        )
        self.accept_ai_btn.clicked.connect(lambda: self.apply_action("accept"))
        row0.addWidget(self.accept_ai_btn)

        self.add_btn = QPushButton("ADD\n(to CAP_IGNORE)")
        self.add_btn.setStyleSheet(
            "padding: 4px; background-color: #4CAF50; color: white;"
        )
        self.add_btn.clicked.connect(lambda: self.apply_action("add"))
        row0.addWidget(self.add_btn)

        self.skip_btn = QPushButton("SKIP\n(once)")
        self.skip_btn.setStyleSheet(
            "padding: 4px; background-color: #9E9E9E; color: white;"
        )
        self.skip_btn.clicked.connect(lambda: self.apply_action("skip"))
        row0.addWidget(self.skip_btn)

        self.skip_all_btn = QPushButton("SKIP ALL\n(in document)")
        self.skip_all_btn.setStyleSheet(
            "padding: 4px; background-color: #757575; color: white;"
        )
        self.skip_all_btn.clicked.connect(lambda: self.apply_action("skip_all"))
        row0.addWidget(self.skip_all_btn)

        layout.addLayout(row0)

        # Row 1: LOWER, LOWER ALL, LOWER ADD, TITLE
        row1 = QHBoxLayout()

        self.lower_btn = QPushButton("LOWER\n(once)")
        self.lower_btn.setStyleSheet(
            "padding: 4px; background-color: #2196F3; color: white;"
        )
        self.lower_btn.clicked.connect(lambda: self.apply_action("lower"))
        row1.addWidget(self.lower_btn)

        self.lower_all_btn = QPushButton("LOWER ALL\n(in document)")
        self.lower_all_btn.setStyleSheet(
            "padding: 4px; background-color: #1976D2; color: white;"
        )
        self.lower_all_btn.clicked.connect(lambda: self.apply_action("lower_all"))
        row1.addWidget(self.lower_all_btn)

        self.lower_add_btn = QPushButton("LOWER ADD\n(to UPPER_TO_LOWER)")
        self.lower_add_btn.setStyleSheet(
            "padding: 4px; background-color: #0D47A1; color: white;"
        )
        self.lower_add_btn.clicked.connect(lambda: self.apply_action("lower_add"))
        row1.addWidget(self.lower_add_btn)

        self.title_btn = QPushButton("TITLE\n(once)")
        self.title_btn.setStyleSheet(
            "padding: 4px; background-color: #FF9800; color: white;"
        )
        self.title_btn.clicked.connect(lambda: self.apply_action("title"))
        row1.addWidget(self.title_btn)

        layout.addLayout(row1)

        # Row 2: TITLE ALL
        row2 = QHBoxLayout()

        self.title_all_btn = QPushButton("TITLE ALL\n(in document)")
        self.title_all_btn.setStyleSheet(
            "padding: 4px; background-color: #F57C00; color: white;"
        )
        self.title_all_btn.clicked.connect(lambda: self.apply_action("title_all"))
        row2.addWidget(self.title_all_btn)

        # Add stretch to balance row
        row2.addStretch()

        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    def populate_sequences_list(self):
        """Populate the sequences list widget."""
        self.sequences_list.clear()

        for i, seq in enumerate(self.caps_sequences):
            caps = seq["caps"]

            # Check if already in CAP_IGNORE
            # Get AI suggestion
            suggestion = seq.get("suggestion", "keep").lower()
            # Format: "CAPS -> suggested_form"
            if suggestion == "lowercase":
                suggested_form = caps.lower()
            elif suggestion in ["keep", "spell", "spell out"]:
                suggested_form = caps  # Keep as-is
            else:
                suggested_form = caps

            if caps in self.cap_ignore_list:
                status = "[IN CAP_IGNORE]"
                item_text = f"{i+1}. {caps} {status}"
                item = QListWidgetItem(item_text)
                item.setBackground(QColor(200, 255, 200))  # Light green
            else:
                item_text = f"{i+1}. {caps} → {suggested_form}"
                item = QListWidgetItem(item_text)

            # Mark if decision made for this specific instance
            decision_key = (caps, seq["position"])
            if decision_key in self.decisions:
                action = self.decisions[decision_key]["action"]
                item.setForeground(QColor(100, 100, 100))  # Gray
                # Show [ACCEPT] for accept action instead of the converted action
                if action == "accept":
                    item_text += " [ACCEPT]"
                else:
                    item_text += f" [{action.upper()}]"
                item.setText(item_text)

            self.sequences_list.addItem(item)

        # Select first item
        if self.caps_sequences:
            self.sequences_list.setCurrentRow(0)

    def _on_font_changed(self, font_family: str, font_size: int):
        """Handle font change from font controls."""
        # Update text edit widget font
        self.text_edit.setFont(QFont(font_family, font_size))

        # Save to config file
        save_font_settings(font_family, font_size)

        log_message(
            f"Font changed to {font_family} {font_size}pt in caps review editor"
        )

    def show_sequence(self, index: int):
        """Display sequence at given index."""
        if index < 0 or index >= len(self.caps_sequences):
            return

        self.current_index = index
        seq = self.caps_sequences[index]

        caps = seq["caps"]
        before = seq["context_before"]
        after = seq["context_after"]
        suggestion = seq.get("suggestion", "Keep as-is")
        confidence = seq.get("confidence", 0.0)
        reasoning = seq.get("reasoning", "No reasoning provided")

        # Update labels
        self.caps_label.setText(f"Caps: {caps}")
        self.context_label.setPlainText(f"Context: ...{before} [{caps}] {after}...")
        self.ai_suggestion_label.setPlainText(
            f"AI Suggests: {suggestion}\n"
            f"Confidence: {confidence:.1%}\n"
            f"Reasoning: {reasoning}"
        )

        # Update progress
        self.progress_bar.setValue(index + 1)

        # Highlight in text
        self.highlight_current_sequence()

        # Update navigation buttons
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.caps_sequences) - 1)

    def highlight_current_sequence(self):
        """Highlight current sequence in text view, showing user's choice or AI suggestion."""
        seq = self.caps_sequences[self.current_index]
        caps = seq["caps"]
        suggestion = seq.get("suggestion", "keep").lower()
        context_before = seq.get("context_before", "")
        context_after = seq.get("context_after", "")

        # Check if user has made a decision for this specific instance
        decision_key = (caps, seq["position"])
        if decision_key in self.decisions:
            # Show user's decision instead of AI suggestion
            action = self.decisions[decision_key].get("actual_action", self.decisions[decision_key]["action"])
            if action in ["lower", "lower_add"]:
                display_word = caps.lower()
            elif action == "title":
                display_word = caps.title()
            else:  # skip, add, accept
                display_word = caps
        else:
            # No decision yet - show AI suggestion
            if suggestion == "lowercase":
                display_word = caps.lower()
            elif suggestion == "title":
                display_word = caps.title()
            else:  # 'keep', 'spell', etc.
                display_word = caps

        # Build context display with the suggested word
        display_text = f"...{context_before} [{display_word}] {context_after}..."

        # Set text to context only
        self.text_edit.setPlainText(display_text)

        # Calculate position of the word in the context display
        highlight_start = len(f"...{context_before} [")
        highlight_end = highlight_start + len(display_word)

        # Highlight the word
        cursor = self.text_edit.textCursor()
        cursor.setPosition(highlight_start)
        cursor.setPosition(highlight_end, QTextCursor.KeepAnchor)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor(255, 255, 0))  # Yellow
        fmt.setFontWeight(QFont.Bold)

        # Use mergeCharFormat; it's safer for applying formats to selections
        # without affecting the cursor's own format state.
        cursor.mergeCharFormat(fmt)

        # Move cursor to the start of the selection to ensure it's visible
        # and to leave the cursor in a non-selected state.
        cursor.setPosition(highlight_start)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def apply_action(self, action: str):
        """Apply chosen action to current sequence."""
        seq = self.caps_sequences[self.current_index]
        caps = seq["caps"]

        # If action is 'accept', apply the AI's suggestion
        if action == "accept":
            suggestion = seq.get("suggestion", "keep").lower()
            # Map AI suggestion to actual action
            if suggestion == "lowercase":
                converted_action = "lower"
            elif suggestion in ["keep", "spell out", "spell"]:
                converted_action = "skip"
            else:
                converted_action = "skip"  # Default to skip if unclear
            log_message(
                f"Accepting AI suggestion '{suggestion}' for '{caps}' → will apply '{converted_action}' action"
            )
            # Store "accept" as the action for display purposes
            # But remember the converted action for actual text processing
            action_to_store = "accept"
            action_to_apply = converted_action
        else:
            action_to_store = action
            action_to_apply = action

        log_message(f"Action '{action_to_store}' chosen for caps '{caps}' at position {seq['position']}")

        # Store decision with (caps, position) tuple as key for per-instance markers
        decision_key = (caps, seq["position"])
        self.decisions[decision_key] = {
            "action": action_to_store,  # For display ([ACCEPT] marker)
            "actual_action": action_to_apply,  # For text processing
            "position": seq["position"],
            "original": caps,
        }

        # Handle special actions (use action_to_apply for actual processing)
        if action_to_apply == "add":
            if caps not in self.to_add_cap_ignore:
                self.to_add_cap_ignore.append(caps)
            log_message(f"Will add '{caps}' to CAP_IGNORE")

            # Mark ALL instances of this caps word as decided
            for idx, other_seq in enumerate(self.caps_sequences):
                if other_seq['caps'].upper() == caps.upper():
                    decision_key = (caps, other_seq["position"])
                    self.decisions[decision_key] = {
                        "action": "add",
                        "actual_action": "skip",  # Will be ignored since it's in CAP_IGNORE
                        "position": other_seq["position"],
                        "original": caps,
                    }
            log_message(f"Marked all instances of '{caps}' as add (CAP_IGNORE)")

        elif action_to_apply == "lower_add":
            if caps not in self.to_add_upper_to_lower:
                self.to_add_upper_to_lower.append(caps)
            log_message(f"Will add '{caps}' to UPPER_TO_LOWER")

            # Mark ALL instances of this caps word as decided
            for idx, other_seq in enumerate(self.caps_sequences):
                if other_seq['caps'].upper() == caps.upper():
                    decision_key = (caps, other_seq["position"])
                    self.decisions[decision_key] = {
                        "action": "lower_add",
                        "actual_action": "lower",  # Will be lowercased
                        "position": other_seq["position"],
                        "original": caps,
                    }
            log_message(f"Marked all instances of '{caps}' as lower_add (UPPER_TO_LOWER)")

        elif action_to_apply == "skip_all":
            self.skip_all_set.add(caps)
            log_message(f"Will skip all instances of '{caps}' in document")

            # Mark ALL instances of this caps word as decided
            for idx, other_seq in enumerate(self.caps_sequences):
                if other_seq['caps'].upper() == caps.upper():
                    decision_key = (caps, other_seq["position"])
                    self.decisions[decision_key] = {
                        "action": "skip_all",
                        "actual_action": "skip",
                        "position": other_seq["position"],
                        "original": caps,
                    }
            log_message(f"Marked all instances of '{caps}' as skip_all")

        elif action_to_apply == "lower_all":
            log_message(f"Will lowercase all instances of '{caps}' in document")

            # Mark ALL instances of this caps word as decided
            for idx, other_seq in enumerate(self.caps_sequences):
                if other_seq['caps'].upper() == caps.upper():
                    decision_key = (caps, other_seq["position"])
                    self.decisions[decision_key] = {
                        "action": "lower_all",
                        "actual_action": "lower",
                        "position": other_seq["position"],
                        "original": caps,
                    }
            log_message(f"Marked all instances of '{caps}' as lower_all")

        elif action_to_apply == "title_all":
            log_message(f"Will title case all instances of '{caps}' in document")

            # Mark ALL instances of this caps word as decided
            for idx, other_seq in enumerate(self.caps_sequences):
                if other_seq['caps'].upper() == caps.upper():
                    decision_key = (caps, other_seq["position"])
                    self.decisions[decision_key] = {
                        "action": "title_all",
                        "actual_action": "title",
                        "position": other_seq["position"],
                        "original": caps,
                    }
            log_message(f"Marked all instances of '{caps}' as title_all")

        # Save decision to learning storage (for future reference)
        try:
            # Map action back to learning decision format (use actual_action)
            learning_decision = (
                "lowercase" if action_to_apply in ["lower", "lower_add"] else "keep"
            )
            ai_suggestion = seq.get("suggestion", "keep")

            # Add decision to learning storage
            self.learning_storage.add_decision(
                caps_word=caps,
                decision=learning_decision,
                context_before=seq.get("context_before", ""),
                context_after=seq.get("context_after", ""),
                ai_suggestion=ai_suggestion,
                line_number=0,
            )
            self.learning_storage.save()
            log_message(f"Learned: '{caps}' → {learning_decision}")
        except Exception as e:
            log_message(
                f"Error saving learning entry for '{caps}': {e}", level="WARNING"
            )

        # Update list display
        self.populate_sequences_list()

        # Auto-advance to next
        self.next_sequence()

    def next_sequence(self):
        """Move to next unflagged sequence."""
        # Find next unflagged item
        for next_idx in range(self.current_index + 1, len(self.caps_sequences)):
            seq = self.caps_sequences[next_idx]
            decision_key = (seq['caps'], seq['position'])
            # Skip if this item already has a decision
            if decision_key not in self.decisions:
                self.show_sequence(next_idx)
                self.sequences_list.setCurrentRow(next_idx)
                return
        # If no unflagged items found, stay on current
        log_message("No more unflagged sequences")

    def previous_sequence(self):
        """Move to previous unflagged sequence."""
        # Find previous unflagged item
        for prev_idx in range(self.current_index - 1, -1, -1):
            seq = self.caps_sequences[prev_idx]
            decision_key = (seq['caps'], seq['position'])
            # Skip if this item already has a decision
            if decision_key not in self.decisions:
                self.show_sequence(prev_idx)
                self.sequences_list.setCurrentRow(prev_idx)
                return
        # If no unflagged items found, stay on current
        log_message("No more unflagged sequences before current")

    def on_sequence_item_clicked(self, item):
        """Handle sequence list item click."""
        row = self.sequences_list.row(item)
        self.show_sequence(row)

    def apply_changes(self):
        """Apply all decisions and emit signal."""
        # Apply changes to text
        modified_text = self.current_text

        # Process decisions in reverse position order to maintain positions
        # decisions is now keyed by (caps, position) tuples
        sorted_decisions = sorted(
            [
                (decision["position"], decision["original"], decision)
                for decision in self.decisions.values()
            ],
            key=lambda x: x[0],
            reverse=True,
        )

        for position, caps, decision in sorted_decisions:
            # Use actual_action for text processing (defaults to action if not present)
            action = decision.get("actual_action", decision["action"])

            if action == "skip" or action == "add":
                # Leave as-is
                continue

            elif action in ("skip_all",):
                # Skip if in skip_all set
                if caps in self.skip_all_set:
                    continue

            elif action == "lower" or action == "lower_add":
                replacement = caps.lower()
                modified_text = (
                    modified_text[:position]
                    + replacement
                    + modified_text[position + len(caps) :]
                )

            elif action == "lower_all":
                # Replace all instances of this caps word
                modified_text = re.sub(
                    r"\b" + re.escape(caps) + r"\b", caps.lower(), modified_text
                )

            elif action == "title":
                replacement = caps.title()
                modified_text = (
                    modified_text[:position]
                    + replacement
                    + modified_text[position + len(caps) :]
                )

            elif action == "title_all":
                # Replace all instances of this caps word
                modified_text = re.sub(
                    r"\b" + re.escape(caps) + r"\b", caps.title(), modified_text
                )

        # Prepare learning data
        learning_data = {
            "to_add_cap_ignore": self.to_add_cap_ignore,
            "to_add_upper_to_lower": self.to_add_upper_to_lower,
        }

        log_message(f"Caps review complete. Decisions: {len(self.decisions)}")
        log_message(f"To add to CAP_IGNORE: {self.to_add_cap_ignore}")
        log_message(f"To add to UPPER_TO_LOWER: {self.to_add_upper_to_lower}")

        # Emit signal with results
        self.changes_applied.emit(modified_text, learning_data)

        self.accept()
