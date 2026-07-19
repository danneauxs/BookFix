
# Gemini Project: Bookfix

## Project Overview

This project, "Bookfix," is a desktop application built with Python and PyQt5. Its primary purpose is to process and clean up ebook text, specifically for use with Text-to-Speech (TTS) systems. The application provides a graphical user interface (GUI) for users to load text files, select various processing steps, and interactively make decisions on ambiguous text, such as homographs.

The architecture is modular, with a processing pipeline that executes a series of steps in a defined order. These steps include both automatic and interactive processors. The application also has AI-powered features, including AI-assisted choices for homographs and all-caps sequences.

## Building and Running

The project can be run using a shell script or by manually setting up a virtual environment and running the main Python script.

**To run the application:**

```bash
./run.sh
```

Alternatively, you can set up the environment manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Testing:**

The project contains a number of test files (e.g., `test_all_improvements.txt`, `test_caps.txt`, etc.), but there is no formal testing framework like `pytest` or `unittest` immediately apparent. Tests seem to be run via individual scripts or by using the `run_test.sh` script.

## Development Conventions

*   **Framework:** The application is built using the PyQt5 framework for the GUI.
*   **Architecture:** It follows a modular architecture with a processing pipeline that orchestrates a series of processors. A central `BookfixContext` data structure is used to pass data between processors.
*   **Styling:** The application has some custom styling, as seen in `bookfix/gui.py`.
*   **AI Integration:** The project integrates AI models for tasks like homograph disambiguation and all-caps processing. It appears to use a local AI service, possibly Ollama, and has a system for reviewing and learning from AI-assisted changes.
*   **Configuration:** The application uses a `.data.txt` file for configuration, which includes find/replace rules, word choices, and ignore lists.

## DocDNA

This project includes a `DocDNA` directory, which contains a set of files that provide a comprehensive, structured, and searchable representation of the codebase. The `DocDNA/prompt.txt` file provides strict instructions for using this documentation as the primary source of information before consulting the raw source code. This "DocDNA-first" protocol is mandatory for all interactions with the codebase.

## Permissions

No file is to be created, edited, or deleted without explicit permission. Reading and scanning files is permitted.
