"""
Caps Review Editor Widget for Bookfix.

Left/right panel design for reviewing AI-processed ALL CAPS text with
buttons for LOWER, LOWER ALL, SKIP, IGNORE ALL, ADD functionality.
"""

import re
from typing import List, Tuple, Set, Optional
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
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor

from ..logging import log_message
from ..ai.learning_storage import LearningStorage
from ..ai.learning_analyzer import LearningAnalyzer
from .font_controls import FontControlsWidget


class CapsReviewEditor(QDialog):
    """
    Interactive caps review editor with left/right panel design.
    Text view on left, caps word list on right with action buttons.
    """

    changes_applied = pyqtSignal(str)  # Signal emitted when changes are applied

    def __init__(
        self,
        text: str,
        caps_words: List[Tuple[int, str, List[Tuple[int, int]]]],
        cap_ignore_list: Set[str] = None,
        parent=None,
    ):
        """Initializes a new instance of the class. Sets up the original and current text, caps words, cap ignore list, protected sequences, and memory ignore sets.
        Args:
        text (str): The initial text to process.
        caps_words (List[Tuple[int, str, List[Tuple[int, int]]]]): A list of tuples containing index, word, and a list of character ranges to keep uppercase.
        cap_ignore_list (Set[str], optional): A set of words to ignore when capitalizing. Defaults to an empty set.
        parent (optional): The parent object.
        Returns: None
        """
        super().__init__(parent)
        self.original_text = text
        self.current_text = text
        self.caps_words = caps_words
        self.cap_ignore_list = cap_ignore_list or set()
        self.protected_sequences = set()  # Sequences to ignore
        self.memory_ignore = set()  # Session-based ignore list

        # Track current selection
        self.current_caps_index = 0
        self.caps_items = []  # Store all caps items for processing

        # Initialize learning system
        self.learning_storage = LearningStorage()
        self.learning_analyzer = LearningAnalyzer(self.learning_storage)
        self.user_decisions = []  # Track decisions for this session

        self.setup_ui()
        self.populate_caps_list()
        self.highlight_current_caps()

    def setup_ui(self):
        """Setup the user interface with left/right panel design."""
        self.setWindowTitle("Caps Review - AI Processing Results")
        self.setModal(True)
        self.resize(1000, 700)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Info label
        self.info_label = QLabel(
            "Review AI caps processing results. Select words to change or ignore."
        )
        main_layout.addWidget(self.info_label)

        # Main splitter (left/right panels)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Text view
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)

        # Header with title and font controls
        header_layout = QHBoxLayout()
        left_label = QLabel("Text View:")
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

        # Right panel - Caps list and buttons
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)

        right_label = QLabel("ALL CAPS Words Found:")
        right_layout.addWidget(right_label)

        self.caps_list = QListWidget()
        self.caps_list.itemClicked.connect(self.on_caps_item_clicked)
        right_layout.addWidget(self.caps_list)

        # Action buttons
        button_layout = QVBoxLayout()

        self.lower_button = QPushButton("LOWER")
        self.lower_button.setToolTip("Convert selected word to lowercase")
        self.lower_button.clicked.connect(self.lower_current)
        button_layout.addWidget(self.lower_button)

        self.lower_all_button = QPushButton("LOWER ALL")
        self.lower_all_button.setToolTip(
            "Convert all instances of this word to lowercase"
        )
        self.lower_all_button.clicked.connect(self.lower_all_current)
        button_layout.addWidget(self.lower_all_button)

        self.skip_button = QPushButton("SKIP")
        self.skip_button.setToolTip("Skip this word (keep as-is)")
        self.skip_button.clicked.connect(self.skip_current)
        button_layout.addWidget(self.skip_button)

        self.ignore_all_button = QPushButton("IGNORE ALL")
        self.ignore_all_button.setToolTip(
            "Ignore all instances of this word in this session"
        )
        self.ignore_all_button.clicked.connect(self.ignore_all_current)
        button_layout.addWidget(self.ignore_all_button)

        self.add_button = QPushButton("ADD")
        self.add_button.setToolTip("Add word to permanent CAP_IGNORE list in data.txt")
        self.add_button.clicked.connect(self.add_to_ignore_list)
        button_layout.addWidget(self.add_button)

        right_layout.addLayout(button_layout)

        splitter.addWidget(right_frame)

        # Set splitter proportions (60% text, 40% list)
        splitter.setSizes([600, 400])

        # Bottom buttons
        bottom_layout = QHBoxLayout()

        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        bottom_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        bottom_layout.addWidget(self.cancel_button)

        main_layout.addLayout(bottom_layout)

        # Initially disable buttons
        self.update_button_states()

    def populate_caps_list(self):
        """Populate the caps list with found ALL CAPS words."""
        self.caps_items.clear()
        self.caps_list.clear()

        # Collect all caps words, filtering out ignored ones
        for line_no, line_content, spans in self.caps_words:
            for start, end in spans:
                caps_word = line_content[start:end]

                # Skip if in ignore lists
                if (
                    caps_word in self.cap_ignore_list
                    or caps_word in self.memory_ignore
                    or len(caps_word) == 1
                ):  # Skip single letters
                    continue

                # Create caps item
                caps_item = {
                    "word": caps_word,
                    "line_no": line_no,
                    "start": start,
                    "end": end,
                    "line_content": line_content,
                    "processed": False,
                }

                self.caps_items.append(caps_item)

        # Populate list widget
        for i, item in enumerate(self.caps_items):
            word = item["word"]
            line_no = item["line_no"]
            list_item = QListWidgetItem(f"{word} (Line {line_no + 1})")
            list_item.setData(Qt.UserRole, i)
            self.caps_list.addItem(list_item)

        # Update info
        self.info_label.setText(
            f"Found {len(self.caps_items)} ALL CAPS words to review"
        )

        # Select first item if available
        if self.caps_items:
            self.caps_list.setCurrentRow(0)
            self.current_caps_index = 0

    def on_caps_item_clicked(self, item):
        """Handle caps list item click."""
        self.current_caps_index = item.data(Qt.UserRole)
        self.highlight_current_caps()
        self.update_button_states()

    def highlight_current_caps(self):
        """Highlight current caps word in text view."""
        if not self.caps_items or self.current_caps_index >= len(self.caps_items):
            return

        item = self.caps_items[self.current_caps_index]
        line_no = item["line_no"]
        start = item["start"]
        end = item["end"]

        # Calculate absolute position in text
        lines = self.current_text.splitlines()
        if line_no >= len(lines):
            return

        # Calculate absolute character position
        abs_start = sum(len(lines[i]) + 1 for i in range(line_no)) + start
        abs_end = abs_start + (end - start)

        # Highlight in text edit
        cursor = self.text_edit.textCursor()
        cursor.setPosition(abs_start)
        cursor.setPosition(abs_end, QTextCursor.KeepAnchor)

        # Set highlight format
        format = QTextCharFormat()
        format.setBackground(QColor(255, 255, 0))  # Yellow highlight
        cursor.setCharFormat(format)

        # Move cursor to highlight position
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def update_button_states(self):
        """Update button enabled/disabled states."""
        # Ensure we get a proper boolean value
        if self.caps_items and isinstance(self.caps_items, list):
            has_selection = bool(0 <= self.current_caps_index < len(self.caps_items))
        else:
            has_selection = False

        self.lower_button.setEnabled(has_selection)
        self.lower_all_button.setEnabled(has_selection)
        self.skip_button.setEnabled(has_selection)
        self.ignore_all_button.setEnabled(has_selection)
        self.add_button.setEnabled(has_selection)

    def _record_user_decision(self, user_action: str, final_result: str = None) -> None:
        """Record user decision for learning."""
        if not self.caps_items or self.current_caps_index >= len(self.caps_items):
            return

        item = self.caps_items[self.current_caps_index]
        word = item["word"]
        line_content = item["line_content"]
        start = item["start"]
        end = item["end"]
        line_no = item["line_no"]

        # Extract context (30 chars before and after)
        context_before = line_content[max(0, start - 30) : start]
        context_after = line_content[end : end + 30]

        # Determine sentence position
        sentence_position = "middle"
        if start <= 5:  # Near beginning of line
            sentence_position = "start"
        elif end >= len(line_content) - 5:  # Near end of line
            sentence_position = "end"

        # Use final_result if provided, otherwise use original word for skip/ignore
        if final_result is None:
            final_result = (
                word if user_action in ["skip", "ignore_all", "add"] else word.lower()
            )

        # Record the decision
        decision = {
            "word": word,
            "context_before": context_before,
            "context_after": context_after,
            "sentence_position": sentence_position,
            "user_action": user_action,
            "final_result": final_result,
            "line_number": line_no,
        }

        self.user_decisions.append(decision)
        log_message(f"Recorded decision: {word} -> {user_action} ({final_result})")

    def _get_ai_suggestion(
        self, word: str, context_before: str, context_after: str, sentence_position: str
    ) -> Optional[str]:
        """Get AI suggestion for a word based on learned patterns."""
        suggestion = self.learning_analyzer.get_suggestion_for_word(
            word, context_before, context_after, sentence_position
        )

        if suggestion and suggestion["confidence"] > 0.6:
            log_message(
                f"AI suggests {suggestion['action']} for '{word}' "
                f"({suggestion['confidence']:.2f} confidence: {suggestion['reason']})"
            )
            return suggestion["action"]

        return None

    def _on_font_changed(self, font_family: str, font_size: int):
        """Handle font change from font controls."""
        # Update text edit widget font
        self.text_edit.setFont(QFont(font_family, font_size))

        # Save to config file (removed since .data.txt deleted)
        log_message(f"Font changed to {font_family} {font_size}pt in caps editor")

    def lower_current(self):
        """Convert current caps word to lowercase."""
        if not self.caps_items or self.current_caps_index >= len(self.caps_items):
            return

        item = self.caps_items[self.current_caps_index]
        word = item["word"]
        lowercase_word = word.lower()

        # Record user decision for learning
        self._record_user_decision("lower", lowercase_word)

        # Apply change to this specific instance
        self._apply_single_change(item, lowercase_word)

        # Mark as processed and move to next
        item["processed"] = True
        self._move_to_next_item()

    def lower_all_current(self):
        """Convert all instances of current caps word to lowercase."""
        if not self.caps_items or self.current_caps_index >= len(self.caps_items):
            return

        item = self.caps_items[self.current_caps_index]
        word = item["word"]
        lowercase_word = word.lower()

        # Record user decision for learning
        self._record_user_decision("lower_all", lowercase_word)

        # Apply to all instances of this word in text
        self._apply_global_change(word, lowercase_word)

        # Add to protected sequences to prevent re-highlighting
        self.protected_sequences.add(lowercase_word)

        # Mark all instances as processed and refresh list
        for caps_item in self.caps_items:
            if caps_item["word"] == word:
                caps_item["processed"] = True

        self._refresh_caps_list()

    def skip_current(self):
        """Skip current caps word (keep as-is)."""
        if not self.caps_items or self.current_caps_index >= len(self.caps_items):
            return

        item = self.caps_items[self.current_caps_index]

        # Record user decision for learning
        self._record_user_decision("skip", item["word"])

        item["processed"] = True
        self._move_to_next_item()

    def ignore_all_current(self):
        """Add current caps word to memory ignore list."""
        if not self.caps_items or self.current_caps_index >= len(self.caps_items):
            return

        item = self.caps_items[self.current_caps_index]
        word = item["word"]

        # Record user decision for learning
        self._record_user_decision("ignore_all", word)

        # Add to memory ignore
        self.memory_ignore.add(word)

        # Mark all instances as processed and refresh list
        for caps_item in self.caps_items:
            if caps_item["word"] == word:
                caps_item["processed"] = True

        self._refresh_caps_list()

        log_message(f"Added '{word}' to session ignore list")

    def add_to_ignore_list(self):
        """Add current caps word to permanent CAP_IGNORE list."""
        if not self.caps_items or self.current_caps_index >= len(self.caps_items):
            return

        item = self.caps_items[self.current_caps_index]
        word = item["word"]

        # Confirm action
        reply = QMessageBox.question(
            self,
            "Add to CAP_IGNORE",
            f"Add '{word}' to permanent CAP_IGNORE list in data.txt?\n\n"
            f"This will prevent '{word}' from being highlighted in future sessions.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Record user decision for learning
            self._record_user_decision("add", word)

            # Add to both memory and permanent ignore
            self.memory_ignore.add(word)
            self.cap_ignore_list.add(word)

            # Signal to update data.txt (would be handled by parent)
            log_message(f"Added '{word}' to permanent CAP_IGNORE list")

            # Mark all instances as processed and refresh list
            for caps_item in self.caps_items:
                if caps_item["word"] == word:
                    caps_item["processed"] = True

            self._refresh_caps_list()

    def _apply_single_change(self, item, replacement):
        """Apply change to a single instance."""
        line_no = item["line_no"]
        start = item["start"]
        end = item["end"]

        lines = self.current_text.splitlines()
        if line_no >= len(lines):
            return

        line = lines[line_no]
        new_line = line[:start] + replacement + line[end:]
        lines[line_no] = new_line

        self.current_text = "\n".join(lines)
        self.text_edit.setPlainText(self.current_text)

        # Update item to reflect change
        item["word"] = replacement
        item["end"] = start + len(replacement)

    def _apply_global_change(self, original_word, replacement):
        """Apply change to all instances of a word in text."""
        # Use word boundary regex for exact matches
        pattern = re.compile(r"\b" + re.escape(original_word) + r"\b")
        self.current_text = pattern.sub(replacement, self.current_text)
        self.text_edit.setPlainText(self.current_text)

        log_message(f"Applied global change: '{original_word}' -> '{replacement}'")

    def _move_to_next_item(self):
        """Move to next unprocessed item."""
        # Find next unprocessed item
        for i in range(self.current_caps_index + 1, len(self.caps_items)):
            if not self.caps_items[i]["processed"]:
                self.current_caps_index = i
                self.caps_list.setCurrentRow(i)
                self.highlight_current_caps()
                return

        # No more unprocessed items
        self._refresh_caps_list()

    def _refresh_caps_list(self):
        """Refresh the caps list, removing processed items."""
        # Remove processed items
        self.caps_items = [item for item in self.caps_items if not item["processed"]]

        # Repopulate list
        self.caps_list.clear()
        for i, item in enumerate(self.caps_items):
            word = item["word"]
            line_no = item["line_no"]
            list_item = QListWidgetItem(f"{word} (Line {line_no + 1})")
            list_item.setData(Qt.UserRole, i)
            self.caps_list.addItem(list_item)

        # Update info
        self.info_label.setText(
            f"Found {len(self.caps_items)} ALL CAPS words to review"
        )

        # Reset selection
        if self.caps_items:
            self.current_caps_index = 0
            self.caps_list.setCurrentRow(0)
            self.highlight_current_caps()
        else:
            self.current_caps_index = -1
            self.info_label.setText("All caps words processed!")

        self.update_button_states()

    def apply_changes(self):
        """Apply all changes and close dialog."""
        # Save all learning data before closing
        self._save_learning_data()

        self.changes_applied.emit(self.current_text)
        self.accept()

    def _save_learning_data(self):
        """Save all user decisions to learning system."""
        if not self.user_decisions:
            log_message("No user decisions to save for learning")
            return

        log_message(f"Saving {len(self.user_decisions)} user decisions for AI learning")

        # Add all decisions to learning analyzer
        for decision in self.user_decisions:
            self.learning_analyzer.add_user_decision(
                word=decision["word"],
                context_before=decision["context_before"],
                context_after=decision["context_after"],
                sentence_position=decision["sentence_position"],
                user_action=decision["user_action"],
                final_result=decision["final_result"],
                line_number=decision["line_number"],
            )

        # Analyze patterns and update storage
        try:
            self.learning_analyzer.analyze_and_update_patterns()
            log_message("AI learning data saved successfully")
        except Exception as e:
            log_message(f"Error saving learning data: {e}", level="ERROR")

    def get_updated_text(self) -> str:
        """Get the updated text with all changes."""
        return self.current_text

    def get_updated_cap_ignore_list(self) -> Set[str]:
        """Get the updated CAP_IGNORE list with any new additions."""
        return self.cap_ignore_list
