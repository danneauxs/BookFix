"""
Master AI Changes Review Window.

PyQt5 modal dialog for reviewing and approving/rejecting AI-generated changes.
Displays changes with highlighting, context, and reasoning.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional, TYPE_CHECKING, Tuple
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
    QInputDialog,
    QComboBox,
    QLineEdit,
    QWidget,
    QFormLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from num2words import num2words

if TYPE_CHECKING:
    from .service import BookfixAIService

from .change_tracker import AIChange, AIChangeTracker
from .edit_dialog import EditChangeDialog
from .replace_dialog import AddReplaceDialog
from .numbers_learning import get_numbers_learning
from .choices_learning import ChoicesLearningStorage, ChoiceLearningEntry, ChoicesLearningAnalyzer
from ..logging import log_message

from ..widgets.font_controls import FontControlsWidget
import os


def save_font_settings(font_family: str, font_size: int) -> None:
    """Persist font_family and font_size to data/settings.txt."""
    settings_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "settings.txt"
    )
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = []

        keys = {"font_family": str(font_family), "font_size": str(font_size)}
        updated = {k: False for k in keys}

        for i, line in enumerate(lines):
            for key in keys:
                if line.startswith(f"{key}:"):
                    lines[i] = f"{key}: {keys[key]}\n"
                    updated[key] = True

        for key, val in keys.items():
            if not updated[key]:
                lines.append(f"{key}: {val}\n")

        with open(settings_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except Exception:
        pass


_choices_cache: Dict[str, dict] = {}


def _load_choices_definitions() -> Dict[str, dict]:
    """Load choices.json data once and cache it."""
    global _choices_cache
    if _choices_cache:
        return _choices_cache

    try:
        choices_path = Path(__file__).parent.parent.parent / "data" / "choices.json"
        with open(choices_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for entry in data:
                word = entry.get("word", "")
                if word:
                    _choices_cache[word.lower()] = entry
    except Exception:
        pass

    return _choices_cache


class AIChangesReviewWindow(QDialog):
    """
    Interactive review window for AI changes.

    Displays all AI-generated changes with options to:
    - Accept the change
    - Reject and revert to original
    - Edit/customize the change
    """

    review_completed = pyqtSignal(
        str, dict, AIChangeTracker
    )  # final_text, learning_data, change_tracker
    review_cancelled = pyqtSignal()

    def __init__(
        self,
        change_tracker: AIChangeTracker,
        parent=None,
        show_reasoning: bool = False,
        input_file_path: str = "",
        ai_service: Optional["BookfixAIService"] = None,
    ):
        """
        Initialize review window.

        Args:
            change_tracker: AIChangeTracker with all changes
            parent: Parent widget
            show_reasoning: Show AI reasoning for each change
            input_file_path: Path to input file
            ai_service: AI service for potential reanalysis
        """
        super().__init__(parent)

        self.change_tracker = change_tracker
        self.show_reasoning = show_reasoning
        self.input_file_path = input_file_path
        self.ai_service = ai_service

        # Track decisions
        self.current_index = 0
        self.decisions = {}  # change_id -> decision_dict

        # Learning data to return
        self.learning_data = {"learned_choices": []}

        # Flag to control whether to record learning
        self.record_learning = True

        # Initialize learning storage for homograph choices
        self.learning_storage = ChoicesLearningStorage()
        self.learning_analyzer = ChoicesLearningAnalyzer(self.learning_storage)

        self.setWindowTitle("Review AI Changes")
        self.setModal(True)
        self.resize(1400, 800)

        self.setup_ui()
        self.populate_changes_list()
        if self.change_tracker.changes:
            self.show_change(0)

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout(self)

        # Info label
        info_text = f"Review {len(self.change_tracker.changes)} AI changes. Choose action for each."
        self.info_label = QLabel(info_text)
        self.info_label.setStyleSheet("font-size: 12pt; padding: 10px;")
        main_layout.addWidget(self.info_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(
            len(self.change_tracker.changes) if self.change_tracker.changes else 1
        )
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Main splitter (left/right panels)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Text view
        left_frame = self._create_text_panel()
        splitter.addWidget(left_frame)

        # Right panel - Change info and action buttons
        right_frame = self._create_control_panel()
        splitter.addWidget(right_frame)

        splitter.setSizes([800, 600])

        # Bottom buttons - Three-button layout
        bottom_layout = QHBoxLayout()

        # Green button: Save & Learn (records to history)
        self.save_and_learn_btn = QPushButton("Save & Learn")
        self.save_and_learn_btn.setStyleSheet(
            "font-size: 11pt; padding: 10px; background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.save_and_learn_btn.setToolTip(
            "Apply all changes AND record decisions to learning history"
        )
        self.save_and_learn_btn.clicked.connect(self.save_and_learn)
        bottom_layout.addWidget(self.save_and_learn_btn)

        # Yellow/Orange button: Apply Only (no learning)
        self.apply_only_btn = QPushButton("Apply Only")
        self.apply_only_btn.setStyleSheet(
            "font-size: 11pt; padding: 10px; background-color: #FF9800; color: white; font-weight: bold;"
        )
        self.apply_only_btn.setToolTip(
            "Apply changes to this document only, DO NOT record to learning history"
        )
        self.apply_only_btn.clicked.connect(self.apply_only)
        bottom_layout.addWidget(self.apply_only_btn)

        bottom_layout.addStretch()

        # Red button: Cancel (discard everything)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(
            "font-size: 11pt; padding: 10px; background-color: #f44336; color: white; font-weight: bold;"
        )
        self.cancel_btn.setToolTip("Discard all changes and exit")
        self.cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(bottom_layout)

    def _create_text_panel(self) -> QFrame:
        """Create left panel with text view."""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Header with title and font controls
        header_layout = QHBoxLayout()
        label = QLabel("Text with Changes Highlighted:")
        label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(label)

        # Add font controls
        self.font_controls = FontControlsWidget(initial_family="Arial", initial_size=12)
        self.font_controls.font_changed.connect(self._on_font_changed)
        header_layout.addWidget(self.font_controls)

        layout.addLayout(header_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        # Set initial font from config (will be updated by font controls)
        self.text_edit.setFont(QFont("Arial", 12))
        layout.addWidget(self.text_edit)

        return frame

    def _create_control_panel(self) -> QFrame:
        """Create right panel with controls."""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Changes list
        list_label = QLabel("Changes:")
        list_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(list_label)

        # Filter dropdown
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by source:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "AI Only", "Rules Only"])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        layout.addLayout(filter_layout)

        self.changes_list = QListWidget()
        self.changes_list.itemClicked.connect(self.on_change_item_clicked)
        layout.addWidget(self.changes_list)

        # Current change info
        self.change_info_box = QGroupBox("Current Change")
        info_layout = QVBoxLayout()

        self.module_label = QLabel()
        # Plain text, no bold or special styling
        info_layout.addWidget(self.module_label)

        self.original_label = QLabel()
        # Hidden — no longer displayed in redesigned layout
        self.original_label.setVisible(False)
        info_layout.addWidget(self.original_label)

        # Generic replacement label (for non-number modules; hidden for choices module, shown for numbered)
        self.replacement_label = QLabel()
        self.replacement_label.setStyleSheet("color: #388e3c; font-weight: bold;")
        info_layout.addWidget(self.replacement_label)

        # --- Widgets for 'numbered' module ---
        self.number_details_widget = QWidget()
        number_layout = QFormLayout(self.number_details_widget)
        number_layout.setContentsMargins(0, 0, 0, 0)

        self.number_type_combo = QComboBox()
        self.number_type_combo.addItems(
            [
                "quantity",
                "year",
                "ordinal",
                "identifier",
                "currency",
                "military_time",
                "elapsed_time",
                "measurement",
                "general_number",
            ]
        )

        self.replacement_edit = QLineEdit()

        number_layout.addRow("Type:", self.number_type_combo)
        number_layout.addRow("Suggestion:", self.replacement_edit)
        info_layout.addWidget(self.number_details_widget)
        # --- End of number widgets ---

        self.confidence_label = QLabel()
        # Plain text, no special styling
        info_layout.addWidget(self.confidence_label)

        self.definition_label = QLabel()
        # Plain text for definitions (no color, no italics)
        self.definition_label.setWordWrap(True)
        info_layout.addWidget(self.definition_label)

        if self.show_reasoning:
            self.reasoning_label = QTextEdit()
            self.reasoning_label.setReadOnly(True)
            self.reasoning_label.setMaximumHeight(80)
            self.reasoning_label.setStyleSheet(
                "padding: 5px; background-color: #fff3cd; border: 1px solid #ffc107;"
            )
            info_layout.addWidget(self.reasoning_label)

        self.change_info_box.setLayout(info_layout)
        layout.addWidget(self.change_info_box)

        # Action buttons
        actions_label = QLabel("Choose Action:")
        actions_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(actions_label)

        layout.addWidget(self._create_action_buttons())

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self.previous_change)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.next_change)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        return frame

    def _create_action_buttons(self) -> QGroupBox:
        """Create action buttons in 2x4 grid (40% smaller, no prominent accept button)."""
        from PyQt5.QtWidgets import QGridLayout, QCheckBox

        group = QGroupBox()
        layout = QVBoxLayout()

        # Grid with all action buttons (2 rows of 4)
        grid = QGridLayout()
        grid.setSpacing(5)
        button_style = "padding: 6px; color: white;"  # 40% smaller padding

        # Row 0: Accept | All | Edit | Add Replace (always visible buttons)
        self.accept_btn = QPushButton("1. Accept")
        self.accept_btn.setStyleSheet(
            button_style + "background-color: #4CAF50; font-weight: bold;"
        )
        self.accept_btn.clicked.connect(lambda: self.apply_action("accept"))
        grid.addWidget(self.accept_btn, 0, 0)

        self.accept_all_single_btn = QPushButton("All")
        self.accept_all_single_btn.setStyleSheet(
            button_style + "background-color: #45a049;"
        )
        self.accept_all_single_btn.clicked.connect(
            lambda: self.apply_action("accept_all")
        )
        grid.addWidget(self.accept_all_single_btn, 0, 1)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet(
            button_style + "background-color: #2196F3; font-weight: bold;"
        )
        self.edit_btn.clicked.connect(lambda: self.apply_action("edit"))
        grid.addWidget(self.edit_btn, 0, 2)

        self.add_replace_btn = QPushButton("4. Add Replace")
        self.add_replace_btn.setStyleSheet(button_style + "background-color: #00BCD4;")
        self.add_replace_btn.clicked.connect(lambda: self.apply_action("add_replace"))
        grid.addWidget(self.add_replace_btn, 0, 3)

        # Row 1: Flip | Flip All | Keyword | Add Skip (choices module only)
        self.flip_btn = QPushButton("2. Flip")
        self.flip_btn.setStyleSheet(
            button_style + "background-color: #FF9800; font-weight: bold;"
        )
        # Flip button now opens keyword dialog (and flips option)
        self.flip_btn.clicked.connect(lambda: self._flip_with_keyword())
        grid.addWidget(self.flip_btn, 1, 0)

        # DUPLICATE CREATION - COMMENTED OUT TO FIX NAVIGATION BUG
        # # Row 1: Flip | Flip All | Keyword | Add Skip (choices module only)
        # self.flip_btn = QPushButton("Flip")
        # self.flip_btn.setStyleSheet(
        #     button_style + "background-color: #FF9800; font-weight: bold;"
        # )
        # # Flip button now opens keyword dialog (and flips option)
        # self.flip_btn.clicked.connect(lambda: self._flip_with_keyword())
        # grid.addWidget(self.flip_btn, 1, 0)

        self.flip_all_btn = QPushButton("Flip All")
        self.flip_all_btn.setStyleSheet(button_style + "background-color: #FB8C00;")
        self.flip_all_btn.clicked.connect(lambda: self.apply_action("flip_all"))
        grid.addWidget(self.flip_all_btn, 1, 1)

        self.add_skip_btn = QPushButton("6. Add Skip")
        self.add_skip_btn.setStyleSheet(button_style + "background-color: #009688;")
        self.add_skip_btn.clicked.connect(lambda: self.apply_action("add_skip"))
        grid.addWidget(self.add_skip_btn, 1, 3)

        # Row 2: Special buttons (conditionally shown)
        self.type_btn = QPushButton("Type")
        self.type_btn.setStyleSheet(button_style + "background-color: #673AB7;")
        self.type_btn.clicked.connect(lambda: self.apply_action("number_type"))
        grid.addWidget(self.type_btn, 2, 0)

        self.ignore_btn = QPushButton("Ignore")
        self.ignore_btn.setStyleSheet(button_style + "background-color: #FFA500;")
        self.ignore_btn.clicked.connect(lambda: self.apply_action("ignore"))
        grid.addWidget(self.ignore_btn, 2, 1)

        # Add grid to main layout
        layout.addLayout(grid)
        group.setLayout(layout)
        return group

    def _on_filter_changed(self, text: str):
        """Handle filter dropdown change."""
        self.populate_changes_list()
        # After filtering, try to show the first item in the new list
        if self.changes_list.count() > 0:
            self.on_change_item_clicked(self.changes_list.item(0))
        else:
            # If filter results in empty list, clear the details
            self.module_label.setText("Module: N/A")
            self.original_label.setText("Original: N/A")
            self.replacement_label.setText("Replacement: N/A")
            self.confidence_label.setText("Confidence: N/A")
            self.definition_label.setText("")
            self.text_edit.clear()

    def populate_changes_list(self):
        """Populate the changes list based on the current filter."""
        self.changes_list.clear()
        filter_text = self.filter_combo.currentText()

        # AI sources are 'llm' (incl. from contextualized disagreement routing), 'llm_override'
        ai_sources = {"llm", "llm_override", "llm_contextualized"}

        for i, change in enumerate(self.change_tracker.changes):
            # Determine if the change should be shown
            is_ai_change = change.decision_source in ai_sources
            show = False
            if filter_text == "All":
                show = True
            elif filter_text == "AI Only" and is_ai_change:
                show = True
            elif filter_text == "Rules Only" and not is_ai_change:
                show = True

            if not show:
                continue

            # Determine prefix (checkmark if reviewed)
            prefix = "✓ " if change.user_reviewed else "  "

            # Determine flag based on status
            flag = ""
            if change.user_corrected:
                if change.user_correction == change.original:
                    flag = "[REJECTED]"
                else:
                    flag = "[EDITED]"
            elif change.user_accepted:
                flag = "[ACCEPTED]"
            elif (
                change.user_reviewed
            ):  # Should not happen if corrected/accepted are handled, but as a fallback
                flag = "[REJECTED]"

            # Use user_correction if available, otherwise use AI's replacement
            display_replacement = (
                change.user_correction if change.user_corrected else change.replacement
            )

            # Build item text
            item_text = f"{prefix}{i+1}. {change.original} → {display_replacement} {flag}".strip()
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)  # Store original index

            # Style reviewed items in gray
            if change.user_reviewed:
                item.setForeground(QColor(128, 128, 128))  # Gray for reviewed

            self.changes_list.addItem(item)

        # Update info label with filtered count
        self.info_label.setText(
            f"Showing {self.changes_list.count()} of {len(self.change_tracker.changes)} changes."
        )

        # Select current item if it's in the filtered list
        current_item = self.find_item_by_data(self.current_index)
        if current_item:
            self.changes_list.setCurrentItem(current_item)
        elif self.changes_list.count() > 0:
            # Otherwise select the first item in the filtered list
            self.changes_list.setCurrentRow(0)
            self.on_change_item_clicked(self.changes_list.item(0))

    def find_item_by_data(self, original_index: int) -> Optional[QListWidgetItem]:
        """Find a QListWidgetItem by its stored original index."""
        for i in range(self.changes_list.count()):
            item = self.changes_list.item(i)
            if item.data(Qt.UserRole) == original_index:
                return item
        return None

    def show_change(self, index: int):
        """Display change at given index."""
        if index < 0 or index >= len(self.change_tracker.changes):
            return

        # Disconnect signal from previous item to prevent unwanted triggers
        try:
            self.number_type_combo.currentTextChanged.disconnect()
        except TypeError:
            pass  # Signal was not connected

        self.current_index = index
        change = self.change_tracker.changes[index]

        # Update labels
        source = change.decision_source
        if source in {"llm", "llm_override", "llm_contextualized"}:
            source_text = "AI"
        elif source == "review_needed":
            # Special case for keyword-only / no-decision entries that must be
            # manually reviewed by the user.
            source_text = "Review Needed"
        elif source:
            source_text = f"Rule ({source})"
        else:
            source_text = "Unknown"

        self.module_label.setText(
            f"Module: {change.module.upper()} (Source: {source_text})"
        )
        # Original label hidden in redesigned layout
        self.original_label.setText(f"Original: {change.original}")
        self.confidence_label.setText(f"Confidence: {change.confidence:.1%}")

        # Show definitions for all options from choices.json if available
        definition_text = ""
        if change.module == "choices":
            choices_data = _load_choices_definitions()
            entry = choices_data.get(change.original.lower())
            if entry:
                definitions = []
                for option in entry.get("options", []):
                    spelling = option.get("spelling", "")
                    definition = option.get("definition", "N/A")
                    definitions.append(f"{spelling}: {definition}")
                definition_text = "\n\n".join(definitions)
        self.definition_label.setText(definition_text)

        if self.show_reasoning:
            self.reasoning_label.setPlainText(
                f"Reasoning: {change.reasoning if change.reasoning else 'No reasoning provided'}"
            )

        # Module-specific UI updates
        if change.module == "numbered":
            self.replacement_label.hide()
            self.number_details_widget.show()

            # Populate and set current type
            self.number_type_combo.setCurrentText(change.type)

            # Populate suggestion
            display_replacement = (
                change.user_correction if change.user_corrected else change.replacement
            )
            self.replacement_edit.setText(display_replacement)

            # Connect signal for interactive updates
            self.number_type_combo.currentTextChanged.connect(
                self._on_number_type_changed
            )
        elif change.module == "choices":
            # For choices module, hide replacement label (definitions are shown instead)
            self.replacement_label.hide()
            self.number_details_widget.hide()
        else:
            # For other modules, show replacement label
            self.replacement_label.show()
            self.number_details_widget.hide()
            display_replacement = (
                change.user_correction if change.user_corrected else change.replacement
            )
            self.replacement_label.setText(f"Replacement: {display_replacement}")

        # Update progress bar
        total_changes = len(self.change_tracker.changes)
        self.progress_bar.setMaximum(total_changes if total_changes > 0 else 1)
        self.progress_bar.setValue(index + 1)

        self.highlight_current_change()
        self.update_button_visibility(change)

    def update_button_visibility(self, change: AIChange):
        """Conditionally show/hide module-specific buttons."""
        is_numbered = change.module == "numbered"
        is_choices = change.module == "choices"
        is_allcaps = change.module == "allcaps"

        self.type_btn.setVisible(is_numbered)
        self.flip_btn.setVisible(is_choices)
        self.flip_all_btn.setVisible(is_choices)
        self.add_skip_btn.setVisible(is_choices)
        self.ignore_btn.setVisible(is_allcaps)


    def _on_font_changed(self, font_family: str, font_size: int):
        """Handle font change from font controls."""
        # Update text edit widget font
        self.text_edit.setFont(QFont(font_family, font_size))

        # Save to config file
        save_font_settings(font_family, font_size)

        log_message(f"Font changed to {font_family} {font_size}pt in AI review window")

    def _on_number_type_changed(self, new_type: str):
        """Handle interactive change of a number's type.

        When user changes the dropdown, open the Type dialog to let them
        add keywords and create a boosted learning entry.
        """
        if not self.number_details_widget.isVisible():
            return

        change = self.change_tracker.changes[self.current_index]
        if change.module != "numbered":
            return

        log_message(f"User changed number type for '{change.original}' to '{new_type}'")

        # Store the old type in case user cancels
        old_type = change.type if hasattr(change, "type") else "general_number"

        # Open the Type dialog with the dropdown pre-populated
        # This allows user to add keywords and create a boosted learning entry
        success = self._action_number_type(change, preset_type=new_type)

        if not success:
            # User cancelled the dialog - revert dropdown to old type
            log_message(f"User cancelled type change, reverting to '{old_type}'")
            # Temporarily disconnect signal to avoid recursive call
            try:
                self.number_type_combo.currentTextChanged.disconnect()
            except TypeError:
                pass
            self.number_type_combo.setCurrentText(old_type)
            # Reconnect signal
            self.number_type_combo.currentTextChanged.connect(
                self._on_number_type_changed
            )
        else:
            # Update display to reflect the change
            self.populate_changes_list()

    def highlight_current_change(self):
        """Highlight current change in text view with 25-word context."""
        change = self.change_tracker.changes[self.current_index]

        # Build context display showing AI's replacement
        context_text, highlight_start, highlight_end = self._build_context_display(
            change
        )

        # Set text to context
        self.text_edit.setPlainText(context_text)

        # Clear all previous formatting
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())  # Reset all formatting
        cursor.clearSelection()

        # Highlight the replacement text (not original)
        cursor.setPosition(highlight_start)
        cursor.setPosition(highlight_end, QTextCursor.KeepAnchor)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor(255, 255, 0))  # Yellow
        fmt.setFontWeight(QFont.Bold)

        cursor.setCharFormat(fmt)

        # Scroll to position
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def _build_context_display(self, change: AIChange) -> Tuple[str, int, int]:
        """
        Build context display showing AI's proposed replacement or user's correction.

        Shows 25 words before + replacement (or user correction) + 25 words after.

        Args:
            change: The AIChange to display

        Returns:
            Tuple of (display_text, highlight_start_offset, highlight_end_offset)
        """
        # Use pre-stored context from original text (not current_text)
        # This avoids position misalignment when text has been modified
        before_text = change.context_before
        after_text = change.context_after

        # Trim to last 25 words before / first 25 words after, preserving original whitespace (incl. newlines)
        matches_before = list(re.finditer(r"\S+", before_text))
        if len(matches_before) > 25:
            before_text = before_text[matches_before[-25].start():]
        elif not matches_before:
            before_text = ""

        matches_after = list(re.finditer(r"\S+", after_text))
        if len(matches_after) > 25:
            after_text = after_text[: matches_after[24].end()]
        elif not matches_after:
            after_text = ""

        # Use user_correction if available, otherwise use AI's replacement
        display_replacement = (
            change.user_correction if change.user_corrected else change.replacement
        )

        # Build display: before + [replacement] + after
        if before_text:
            display_text = before_text + " [" + display_replacement + "] " + after_text
        else:
            display_text = "[" + display_replacement + "] " + after_text

        # Calculate highlight positions
        if before_text:
            highlight_start = len(before_text) + 1  # +1 for the space before "["
        else:
            highlight_start = 0

        highlight_start_bracket = highlight_start
        highlight_end = (
            highlight_start_bracket + 1 + len(display_replacement)
        )  # +1 for "["

        return (display_text, highlight_start_bracket + 1, highlight_end)

    def apply_action(self, action: str):
        """Apply chosen action to current change."""
        change = self.change_tracker.changes[self.current_index]

        log_message(
            f"Action '{action}' chosen for change '{change.original}' → '{change.replacement}'"
        )

        if action == "accept":
            self._action_accept_single(change)
        elif action == "accept_all":
            self._action_accept_all(change)
        elif action == "flip":
            log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "gui_debug.log")
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a") as f:
                f.write(f"Flip action started for change {change.original}\n")
            self._action_flip(change)
        elif action == "flip_all":
            self._action_flip_all(change)
        elif action == "ignore":
            self._action_ignore(change)
        elif action == "edit":
            self._action_edit(change)
        elif action == "number_type":
            self._action_number_type(change)
        elif action == "add_replace":
            self._action_add_replace(change)
        elif action == "add_skip":
            self._action_add_skip(change)

        # Update list display and highlight in Changes list
        self.populate_changes_list()

        # For flip action, update the current list item text immediately
        if action == "flip":
            current_item = self.changes_list.currentItem()
            if current_item:
                index = current_item.data(Qt.UserRole)
                if index is not None and 0 <= index < len(self.change_tracker.changes):
                    change = self.change_tracker.changes[index]
                    # Rebuild item text as in populate_changes_list
                    prefix = "✓ " if change.user_reviewed else "  "
                    flag = ""
                    if change.user_corrected:
                        if change.user_correction == change.original:
                            flag = "[REJECTED]"
                        else:
                            flag = "[EDITED]"
                    elif change.user_accepted:
                        flag = "[ACCEPTED]"
                    display_replacement = (
                        change.user_correction if change.user_corrected else change.replacement
                    )
                    item_text = f"{prefix}{index+1}. {change.original} → {display_replacement} {flag}".strip()
                    current_item.setText(item_text)

        # Auto-advance to next unreviewed (except for number_type, add_replace which stay on current)
        # "ignore" now advances since it marks all instances as complete
        if action not in ["number_type", "add_replace"]:
            self.next_change()
        else:
            # Still update current row highlight in Changes list
            self.changes_list.setCurrentRow(self.current_index)

    def _action_accept_single(self, change: AIChange):
        """Accept single change."""
        # If it's a number, the "truth" is in the editable line edit
        if change.module == "numbered":
            final_replacement = self.replacement_edit.text()
            # Only mark as corrected if user actually changed the suggestion
            if final_replacement != change.replacement:
                change.user_correction = final_replacement
                change.user_corrected = True
            else:
                # User accepted without changes - don't set corrected flag
                change.user_corrected = False
        else:
            final_replacement = change.replacement
            change.user_corrected = False

        change.user_reviewed = True
        change.user_accepted = True

        self._record_learning_for_change(change, "accept", final_replacement)
        log_message(f"ACCEPT: '{change.original}' → '{final_replacement}'")

        # Real-time logging
        full_sentence = self._extract_full_sentence(self.change_tracker.original_text, change.original, change.start_pos)
        self._log_review_changes("Accepted", change.original, final_replacement, full_sentence)

    def _action_accept_all(self, change: AIChange):
        """Accept all instances of this original text."""
        affected = self.change_tracker.apply_bulk_decision(change.original, "accept")
        log_message(
            f"ACCEPT ALL: Applied to {affected} instances of '{change.original}'"
        )

    def _action_reject_single(self, change: AIChange):
        """Reject single change."""
        self.decisions[change.id] = {
            "action": "reject",
            "id": change.id,
            "original": change.original,
            "replacement": change.replacement,
        }
        change.user_reviewed = True
        change.user_accepted = False
        change.user_corrected = True
        change.user_correction = change.original

        # Record learning for numbers module
        self._record_learning_for_change(change, "reject", change.original)

        log_message(f"REJECT: Reverted '{change.replacement}' to '{change.original}'")

    def _action_reject_all(self, change: AIChange):
        """Reject all instances of this original text."""
        affected = self.change_tracker.apply_bulk_decision(change.original, "reject")
        log_message(
            f"REJECT ALL: Applied to {affected} instances of '{change.original}'"
        )

    def _action_ignore(self, change: AIChange):
        """Ignore all instances of this original text."""
        affected = self.change_tracker.apply_bulk_decision(change.original, "reject")
        log_message(
            f"IGNORE: Marked {affected} instances of '{change.original}' as rejected"
        )

    def _action_edit(self, change: AIChange):
        """Open edit dialog for custom change."""
        # For numbers, the edit happens directly in the QLineEdit
        if change.module == "numbered":
            # We just need to save the current state of the line edit
            custom_text = self.replacement_edit.text()
            self._apply_custom_edit(change, custom_text, apply_to_all=False)
            # We stay on the current item, so we manually repopulate and show
            self.populate_changes_list()
            self.show_change(self.current_index)
            return

        # For other modules, open the dialog
        dialog = EditChangeDialog(change.original, change.replacement, parent=self)
        dialog.change_saved.connect(
            lambda text, apply_all: self._apply_custom_edit(change, text, apply_all)
        )
        dialog.exec_()

    def _apply_custom_edit(
        self, change: AIChange, custom_text: str, apply_to_all: bool
    ):
        """Apply custom edit to change(s)."""
        if apply_to_all:
            affected = self.change_tracker.apply_bulk_decision(
                change.original, "custom", custom_text
            )
            log_message(
                f"EDIT ALL: Applied custom '{custom_text}' to {affected} instances of '{change.original}'"
            )
        else:
            self.change_tracker.apply_user_correction(change.id, custom_text)
            log_message(f"EDIT: Changed '{change.original}' → '{custom_text}'")

        # NOTE: We do NOT record learning for Edit button
        # Edit is for rare one-off corrections, not patterns to learn
        # Learning should come from Type dropdown (creates boosted entries)

        # Update display
        self.populate_changes_list()
        self.show_change(self.current_index)

    def _get_available_keywords_for_type(self, selected_type: str) -> list:
        """Get all available keywords for a given type, excluding already-used ones."""
        # Keyword suggestions for each type
        keywords_by_type = {
            "measurement": [
                "meters",
                "meter",
                "kilometers",
                "kilometer",
                "centimeters",
                "centimeter",
                "feet",
                "foot",
                "inches",
                "inch",
                "miles",
                "mile",
                "yards",
                "yard",
                "kilograms",
                "kilogram",
                "grams",
                "gram",
                "pounds",
                "pound",
                "ounces",
                "ounce",
                "liters",
                "liter",
                "gallons",
                "gallon",
                "pints",
                "pint",
                "cups",
                "cup",
                "hours",
                "hour",
                "minutes",
                "minute",
                "seconds",
                "second",
                "joules",
                "joule",
                "watts",
                "watt",
                "calories",
                "calorie",
                "degrees",
                "degree",
                "percent",
                "percentage",
            ],
            "currency": [
                "dollars",
                "dollar",
                "cents",
                "cent",
                "pounds",
                "pound",
                "euros",
                "euro",
                "cost",
                "price",
                "paid",
                "pay",
                "charge",
                "fee",
                "bill",
                "invoice",
                "total",
                "tax",
                "tip",
                "balance",
                "amount",
            ],
            "year": [
                "year",
                "years",
                "century",
                "centuries",
                "decade",
                "decades",
                "era",
                "period",
            ],
            "identifier": [
                "model",
                "catalog",
                "designation",
                "serial",
                "version",
                "number",
                "kepler",
                "gliese",
                "ngc",
                "koi",
                "gaia",
                "wasp",
                "trappist",
                "designation",
                "catalog",
                "code",
                "reference",
            ],
            "quantity": [
                "ships",
                "people",
                "soldiers",
                "items",
                "things",
                "units",
                "pieces",
                "cars",
                "trucks",
                "buildings",
                "students",
                "workers",
                "coins",
            ],
            "elapsed_time": [
                "timer",
                "countdown",
                "count-down",
                "remaining",
                "left",
                "elapsed",
                "duration",
                "time-remaining",
                "ticking",
                "countdown-timer",
                "time-left",
            ],
        }

        # Get keywords for selected type
        available = keywords_by_type.get(selected_type, [])

        # Load learning storage to find already-used keywords for this type
        learning_storage = get_numbers_learning()
        used_keywords = set()

        for entry in learning_storage.entries:
            if entry.boost and entry.corrected_classification == selected_type:
                for kw in entry.context_keywords:
                    used_keywords.add(kw.lower())

        # Filter out already-used keywords
        filtered = [kw for kw in available if kw.lower() not in used_keywords]
        return sorted(filtered)  # Alphabetical order

    def _action_number_type(self, change: AIChange, preset_type: str = None):
        """Open dialog to set number type and keywords (boosted learning).

        Args:
            change: The AIChange object to modify
            preset_type: Optional type to pre-select in the dropdown

        Returns:
            bool: True if user saved changes, False if cancelled
        """
        from PyQt5.QtWidgets import (
            QComboBox,
            QLineEdit,
            QListWidget,
            QListWidgetItem,
            QFormLayout,
            QCompleter,
        )

        # Only for numbers (check if original is digit-like)
        if not any(c.isdigit() for c in change.original):
            QMessageBox.information(
                self,
                "Number Type",
                "This action is for numbers only. Please use 'Edit' for other changes.",
            )
            return False

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Set Number Type for '{change.original}'")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)

        layout = QFormLayout()

        # Type selector
        type_combo = QComboBox()
        type_options = [
            "measurement",
            "currency",
            "year",
            "identifier",
            "quantity",
            "general_number",
            "military_time",
            "elapsed_time",
            "ordinal",
        ]
        type_combo.addItems(type_options)

        # Pre-select the type if provided
        if preset_type and preset_type in type_options:
            type_combo.setCurrentText(preset_type)

        layout.addRow("Classification Type:", type_combo)

        # Keywords input with autocomplete
        keywords_input = QLineEdit()
        keywords_input.setPlaceholderText("Type keyword (autocomplete as you type)")

        # Create completer with available keywords
        def update_completer():
            """Updates the completer for the keywords input based on the selected type from a combo box.
            Args:
            None
            Returns:
            None
            """
            selected_type = type_combo.currentText()
            available_keywords = self._get_available_keywords_for_type(selected_type)
            completer = QCompleter(available_keywords)
            completer.setCaseSensitivity(False)
            keywords_input.setCompleter(completer)

        type_combo.currentTextChanged.connect(update_completer)
        update_completer()  # Initialize with default type

        layout.addRow("Context Keyword:", keywords_input)

        # Selected keywords list
        selected_list = QListWidget()
        selected_list.setMaximumHeight(150)
        layout.addRow("Selected Keywords:", selected_list)

        # Add button
        add_kw_layout = QHBoxLayout()
        add_kw_btn = QPushButton("Add Keyword")
        add_kw_btn.setStyleSheet(
            "padding: 5px; background-color: #2196F3; color: white;"
        )

        def add_keyword():
            """Adds a keyword to a list if it's not already present.
            Args:
            None
            Returns:
            None
            """
            keyword = keywords_input.text().strip().lower()
            if keyword and not any(
                selected_list.item(i).text() == keyword
                for i in range(selected_list.count())
            ):
                selected_list.addItem(keyword)
                keywords_input.clear()
                keywords_input.setFocus()

        add_kw_btn.clicked.connect(add_keyword)
        add_kw_layout.addWidget(add_kw_btn)
        add_kw_layout.addStretch()

        remove_kw_btn = QPushButton("Remove Selected")
        remove_kw_btn.setStyleSheet(
            "padding: 5px; background-color: #f44336; color: white;"
        )
        remove_kw_btn.clicked.connect(
            lambda: (
                selected_list.takeItem(selected_list.row(selected_list.currentItem()))
                if selected_list.currentItem()
                else None
            )
        )
        add_kw_layout.addWidget(remove_kw_btn)

        layout.addRow(add_kw_layout)

        # Buttons
        button_layout = QHBoxLayout()

        ok_btn = QPushButton("Save as Boosted")
        ok_btn.setStyleSheet("padding: 8px; background-color: #4CAF50; color: white;")
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("padding: 8px;")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)
        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            selected_type = type_combo.currentText()
            keywords_list = [
                selected_list.item(i).text() for i in range(selected_list.count())
            ]

            # Re-format the number using the selected type
            new_suggestion = self._format_number_helper(change.original, selected_type)

            # Update the change object
            change.type = selected_type
            change.user_correction = new_suggestion
            change.user_corrected = True
            change.user_reviewed = True

            # Update the replacement edit widget if visible
            if self.replacement_edit.isVisible():
                self.replacement_edit.setText(new_suggestion)

            # Store the boosted entry in learning storage
            learning_storage = get_numbers_learning()
            learning_storage.add_boosted_entry(
                original_number=change.original,
                context_before=(
                    change.context_before if hasattr(change, "context_before") else ""
                ),
                context_after=(
                    change.context_after if hasattr(change, "context_after") else ""
                ),
                user_correction=new_suggestion,
                corrected_classification=selected_type,
                context_keywords=keywords_list,
                line_number=0,
            )

            # Save to disk
            try:
                import json

                with open(learning_storage.entries_file, "w", encoding="utf-8") as f:
                    entries_data = []
                    for entry in learning_storage.entries:
                        entry_dict = {
                            "timestamp": entry.timestamp,
                            "original_number": entry.original_number,
                            "context_before": entry.context_before,
                            "context_after": entry.context_after,
                            "original_classification": entry.original_classification,
                            "user_correction": entry.user_correction,
                            "corrected_classification": entry.corrected_classification,
                            "line_number": entry.line_number,
                            "boost": entry.boost,
                            "context_keywords": entry.context_keywords,
                        }
                        entries_data.append(entry_dict)
                    json.dump(
                        {"entries": entries_data}, f, indent=2, ensure_ascii=False
                    )

                QMessageBox.information(
                    self,
                    "Boosted Learning Saved",
                    f"Number '{change.original}' learned as '{selected_type}'\n"
                    f"Keywords: {', '.join(keywords_list) if keywords_list else '(none)'}",
                )
                return True  # Success
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to save boosted entry: {e}"
                )
                return False  # Failed to save
        else:
            # User cancelled dialog
            return False

    def _action_flip(self, change: AIChange):
        """Flip to next alternative option."""
        if len(change.options) < 2:
            QMessageBox.warning(self, "Flip", "No alternative option available")
            return

        try:
            current_idx = change.options.index(change.replacement)
        except ValueError:
            QMessageBox.warning(self, "Flip", "Current replacement not in options list")
            return

        # Cycle to next option
        next_idx = (current_idx + 1) % len(change.options)
        new_replacement = change.options[next_idx]

        # Apply as user correction - UPDATE replacement so display shows new value
        old_replacement = change.replacement
        change.replacement = new_replacement  # UPDATE THIS for display
        change.user_corrected = True
        change.user_correction = new_replacement
        change.user_reviewed = True
        change.user_accepted = True
        log_message(
            f"FLIP: '{change.original}' → '{new_replacement}' (was {old_replacement})"
        )

        # Real-time logging
        full_sentence = self._extract_full_sentence(self.change_tracker.original_text, change.original, change.start_pos)
        self._log_review_changes(f"Flipped (was {old_replacement})", change.original, new_replacement, full_sentence)

        # Advance to next unreviewed item (same as accept does)
        self.next_change()

    def _flip_with_keyword(self):
        """Flip to next alternative option. Learning is deferred to Save & Learn."""
        change = self.change_tracker.changes[self.current_index]
        self._action_flip(change)
        self.populate_changes_list()

    def _action_flip_all(self, change: AIChange):
        """Flip all instances to same alternative option."""
        if len(change.options) < 2:
            QMessageBox.warning(self, "Flip All", "No alternative option available")
            return

        try:
            current_idx = change.options.index(change.replacement)
        except ValueError:
            QMessageBox.warning(
                self, "Flip All", "Current replacement not in options list"
            )
            return

        # Cycle to next option
        next_idx = (current_idx + 1) % len(change.options)
        new_replacement = change.options[next_idx]
        old_replacement = change.replacement

        # Update ALL matching instances to flip them
        matching_changes = self.change_tracker.get_all_changes_by_original(
            change.original
        )
        for matching_change in matching_changes:
            # Update replacement field so display shows flipped value
            matching_change.replacement = new_replacement
            # Mark as corrected
            matching_change.user_corrected = True
            matching_change.user_correction = new_replacement
            matching_change.user_reviewed = True
            matching_change.user_accepted = True

        log_message(
            f"FLIP ALL: Applied {new_replacement} to {len(matching_changes)} instances of '{change.original}' (was {old_replacement})"
        )

    def _auto_extract_and_save_features(self, change: AIChange):
        """Extract and save learning entry from user's homograph choice in review window."""
        # Only save if this is a homograph/choices change
        if change.module != "choices":
            return

        try:
            # Determine user's final choice (correction takes precedence)
            user_choice = change.user_correction if change.user_correction else change.replacement

            # Get lemma (base form of the word)
            lemma = change.original.lower()

            # Create learning entry with decision metadata
            entry = ChoiceLearningEntry.create(
                original_word=change.original,
                lemma=lemma,
                options=change.options,
                context_before=change.context_before,
                context_after=change.context_after,
                user_choice=user_choice,
                line_number=change.original_start,  # Use original position
                pos_tag=change.pos_tag,
                original_decision_source=change.decision_source,
                original_confidence=change.confidence,
                was_user_correction=change.user_corrected,
            )

            # Save the entry
            self.learning_storage.add_learning_entry(entry)
            log_message(
                f"Saved learning entry: {change.original} → {user_choice} "
                f"(source: {change.decision_source}, conf: {change.confidence:.2f}, "
                f"correction: {change.user_corrected})"
            )

        except Exception as e:
            log_message(f"Error saving learning entry for '{change.original}': {e}", level="ERROR")

    def _action_add_replace(self, change: AIChange):
        """Open Add Replace dialog to add rule to data/replace.txt, pre-filled with context."""
        # Build pre-fill string: [word_before] [original] [word_after] -> [word_before] [replacement] [word_after]
        before_words = change.context_before.strip().split()
        after_words = change.context_after.strip().split()

        word_before = before_words[-1] if before_words else ""
        word_after = after_words[0] if after_words else ""

        # Left side: context with original
        left_side_parts = []
        if word_before:
            left_side_parts.append(word_before)
        left_side_parts.append(change.original)
        if word_after:
            left_side_parts.append(word_after)
        left_side = " ".join(left_side_parts)

        # Right side: context with replacement
        right_side_parts = []
        if word_before:
            right_side_parts.append(word_before)
        right_side_parts.append(change.replacement)
        if word_after:
            right_side_parts.append(word_after)
        right_side = " ".join(right_side_parts)

        prefill = f"{left_side} -> {right_side}"

        project_root = Path(__file__).parent.parent.parent
        data_file_path = project_root / "data" / "replace.txt"
        dialog = AddReplaceDialog(str(data_file_path), prefill=prefill, parent=self)
        dialog.exec_()

    def _action_add_skip(self, change: AIChange):
        """Add a phrase to the SKIP_CHOICE list."""
        if change.module != "choices":
            return

        # Construct a suggested phrase from the context
        words_before = change.context_before.split()
        word_before = words_before[-1] if words_before else ""

        words_after = change.context_after.split()
        word_after = words_after[0] if words_after else ""

        # Suggest a two-word phrase, preferring the word after
        if word_after:
            default_phrase = f"{change.original} {word_after}"
        elif word_before:
            default_phrase = f"{word_before} {change.original}"
        else:
            default_phrase = change.original

        # Prompt user for the phrase
        phrase, ok = QInputDialog.getText(
            self,
            "Add Skip Choice Phrase",
            "Enter phrase to skip for this choice:",
            text=default_phrase,
        )

        if ok and phrase:
            project_root = Path(__file__).parent.parent.parent
            skip_file_path = project_root / "data" / "skip_choice.txt"

            try:
                with open(skip_file_path, "a", encoding="utf-8") as f:
                    f.write(f"{phrase}\n")
                log_message(f"Successfully added '{phrase}' to skip_choice.txt.")
                # Update the running context if possible
                if hasattr(self.parent(), "ctx") and hasattr(
                    self.parent().ctx, "skip_choice"
                ):
                    self.parent().ctx.skip_choice.append(phrase)

                # Treat this change as rejected/skipped and advance
                self._action_reject_single(change)
                self.populate_changes_list()
                self.next_change()
            except Exception as e:
                log_message(f"Failed to add '{phrase}' to skip_choice.txt: {e}", level="ERROR")

    def _record_learning_for_change(
        self, change: AIChange, user_action: str, final_result: str = None
    ):
        """Record learning for numbers and choices module changes."""
        # Check if learning is enabled
        if not self.record_learning:
            log_message(
                f"Learning disabled - skipping recording for '{change.original}'",
                level="DEBUG",
            )
            return

        # Determine what the user chose
        if final_result is None:
            final_result = (
                change.replacement if user_action == "accept" else change.original
            )

        # Handle numbers module learning
        if change.module == "numbered":
            return

    def next_change(self):
        """Move to next unreviewed change, wrapping around the list."""
        log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "gui_debug.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"next_change called from index {self.current_index}\n")
        total_changes = len(self.change_tracker.changes)
        start_index = self.current_index

        # Loop through all changes looking for unreviewed item
        for i in range(total_changes):
            # Calculate index with wrapping (loop around)
            next_index = (self.current_index + 1 + i) % total_changes

            change = self.change_tracker.changes[next_index]
            if not change.user_reviewed:
                # Found unreviewed, display it
                self.current_index = next_index
                self.show_change(self.current_index)
                self.changes_list.setCurrentRow(self.current_index)  # Ensure visual highlight updates
                log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "gui_debug.log")
                with open(log_path, "a") as f:
                    f.write(f"Moved to next change at index {self.current_index}\n")
                return  # Exit once found and displayed

        # No unreviewed items found - all items are reviewed
        log_message("All changes have been reviewed")
        self._all_changes_reviewed()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for review actions.

        Keys active only when choices-module buttons are visible (flip/add_skip shown):
          1 = Accept, 2 = Flip, 4 = Add Replace, 6 = Add Skip.
        Always active: 1 = Accept, 4 = Add Replace.
        """
        key = event.key()
        if key == Qt.Key_1:
            self.apply_action("accept")
        elif key == Qt.Key_2 and self.flip_btn.isVisible():
            self._flip_with_keyword()
        elif key == Qt.Key_4:
            self.apply_action("add_replace")
        elif key == Qt.Key_6 and self.add_skip_btn.isVisible():
            self.apply_action("add_skip")
        else:
            super().keyPressEvent(event)

    def _all_changes_reviewed(self):
        """Called when all changes have been reviewed. Waits for user to click Save & Learn or Apply Only."""
        log_message("All changes have been reviewed")

    def _apply_changes_and_close(self):
        """Apply all reviewed changes and close the window."""
        # Apply changes to the change tracker
        for change in self.change_tracker.changes:
            # Only accept changes that were actually reviewed by the user
            # Skipped items (user_reviewed = False) will keep original text
            if change.user_reviewed:
                self.decisions[change.id] = {
                    "action": "accept",
                    "id": change.id,
                    "original": change.original,
                    "replacement": change.replacement,
                }

        final_text = self.change_tracker.build_final_text()
        log_message(f"All changes applied, final text length: {len(final_text)}")
        self.review_completed.emit(final_text, {}, self.change_tracker)
        self.accept()

    def _log_review_changes(self, action_type=None, original=None, replacement=None, full_sentence=None):
        """Log review changes to separate file with full sentence context."""
        import os
        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_path = os.path.join(log_dir, "logs", "review_changes.log")

        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        if action_type and original and replacement and full_sentence:
            # Real-time logging for individual actions
            clean_sentence = " ".join(full_sentence.split())
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{action_type}: '{original}' -> '{replacement}' | Sentence: {clean_sentence}\n")
                f.flush()  # Ensure immediate write
        else:
            # Batch logging for all changes (on close)
            with open(log_path, "a", encoding="utf-8") as f:
                for change in self.change_tracker.changes:
                    original = change.original
                    replacement = change.replacement
                    # Extract full sentence containing the word
                    full_sentence = self._extract_full_sentence(self.change_tracker.original_text, original, change.start_pos)
                    f.write(f"Final: '{original}' -> '{replacement}' | Sentence: {full_sentence}\n")
                f.flush()

    def _extract_full_sentence(self, full_text, word, start_pos):
        """Extract the full sentence containing the word."""
        if not full_text or start_pos < 0:
            return "Context unavailable"

        # Find sentence boundaries (look for periods, question marks, etc.)
        sentence_start = full_text.rfind('.', 0, start_pos) + 1 if '.' in full_text[:start_pos] else 0
        sentence_end = full_text.find('.', start_pos)
        if sentence_end == -1:
            sentence_end = len(full_text)

        sentence = full_text[sentence_start:sentence_end].strip()
        return sentence if sentence else "Context unavailable"

    def previous_change(self):
        """Move to previous change."""
        if self.current_index > 0:
            self.show_change(self.current_index - 1)
            self.changes_list.setCurrentRow(self.current_index)

    def on_change_item_clicked(self, item: QListWidgetItem):
        """Handle change list item click."""
        original_index = item.data(Qt.UserRole)
        if original_index is not None:
            self.show_change(original_index)

    def save_and_learn(self):
        """Save & Learn button handler. Learning is written here, not on individual flips."""
        final_text = self.change_tracker.build_final_text()

        learned_choices = []
        for change in self.change_tracker.changes:
            if change.user_accepted or change.user_reviewed:
                user_choice = change.replacement
                if hasattr(change, 'user_correction') and change.user_correction:
                    user_choice = change.user_correction
                learned_choices.append((change.original, user_choice))
                # Save learning entry now using final state of this change
                self._auto_extract_and_save_features(change)

        self.learning_data['learned_choices'] = learned_choices

        # Extract patterns from all learning entries (including newly saved ones)
        try:
            self.learning_analyzer.analyze_and_update_patterns()
            log_message("Learning patterns updated and synced to POS dictionary")
        except Exception as e:
            log_message(f"Error updating learning patterns: {e}", level="ERROR")

        log_message(f"Review completed with {len(learned_choices)} learned choices saved")
        self.review_completed.emit(final_text, self.learning_data, self.change_tracker)
        self.accept()

    def apply_only(self):
        """Accept all changes but DO NOT record to learning history (yellow/orange button)."""
        for change in self.change_tracker.changes:
            # Only accept changes that were actually reviewed by the user
            # Skipped items (user_reviewed = False) will keep original text
            if change.user_reviewed:
                self.decisions[change.id] = {
                    "action": "accept",
                    "id": change.id,
                    "original": change.original,
                    "replacement": change.replacement,
                }
                # Keep existing user_accepted status (already set by individual actions)

        # Do NOT enable learning
        # self.record_learning = False  # Default is False

        self.populate_changes_list()
        self._apply_changes_and_close()

    # --- Helper functions for number formatting ---
    def _format_number_helper(self, number: str, number_type: str) -> str:
        """Formats a number string into a spoken-word string based on its classified type."""
        try:
            # Handle comma-separated numbers (e.g., "60,000" → "60000")
            number_digits = number.replace(",", "")

            if number_type == "military_time":
                if ":" in number_digits:
                    parts = number_digits.split(":")
                    h, m = int(parts[0]), int(parts[1])
                else:
                    num_val = int(number_digits)
                    h, m = (
                        divmod(num_val, 100) if len(number_digits) > 2 else (num_val, 0)
                    )

                hour_text = "zero " + num2words(h) if h < 10 else num2words(h)
                minute_text = num2words(m)
                if m == 0:
                    minute_text = "hundred"
                elif m < 10:
                    minute_text = "zero " + minute_text

                return f"{hour_text} {minute_text}"

            elif number_type == "year":
                return num2words(int(number_digits), to="year")

            elif number_type == "ordinal":
                num_part = re.sub(r"(st|nd|rd|th)$", "", number_digits)
                return num2words(int(num_part), to="ordinal")

            elif number_type == "identifier":
                # For identifiers, speak only the digits (skip commas)
                return " ".join(list(number_digits))

            elif number_type == "currency":
                return self._format_currency_helper(number)

            elif number_type == "elapsed_time":
                return self._format_elapsed_time_helper(number)

            elif number_type in ["quantity", "measurement", "general_number"]:
                return num2words(int(number_digits))

        except Exception as e:
            log_message(
                f"Failed to format number '{number}' of type '{number_type}': {e}",
                level="WARNING",
            )

        return number  # Fallback to original

    def _format_currency_helper(self, currency_str: str) -> str:
        """Format currency amounts into spoken words."""
        try:
            # Remove spaces and extract symbol
            clean_str = currency_str.replace(" ", "")

            # Currency symbol mapping
            symbol_map = {
                "$": "dollars",
                "¢": "cents",
                "£": "pounds",
                "€": "euros",
                "¥": "yen",
                "₹": "rupees",
            }

            # Find currency symbol
            currency_symbol = None
            currency_name = None
            for symbol, name in symbol_map.items():
                if symbol in clean_str:
                    currency_symbol = symbol
                    currency_name = name
                    break

            # Extract numeric part (remove symbol)
            numeric_str = (
                clean_str.replace(currency_symbol, "") if currency_symbol else clean_str
            )

            # Parse the amount
            if "." in numeric_str:
                # Has decimal part
                parts = numeric_str.split(".")
                dollars = parts[0] if parts[0] else "0"
                cents = parts[1] if len(parts) > 1 else "00"

                dollars_int = int(dollars) if dollars else 0
                cents_int = int(cents) if cents else 0

                # Format with dollars and cents
                if dollars_int > 0 and cents_int > 0:
                    dollars_text = num2words(dollars_int)
                    cents_text = num2words(cents_int)
                    return f"{dollars_text} {currency_name} and {cents_text} cents"
                elif dollars_int > 0:
                    return f"{num2words(dollars_int)} {currency_name}"
                elif cents_int > 0:
                    return f"{num2words(cents_int)} cents"
                else:
                    return "zero dollars"
            else:
                # No decimal, just whole amount
                amount = int(numeric_str) if numeric_str else 0
                if currency_name == "cents":
                    return f"{num2words(amount)} cents"
                else:
                    return f"{num2words(amount)} {currency_name}"
        except Exception as e:
            log_message(
                f"Failed to format currency '{currency_str}': {e}", level="WARNING"
            )
            return currency_str

    def _format_elapsed_time_helper(self, time_str: str) -> str:
        """Format elapsed time (HH:MM:SS or HH:MM) into spoken words."""
        try:
            # Handle colon-separated time format
            if ":" in time_str:
                parts = time_str.split(":")
                hours = int(parts[0]) if parts[0] else 0
                minutes = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                seconds = int(parts[2]) if len(parts) > 2 and parts[2] else 0

                # Build the spoken representation
                result_parts = []

                # Hours
                if hours > 0:
                    hour_text = num2words(hours)
                    result_parts.append(f"{hour_text} hour{'s' if hours != 1 else ''}")

                # Minutes
                if minutes > 0:
                    minute_text = num2words(minutes)
                    result_parts.append(
                        f"{minute_text} minute{'s' if minutes != 1 else ''}"
                    )

                # Seconds
                if seconds > 0:
                    second_text = num2words(seconds)
                    result_parts.append(
                        f"{second_text} second{'s' if seconds != 1 else ''}"
                    )

                # If nothing was specified, return "zero"
                if not result_parts:
                    return "zero"

                # Join with commas and "and"
                if len(result_parts) == 1:
                    return result_parts[0]
                elif len(result_parts) == 2:
                    return f"{result_parts[0]} and {result_parts[1]}"
                else:  # 3 parts
                    return (
                        f"{result_parts[0]}, {result_parts[1]}, and {result_parts[2]}"
                    )
            else:
                # Fallback if no colon format
                return num2words(int(time_str.replace(",", "")))

        except Exception as e:
            log_message(
                f"Failed to format elapsed time '{time_str}': {e}", level="WARNING"
            )
            return time_str
