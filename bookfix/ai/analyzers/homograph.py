"""Homograph pronunciation disambiguation analyzer."""

from typing import List, Tuple
from .base import BaseAnalyzer
from ..service import AIResponse


class HomographAnalyzer(BaseAnalyzer):
    """Analyzes homographs (words with multiple pronunciations)."""

    def analyze_simple(self, word: str, context: str, options: List[str]) -> AIResponse:
        """Simple homograph analysis."""
        options_text = " / ".join(options)

        prompt_template = self._load_prompt("homograph_simple")
        if not prompt_template:
            return AIResponse(False, "", 0.0, "Prompt not found")

        prompt = prompt_template.format(
            word=word, context=context, options_text=options_text
        )
        response = self.service._make_request(prompt)

        if response.success:
            chosen = response.content.strip()
            if chosen in options:
                confidence = (
                    0.9
                    if any(
                        indicator in context.lower()
                        for indicator in ["will", "to", "the", "yesterday", "ago"]
                    )
                    else 0.7
                )
                return AIResponse(
                    True, chosen, confidence, f"Chose {chosen} based on context"
                )
            else:
                return AIResponse(False, "", 0.0, "AI returned invalid option")

        return response

    def analyze_contextualized(
        self,
        word: str,
        context: str,
        contextualized_options: List[Tuple[str, str]],
        show_reasoning: bool = False,
    ) -> AIResponse:
        """Analyze homograph with POS tag context definitions."""
        if not contextualized_options:
            return AIResponse(
                False, "", 0.0, "No contextualized options were provided."
            )

        # Build options text
        options_text = "\n".join(
            [
                f"  - {spelling}: {definition}"
                for spelling, definition in contextualized_options
            ]
        )
        option_spellings = ", ".join(
            [spelling for spelling, _ in contextualized_options]
        )

        # Load few-shot examples
        few_shot_text = self.service._load_few_shot_examples(word, max_examples=5)

        # Select prompt based on provider and reasoning flag
        if self.service.provider == "gemini-cli":
            prompt_name = "homograph_gemini_cli"
        elif show_reasoning:
            prompt_name = "homograph_with_reasoning"
        else:
            prompt_name = "homograph_simple_contextualized"

        prompt_template = self._load_prompt(prompt_name)
        if not prompt_template:
            return AIResponse(False, "", 0.0, "Prompt not found")

        prompt = prompt_template.format(
            word=word,
            context=context,
            options_text=options_text,
            few_shot_text=few_shot_text,
            option_spellings=option_spellings,
        )

        response = self.service._make_request(prompt)
        # (rest of JSON parsing logic would go here - keeping it simple for now)
        return response
