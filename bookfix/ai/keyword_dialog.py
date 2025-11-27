"""
Keyword Management Dialog for AI Changes Review.

PyQt5 modal dialog allowing user to manage context keywords
for word/number pronunciations and save them persistently.
"""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QGroupBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont

from ..logging import log_message
from .pos_dictionary import reset_pos_dictionary


class KeywordManagementDialog(QDialog):
    """
    Modal dialog for managing context keywords for word pronunciations.

    Allows user to:
    - View current pronunciation options and their keywords
    - Add new keywords
    - Remove existing keywords
    - Save keywords to both session and persistent storage
    """

    # Signals (use str instead of Dict for PyQt5 compatibility)
    keywords_updated = pyqtSignal(str)  # word (caller will handle dict separately)

    def __init__(
        self, word: str, current_pronunciation: str, pos_dictionary=None, parent=None
    ):
        """
        Initialize keyword dialog.

        Args:
            word: Word being edited (e.g., "tear")
            current_pronunciation: Current pronunciation (e.g., "teer")
            pos_dictionary: POSDictionary instance for loading/saving
            parent: Parent widget
        """
        super().__init__(parent)

        self.word = word
        self.current_pronunciation = current_pronunciation
        self.pos_dictionary = pos_dictionary

        self.setWindowTitle(f"Manage Keywords - {word}")
        self.setModal(True)
        self.resize(600, 500)

        self.setup_ui()
        self.load_keywords()

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout(self)

        # Info section
        info_layout = QHBoxLayout()

        word_label = QLabel(f"Word: <b>{self.word}</b>")
        word_label.setStyleSheet("font-size: 12pt;")
        info_layout.addWidget(word_label)

        pron_label = QLabel(f"Pronunciation: <b>{self.current_pronunciation}</b>")
        pron_label.setStyleSheet("font-size: 12pt; color: #2196F3;")
        info_layout.addWidget(pron_label)

        info_layout.addStretch()
        main_layout.addLayout(info_layout)

        # Description
        desc_label = QLabel(
            "Context keywords help identify which pronunciation to use.\n"
            "Example: 'tear' + keyword 'through' → use 'tair' (to tear through paper)"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 10pt; padding: 5px;")
        main_layout.addWidget(desc_label)

        # Current keywords section
        keywords_label = QLabel("Current Keywords:")
        keywords_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(keywords_label)

        self.keywords_list = QListWidget()
        self.keywords_list.setMaximumHeight(150)
        main_layout.addWidget(self.keywords_list)

        # Add keyword section
        add_label = QLabel("Add New Keyword:")
        add_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(add_label)

        add_layout = QHBoxLayout()

        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keyword (e.g., 'through', 'rip')")
        self.keyword_input.returnPressed.connect(self.add_keyword)
        add_layout.addWidget(self.keyword_input)

        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet(
            "padding: 5px 15px; background-color: #4CAF50; color: white;"
        )
        self.add_btn.clicked.connect(self.add_keyword)
        add_layout.addWidget(self.add_btn)

        main_layout.addLayout(add_layout)

        # Delete button
        delete_layout = QHBoxLayout()

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setStyleSheet(
            "padding: 5px 15px; background-color: #f44336; color: white;"
        )
        self.delete_btn.clicked.connect(self.delete_keyword)
        delete_layout.addWidget(self.delete_btn)

        delete_layout.addStretch()
        main_layout.addLayout(delete_layout)

        # Bottom buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet(
            "padding: 8px 20px; background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.save_btn.clicked.connect(self.save_keywords)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("padding: 8px 20px;")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def load_keywords(self):
        """Load current keywords from pos_dictionary."""
        self.keywords_list.clear()

        if not self.pos_dictionary:
            return

        try:
            word_info = self.pos_dictionary.get_option_info(
                self.word, self.current_pronunciation
            )
            if word_info:
                keywords = word_info.get("context_keywords", [])
                for keyword in keywords:
                    item = QListWidgetItem(keyword)
                    self.keywords_list.addItem(item)
                log_message(
                    f"Loaded {len(keywords)} keywords for '{self.word}' → '{self.current_pronunciation}'"
                )
        except Exception as e:
            log_message(f"Error loading keywords: {e}", level="ERROR")

    def add_keyword(self):
        """Add a new keyword to the list."""
        keyword = self.keyword_input.text().strip()

        if not keyword:
            log_message("Empty keyword entered", level="WARNING")
            return

        # Check for duplicates
        for i in range(self.keywords_list.count()):
            item = self.keywords_list.item(i)
            if item.text().lower() == keyword.lower():
                log_message(f"Keyword '{keyword}' already exists", level="WARNING")
                return

        # Add to list
        item = QListWidgetItem(keyword)
        self.keywords_list.addItem(item)
        log_message(f"Added keyword: '{keyword}'")

        # Clear input
        self.keyword_input.clear()
        self.keyword_input.setFocus()

    def delete_keyword(self):
        """Delete selected keyword from the list."""
        current_item = self.keywords_list.currentItem()
        if not current_item:
            log_message("No keyword selected for deletion", level="WARNING")
            return

        keyword = current_item.text()
        row = self.keywords_list.row(current_item)
        self.keywords_list.takeItem(row)
        log_message(f"Deleted keyword: '{keyword}'")

    def save_keywords(self):
        """Save keywords to POS dictionary (session + persistent)."""
        if not self.pos_dictionary:
            log_message("No POS dictionary available for saving", level="ERROR")
            return

        try:
            # Get current keywords from list
            current_keywords = []
            for i in range(self.keywords_list.count()):
                item = self.keywords_list.item(i)
                current_keywords.append(item.text())

            # Update pos_dictionary
            word_info = self.pos_dictionary.get_option_info(
                self.word, self.current_pronunciation
            )
            if word_info:
                word_info["context_keywords"] = current_keywords

                # Save to persistent storage
                if self.pos_dictionary.save_dictionary():
                    log_message(
                        f"Saved {len(current_keywords)} keywords to persistent storage for '{self.word}'"
                    )
                    # Reset global dictionary singleton to ensure new keywords are loaded
                    reset_pos_dictionary()
                    self.keywords_updated.emit(self.word)
                    self.accept()
                else:
                    log_message(
                        "Failed to save keywords to persistent storage", level="ERROR"
                    )
            else:
                log_message(
                    f"Word option '{self.word}' → '{self.current_pronunciation}' not found",
                    level="ERROR",
                )

        except Exception as e:
            log_message(f"Error saving keywords: {e}", level="ERROR")
