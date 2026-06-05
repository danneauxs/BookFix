"""
Font controls widget for review windows.

Provides reusable font size and font family controls that can be added
to any review window in the application.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import pyqtSignal


class FontControlsWidget(QWidget):
    """
    Reusable widget providing font size and font family controls.

    Signals:
        font_changed: Emitted when font family or size changes (font_family, font_size)
    """

    font_changed = pyqtSignal(str, int)

    # Font size constraints
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 36
    FONT_SIZE_INCREMENT = 2

    # Available font families organized by category
    SERIF_FONTS = ["Georgia", "Times New Roman", "Palatino"]
    SANS_SERIF_FONTS = ["Arial", "Helvetica", "Verdana", "Tahoma"]
    MONOSPACE_FONTS = ["Courier New", "Consolas", "Monaco"]

    def __init__(
        self, initial_family: str = "Arial", initial_size: int = 12, parent=None
    ):
        """
        Initialize font controls widget.

        Args:
            initial_family: Initial font family name
            initial_size: Initial font size in points
            parent: Parent widget
        """
        super().__init__(parent)

        self.current_font_family = initial_family
        self.current_font_size = initial_size

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Font size controls
        self.size_label = QLabel(f"Font: {self.current_font_size}pt")
        layout.addWidget(self.size_label)

        self.decrease_btn = QPushButton("-")
        self.decrease_btn.setFixedWidth(30)
        self.decrease_btn.setToolTip("Decrease font size")
        self.decrease_btn.clicked.connect(self.decrease_font)
        layout.addWidget(self.decrease_btn)

        self.increase_btn = QPushButton("+")
        self.increase_btn.setFixedWidth(30)
        self.increase_btn.setToolTip("Increase font size")
        self.increase_btn.clicked.connect(self.increase_font)
        layout.addWidget(self.increase_btn)

        # Font family dropdown
        layout.addSpacing(10)
        self.font_combo = QComboBox()
        self.font_combo.setToolTip("Select font family")

        # Populate font dropdown with categories
        self._populate_font_dropdown()

        # Set initial selection
        index = self.font_combo.findText(self.current_font_family)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)

        self.font_combo.currentTextChanged.connect(self.change_font)
        layout.addWidget(self.font_combo)

        layout.addStretch()

        # Update button states
        self._update_button_states()

    def _populate_font_dropdown(self):
        """Populate the font family dropdown with categorized fonts."""
        self.font_combo.addItem("--- Sans-Serif ---")
        for font in self.SANS_SERIF_FONTS:
            self.font_combo.addItem(font)

        self.font_combo.addItem("--- Serif ---")
        for font in self.SERIF_FONTS:
            self.font_combo.addItem(font)

        self.font_combo.addItem("--- Monospace ---")
        for font in self.MONOSPACE_FONTS:
            self.font_combo.addItem(font)

        # Disable category separator items
        for i in range(self.font_combo.count()):
            if self.font_combo.itemText(i).startswith("---"):
                self.font_combo.model().item(i).setEnabled(False)

    def increase_font(self):
        """Increase font size by increment."""
        new_size = self.current_font_size + self.FONT_SIZE_INCREMENT
        if new_size <= self.MAX_FONT_SIZE:
            self.current_font_size = new_size
            self._update_display()
            self._emit_font_changed()

    def decrease_font(self):
        """Decrease font size by increment."""
        new_size = self.current_font_size - self.FONT_SIZE_INCREMENT
        if new_size >= self.MIN_FONT_SIZE:
            self.current_font_size = new_size
            self._update_display()
            self._emit_font_changed()

    def change_font(self, font_name: str):
        """
        Change font family.

        Args:
            font_name: Name of the font family
        """
        # Ignore category separators
        if font_name.startswith("---"):
            return

        if font_name and font_name != self.current_font_family:
            self.current_font_family = font_name
            self._emit_font_changed()

    def set_font(self, font_family: str, font_size: int):
        """
        Programmatically set font family and size.

        Args:
            font_family: Font family name
            font_size: Font size in points
        """
        changed = False

        if font_family != self.current_font_family:
            self.current_font_family = font_family
            index = self.font_combo.findText(font_family)
            if index >= 0:
                self.font_combo.setCurrentIndex(index)
            changed = True

        if font_size != self.current_font_size:
            # Clamp to valid range
            font_size = max(self.MIN_FONT_SIZE, min(self.MAX_FONT_SIZE, font_size))
            self.current_font_size = font_size
            self._update_display()
            changed = True

        if changed:
            self._emit_font_changed()

    def get_font_family(self) -> str:
        """Get current font family."""
        return self.current_font_family

    def get_font_size(self) -> int:
        """Get current font size."""
        return self.current_font_size

    def _update_display(self):
        """Update the font size label and button states."""
        self.size_label.setText(f"Font: {self.current_font_size}pt")
        self._update_button_states()

    def _update_button_states(self):
        """Enable/disable buttons based on current size."""
        self.decrease_btn.setEnabled(self.current_font_size > self.MIN_FONT_SIZE)
        self.increase_btn.setEnabled(self.current_font_size < self.MAX_FONT_SIZE)

    def _emit_font_changed(self):
        """Emit the font_changed signal."""
        self.font_changed.emit(self.current_font_family, self.current_font_size)
