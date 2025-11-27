"""
Add Replace Rule Dialog for AI Changes Review.

PyQt5 modal dialog allowing user to add text replacement rules
to the .data.txt configuration file.
"""

from typing import Optional, Tuple
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..logging import log_message
from ..datafile import append_replace_rule


class AddReplaceDialog(QDialog):
    """
    Modal dialog for adding replacement rules to .data.txt.

    Users enter rules in format: "from text -> to text"
    Rules are appended to the # REPLACE section of .data.txt
    """

    def __init__(self, data_file_path: str = ".data.txt", parent=None):
        """
        Initialize add replace dialog.

        Args:
            data_file_path: Path to .data.txt configuration file
            parent: Parent widget
        """
        super().__init__(parent)

        self.data_file_path = data_file_path
        self.from_text = ""
        self.to_text = ""

        self.setWindowTitle("Add Replacement Rule")
        self.setModal(True)
        self.resize(500, 200)

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout(self)

        # Info section
        info_label = QLabel(
            "Add a new text replacement rule.\n"
            "Format: from text -> to text\n\n"
            "Example: to lead -> to leed"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10pt;")
        main_layout.addWidget(info_label)

        # Input section
        input_label = QLabel("Replacement Rule:")
        input_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(input_label)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("from text -> to text")
        self.input_field.setFont(QFont("Courier", 10))
        self.input_field.returnPressed.connect(self.save_rule)
        main_layout.addWidget(self.input_field)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet(
            "padding: 8px 20px; background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.save_btn.clicked.connect(self.save_rule)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("padding: 8px 20px;")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def save_rule(self):
        """Save replacement rule to .data.txt."""
        rule_text = self.input_field.text().strip()

        if not rule_text:
            QMessageBox.warning(self, "Error", "Please enter a replacement rule.")
            return

        # Validate format: "from -> to"
        if " -> " not in rule_text:
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Rule must be in format: from text -> to text\n\n"
                "Example: to lead -> to leed",
            )
            return

        # Parse the rule
        parts = rule_text.split(" -> ")
        if len(parts) != 2:
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Rule must contain exactly one ' -> ' separator.\n\n"
                "Example: to lead -> to leed",
            )
            return

        from_text = parts[0].strip()
        to_text = parts[1].strip()

        if not from_text or not to_text:
            QMessageBox.warning(
                self, "Error", "Both 'from' and 'to' text must be non-empty."
            )
            return

        # Save to .data.txt
        if append_replace_rule(self.data_file_path, from_text, to_text):
            log_message(f"Added replacement rule: '{from_text}' -> '{to_text}'")
            QMessageBox.information(
                self, "Success", f"Rule saved:\n{from_text} -> {to_text}"
            )
            self.accept()
        else:
            QMessageBox.critical(
                self, "Error", f"Failed to save rule to {self.data_file_path}"
            )
