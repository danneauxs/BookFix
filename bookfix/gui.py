"""
PyQt5 GUI interface for Bookfix.

This module provides a modern PyQt5-based interface for the Bookfix application,
replacing the original Tkinter implementation with improved usability and design.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QVBoxLayout,
        QHBoxLayout,
        QWidget,
        QPushButton,
        QTextEdit,
        QLabel,
        QCheckBox,
        QProgressBar,
        QFileDialog,
        QMessageBox,
        QGroupBox,
        QGridLayout,
        QSplitter,
        QButtonGroup,
        QRadioButton,
        QSpinBox,
        QFrame,
        QComboBox,
        QDialog,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QMouseEvent, QPixmap
except ImportError:
    print("PyQt5 not installed. Please install with: pip install PyQt5")
    sys.exit(1)

from .context import BookfixContext
from .logging import log_message

from .pipeline import run_processing, get_available_processors
from .processors.ai_allcaps import AIAllCapsProcessor
from .ai.pipeline import create_ai_pipeline
from .ai.review_window import AIChangesReviewWindow
from .dialogs.heteronym_manager import HeteronymDictionaryManager
from .ai.change_tracker import AIChangeTracker


from .ai.pos_dictionary import get_pos_dictionary


class ProcessingThread(QThread):
    """Thread for running non-interactive processing steps."""

    progress_updated = pyqtSignal(int, int, str)  # current, total, description
    status_updated = pyqtSignal(str)
    processing_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, ctx: BookfixContext, enabled_steps: Dict[str, bool]):
        """Initialize a processing pipeline with context and enabled steps. Args: ctx (BookfixContext): The bookfix context. enabled_steps (Dict[str, bool]): A dictionary of enabled steps. Returns: None"""
        super().__init__()
        self.ctx = ctx
        self.enabled_steps = enabled_steps

    def run(self):
        """Run the processing pipeline in a separate thread."""
        try:
            log_message("Starting processing thread")

            def progress_callback(current: int, total: int, description: str):
                """Triggers callbacks to update progress and status during processing.
                Args:
                current (int): The current progress value.
                total (int): The total progress value.
                description (str): A description of the current step.
                status (str): The current status message.
                Returns: None
                """
                self.progress_updated.emit(current, total, description)

            def status_callback(status: str):
                """Handles the completion of processing by emitting signals and logging messages.
                Args:
                status (str): The final status message to be emitted.
                Returns:
                None
                """
                self.status_updated.emit(status)

            self.ctx = run_processing(
                self.ctx,
                self.enabled_steps,
                progress_callback=progress_callback,
                status_callback=status_callback,
            )

            self.processing_complete.emit()
            log_message("Processing thread completed")

        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            log_message(error_msg, level="ERROR")
            self.error_occurred.emit(error_msg)


class RightClickCheckBox(QCheckBox):
    """Custom checkbox that allows right-click to make it the only checked box."""

    def __init__(self, text: str = "", parent: QWidget = None):
        """Initialize the checkbox."""
        super().__init__(text, parent)
        self.all_checkboxes: List[QCheckBox] = []  # Will be set by the GUI

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events, including right-clicks."""
        if event.button() == Qt.RightButton:
            # Right-click: make this the only checked box
            for checkbox in self.all_checkboxes:
                checkbox.setChecked(False)
            self.setChecked(True)
            event.accept()
        else:
            # Left-click: normal behavior
            super().mousePressEvent(event)


class BookfixMainWindow(QMainWindow):
    """Main application window for Bookfix."""

    def __init__(self):
        """Initializes a Bookfix application instance, setting up context, loading data files, and preparing AI components for processing and GUI state management."""
        super().__init__()
        self.ctx = BookfixContext()
        self._load_data_files()
        self.processing_thread: Optional[ProcessingThread] = None

        # AI processing
        self.ai_pipeline = None

        # GUI state
        self.current_interactive_step: Optional[str] = None
        self.pending_interactive_steps: List[str] = []

        # Track completed processing steps
        self.completed_steps: List[str] = []
        self._initial_enabled_steps: Dict[str, bool] = {}
        self.choice_buttons: List[QPushButton] = []

        self.init_ui()
        self.setup_callbacks()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Bookfix - Ebook Text Processor")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # File selection section
        file_section = self.create_file_section()
        main_layout.addWidget(file_section)

        # Processing options section
        options_section = self.create_options_section()
        main_layout.addWidget(options_section)

        # Main content area with splitter
        content_splitter = QSplitter(Qt.Horizontal)

        # Text display area
        text_widget = self.create_text_section()
        content_splitter.addWidget(text_widget)

        content_splitter.setSizes([800, 400])
        main_layout.addWidget(content_splitter)

        # Status and progress section
        status_section = self.create_status_section()
        main_layout.addWidget(status_section)

        # Action buttons
        button_section = self.create_button_section()
        main_layout.addWidget(button_section)

        # Style the interface
        self.apply_styles()

    def create_file_section(self) -> QGroupBox:
        """Create the file selection section."""
        group = QGroupBox("File Selection")
        layout = QHBoxLayout()

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("font-weight: bold;")

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)

        layout.addWidget(QLabel("File:"))
        layout.addWidget(self.file_label, 1)
        layout.addWidget(self.browse_button)

        # Logo image to the right of Browse button
        logo_path = Path(__file__).resolve().parent.parent / "images" / "DNXSBF.png"
        if logo_path.exists():
            layout.addSpacing(20)
            self.logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    260, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.logo_label.setPixmap(scaled)
            layout.addWidget(self.logo_label)

        group.setLayout(layout)
        return group

    def create_options_section(self) -> QGroupBox:
        """Create the processing options section."""
        group = QGroupBox("Processing Options")
        layout = QGridLayout()

        # Set equal column stretching for balanced layout
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)

        self.checkboxes = {}
        processors = get_available_processors()

        row = 0
        col = 0

        # Define which processors require interaction
        interactive_processors = {"choices", "allcaps", "numbered"}

        # Define which processors should be unchecked by default
        unchecked_by_default = {"blanklines", "lowercase"}

        for processor_name, description in processors.items():
            # Special handling for 'choices' - create a container with AI sub-options
            if processor_name == "choices":
                # Create container widget for choices + AI options
                choices_container = QWidget()
                choices_layout = QVBoxLayout()
                choices_layout.setContentsMargins(0, 0, 0, 0)
                choices_layout.setSpacing(2)

                # Main checkbox
                checkbox = RightClickCheckBox(description)
                checkbox.setChecked(True)
                checkbox.setStyleSheet("color: #0066CC; font-weight: bold;")
                checkbox.setToolTip(
                    "This step requires user interaction (right-click to select alone)"
                )
                self.checkboxes[processor_name] = checkbox
                choices_layout.addWidget(checkbox)

                # AI Reasoning checkbox (indented)
                self.show_ai_reasoning_checkbox = QCheckBox("Show AI Reasoning (Debug)")
                self.show_ai_reasoning_checkbox.setChecked(False)
                self.show_ai_reasoning_checkbox.setToolTip(
                    "Display AI reasoning in the review window (may be verbose)"
                )
                self.show_ai_reasoning_checkbox.setStyleSheet(
                    "font-size: 9px; margin-left: 20px;"
                )
                choices_layout.addWidget(self.show_ai_reasoning_checkbox)

                # AI Mode dropdown with label (indented)
                ai_mode_widget = QWidget()
                ai_mode_layout = QHBoxLayout()
                ai_mode_layout.setContentsMargins(20, 0, 0, 0)
                ai_mode_layout.setSpacing(5)
                ai_mode_label = QLabel("AI Mode:")
                ai_mode_label.setStyleSheet("font-size: 9px;")
                self.ai_mode_combo = QComboBox()
                self.ai_mode_combo.addItems(
                    [
                        "Hybrid (rules + AI)",
                        "Verify ALL (AI checks all)",
                        "Rules ONLY (no AI)",
                    ]
                )
                self.ai_mode_combo.setCurrentIndex(0)  # Default to Hybrid
                self.ai_mode_combo.setToolTip(
                    "Hybrid: AI only when rules are unsure\nVerify ALL: AI checks every decision\nRules ONLY: Use rules only, no AI"
                )
                self.ai_mode_combo.setStyleSheet("font-size: 9px;")
                ai_mode_layout.addWidget(ai_mode_label)
                ai_mode_layout.addWidget(self.ai_mode_combo)
                ai_mode_layout.addStretch()
                ai_mode_widget.setLayout(ai_mode_layout)
                choices_layout.addWidget(ai_mode_widget)

                # Context size dropdown with label (indented)
                context_widget = QWidget()
                context_layout = QHBoxLayout()
                context_layout.setContentsMargins(20, 0, 0, 0)
                context_layout.setSpacing(5)
                context_label = QLabel("Context:")
                context_label.setStyleSheet("font-size: 9px;")
                self.context_size_combo = QComboBox()
                self.context_size_combo.addItems(["50", "100", "250"])
                self.context_size_combo.setCurrentIndex(2)
                self.context_size_combo.setToolTip(
                    "Amount of surrounding text (chars) AI uses for analysis"
                )
                self.context_size_combo.setStyleSheet("font-size: 9px;")
                context_layout.addWidget(context_label)
                context_layout.addWidget(self.context_size_combo)
                context_layout.addStretch()
                context_widget.setLayout(context_layout)
                choices_layout.addWidget(context_widget)

                choices_container.setLayout(choices_layout)
                layout.addWidget(choices_container, row, col)
            else:
                # Normal processor checkbox
                checkbox = RightClickCheckBox(description)
                checkbox.setChecked(processor_name not in unchecked_by_default)

                if processor_name in interactive_processors:
                    checkbox.setStyleSheet("color: #0066CC; font-weight: bold;")
                    checkbox.setToolTip(
                        "This step requires user interaction (right-click to select alone)"
                    )
                else:
                    checkbox.setToolTip("Right-click to select this step alone")

                self.checkboxes[processor_name] = checkbox
                layout.addWidget(checkbox, row, col)

            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1

        # Phonetic analysis checkbox - DISABLED (unreliable results)
        # See phoneticreplacement.txt for details on why this was removed
        self.phonetic_auto_checkbox = QCheckBox(
            "Use Phonetic Analysis (DISABLED - unreliable)"
        )
        self.phonetic_auto_checkbox.setChecked(False)
        self.phonetic_auto_checkbox.setEnabled(False)
        self.phonetic_auto_checkbox.setStyleSheet("color: #888888; font-style: italic;")
        self.phonetic_auto_checkbox.setToolTip(
            "Phonetic analysis disabled due to poor accuracy. Manual interactive choices remain fully functional."
        )

        # Add to layout (new row if needed)
        if col != 0:
            row += 1
        layout.addWidget(self.phonetic_auto_checkbox, row, 0, 1, 3)  # Span 3 columns

        # Set up right-click functionality: each checkbox needs to know about all other checkboxes
        # so it can uncheck them when right-clicked
        all_checkboxes = list(self.checkboxes.values())
        for checkbox in all_checkboxes:
            if isinstance(checkbox, RightClickCheckBox):
                checkbox.all_checkboxes = all_checkboxes

        group.setLayout(layout)
        return group

    def create_text_section(self) -> QWidget:
        """Create the text display section."""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Text Content:"))

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier New", 10))
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        widget.setLayout(layout)
        return widget

    def create_status_section(self) -> QWidget:
        """Create the status and progress section."""
        widget = QWidget()
        layout = QVBoxLayout()

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        widget.setLayout(layout)
        return widget

    def create_button_section(self) -> QWidget:
        """Create the action buttons section."""
        widget = QWidget()
        layout = QHBoxLayout()

        self.start_button = QPushButton("Start Processing")
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setStyleSheet("font-weight: bold; padding: 8px 16px;")

        self.manage_heteronyms_button = QPushButton("Manage Heteronyms")
        self.manage_heteronyms_button.clicked.connect(self.open_heteronym_manager)

        self.analyze_patterns_button = QPushButton("Analyze Patterns")
        self.analyze_patterns_button.clicked.connect(self.launch_pattern_analyzer)
        self.analyze_patterns_button.setToolTip(
            "Analyze learning history and suggest REPLACE/SKIP_CHOICE patterns"
        )

        self.save_button = QPushButton("Save Output")
        self.save_button.clicked.connect(self.save_output)
        self.save_button.setEnabled(False)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        layout.addWidget(self.start_button)
        layout.addWidget(self.manage_heteronyms_button)
        layout.addWidget(self.analyze_patterns_button)
        layout.addStretch()
        layout.addWidget(self.save_button)
        layout.addWidget(self.quit_button)

        widget.setLayout(layout)
        return widget

    def setup_callbacks(self):
        """Setup callbacks. (Traditional processor callbacks removed with dead code cleanup.)"""
        pass

    def apply_styles(self):
        """Apply custom styles to the interface."""
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
            padding: 5px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #e1e1e1;
            border: 1px solid #999999;
            border-radius: 3px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #d4d4d4;
        }
        QPushButton:pressed {
            background-color: #c4c4c4;
        }
        QPushButton:disabled {
            color: #666666;
            background-color: #f0f0f0;
        }
        """
        self.setStyleSheet(style)



    def _on_show_reasoning_changed(self, state):
        """Save show_ai_reasoning setting when checkbox changes."""
        is_checked = state == Qt.Checked
        # save_ai_config_to_data_file removed since .data.txt deleted

    def _on_context_size_changed(self, index):
        """Save context_size setting when dropdown changes."""
        # Map index to size
        sizes = [50, 100, 250]
        context_size = sizes[index]
        # save_ai_config_to_data_file removed since .data.txt deleted

    def browse_file(self):
        """Handle file browser dialog."""
        file_dialog = QFileDialog()

        # Set initial directory
        initial_dir = (
            str(self.ctx.default_directory)
            if self.ctx.default_directory
            else str(Path.home())
        )

        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select file to process",
            initial_dir,
            "Text files (*.txt);;HTML files (*.html *.xhtml);;All files (*.*)",
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """Load a file for processing."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.ctx.text = content
            self.ctx.filepath = file_path
            self.ctx.current_file_path = file_path

            # Clear any pending processing state from previous file
            # This ensures new file starts fresh, not continuing old workflow
            self.pending_interactive_steps = []
            self.pending_steps = []
            self.current_interactive_step = None
            if hasattr(self, "_remaining_traditional_steps"):
                del self._remaining_traditional_steps
            if hasattr(self, "_initial_enabled_steps"):
                del self._initial_enabled_steps

            # Update UI
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setToolTip(file_path)
            self.text_edit.setPlainText(content)
            self.start_button.setEnabled(True)
            self.update_status(f"Loaded file: {os.path.basename(file_path)}")

            # Change working directory
            os.chdir(os.path.dirname(file_path))

            log_message(f"File loaded: {file_path}")

        except Exception as e:
            error_msg = f"Error loading file: {e}"
            log_message(error_msg, level="ERROR")
            QMessageBox.critical(self, "File Error", error_msg)

    def _load_data_files(self):
        """Load replace.txt, skip_choice.txt, cap_ignore.txt, and upper_to_lower.txt into context at startup."""
        import os
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

        # Load replacements from data/replace.txt
        replace_path = os.path.join(data_dir, "replace.txt")
        if os.path.exists(replace_path):
            with open(replace_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if " -> " in line:
                        key, _, val = line.partition(" -> ")
                        self.ctx.replacements[key.strip()] = val.strip()

        # Load skip phrases from data/skip_choice.txt
        skip_path = os.path.join(data_dir, "skip_choice.txt")
        if os.path.exists(skip_path):
            with open(skip_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.ctx.skip_choice.append(line)

        # Load cap ignore list from data/cap_ignore.txt
        cap_ignore_path = os.path.join(data_dir, "cap_ignore.txt")
        if os.path.exists(cap_ignore_path):
            with open(cap_ignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.ctx.cap_ignore.append(line)

        # Load upper-to-lower conversion list from data/upper_to_lower.txt
        upper_to_lower_path = os.path.join(data_dir, "upper_to_lower.txt")
        if os.path.exists(upper_to_lower_path):
            with open(upper_to_lower_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.ctx.upper_to_lower.append(line)

    def get_enabled_steps(self) -> Dict[str, bool]:
        """Get the currently enabled processing steps."""
        return {
            name: checkbox.isChecked() for name, checkbox in self.checkboxes.items()
        }

    def start_processing(self):
        """Start the text processing workflow."""
        # Reload dictionary to pick up any changes
        get_pos_dictionary().reload()

        if not self.ctx.text:
            QMessageBox.warning(
                self, "No File", "Please select a file to process first."
            )
            return

        # Clear any pending state from previous processing run
        # This ensures fresh start even if clicking "Start Processing" multiple times
        self.pending_interactive_steps = []
        self.pending_steps = []
        self.current_interactive_step = None

        enabled_steps = self.get_enabled_steps()

        # AI processing is always used
        self._start_ai_processing(enabled_steps)

    def _start_ai_processing(self, enabled_steps):
        """Start AI-enhanced processing workflow."""
        log_message(
            f"Starting AI-enhanced processing workflow with enabled_steps: {enabled_steps}"
        )

        # Store initial enabled steps for later use
        self._initial_enabled_steps = enabled_steps.copy()

        # Clear log files
        self.clear_log_files()

        # Disable UI during processing
        self.start_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Use SAME processing order as traditional mode - this is the ONLY order
        processing_order = [
            "replacements",
            "periods",
            "blanklines",
            "lowercase",
            "pagination",
            "choices",
            "allcaps",
            "numbered",
        ]

        # Step 1: Run ALL checked automatic processors in order using standard pipeline
        # This ensures replacements, periods, etc. run BEFORE any interactive steps
        automatic_steps = [
            "replacements",
            "periods",
            "blanklines",
            "lowercase",
            "pagination",
        ]
        enabled_auto = {
            step: enabled_steps.get(step, False) for step in automatic_steps
        }

        if any(enabled_auto.values()):
            log_message(
                f"Running automatic processors: {[s for s, v in enabled_auto.items() if v]}"
            )
            self.update_status("Running automatic processors...")

            # Run standard automatic processing
            self.ctx = run_processing(self.ctx, enabled_auto)
            self.update_text_display(self.ctx.text)

            log_message("Automatic processors complete")

        # Step 2: Queue checked interactive processors in correct order
        interactive_steps = ["choices", "allcaps", "numbered"]
        self.pending_interactive_steps = []

        for step in interactive_steps:
            if enabled_steps.get(step, False):
                # Map to the actual handler names used by start_next_interactive_step
                if step == "choices":
                    self.pending_interactive_steps.append("interactive_choices")
                elif step == "allcaps":
                    self.pending_interactive_steps.append("all_caps_processing")
                elif step == "numbered":
                    self.pending_interactive_steps.append("numbered_line_edit")

        log_message(f"Pending interactive steps: {self.pending_interactive_steps}")

        # Step 3: Start first interactive step or complete if none
        if self.pending_interactive_steps:
            log_message("Starting interactive steps")
            self.start_next_interactive_step()
        else:
            log_message("No interactive steps, completing processing")
            self.complete_all_processing()

    def _process_next_step(self):
        """Process the next step in the ordered queue."""
        if not self.pending_steps:
            # All steps complete
            log_message("All processing steps complete")
            self.complete_all_processing()
            return

        # Get next step
        step = self.pending_steps.pop(0)
        log_message(f"Processing step: {step}")

        # Map step names to handlers
        interactive_steps = {
            "choices": "interactive_choices",
            "allcaps": "all_caps_processing",
            "numbered": "numbered_line_edit",
        }

        if step in interactive_steps:
            # Interactive step - call handler directly
            self.pending_interactive_steps = [interactive_steps[step]]
            self.start_next_interactive_step()
        else:
            # Automatic step - run in thread
            step_dict = {step: True}
            self.processing_thread = ProcessingThread(self.ctx, step_dict)
            self.processing_thread.progress_updated.connect(self.on_progress_updated)
            self.processing_thread.status_updated.connect(self.update_status)
            self.processing_thread.processing_complete.connect(self._on_step_complete)
            self.processing_thread.error_occurred.connect(self.on_processing_error)
            self.processing_thread.start()

    def _on_step_complete(self):
        """Handle completion of a single automatic step."""
        self.ctx = self.processing_thread.ctx
        self.update_text_display(self.ctx.text)
        # Process next step
        self._process_next_step()

    def _show_ai_review_window(self):
        """Show the AI changes review window."""
        change_tracker = self.ai_pipeline.get_change_tracker()

        # Get show_reasoning setting from config
        show_reasoning = False
        if hasattr(self.ctx, "ai_config"):
            show_reasoning = self.ctx.ai_config.get("show_ai_reasoning", False)

        # Get AI service for keyword extraction
        ai_service = self.ai_pipeline.get_ai_service() if self.ai_pipeline else None

        # Create and show review window
        review_window = AIChangesReviewWindow(
            change_tracker,
            self,
            show_reasoning=show_reasoning,
            input_file_path=self.ctx.current_file_path,
            ai_service=ai_service,
        )

        # Connect signals
        review_window.review_completed.connect(self._on_ai_review_completed)
        review_window.review_cancelled.connect(self._on_ai_review_cancelled)

        # Show as modal dialog
        review_window.exec_()

    def _on_ai_review_completed(
        self,
        final_text: str,
        learning_data: dict = None,
        change_tracker: AIChangeTracker = None,
    ):
        """Handle completion of AI review."""
        log_message("AI review completed by user")

        # Update context with final reviewed text
        self.ctx.text = final_text
        self.update_text_display(final_text)

        # Log accepted/corrected changes to BookfixContext
        if change_tracker:
            for change in change_tracker.changes:
                if change.user_accepted or change.user_corrected:
                    # Log the change to the main context
                    self.ctx.log_change(
                        change.module,
                        f"{change.original} -> {change.user_correction if change.user_corrected else change.replacement}",
                        len(change.original),
                        len(
                            change.user_correction
                            if change.user_corrected
                            else change.replacement
                        ),
                    )

        # Continue with standard ordered queue flow
        # This ensures all enabled steps run in proper sequence (automatic + interactive)
        # Use QTimer to defer until the review window has fully closed
        log_message("AI review completed, continuing with ordered processing queue")
        QTimer.singleShot(0, self.finish_current_interactive_step)

    # _save_learned_choices_to_learning_system removed — choices learning system retired.
    # Files preserved at .ai_learning/choices_learning.json and choices_patterns.json.

    def _on_ai_review_cancelled(self):
        """Handle cancellation of AI review."""
        log_message("AI review cancelled by user")

        # Restore original text or keep AI changes - let user decide
        reply = QMessageBox.question(
            self,
            "Review Cancelled",
            "Do you want to keep the AI changes or revert to original text?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if reply == QMessageBox.No:
            # Revert to original text
            change_tracker = self.ai_pipeline.get_change_tracker()
            self.ctx.text = change_tracker.original_text
            self.update_text_display(self.ctx.text)

        self.complete_all_processing()

    def clear_log_files(self):
        """Clear debug and log files."""
        from pathlib import Path
        log_dir = Path(__file__).parent / "logs"  # Inline here since gui imports are already heavy
        for filename in [
            "debug.txt",
            "matches.txt",
            "pagination_debug.txt",
        ]:
            try:
                log_file = log_dir / filename
                log_file.write_text("", encoding="utf-8")
            except Exception as e:
                log_message(f"Error clearing {filename}: {e}", level="WARNING")

    def on_progress_updated(self, current: int, total: int, description: str):
        """Handle progress updates from processing thread."""
        progress_percent = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress_percent)
        self.update_status(f"Step {current}/{total}: {description}")

    def on_processing_complete(self):
        """Handle completion of non-interactive processing."""
        self.ctx = self.processing_thread.ctx
        self.update_text_display(self.ctx.text)

        # Start interactive processing if needed
        if self.pending_interactive_steps:
            self.start_next_interactive_step()
        else:
            self.complete_all_processing()

    def on_processing_error(self, error_message: str):
        """Handle processing errors."""
        self.progress_bar.setVisible(False)
        self.start_button.setEnabled(True)
        QMessageBox.critical(self, "Processing Error", error_message)

    def start_next_interactive_step(self):
        """Start the next interactive processing step."""
        from .logging import log_message

        log_message(
            f"GUI: start_next_interactive_step called, pending steps: {self.pending_interactive_steps}"
        )

        if not self.pending_interactive_steps:
            log_message("GUI: No pending interactive steps, completing processing")
            self.complete_all_processing()
            return

        step = self.pending_interactive_steps.pop(0)
        self.current_interactive_step = step
        log_message(f"GUI: Starting interactive step: {step}")

        if step == "interactive_choices":
            log_message("GUI: Starting interactive choices")
            self.start_interactive_choices()
        elif step == "all_caps_processing":
            log_message("GUI: Starting all caps processing")
            self.start_all_caps_processing()
        elif step == "numbered_line_edit":
            log_message("GUI: Starting numbered line edit")
            self.start_numbered_line_edit()
        else:
            log_message(f"GUI: Unknown interactive step: {step}", level="ERROR")

    def start_interactive_choices(self):
        """Start AI-enhanced choices processing with the new review window."""
        from .processors.ai_choices import AIChoiceProcessor
        from .ai.change_tracker import AIChangeTracker
        import os

        log_message("GUI: Starting AI choices processing with new review workflow")

        try:
            # Load homograph choices from choices.json (LexiconLoader) - the modern way
            from bookfix.lexicon_loader import LexiconLoader
            lexicon_loader = LexiconLoader()
            all_words = lexicon_loader.get_all_words()
            log_message(f"GUI: Loaded {len(all_words)} homograph words from choices.json: {all_words}")

            # Populate ctx.choices for the processor (this IS the context the processor uses)
            self.ctx.choices = {}
            self.ctx.choice_definitions = {}
            for word in all_words:
                entry = lexicon_loader.get_homograph(word)
                if entry:
                    # choices: dict of word -> list of spelling options
                    options = entry.get("options", [])
                    self.ctx.choices[word] = [opt.get("spelling", "") for opt in options if opt.get("spelling")]
                    # choice_definitions: rich data from choices.json
                    self.ctx.choice_definitions[word] = entry
            log_message(f"GUI: Populated ctx.choices with {len(self.ctx.choices)} words: {list(self.ctx.choices.keys())}")

            # AI configuration - read from dropdown (Rules ONLY, Hybrid, Verify ALL)
            change_tracker = AIChangeTracker()

            # Load AI provider config from file (replaces deleted .data.txt AI section)
            import json as _json
            import os as _os
            _ai_cfg_path = _os.path.join(_os.path.dirname(__file__), "config", "ai_config.json")
            try:
                with open(_ai_cfg_path) as _f:
                    ai_config = _json.load(_f)
                log_message(f"GUI: Loaded AI config from ai_config.json (provider={ai_config.get('provider')})")
            except (FileNotFoundError, Exception) as _e:
                log_message(f"GUI: Could not load ai_config.json: {_e} — using defaults", level="WARNING")
                ai_config = {"context_size": 250, "show_ai_reasoning": False}

            # Get context size and show_reasoning from config
            context_size = ai_config.get("context_size", 250)
            show_reasoning = ai_config.get("show_ai_reasoning", False)

            # Get AI mode from dropdown (Hybrid, Verify ALL, or Rules ONLY)
            ai_mode_index = self.ai_mode_combo.currentIndex()
            ai_mode_text = self.ai_mode_combo.currentText()

            # Map dropdown selection to AI settings
            if ai_mode_index == 1:  # "Verify ALL (AI checks all)"
                ai_config["ai_enabled"] = True
                ai_config["ai_verify_all"] = True
                log_message(
                    f"GUI: AI Mode set to VERIFY ALL (AI checks every decision)"
                )
            elif ai_mode_index == 2:  # "Rules ONLY (no AI)"
                ai_config["ai_enabled"] = False
                ai_config["ai_verify_all"] = False
                log_message(f"GUI: AI Mode set to RULES ONLY (no AI used)")
            else:  # Default index 0: "Hybrid (rules + AI)"
                ai_config["ai_enabled"] = True
                ai_config["ai_verify_all"] = False
                log_message(f"GUI: AI Mode set to HYBRID (AI only when rules unsure)")

            # DEBUG: Log the final config before passing to processor
            log_message(
                f"GUI: Final AI config before init: ai_enabled={ai_config.get('ai_enabled')}, ai_verify_all={ai_config.get('ai_verify_all')}"
            )

            log_message(
                f"GUI: Creating AIChoiceProcessor with context_size={context_size}, show_reasoning={show_reasoning}"
            )
            ai_processor = AIChoiceProcessor(
                change_tracker=change_tracker,
                context_size=context_size,
                show_reasoning=False,
            )
            log_message(f"GUI: Initializing AI with config: {ai_config}")
            init_result = ai_processor.initialize_ai(ai_config)
            log_message(f"GUI: initialize_ai returned: {init_result}")
            if not init_result:
                log_message(
                    "AI initialization failed for choices processing",
                    level="ERROR",
                )
                QMessageBox.critical(
                    self,
                    "AI Initialization Error",
                    "Failed to initialize AI for choices processing. Please check your AI configuration.",
                )
                self.finish_current_interactive_step()
                return

            log_message(
                f"Starting AI choices analysis for {len(self.ctx.choices)} words..."
            )

            # Show progress indicator
            from PyQt5.QtWidgets import QProgressDialog

            progress = QProgressDialog(
                "AI is analyzing homographs...", "Cancel", 0, 0, self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            try:
                # Safety net: clear all logs before processing
                import os
                import datetime
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                header = f"=== NEW PROCESSING RUN: {timestamp} ===\n"
                for filename in ["rules_choices.log", "rule_reasoning.log"]:
                    path = os.path.join(log_dir, filename)
                    if os.path.exists(path):
                        os.unlink(path)
                    with open(path, "w") as f:
                        f.write(header)

                # This now populates the change_tracker internally
                tracker_result = ai_processor.process_choices_ai_review_mode(
                    self.ctx, force_all=True
                )
            finally:
                progress.close()

            if not tracker_result or not tracker_result.changes:
                log_message("AI made no decisions - no homographs found in text")
                QMessageBox.information(
                    self,
                    "No Homographs Found",
                    "AI analysis complete. No instances of the configured homograph words were found.",
                )
                self.finish_current_interactive_step()
                return

            log_message(
                f"AI analysis complete. {len(tracker_result.changes)} decisions ready for review."
            )

            # Get decision statistics
            self.choice_stats = ai_processor.get_decision_statistics()
            log_message(f"GUI: Got decision stats: {self.choice_stats}")

            # Get show_reasoning setting from config
            show_reasoning = ai_config.get("show_ai_reasoning", False)

            # Get AI service for keyword extraction
            ai_service = ai_processor.ai_service

            # Use the new, correct review window
            review_window = AIChangesReviewWindow(
                tracker_result,
                self,
                show_reasoning=show_reasoning,
                input_file_path=self.ctx.current_file_path,
                ai_service=ai_service,
            )
            review_window.review_completed.connect(self._on_ai_review_completed)
            review_window.review_cancelled.connect(self._on_ai_review_cancelled)
            review_window.exec_()

        except Exception as e:
            log_message(f"AI choices processing failed: {e}", level="ERROR")
            import traceback

            error_details = traceback.format_exc()
            log_message(f"Full error traceback:\n{error_details}", level="ERROR")
            QMessageBox.critical(
                self,
                "AI Processing Error",
                f"AI choices processing failed with error:\n\n{e}",
            )
            self.finish_current_interactive_step()

    def start_all_caps_processing(self):
        """Start AI-enhanced caps processing with CapsReviewEditor."""
        from .logging import log_message
        import json as _json
        import os as _os

        log_message("GUI: Starting AI caps processing")

        try:
            # Load AI config from file (same pattern as choices)
            _ai_cfg_path = _os.path.join(_os.path.dirname(__file__), "config", "ai_config.json")
            try:
                with open(_ai_cfg_path) as _f:
                    ai_config = _json.load(_f)
                log_message(f"GUI: Loaded AI config from ai_config.json (provider={ai_config.get('provider')})")
            except (FileNotFoundError, Exception) as _e:
                log_message(f"GUI: Could not load ai_config.json: {_e} — using defaults", level="WARNING")
                ai_config = {}

            # Get AI mode from dropdown
            ai_mode_index = self.ai_mode_combo.currentIndex()

            # Map dropdown selection to AI settings
            if ai_mode_index == 2:  # Rules ONLY
                ai_config["ai_enabled"] = False
                log_message("GUI: AI Mode set to RULES ONLY (no AI used)")
            elif ai_mode_index == 1:  # Verify ALL
                ai_config["ai_enabled"] = True
                ai_config["ai_verify_all"] = True
                log_message("GUI: AI Mode set to VERIFY ALL for caps")
            else:  # Hybrid (default)
                ai_config["ai_enabled"] = True
                ai_config["ai_verify_all"] = False
                log_message("GUI: AI Mode set to HYBRID for caps")

            ai_processor = AIAllCapsProcessor()

            if ai_config.get("ai_enabled", True):
                if not ai_processor.initialize_ai(ai_config):
                    log_message("AI init failed for caps processing", level="ERROR")
                    QMessageBox.critical(
                        self,
                        "AI Initialization Error",
                        "Failed to initialize AI for caps processing. Please check your AI configuration.",
                    )
                    self.finish_current_interactive_step()
                    return
            else:
                log_message("AI disabled for caps — using learning/rules only")

            log_message("Starting AI all-caps processing...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Processing ALL CAPS sequences with AI...")

            # process_all_caps_sequences_ai opens CapsReviewEditor internally
            self.ctx = ai_processor.process_all_caps_sequences_ai(self.ctx)

            self.update_text_display(self.ctx.text)
            log_message("AI all-caps processing completed")
            self.finish_current_interactive_step()

        except Exception as e:
            log_message(f"AI caps processing failed: {e}", level="ERROR")
            import traceback
            log_message(traceback.format_exc(), level="ERROR")
            QMessageBox.critical(self, "Caps Processing Error", f"Processing failed: {e}")
            self.finish_current_interactive_step()

    def start_numbered_line_edit(self):
        """
        Start improved numbered line processing using RulesOnlyNumberProcessor.

        Uses the purpose-built NumberReviewWindow (type buttons 0-9, keyboard shortcuts,
        currency selector, !!FLASH!! flag) instead of the unified AI review window.
        Flow: propose() → NumberReviewWindow → apply_proposals() → update ctx.text.
        """
        from .logging import log_message
        from .processors.rules_processor import RulesOnlyNumberProcessor
        from .ai.number_review_window import NumberReviewWindow
        from PyQt5.QtWidgets import QProgressDialog

        log_message("GUI: Starting improved numbered line processing with rules engine")

        try:
            processor = RulesOnlyNumberProcessor()

            log_message("Starting numbered proposal generation...")

            progress = QProgressDialog(
                "Analyzing numbered lines...", "Cancel", 0, 0, self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            try:
                ai_mode_index = self.ai_mode_combo.currentIndex()
                if ai_mode_index == 1:
                    _numbers_ai_mode = "ai_only"
                elif ai_mode_index == 2:
                    _numbers_ai_mode = "rules_only"
                else:
                    _numbers_ai_mode = "rules_then_ai"
                _original_lines, proposals = processor.propose(self.ctx.text, ai_mode=_numbers_ai_mode)
            finally:
                progress.close()

            if not proposals:
                log_message("No numbered lines found that need processing")
                QMessageBox.information(
                    self,
                    "No Changes",
                    "No numbered lines needed changes.",
                )
                self.finish_current_interactive_step()
                return

            log_message(f"Generated {len(proposals)} numbered proposals")

            review_window = NumberReviewWindow(
                original_text=self.ctx.text,
                proposals=proposals,
                processor=processor,
                parent=self,
            )
            result = review_window.exec_()

            if result == QDialog.Accepted:
                reviewed_proposals = review_window.get_proposals()
                final_text, applied = processor.apply_proposals(self.ctx.text, reviewed_proposals)
                log_message(f"Applied {len(applied)} numbered changes")
                self.ctx.text = final_text
                self.update_text_display(self.ctx.text)

            self.finish_current_interactive_step()

        except Exception as e:
            log_message(f"Numbered processing failed: {e}", level="ERROR")
            import traceback

            error_details = traceback.format_exc()
            log_message(f"Full error traceback:\n{error_details}", level="ERROR")
            QMessageBox.critical(
                self,
                "Processing Error",
                f"Numbered processing failed: {e}",
            )
            self.finish_current_interactive_step()

    def finish_current_interactive_step(self):
        """Finish the current interactive step and move to next."""
        self.current_interactive_step = None
        self.clear_text_highlighting()
        self.update_text_display(self.ctx.text, preserve_highlighting=False)
        if self.pending_interactive_steps:
            self.start_next_interactive_step()
        elif hasattr(self, "pending_steps") and self.pending_steps:
            self._process_next_step()
        else:
            self.complete_all_processing()

    def complete_all_processing(self):
        """Complete all processing and enable saving."""
        self.progress_bar.setVisible(False)
        self.start_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.update_status("Processing complete. Ready to save output.")

        # Show processing summary
        summary = self.ctx.get_changes_summary()
        log_message("Processing completed successfully")
        log_message(summary)

        # Show completion dialog
        self._show_completion_dialog()

        # Unload AI model if using Ollama
        if self.ai_pipeline:
            ai_service = self.ai_pipeline.get_ai_service()
            if ai_service and ai_service.provider == "ollama":
                log_message("Unloading Ollama model from VRAM.")
                ai_service.unload_model()

    def update_progress(self, current: int, total: int, description: str):
        """Update progress display."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
        self.update_status(description)

    def clear_text_highlighting(self):
        """Clear all text highlighting."""
        # Get the current document
        document = self.text_edit.document()
        cursor = QTextCursor(document)

        # Select all text and clear formatting
        cursor.select(QTextCursor.Document)
        format_default = QTextCharFormat()
        cursor.setCharFormat(format_default)

        # Clear the selection to avoid visual confusion
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    def update_text_display(self, text: str, preserve_highlighting: bool = True):
        """Update the text display."""
        from .logging import log_message

        log_message(
            f"Updating text display (length: {len(text)}, preserve_highlighting: {preserve_highlighting})"
        )

        # Update the text content
        self.text_edit.setPlainText(text)
        self.ctx.text = text  # Keep context in sync

    def update_status(self, status: str):
        """Update status display."""
        self.status_label.setText(status)

    def complete_numbered_edit(self, edits: Dict[int, str]):
        """Complete numbered line editing."""
        # Apply edits handled by the processor
        pass

    def save_output(self):
        """Save the processed text to a file."""
        if not self.ctx.text:
            QMessageBox.warning(self, "No Content", "No processed content to save.")
            return

        # Generate default filename
        if self.ctx.filepath:
            base_name = os.path.splitext(os.path.basename(self.ctx.filepath))[0]
            default_name = f"{base_name}_output.txt"
        else:
            default_name = "bookfix_output.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save processed text",
            default_name,
            "Text files (*.txt);;All files (*.*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.ctx.text)

                QMessageBox.information(
                    self, "File Saved", f"Output saved to:\n{file_path}"
                )
                log_message(f"Output saved to: {file_path}")

            except Exception as e:
                error_msg = f"Error saving file: {e}"
                log_message(error_msg, level="ERROR")
                QMessageBox.critical(self, "Save Error", error_msg)

    def open_heteronym_manager(self):
        """Open the Heteronym Dictionary Manager dialog."""
        dialog = HeteronymDictionaryManager(self)
        dialog.exec_()

    def launch_pattern_analyzer(self):
        """Launch the pattern analyzer GUI to review learning data and suggest patterns."""
        from pathlib import Path
        import subprocess
        import sys

        # Check if learning file exists
        learning_file = Path(".ai_learning/choices_learning.json")
        if not learning_file.exists():
            QMessageBox.warning(
                self,
                "No Learning Data",
                "No learning data found. Process some documents first to build up learning history.",
            )
            return

        # Check if analyzer script exists
        analyzer_script = Path("test/analyze_learning_patterns.py")
        if not analyzer_script.exists():
            QMessageBox.critical(
                self,
                "Analyzer Not Found",
                f"Pattern analyzer script not found at: {analyzer_script}",
            )
            return

        try:
            # Launch the analyzer with GUI (no --no-gui flag)
            # Run in background so main GUI remains responsive
            # Use BookFix project root, not current working directory
            project_root = Path(__file__).parent.parent
            subprocess.Popen(
                [sys.executable, str(analyzer_script), "--min-frequency", "5"],
                cwd=str(project_root),
            )

            log_message("Launched pattern analyzer GUI")

        except Exception as e:
            QMessageBox.critical(
                self, "Launch Failed", f"Failed to launch pattern analyzer:\n{str(e)}"
            )
            log_message(f"Error launching pattern analyzer: {e}", level="ERROR")

    def _show_ai_validation_warning(self, processor):
        """
        Show warning dialog when AI validation fails or partially fails.

        Args:
            processor: The processor object with validation_results attribute
        """
        if not hasattr(processor, 'validation_results'):
            return  # No validation results, nothing to warn about

        results = processor.validation_results
        total = results['total_conversions']
        validated = len(results['validated_indices'])
        unvalidated = total - validated
        chunks_failed = results['chunks_failed']

        if chunks_failed == 0:
            return  # All chunks succeeded, no warning needed

        # Build warning message
        if chunks_failed == results['chunks_attempted']:
            # Complete failure
            title = "❌ AI Validation Failed"
            message = (
                f"AI validation completely failed for {total} Roman numeral conversions.\n\n"
                f"All conversions were kept without AI review.\n\n"
                f"This may result in false positives like:\n"
                f"  • 'Donnie D' → 'Donnie 500'\n"
                f"  • 'MC' → '1100'\n\n"
                f"Chunks attempted: {results['chunks_attempted']}\n"
                f"Chunks succeeded: {results['chunks_succeeded']}\n"
                f"Chunks failed: {chunks_failed}"
            )
        else:
            # Partial failure
            title = "⚠️ AI Validation Partial Failure"
            message = (
                f"AI validation partially failed: {validated}/{total} conversions validated.\n\n"
                f"{unvalidated} conversions were kept without AI review.\n\n"
                f"False positives may exist in unvalidated conversions.\n\n"
                f"Chunks attempted: {results['chunks_attempted']}\n"
                f"Chunks succeeded: {results['chunks_succeeded']}\n"
                f"Chunks failed: {chunks_failed}"
            )

        # Show dialog
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(title)
        msg_box.setInformativeText(message)

        # Add error details if available
        if results['error_messages']:
            detailed_text = "Validation errors:\n"
            for err in results['error_messages'][:5]:
                detailed_text += f"  • {err}\n"
            if len(results['error_messages']) > 5:
                detailed_text += f"  ... and {len(results['error_messages']) - 5} more\n"
            msg_box.setDetailedText(detailed_text)

        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def _show_completion_dialog(self):
        """Show a dialog summarizing which modules completed."""
        # Build list of completed module names
        module_names = {
            "replacements": "Text Replacements",
            "choices": "Word Choices",
            "roman": "Roman Numerals",
            "allcaps": "All Caps",
            "numbered": "Numbered Lines",
            "blanklines": "Blank Lines",
            "period": "Period Processing",
        }

        completed_modules = []
        for step, enabled in self._initial_enabled_steps.items():
            if enabled:
                name = module_names.get(step, step.title())
                completed_modules.append(name)

        if not completed_modules:
            message = "No processing modules were run."
        else:
            message = "Processing completed successfully!\n\nModules processed:\n"
            for module in completed_modules:
                message += f"  ✓ {module}\n"

            # Add change statistics if available
            if self.ctx.changes_log:
                total_changes = len(self.ctx.changes_log)
                message += f"\nTotal changes made: {total_changes}"

            # Add choice decision statistics if available
            if hasattr(self, "choice_stats") and self.choice_stats:
                message += "\n\nChoice Decision Breakdown:\n"
                # Define a more user-friendly mapping for source names
                source_map = {
                    "pos": "Grammar Rules (POS)",
                    "keyword": "Keyword Rules",
                    "semantic": "Semantic Rules",
                    "entity": "Entity Rules",
                    "llm": "AI Analysis",
                    "llm_override": "AI Override",
                    "default": "Default Fallback",
                }
                for source, count in self.choice_stats.items():
                    friendly_name = source_map.get(source, source)
                    message += f"  - {friendly_name}: {count}\n"

        QMessageBox.information(self, "Processing Complete", message)


    def closeEvent(self, event):
        """Handle application close event."""
        # Stop processing thread if running
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.terminate()
            self.processing_thread.wait()

        log_message("Application closing")
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Bookfix")
    app.setOrganizationName("Bookfix")

    # Load configuration and check default directory
    # temp_ctx removed since .data.txt deleted
    temp_ctx = type('obj', (object,), {'default_directory': ''})()

    # Check if default directory needs to be set
    if not temp_ctx.default_directory or not Path(temp_ctx.default_directory).is_dir():
        reply = QMessageBox.question(
            None,
            "Set Default Directory",
            "A default start directory for the file dialog has not been set or is invalid.\n\n"
            "Would you like to select a default directory now?\n\n"
            "Your Calibre Library folder is best, OR a folder you keep your ebook text files.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            initial_dir = str(Path.home())
            directory = QFileDialog.getExistingDirectory(
                None, "Select Default Directory for File Dialog", initial_dir
            )

            if directory:
                QMessageBox.information(
                    None,
                    "Default Directory Set",
                    f"Default directory set to:\n{directory}\n\n(Note: Not saved since .data.txt removed)",
                )
            else:
                # User cancelled, exit
                sys.exit(0)
        else:
            # User chose not to set directory, continue anyway
            pass

    # Create and show main window
    window = BookfixMainWindow()
    window.show()

    log_message("Bookfix PyQt5 application started")

    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
