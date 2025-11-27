"""
Change Edit Dialog for AI Review System.

Dialog for editing individual AI changes with context display,
confidence information, and correction options.
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QDialogButtonBox,
    QGroupBox,
    QProgressBar,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .change_tracker import AIChange


class ChangeEditDialog(QDialog):
    """
    Dialog for editing individual AI changes.

    Shows change context, confidence, and allows user to:
    - Accept the AI change
    - Reject and revert to original
    - Make a custom correction
    """

    # Signals
    change_accepted = pyqtSignal(int)  # change_id
    change_rejected = pyqtSignal(int)  # change_id
    change_corrected = pyqtSignal(int, str)  # change_id, correction

    def __init__(
        self, change: "AIChange", context_info: Optional[str] = None, parent=None
    ):
        super().__init__(parent)

        self.change = change
        self.context_info = context_info
        self.correction_text = ""

        self.setWindowTitle(f"Edit Change - {change.module}")
        self.setModal(True)
        self.resize(600, 550)  # Increased height for new section

        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Header with change info
        self._create_header(layout)

        # Context display
        self._create_context_section(layout)

        # Keyword/Context Analysis display
        self._create_keyword_section(layout)

        # Change details
        self._create_change_section(layout)

        # Correction input
        self._create_correction_section(layout)

        # Action buttons
        self._create_buttons(layout)

    def _create_header(self, parent_layout):
        """Create the header section with change info."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QVBoxLayout(header_frame)

        # Module and timestamp
        module_label = QLabel(f"Module: {self.change.module.title()}")
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        module_label.setFont(font)
        header_layout.addWidget(module_label)

        time_label = QLabel(
            f"Changed: {self.change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        time_label.setStyleSheet("color: gray;")
        header_layout.addWidget(time_label)

        # Confidence bar
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confidence:"))

        confidence_bar = QProgressBar()
        confidence_bar.setRange(0, 100)
        confidence_bar.setValue(int(self.change.confidence * 100))
        confidence_bar.setTextVisible(True)
        confidence_bar.setFormat(f"{self.change.confidence:.2f}")

        # Color based on confidence
        if self.change.confidence >= 0.8:
            confidence_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #4CAF50; }"
            )
        elif self.change.confidence >= 0.6:
            confidence_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #FF9800; }"
            )
        else:
            confidence_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #F44336; }"
            )

        conf_layout.addWidget(confidence_bar)
        header_layout.addLayout(conf_layout)

        parent_layout.addWidget(header_frame)

    def _create_context_section(self, parent_layout):
        """Create the context display section."""
        context_group = QGroupBox("Context")
        context_layout = QVBoxLayout(context_group)

        # Context text with highlighted change
        self.context_display = QTextEdit()
        self.context_display.setMaximumHeight(100)
        self.context_display.setReadOnly(True)

        # Use monospace font for better alignment
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.context_display.setFont(font)

        context_layout.addWidget(self.context_display)

        # Reasoning (if provided)
        if self.change.reasoning:
            reasoning_label = QLabel("AI Reasoning:")
            reasoning_label.setFont(QFont())
            reasoning_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
            context_layout.addWidget(reasoning_label)

            reasoning_text = QLabel(self.change.reasoning)
            reasoning_text.setWordWrap(True)
            reasoning_text.setStyleSheet(
                "color: #555; font-style: italic; margin-left: 10px;"
            )
            context_layout.addWidget(reasoning_text)

        parent_layout.addWidget(context_group)

    def _create_keyword_section(self, parent_layout):
        """Create the keyword/context analysis display section."""
        if not self.context_info:
            return

        keyword_group = QGroupBox("Context Analysis")
        keyword_layout = QVBoxLayout(keyword_group)

        info_label = QLabel(self.context_info)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #333; margin-left: 10px;")
        keyword_layout.addWidget(info_label)

        parent_layout.addWidget(keyword_group)

    def _create_change_section(self, parent_layout):
        """Create the change details section."""
        change_group = QGroupBox("Change Details")
        change_layout = QVBoxLayout(change_group)

        # Original text
        orig_layout = QHBoxLayout()
        orig_layout.addWidget(QLabel("Original:"))

        self.original_display = QLineEdit(self.change.original)
        self.original_display.setReadOnly(True)
        self.original_display.setStyleSheet(
            "background-color: #ffebee; border: 1px solid #ccc;"
        )
        orig_layout.addWidget(self.original_display)

        change_layout.addLayout(orig_layout)

        # AI replacement
        ai_layout = QHBoxLayout()
        ai_layout.addWidget(QLabel("AI Change:"))

        self.ai_display = QLineEdit(self.change.replacement)
        self.ai_display.setReadOnly(True)
        self.ai_display.setStyleSheet(
            "background-color: #e8f5e8; border: 1px solid #ccc;"
        )
        ai_layout.addWidget(self.ai_display)

        change_layout.addLayout(ai_layout)

        parent_layout.addWidget(change_group)

    def _create_correction_section(self, parent_layout):
        """Create the correction input section."""
        correction_group = QGroupBox("Your Correction (Optional)")
        correction_layout = QVBoxLayout(correction_group)

        correction_label = QLabel(
            "Enter your preferred text (e.g., 'Pope John the 4th'), or leave blank to accept/reject:"
        )
        correction_label.setWordWrap(True)
        correction_layout.addWidget(correction_label)

        self.correction_input = QLineEdit()
        self.correction_input.setPlaceholderText(
            "Type your custom text here (e.g., 'Pope John the 4th')..."
        )
        self.correction_input.textChanged.connect(self._on_correction_changed)
        correction_layout.addWidget(self.correction_input)

        # Quick buttons for common actions
        quick_layout = QHBoxLayout()

        use_original_btn = QPushButton("Use Original")
        use_original_btn.clicked.connect(
            lambda: self.correction_input.setText(self.change.original)
        )
        quick_layout.addWidget(use_original_btn)

        use_ai_btn = QPushButton("Use AI Change")
        use_ai_btn.clicked.connect(
            lambda: self.correction_input.setText(self.change.replacement)
        )
        quick_layout.addWidget(use_ai_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self.correction_input.clear())
        quick_layout.addWidget(clear_btn)

        quick_layout.addStretch()
        correction_layout.addLayout(quick_layout)

        parent_layout.addWidget(correction_group)

    def _create_buttons(self, parent_layout):
        """Create the action buttons."""
        button_layout = QHBoxLayout()

        # Accept button
        self.accept_btn = QPushButton("✓ Accept AI Change")
        self.accept_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.accept_btn.clicked.connect(self._accept_change)
        button_layout.addWidget(self.accept_btn)

        # Reject button
        self.reject_btn = QPushButton("✗ Reject & Revert")
        self.reject_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """
        )
        self.reject_btn.clicked.connect(self._reject_change)
        button_layout.addWidget(self.reject_btn)

        # Apply correction button
        self.correct_btn = QPushButton("✎ Apply Correction")
        self.correct_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """
        )
        self.correct_btn.clicked.connect(self._apply_correction)
        self.correct_btn.setEnabled(False)  # Enabled when correction is entered
        button_layout.addWidget(self.correct_btn)

        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        parent_layout.addLayout(button_layout)

    def _populate_data(self):
        """Populate the dialog with change data."""
        # Create context display with highlighting
        context_text = f"{self.change.context_before}[{self.change.original} → {self.change.replacement}]{self.change.context_after}"
        self.context_display.setPlainText(context_text)

        # Highlight the change in context
        cursor = self.context_display.textCursor()
        start_pos = len(self.change.context_before) + 1  # +1 for '['
        end_pos = start_pos + len(f"{self.change.original} → {self.change.replacement}")

        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, cursor.KeepAnchor)

        # Apply highlight format
        format = cursor.charFormat()
        format.setBackground(Qt.yellow)
        cursor.setCharFormat(format)

    def _on_correction_changed(self, text: str):
        """Handle correction text changes."""
        self.correction_text = text.strip()
        self.correct_btn.setEnabled(bool(self.correction_text))

        # Update button text based on correction
        if self.correction_text:
            if self.correction_text == self.change.original:
                self.correct_btn.setText("✓ Use Original")
            elif self.correction_text == self.change.replacement:
                self.correct_btn.setText("✓ Use AI Change")
            else:
                self.correct_btn.setText("✎ Apply Correction")
        else:
            self.correct_btn.setText("✎ Apply Correction")

    def _accept_change(self):
        """Accept the AI change."""
        self.change_accepted.emit(self.change.id)
        self.accept()

    def _reject_change(self):
        """Reject the AI change and revert."""
        self.change_rejected.emit(self.change.id)
        self.accept()

    def _apply_correction(self):
        """Apply user correction."""
        if self.correction_text:
            self.change_corrected.emit(self.change.id, self.correction_text)
            self.accept()

    def get_correction(self) -> str:
        """Get the correction text."""
        return self.correction_text


class QuickActionDialog(QDialog):
    """
    Quick action dialog for batch operations.

    Allows users to quickly accept/reject multiple changes
    or apply actions to all changes of a specific type.
    """

    def __init__(self, changes_by_module: dict, parent=None):
        super().__init__(parent)

        self.changes_by_module = changes_by_module
        self.selected_actions = {}

        self.setWindowTitle("Quick Actions")
        self.setModal(True)
        self.resize(400, 300)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Instructions
        instructions = QLabel("Select actions to apply to all changes of each type:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Module actions
        for module, changes in self.changes_by_module.items():
            if not changes:
                continue

            group = QGroupBox(f"{module.title()} ({len(changes)} changes)")
            group_layout = QHBoxLayout(group)

            accept_all_btn = QPushButton(f"Accept All ({len(changes)})")
            accept_all_btn.clicked.connect(
                lambda checked, m=module: self._set_module_action(m, "accept")
            )
            group_layout.addWidget(accept_all_btn)

            reject_all_btn = QPushButton(f"Reject All ({len(changes)})")
            reject_all_btn.clicked.connect(
                lambda checked, m=module: self._set_module_action(m, "reject")
            )
            group_layout.addWidget(reject_all_btn)

            layout.addWidget(group)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _set_module_action(self, module: str, action: str):
        """Set action for all changes in a module."""
        self.selected_actions[module] = action

        # Update button text to show selection
        for group in self.findChildren(QGroupBox):
            if group.title().startswith(module.title()):
                group.setTitle(f"{module.title()} - {action.title()} All")
                break

    def get_actions(self) -> dict:
        """Get selected actions."""
        return self.selected_actions
