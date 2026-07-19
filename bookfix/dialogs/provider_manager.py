"""Dialogs for managing BookFix AI provider definitions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt

class ProviderEditDialog(QDialog):
    """Edit one provider record, including endpoint and credentials."""

    def __init__(
        self,
        provider: Optional[Dict[str, Any]] = None,
        parent=None,
    ) -> None:
        """Initialize provider fields from an existing record or blank defaults."""
        super().__init__(parent)
        self._provider = dict(provider or {})
        self._is_existing = provider is not None
        self.setWindowTitle("Edit AI Provider" if self._is_existing else "Add AI Provider")
        self.setMinimumWidth(520)
        self._build_form()
        self._load_provider()

    def _build_form(self) -> None:
        """Create provider identity, endpoint, authentication, and model fields."""
        layout = QFormLayout()

        self.key_edit = QLineEdit()
        self.key_edit.setToolTip("Stable identifier used internally by BookFix.")
        layout.addRow("Identifier:", self.key_edit)

        self.name_edit = QLineEdit()
        layout.addRow("Display name:", self.name_edit)

        self.base_url_edit = QLineEdit()
        self.base_url_edit.setToolTip(
            "API root before /chat/completions, /models, or provider-specific paths."
        )
        layout.addRow("Base URL:", self.base_url_edit)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setToolTip("Optional API key. Stored in providers.json.")
        layout.addRow("API key:", self.api_key_edit)

        self.family_combo = QComboBox()
        self.family_combo.addItem("OpenAI-compatible", "openai-compatible")
        self.family_combo.addItem("Ollama", "ollama")
        self.family_combo.addItem("Google Gemini", "gemini")
        self.family_combo.addItem("Anthropic", "anthropic")
        self.family_combo.addItem("Hugging Face", "huggingface")
        layout.addRow("API format:", self.family_combo)

        self.models_edit = QPlainTextEdit()
        self.models_edit.setPlaceholderText("Optional fallback model names, one per line")
        self.models_edit.setMaximumHeight(100)
        layout.addRow("Known models:", self.models_edit)

        self.default_model_edit = QLineEdit()
        layout.addRow("Default model:", self.default_model_edit)

        self.rate_limit_combo = QComboBox()
        self.rate_limit_combo.addItem("No limit (local)", 0.0)
        self.rate_limit_combo.addItem("Free tier (1 request/min)", 1.0 / 60.0)
        self.rate_limit_combo.addItem("Free tier (30 requests/min)", 0.5)
        self.rate_limit_combo.addItem("Paid tier (60 requests/min)", 1.0)
        self.rate_limit_combo.addItem("Paid tier (120 requests/min)", 2.0)
        self.rate_limit_combo.addItem("Custom", None)
        self.rate_limit_combo.currentIndexChanged.connect(self._update_custom_rate_visibility)
        layout.addRow("Rate limit:", self.rate_limit_combo)

        self.custom_rate_spin = QDoubleSpinBox()
        self.custom_rate_spin.setRange(0.0, 100.0)
        self.custom_rate_spin.setDecimals(4)
        self.custom_rate_spin.setSingleStep(0.25)
        self.custom_rate_spin.setSuffix(" req/s")
        layout.addRow("Custom rate:", self.custom_rate_spin)

        self.requires_key_combo = QComboBox()
        self.requires_key_combo.addItem("No", False)
        self.requires_key_combo.addItem("Yes", True)
        layout.addRow("API key required:", self.requires_key_combo)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self._validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        wrapper = QVBoxLayout()
        wrapper.addLayout(layout)
        wrapper.addWidget(self.button_box)
        self.setLayout(wrapper)

    def _load_provider(self) -> None:
        """Populate form widgets from provider record values."""
        provider = self._provider
        self.key_edit.setText(str(provider.get("key", "")))
        self.name_edit.setText(str(provider.get("name", "")))
        self.base_url_edit.setText(str(provider.get("base_url", "")))
        self.api_key_edit.setText(str(provider.get("api_key", "")))
        family = str(provider.get("family", "openai-compatible"))
        family_index = self.family_combo.findData(family)
        # Unknown custom families use the safest supported request format.
        self.family_combo.setCurrentIndex(family_index if family_index >= 0 else 0)
        self.models_edit.setPlainText("\n".join(provider.get("models", [])))
        self.default_model_edit.setText(str(provider.get("default_model", "")))
        self.requires_key_combo.setCurrentIndex(
            1 if provider.get("requires_api_key", False) else 0
        )
        self._set_rate_limit(float(provider.get("rate_limit", 0.0)))
        if self._is_existing and provider.get("builtin"):
            self.key_edit.setReadOnly(True)

    def _set_rate_limit(self, rate_limit: float) -> None:
        """Select a preset when possible, otherwise load custom rate value."""
        preset_index = -1
        for index in range(self.rate_limit_combo.count() - 1):
            value = float(self.rate_limit_combo.itemData(index))
            if abs(value - rate_limit) < 0.00001:
                preset_index = index
                break
        # Values outside presets remain editable through the custom control.
        self.rate_limit_combo.setCurrentIndex(
            preset_index if preset_index >= 0 else self.rate_limit_combo.count() - 1
        )
        self.custom_rate_spin.setValue(rate_limit)

    def _update_custom_rate_visibility(self, index: int) -> None:
        """Show custom rate control only when custom preset is selected."""
        self.custom_rate_spin.setEnabled(self.rate_limit_combo.itemData(index) is None)

    def _selected_rate_limit(self) -> float:
        """Return selected request-per-second rate limit."""
        value = self.rate_limit_combo.currentData()
        return self.custom_rate_spin.value() if value is None else float(value)

    def _validate_and_accept(self) -> None:
        """Reject incomplete provider records before closing dialog."""
        key = self.key_edit.text().strip()
        name = self.name_edit.text().strip()
        base_url = self.base_url_edit.text().strip()
        # Provider identity and endpoint are required for every saved record.
        if not key or not name or not base_url:
            QMessageBox.warning(
                self,
                "Incomplete Provider",
                "Identifier, display name, and base URL are required.",
            )
            return
        self.accept()

    def provider_record(self) -> Dict[str, Any]:
        """Return normalized provider data represented by form fields."""
        models = [
            line.strip()
            for line in self.models_edit.toPlainText().splitlines()
            if line.strip()
        ]
        return {
            "key": self.key_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "family": self.family_combo.currentData(),
            "base_url": self.base_url_edit.text().strip().rstrip("/"),
            "api_key": self.api_key_edit.text(),
            "models": models,
            "default_model": self.default_model_edit.text().strip(),
            "rate_limit": self._selected_rate_limit(),
            "requires_api_key": bool(self.requires_key_combo.currentData()),
            "builtin": bool(self._provider.get("builtin", False)),
        }


class ProviderManagerDialog(QDialog):
    """Manage built-in and user-defined providers persisted in providers.json."""

    def __init__(self, providers: List[Dict[str, Any]], parent=None) -> None:
        """Initialize manager with a private editable provider list."""
        super().__init__(parent)
        self.setWindowTitle("Manage AI Providers")
        self.setMinimumSize(700, 420)
        self.providers = [dict(provider) for provider in providers]
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        """Create provider list and management actions."""
        self.provider_list = QListWidget()
        self.provider_list.currentRowChanged.connect(self._update_buttons)

        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.add_button.clicked.connect(self._add_provider)
        self.edit_button.clicked.connect(self._edit_provider)
        self.delete_button.clicked.connect(self._delete_provider)

        actions = QHBoxLayout()
        actions.addWidget(self.add_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self._save_and_accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel("Built-in providers can be edited. Add custom endpoints without changing source files.")
        )
        layout.addWidget(self.provider_list)
        layout.addLayout(actions)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def _refresh_list(self, selected_key: str = "") -> None:
        """Refresh list labels and preserve selected provider when possible."""
        self.provider_list.blockSignals(True)
        self.provider_list.clear()
        selected_row = 0
        for row, provider in enumerate(self.providers):
            key_state = "key set" if provider.get("api_key") else "no key"
            item = QListWidgetItem(f"{provider['name']}  [{provider['key']}; {key_state}]")
            item.setData(Qt.UserRole, provider["key"])
            self.provider_list.addItem(item)
            if provider["key"] == selected_key:
                selected_row = row
        self.provider_list.blockSignals(False)
        if self.providers:
            self.provider_list.setCurrentRow(selected_row)
        self._update_buttons(self.provider_list.currentRow())

    def _update_buttons(self, row: int) -> None:
        """Enable actions according to current selection and provider ownership."""
        valid_row = 0 <= row < len(self.providers)
        self.edit_button.setEnabled(valid_row)
        # Built-in records remain available and editable but cannot be deleted.
        self.delete_button.setEnabled(valid_row and not self.providers[row].get("builtin", False))

    def _add_provider(self) -> None:
        """Open blank provider form and append a validated custom record."""
        dialog = ProviderEditDialog(parent=self)
        if dialog.exec_() != QDialog.Accepted:
            return
        provider = dialog.provider_record()
        # Suggest a unique slug when user left the generated identifier unchanged.
        if any(item["key"] == provider["key"] for item in self.providers):
            QMessageBox.warning(self, "Duplicate Identifier", "Provider identifier already exists.")
            return
        self.providers.append(provider)
        self._refresh_list(provider["key"])

    def _edit_provider(self) -> None:
        """Edit currently selected provider and preserve its row identity."""
        row = self.provider_list.currentRow()
        if not 0 <= row < len(self.providers):
            return
        original_key = self.providers[row]["key"]
        dialog = ProviderEditDialog(self.providers[row], self)
        if dialog.exec_() != QDialog.Accepted:
            return
        provider = dialog.provider_record()
        # Prevent changing one provider into another existing provider.
        if any(
            index != row and item["key"] == provider["key"]
            for index, item in enumerate(self.providers)
        ):
            QMessageBox.warning(self, "Duplicate Identifier", "Provider identifier already exists.")
            return
        self.providers[row] = provider
        self._refresh_list(provider["key"] or original_key)

    def _delete_provider(self) -> None:
        """Delete selected custom provider after explicit confirmation."""
        row = self.provider_list.currentRow()
        if not 0 <= row < len(self.providers) or self.providers[row].get("builtin", False):
            return
        provider = self.providers[row]
        # Deletion is destructive to stored endpoint and credential metadata.
        answer = QMessageBox.question(
            self,
            "Delete Provider",
            f"Delete '{provider['name']}' from the provider list?",
        )
        if answer == QMessageBox.Yes:
            del self.providers[row]
            self._refresh_list()

    def _save_and_accept(self) -> None:
        """Return edited providers to caller after duplicate validation."""
        keys = [provider.get("key") for provider in self.providers]
        # Duplicate keys make selected-provider lookup ambiguous.
        if len(keys) != len(set(keys)):
            QMessageBox.warning(self, "Duplicate Identifier", "Provider identifiers must be unique.")
            return
        self.accept()

    def provider_records(self) -> List[Dict[str, Any]]:
        """Return provider records after dialog acceptance."""
        return [dict(provider) for provider in self.providers]
