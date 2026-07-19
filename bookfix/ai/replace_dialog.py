"""
Add Replace Rule Dialog for AI Changes Review.

PyQt5 modal dialog allowing user to add text replacement rules
to the .data.txt configuration file.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..logging import log_message


_WORD_EDGE_PUNCTUATION = ".,!?;:\"'\u201c\u201d\u2018\u2019\u00ab\u00bb()[]{}"
_IRREGULAR_SOURCE_FORMS = {
    ("read", "ed"): "read",
    ("lead", "ed"): "led",
}
_LINKING_VERBS = {"am", "are", "be", "been", "being", "is", "was", "were"}
_VERB_PREPOSITIONS = {
    "from",
    "into",
    "onto",
    "through",
    "to",
    "toward",
    "towards",
}


@dataclass(frozen=True)
class ReplacementSuggestion:
    """Represent one complete phrase rule suggested from a base rule."""

    from_text: str
    to_text: str
    label: str


def _load_choice_entries(choices_path: Path) -> Dict[str, List[dict]]:
    """Load choice options keyed by normalized source word.

    Args:
        choices_path: JSON file containing canonical homograph choices.

    Returns:
        Mapping from lowercase source word to its option records.
    """
    try:
        with choices_path.open(encoding="utf-8") as handle:
            entries = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        log_message(f"Could not load choices for replacement suggestions: {exc}", level="WARNING")
        return {}

    return {
        entry["word"].casefold(): entry.get("options", [])
        for entry in entries
        if isinstance(entry, dict) and entry.get("word")
    }


def _normalized_word(token: str) -> str:
    """Remove edge punctuation before comparing a phrase token to choices data.

    Args:
        token: Whitespace-delimited phrase token.

    Returns:
        Token normalized for case-insensitive choice lookup.
    """
    return token.strip(_WORD_EDGE_PUNCTUATION).casefold()


def _inflect_source(word: str, suffix: str) -> str:
    """Create common plural, past-tense, or gerund source forms.

    Args:
        word: Base source word without edge punctuation.
        suffix: One of ``s``, ``ed``, or ``ing``.

    Returns:
        Inflected source word using conservative English spelling rules.
    """
    irregular = _IRREGULAR_SOURCE_FORMS.get((word.casefold(), suffix))
    if irregular is not None:
        return irregular
    # Apply regular plural spelling rules only when no known irregular form exists.
    if suffix == "s":
        if word.casefold().endswith(("s", "x", "z", "ch", "sh")):
            return word + "es"
        return word + "s"
    if suffix == "ed":
        if word.casefold().endswith("e"):
            return word + "d"
        if word.casefold().endswith("y") and len(word) > 1 and word[-2].lower() not in "aeiou":
            return word[:-1] + "ied"
        return word + "ed"
    if suffix == "ing":
        if word.casefold().endswith("e") and not word.casefold().endswith("ee"):
            return word[:-1] + "ing"
        return word + "ing"
    raise ValueError(f"Unsupported replacement suffix: {suffix}")


def _inflect_replacement(spelling: str, suffix: str) -> str:
    """Apply suffix spelling to a TTS replacement phrase.

    Args:
        spelling: Choice spelling, which may contain spaces.
        suffix: One of ``s``, ``ed``, or ``ing``.

    Returns:
        Inflected replacement spelling preserving its internal spaces.
    """
    parts = spelling.split()
    if not parts:
        return spelling
    parts[-1] = _inflect_source(parts[-1], suffix)
    return " ".join(parts)


def _choice_suffixes(
    left_tokens: Sequence[str],
    target_index: int,
    selected_option: Optional[dict],
) -> Tuple[str, ...]:
    """Select suffixes that are plausible for the phrase's local grammar.

    Args:
        left_tokens: Tokens from the source phrase.
        target_index: Index of the Choices word in the source phrase.
        selected_option: Choice record matched on the destination side.

    Returns:
        Suffix names to offer in the related-rules dialog.
    """
    grammar = (selected_option or {}).get("grammar", {})
    verb_forms = {
        str(form).casefold() for form in grammar.get("verb_forms", [])
    }
    previous = _normalized_word(left_tokens[target_index - 1]) if target_index else ""
    following = (
        _normalized_word(left_tokens[target_index + 1])
        if target_index + 1 < len(left_tokens)
        else ""
    )

    # Past-tense choices such as "red" should offer the base spelling's gerund,
    # not fabricated forms such as "reding" or "readed".
    if "past" in verb_forms or "participle" in verb_forms:
        return ("ing",)
    # A linking verb normally permits a following gerund, not third-person or
    # invented past forms.
    if previous in _LINKING_VERBS:
        return ("ing",)
    # Plural subjects followed by a directional preposition use the base verb;
    # offer its gerund but do not invent forms such as "pipes leads".
    if previous.endswith("s") and following in _VERB_PREPOSITIONS:
        return ("ing",)
    return ("s", "ed", "ing")


def _option_for_suffix(options: Sequence[dict], selected_option: Optional[dict], suffix: str) -> Optional[dict]:
    """Choose spelling option whose grammatical form matches a suffix.

    Args:
        options: Choice options for the source word.
        selected_option: Option used by the base replacement.
        suffix: Requested inflection suffix.

    Returns:
        Best option record, or ``None`` when no better option exists.
    """
    for option in options:
        forms = {
            str(form).casefold()
            for form in option.get("grammar", {}).get("verb_forms", [])
        }
        if suffix == "ing" and ("base" in forms or "imperative" in forms):
            return option
        if suffix == "ed" and ("past" in forms or "participle" in forms):
            return option
    # Older choice records omit grammar details; use a verb spelling for
    # inflected forms when one is available instead of appending to a noun.
    if suffix in {"ed", "ing"}:
        for option in options:
            pos_tags = {
                tag.strip() for tag in str(option.get("pos", "")).upper().split("/")
            }
            if "VERB" in pos_tags:
                return option
    # Selected spelling remains safest when metadata does not identify a form.
    return selected_option


def _replace_token(tokens: Sequence[str], index: int, replacement: str) -> List[str]:
    """Replace one phrase token while retaining punctuation attached to it.

    Args:
        tokens: Original whitespace-delimited phrase tokens.
        index: Index of target token.
        replacement: Replacement text for target token.

    Returns:
        New token list with target token replaced.
    """
    token = tokens[index]
    leading = token[: len(token) - len(token.lstrip(_WORD_EDGE_PUNCTUATION))]
    trailing = token[len(token.rstrip(_WORD_EDGE_PUNCTUATION)) :]
    return list(tokens[:index]) + [leading + replacement + trailing] + list(tokens[index + 1 :])


def _find_option_tokens(tokens: Sequence[str], spelling: str) -> Optional[Tuple[int, int]]:
    """Find a choice spelling's token span inside a replacement phrase.

    Args:
        tokens: Whitespace-delimited replacement phrase tokens.
        spelling: Choice spelling, possibly containing spaces.

    Returns:
        Inclusive start and exclusive end token indices, or ``None`` when absent.
    """
    option_tokens = spelling.split()
    normalized = [_normalized_word(token) for token in tokens]
    target = [_normalized_word(token) for token in option_tokens]
    for start in range(len(tokens) - len(option_tokens) + 1):
        if normalized[start : start + len(option_tokens)] == target:
            return start, start + len(option_tokens)
    return None


def _replace_token_span(tokens: Sequence[str], start: int, end: int, replacement: str) -> List[str]:
    """Replace a multi-token choice spelling while retaining ending punctuation.

    Args:
        tokens: Original phrase tokens.
        start: Inclusive start index of choice spelling.
        end: Exclusive end index of choice spelling.
        replacement: Replacement spelling, possibly containing spaces.

    Returns:
        New token list with choice spelling replaced.
    """
    trailing = tokens[end - 1][len(tokens[end - 1].rstrip(_WORD_EDGE_PUNCTUATION)) :]
    replacement_tokens = replacement.split()
    replacement_tokens[-1] += trailing
    return list(tokens[:start]) + replacement_tokens + list(tokens[end:])


def _changed_word_index(left_tokens: Sequence[str], right_tokens: Sequence[str]) -> Optional[int]:
    """Find sole changed left-token index when no choices word identifies it.

    Args:
        left_tokens: Tokens from rule's source phrase.
        right_tokens: Tokens from rule's replacement phrase.

    Returns:
        Changed left-token index, or ``None`` when comparison is ambiguous.
    """
    if len(left_tokens) != len(right_tokens):
        return None
    changed = [
        index
        for index, (left, right) in enumerate(zip(left_tokens, right_tokens))
        if left.casefold() != right.casefold()
    ]
    return changed[0] if len(changed) == 1 else None


def build_replacement_suggestions(
    from_text: str,
    to_text: str,
    choices_path: Optional[Path] = None,
) -> List[ReplacementSuggestion]:
    """Build full-phrase suffix rules from one user-entered replacement.

    The function scans every source phrase token for a Choices entry. If it finds
    one, it matches the corresponding choice spelling in the destination phrase
    and uses POS-aware stems for plural, past, and gerund forms. If no Choices
    entry exists, it uses the single changed token as a deterministic fallback.

    Args:
        from_text: Full source phrase entered by the user.
        to_text: Full replacement phrase entered by the user.
        choices_path: Optional path to choices JSON; project default is used otherwise.

    Returns:
        Deduplicated suffix suggestions, excluding the base rule.
    """
    left_tokens = from_text.split()
    right_tokens = to_text.split()
    if not left_tokens or not right_tokens:
        return []

    if choices_path is None:
        choices_path = Path(__file__).parents[2] / "data" / "choices.json"
    choices = _load_choice_entries(choices_path)

    target_index = None
    options: List[dict] = []
    for index, token in enumerate(left_tokens):
        candidate_options = choices.get(_normalized_word(token))
        if candidate_options:
            target_index = index
            options = candidate_options
            break

    if target_index is None:
        target_index = _changed_word_index(left_tokens, right_tokens)
        if target_index is None:
            return []
        source_word = _normalized_word(left_tokens[target_index])
        replacement_word = right_tokens[target_index]
        selected_spelling = replacement_word
        selected_option = None
    else:
        source_word = _normalized_word(left_tokens[target_index])
        selected_option = None
        selected_spelling = ""
        for option in options:
            span = _find_option_tokens(right_tokens, option.get("spelling", ""))
            if span:
                selected_option = option
                selected_spelling = option["spelling"]
                break
        if not selected_spelling:
            return []

    candidate_forms: List[Tuple[str, str, str]] = []
    suffixes = _choice_suffixes(left_tokens, target_index, selected_option)
    for suffix in suffixes:
        source_form = _inflect_source(source_word, suffix)
        replacement_option = _option_for_suffix(options, selected_option, suffix)
        if replacement_option is None:
            replacement_spelling = selected_spelling
        else:
            replacement_spelling = replacement_option.get("spelling", selected_spelling)
        replacement_form = _inflect_replacement(replacement_spelling, suffix)

        # Do not offer an unchanged source phrase for irregular forms such as
        # read -> read; base rule already covers that spelling.
        if source_form.casefold() == source_word.casefold():
            continue

        left_variant = _replace_token(left_tokens, target_index, source_form)
        if selected_option is None:
            right_variant = _replace_token(right_tokens, target_index, replacement_form)
        else:
            option_span = _find_option_tokens(right_tokens, selected_spelling)
            if option_span is None:
                continue
            right_variant = _replace_token_span(
                right_tokens,
                option_span[0],
                option_span[1],
                replacement_form,
            )
        candidate_forms.append((" ".join(left_variant), " ".join(right_variant), suffix))

    seen = set()
    suggestions = []
    for generated_from, generated_to, suffix in candidate_forms:
        key = (generated_from.casefold(), generated_to.casefold())
        if key in seen or key == (from_text.casefold(), to_text.casefold()):
            continue
        seen.add(key)
        suggestions.append(
            ReplacementSuggestion(
                generated_from,
                generated_to,
                f"{generated_from} -> {generated_to} ({suffix} form)",
            )
        )
    return suggestions


class SuffixSuggestionsDialog(QDialog):
    """Let users select full-phrase suffix rules before they are written."""

    def __init__(self, suggestions: Sequence[ReplacementSuggestion], parent=None):
        """Initialize selectable suffix-rule suggestions.

        Args:
            suggestions: Candidate full-phrase rules to display.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.checkboxes: List[QCheckBox] = []
        self.setWindowTitle("Add Related Replacement Rules")
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select related forms to add with this replacement:"))
        for suggestion in suggestions:
            checkbox = QCheckBox(suggestion.label)
            # Related rules are optional; require the user to opt in to each one.
            checkbox.setChecked(False)
            checkbox.setProperty("suggestion", suggestion)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_suggestions(self) -> List[ReplacementSuggestion]:
        """Return suggestions selected by the user.

        Returns:
            Selected suggestions in display order.
        """
        return [
            checkbox.property("suggestion")
            for checkbox in self.checkboxes
            if checkbox.isChecked()
        ]


class AddReplaceDialog(QDialog):
    """
    Modal dialog for adding replacement rules to .data.txt.

    Users enter rules in format: "from text -> to text"
    Rules are appended to the # REPLACE section of .data.txt
    """

    def __init__(self, data_file_path: str = ".data.txt", prefill: str = "", parent=None):
        """
        Initialize add replace dialog.

        Args:
            data_file_path: Path to .data.txt configuration file
            prefill: Pre-fill text for the input field (context: "word1 word2 word3 -> word1 replacement word3")
            parent: Parent widget
        """
        super().__init__(parent)

        self.data_file_path = data_file_path
        self.prefill = prefill
        self.from_text = ""
        self.to_text = ""

        self.setWindowTitle("Add Replacement Rule")
        self.setModal(True)
        self.resize(500, 200)

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout(self)

        # Info section
        info_label = QLabel(
            "Add a new text replacement rule.\n"
            "Format: from text -> to text\n\n"
            "Example: to lead -> to leed"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10pt;")
        main_layout.addWidget(info_label)

        # Input section
        input_label = QLabel("Replacement Rule:")
        input_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(input_label)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("from text -> to text")
        self.input_field.setFont(QFont("Courier", 10))
        if self.prefill:
            self.input_field.setText(self.prefill)
        self.input_field.returnPressed.connect(self.save_rule)
        main_layout.addWidget(self.input_field)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet(
            "padding: 8px 20px; background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.save_btn.clicked.connect(self.save_rule)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("padding: 8px 20px;")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def save_rule(self):
        """Save base rule and selected full-phrase related forms to data file.

        The base rule is always written. When the source phrase contains a
        Choices word, or has one unambiguous changed token, related plural,
        past-tense, and gerund rules are offered in a second dialog.
        """
        rule_text = self.input_field.text().strip()

        if not rule_text:
            QMessageBox.warning(self, "Error", "Please enter a replacement rule.")
            return

        # Validate format: "from -> to"
        if " -> " not in rule_text:
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Rule must be in format: from text -> to text\n\n"
                "Example: to lead -> to leed",
            )
            return

        # Parse the rule
        parts = rule_text.split(" -> ")
        if len(parts) != 2:
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Rule must contain exactly one ' -> ' separator.\n\n"
                "Example: to lead -> to leed",
            )
            return

        from_text = parts[0].strip()
        to_text = parts[1].strip()

        if not from_text or not to_text:
            QMessageBox.warning(
                self, "Error", "Both 'from' and 'to' text must be non-empty."
            )
            return

        suggestions = build_replacement_suggestions(from_text, to_text)
        selected_suggestions: List[ReplacementSuggestion] = []
        if suggestions:
            suggestion_dialog = SuffixSuggestionsDialog(suggestions, parent=self)
            if suggestion_dialog.exec_() == QDialog.Accepted:
                selected_suggestions = suggestion_dialog.selected_suggestions()

        try:
            with open(self.data_file_path, "a", encoding="utf-8") as handle:
                handle.write(f"literal:{from_text} -> {to_text}\n")
                for suggestion in selected_suggestions:
                    handle.write(
                        f"literal:{suggestion.from_text} -> {suggestion.to_text}\n"
                    )
            log_message(f"Added replacement rule: '{from_text}' -> '{to_text}'")
            for suggestion in selected_suggestions:
                log_message(
                    f"Added related replacement rule: '{suggestion.from_text}' -> '{suggestion.to_text}'"
                )
            self.accept()
        except Exception as e:
            log_message(f"Failed to save replacement rule: {e}", level="ERROR")
            QMessageBox.critical(self, "Error", f"Could not save rule:\n{e}")
