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
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QMouseEvent
except ImportError:
    print("PyQt5 not installed. Please install with: pip install PyQt5")
    sys.exit(1)

from .context import BookfixContext
from .logging import log_message
from .datafile import (
    load_data_file,
    save_default_directory_to_data_file,
    save_cap_ignore_to_data_file,
)
from .pipeline import run_processing, get_available_processors
from .processors.choices import InteractiveChoiceProcessor
from .processors.allcaps import AllCapsProcessor
from .processors.numbered import NumberedLineProcessor
from .processors.ai_allcaps import AIAllCapsProcessor
from .widgets.caps_editor import CapsReviewEditor
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
        super().__init__()
        self.ctx = ctx
        self.enabled_steps = enabled_steps

    def run(self):
        """Run the processing pipeline in a separate thread."""
        try:
            log_message("Starting processing thread")

            def progress_callback(current: int, total: int, description: str):
                self.progress_updated.emit(current, total, description)

            def status_callback(status: str):
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
        super().__init__()
        self.ctx = BookfixContext()
        self.processing_thread: Optional[ProcessingThread] = None

        # Interactive processors
        self.choice_processor = InteractiveChoiceProcessor()
        self.caps_processor = AllCapsProcessor()
        self.numbered_processor = NumberedLineProcessor()

        # AI caps processor
        self.ai_caps_processor = AIAllCapsProcessor()

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
        self.load_configuration()

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

        # Interactive panel (initially hidden)
        self.interactive_panel = self.create_interactive_panel()
        content_splitter.addWidget(self.interactive_panel)
        self.interactive_panel.hide()

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

    def create_interactive_panel(self) -> QWidget:
        """Create the interactive processing panel."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Title
        self.interactive_title = QLabel("Interactive Processing")
        self.interactive_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #0066CC;"
        )
        layout.addWidget(self.interactive_title)

        # Current item info
        self.current_item_label = QLabel("")
        layout.addWidget(self.current_item_label)

        # Choice buttons frame
        self.choice_frame = QFrame()
        choice_layout = QVBoxLayout()
        self.choice_frame.setLayout(choice_layout)
        layout.addWidget(self.choice_frame)

        # Navigation/action buttons
        nav_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.handle_previous)
        self.prev_button.setEnabled(False)

        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.handle_skip)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.skip_button)

        layout.addLayout(nav_layout)

        # Roman numeral legend (hidden by default, shown only during numbers processing)
        self.legend_label = QLabel(
            "Roman Numerals: V=5, X=10, L=50, C=100, D=500, M=1000"
        )
        self.legend_label.setStyleSheet(
            "color: #333; font-size: 12px; font-style: italic;"
        )
        self.legend_label.setVisible(False)  # Hide by default
        layout.addWidget(self.legend_label)

        # Helper text
        self.helper_label = QLabel("")
        self.helper_label.setStyleSheet("color: #666; font-size: 9px;")
        layout.addWidget(self.helper_label)

        layout.addStretch()
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
        """Setup callbacks for interactive processors."""
        # Choice processor callbacks
        self.choice_processor.progress_callback = self.update_progress
        self.choice_processor.choice_display_callback = self.display_choices
        self.choice_processor.text_update_callback = self.update_text_display
        self.choice_processor.status_callback = self.update_status
        self.choice_processor.completion_callback = self._handle_manual_completion
        self.choice_processor.text_edit_widget = (
            self.text_edit
        )  # Give direct access to text widget

        # Caps processor callbacks
        self.caps_processor.choice_display_callback = self.display_caps_choices
        self.caps_processor.text_update_callback = self.update_text_display
        self.caps_processor.status_callback = self.update_status
        self.caps_processor.text_edit_widget = (
            self.text_edit
        )  # Give direct access to text widget

        # Numbered processor callbacks
        self.numbered_processor.line_display_callback = self.display_numbered_line
        self.numbered_processor.navigation_callback = self.update_navigation
        self.numbered_processor.completion_callback = self.complete_numbered_edit
        self.numbered_processor.status_callback = self.update_status

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

    def load_configuration(self):
        """Load configuration from .data.txt file."""
        try:
            self.ctx = load_data_file(self.ctx)
            log_message("Configuration loaded successfully")

            # Debug AI config
            if hasattr(self.ctx, "ai_config"):
                log_message(f"AI Config loaded: {self.ctx.ai_config}")

                # Load UI settings from ai_config
                show_reasoning = self.ctx.ai_config.get("show_ai_reasoning", False)
                self.show_ai_reasoning_checkbox.setChecked(show_reasoning)

                context_size = self.ctx.ai_config.get("context_size", 250)
                # Map context size to combo box index (dropdown shows "50", "100", "250")
                size_map = {50: 0, 100: 1, 250: 2}
                index = size_map.get(context_size, 2)  # Default to 250
                self.context_size_combo.setCurrentIndex(index)

            else:
                log_message("WARNING: No AI config found in context", level="WARNING")

            # Connect change handlers for persistence
            self.show_ai_reasoning_checkbox.stateChanged.connect(
                self._on_show_reasoning_changed
            )
            self.context_size_combo.currentIndexChanged.connect(
                self._on_context_size_changed
            )

        except Exception as e:
            log_message(f"Error loading configuration: {e}", level="ERROR")
            QMessageBox.warning(
                self, "Configuration Error", f"Could not load configuration: {e}"
            )

    def _on_show_reasoning_changed(self, state):
        """Save show_ai_reasoning setting when checkbox changes."""
        from .datafile import save_ai_config_to_data_file

        is_checked = state == Qt.Checked
        save_ai_config_to_data_file("show_ai_reasoning", is_checked)

    def _on_context_size_changed(self, index):
        """Save context_size setting when dropdown changes."""
        from .datafile import save_ai_config_to_data_file

        # Map index to size
        sizes = [50, 100, 250]
        context_size = sizes[index]
        save_ai_config_to_data_file("context_size", context_size)

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

        # Check if AI processing should be used
        use_ai = self._should_use_ai_processing(enabled_steps)

        if use_ai:
            self._start_ai_processing(enabled_steps)
        else:
            self._start_traditional_processing(enabled_steps)

    def _should_use_ai_processing(self, enabled_steps):
        """Determine if AI processing should be used."""
        # AI and traditional now use the same dispatcher - this always returns False
        # The individual steps (choices, allcaps, numbered) check AI config themselves
        return True

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
            "roman",
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
            "roman",
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

            # Check if roman is enabled and needs AI processing
            if enabled_auto.get("roman", False):
                # Initialize AI pipeline for roman processing
                self.ai_pipeline = create_ai_pipeline(self.ctx.ai_config)

                if self.ai_pipeline:
                    # Run non-roman automatic processors first via standard pipeline
                    non_roman_auto = {
                        k: v for k, v in enabled_auto.items() if k != "roman"
                    }
                    if any(non_roman_auto.values()):
                        self.ctx = run_processing(self.ctx, non_roman_auto)
                        self.update_text_display(self.ctx.text)

                    # Then run roman with AI
                    log_message("Running Roman numeral processor with AI")
                    self.ctx = self.ai_pipeline.process_with_ai(self.ctx, ["roman"])
                    self.update_text_display(self.ctx.text)
                else:
                    # Fallback to standard processing if AI init fails
                    log_message(
                        "AI pipeline init failed for roman, using standard processing",
                        level="WARNING",
                    )
                    self.ctx = run_processing(self.ctx, enabled_auto)
                    self.update_text_display(self.ctx.text)
            else:
                # No roman processor, just run standard automatic processing
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

    def _start_traditional_processing(self, enabled_steps):
        """Start traditional (non-AI) processing workflow."""
        log_message("Starting traditional processing workflow")

        # Store initial enabled steps for completion summary
        self._initial_enabled_steps = enabled_steps.copy()

        # Clear log files
        self.clear_log_files()

        # Disable UI during processing
        self.start_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.update_status("Initializing text processing...")

        # Build ordered list of enabled steps - this is the ONLY order
        processing_order = [
            "replacements",
            "periods",
            "roman",
            "blanklines",
            "lowercase",
            "pagination",
            "choices",
            "allcaps",
            "numbered",
        ]

        # Filter to only enabled steps, maintaining order
        self.pending_steps = [
            step for step in processing_order if enabled_steps.get(step, False)
        ]
        log_message(f"GUI: Ordered pending steps: {self.pending_steps}")

        # Start processing from first step
        self._process_next_step()

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

        # Save learned choices to the learning system (NOT .data.txt)
        if learning_data and learning_data.get("learned_choices"):
            self._save_learned_choices_to_learning_system(
                learning_data["learned_choices"]
            )

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

        # Hide interactive panel since AI review is done
        self.interactive_panel.hide()

        # Continue with standard ordered queue flow
        # This ensures all enabled steps run in proper sequence (automatic + interactive)
        # Use QTimer to defer until the review window has fully closed
        log_message("AI review completed, continuing with ordered processing queue")
        QTimer.singleShot(0, self.finish_current_interactive_step)

    def _save_learned_choices_to_learning_system(self, learned_choices: list):
        """
        Save learned choices to the AI learning system (NOT .data.txt).

        Args:
            learned_choices: List of (word, chosen_option) tuples
        """
        if not learned_choices:
            return

        log_message(f"Saving {len(learned_choices)} learned choices to learning system")

        try:
            from .ai.choices_learning import ChoicesLearningStorage

            # Initialize learning storage
            learning_storage = ChoicesLearningStorage()

            # The learned_choices list just has (word, chosen_option)
            # But the learning system needs full context from the change tracker
            # So we get it from the review window's change tracker

            # For now, just log that we're saving them
            # The actual learning happens in the review window via record_manual_choice
            log_message(
                f"✓ Learning data already recorded during review ({len(learned_choices)} choices)"
            )

        except Exception as e:
            log_message(f"ERROR accessing learning system: {e}", level="ERROR")
            import traceback

            log_message(traceback.format_exc(), level="ERROR")

    def _on_ai_review_cancelled(self):
        """Handle cancellation of AI review."""
        log_message("AI review cancelled by user")

        # Hide interactive panel since AI review is done
        self.interactive_panel.hide()

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

        # Continue with remaining processing or complete
        if hasattr(self, "_remaining_traditional_steps"):
            enabled_steps = self._remaining_traditional_steps
            # Mark 'choices' as completed so we don't try to run it again
            self._continue_with_traditional_steps(enabled_steps, ["choices"])
        else:
            self.complete_all_processing()

    def _continue_with_traditional_steps(self, all_enabled_steps, completed_ai_steps):
        """Continue with traditional processing steps after AI processing."""
        # Determine remaining steps that weren't handled by AI
        remaining_steps = {
            k: v
            for k, v in all_enabled_steps.items()
            if k not in completed_ai_steps and v
        }

        # Store for later use
        self._remaining_traditional_steps = remaining_steps

        if not remaining_steps:
            self.complete_all_processing()
            return

        # Determine which remaining steps need interaction
        # Order: choices → numbered → allcaps
        interactive_steps = []
        if remaining_steps.get("choices", False):
            # Choices hasn't been completed yet, add it first
            interactive_steps.append("interactive_choices")
        if remaining_steps.get("numbered", False):
            interactive_steps.append("numbered_line_edit")
        if remaining_steps.get("allcaps", False):
            interactive_steps.append("all_caps_processing")

        self.pending_interactive_steps = interactive_steps

        if interactive_steps:
            # Start interactive processing
            self.start_next_interactive_step()
        else:
            # Run remaining non-interactive steps
            self.processing_thread = ProcessingThread(self.ctx, remaining_steps)
            self.processing_thread.progress_updated.connect(self.on_progress_updated)
            self.processing_thread.status_updated.connect(self.update_status)
            self.processing_thread.processing_complete.connect(
                self.on_processing_complete
            )
            self.processing_thread.error_occurred.connect(self.on_processing_error)
            self.processing_thread.start()

    def clear_log_files(self):
        """Clear debug and log files."""
        for filename in [
            "debug.txt",
            "matches.txt",
            "roman_conversions.log",
            "pagination_debug.txt",
        ]:
            try:
                open(filename, "w").close()
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

        # Show interactive panel
        self.interactive_panel.show()

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
        from .datafile import load_data_file
        import os

        log_message("GUI: Starting AI choices processing with new review workflow")

        try:
            # Load AI configuration
            original_cwd = os.getcwd()
            log_message(f"GUI: Current working directory: {original_cwd}")
            try:
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                log_message(f"GUI: Changing to app_dir: {app_dir}")
                os.chdir(app_dir)
                log_message(f"GUI: Now in: {os.getcwd()}")
                data_ctx = load_data_file()
                ai_config = getattr(data_ctx, "ai_config", None)
                log_message(f"GUI: ai_config loaded: {ai_config}")
            finally:
                os.chdir(original_cwd)

            if not ai_config:
                log_message(
                    "No AI configuration found, falling back to traditional processing",
                    level="WARNING",
                )
                self._start_traditional_choices_processing()
                return

            # Create and initialize AI processor with a new tracker
            change_tracker = AIChangeTracker()
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
                    "AI initialization failed, falling back to traditional processing",
                    level="WARNING",
                )
                self._start_traditional_choices_processing()
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
            QMessageBox.warning(
                self,
                "AI Processing Error",
                f"AI choices processing failed with error:\n\n{e}\n\nFalling back to traditional processing.",
            )
            self._start_traditional_choices_processing()

    def _start_traditional_choices_processing(self):
        """Fallback traditional choices processing without AI."""
        from .logging import log_message

        log_message("Starting traditional interactive choices processing")

        # Set UI labels
        self.interactive_title.setText("Interactive Word Choices")
        self.helper_label.setText(
            "Select the best replacement for each highlighted word."
        )

        # Update text widget with current processed text
        current_widget_text = self.text_edit.toPlainText()
        log_message(f"BEFORE UPDATE: Widget has {len(current_widget_text)} chars")

        # Update the widget
        self.text_edit.setPlainText(self.ctx.text)

        # Force widget refresh
        self.text_edit.update()
        self.text_edit.repaint()

        log_message(
            f"Updated text widget with current processed text ({len(self.ctx.text)} chars)"
        )

        # Start the traditional choice processing
        self.choice_processor.process_choices(self.ctx)

    def _handle_choices_review_completion(self, updated_text: str, review_dialog):
        """Handle completion of choices review window."""
        from .logging import log_message

        log_message("Choices review completed, updating text")

        # Update context with reviewed text
        self.ctx.text = updated_text
        self.text_edit.setPlainText(updated_text)

        # Get correction count for logging
        corrections_made = review_dialog.get_corrections_count()
        if corrections_made > 0:
            log_message(
                f"User made {corrections_made} corrections - saved for learning"
            )

        # Move to next step
        self.finish_current_interactive_step()

    def start_all_caps_processing(self):
        """Start AI-enhanced caps processing with review window."""
        from .logging import log_message
        from .processors.ai_caps import AICapsProcessor
        from .datafile import load_data_file
        import os

        log_message("GUI: Starting AI caps processing")

        # Check if AI is enabled in step settings
        enabled_steps = getattr(self, "enabled_steps", {})
        use_ai = enabled_steps.get("all_caps_processing", {}).get("use_ai", True)

        if not use_ai:
            log_message(
                "AI processing disabled in settings, using traditional caps processing"
            )
            self._start_traditional_caps_processing()
            return

        try:
            # Load configuration from main app directory
            original_cwd = os.getcwd()
            try:
                # Change to app directory to load correct data file
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                os.chdir(app_dir)

                data_ctx = load_data_file()

                # Check if AI config exists
                if not hasattr(data_ctx, "ai_config") or not data_ctx.ai_config:
                    log_message(
                        "No AI configuration found, falling back to traditional processing"
                    )
                    self._start_traditional_caps_processing()
                    return

                ai_config = data_ctx.ai_config
                cap_ignore_list = getattr(data_ctx, "cap_ignore", [])

            finally:
                # Restore original working directory
                os.chdir(original_cwd)

            # Create and initialize AI processor
            ai_processor = AIAllCapsProcessor()

            # Initialize AI
            if not ai_processor.initialize_ai(ai_config):
                log_message(
                    "AI initialization failed, falling back to traditional processing"
                )
                self._start_traditional_caps_processing()
                return

            log_message("Starting AI all-caps processing...")

            # Show progress indicator
            from PyQt5.QtWidgets import QProgressDialog

            progress = QProgressDialog(
                "AI is analyzing all-caps sequences...", "Cancel", 0, 0, self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle("Processing All-Caps")
            progress.show()

            try:
                # Process text with AI (this will show review window)
                original_text = self.ctx.text
                processed_ctx = ai_processor.process_all_caps_sequences_ai(self.ctx)

                # Update context with AI-processed text (review window already shown)
                self.ctx = processed_ctx
                self.text_edit.setPlainText(self.ctx.text)

                log_message("AI caps processing complete with review")
            finally:
                progress.close()

            # Finish this step
            self.finish_current_interactive_step()

        except Exception as e:
            log_message(f"AI processing failed: {e}", level="ERROR")
            QMessageBox.warning(
                self,
                "AI Processing Error",
                f"AI processing failed: {e}\nFalling back to traditional processing.",
            )
            self._start_traditional_caps_processing()

    def _start_traditional_caps_processing(self):
        """Fallback traditional caps processing without AI."""
        from .logging import log_message
        from .datafile import load_data_file
        import re, os

        log_message("Starting traditional caps processing")

        original_text = self.ctx.text

        # Find caps words manually using the same logic as AI processor
        lines = original_text.splitlines()
        caps_words = []

        # Pattern to find ALL CAPS words (2+ letters, not single letters)
        caps_pattern = re.compile(r"\b[A-Z]{2,}\b")

        for idx, line in enumerate(lines):
            spans = []
            for match in caps_pattern.finditer(line):
                spans.append(match.span())

            if spans:
                caps_words.append((idx, line, spans))

        if not caps_words:
            log_message("No ALL CAPS words found in text")
            self.finish_current_interactive_step()
            return

        log_message(f"Found {len(caps_words)} lines with caps words for review")

        # Load CAP_IGNORE list from main app directory
        original_cwd = os.getcwd()
        try:
            # Change to app directory to load correct data file
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(app_dir)

            data_ctx = load_data_file()
            cap_ignore_list = set(getattr(data_ctx, "cap_ignore", []))

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

        review_dialog = CapsReviewEditor(
            original_text, caps_words, cap_ignore_list, parent=self
        )

        # Connect signal to handle completion
        review_dialog.changes_applied.connect(
            lambda updated_text: self._handle_caps_review_completion(
                updated_text, review_dialog
            )
        )

        # Show dialog
        if review_dialog.exec_() == CapsReviewEditor.Accepted:
            # Dialog was accepted, changes should already be applied via signal
            pass
        else:
            # Dialog was cancelled, finish step without changes
            self.finish_current_interactive_step()

    def _handle_caps_review_completion(self, updated_text: str, review_dialog):
        """Handle completion of caps review window."""
        from .logging import log_message

        log_message("Caps review completed, updating text")

        # Update context with reviewed text
        self.ctx.text = updated_text
        self.text_edit.setPlainText(updated_text)

        # Save any updated CAP_IGNORE list back to data file
        updated_cap_ignore_list = review_dialog.get_updated_cap_ignore_list()

        # Load current CAP_IGNORE from main app directory
        import os

        original_cwd = os.getcwd()
        try:
            # Change to app directory to load correct data file
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(app_dir)

            current_data_ctx = load_data_file()
            current_cap_ignore = set(getattr(current_data_ctx, "cap_ignore", []))

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

        # Check if CAP_IGNORE list was updated
        if updated_cap_ignore_list != current_cap_ignore:
            log_message(
                f"Saving updated CAP_IGNORE list with {len(updated_cap_ignore_list)} items"
            )
            save_cap_ignore_to_data_file(list(updated_cap_ignore_list))

        log_message("Caps processing completed successfully")
        self.finish_current_interactive_step()

    def start_numbered_line_edit(self):
        """Start AI-enhanced numbered line processing with review window."""
        from .logging import log_message
        from .processors.ai_numbered import AINumberedLineProcessor
        from .ai.change_tracker import AIChangeTracker
        from .datafile import load_data_file
        import os

        log_message("GUI: Starting AI numbered line processing with review workflow")

        try:
            # Load AI configuration
            original_cwd = os.getcwd()
            try:
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                os.chdir(app_dir)
                data_ctx = load_data_file()
                ai_config = getattr(data_ctx, "ai_config", None)
            finally:
                os.chdir(original_cwd)

            if not ai_config:
                log_message(
                    "No AI configuration found, falling back to traditional numbered processing",
                    level="WARNING",
                )
                self._start_traditional_numbered_processing()
                return

            # Get AI mode from dropdown (Hybrid, Verify ALL, or Rules ONLY)
            ai_mode_index = self.ai_mode_combo.currentIndex()
            ai_mode_text = self.ai_mode_combo.currentText()

            # Check if Rules ONLY mode is selected
            if ai_mode_index == 2:  # "Rules ONLY (no AI)"
                log_message(
                    f"GUI: AI Mode set to RULES ONLY - using rule-based classification only"
                )
                ai_config["ai_enabled"] = False
                ai_config["ai_verify_all"] = False
            else:
                # Hybrid or Verify ALL modes - enable AI
                if ai_mode_index == 1:  # "Verify ALL (AI checks all)"
                    ai_config["ai_enabled"] = True
                    ai_config["ai_verify_all"] = True
                    log_message(f"GUI: AI Mode set to VERIFY ALL")
                else:  # Default index 0: "Hybrid (rules + AI)"
                    ai_config["ai_enabled"] = True
                    ai_config["ai_verify_all"] = False
                    log_message(f"GUI: AI Mode set to HYBRID")

            # Create and initialize AI processor with change tracker
            change_tracker = AIChangeTracker()
            change_tracker.set_text(
                self.ctx.text, self.ctx.text
            )  # Set original text for context display
            show_reasoning = ai_config.get("show_ai_reasoning", False)
            ai_processor = AINumberedLineProcessor(change_tracker=change_tracker)

            # Initialize AI (if enabled) or just use rules
            if ai_config.get("ai_enabled", True):
                if not ai_processor.initialize_ai(ai_config):
                    log_message(
                        "AI initialization failed for numbered processor, falling back to traditional"
                    )
                    self._start_traditional_numbered_processing()
                    return
            else:
                log_message(
                    "AI disabled for numbered processor - using rule-based classification only"
                )
                # Set a flag so processor knows to skip AI
                ai_processor.rules_only_mode = True

            # Setup per-file logging
            ai_processor._setup_numbered_log(self.ctx.current_file_path)

            log_message("Starting AI numbered analysis...")

            # Show progress indicator
            from PyQt5.QtWidgets import QProgressDialog

            progress = QProgressDialog(
                "AI is analyzing numbered lines...", "Cancel", 0, 0, self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            try:
                # Process with review mode (populates change_tracker)
                tracker_result = ai_processor.process_numbers_ai_review_mode(self.ctx)
            finally:
                progress.close()

            if not tracker_result or not tracker_result.changes:
                log_message("AI made no numbered line changes")
                QMessageBox.information(
                    self,
                    "No Changes",
                    "AI analysis complete. No numbered lines needed changes.",
                )
                self.finish_current_interactive_step()
                return

            log_message(
                f"AI analysis complete. {len(tracker_result.changes)} numbered changes ready for review."
            )

            # Get AI service for keyword extraction
            ai_service = self.ai_pipeline.get_ai_service() if self.ai_pipeline else None

            # Show review window
            review_window = AIChangesReviewWindow(
                tracker_result,
                self,
                show_reasoning=show_reasoning,
                input_file_path=self.ctx.current_file_path,
                ai_service=ai_service,
            )
            review_window.review_completed.connect(self._on_numbered_review_completed)
            review_window.review_cancelled.connect(self._on_numbered_review_cancelled)
            review_window.exec_()

        except Exception as e:
            log_message(f"AI numbered processing failed: {e}", level="ERROR")
            import traceback

            error_details = traceback.format_exc()
            log_message(f"Full error traceback:\n{error_details}", level="ERROR")
            QMessageBox.warning(
                self,
                "AI Processing Error",
                f"AI numbered processing failed: {e}\nFalling back to traditional processing.",
            )
            self._start_traditional_numbered_processing()

    def _start_traditional_numbered_processing(self):
        """Start traditional (non-AI) numbered line processing."""
        from .logging import log_message

        log_message("Starting traditional numbered line processing")

        # Initialize traditional numbered processor
        if not hasattr(self, "numbered_processor"):
            from .processors.numbered import NumberedLineProcessor

            self.numbered_processor = NumberedLineProcessor()

        # Set up callbacks
        self.numbered_processor.line_display_callback = self.display_numbered_line
        self.numbered_processor.navigation_callback = (
            lambda current, total: self.update_status(f"Editing line {current}/{total}")
        )
        self.numbered_processor.status_callback = self.update_status

        # Start the numbered line editing process
        if not self.numbered_processor.start_numbered_line_edit(self.ctx):
            # No numbered lines found
            QMessageBox.information(
                self, "No Numbered Lines", "No lines with 3+ digit numbers found."
            )
            self.finish_current_interactive_step()
            return

        # Show interactive panel - the callback will display the first line
        self.interactive_panel.show()

    def _on_numbered_review_completed(self, final_text: str, learning_data: dict):
        """Handle when numbered line review is completed."""
        from .logging import log_message

        log_message(
            f"GUI: Numbered review completed, updating context with {len(final_text)} chars"
        )

        # Update the context with the reviewed text
        self.ctx.text = final_text

        # Update the main text display
        self.update_text_display(self.ctx.text)

        # Move to next step
        self.finish_current_interactive_step()

    def _on_numbered_review_cancelled(self):
        """Handle when numbered review is cancelled."""
        from .logging import log_message

        log_message("GUI: Numbered review cancelled")

        # Move to next step without changes
        self.finish_current_interactive_step()

    def _on_numbered_editing_completed(self, final_text: str):
        """Handle when numbered editing is completed."""
        from .logging import log_message

        log_message(
            f"GUI: Numbered editing completed, updating context with {len(final_text)} chars"
        )

        # Update the context with the edited text
        self.ctx.text = final_text

        # Update the main text display
        self.update_text_display(self.ctx.text)

        # Move to next step
        self.finish_current_interactive_step()

    def _on_numbered_editing_cancelled(self):
        """Handle when numbered editing is cancelled."""
        from .logging import log_message

        log_message("GUI: Numbered editing cancelled")

        # Move to next step without changes
        self.finish_current_interactive_step()

    def display_choices(self, word: str, options: List[str]):
        """Display choice options for interactive processing."""
        self.current_item_label.setText(f"Word: '{word}'")

        # Clear existing choices
        layout = self.choice_frame.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # Store choice buttons for keyboard access
        self.choice_buttons = []

        # Add choice buttons
        for i, option in enumerate(options):
            button = QPushButton(f"{i+1}. {option}")
            button.clicked.connect(
                lambda checked, opt=option: self.handle_choice_selection(opt)
            )

            # Add keyboard shortcut
            if i < 9:  # Support keys 1-9
                button.setShortcut(f"{i+1}")
                button.setToolTip(f"Press {i+1} or click")

            self.choice_buttons.append(button)
            layout.addWidget(button)

        # Enable keyboard focus and shortcuts for the main window
        self.setFocusPolicy(Qt.StrongFocus)
        self.interactive_panel.setFocusPolicy(Qt.StrongFocus)

    def display_caps_choices(self, sequence: str, options: List[str]):
        """Display choices for all-caps sequences."""
        self.current_item_label.setText(f"All-caps sequence: '{sequence}'")

        # Clear existing choices
        layout = self.choice_frame.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
            elif item and item.layout():
                # Handle nested layouts
                nested_layout = item.layout()
                for j in reversed(range(nested_layout.count())):
                    nested_item = nested_layout.itemAt(j)
                    if nested_item and nested_item.widget():
                        nested_item.widget().setParent(None)

        # Add choice buttons with specific handlers
        choices = [
            ("Yes (lowercase)", lambda: self.handle_caps_selection("y")),
            ("No (keep uppercase)", lambda: self.handle_caps_selection("n")),
            ("Add to Ignore", lambda: self.handle_caps_selection("a")),
            ("Auto Lowercase", lambda: self.handle_caps_selection("i")),
        ]

        for i, (text, handler) in enumerate(choices):
            button = QPushButton(f"{text}")
            button.clicked.connect(handler)
            layout.addWidget(button)

    def display_numbered_line(
        self, line_no: int, line_content: str, spans: List[Tuple[int, int]]
    ):
        """Display numbered line for editing."""
        self.current_item_label.setText(f"Line {line_no + 1}:")

        # Clear existing widgets
        layout = self.choice_frame.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
            elif item and item.layout():
                # Handle nested layouts
                nested_layout = item.layout()
                for j in reversed(range(nested_layout.count())):
                    nested_item = nested_layout.itemAt(j)
                    if nested_item and nested_item.widget():
                        nested_item.widget().setParent(None)

        # Add text edit for the line
        self.line_edit = QTextEdit()
        self.line_edit.setPlainText(line_content)
        self.line_edit.setMaximumHeight(150)

        # Highlight numbers in the text
        cursor = self.line_edit.textCursor()
        format_highlight = QTextCharFormat()
        format_highlight.setBackground(QColor("yellow"))

        for start, end in spans:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            cursor.setCharFormat(format_highlight)

        layout.addWidget(self.line_edit)

        # Add buttons
        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply & Next")
        apply_button.clicked.connect(self.handle_numbered_apply)

        skip_button = QPushButton("Skip")
        skip_button.clicked.connect(self.handle_numbered_skip)

        ignore_button = QPushButton("Ignore")
        ignore_button.clicked.connect(self.handle_numbered_ignore)
        ignore_button.setToolTip(
            "Ignore all instances of numbers in this line for this session"
        )

        button_layout.addWidget(apply_button)
        button_layout.addWidget(skip_button)
        button_layout.addWidget(ignore_button)

        layout.addLayout(button_layout)

    def handle_choice_selection(self, choice: str):
        """Handle selection of a word choice."""
        if not self.choice_processor.handle_choice(choice, self.ctx):
            # All manual choices complete - phonetic processing disabled
            # No automatic processing, finish step
            self.finish_current_interactive_step()

    def handle_caps_selection(self, choice: str):
        """Handle selection of caps processing choice."""
        if self.caps_processor.handle_caps_choice(choice, self.ctx):
            # More sequences to process
            pass
        else:
            # All sequences complete
            self.finish_current_interactive_step()

    def handle_numbered_apply(self):
        """Handle apply button for numbered line editing."""
        from .logging import log_message

        edited_text = self.line_edit.toPlainText()
        log_message(f"GUI: Applying numbered edit: '{edited_text}'")

        if not self.numbered_processor.save_and_next(edited_text):
            # Editing complete
            log_message("GUI: Numbered editing complete, applying edits")
            self.numbered_processor.apply_edits(self.ctx)
            self.finish_current_interactive_step()

    def handle_numbered_skip(self):
        """Handle skip button for numbered line editing."""
        from .logging import log_message

        log_message("GUI: User skipped numbered line")

        if not self.numbered_processor.skip_current_line():
            # Editing complete
            log_message("GUI: Numbered editing complete after skip")
            self.numbered_processor.apply_edits(self.ctx)
            self.finish_current_interactive_step()

    def handle_numbered_ignore(self):
        """Handle ignore button for numbered line editing."""
        from .logging import log_message

        log_message("GUI: User ignored numbers in current line")

        if not self.numbered_processor.ignore_current_numbers(self.ctx):
            # Editing complete
            log_message("GUI: Numbered editing complete after ignore")
            self.numbered_processor.apply_edits(self.ctx)
            self.finish_current_interactive_step()

    def handle_previous(self):
        """Handle previous button."""
        if self.current_interactive_step == "numbered_line_edit":
            self.numbered_processor.go_previous()

    def handle_skip(self):
        """Handle skip button."""
        if self.current_interactive_step == "interactive_choices":
            # Skip current word
            self.choice_processor.handle_choice("", self.ctx)
        elif self.current_interactive_step == "all_caps_processing":
            # Skip current sequence (treat as 'No')
            self.handle_caps_selection("n")
        elif self.current_interactive_step == "numbered_line_edit":
            self.handle_numbered_skip()

    def finish_current_interactive_step(self):
        """Finish the current interactive step and move to next."""
        self.current_interactive_step = None

        # Hide roman legend when finishing any step
        self.legend_label.setVisible(False)

        # Clear interactive panel
        layout = self.choice_frame.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                # Handle nested layouts
                nested_layout = item.layout()
                for j in reversed(range(nested_layout.count())):
                    nested_item = nested_layout.itemAt(j)
                    if nested_item.widget():
                        nested_item.widget().setParent(None)

        # Update text display and clear any highlighting when transitioning between modes
        self.clear_text_highlighting()
        self.update_text_display(self.ctx.text, preserve_highlighting=False)

        # Continue with next step in order
        if self.pending_interactive_steps:
            # More interactive steps in current batch
            self.start_next_interactive_step()
        elif hasattr(self, "pending_steps") and self.pending_steps:
            # Continue with next step in ordered queue
            self.interactive_panel.hide()
            self._process_next_step()
        else:
            # All processing complete
            self.interactive_panel.hide()
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

    def update_navigation(self, current: int, total: int):
        """Update navigation display for numbered editing."""
        self.prev_button.setEnabled(current > 1)

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

        # Show pattern analyzer prompt if enabled
        self._show_pattern_analyzer_prompt()

    def _show_pattern_analyzer_prompt(self):
        """Show prompt to analyze learning patterns after processing completes."""
        log_message("DEBUG: _show_pattern_analyzer_prompt() called")

        # Check if prompt is enabled in config
        show_prompt = self.ctx.ai_config.get("show_pattern_analyzer_prompt", True)
        log_message(f"DEBUG: show_pattern_analyzer_prompt config = {show_prompt}")
        if not show_prompt:
            log_message("DEBUG: Prompt disabled in config, skipping")
            return

        # Check if learning file exists
        from pathlib import Path

        learning_file = Path(".ai_learning/choices_learning.json")
        log_message(f"DEBUG: Checking for learning file: {learning_file.absolute()}")
        if not learning_file.exists():
            log_message("DEBUG: Learning file does not exist, skipping prompt")
            return  # No learning data, skip prompt

        log_message("DEBUG: Showing pattern analyzer prompt dialog")

        # Create custom dialog with checkbox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Analyze Learning Patterns")
        msg_box.setText("Processing complete!")
        msg_box.setInformativeText(
            "Would you like to analyze learning patterns now?\n\n"
            "This will review your decision history and suggest new REPLACE/SKIP_CHOICE rules."
        )
        msg_box.setIcon(QMessageBox.Question)

        # Add Yes and No buttons
        yes_button = msg_box.addButton("Yes", QMessageBox.YesRole)
        no_button = msg_box.addButton("No", QMessageBox.NoRole)
        msg_box.setDefaultButton(yes_button)

        # Add checkbox for "Don't ask again"
        checkbox = QCheckBox("Don't ask again")
        msg_box.setCheckBox(checkbox)

        # Show dialog
        msg_box.exec_()

        # Handle checkbox
        if checkbox.isChecked():
            self._save_pattern_analyzer_prompt_preference(False)
            log_message("Pattern analyzer prompt disabled by user")

        # Handle button click
        if msg_box.clickedButton() == yes_button:
            self.launch_pattern_analyzer()

    def _save_pattern_analyzer_prompt_preference(self, enabled: bool):
        """Save the pattern analyzer prompt preference to data/settings.txt or .data.txt."""
        try:
            # Use the existing save function which handles data/ directory correctly
            save_ai_config_to_data_file("show_pattern_analyzer_prompt", enabled)

            # Update context
            self.ctx.ai_config["show_pattern_analyzer_prompt"] = enabled

            log_message(f"Updated show_pattern_analyzer_prompt: {enabled}")

        except Exception as e:
            log_message(f"Error saving pattern analyzer preference: {e}", level="ERROR")

    def keyPressEvent(self, event):
        """Handle keyboard events for choice shortcuts."""
        # Only handle keyboard events during interactive processing
        if (
            self.current_interactive_step == "interactive_choices"
            and hasattr(self, "choice_buttons")
            and self.choice_buttons
        ):

            # Handle number keys 1-9
            key = event.key()
            if Qt.Key_1 <= key <= Qt.Key_9:
                button_index = key - Qt.Key_1  # Convert to 0-based index
                if button_index < len(self.choice_buttons):
                    self.choice_buttons[button_index].click()
                    return

        # Let parent handle other keys
        super().keyPressEvent(event)

    def _show_phonetic_review(self):
        """Show phonetic processing review with unified click-to-edit text interface."""
        phonetic_log = self.choice_processor.get_phonetic_log()

        if not phonetic_log:
            self.current_item_label.setText("Phonetic analysis made no changes.")
            # Continue to manual processing if needed
            manual_words = len(self.ctx.choices) if hasattr(self.ctx, "choices") else 0
            if manual_words == 0:
                self.finish_current_interactive_step()
            return

        self.interactive_title.setText("Phonetic Processing Review")
        self.helper_label.setText(
            "💡 TIP: Click any highlighted yellow word to cycle through spelling options. Click Apply Changes when done."
        )
        self.helper_label.setStyleSheet(
            "color: #000; font-size: 12pt; font-weight: bold; padding: 5px; background-color: #ffffcc; border: 1px solid #ccc;"
        )
        self.current_item_label.setText(
            f"Phonetic analysis made {len(phonetic_log)} changes:"
        )

        # Clear existing choices
        layout = self.choice_frame.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        try:
            from PyQt5.QtWidgets import (
                QTextEdit,
                QPushButton,
                QVBoxLayout,
                QWidget,
                QScrollArea,
            )
            from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
            from PyQt5.QtCore import Qt

            # Create compact review showing only changes with context
            self.phonetic_review_edit = QTextEdit()
            self.phonetic_review_edit.setMaximumHeight(400)
            self.phonetic_review_edit.setStyleSheet(
                "font-family: 'Courier New', monospace; font-size: 10pt; background-color: #f9f9f9;"
            )

            # Build compact text showing only changes with context
            review_text = ""
            self.phonetic_changes = {}
            current_pos = 0

            for i, change in enumerate(phonetic_log):
                original = change["original"]
                replacement = change["replacement"]
                context_before = change["context_before"]
                context_after = change["context_after"]
                options = change["options"]

                # Create context snippet: "...context_before [REPLACEMENT] context_after..."
                snippet = f"Change {i+1}: ...{context_before} [{replacement}] {context_after}...\n\n"

                # Find position of the replacement word in this snippet
                bracket_start = snippet.find("[")
                word_start = bracket_start + 1
                word_end = word_start + len(replacement)

                # Adjust for current position in review text
                absolute_start = current_pos + word_start
                absolute_end = current_pos + word_end

                # Store change data for click handling
                self.phonetic_changes[absolute_start] = {
                    "original": original,
                    "current": replacement,
                    "options": options,
                    "option_index": (
                        options.index(replacement) if replacement in options else 0
                    ),
                    "start": absolute_start,
                    "end": absolute_end,
                    "snippet_start": current_pos,
                    "snippet_text": snippet,
                }

                review_text += snippet
                current_pos = len(review_text)

            # Set the compact review text
            self.phonetic_review_edit.setPlainText(review_text)

            # Apply highlighting to all changes
            cursor = self.phonetic_review_edit.textCursor()
            for change_data in self.phonetic_changes.values():
                cursor.setPosition(change_data["start"])
                cursor.setPosition(change_data["end"], QTextCursor.KeepAnchor)

                highlight_format = QTextCharFormat()
                highlight_format.setBackground(QColor(255, 255, 0))  # Bright yellow
                highlight_format.setForeground(QColor(0, 0, 0))
                highlight_format.setFontWeight(700)
                cursor.setCharFormat(highlight_format)

            # Make text clickable
            self.phonetic_review_edit.mousePressEvent = (
                self._handle_phonetic_compact_click
            )

            # Apply changes button
            apply_button = QPushButton("Apply Changes")
            apply_button.clicked.connect(self._apply_compact_phonetic_changes)
            apply_button.setStyleSheet(
                "font-weight: bold; padding: 8px; background-color: #4CAF50; color: white;"
            )

            layout.addWidget(self.phonetic_review_edit)
            layout.addWidget(apply_button)

        except Exception as e:
            from .logging import log_message

            log_message(f"Error displaying unified phonetic review: {e}", level="ERROR")
            # Fallback to simple text display
            self.current_item_label.setText(
                f"Phonetic analysis made {len(phonetic_log)} changes."
            )
            self._accept_phonetic_changes()

    def _start_phonetic_processing(self):
        """Start phonetic processing phase after manual choices are complete."""
        from .logging import log_message

        self.interactive_title.setText("Phonetic Automatic Processing")
        self.helper_label.setText(
            "Phonetic analysis is automatically processing tagged word choices..."
        )

        # Clear existing choice display
        layout = self.choice_frame.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # Run phonetic processing
        log_message("Starting phonetic processing phase after manual choices")
        self.choice_processor.process_choices_with_phonetic_analysis(self.ctx)

        # Show phonetic review
        self._show_phonetic_review()

    def _edit_phonetic_changes(self):
        """Allow user to edit individual phonetic changes."""
        phonetic_log = self.choice_processor.get_phonetic_log()

        if not phonetic_log:
            return

        # Create edit dialog
        from PyQt5.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QScrollArea,
            QWidget,
            QHBoxLayout,
            QComboBox,
            QLabel,
            QPushButton,
        )
        from PyQt5.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Phonetic Changes")
        dialog.setModal(True)
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        # Create scrollable area for edits
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.edit_widgets = []

        for i, entry in enumerate(phonetic_log):
            # Create edit widget for each change
            change_widget = QWidget()
            change_layout = QVBoxLayout(change_widget)

            # Context display
            context_label = QLabel(
                f"Context: ...{entry['context_before']} [{entry['original']}] {entry['context_after']}..."
            )
            context_label.setWordWrap(True)
            context_label.setStyleSheet("font-size: 10pt; color: #666;")

            # Choice selection
            choice_layout = QHBoxLayout()
            choice_label = QLabel(f"Change {i+1}: '{entry['original']}' →")
            choice_label.setMinimumWidth(120)

            choice_combo = QComboBox()
            choice_combo.addItems(entry["options"])

            # Set current selection
            if entry["replacement"] in entry["options"]:
                choice_combo.setCurrentText(entry["replacement"])

            choice_layout.addWidget(choice_label)
            choice_layout.addWidget(choice_combo)
            choice_layout.addStretch()

            change_layout.addWidget(context_label)
            change_layout.addLayout(choice_layout)
            change_layout.addWidget(QWidget())  # Spacer

            # Store reference for later
            self.edit_widgets.append(
                {"combo": choice_combo, "entry": entry, "index": i}
            )

            scroll_layout.addWidget(change_widget)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Dialog buttons
        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply Changes")
        apply_button.clicked.connect(lambda: self._apply_edits(dialog))

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)

        layout.addWidget(QLabel("Edit individual phonetic changes:"))
        layout.addWidget(scroll_area)
        layout.addLayout(button_layout)

        dialog.exec_()

    def _apply_phonetic_review_changes(self):
        """Apply user edits from phonetic review and continue processing."""
        # Get current text
        current_text = self.ctx.text

        # Apply changes in reverse order to maintain positions
        edits_to_apply = []
        for widget_data in self.phonetic_edit_widgets:
            new_choice = widget_data["combo"].currentText()
            entry = widget_data["entry"]

            if new_choice != entry["replacement"]:
                # User changed this selection
                edits_to_apply.append(
                    {
                        "position": entry["position"],
                        "original": entry["original"],
                        "old_replacement": entry["replacement"],
                        "new_replacement": new_choice,
                    }
                )

        # Sort by position (reverse order)
        edits_to_apply.sort(key=lambda x: x["position"], reverse=True)

        # Apply changes
        for edit in edits_to_apply:
            # Find and replace in current text
            pos = edit["position"]
            old_text = edit["old_replacement"]
            new_text = edit["new_replacement"]

            # Replace at specific position
            if current_text[pos : pos + len(old_text)] == old_text:
                current_text = (
                    current_text[:pos] + new_text + current_text[pos + len(old_text) :]
                )

        # Update context and display
        self.ctx.text = current_text
        self.choice_processor.current_text = current_text

        # Update text display directly
        self.update_text_display(self.ctx.text, preserve_highlighting=False)

        # Continue to next processing step
        self.finish_current_interactive_step()

    def _handle_phonetic_compact_click(self, event):
        """Handle clicking on highlighted words in compact phonetic review."""
        try:
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor

            # Get click position
            cursor = self.phonetic_review_edit.cursorForPosition(event.pos())
            click_pos = cursor.position()

            # Find if click is on a highlighted change
            clicked_change = None
            for start_pos, change_data in self.phonetic_changes.items():
                if change_data["start"] <= click_pos <= change_data["end"]:
                    clicked_change = change_data
                    break

            if clicked_change:
                # Cycle to next option
                options = clicked_change["options"]
                current_index = clicked_change["option_index"]
                next_index = (current_index + 1) % len(options)
                new_option = options[next_index]

                # Save current scroll position before making changes
                scrollbar = self.phonetic_review_edit.verticalScrollBar()
                saved_scroll_position = scrollbar.value()

                # Update the text in the compact view
                start = clicked_change["start"]
                end = clicked_change["end"]
                current_text = self.phonetic_review_edit.toPlainText()

                # Replace text
                new_text = current_text[:start] + new_option + current_text[end:]
                self.phonetic_review_edit.setPlainText(new_text)

                # Update positions for all changes after this one
                length_diff = len(new_option) - len(clicked_change["current"])
                if length_diff != 0:
                    for pos, change in self.phonetic_changes.items():
                        if change["start"] > start:
                            change["start"] += length_diff
                            change["end"] += length_diff

                # Update clicked change
                clicked_change["current"] = new_option
                clicked_change["option_index"] = next_index
                clicked_change["end"] = start + len(new_option)

                # Re-apply all highlighting
                self._reapply_phonetic_highlighting()

                # Restore scroll position after changes
                scrollbar.setValue(saved_scroll_position)

        except Exception as e:
            from .logging import log_message

            log_message(f"Error handling compact phonetic click: {e}", level="ERROR")

    def _reapply_phonetic_highlighting(self):
        """Re-apply highlighting to all phonetic changes."""
        try:
            from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor

            cursor = self.phonetic_review_edit.textCursor()

            # Clear all formatting first
            cursor.select(QTextCursor.Document)
            default_format = QTextCharFormat()
            cursor.setCharFormat(default_format)
            cursor.clearSelection()

            # Re-apply highlighting to all changes
            for change_data in self.phonetic_changes.values():
                cursor.setPosition(change_data["start"])
                cursor.setPosition(change_data["end"], QTextCursor.KeepAnchor)

                highlight_format = QTextCharFormat()
                highlight_format.setBackground(
                    QColor(255, 255, 0, 180)
                )  # Semi-transparent yellow
                highlight_format.setForeground(QColor(0, 0, 0))
                highlight_format.setFontWeight(700)
                cursor.setCharFormat(highlight_format)

        except Exception as e:
            from .logging import log_message

            log_message(f"Error re-applying phonetic highlighting: {e}", level="ERROR")

    def _apply_compact_phonetic_changes(self):
        """Apply changes from compact phonetic review interface."""
        try:
            # Apply the user's selections to the actual text
            final_text = self.ctx.text  # Start with current processed text

            # Get the original phonetic log to find original positions
            phonetic_log = self.choice_processor.get_phonetic_log()

            # Apply changes in reverse order to maintain positions
            changes_to_apply = []
            for change_data in self.phonetic_changes.values():
                # Find corresponding entry in phonetic_log to get original position
                for log_entry in phonetic_log:
                    if (
                        log_entry["original"] == change_data["original"]
                        and log_entry["replacement"] != change_data["current"]
                    ):
                        # User changed this selection
                        changes_to_apply.append(
                            {
                                "position": log_entry["position"],
                                "original_replacement": log_entry["replacement"],
                                "new_replacement": change_data["current"],
                                "original_word": change_data["original"],
                            }
                        )
                        break

            # Sort by position (reverse order for stable replacement)
            changes_to_apply.sort(key=lambda x: x["position"], reverse=True)

            # Apply the changes to the actual text
            for change in changes_to_apply:
                pos = change["position"]
                old_replacement = change["original_replacement"]
                new_replacement = change["new_replacement"]

                # Replace in the actual text
                if final_text[pos : pos + len(old_replacement)] == old_replacement:
                    final_text = (
                        final_text[:pos]
                        + new_replacement
                        + final_text[pos + len(old_replacement) :]
                    )

            # Update context
            self.ctx.text = final_text
            self.choice_processor.current_text = final_text

            # Update main text display
            self.update_text_display(final_text, preserve_highlighting=False)

            # Continue to next processing step
            self.finish_current_interactive_step()

        except Exception as e:
            from .logging import log_message

            log_message(f"Error applying compact phonetic changes: {e}", level="ERROR")
            # Fallback to accepting current changes
            self._accept_phonetic_changes()

    def _handle_manual_completion(self):
        """Handle automatic completion of manual choices without requiring user interaction."""
        # Check if phonetic processing should run
        use_phonetic_auto = self.phonetic_auto_checkbox.isChecked()
        if (
            use_phonetic_auto
            and hasattr(self.ctx, "tagged_choices")
            and self.ctx.tagged_choices
        ):
            # Start phonetic processing phase
            self._start_phonetic_processing()
        else:
            # No phonetic processing needed, finish step
            self.finish_current_interactive_step()

    def _accept_phonetic_changes(self):
        """Accept phonetic changes and finish the choice processing step."""
        # Phonetic processing is complete, move to next step
        self.finish_current_interactive_step()

    def _on_phonetic_toggled(self, checked):
        """Handle phonetic checkbox toggle - ensure interactive choices is enabled when phonetic is enabled."""
        if "interactive_choices" in self.checkboxes:
            interactive_checkbox = self.checkboxes["interactive_choices"]
            if checked:
                # Phonetic enabled - ensure interactive choices is checked and inform user
                interactive_checkbox.setChecked(True)
                interactive_checkbox.setToolTip(
                    "Enhanced with phonetic automatic processing"
                )
            else:
                # Phonetic disabled - restore normal tooltip
                interactive_checkbox.setToolTip("This step requires user interaction")

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
    temp_ctx = load_data_file()

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
                save_default_directory_to_data_file(directory)
                QMessageBox.information(
                    None,
                    "Default Directory Set",
                    f"Default directory set to:\n{directory}",
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
