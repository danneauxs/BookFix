"""Persistent provider definitions used by BookFix AI configuration."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_PROVIDERS: List[Dict[str, Any]] = [
    {
        "key": "ollama",
        "name": "Ollama",
        "family": "ollama",
        "base_url": "http://localhost:11434/api",
        "api_key": "",
        "models": [],
        "default_model": "qwen3:8b",
        "rate_limit": 0.0,
        "requires_api_key": False,
        "builtin": True,
    },
    {
        "key": "lm-studio",
        "name": "LM Studio",
        "family": "openai-compatible",
        "base_url": "http://localhost:1234/v1",
        "api_key": "",
        "models": [],
        "default_model": "",
        "rate_limit": 0.0,
        "requires_api_key": False,
        "builtin": True,
    },
    {
        "key": "llama.cpp",
        "name": "llama.cpp",
        "family": "openai-compatible",
        "base_url": "http://localhost:8080/v1",
        "api_key": "",
        "models": [],
        "default_model": "",
        "rate_limit": 0.0,
        "requires_api_key": False,
        "builtin": True,
    },
    {
        "key": "jan",
        "name": "Jan",
        "family": "openai-compatible",
        "base_url": "http://localhost:1337/v1",
        "api_key": "",
        "models": [],
        "default_model": "",
        "rate_limit": 0.0,
        "requires_api_key": False,
        "builtin": True,
    },
    {
        "key": "mistral",
        "name": "Mistral",
        "family": "openai-compatible",
        "base_url": "https://api.mistral.ai/v1",
        "api_key": "",
        "models": [
            "mistral-small-latest",
            "mistral-medium-latest",
            "mistral-large-latest",
        ],
        "default_model": "mistral-small-latest",
        "rate_limit": 0.016,
        "requires_api_key": True,
        "builtin": True,
    },
    {
        "key": "openai",
        "name": "OpenAI",
        "family": "openai-compatible",
        "base_url": "https://api.openai.com/v1",
        "api_key": "",
        "models": ["gpt-4o-mini", "gpt-4o"],
        "default_model": "gpt-4o-mini",
        "rate_limit": 0.05,
        "requires_api_key": True,
        "builtin": True,
    },
    {
        "key": "groq",
        "name": "Groq",
        "family": "openai-compatible",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "",
        "models": [
            "llama-3.3-70b-versatile",
            "qwen/qwen3-32b",
            "llama-3.1-8b-instant",
        ],
        "default_model": "llama-3.3-70b-versatile",
        "rate_limit": 0.5,
        "requires_api_key": True,
        "builtin": True,
    },
    {
        "key": "xai",
        "name": "xAI (Grok)",
        "family": "openai-compatible",
        "base_url": "https://api.x.ai/v1",
        "api_key": "",
        "models": ["grok-3-mini", "grok-3"],
        "default_model": "grok-3-mini",
        "rate_limit": 0.05,
        "requires_api_key": True,
        "builtin": True,
    },
    {
        "key": "together",
        "name": "Together AI",
        "family": "openai-compatible",
        "base_url": "https://api.together.xyz/v1",
        "api_key": "",
        "models": [],
        "default_model": "",
        "rate_limit": 0.5,
        "requires_api_key": True,
        "builtin": True,
    },
    {
        "key": "gemini",
        "name": "Google Gemini",
        "family": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "api_key": "",
        "models": ["gemini-2.0-flash", "gemini-2.5-flash"],
        "default_model": "gemini-2.0-flash",
        "rate_limit": 1.0,
        "requires_api_key": True,
        "builtin": True,
    },
    {
        "key": "anthropic",
        "name": "Anthropic Claude",
        "family": "anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "api_key": "",
        "models": ["claude-3-5-haiku-latest", "claude-3-7-sonnet-latest"],
        "default_model": "claude-3-5-haiku-latest",
        "rate_limit": 0.25,
        "requires_api_key": True,
        "builtin": True,
    },
    {
        "key": "huggingface",
        "name": "Hugging Face",
        "family": "huggingface",
        "base_url": "https://router.huggingface.co/hf-inference",
        "api_key": "",
        "models": [],
        "default_model": "",
        "rate_limit": 0.25,
        "requires_api_key": True,
        "builtin": True,
    },
    {
        "key": "openai-compatible",
        "name": "OpenAI-compatible endpoint",
        "family": "openai-compatible",
        "base_url": "http://localhost:8000/v1",
        "api_key": "",
        "models": [],
        "default_model": "",
        "rate_limit": 0.0,
        "requires_api_key": False,
        "builtin": True,
    },
    {
        "key": "custom-openai",
        "name": "Custom endpoint",
        "family": "openai-compatible",
        "base_url": "",
        "api_key": "",
        "models": [],
        "default_model": "",
        "rate_limit": 0.0,
        "requires_api_key": False,
        "builtin": True,
    },
]


def default_provider_path() -> Path:
    """Return the application provider registry path."""
    return Path(__file__).resolve().parent.parent / "config" / "providers.json"


def _normalize_provider(provider: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize one provider record and reject records without identity."""
    key = str(provider.get("key", "")).strip()
    name = str(provider.get("name", key)).strip()
    if not key or not name:
        return None
    normalized = dict(provider)
    normalized.update(
        {
            "key": key,
            "name": name,
            "family": str(provider.get("family", "openai-compatible")).strip()
            or "openai-compatible",
            "base_url": str(provider.get("base_url", "")).strip().rstrip("/"),
            "api_key": str(provider.get("api_key", "")),
            "models": [
                str(model).strip()
                for model in provider.get("models", [])
                if str(model).strip()
            ],
            "default_model": str(provider.get("default_model", "")).strip(),
            "rate_limit": float(provider.get("rate_limit", 0.0)),
            "requires_api_key": bool(provider.get("requires_api_key", False)),
            "builtin": bool(provider.get("builtin", False)),
        }
    )
    return normalized


def load_providers(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load provider records from disk, falling back to built-in definitions."""
    config_path = Path(path) if path else default_provider_path()
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        raw_providers = payload.get("providers", [])
    except (OSError, json.JSONDecodeError, AttributeError):
        raw_providers = []

    providers: List[Dict[str, Any]] = []
    seen_keys = set()
    for raw_provider in raw_providers:
        if not isinstance(raw_provider, dict):
            continue
        normalized = _normalize_provider(raw_provider)
        if normalized and normalized["key"] not in seen_keys:
            providers.append(normalized)
            seen_keys.add(normalized["key"])

    if not providers:
        providers = [dict(provider) for provider in DEFAULT_PROVIDERS]
    return providers


def save_providers(providers: List[Dict[str, Any]], path: Optional[Path] = None) -> None:
    """Validate and persist provider records as readable JSON."""
    config_path = Path(path) if path else default_provider_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    normalized: List[Dict[str, Any]] = []
    seen_keys = set()
    for provider in providers:
        item = _normalize_provider(provider)
        if item and item["key"] not in seen_keys:
            normalized.append(item)
            seen_keys.add(item["key"])
    temporary_path = config_path.with_suffix(config_path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as handle:
        json.dump({"providers": normalized}, handle, indent=2)
        handle.write("\n")
    temporary_path.replace(config_path)


def provider_for_key(providers: List[Dict[str, Any]], key: str) -> Optional[Dict[str, Any]]:
    """Return provider record matching key, if present."""
    for provider in providers:
        if provider.get("key") == key:
            return provider
    return None


def slugify_provider_name(name: str) -> str:
    """Create a stable identifier suitable for a custom provider key."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "custom-provider"
