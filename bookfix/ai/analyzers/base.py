"""Base analyzer class with prompt loading."""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..service import BookfixAIService


class BaseAnalyzer:
    """Base class for all analyzers."""

    def __init__(self, service: "BookfixAIService"):
        self.service = service
        self.prompts_dir = service.prompts_dir
        self._prompt_cache = {}

    def _load_prompt(self, prompt_name: str) -> str:
        """Load a prompt template from the prompts directory."""
        if prompt_name in self._prompt_cache:
            return self._prompt_cache[prompt_name]

        prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
            self._prompt_cache[prompt_name] = prompt
            return prompt
        except FileNotFoundError:
            self.service._debug_log(f"Prompt file not found: {prompt_path}")
            return ""
        except Exception as e:
            self.service._debug_log(f"Error loading prompt {prompt_name}: {e}")
            return ""
