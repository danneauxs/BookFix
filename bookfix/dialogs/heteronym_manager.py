"""
Heteronym Dictionary Manager GUI
Allows user to add/edit heteronym entries in choices_pos_dictionary.json
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
    QFrame,
    QGroupBox,
)
from PyQt5.QtCore import Qt


class PronunciationWidget(QWidget):
    """Widget for editing a single pronunciation variant"""

    def __init__(self, parent=None):
        """Initializes the user interface components for a pronunciation application.
        Args:
        parent (QWidget): The parent widget of this dialog.
        Returns: None
        """
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initializes the user interface for pronunciation and part-of-speech input.
        Args:
        None
        Returns:
        None
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 10)

        # Pronunciation name
        pron_layout = QHBoxLayout()
        pron_layout.addWidget(QLabel("Pronunciation:"))
        self.pronunciation_field = QLineEdit()
        self.pronunciation_field.setPlaceholderText("e.g., leed, led, etc.")
        pron_layout.addWidget(self.pronunciation_field)
        layout.addLayout(pron_layout)

        # POS tags
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("POS Tags:"))
        self.pos_tags_field = QLineEdit()
        self.pos_tags_field.setPlaceholderText(
            "e.g., VB, VBP, VBZ, NN (comma-separated)"
        )
        pos_layout.addWidget(self.pos_tags_field)
        layout.addLayout(pos_layout)

        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_field = QLineEdit()
        self.description_field.setPlaceholderText(
            "e.g., verb: to guide or noun: a leader"
        )
        desc_layout.addWidget(self.description_field)
        layout.addLayout(desc_layout)

        # Semantic tags
        layout.addWidget(QLabel("Semantic Tags (comma-separated context words):"))
        self.semantic_tags_field = QTextEdit()
        self.semantic_tags_field.setPlaceholderText(
            "e.g., guide, leader, team, command, etc."
        )
        self.semantic_tags_field.setMaximumHeight(60)
        layout.addWidget(self.semantic_tags_field)

        # Context keywords (NEW)
        layout.addWidget(
            QLabel("Context Keywords (comma-separated strong indicators):")
        )
        self.context_keywords_field = QTextEdit()
        self.context_keywords_field.setPlaceholderText(
            "e.g., door, window, eyes (for close=verb) or friend, relationship (for close=adjective)"
        )
        self.context_keywords_field.setMaximumHeight(60)
        self.context_keywords_field.setStyleSheet(
            "background-color: #ffffcc;"
        )  # Light yellow to distinguish from semantic tags
        layout.addWidget(self.context_keywords_field)

        # Examples
        layout.addWidget(QLabel("Examples (one per line):"))
        self.examples_field = QTextEdit()
        self.examples_field.setPlaceholderText(
            "will lead the team\nin the lead\nlead position"
        )
        self.examples_field.setMaximumHeight(60)
        layout.addWidget(self.examples_field)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        self.setLayout(layout)

    def get_data(self) -> Dict:
        """Get pronunciation data from fields"""
        pronunciation = self.pronunciation_field.text().strip()
        if not pronunciation:
            return {}

        # Parse POS tags
        pos_tags_text = self.pos_tags_field.text().strip()
        pos_tags = [tag.strip() for tag in pos_tags_text.split(",") if tag.strip()]

        # Parse semantic tags
        semantic_tags_text = self.semantic_tags_field.toPlainText().strip()
        semantic_tags = [
            tag.strip() for tag in semantic_tags_text.split(",") if tag.strip()
        ]

        # Parse context keywords (NEW)
        context_keywords_text = self.context_keywords_field.toPlainText().strip()
        context_keywords = [
            kw.strip() for kw in context_keywords_text.split(",") if kw.strip()
        ]

        # Parse examples
        examples_text = self.examples_field.toPlainText().strip()
        examples = [ex.strip() for ex in examples_text.split("\n") if ex.strip()]

        data = {
            "pos_tags": pos_tags,
            "description": self.description_field.text().strip(),
        }

        if semantic_tags:
            data["semantic_tags"] = semantic_tags

        if context_keywords:
            data["context_keywords"] = context_keywords

        if examples:
            data["examples"] = examples

        return {pronunciation: data}

    def set_data(self, pronunciation: str, data: Dict):
        """Load pronunciation data into fields"""
        self.pronunciation_field.setText(pronunciation)

        # Load POS tags
        pos_tags = data.get("pos_tags", [])
        self.pos_tags_field.setText(", ".join(pos_tags))

        # Load description
        self.description_field.setText(data.get("description", ""))

        # Load semantic tags
        semantic_tags = data.get("semantic_tags", [])
        self.semantic_tags_field.setPlainText(", ".join(semantic_tags))

        # Load context keywords (NEW)
        context_keywords = data.get("context_keywords", [])
        self.context_keywords_field.setPlainText(", ".join(context_keywords))

        # Load examples
        examples = data.get("examples", [])
        self.examples_field.setPlainText("\n".join(examples))

    def clear(self):
        """Clears all fields in the heteronym dictionary manager dialog.
        Args:
        None
        Returns:
        None
        """
        """Clear all fields"""
        self.pronunciation_field.clear()
        self.pos_tags_field.clear()
        self.description_field.clear()
        self.semantic_tags_field.clear()
        self.context_keywords_field.clear()  # NEW
        self.examples_field.clear()


class HeteronymDictionaryManager(QDialog):
    """Dialog for managing heteronym dictionary entries"""

    def __init__(self, parent=None):
        """Initialize a Heteronym Dictionary Manager window.
        Args:
        parent (QWidget): Parent widget for this manager.
        Returns: None
        """
        super().__init__(parent)
        self.setWindowTitle("Heteronym Dictionary Manager")
        self.setMinimumSize(800, 700)

        # Load dictionary
        self.dict_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            ".ai_learning",
            "choices_pos_dictionary.json",
        )
        self.load_dictionary()

        # Current state
        self.current_index = 0
        self.is_new_entry = False

        self.init_ui()
        self.display_current_entry()

    def load_dictionary(self):
        """Load the dictionary from JSON file"""
        try:
            with open(self.dict_file, "r", encoding="utf-8") as f:
                self.dictionary = json.load(f)

            # Extract just the words section
            self.words = self.dictionary.get("words", {})
            self.word_list = list(self.words.keys())
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load dictionary: {e}")
            self.dictionary = {
                "version": "1.0",
                "description": "POS-tagged pronunciation dictionary for heteronyms",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "words": {},
            }
            self.words = {}
            self.word_list = []

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()

        # Top button bar
        button_layout = QHBoxLayout()

        self.prev_button = QPushButton("◀ Prev")
        self.prev_button.clicked.connect(self.prev_entry)
        button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self.next_entry)
        button_layout.addWidget(self.next_button)

        self.position_label = QLabel()
        button_layout.addWidget(self.position_label)
        button_layout.addStretch()

        self.add_button = QPushButton("ADD")
        self.add_button.clicked.connect(self.add_new_entry)
        button_layout.addWidget(self.add_button)

        self.disable_button = QPushButton("DISABLE")
        self.disable_button.clicked.connect(self.toggle_disabled)
        button_layout.addWidget(self.disable_button)

        self.import_keywords_button = QPushButton("Import Learned Keywords")
        self.import_keywords_button.clicked.connect(self.import_learned_keywords)
        self.import_keywords_button.setToolTip(
            "Import keywords from AI learning storage"
        )
        button_layout.addWidget(self.import_keywords_button)

        main_layout.addLayout(button_layout)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        content_layout = QVBoxLayout()

        # Word field
        word_layout = QHBoxLayout()
        word_layout.addWidget(QLabel("Word:"))
        self.word_field = QLineEdit()
        self.word_field.setPlaceholderText("The heteronym (e.g., lead, read, close)")
        self.word_field.textChanged.connect(self.check_word_exists)
        word_layout.addWidget(self.word_field)
        content_layout.addLayout(word_layout)

        # Pronunciation widgets (start with 4 slots)
        content_layout.addWidget(QLabel("<b>Pronunciations:</b>"))
        self.pronunciation_widgets = []
        for i in range(4):
            widget = PronunciationWidget()
            self.pronunciation_widgets.append(widget)
            content_layout.addWidget(widget)

        scroll_content.setLayout(content_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Generate button
        generate_layout = QHBoxLayout()
        generate_layout.addStretch()
        self.generate_button = QPushButton("GENERATE")
        self.generate_button.clicked.connect(self.generate_with_ai)
        self.generate_button.setStyleSheet("font-weight: bold; padding: 10px;")
        generate_layout.addWidget(self.generate_button)
        generate_layout.addStretch()
        main_layout.addLayout(generate_layout)

        # POS Tags Legend (collapsible)
        legend_box = QGroupBox("POS Tags Reference (click to show/hide)")
        legend_box.setCheckable(True)
        legend_box.setChecked(False)  # Hidden by default

        # Content widget that will be hidden/shown
        self.legend_content = QWidget()
        legend_content_layout = QVBoxLayout()
        legend_content_layout.setContentsMargins(0, 0, 0, 0)

        legend_text = QLabel(
            """
<b>Common POS Tags:</b><br>
<table style="margin-left: 10px; line-height: 1.6;">
<tr><td><b>Verbs:</b></td><td>VB (base), VBP (present), VBZ (3rd singular), VBD (past), VBN (past participle), VBG (gerund/present participle)</td></tr>
<tr><td><b>Nouns:</b></td><td>NN (singular), NNS (plural), NNP (proper singular), NNPS (proper plural)</td></tr>
<tr><td><b>Adjectives:</b></td><td>JJ (base), JJR (comparative), JJS (superlative)</td></tr>
<tr><td><b>Adverbs:</b></td><td>RB (base), RBR (comparative), RBS (superlative)</td></tr>
<tr><td><b>Other:</b></td><td>IN (preposition), RP (particle), DT (determiner)</td></tr>
</table>
        """
        )
        legend_text.setWordWrap(True)
        legend_text.setTextFormat(Qt.RichText)
        legend_content_layout.addWidget(legend_text)
        self.legend_content.setLayout(legend_content_layout)
        self.legend_content.setVisible(False)  # Hidden by default

        # Add content to group box
        legend_box_layout = QVBoxLayout()
        legend_box_layout.addWidget(self.legend_content)
        legend_box.setLayout(legend_box_layout)

        # Connect checkbox to toggle visibility
        legend_box.toggled.connect(self.legend_content.setVisible)

        main_layout.addWidget(legend_box)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_entry)
        save_button.setStyleSheet("font-weight: bold;")
        bottom_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_button)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def update_position_label(self):
        """Update the position indicator"""
        if self.is_new_entry:
            self.position_label.setText("New Entry")
        elif self.word_list:
            total = len(self.word_list)
            self.position_label.setText(f"Entry {self.current_index + 1} of {total}")
        else:
            self.position_label.setText("No Entries")

        # Update button states
        self.prev_button.setEnabled(not self.is_new_entry and self.current_index > 0)
        self.next_button.setEnabled(
            not self.is_new_entry and self.current_index < len(self.word_list) - 1
        )
        self.disable_button.setEnabled(
            not self.is_new_entry and len(self.word_list) > 0
        )

    def display_current_entry(self):
        """Display the current entry in the form"""
        # Clear all fields first
        self.word_field.clear()
        for widget in self.pronunciation_widgets:
            widget.clear()

        if self.is_new_entry or not self.word_list:
            self.update_position_label()
            return

        # Load current word
        word = self.word_list[self.current_index]
        self.word_field.setText(word)

        # Load pronunciations
        pronunciations = self.words[word]
        for i, (pronunciation, data) in enumerate(pronunciations.items()):
            if i < len(self.pronunciation_widgets):
                self.pronunciation_widgets[i].set_data(pronunciation, data)

        # Update disable button text
        is_disabled = pronunciations.get("disabled", False)
        self.disable_button.setText("ENABLE" if is_disabled else "DISABLE")

        self.update_position_label()
        self._silent_import_keywords()

    def prev_entry(self):
        """Go to previous entry"""
        if self.current_index > 0:
            self.is_new_entry = False
            self.current_index -= 1
            self.display_current_entry()

    def next_entry(self):
        """Go to next entry
        Args:
        - None
        Returns:
        - None
        Switch to blank form for new entry
        Args:
        - None
        Returns:
        - None
        Toggle disabled status of current entry
        Args:
        - None
        Returns:
        - None
        """
        """Go to next entry"""
        if self.current_index < len(self.word_list) - 1:
            self.is_new_entry = False
            self.current_index += 1
            self.display_current_entry()

    def add_new_entry(self):
        """Switch to blank form for new entry"""
        self.is_new_entry = True
        self.display_current_entry()

    def toggle_disabled(self):
        """Toggle disabled status of current entry"""
        if self.is_new_entry or not self.word_list:
            return

        word = self.word_list[self.current_index]
        pronunciations = self.words[word]

        is_disabled = pronunciations.get("disabled", False)
        pronunciations["disabled"] = not is_disabled

        # Update button text
        self.disable_button.setText("ENABLE" if not is_disabled else "DISABLE")

        # Save to file
        self.save_dictionary()

        QMessageBox.information(
            self,
            "Success",
            f"Entry '{word}' has been {'disabled' if not is_disabled else 'enabled'}.",
        )

    def check_word_exists(self):
        """Check if word already exists when user types"""
        # Only check if we're in new entry mode
        if not self.is_new_entry:
            return

        word = self.word_field.text().strip().lower()
        if not word:
            return

        if word in self.words:
            reply = QMessageBox.question(
                self,
                "Word Exists",
                f"Word '{word}' already exists with {len([k for k in self.words[word].keys() if k != 'disabled'])} pronunciations.\n\nEdit existing entry?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                # Load existing entry
                self.is_new_entry = False
                self.current_index = self.word_list.index(word)
                self.display_current_entry()

    def generate_with_ai(self):
        """Generate POS tags, semantic tags, descriptions, and examples using AI"""
        word = self.word_field.text().strip()
        if not word:
            QMessageBox.warning(self, "Error", "Please enter a word first.")
            return

        # Collect pronunciations
        pronunciations = []
        seed_data = []

        for widget in self.pronunciation_widgets:
            pron = widget.pronunciation_field.text().strip()
            if pron:
                # Collect any seed data user has entered
                pos_hint = widget.pos_tags_field.text().strip()
                desc_hint = widget.description_field.text().strip()
                sem_hint = widget.semantic_tags_field.toPlainText().strip()
                ex_hint = widget.examples_field.toPlainText().strip()

                pronunciations.append(pron)
                seed_data.append(
                    {
                        "pos": pos_hint,
                        "desc": desc_hint,
                        "semantic": sem_hint,
                        "examples": ex_hint,
                    }
                )

        if not pronunciations:
            QMessageBox.warning(
                self, "Error", "Please enter at least one pronunciation."
            )
            return

        # Import AI client
        try:
            from bookfix.ai.llm_client import LLMClient
            from bookfix.context import BookfixContext

            # Get parent's context (from main GUI)
            if hasattr(self.parent(), "ctx"):
                ctx = self.parent().ctx
            else:
                ctx = BookfixContext()

            client = LLMClient(ctx)

            # Build prompt
            prompt = self._build_ai_prompt(word, pronunciations, seed_data)

            # Call AI
            QMessageBox.information(
                self,
                "Generating",
                "Calling AI to generate data. This may take a moment...",
            )

            response = client.send_message(prompt)

            if response.success:
                # Parse response and fill in fields
                self._parse_ai_response(response.content, pronunciations)
                QMessageBox.information(
                    self,
                    "Success",
                    "AI has generated data. Please review and edit as needed.",
                )
            else:
                QMessageBox.warning(
                    self, "Error", f"AI generation failed: {response.error}"
                )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate with AI: {e}")

    def _build_ai_prompt(
        self, word: str, pronunciations: List[str], seed_data: List[Dict]
    ) -> str:
        """Build the AI prompt for generating dictionary data"""
        prompt = f"I need help creating a pronunciation dictionary entry for the heteronym '{word}'.\n\n"
        prompt += f"This word has {len(pronunciations)} different pronunciations: {', '.join(pronunciations)}\n\n"

        for i, (pron, seed) in enumerate(zip(pronunciations, seed_data)):
            prompt += f"For pronunciation '{pron}':\n"

            if seed["pos"]:
                prompt += f"  - User hint for POS: {seed['pos']}\n"
            if seed["desc"]:
                prompt += f"  - User hint for description: {seed['desc']}\n"
            if seed["semantic"]:
                prompt += f"  - User provided semantic tags: {seed['semantic']}\n"
            if seed["examples"]:
                prompt += f"  - User provided examples: {seed['examples']}\n"

            prompt += "\n"

        prompt += """For EACH pronunciation, please provide:
1. Penn Treebank POS tags (comma-separated, e.g., VB, VBP, VBZ, NN, NNS, JJ)
2. A brief description (5-10 words explaining when this pronunciation is used)
3. Semantic context words (10-15 words that commonly appear near this pronunciation, comma-separated)
4. Example sentences (2-3 short examples showing usage)

Please format your response EXACTLY like this for each pronunciation:

PRONUNCIATION: [pronunciation]
POS_TAGS: [tags]
DESCRIPTION: [description]
SEMANTIC_TAGS: [tags]
EXAMPLES:
[example 1]
[example 2]
[example 3]

---

Generate data for all pronunciations now."""

        return prompt

    def _parse_ai_response(self, content: str, pronunciations: List[str]):
        """Parse AI response and populate fields"""
        # Split by pronunciation sections
        sections = content.split("PRONUNCIATION:")

        for section in sections[1:]:  # Skip first empty section
            lines = section.strip().split("\n")
            if not lines:
                continue

            # Extract pronunciation name
            pron_name = lines[0].strip()

            pos_tags = ""
            description = ""
            semantic_tags = ""
            examples = []

            in_examples = False

            for line in lines[1:]:
                line = line.strip()

                if line.startswith("POS_TAGS:"):
                    pos_tags = line.replace("POS_TAGS:", "").strip()
                elif line.startswith("DESCRIPTION:"):
                    description = line.replace("DESCRIPTION:", "").strip()
                elif line.startswith("SEMANTIC_TAGS:"):
                    semantic_tags = line.replace("SEMANTIC_TAGS:", "").strip()
                elif line.startswith("EXAMPLES:"):
                    in_examples = True
                elif in_examples and line and not line.startswith("---"):
                    # Remove leading dashes or bullets
                    example = line.lstrip("- ").strip()
                    if example:
                        examples.append(example)

            # Find matching pronunciation widget
            for widget in self.pronunciation_widgets:
                if widget.pronunciation_field.text().strip() == pron_name:
                    # Only fill in empty fields (preserve user's seed data if they want to keep it)
                    if not widget.pos_tags_field.text().strip() and pos_tags:
                        widget.pos_tags_field.setText(pos_tags)

                    if not widget.description_field.text().strip() and description:
                        widget.description_field.setText(description)

                    # For semantic tags and examples, append to existing if any
                    existing_semantic = widget.semantic_tags_field.toPlainText().strip()
                    if existing_semantic and semantic_tags:
                        combined_semantic = existing_semantic + ", " + semantic_tags
                        widget.semantic_tags_field.setPlainText(combined_semantic)
                    elif semantic_tags:
                        widget.semantic_tags_field.setPlainText(semantic_tags)

                    existing_examples = widget.examples_field.toPlainText().strip()
                    if existing_examples and examples:
                        combined_examples = (
                            existing_examples + "\n" + "\n".join(examples)
                        )
                        widget.examples_field.setPlainText(combined_examples)
                    elif examples:
                        widget.examples_field.setPlainText("\n".join(examples))

                    break

    def save_entry(self):
        """Save the current entry to the dictionary"""
        word = self.word_field.text().strip().lower()
        if not word:
            QMessageBox.warning(self, "Error", "Please enter a word.")
            return

        # Collect pronunciation data
        entry_data = {}
        pronunciations_found = 0

        for widget in self.pronunciation_widgets:
            pron_data = widget.get_data()
            if pron_data:
                entry_data.update(pron_data)
                pronunciations_found += 1

        if pronunciations_found < 1:
            QMessageBox.warning(
                self, "Error", "Please enter at least one pronunciation with data."
            )
            return

        # Check if pronunciations are different
        pron_names = list(entry_data.keys())
        if len(pron_names) != len(set(pron_names)):
            QMessageBox.warning(
                self, "Error", "Pronunciations must be different from each other."
            )
            return

        # Validate each pronunciation has required fields
        for pron, data in entry_data.items():
            if not data.get("pos_tags"):
                reply = QMessageBox.question(
                    self,
                    "Missing Data",
                    f"Pronunciation '{pron}' is missing POS tags. Save anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

        # Add to dictionary
        if word in self.words and not self.is_new_entry:
            # Update existing entry (preserve disabled status if it exists)
            if "disabled" in self.words[word]:
                entry_data["disabled"] = self.words[word]["disabled"]

        self.words[word] = entry_data

        # Update word list if new
        if word not in self.word_list:
            self.word_list.append(word)
            self.word_list.sort()

        # Save to file
        if self.save_dictionary():
            QMessageBox.information(self, "Success", f"Entry '{word}' has been saved.")

            # Update state
            self.is_new_entry = False
            self.current_index = self.word_list.index(word)
            self.display_current_entry()

    def import_learned_keywords(self):
        """Import keywords from AI learning storage into current entry."""
        word = self.word_field.text().strip().lower()
        if not word:
            QMessageBox.information(self, "No Word", "Please enter a word first.")
            return

        # Import keyword storage
        try:
            from bookfix.ai.keyword_learning import get_keyword_storage

            keyword_storage = get_keyword_storage()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load keyword storage: {e}")
            return

        # Get keywords for this word
        if word not in keyword_storage.keywords:
            QMessageBox.information(
                self, "No Keywords", f"No learned keywords found for '{word}'."
            )
            return

        # Show import dialog with keyword stats
        import_text = f"Found learned keywords for '{word}':\n\n"
        total_imported = 0

        for pron_idx, widget in enumerate(self.pronunciation_widgets):
            pronunciation = widget.pronunciation_field.text().strip().lower()
            if not pronunciation:
                continue

            # Get keywords for this pronunciation
            keywords = keyword_storage.get_all_keywords(word, pronunciation)
            if not keywords:
                continue

            # Build import text
            import_text += f"\n{pronunciation} ({len(keywords)} keywords):\n"
            keyword_list = []
            for kw in keywords:
                manual_flag = "✓" if kw.manual else "AI"
                import_text += f"  • {kw.word} (conf: {kw.confidence:.2f}, {manual_flag}, seen: {kw.learned_from}x)\n"
                keyword_list.append(kw.word)

            # Get existing context keywords
            existing_text = widget.context_keywords_field.toPlainText().strip()
            existing_keywords = set(
                k.strip().lower() for k in existing_text.split(",") if k.strip()
            )

            # Merge learned keywords with existing (avoiding duplicates)
            new_keywords = [
                kw for kw in keyword_list if kw.lower() not in existing_keywords
            ]
            if new_keywords:
                if existing_text:
                    merged_keywords = existing_text + ", " + ", ".join(new_keywords)
                else:
                    merged_keywords = ", ".join(new_keywords)
                widget.context_keywords_field.setPlainText(merged_keywords)
                total_imported += len(new_keywords)

        if total_imported == 0:
            import_text += "\n(No new keywords to import - all are already present)"

        import_text += f"\n\nTotal new keywords imported: {total_imported}"

        QMessageBox.information(self, "Import Complete", import_text)

    def _silent_import_keywords(self):
        """Silently attempts to import keywords for a given word.
        Args:
        self (object): The current object instance.
        Returns:
        None
        """
        word = self.word_field.text().strip().lower()
        if not word:
            return

        print(f"DEBUG: Silent import for word: {word}")

        try:
            from bookfix.ai.keyword_learning import get_keyword_storage

            keyword_storage = get_keyword_storage()
        except Exception as e:
            print(f"DEBUG: Failed to get keyword storage: {e}")
            return

        if word not in keyword_storage.keywords:
            print(f"DEBUG: No keywords found in storage for word: {word}")
            return

        for widget in self.pronunciation_widgets:
            try:
                pronunciation = widget.pronunciation_field.text().strip().lower()
                if not pronunciation:
                    continue

                print(f"DEBUG: Checking pronunciation: {pronunciation}")

                keywords = keyword_storage.get_all_keywords(word, pronunciation)
                if not keywords:
                    continue

                print(
                    f"DEBUG: Found keywords for {pronunciation}: {[kw.word for kw in keywords]}"
                )

                keyword_list = [kw.word for kw in keywords]
                existing_text = widget.context_keywords_field.toPlainText().strip()
                existing_keywords = set(
                    k.strip().lower() for k in existing_text.split(",") if k.strip()
                )

                new_keywords = [
                    kw for kw in keyword_list if kw.lower() not in existing_keywords
                ]
                if new_keywords:
                    print(f"DEBUG: New keywords to add: {new_keywords}")
                    if existing_text:
                        merged_keywords = existing_text + ", " + ", ".join(new_keywords)
                    else:
                        merged_keywords = ", ".join(new_keywords)

                    print(
                        f"DEBUG: Setting context_keywords_field to: {merged_keywords}"
                    )
                    widget.context_keywords_field.setPlainText(merged_keywords)
            except Exception as e:
                print(f"DEBUG: Error in _silent_import_keywords loop: {e}")

    def save_dictionary(self) -> bool:
        """Save the dictionary to JSON file"""
        try:
            # Update the words section
            self.dictionary["words"] = self.words

            # Write to file
            with open(self.dict_file, "w", encoding="utf-8") as f:
                json.dump(self.dictionary, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save dictionary: {e}")
            return False
