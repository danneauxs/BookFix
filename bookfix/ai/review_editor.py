"""
Multi-Highlight Text Editor for AI Changes Review.

PyQt5 text editor with color-coded highlights, click navigation,
and keyboard shortcuts for reviewing AI changes.
"""

from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont

from typing import List, Tuple, Optional


class AIReviewTextEditor(QTextEdit):
    """
    Text editor for displaying AI changes. Highlighting is managed by the parent window.
    """

    change_clicked = pyqtSignal(int)  # Emitted when a change is clicked (change_id)

    def __init__(self, parent=None):
        """Initializes a custom editor widget.
        Args:
        parent (QWidget): The parent widget of this editor.
        Returns: None
        """
        super().__init__(parent)
        self._highlight_map: List[Tuple[int, int, int]] = []  # (start, end, change_id)
        self._setup_editor()

    def _setup_editor(self):
        """Configure the text editor."""
        font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        self.setFont(font)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setReadOnly(True)  # Text is built and set by the parent
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.mousePressEvent = self._handle_mouse_press

    def apply_highlights(self, regions: List[Tuple[int, int, QColor, int]]):
        """
        Applies a list of highlights to the document. This is called by the parent window.

        Args:
            regions: A list of tuples, each containing (start, end, color, change_id).
        """
        # Store region boundaries for click detection
        self._highlight_map = [
            (start, end, change_id) for start, end, _, change_id in regions
        ]

        cursor = self.textCursor()

        # Clear all existing formatting from the document
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())

        # Apply the new highlight formats
        for start, end, color, _ in regions:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)

            char_format = QTextCharFormat()
            char_format.setBackground(color)
            cursor.setCharFormat(char_format)

    def _handle_mouse_press(self, event):
        """Handle mouse clicks to find and emit the ID of a clicked change."""
        QTextEdit.mousePressEvent(self, event)
        if event.button() == Qt.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            position = cursor.position()

            # Check if the click position is within any highlighted region
            for start, end, change_id in self._highlight_map:
                if start <= position < end:
                    self.change_clicked.emit(change_id)
                    return  # Stop after finding the first match
