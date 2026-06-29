"""
Heteronym Dictionary Manager GUI.
Edits both choices.json and choices_pos_dictionary.json for each homograph word.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QWidget,
    QScrollArea,
    QGroupBox,
    QListWidget,
    QComboBox,
    QSplitter,
    QInputDialog,
)
from PyQt5.QtCore import Qt


class SpellingWidget(QWidget):
    """Displays and edits choices.json + pos_dictionary fields for one pronunciation spelling."""

    def __init__(self, parent=None):
        """Initialize the spelling widget with side-by-side panels for both data sources."""
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Build the two-panel layout: choices.json on the left, pos_dictionary on the right."""
        outer = QVBoxLayout()
        outer.setContentsMargins(4, 4, 4, 4)

        # Spelling name row
        spelling_row = QHBoxLayout()
        spelling_row.addWidget(QLabel("Spelling:"))
        self.spelling_field = QLineEdit()
        self.spelling_field.setPlaceholderText("e.g., leed, led")
        spelling_row.addWidget(self.spelling_field)
        outer.addLayout(spelling_row)

        panels = QHBoxLayout()
        panels.setSpacing(8)

        # --- Left panel: choices.json fields ---
        choices_box = QGroupBox("Definition Data  (choices.json)")
        choices_layout = QVBoxLayout()

        row = QHBoxLayout()
        row.addWidget(QLabel("POS (coarse):"))
        self.pos_field = QLineEdit()
        self.pos_field.setPlaceholderText("VERB, NOUN, ADJECTIVE, Other")
        row.addWidget(self.pos_field)
        choices_layout.addLayout(row)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Definition:"))
        self.definition_field = QLineEdit()
        self.definition_field.setPlaceholderText("Short human-readable definition")
        row2.addWidget(self.definition_field)
        choices_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("NLI Hypothesis:"))
        self.nli_field = QLineEdit()
        self.nli_field.setPlaceholderText("Short targeted sentence for NLI model")
        row3.addWidget(self.nli_field)
        choices_layout.addLayout(row3)

        choices_layout.addWidget(QLabel("Strong Keywords (one per line):"))
        self.strong_keywords_field = QTextEdit()
        self.strong_keywords_field.setMaximumHeight(70)
        self.strong_keywords_field.setStyleSheet("background-color: #fff8dc;")
        choices_layout.addWidget(self.strong_keywords_field)

        choices_layout.addWidget(QLabel("Context Keywords (one per line):"))
        self.choices_context_field = QTextEdit()
        self.choices_context_field.setMaximumHeight(70)
        choices_layout.addWidget(self.choices_context_field)

        choices_layout.addWidget(QLabel("Examples (one per line):"))
        self.examples_field = QTextEdit()
        self.examples_field.setMaximumHeight(70)
        choices_layout.addWidget(self.examples_field)

        choices_box.setLayout(choices_layout)
        panels.addWidget(choices_box)

        # --- Right panel: pos_dictionary fields ---
        pos_box = QGroupBox("POS Rules  (pos_dictionary)")
        pos_layout = QVBoxLayout()

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("POS Tags:"))
        self.pos_tags_field = QLineEdit()
        self.pos_tags_field.setPlaceholderText("e.g., VBD, VBN  (comma-separated)")
        row4.addWidget(self.pos_tags_field)
        pos_layout.addLayout(row4)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Description:"))
        self.pos_desc_field = QLineEdit()
        self.pos_desc_field.setPlaceholderText("5-10 words describing this usage")
        row5.addWidget(self.pos_desc_field)
        pos_layout.addLayout(row5)

        pos_layout.addWidget(QLabel("Context Keywords (one per line):"))
        self.pos_context_field = QTextEdit()
        self.pos_context_field.setMaximumHeight(70)
        pos_layout.addWidget(self.pos_context_field)

        pos_layout.addWidget(QLabel("Dep Rules (raw JSON array):"))
        self.dep_rules_field = QTextEdit()
        self.dep_rules_field.setMaximumHeight(90)
        self.dep_rules_field.setPlaceholderText(
            '[{"type": "dep_relation", "values": ["ROOT"]}, {"type": "pos_tag", "values": ["VBD"]}]'
        )
        self.dep_rules_field.setStyleSheet("font-family: monospace; font-size: 11px;")
        pos_layout.addWidget(self.dep_rules_field)

        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Match Mode:"))
        self.match_mode_combo = QComboBox()
        self.match_mode_combo.addItems(["all", "any"])
        row6.addWidget(self.match_mode_combo)
        row6.addStretch()
        self.auto_badge = QLabel("AUTO-GENERATED")
        self.auto_badge.setStyleSheet("color: #999; font-size: 10px; font-style: italic;")
        self.auto_badge.setVisible(False)
        row6.addWidget(self.auto_badge)
        pos_layout.addLayout(row6)

        pos_box.setLayout(pos_layout)
        panels.addWidget(pos_box)

        outer.addLayout(panels)
        self.setLayout(outer)

    def get_spelling(self) -> str:
        """Return the spelling text, lowercased and stripped."""
        return self.spelling_field.text().strip().lower()

    def validate_dep_rules(self) -> Optional[str]:
        """Validate the dep_rules field as a JSON array. Returns an error string or None."""
        text = self.dep_rules_field.toPlainText().strip()
        if not text:
            return None
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, list):
                return f"Dep rules for '{self.get_spelling()}' must be a JSON array, not an object."
            return None
        except json.JSONDecodeError as e:
            return f"Invalid JSON in dep rules for '{self.get_spelling()}': {e}"

    def get_choices_data(self) -> dict:
        """Return a choices.json option dict built from the left-panel fields."""
        def lines(field: QTextEdit) -> List[str]:
            return [l.strip() for l in field.toPlainText().strip().splitlines() if l.strip()]

        return {
            "spelling": self.get_spelling(),
            "definition": self.definition_field.text().strip(),
            "pos": self.pos_field.text().strip(),
            "strong_keywords": lines(self.strong_keywords_field),
            "context_keywords": lines(self.choices_context_field),
            "examples": lines(self.examples_field),
            "nli_hypothesis": self.nli_field.text().strip(),
        }

    def get_pos_dict_data(self) -> Optional[dict]:
        """Return a pos_dictionary spelling entry, or None if all right-panel fields are empty."""
        tags_text = self.pos_tags_field.text().strip()
        dep_text = self.dep_rules_field.toPlainText().strip()
        desc = self.pos_desc_field.text().strip()
        if not tags_text and not dep_text and not desc:
            return None

        def lines(field: QTextEdit) -> List[str]:
            return [l.strip() for l in field.toPlainText().strip().splitlines() if l.strip()]

        tags = [t.strip() for t in tags_text.split(",") if t.strip()]
        context = lines(self.pos_context_field)

        result: dict = {
            "pos_tags": tags,
            "description": desc,
            "match_mode": self.match_mode_combo.currentText(),
        }
        if context:
            result["context_keywords"] = context
        if dep_text:
            result["dep_rules"] = json.loads(dep_text)
        return result

    def set_choices_data(self, option: dict):
        """Populate the left-panel fields from a choices.json option object."""
        self.spelling_field.setText(option.get("spelling", ""))
        self.definition_field.setText(option.get("definition", ""))
        self.pos_field.setText(option.get("pos", ""))
        self.nli_field.setText(option.get("nli_hypothesis", ""))
        self.strong_keywords_field.setPlainText("\n".join(option.get("strong_keywords", [])))
        self.choices_context_field.setPlainText("\n".join(option.get("context_keywords", [])))
        self.examples_field.setPlainText("\n".join(option.get("examples", [])))

    def set_pos_dict_data(self, data: dict):
        """Populate the right-panel fields from a pos_dictionary spelling entry."""
        self.pos_tags_field.setText(", ".join(data.get("pos_tags", [])))
        self.pos_desc_field.setText(data.get("description", ""))
        self.pos_context_field.setPlainText("\n".join(data.get("context_keywords", [])))
        dep = data.get("dep_rules", [])
        self.dep_rules_field.setPlainText(json.dumps(dep, indent=2) if dep else "")
        mode = data.get("match_mode", "all")
        idx = self.match_mode_combo.findText(mode)
        if idx >= 0:
            self.match_mode_combo.setCurrentIndex(idx)
        self.auto_badge.setVisible(bool(data.get("auto_generated", False)))

    def clear_pos_dict(self):
        """Clear all right-panel (pos_dictionary) fields."""
        self.pos_tags_field.clear()
        self.pos_desc_field.clear()
        self.pos_context_field.clear()
        self.dep_rules_field.clear()
        self.match_mode_combo.setCurrentIndex(0)
        self.auto_badge.setVisible(False)

    def connect_dirty_callback(self, callback):
        """Connect all editable fields to a callback so any edit marks the form dirty."""
        for field in (
            self.spelling_field, self.definition_field,
            self.pos_field, self.nli_field, self.pos_tags_field, self.pos_desc_field,
        ):
            field.textChanged.connect(callback)
        for area in (
            self.strong_keywords_field, self.choices_context_field,
            self.examples_field, self.pos_context_field, self.dep_rules_field,
        ):
            area.textChanged.connect(callback)
        self.match_mode_combo.currentIndexChanged.connect(callback)

    def clear(self):
        """Clear all fields in both panels."""
        self.spelling_field.clear()
        self.definition_field.clear()
        self.pos_field.clear()
        self.nli_field.clear()
        self.strong_keywords_field.clear()
        self.choices_context_field.clear()
        self.examples_field.clear()
        self.clear_pos_dict()


class HeteronymDictionaryManager(QDialog):
    """Dialog for managing heteronym entries in both choices.json and choices_pos_dictionary.json."""

    MAX_SPELLINGS = 4

    def __init__(self, parent=None):
        """Initialize the dialog, load both data files, and build the UI."""
        super().__init__(parent)
        self.setWindowTitle("Heteronym Dictionary Manager")
        self.setMinimumSize(1150, 780)

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.choices_file = os.path.join(project_root, "data", "choices.json")
        self.dict_file = os.path.join(
            project_root, ".ai_learning", "choices_pos_dictionary.json"
        )

        self._load_choices_json()
        self._load_pos_dictionary()

        self._is_dirty = False
        self._loading = False          # blocks re-entrance in _on_word_selected
        self._current_loaded_word: Optional[str] = None
        self._current_loaded_row: int = -1
        self._original_spellings: Dict[int, str] = {}  # slot index → spelling at load time

        self.init_ui()
        self._refresh_word_list()
        if self.word_list:
            self.word_list_widget.setCurrentRow(0)

    def _load_choices_json(self):
        """Load choices.json, separating comment entries from word entries."""
        try:
            with open(self.choices_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Comment entries have no "word" key — preserve them for save
            self._comment_entries = [e for e in raw if "word" not in e]
            self.choices_data = [e for e in raw if "word" in e]
            self.word_list = sorted(
                e["word"].lower() for e in self.choices_data
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load choices.json: {e}")
            self._comment_entries = []
            self.choices_data = []
            self.word_list = []

    def _load_pos_dictionary(self):
        """Load choices_pos_dictionary.json, keeping metadata separate from words."""
        try:
            with open(self.dict_file, "r", encoding="utf-8") as f:
                full = json.load(f)
            self._pos_meta = {k: v for k, v in full.items() if k != "words"}
            self.pos_dict = full.get("words", {})
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load pos_dictionary: {e}")
            self._pos_meta = {
                "version": "1.0",
                "description": "POS-tagged pronunciation dictionary for heteronyms",
                "created": datetime.now().strftime("%Y-%m-%d"),
            }
            self.pos_dict = {}

    def init_ui(self):
        """Build the main dialog layout: word list on the left, spelling panels on the right."""
        main_layout = QHBoxLayout()

        # --- Left panel: word list ---
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("<b>Words</b>"))

        self.word_list_widget = QListWidget()
        self.word_list_widget.currentRowChanged.connect(self._on_word_selected)
        left_panel.addWidget(self.word_list_widget)

        word_btn_row = QHBoxLayout()
        add_word_btn = QPushButton("Add")
        add_word_btn.setToolTip("Add a new homograph word")
        add_word_btn.clicked.connect(self._add_word)
        word_btn_row.addWidget(add_word_btn)
        del_word_btn = QPushButton("Delete")
        del_word_btn.setToolTip("Remove selected word from both files")
        del_word_btn.clicked.connect(self._delete_word)
        word_btn_row.addWidget(del_word_btn)
        self.disable_btn = QPushButton("Disable")
        self.disable_btn.setToolTip("Toggle disabled flag in pos_dictionary")
        self.disable_btn.clicked.connect(self._toggle_disabled)
        word_btn_row.addWidget(self.disable_btn)
        left_panel.addLayout(word_btn_row)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(200)

        # --- Right panel: spelling widgets in a scroll area ---
        right_panel = QVBoxLayout()

        word_header = QHBoxLayout()
        self.word_label = QLabel("")
        self.word_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        word_header.addWidget(QLabel("<b>Word:</b>"))
        word_header.addWidget(self.word_label)
        self.disabled_label = QLabel("[DISABLED]")
        self.disabled_label.setStyleSheet("color: #c00; font-weight: bold;")
        self.disabled_label.setVisible(False)
        word_header.addWidget(self.disabled_label)
        word_header.addStretch()
        add_spelling_btn = QPushButton("+ Add Spelling")
        add_spelling_btn.setToolTip("Show a blank spelling slot for a new pronunciation")
        add_spelling_btn.clicked.connect(self._add_spelling_slot)
        word_header.addWidget(add_spelling_btn)
        right_panel.addLayout(word_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout()
        self._scroll_layout.setSpacing(12)

        self.spelling_widgets: List[SpellingWidget] = []
        for _ in range(self.MAX_SPELLINGS):
            sw = SpellingWidget()
            sw.setVisible(False)
            self.spelling_widgets.append(sw)
            self._scroll_layout.addWidget(sw)

        self._scroll_layout.addStretch()
        scroll_content.setLayout(self._scroll_layout)
        scroll.setWidget(scroll_content)
        right_panel.addWidget(scroll)

        # Bottom action bar
        bottom = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("font-weight: bold; padding: 6px 18px;")
        save_btn.clicked.connect(self._save)
        bottom.addWidget(save_btn)

        import_btn = QPushButton("Import Learned Keywords")
        import_btn.setToolTip("Merge keywords from AI learning storage into pos_dictionary context keywords")
        import_btn.clicked.connect(self._import_learned_keywords)
        bottom.addWidget(import_btn)

        generate_btn = QPushButton("Generate with AI")
        generate_btn.setToolTip("Ask AI to suggest pos_dictionary fields for this word")
        generate_btn.clicked.connect(self._generate_with_ai)
        bottom.addWidget(generate_btn)

        bottom.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        bottom.addWidget(close_btn)
        right_panel.addLayout(bottom)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def _refresh_word_list(self):
        """Repopulate the word list widget from self.word_list (sorted)."""
        self.word_list_widget.blockSignals(True)
        self.word_list_widget.clear()
        for word in sorted(self.word_list):
            self.word_list_widget.addItem(word)
        self.word_list_widget.blockSignals(False)

    def _current_word(self) -> Optional[str]:
        """Return the text of the currently selected word list item, or None."""
        item = self.word_list_widget.currentItem()
        return item.text() if item else None

    def _on_word_selected(self, new_row: int):
        """Check for unsaved changes, then load the selected word into the spelling widgets."""
        if self._loading:
            return

        new_word = (
            self.word_list_widget.item(new_row).text()
            if self.word_list_widget.item(new_row) else None
        )

        if self._is_dirty and self._current_loaded_word:
            # Restore previous selection visually while we ask the user
            self._loading = True
            self.word_list_widget.setCurrentRow(self._current_loaded_row)
            self._loading = False

            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to '{self._current_loaded_word}' before switching?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )
            if result == QMessageBox.Cancel:
                return
            if result == QMessageBox.Yes:
                if not self._do_save():
                    return  # Save failed — stay on current word

            # Proceed to new word
            self._loading = True
            self.word_list_widget.setCurrentRow(new_row)
            self._loading = False

        self._load_word(new_word, new_row)

    def _load_word(self, word: Optional[str], row: int):
        """Load both files' data for the given word into the spelling widgets."""
        if not word:
            return

        self.word_label.setText(word)
        self._current_loaded_word = word
        self._current_loaded_row = row

        choices_entry = next(
            (e for e in self.choices_data if e.get("word", "").lower() == word), None
        )
        options = choices_entry.get("options", []) if choices_entry else []

        pos_word = self.pos_dict.get(word, {})
        is_disabled = bool(pos_word.get("disabled", False))
        self.disabled_label.setVisible(is_disabled)
        self.disable_btn.setText("Enable" if is_disabled else "Disable")

        self._original_spellings = {}
        for i, sw in enumerate(self.spelling_widgets):
            if i < len(options):
                option = options[i]
                spelling = option.get("spelling", "")
                sw.set_choices_data(option)
                pos_spelling = {
                    k: v for k, v in pos_word.get(spelling, {}).items()
                }
                if pos_spelling:
                    sw.set_pos_dict_data(pos_spelling)
                else:
                    sw.clear_pos_dict()
                sw.setVisible(True)
                self._original_spellings[i] = spelling
            else:
                sw.clear()
                sw.setVisible(False)

        # Connect all fields to dirty marker AFTER loading (prevents false positives)
        self._is_dirty = False
        for sw in self.spelling_widgets:
            sw.connect_dirty_callback(self._mark_dirty)

        self._silent_import_keywords(word)

    def _mark_dirty(self):
        """Mark the form as having unsaved changes."""
        self._is_dirty = True

    def _add_spelling_slot(self):
        """Make the next hidden spelling widget visible so the user can enter a new spelling."""
        for sw in self.spelling_widgets:
            if not sw.isVisible():
                sw.clear()
                sw.setVisible(True)
                return
        QMessageBox.information(
            self, "Limit", f"Maximum {self.MAX_SPELLINGS} spellings per word."
        )

    def _add_word(self):
        """Prompt for a new word name and add blank entries to both data structures."""
        if not self._confirm_discard_or_save():
            return
        word, ok = QInputDialog.getText(self, "Add Word", "New homograph word:")
        if not ok or not word.strip():
            return
        word = word.strip().lower()
        if word in self.word_list:
            items = self.word_list_widget.findItems(word, Qt.MatchExactly)
            if items:
                self.word_list_widget.setCurrentItem(items[0])
            return
        self.word_list.append(word)
        self.word_list = sorted(self.word_list)
        self.choices_data.append({"word": word, "options": []})
        self._refresh_word_list()
        items = self.word_list_widget.findItems(word, Qt.MatchExactly)
        if items:
            self.word_list_widget.setCurrentItem(items[0])

    def _delete_word(self):
        """Remove the selected word from both in-memory structures after confirmation."""
        word = self._current_word()
        if not word:
            return
        dirty_note = "\n\nUnsaved changes will also be discarded." if self._is_dirty else ""
        reply = QMessageBox.question(
            self,
            "Delete Word",
            f"Remove '{word}' from both choices.json and pos_dictionary?{dirty_note}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.choices_data = [
            e for e in self.choices_data if e.get("word", "").lower() != word
        ]
        self.word_list = [w for w in self.word_list if w != word]
        self.pos_dict.pop(word, None)
        self._is_dirty = False
        self._current_loaded_word = None
        self._refresh_word_list()

    def _toggle_disabled(self):
        """Toggle the disabled flag in the pos_dictionary for the current word and save immediately."""
        word = self._current_word()
        if not word:
            return
        pos_word = self.pos_dict.get(word, {})
        current = bool(pos_word.get("disabled", False))
        pos_word["disabled"] = not current
        self.pos_dict[word] = pos_word
        self._write_pos_dictionary()
        self.disabled_label.setVisible(not current)
        self.disable_btn.setText("Enable" if not current else "Disable")

    def _collect_entry(self) -> Optional[dict]:
        """Gather data from all visible spelling widgets. Returns None if validation fails."""
        visible = [
            sw for sw in self.spelling_widgets
            if sw.isVisible() and sw.get_spelling()
        ]
        if not visible:
            QMessageBox.warning(self, "Error", "Enter at least one spelling.")
            return None

        # Validate dep_rules JSON in every visible widget
        for sw in visible:
            err = sw.validate_dep_rules()
            if err:
                QMessageBox.warning(self, "Invalid JSON", err)
                return None

        # Reject duplicate spellings
        spellings = [sw.get_spelling() for sw in visible]
        if len(spellings) != len(set(spellings)):
            QMessageBox.warning(self, "Error", "Spellings must be unique within a word.")
            return None

        options = [sw.get_choices_data() for sw in visible]
        pos_spellings = {}
        for sw in visible:
            pd = sw.get_pos_dict_data()
            if pd is not None:
                pos_spellings[sw.get_spelling()] = pd

        return {"options": options, "pos_spellings": pos_spellings}

    def _save(self):
        """Public Save button handler — calls _do_save and shows result."""
        if self._do_save():
            QMessageBox.information(
                self, "Saved", f"'{self._current_loaded_word}' saved to both files."
            )

    def _do_save(self) -> bool:
        """Validate, rename spelling keys if changed, update hybrid_deciders, and write both files.

        Returns True on success, False if validation failed or a write error occurred.
        """
        word = self._current_word() or self._current_loaded_word
        if not word:
            QMessageBox.warning(self, "Error", "No word selected.")
            return False

        entry = self._collect_entry()
        if entry is None:
            return False

        # Detect spelling renames: compare current spellings against originals loaded
        renames: Dict[str, str] = {}
        for i, sw in enumerate(self.spelling_widgets):
            if not sw.isVisible():
                continue
            old = self._original_spellings.get(i, "")
            new = sw.get_spelling()
            if old and new and old != new:
                renames[old] = new

        # Apply renames in pos_dict keys for this word
        if renames and word in self.pos_dict:
            pos_word = dict(self.pos_dict[word])
            for old_sp, new_sp in renames.items():
                if old_sp in pos_word:
                    pos_word[new_sp] = pos_word.pop(old_sp)
            self.pos_dict[word] = pos_word

        # Update choices_data
        for e in self.choices_data:
            if e.get("word", "").lower() == word:
                e["options"] = entry["options"]
                break

        # Update pos_dict — preserve disabled flag
        if entry["pos_spellings"]:
            old_disabled = self.pos_dict.get(word, {}).get("disabled", False)
            # Merge: keep existing spellings not in entry (other slots), replace those in entry
            existing = {
                k: v for k, v in self.pos_dict.get(word, {}).items()
                if k != "disabled"
            }
            existing.update(entry["pos_spellings"])
            if old_disabled:
                existing["disabled"] = True
            self.pos_dict[word] = existing

        # Update hybrid_deciders.py for renamed spellings
        if renames:
            self._update_hybrid_deciders(renames)

        if not self._write_choices_json():
            return False
        if not self._write_pos_dictionary():
            return False

        # Update original spellings to reflect the saved state
        for i, sw in enumerate(self.spelling_widgets):
            if sw.isVisible():
                self._original_spellings[i] = sw.get_spelling()

        self._is_dirty = False
        return True

    def _update_hybrid_deciders(self, renames: Dict[str, str]):
        """Replace old spelling string literals with new ones in hybrid_deciders.py.

        Only replaces quoted string literals — e.g., "win'd" → "wind" — which
        are the return values from decide_* functions.
        """
        deciders_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "bookfix", "ai", "hybrid_deciders.py",
        )
        try:
            with open(deciders_path, "r", encoding="utf-8") as f:
                src = f.read()
            modified = src
            for old_sp, new_sp in renames.items():
                modified = modified.replace(f'"{old_sp}"', f'"{new_sp}"')
                modified = modified.replace(f"'{old_sp}'", f"'{new_sp}'")
            if modified != src:
                with open(deciders_path, "w", encoding="utf-8") as f:
                    f.write(modified)
        except Exception as e:
            QMessageBox.warning(
                self, "Warning",
                f"Saved data files but could not update hybrid_deciders.py:\n{e}\n\n"
                f"Manually update return values for renamed spellings: {renames}",
            )

    def _confirm_discard_or_save(self) -> bool:
        """Ask user what to do with unsaved changes. Returns True to continue, False to cancel."""
        if not self._is_dirty or not self._current_loaded_word:
            return True
        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            f"Save changes to '{self._current_loaded_word}'?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        )
        if result == QMessageBox.Cancel:
            return False
        if result == QMessageBox.Yes:
            return self._do_save()
        return True  # No: discard and continue

    def closeEvent(self, event):
        """Intercept window close to prompt for unsaved changes."""
        if self._is_dirty and self._current_loaded_word:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to '{self._current_loaded_word}' before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            )
            if result == QMessageBox.Cancel:
                event.ignore()
                return
            if result == QMessageBox.Yes:
                if not self._do_save():
                    event.ignore()
                    return
        event.accept()

    def _write_choices_json(self) -> bool:
        """Write self.choices_data (with comment entries prepended) to choices.json."""
        try:
            output = self._comment_entries + self.choices_data
            with open(self.choices_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save choices.json: {e}")
            return False

    def _write_pos_dictionary(self) -> bool:
        """Write self.pos_dict (with metadata) to choices_pos_dictionary.json."""
        try:
            full = dict(self._pos_meta)
            full["words"] = self.pos_dict
            with open(self.dict_file, "w", encoding="utf-8") as f:
                json.dump(full, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save pos_dictionary: {e}")
            return False

    def _import_learned_keywords(self):
        """Import keywords from AI learning storage into each spelling's pos_dictionary context keywords."""
        word = self._current_word()
        if not word:
            QMessageBox.information(self, "No Word", "Select a word first.")
            return
        try:
            from bookfix.ai.keyword_learning import get_keyword_storage
            keyword_storage = get_keyword_storage()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load keyword storage: {e}")
            return
        if word not in keyword_storage.keywords:
            QMessageBox.information(
                self, "No Keywords", f"No learned keywords found for '{word}'."
            )
            return

        total = 0
        for sw in self.spelling_widgets:
            if not sw.isVisible():
                continue
            spelling = sw.get_spelling()
            if not spelling:
                continue
            keywords = keyword_storage.get_all_keywords(word, spelling)
            if not keywords:
                continue
            keyword_list = [kw.word for kw in keywords]
            existing = sw.pos_context_field.toPlainText().strip()
            existing_set = {k.strip().lower() for k in existing.splitlines() if k.strip()}
            new_kws = [k for k in keyword_list if k.lower() not in existing_set]
            if new_kws:
                merged = (existing + "\n" if existing else "") + "\n".join(new_kws)
                sw.pos_context_field.setPlainText(merged.strip())
                total += len(new_kws)

        QMessageBox.information(
            self, "Import Complete", f"Imported {total} new keyword(s)."
        )

    def _silent_import_keywords(self, word: str):
        """Silently merge learned keywords for a word when it is first selected."""
        try:
            from bookfix.ai.keyword_learning import get_keyword_storage
            keyword_storage = get_keyword_storage()
        except Exception:
            return
        if word not in keyword_storage.keywords:
            return
        for sw in self.spelling_widgets:
            if not sw.isVisible():
                continue
            spelling = sw.get_spelling()
            if not spelling:
                continue
            keywords = keyword_storage.get_all_keywords(word, spelling)
            if not keywords:
                continue
            keyword_list = [kw.word for kw in keywords]
            existing = sw.pos_context_field.toPlainText().strip()
            existing_set = {k.strip().lower() for k in existing.splitlines() if k.strip()}
            new_kws = [k for k in keyword_list if k.lower() not in existing_set]
            if new_kws:
                merged = (existing + "\n" if existing else "") + "\n".join(new_kws)
                sw.pos_context_field.setPlainText(merged.strip())

    def _generate_with_ai(self):
        """Call the LLM to suggest pos_dictionary fields for the currently visible spellings."""
        word = self._current_word()
        if not word:
            QMessageBox.warning(self, "Error", "Select a word first.")
            return
        visible = [
            sw for sw in self.spelling_widgets
            if sw.isVisible() and sw.get_spelling()
        ]
        if not visible:
            QMessageBox.warning(self, "Error", "Add at least one spelling first.")
            return

        pronunciations = [sw.get_spelling() for sw in visible]
        seed_data = []
        for sw in visible:
            seed_data.append({
                "pos": sw.pos_tags_field.text().strip(),
                "desc": sw.pos_desc_field.text().strip(),
                "examples": sw.examples_field.toPlainText().strip(),
            })

        try:
            from bookfix.ai.llm_client import LLMClient
            from bookfix.context import BookfixContext

            ctx = self.parent().ctx if hasattr(self.parent(), "ctx") else BookfixContext()
            client = LLMClient(ctx)
            prompt = self._build_ai_prompt(word, pronunciations, seed_data)

            QMessageBox.information(
                self, "Generating", "Calling AI to generate data. This may take a moment..."
            )
            response = client.send_message(prompt)

            if response.success:
                self._parse_ai_response(response.content, visible)
                QMessageBox.information(
                    self, "Success", "AI has generated data. Please review before saving."
                )
            else:
                QMessageBox.warning(self, "Error", f"AI generation failed: {response.error}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate with AI: {e}")

    def _build_ai_prompt(
        self, word: str, pronunciations: List[str], seed_data: List[dict]
    ) -> str:
        """Build the LLM prompt requesting pos_dictionary fields for each pronunciation."""
        prompt = (
            f"I need help creating a POS dictionary entry for the heteronym '{word}'.\n\n"
            f"This word has {len(pronunciations)} pronunciation(s): {', '.join(pronunciations)}\n\n"
        )
        for pron, seed in zip(pronunciations, seed_data):
            prompt += f"For pronunciation '{pron}':\n"
            if seed["pos"]:
                prompt += f"  - POS hint: {seed['pos']}\n"
            if seed["desc"]:
                prompt += f"  - Description hint: {seed['desc']}\n"
            if seed["examples"]:
                prompt += f"  - Examples: {seed['examples']}\n"
            prompt += "\n"

        prompt += (
            "For EACH pronunciation provide:\n"
            "1. Penn Treebank POS tags (comma-separated: VB, VBP, VBZ, VBD, VBN, NN, etc.)\n"
            "2. A brief description (5-10 words)\n"
            "3. Context keywords (10-15 words that appear near this pronunciation)\n"
            "4. Example sentences (2-3 short examples)\n\n"
            "Format EXACTLY:\n\n"
            "PRONUNCIATION: [pronunciation]\n"
            "POS_TAGS: [tags]\n"
            "DESCRIPTION: [description]\n"
            "CONTEXT_KEYWORDS: [keywords]\n"
            "EXAMPLES:\n[example 1]\n[example 2]\n\n---\n\n"
            "Generate data for all pronunciations now."
        )
        return prompt

    def _parse_ai_response(self, content: str, widgets: List[SpellingWidget]):
        """Parse the AI response and populate pos_dictionary fields in the matching widgets."""
        sections = content.split("PRONUNCIATION:")
        for section in sections[1:]:
            lines = section.strip().split("\n")
            if not lines:
                continue
            pron_name = lines[0].strip()
            pos_tags = description = context_keywords = ""
            examples: List[str] = []
            in_examples = False

            for line in lines[1:]:
                line = line.strip()
                if line.startswith("POS_TAGS:"):
                    pos_tags = line.replace("POS_TAGS:", "").strip()
                elif line.startswith("DESCRIPTION:"):
                    description = line.replace("DESCRIPTION:", "").strip()
                elif line.startswith("CONTEXT_KEYWORDS:"):
                    context_keywords = line.replace("CONTEXT_KEYWORDS:", "").strip()
                elif line.startswith("EXAMPLES:"):
                    in_examples = True
                elif in_examples and line and not line.startswith("---"):
                    ex = line.lstrip("- ").strip()
                    if ex:
                        examples.append(ex)

            for sw in widgets:
                if sw.get_spelling() != pron_name:
                    continue
                if not sw.pos_tags_field.text().strip() and pos_tags:
                    sw.pos_tags_field.setText(pos_tags)
                if not sw.pos_desc_field.text().strip() and description:
                    sw.pos_desc_field.setText(description)
                if context_keywords:
                    existing = sw.pos_context_field.toPlainText().strip()
                    kws = [k.strip() for k in context_keywords.split(",") if k.strip()]
                    if existing:
                        sw.pos_context_field.setPlainText(existing + "\n" + "\n".join(kws))
                    else:
                        sw.pos_context_field.setPlainText("\n".join(kws))
                if examples:
                    sw.examples_field.setPlainText("\n".join(examples))
                break
