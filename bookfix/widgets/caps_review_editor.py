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
    QLineEdit,
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
from .font_controls import FontControlsWidget
from ..ai.review_window import save_font_settings
from ..processors.roman import roman_to_arabic


class CapsReviewEditor(QDialog):
    """
    Interactive caps review editor for AI all-caps decisions.

    Provides 9 action options plus keyboard number shortcuts (0-9):
    - 1: ACCEPT: Accept AI suggestion or custom edit
    - 0: SKIP: Skip this occurrence
    - 5: SKIP ALL: Skip all occurrences in document
    - 2: LOWER: Lowercase this occurrence
    - 3: LOWER ALL: Lowercase all occurrences in document
    - 4: ADD: Add to CAP_IGNORE (keep as-is forever)
    - 6: LOWER ADD: Add to UPPER_TO_LOWER (always lowercase)
    - 7: HYPHEN: Insert hyphens between letters (GHR → G-H-R)
    - 8: ROMAN: Convert to Arabic numeral (if valid Roman)
    - 9: HYPHEN ALL: Hyphenate all occurrences in document
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

        edit_label = QLabel("Replacement (editable):")
        edit_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        info_layout.addWidget(edit_label)

        self.word_edit_box = QLineEdit()
        self.word_edit_box.setStyleSheet("font-size: 13pt; padding: 4px;")
        info_layout.addWidget(self.word_edit_box)

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

        # Row 0: Accept, ADD, SKIP, SKIP ALL
        row0 = QHBoxLayout()

        self.accept_ai_btn = QPushButton("1) Accept")
        self.accept_ai_btn.setStyleSheet(
            "padding: 4px; background-color: #27AE60; color: white; font-weight: bold;"
        )
        self.accept_ai_btn.clicked.connect(lambda: self.apply_action("accept"))
        row0.addWidget(self.accept_ai_btn)

        self.add_btn = QPushButton("4) ADD\n(to CAP_IGNORE)")
        self.add_btn.setStyleSheet(
            "padding: 4px; background-color: #4CAF50; color: white;"
        )
        self.add_btn.clicked.connect(lambda: self.apply_action("add"))
        row0.addWidget(self.add_btn)

        self.skip_btn = QPushButton("0) SKIP\n(once)")
        self.skip_btn.setStyleSheet(
            "padding: 4px; background-color: #9E9E9E; color: white;"
        )
        self.skip_btn.clicked.connect(lambda: self.apply_action("skip"))
        row0.addWidget(self.skip_btn)

        self.skip_all_btn = QPushButton("5) SKIP ALL\n(in document)")
        self.skip_all_btn.setStyleSheet(
            "padding: 4px; background-color: #757575; color: white;"
        )
        self.skip_all_btn.clicked.connect(lambda: self.apply_action("skip_all"))
        row0.addWidget(self.skip_all_btn)

        layout.addLayout(row0)

        # Row 1: LOWER, LOWER ALL, LOWER ADD, TITLE
        row1 = QHBoxLayout()

        self.lower_btn = QPushButton("2) LOWER\n(once)")
        self.lower_btn.setStyleSheet(
            "padding: 4px; background-color: #2196F3; color: white;"
        )
        self.lower_btn.clicked.connect(lambda: self.apply_action("lower"))
        row1.addWidget(self.lower_btn)

        self.lower_all_btn = QPushButton("3) LOWER ALL\n(in document)")
        self.lower_all_btn.setStyleSheet(
            "padding: 4px; background-color: #1976D2; color: white;"
        )
        self.lower_all_btn.clicked.connect(lambda: self.apply_action("lower_all"))
        row1.addWidget(self.lower_all_btn)

        self.lower_add_btn = QPushButton("6) LOWER ADD\n(to UPPER_TO_LOWER)")
        self.lower_add_btn.setStyleSheet(
            "padding: 4px; background-color: #0D47A1; color: white;"
        )
        self.lower_add_btn.clicked.connect(lambda: self.apply_action("lower_add"))
        row1.addWidget(self.lower_add_btn)

        layout.addLayout(row1)

        # Row 2: ROMAN, HYPHEN, HYPHEN ALL
        row2 = QHBoxLayout()

        self.roman_btn = QPushButton("8) ROMAN\n(to Arabic)")
        self.roman_btn.setStyleSheet(
            "QPushButton { padding: 4px; background-color: #9C27B0; color: white; } "
            "QPushButton:disabled { background-color: #CCCCCC; color: #999999; }"
        )
        self.roman_btn.clicked.connect(self.on_roman_clicked)
        row2.addWidget(self.roman_btn)

        self.hyphen_btn = QPushButton("7) HYPHEN\n(G-H-R, once)")
        self.hyphen_btn.setStyleSheet(
            "padding: 4px; background-color: #E65100; color: white;"
        )
        self.hyphen_btn.clicked.connect(lambda: self.apply_action("hyphen"))
        row2.addWidget(self.hyphen_btn)

        self.hyphen_all_btn = QPushButton("9) HYPHEN ALL\n(in document)")
        self.hyphen_all_btn.setStyleSheet(
            "padding: 4px; background-color: #BF360C; color: white;"
        )
        self.hyphen_all_btn.clicked.connect(lambda: self.apply_action("hyphen_all"))
        row2.addWidget(self.hyphen_all_btn)

        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    @staticmethod
    def _hyphenate(word: str) -> str:
        """Insert hyphens between every letter so TTS reads each letter individually (GHR → G-H-R)."""
        return "-".join(list(word))

    def populate_sequences_list(self):
        """Populate the sequences list widget."""
        self.sequences_list.clear()

        for i, seq in enumerate(self.caps_sequences):
            caps = seq["caps"]
            decision_key = (caps, seq["position"])

            # Determine what the result will be based on decision or AI suggestion
            if decision_key in self.decisions:
                # Decision made - show actual result
                decision = self.decisions[decision_key]
                actual_action = decision.get("actual_action", decision["action"])

                if actual_action == "skip" or actual_action == "add":
                    result_form = caps  # Keep original
                elif actual_action == "lower" or actual_action == "lower_add":
                    result_form = caps.lower()
                elif actual_action == "edit":
                    result_form = decision.get("edited_text", caps)
                elif actual_action == "hyphen":
                    result_form = self._hyphenate(caps)
                else:
                    result_form = caps
            else:
                # No decision yet - show AI suggestion
                suggestion = seq.get("suggestion", "keep").lower()
                if suggestion == "lowercase":
                    result_form = caps.lower()
                elif suggestion in ["keep", "spell", "spell out"]:
                    result_form = caps
                else:
                    result_form = caps

            # Format item text
            if caps in self.cap_ignore_list:
                status = "[IN CAP_IGNORE]"
                item_text = f"{i+1}. {caps} {status}"
                item = QListWidgetItem(item_text)
                item.setBackground(QColor(200, 255, 200))  # Light green
            else:
                item_text = f"{i+1}. {caps} → {result_form}"
                item = QListWidgetItem(item_text)

            # Mark if decision made - add action label
            if decision_key in self.decisions:
                decision = self.decisions[decision_key]
                action = decision["action"]

                if action == "accept":
                    item_text += " [ACCEPT]"
                elif action == "edit":
                    item_text += " [EDIT]"
                elif action == "skip":
                    item_text += " [SKIP]"
                elif action == "skip_all":
                    item_text += " [SKIP ALL]"
                elif action == "add":
                    item_text += " [ADD]"
                elif action == "lower":
                    item_text += " [LOWER]"
                elif action == "lower_all":
                    item_text += " [LOWER ALL]"
                elif action == "lower_add":
                    item_text += " [LOWER ADD]"
                elif action in ("hyphen", "hyphen_all"):
                    item_text += " [HYPHEN]"

                item.setText(item_text)
                item.setForeground(QColor(100, 100, 100))  # Gray for decided items

            self.sequences_list.addItem(item)

        # Select first undecided item
        if self.caps_sequences:
            for i, seq in enumerate(self.caps_sequences):
                decision_key = (seq["caps"], seq["position"])
                if decision_key not in self.decisions:
                    self.sequences_list.setCurrentRow(i)
                    return
            # If all decided, select first
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

        # Update labels
        self.caps_label.setText(f"Caps: {caps}")

        # Pre-populate edit box with converted AI suggestion
        if suggestion.lower() == "lowercase":
            self.word_edit_box.setText(caps.lower())
        else:  # keep, title (now ignored), spell, spell out, or unknown
            self.word_edit_box.setText(caps)

        # Update progress
        self.progress_bar.setValue(index + 1)

        # Highlight in text
        self.highlight_current_sequence()

        # Update navigation buttons
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.caps_sequences) - 1)

        # Enable/disable Roman button based on validity
        is_valid_roman = roman_to_arabic(caps) is not None
        self.roman_btn.setEnabled(is_valid_roman)

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
            elif action == "edit":
                display_word = self.decisions[decision_key].get("edited_text", caps)
            elif action == "hyphen":
                display_word = self._hyphenate(caps)
            else:  # skip, add, accept
                display_word = caps
        else:
            # No decision yet - show AI suggestion
            if suggestion == "lowercase":
                display_word = caps.lower()
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

        # Check if this is a sound effect - use orange highlighting, otherwise yellow
        is_sound_effect = seq.get("is_sound_effect", False)
        if is_sound_effect:
            fmt.setBackground(QColor(255, 165, 0))  # Orange
        else:
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

        # If action is 'accept', check if user edited the text
        if action == "accept":
            edited_text = self.word_edit_box.text().strip()
            if edited_text and edited_text != caps:
                # User changed the text — treat as custom edit
                action_to_store = "accept"
                action_to_apply = "edit"
                log_message(f"User edited '{caps}' to '{edited_text}'")
                self.decisions[(caps, seq["position"])] = {
                    "action": "accept",
                    "actual_action": "edit",
                    "position": seq["position"],
                    "original": caps,
                    "edited_text": edited_text,
                }
            else:
                # Unchanged — skip (keep as-is)
                action_to_store = "accept"
                action_to_apply = "skip"
                log_message(f"Accept (unchanged) for '{caps}'")
                self.decisions[(caps, seq["position"])] = {
                    "action": "accept",
                    "actual_action": "skip",
                    "position": seq["position"],
                    "original": caps,
                }
        else:
            action_to_store = action
            action_to_apply = action
            log_message(f"Action '{action_to_store}' chosen for caps '{caps}' at position {seq['position']}")

            # Store decision with (caps, position) tuple as key for per-instance markers
            decision_key = (caps, seq["position"])
            self.decisions[decision_key] = {
                "action": action_to_store,
                "actual_action": action_to_apply,
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

        elif action_to_apply == "hyphen_all":
            log_message(f"Will hyphenate all instances of '{caps}' in document")

            # Mark ALL instances of this caps word as decided
            for idx, other_seq in enumerate(self.caps_sequences):
                if other_seq['caps'].upper() == caps.upper():
                    decision_key = (caps, other_seq["position"])
                    self.decisions[decision_key] = {
                        "action": "hyphen_all",
                        "actual_action": "hyphen",
                        "position": other_seq["position"],
                        "original": caps,
                    }
            log_message(f"Marked all instances of '{caps}' as hyphen_all")

        # Update list display
        self.populate_sequences_list()

        # Auto-advance to next
        self.next_sequence()

    def on_roman_clicked(self):
        """Convert current caps word to Roman numeral if valid."""
        if self.current_index < 0 or self.current_index >= len(self.caps_sequences):
            return

        seq = self.caps_sequences[self.current_index]
        caps = seq["caps"]

        # Try to convert to Arabic
        arabic = roman_to_arabic(caps)
        if arabic is not None:
            # Valid Roman numeral — show Arabic number in edit box
            self.word_edit_box.setText(str(arabic))
            log_message(f"Roman: '{caps}' → {arabic}")
        else:
            # Not a valid Roman numeral — no change
            log_message(f"'{caps}' is not a valid Roman numeral")

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

            elif action == "edit":
                # Replace with edited text
                edited_text = decision.get("edited_text", caps)
                modified_text = (
                    modified_text[:position]
                    + edited_text
                    + modified_text[position + len(caps) :]
                )
                log_message(f"Applied edit: '{caps}' → '{edited_text}' at position {position}")

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

            elif action == "hyphen":
                replacement = self._hyphenate(caps)
                modified_text = (
                    modified_text[:position]
                    + replacement
                    + modified_text[position + len(caps):]
                )
                log_message(f"Applied hyphen: '{caps}' → '{replacement}' at position {position}")

        # Prepare learning data
        learning_data = {
            "to_add_cap_ignore": self.to_add_cap_ignore,
            "to_add_upper_to_lower": self.to_add_upper_to_lower,
        }

        log_message(f"Caps review complete. Decisions: {len(self.decisions)}")
        log_message(f"To add to CAP_IGNORE: {self.to_add_cap_ignore}")
        log_message(f"To add to UPPER_TO_LOWER: {self.to_add_upper_to_lower}")

        # Save all decisions to learning storage (only when Apply is clicked)
        try:
            from ai.caps_learning import CapsLearningEntry
            for position, caps, decision in sorted_decisions:
                action = decision.get("actual_action", decision["action"])

                # Find the sequence to get context + AI suggestion
                context_before = ""
                context_after = ""
                ai_suggestion = "keep"
                for seq in self.caps_sequences:
                    if seq["caps"] == caps and seq["position"] == position:
                        ai_suggestion = seq.get("suggestion", "keep")
                        context_before = seq.get("context_before", "")
                        context_after = seq.get("context_after", "")
                        break

                # Determine learning decision based on what the word BECAME, not which button was pressed
                learning_decision = None

                if action in ["lower", "lower_add"]:
                    learning_decision = "lowercase"
                elif action == "edit":
                    # User changed the text — check what it became
                    edited_text = decision.get("edited_text", caps)
                    if edited_text == caps.lower():
                        learning_decision = "lowercase"
                    # else: truly custom edit (e.g., IIV → 3) — don't save
                elif action == "hyphen":
                    # Stays as letters (hyphenated) — treat as keep for learning
                    learning_decision = "keep"
                elif action in ["skip", "skip_all", "add"]:
                    learning_decision = "keep"
                else:
                    learning_decision = "keep"

                # Only save if we have a valid learning decision
                if learning_decision is not None:
                    entry = CapsLearningEntry.create(
                        caps_word=caps,
                        decision=learning_decision,
                        context_before=context_before,
                        context_after=context_after,
                        ai_suggestion=ai_suggestion,
                        line_number=0,
                    )
                    self.learning_storage.entries.append(entry)

            # Save all at once
            self.learning_storage.save()
            log_message(f"Saved {len(self.decisions)} decisions to learning storage")
        except Exception as e:
            log_message(f"Error saving learning data: {e}", level="WARNING")

        # For captest: save modified text to output file
        try:
            output_path = getattr(self, 'output_file_path', None)
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(modified_text)
                log_message(f"Saved output to {output_path}")
        except Exception as e:
            log_message(f"Error saving output file: {e}", level="WARNING")

        # Emit signal with results
        self.changes_applied.emit(modified_text, learning_data)

        self.accept()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for button actions."""
        # If edit box has focus, pass through normally (allow typing)
        if self.word_edit_box.hasFocus():
            super().keyPressEvent(event)
            return

        # Map digit keys to button actions
        key_map = {
            Qt.Key_0: self.skip_btn,
            Qt.Key_1: self.accept_ai_btn,
            Qt.Key_2: self.lower_btn,
            Qt.Key_3: self.lower_all_btn,
            Qt.Key_4: self.add_btn,
            Qt.Key_5: self.skip_all_btn,
            Qt.Key_6: self.lower_add_btn,
            Qt.Key_7: self.hyphen_btn,
            Qt.Key_8: self.roman_btn,
            Qt.Key_9: self.hyphen_all_btn,
        }

        if event.key() in key_map:
            btn = key_map[event.key()]
            if btn.isEnabled():
                btn.click()
                event.accept()
            return

        # Other keys — pass through
        super().keyPressEvent(event)
