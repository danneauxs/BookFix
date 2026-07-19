"""
Interactive PyQt5 review window for number formatting proposals.

Allows user to confirm, correct, or reclassify each proposed number format
using quick keyboard shortcuts (0-9) and an editable output field.
Adapted from numtest_standalone/review_window.py for BookFix integration.
"""

from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QSplitter,
    QProgressBar,
    QGroupBox,
    QFrame,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QBrush

from ..logging import log_message
from ..widgets.font_controls import FontControlsWidget


class NumberReviewWindow(QDialog):
    """
    Interactive review window for number formatting proposals.

    Shows each proposed change with context, allows user to:
    - Accept/reject changes
    - Change classification type using quick keys (1-8), 0 to skip
    - Edit output text directly
    - Navigate between changes with arrow keys
    - Flag problematic numbers with !!FLASH!! using key 9
    """

    def __init__(self, original_text: str, proposals: List[Dict], processor, parent=None):
        """
        Initialize the number review window.

        Args:
            original_text: Full original input text (used for context extraction)
            proposals: List of proposal dicts from RulesOnlyNumberProcessor.propose()
            processor: RulesOnlyNumberProcessor instance used for re-formatting on type change
            parent: Parent widget
        """
        super().__init__(parent)
        self.original_text = original_text
        self.original_lines = original_text.splitlines(keepends=False)
        self.proposals = proposals
        self.processor = processor

        self.current_index = 0
        self.setWindowTitle("Number Review")
        self.resize(1200, 600)

        self.setup_ui()
        if self.proposals:
            self.populate_numbers_list()
            self.show_proposal(0)

    def setup_ui(self):
        """Build the complete UI layout with list panel, context panel, type buttons, and navigation."""
        main_layout = QVBoxLayout(self)

        # Header: title label + progress bar
        header = QHBoxLayout()
        self.title_label = QLabel()
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(20)
        header.addWidget(self.title_label, 1)
        header.addWidget(self.progress, 0)
        main_layout.addLayout(header)

        # Main content: 2-way splitter — context left, list+controls right
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: sentence context display
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("SENTENCE:"))

        # Font controls
        self.font_controls = FontControlsWidget(initial_family="Arial", initial_size=12)
        self.font_controls.font_changed.connect(self._on_font_changed)
        left_layout.addWidget(self.font_controls)

        self.context_edit = QTextEdit()
        self.context_edit.setReadOnly(True)
        self.context_edit.setMaximumWidth(400)
        self.context_edit.setFont(QFont("Arial", 12))
        left_layout.addWidget(self.context_edit)
        splitter.addWidget(left_panel)

        # Right panel: item list on top + change info + type buttons + output below
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)

        # Item list (takes upper space with stretch)
        list_label_layout = QHBoxLayout()
        list_label_layout.addWidget(QLabel("Items:"))
        list_label_layout.addStretch()
        right_layout.addLayout(list_label_layout)
        self.numbers_list = QListWidget()
        self.numbers_list.itemClicked.connect(self.on_number_item_clicked)
        right_layout.addWidget(self.numbers_list, 1)  # stretch factor 1

        # Separator
        right_layout.addSpacing(10)

        # Info section
        info_group = QGroupBox("Current Change")
        info_layout = QVBoxLayout(info_group)
        self.original_label = QLabel()
        self.type_label = QLabel()
        info_layout.addWidget(self.original_label)
        info_layout.addWidget(self.type_label)
        right_layout.addWidget(info_group)

        # Output section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        output_layout.addWidget(QLabel("Formatted (edit to customize):"))

        output_row = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.returnPressed.connect(self.accept_proposal)
        output_row.addWidget(self.output_edit, 1)

        self.all_btn = QPushButton("All")
        self.all_btn.setMaximumWidth(50)
        self.all_btn.setAutoDefault(False)
        self.all_btn.clicked.connect(self.apply_to_all)
        output_row.addWidget(self.all_btn)

        output_layout.addLayout(output_row)
        right_layout.addWidget(output_group)

        # Type selector buttons (rows 1 and 2)
        type_group = QGroupBox("Type (quick keys)")
        type_layout = QVBoxLayout(type_group)

        row1 = QHBoxLayout()
        self.type_buttons = {}
        for key, label in [(1, "General"), (2, "Year"), (3, "Code/ID"), (4, "Currency")]:
            btn = QPushButton(f"[{key}] {label}")
            btn.setMaximumWidth(120)
            btn.setAutoDefault(False)
            btn.clicked.connect(lambda checked=False, k=key: self.select_type(k))
            row1.addWidget(btn)
            self.type_buttons[key] = btn
        type_layout.addLayout(row1)

        row2 = QHBoxLayout()
        for key, label in [(5, "Time"), (6, "Measure"), (7, "Ordinal"), (8, "Range")]:
            btn = QPushButton(f"[{key}] {label}")
            btn.setMaximumWidth(120)
            btn.setAutoDefault(False)
            btn.clicked.connect(lambda checked=False, k=key: self.select_type(k))
            row2.addWidget(btn)
            self.type_buttons[key] = btn

        skip_type_btn = QPushButton("[0] Skip")
        skip_type_btn.setMaximumWidth(120)
        skip_type_btn.setAutoDefault(False)
        skip_type_btn.clicked.connect(lambda checked=False, k=0: self.select_type(k))
        row2.addWidget(skip_type_btn)
        self.type_buttons[0] = skip_type_btn
        type_layout.addLayout(row2)

        row3 = QHBoxLayout()
        flag_btn = QPushButton("[9] Flag (!!FLASH!!)")
        flag_btn.setMaximumWidth(150)
        flag_btn.setAutoDefault(False)
        flag_btn.clicked.connect(self.flag_number)
        row3.addWidget(flag_btn)
        self.accept_btn = QPushButton("✓ Accept (Enter)")
        self.accept_btn.setAutoDefault(False)
        self.accept_btn.clicked.connect(self.accept_proposal)
        self.accept_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        row3.addWidget(self.accept_btn)
        row3.addStretch()
        type_layout.addLayout(row3)

        right_layout.addWidget(type_group)

        # Currency symbol selector (hidden until type 4 selected)
        self.currency_group = QGroupBox("Currency")
        currency_layout = QHBoxLayout(self.currency_group)
        self.currency_buttons = {}
        for i, symbol in enumerate(["$", "£", "€", "¥"]):
            btn = QPushButton(f"{i+1}) {symbol}")
            btn.setMaximumWidth(70)
            btn.setAutoDefault(False)
            btn.clicked.connect(lambda checked=False, s=symbol: self.select_currency(s))
            currency_layout.addWidget(btn)
            self.currency_buttons[i + 1] = (btn, symbol)
        self.currency_group.hide()
        right_layout.addWidget(self.currency_group)

        right_layout.addStretch()

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        # Bottom navigation + action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton("Apply & Save")
        self.apply_btn.setAutoDefault(False)
        self.apply_btn.clicked.connect(self.apply_and_save)
        self.apply_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.apply_btn.setEnabled(False)
        button_layout.addWidget(self.apply_btn)

        main_layout.addLayout(button_layout)

    def _get_expanded_context(self, proposal: Dict) -> str:
        """
        Extract context for the number: from start of paragraph backward to first blank line,
        and from end of number forward to first blank line.

        Returns context string with number marked by « » boundaries.

        Args:
            proposal: Proposal dict with line_no, start, end, original keys

        Returns:
            Context string showing paragraph containing the number with number marked
        """
        line_no = proposal["line_no"]
        start = proposal["start"]
        end = proposal["end"]
        num = proposal["original"]

        # Collect backward to start of paragraph (stop at first blank line)
        before = ""
        current_line = line_no
        current_pos = start

        while current_line >= 0:
            line = self.original_lines[current_line]
            if current_line == line_no:
                segment = line[:current_pos]
            else:
                segment = line

            if not segment.strip():  # blank line = end of backward collection
                break

            if current_line < line_no:
                before = segment + "\n" + before
            else:
                before = segment + before

            current_line -= 1

        # Collect forward to end of paragraph (stop at first blank line)
        after = ""
        current_line = line_no
        current_pos = end

        while current_line < len(self.original_lines):
            line = self.original_lines[current_line]
            if current_line == line_no:
                segment = line[current_pos:]
            else:
                segment = line

            if not segment.strip():  # blank line = end of forward collection
                break

            if current_line > line_no:
                after = after + "\n" + segment
            else:
                after = after + segment

            current_line += 1

        return f"{before} » {num} « {after}"

    def show_proposal(self, index: int):
        """
        Display the proposal at the given index.

        Updates title, progress bar, context display, original/type labels,
        and output edit field. Resets currency panel visibility.

        Args:
            index: Index into self.proposals to display
        """
        if index < 0 or index >= len(self.proposals):
            return

        self.current_index = index
        p = self.proposals[index]

        self.title_label.setText(f"Change {index + 1} of {len(self.proposals)}")
        self.progress.setValue(int((index + 1) / len(self.proposals) * 100))

        # Sync list selection to current item
        self.numbers_list.setCurrentRow(index)

        # Show context with number highlighted
        sentence = self._get_expanded_context(p)
        original_num = p["original"]
        self.context_edit.setText(sentence)

        cursor = self.context_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#FFFF00"))
        # Search for the marker form first (» num «) to find the RIGHT occurrence when same number appears multiple times
        marker = f"» {original_num} «"
        marker_idx = sentence.find(marker)
        if marker_idx != -1:
            idx = marker_idx + 2  # offset past "» " (2 chars) to reach the number itself
        else:
            idx = sentence.find(original_num)
        if idx != -1:
            cursor.setPosition(idx)
            cursor.setPosition(idx + len(original_num), QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(fmt)      # apply yellow BEFORE setting cursor on widget
            self.context_edit.setTextCursor(cursor)

        self.original_label.setText(f"Original: {p['original']}")
        self.type_label.setTextFormat(Qt.RichText)
        type_html = f'Type: <b><span style="font-size:14pt; color:red;">{p["type"]}</span></b> [{p["rule"]}]'
        self.type_label.setText(type_html)

        self.output_edit.setText(p["user_text"])
        self.setFocus()

        self.apply_btn.setEnabled(False)
        self.currency_group.hide()

    def _on_font_changed(self, family: str, size: int):
        """Update context editor font when user changes font controls."""
        self.context_edit.setFont(QFont(family, size))

    def populate_numbers_list(self):
        """Populate the list of numbers with their current state."""
        self.numbers_list.clear()
        for i, p in enumerate(self.proposals):
            original = p["original"]
            user_text = p.get("user_text", p.get("formatted", original))

            if p.get("decided", False):
                # User has reviewed this item — show label
                if p.get("accepted", True):
                    # Accepted with action label
                    action_type = p.get("type", "accept")
                    if action_type == "general_number":
                        label = "[accept]"
                    elif action_type == "year":
                        label = "[year]"
                    elif action_type == "identifier":
                        label = "[code]"
                    elif action_type == "currency":
                        label = "[currency]"
                    elif action_type == "clock_time":
                        label = "[time]"
                    elif action_type == "measurement":
                        label = "[measure]"
                    elif action_type == "ordinal":
                        label = "[ordinal]"
                    elif action_type == "range_measurement":
                        label = "[range]"
                    elif action_type == "flag":
                        label = "[flag]"
                    else:
                        label = "[accept]"
                    text = f"{i+1}. {original} → {user_text} {label}"
                else:
                    # Skipped
                    text = f"{i+1}. {original} → {original} [skip]"
            else:
                # Not yet reviewed — no label
                text = f"{i+1}. {original} → {user_text}"

            item = QListWidgetItem(text)
            if p.get("decided", False) and not p.get("accepted", True):
                item.setForeground(QColor(100, 100, 100))  # gray for skipped
            self.numbers_list.addItem(item)

    def on_number_item_clicked(self, item):
        """Navigate to clicked item in list."""
        row = self.numbers_list.row(item)
        self.show_proposal(row)

    def select_type(self, type_key: int):
        """
        Re-format the current number with the selected type key.

        Type key 0 restores original (skip). Type key 4 shows currency panel.
        All others re-format via processor.reformat() and auto-advance.

        Args:
            type_key: Integer 0-8 mapping to type names
        """
        if type_key == 0:  # Skip: restore original
            self.proposals[self.current_index]["user_text"] = self.proposals[self.current_index]["original"]
            self.proposals[self.current_index]["accepted"] = False
            self.proposals[self.current_index]["decided"] = True
            self.output_edit.setText(self.proposals[self.current_index]["original"])
            self.populate_numbers_list()
            self._advance_to_next()
            return

        type_map = {
            1: "general_number",
            2: "year",
            3: "identifier",
            4: "currency",
            5: "clock_time",
            6: "measurement",
            7: "ordinal",
            8: "range_measurement",
        }

        if type_key not in type_map:
            return

        p = self.proposals[self.current_index]
        new_type = type_map[type_key]

        if type_key == 4:  # Currency: show symbol selector first
            self.currency_group.show()
            return

        formatted = self.processor.reformat(p["original"], new_type)
        self.proposals[self.current_index]["user_text"] = formatted
        self.proposals[self.current_index]["type"] = new_type
        self.proposals[self.current_index]["accepted"] = True
        self.proposals[self.current_index]["decided"] = True
        self.output_edit.setText(formatted)
        self.populate_numbers_list()
        self._advance_to_next()

    def select_currency(self, symbol: str):
        """
        Select currency symbol and re-format current number as currency.

        Args:
            symbol: Currency symbol string (e.g., "$", "£", "€", "¥")
        """
        p = self.proposals[self.current_index]
        formatted = self.processor.reformat(p["original"], "currency", currency_symbol=symbol)
        self.proposals[self.current_index]["user_text"] = formatted
        self.proposals[self.current_index]["type"] = "currency"
        self.proposals[self.current_index]["accepted"] = True
        self.proposals[self.current_index]["decided"] = True
        self.output_edit.setText(formatted)
        self.currency_group.hide()
        self.populate_numbers_list()
        self._advance_to_next()

    def flag_number(self):
        """Flag current number with !!FLASH!! prefix to mark it for manual review."""
        p = self.proposals[self.current_index]
        flagged_text = f"!!FLASH!! {p['original']}"
        self.proposals[self.current_index]["user_text"] = flagged_text
        self.proposals[self.current_index]["accepted"] = True
        self.proposals[self.current_index]["type"] = "flag"
        self.proposals[self.current_index]["decided"] = True
        self.output_edit.setText(flagged_text)
        log_message(f"Flagged number '{p['original']}' with !!FLASH!!")
        self.populate_numbers_list()
        self._advance_to_next()

    def apply_to_all(self):
        """Apply current output_edit text to all proposals with the same original number."""
        current = self.proposals[self.current_index]
        original = current["original"]
        new_text = self.output_edit.text()

        count = 0
        for p in self.proposals:
            if p["original"] == original:
                p["user_text"] = new_text
                count += 1

        if count > 1:
            log_message(f"Applied '{new_text}' to {count} instances of '{original}'")

    def accept_proposal(self):
        """Accept current proposal using output_edit text and advance to next."""
        p = self.proposals[self.current_index]
        p["user_text"] = self.output_edit.text()
        p["accepted"] = True
        p["decided"] = True
        self.populate_numbers_list()

        self.current_index += 1
        if self.current_index < len(self.proposals):
            self.show_proposal(self.current_index)
        else:
            self.current_index = len(self.proposals) - 1
            self.apply_btn.setEnabled(True)

    def next_proposal(self):
        """Navigate to next proposal without accepting current."""
        self.current_index += 1
        if self.current_index < len(self.proposals):
            self.show_proposal(self.current_index)
        else:
            self.current_index = len(self.proposals) - 1
            self.apply_btn.setEnabled(True)

    def previous_proposal(self):
        """Navigate to previous proposal."""
        self.current_index -= 1
        if self.current_index >= 0:
            self.show_proposal(self.current_index)
        else:
            self.current_index = 0

    def _advance_to_next(self):
        """Advance to next proposal after action."""
        self.current_index += 1
        if self.current_index < len(self.proposals):
            self.show_proposal(self.current_index)
        else:
            self.current_index = len(self.proposals) - 1
            self.apply_btn.setEnabled(True)

    def apply_and_save(self):
        """Accept all reviewed proposals and close dialog with Accepted result."""
        self.accept()

    def keyPressEvent(self, event):
        """
        Handle keyboard shortcuts for rapid number triage.

        Keys:
            0-8: Select type (0=skip, 1=General, 2=Year, 3=Code/ID, 4=Currency,
                 5=Time, 6=Measure, 7=Ordinal, 8=Range)
            9: Flag with !!FLASH!!
            1-4: Select currency symbol when currency panel is visible
            Enter/Space: Accept current proposal
            Left arrow: Previous proposal
            Right arrow: Next proposal (skip)
            Backspace: Skip (restore original)
        """
        key = event.key()

        # When currency panel visible: 1-4 selects symbol
        if self.currency_group.isVisible() and Qt.Key_1 <= key <= Qt.Key_4:
            symbol_map = {
                Qt.Key_1: "$",
                Qt.Key_2: "£",
                Qt.Key_3: "€",
                Qt.Key_4: "¥",
            }
            self.select_currency(symbol_map[key])
            return

        if key == Qt.Key_9:
            self.flag_number()
            return

        if Qt.Key_0 <= key <= Qt.Key_8:
            self.select_type(key - Qt.Key_0)
            return

        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.accept_proposal()
            return

        if key == Qt.Key_Left:
            self.previous_proposal()
            return

        if key == Qt.Key_Right:
            self.next_proposal()
            return

        if key == Qt.Key_Backspace:
            self.select_type(0)
            return

        super().keyPressEvent(event)

    def get_proposals(self) -> List[Dict]:
        """Return the modified proposals list for passing to apply_proposals()."""
        return self.proposals
