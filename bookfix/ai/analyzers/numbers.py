"""Number formatting analyzer for TTS."""

import json
from typing import Dict
from .base import BaseAnalyzer
from ..service import AIResponse


class NumberAnalyzer(BaseAnalyzer):
    """Analyzes numbers in context and determines TTS formatting."""

    def analyze_formatting(
        self, number: str, context: str, rules: Dict[str, str]
    ) -> AIResponse:
        """
        Determine how to format a number based on context and rules.

        Args:
            number: The number to format (e.g., "1984", "0800", "1500")
            context: Surrounding text
            rules: Dictionary of formatting rules

        Returns:
            AIResponse with formatted number and context type
        """
        prompt_template = self._load_prompt("number_formatting")
        if not prompt_template:
            return AIResponse(False, number, 0.0, "Prompt not found")

        prompt = prompt_template.format(number=number, context=context)
        response = self.service._make_request(prompt)

        if response.success:
            try:
                content = response.content.strip()

                # Remove markdown code fences if present
                if content.startswith("```"):
                    lines = content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    content = "\n".join(lines).strip()

                result = json.loads(content)
                formatted = result.get("formatted", number)
                number_type = result.get("type", "general")
                reasoning = result.get("reasoning", "Formatted based on context")

                confidence = 0.85 if number_type != "general" else 0.6
                return AIResponse(
                    True, formatted, confidence, f"Type: {number_type}. {reasoning}"
                )

            except json.JSONDecodeError:
                formatted = response.content.strip()
                confidence = 0.7
                return AIResponse(
                    True,
                    formatted,
                    confidence,
                    "Formatted based on context (non-JSON response)",
                )

        return AIResponse(False, number, 0.0, "AI formatting failed, keeping original")
