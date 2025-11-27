"""
Enhanced Numbered Line Editor with Left/Right Panel Design.

Left panel: Text view with highlighted numbers
Right panel: Simple list of numbers for editing
Buttons: Apply, Apply All, Skip, Ignore, Ignore All
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QWidget,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QMessageBox,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from typing import List, Tuple, Dict, Optional, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from ..context import BookfixContext

from ..datafile import save_font_settings
from .font_controls import FontControlsWidget


class NumberListItem(QListWidgetItem):
    """Custom list item for numbers with editing capability."""

    def __init__(self, number: str, line_no: int, position: int):
        super().__init__(number)
        self.original_number = number
        self.edited_number = number
        self.line_no = line_no  # 0-based line number
        self.position = position  # Position in text
        self.is_edited = False
        self.status = "pending"  # pending, applied, skipped, ignored

        # Make it editable
        self.setFlags(self.flags() | Qt.ItemIsEditable)

    def set_edited(self, new_text: str):
        """Mark item as edited with new text."""
        self.edited_number = new_text
        self.is_edited = new_text != self.original_number
        self.setText(
            f"{self.original_number} → {new_text}" if self.is_edited else new_text
        )

    def get_display_text(self) -> str:
        """Get the text to replace in the document."""
        return self.edited_number if self.is_edited else self.original_number


class NumberedLineEditor(QDialog):
    """
    Enhanced numbered line editor with left/right panel design.

    Left: Text editor with highlighted numbers
    Right: List of numbers for individual editing
    """

    # Signals
    editing_completed = pyqtSignal(str)  # Final edited text
    editing_cancelled = pyqtSignal()

    def __init__(self, ctx: "BookfixContext", parent=None):
        super().__init__(parent)

        self.ctx = ctx
        self.original_text = ctx.text
        self.current_text = ctx.text

        # Number finding and tracking
        self.numbered_lines: List[Tuple[int, str, List[Tuple[int, int]]]] = []
        self.number_items: List[NumberListItem] = []
        self.current_selection = 0

        # Memory ignore lists
        self.session_ignored_numbers = set()  # Numbers to ignore for session
        self.processed_numbers = set()  # Numbers processed with Apply All/Ignore All
        self.protected_sequences = (
            set()
        )  # Exact text sequences to protect (e.g., "15 12", "zero 800")

        # UI setup
        self.setWindowTitle("Numbered Line Editor")
        self.setModal(True)
        self.resize(1200, 800)
        self._setup_ui()

        # Initialize with current text
        self._find_and_display_numbers()

    def _setup_ui(self):
        """Create the UI layout."""
        layout = QVBoxLayout(self)

        # Title and status
        title_label = QLabel("Interactive Numbered Line Editor")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)

        self.status_label = QLabel("Ready to edit numbers")
        layout.addWidget(self.status_label)

        # Main splitter (left: text, right: number list)
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - text editor with highlights
        self._create_text_panel(splitter)

        # Right panel - number list and buttons
        self._create_number_panel(splitter)

        # Set splitter proportions (3:1 ratio)
        splitter.setSizes([900, 300])
        layout.addWidget(splitter)

        # Bottom buttons
        self._create_bottom_buttons(layout)

    def _create_text_panel(self, parent):
        """Create left panel with text editor."""
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)

        # Header with title and font controls
        header_layout = QHBoxLayout()
        left_label = QLabel("Text View:")
        left_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(left_label)

        # Add font controls
        self.font_controls = FontControlsWidget(initial_family="Arial", initial_size=12)
        self.font_controls.font_changed.connect(self._on_font_changed)
        header_layout.addWidget(self.font_controls)

        left_layout.addLayout(header_layout)

        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont("Arial", 12))
        self.text_editor.setReadOnly(True)  # Read-only for display
        self.text_editor.mousePressEvent = self._text_click_handler

        left_layout.addWidget(self.text_editor)

        parent.addWidget(left_frame)

    def _create_number_panel(self, parent):
        """Create right panel with number list and buttons."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Number list
        list_label = QLabel("Numbers to Review:")
        list_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(list_label)

        self.number_list = QListWidget()
        self.number_list.setFont(QFont("Courier", 10))
        self.number_list.itemClicked.connect(self._number_list_clicked)
        self.number_list.itemDoubleClicked.connect(self._number_list_double_clicked)
        self.number_list.itemChanged.connect(self._number_item_changed)
        right_layout.addWidget(self.number_list)

        # Action buttons
        self._create_action_buttons(right_layout)

        parent.addWidget(right_widget)

    def _create_action_buttons(self, layout):
        """Create action buttons for the right panel."""
        # Single instance buttons
        single_layout = QHBoxLayout()

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_single)
        self.apply_button.setToolTip("Apply this change to this instance only")
        single_layout.addWidget(self.apply_button)

        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self._skip_single)
        self.skip_button.setToolTip("Skip this number (leave unchanged)")
        single_layout.addWidget(self.skip_button)

        layout.addLayout(single_layout)

        # Global buttons
        global_layout = QHBoxLayout()

        self.apply_all_button = QPushButton("Apply All")
        self.apply_all_button.clicked.connect(self._apply_all)
        self.apply_all_button.setToolTip(
            "Apply this change to ALL instances of this number"
        )
        global_layout.addWidget(self.apply_all_button)

        self.ignore_button = QPushButton("Ignore")
        self.ignore_button.clicked.connect(self._ignore_all)
        self.ignore_button.setToolTip("Ignore ALL instances of this number")
        global_layout.addWidget(self.ignore_button)

        layout.addLayout(global_layout)

    def _create_bottom_buttons(self, layout):
        """Create bottom control buttons."""
        button_layout = QHBoxLayout()

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self._finish_editing)
        button_layout.addWidget(self.done_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._cancel_editing)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _on_font_changed(self, font_family: str, font_size: int):
        """Handle font change from font controls."""
        # Update text editor widget font
        self.text_editor.setFont(QFont(font_family, font_size))

        # Save to config file
        save_font_settings(font_family, font_size)

        from ..logging import log_message

        log_message(f"Font changed to {font_family} {font_size}pt in numbered editor")

    def _find_and_display_numbers(self):
        """Find all numbers in text and update display."""
        self._find_numbered_lines()
        self._populate_number_list()
        self._highlight_text()
        self._update_status()

    def _find_numbered_lines(self):
        """Find lines containing numbers (3+ digits or any digits)."""
        lines = self.current_text.splitlines()
        self.numbered_lines = []

        # Pattern to find numbers with 3+ digits (like original system)
        patterns = [
            r"\b\d{3,}\b",  # 3 or more digits only
            r"\b\d+[.,]\d+\b",  # Numbers with decimal/comma
            r"\b\d{1,2}:\d{2}\b",  # Time format
        ]

        combined_pattern = "|".join(f"({p})" for p in patterns)
        number_pattern = re.compile(combined_pattern)

        for idx, line in enumerate(lines):
            spans = []
            for match in number_pattern.finditer(line):
                number_text = match.group()
                # Skip if in ignore lists or part of protected sequence
                if (
                    number_text not in self.session_ignored_numbers
                    and number_text not in self.processed_numbers
                    and not self._is_part_of_protected_sequence(line, match.span())
                ):
                    spans.append(match.span())

            if spans:
                self.numbered_lines.append((idx, line, spans))

    def _populate_number_list(self):
        """Populate the right panel list with numbers."""
        self.number_list.clear()
        self.number_items = []

        # Calculate absolute positions
        line_positions = self._get_line_positions()

        for line_no, line_content, spans in self.numbered_lines:
            line_start = line_positions[line_no]

            for start, end in spans:
                number_text = line_content[start:end]
                absolute_pos = line_start + start

                item = NumberListItem(number_text, line_no, absolute_pos)
                self.number_items.append(item)
                self.number_list.addItem(item)

    def _get_line_positions(self) -> List[int]:
        """Get starting position of each line in the text."""
        lines = self.current_text.splitlines()
        positions = [0]

        for line in lines:
            positions.append(positions[-1] + len(line) + 1)  # +1 for newline

        return positions

    def _highlight_text(self):
        """Apply highlights to numbers in the text editor."""
        self.text_editor.setPlainText(self.current_text)
        cursor = self.text_editor.textCursor()

        # Yellow highlight for normal numbers
        yellow_format = QTextCharFormat()
        yellow_format.setBackground(QColor("#FFE066"))

        # Green highlight for selected number
        green_format = QTextCharFormat()
        green_format.setBackground(QColor("#66FF66"))

        # Blue highlight for processed numbers
        blue_format = QTextCharFormat()
        blue_format.setBackground(QColor("#66B3FF"))

        # Apply highlights
        for i, item in enumerate(self.number_items):
            cursor.setPosition(item.position)
            cursor.setPosition(
                item.position + len(item.original_number), QTextCursor.KeepAnchor
            )

            if i == self.current_selection:
                cursor.setCharFormat(green_format)
            elif item.status in ["applied", "skipped"]:
                cursor.setCharFormat(blue_format)
            else:
                cursor.setCharFormat(yellow_format)

    def _update_status(self):
        """Update status label."""
        total = len(self.number_items)
        if total == 0:
            self.status_label.setText("No numbers found to edit")
        else:
            current = self.current_selection + 1
            self.status_label.setText(f"Number {current} of {total}")

    def _text_click_handler(self, event):
        """Handle clicks on the text editor to select numbers."""
        # Call original handler first
        QTextEdit.mousePressEvent(self.text_editor, event)

        if event.button() == Qt.LeftButton:
            cursor = self.text_editor.cursorForPosition(event.pos())
            position = cursor.position()

            # Find which number was clicked
            for i, item in enumerate(self.number_items):
                if (
                    item.position
                    <= position
                    < item.position + len(item.original_number)
                ):
                    self._select_number(i)
                    break

    def _number_list_clicked(self, item):
        """Handle clicks on the number list."""
        try:
            index = self.number_items.index(item)
            self._select_number(index)
        except ValueError:
            pass

    def _number_list_double_clicked(self, item):
        """Handle double-clicks on number list for editing."""
        self.number_list.editItem(item)

    def _number_item_changed(self, item):
        """Handle when a number item is edited."""
        if isinstance(item, NumberListItem):
            # Extract the edited text
            item_text = item.text()
            if " → " in item_text:
                # Format: "1972 → 19 72"
                edited_text = item_text.split(" → ")[1]
            else:
                edited_text = item_text

            item.set_edited(edited_text)
            self._highlight_text()  # Refresh highlights

    def _select_number(self, index: int):
        """Select a number by index."""
        if 0 <= index < len(self.number_items):
            self.current_selection = index
            self.number_list.setCurrentRow(index)

            # Scroll text to show selected number
            item = self.number_items[index]
            cursor = self.text_editor.textCursor()
            cursor.setPosition(item.position)
            self.text_editor.setTextCursor(cursor)
            self.text_editor.ensureCursorVisible()

            self._highlight_text()
            self._update_status()

    def _apply_single(self):
        """Apply the current number change to this instance only."""
        if not self.number_items:
            return

        item = self.number_items[self.current_selection]
        if item.is_edited:
            # Apply the change to the text
            lines = self.current_text.splitlines()
            line_content = lines[item.line_no]

            # Find the number in the line and replace it
            start_in_line = item.position - self._get_line_positions()[item.line_no]
            end_in_line = start_in_line + len(item.original_number)

            new_line = (
                line_content[:start_in_line]
                + item.edited_number
                + line_content[end_in_line:]
            )
            lines[item.line_no] = new_line
            self.current_text = "\n".join(lines)

        # Mark as applied
        item.status = "applied"
        self._move_to_next()

    def _skip_single(self):
        """Skip the current number (leave unchanged)."""
        if not self.number_items:
            return

        item = self.number_items[self.current_selection]
        item.status = "skipped"
        self._move_to_next()

    def _apply_all(self):
        """Apply the current change to ALL instances of this number in entire text."""
        if not self.number_items:
            return

        item = self.number_items[self.current_selection]
        original_num = item.original_number
        replacement = item.edited_number if item.is_edited else original_num

        if replacement != original_num:
            # Replace ALL instances in ENTIRE text (not just from current position)
            self.current_text = self.current_text.replace(original_num, replacement)

            # Add replacement to protected sequences (exact sequence matching)
            self.protected_sequences.add(replacement)

        # Add original to processed list
        self.processed_numbers.add(original_num)

        # Full refresh needed
        self._find_and_display_numbers()
        self._select_first_available()

    def _ignore_all(self):
        """Ignore ALL instances of this number."""
        if not self.number_items:
            return

        item = self.number_items[self.current_selection]
        original_num = item.original_number

        # Add to processed list
        self.processed_numbers.add(original_num)

        # Full refresh needed
        self._find_and_display_numbers()
        self._select_first_available()

    def _move_to_next(self):
        """Move to the next unprocessed number."""
        # Find next pending item
        for i in range(self.current_selection + 1, len(self.number_items)):
            if self.number_items[i].status == "pending":
                self._select_number(i)
                return

        # If no next item, try from beginning
        for i in range(self.current_selection):
            if self.number_items[i].status == "pending":
                self._select_number(i)
                return

        # No pending items left
        self.status_label.setText("All numbers processed")

    def _select_first_available(self):
        """Select first available number after refresh."""
        if self.number_items:
            self._select_number(0)
        else:
            self.current_selection = 0
            self._update_status()

    def _finish_editing(self):
        """Finish editing and emit the final text."""
        # Apply any remaining single changes
        for item in self.number_items:
            if item.status == "pending" and item.is_edited:
                # Auto-apply pending edits
                self._apply_single_item(item)

        self.editing_completed.emit(self.current_text)
        self.accept()

    def _apply_single_item(self, item: NumberListItem):
        """Apply a single item change."""
        if not item.is_edited:
            return

        lines = self.current_text.splitlines()
        line_content = lines[item.line_no]

        start_in_line = item.position - self._get_line_positions()[item.line_no]
        end_in_line = start_in_line + len(item.original_number)

        new_line = (
            line_content[:start_in_line]
            + item.edited_number
            + line_content[end_in_line:]
        )
        lines[item.line_no] = new_line
        self.current_text = "\n".join(lines)

    def _cancel_editing(self):
        """Cancel editing and emit cancel signal."""
        self.editing_cancelled.emit()
        self.reject()

    def _is_part_of_protected_sequence(
        self, line: str, number_span: Tuple[int, int]
    ) -> bool:
        """Check if a number span is part of any protected sequence."""
        start, end = number_span

        # Check each protected sequence to see if it appears in this line
        for protected in self.protected_sequences:
            # Find all occurrences of this protected sequence in the line
            pos = 0
            while True:
                found = line.find(protected, pos)
                if found == -1:
                    break

                # Check if the number span overlaps with this protected sequence
                protected_start = found
                protected_end = found + len(protected)

                # Check if number span is within or overlaps the protected sequence
                if (
                    (start >= protected_start and start < protected_end)
                    or (end > protected_start and end <= protected_end)
                    or (start <= protected_start and end >= protected_end)
                ):
                    return True

                pos = found + 1  # Look for next occurrence

        return False
