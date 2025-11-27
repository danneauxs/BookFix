"""
Edit Dialog for AI Changes Review.

PyQt5 modal dialog allowing user to edit proposed changes
with options to save for single instance or all matching instances.
"""

from typing import Optional, Tuple
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QGroupBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..logging import log_message


class EditChangeDialog(QDialog):
    """
    Modal dialog for editing AI proposed changes.

    Allows user to:
    - View and edit the proposed replacement text
    - Save the custom text for single instance
    - Save the custom text for all instances of the same original
    """

    # Signals
    change_saved = pyqtSignal(str, bool)  # (custom_text, apply_to_all)

    def __init__(self, original: str, proposed_replacement: str, parent=None):
        """
        Initialize edit dialog.

        Args:
            original: Original text being changed (e.g., "tear")
            proposed_replacement: AI's proposed replacement (e.g., "teer")
            parent: Parent widget
        """
        super().__init__(parent)

        self.original = original
        self.proposed_replacement = proposed_replacement
        self.result_text = proposed_replacement
        self.apply_to_all = False

        self.setWindowTitle("Edit Change")
        self.setModal(True)
        self.resize(500, 300)

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout(self)

        # Info section
        info_layout = QVBoxLayout()

        original_label = QLabel("Original:")
        original_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(original_label)

        original_text = QLabel(f"  {self.original}")
        original_text.setStyleSheet("color: #d32f2f; padding-left: 10px;")
        info_layout.addWidget(original_text)

        proposed_label = QLabel("Proposed Change:")
        proposed_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        info_layout.addWidget(proposed_label)

        proposed_text = QLabel(f"  {self.proposed_replacement}")
        proposed_text.setStyleSheet("color: #388e3c; padding-left: 10px;")
        info_layout.addWidget(proposed_text)

        main_layout.addLayout(info_layout)

        # Edit section
        edit_label = QLabel("Your Custom Change:")
        edit_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        main_layout.addWidget(edit_label)

        self.edit_widget = QTextEdit()
        self.edit_widget.setPlainText(self.proposed_replacement)
        self.edit_widget.setFont(QFont("Courier", 10))
        self.edit_widget.setMinimumHeight(100)
        main_layout.addWidget(self.edit_widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save (Single)")
        self.save_btn.setStyleSheet(
            "padding: 8px; background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.save_btn.clicked.connect(self.save_single)
        button_layout.addWidget(self.save_btn)

        self.save_all_btn = QPushButton("Save All")
        self.save_all_btn.setStyleSheet(
            "padding: 8px; background-color: #2196F3; color: white; font-weight: bold;"
        )
        self.save_all_btn.clicked.connect(self.save_all)
        button_layout.addWidget(self.save_all_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("padding: 8px;")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def save_single(self):
        """Save custom text for single instance."""
        self.result_text = self.edit_widget.toPlainText()
        self.apply_to_all = False
        log_message(
            f"Edit dialog: Saving single instance change '{self.original}' → '{self.result_text}'"
        )
        self.change_saved.emit(self.result_text, False)
        self.accept()

    def save_all(self):
        """Save custom text for all instances of this original."""
        self.result_text = self.edit_widget.toPlainText()
        self.apply_to_all = True
        log_message(
            f"Edit dialog: Saving all instances change '{self.original}' → '{self.result_text}'"
        )
        self.change_saved.emit(self.result_text, True)
        self.accept()

    def get_result(self) -> Tuple[str, bool]:
        """
        Get the result of the dialog.

        Returns:
            Tuple of (custom_text, apply_to_all)
        """
        return (self.result_text, self.apply_to_all)
