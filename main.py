#!/usr/bin/env python3
"""
Bookfix - Ebook Text Processor
Main entry point for the application.
"""

import sys

# Must import torch FIRST on Windows to avoid MSVCP140.dll conflict with PyQt5.
# PyQt5 bundles an older MSVCP140.dll (14.26) that breaks torch c10.dll initialization
# if loaded before torch. Importing torch first claims the newer system MSVCP140 slot.
if sys.platform == "win32":
    import torch  # noqa: F401
import os
from pathlib import Path

# Add the bookfix package to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import Qt
except ImportError:
    print("Error: PyQt5 not installed.")
    print("Please install PyQt5: pip install PyQt5")
    sys.exit(1)

from bookfix.gui import BookfixMainWindow
from bookfix.logging import setup_logging


def main():
    """Main application entry point."""
    # Remove developer-only flag before Qt parses application arguments.
    dev_mode = "--dev" in sys.argv
    if dev_mode:
        sys.argv.remove("--dev")

    # Set up logging
    setup_logging()
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Bookfix")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Bookfix")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        # Create and show main window
        window = BookfixMainWindow(dev_mode=dev_mode)
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        # Show error dialog if something goes wrong
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Bookfix Error")
        error_dialog.setText(f"An error occurred while starting Bookfix:\n\n{str(e)}")
        error_dialog.setDetailedText(f"Error details:\n{str(e)}")
        error_dialog.exec_()
        sys.exit(1)


if __name__ == "__main__":
    main()
