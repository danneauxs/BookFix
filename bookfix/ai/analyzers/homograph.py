"""Homograph pronunciation disambiguation analyzer."""

from typing import List, Tuple, Optional, Dict
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
        options: List[Tuple[str, str]],
        context_before: str,
        context_after: str,
        context_keywords: Optional[Dict[str, List[str]]] = None,
        batch_mode: bool = False,
        batch_items: List[Dict] = None,
    ) -> AIResponse:
        """
        Analyze homograph with structured linguistic clues (POS tags, keywords, history).

        Args:
            word: The homograph word
            options: List of (spelling, description) tuples
            context_before: Text before the word
            context_after: Text after the word
            context_keywords: Dict mapping spelling to keywords that indicate that pronunciation
            batch_mode: If True, process multiple items in one call
            batch_items: List of dicts for batch (each {'word', 'options', 'before', 'after', 'id'})

        Returns:
            AIResponse with chosen pronunciation and confidence
        """
        from .pos_tagger import get_pos_tagger

        pos_tagger = get_pos_tagger()
        pos_tag = pos_tagger.tag_with_context(context_before, word, context_after)
        pos_explanation = pos_tagger.explain_tag(pos_tag) if pos_tag else "unknown"

        best_guess = None  # choices learning retired

        # Phonetics dict for multi-choice (expandable)
        phonetics = {
            "reed": "/ri:d/",
            "red": "/rɛd/",
            "leed": "/li:d/",
            "led": "/lɛd/",
            "bass_beɪs": "/beɪs/",
            "bass_bæs": "/bæs/",
            # Add more from config options
        }

        # Prepare option spellings and descriptions
        option_spellings = [option[0] for option in options]
        option_descriptions = [option[1] for option in options]

        # Create contextualized options
        contextualized_options = []
        for spelling, description in options:
            contextualized_options.append((spelling, description))

        # Build clues text
        clues_text = ""
        if context_keywords:
            for spelling, keywords in context_keywords.items():
                if keywords:
                    clues_text += f"  {spelling}: {', '.join(keywords)}\n"

        if batch_mode and batch_items:
            # Batch prompt for multiple items
            batch_prompt = "Analyze these homographs. For each, respond with the letter (A/B) only.\n\n"
            numbered_items = []
            for i, item in enumerate(batch_items):
                item_word = item["word"]
                item_options = item["options"]
                item_before = item["before"]
                item_after = item["after"]
                item_pos = pos_tagger.tag_with_context(
                    item_before, item_word, item_after
                )
                item_guess = (
                    learning_storage.get_best_suggestion(
                        item_word, f"{item_before} {item_after}"
                    )[0]
                    if learning_storage.get_best_suggestion(
                        item_word, f"{item_before} {item_after}"
                    )
                    else None
                )

                item_clues = clues_text  # Simplified; per-item if needed

                numbered_prompt = f'{i+1}. Word: {item_word}\nContext: "...{item_before} [{item_word}] {item_after}..."\nPOS: {item_pos}\nGuess: {item_guess}\nOptions:\n'
                for j, (spelling, desc) in enumerate(item_options):
                    phon = phonetics.get(spelling, "/phon/")
                    numbered_prompt += f"  ({chr(65+j)}) {spelling} {phon}: {desc}\n"
                numbered_prompt += f"Respond with letter only (A/B etc.).\n\n"
                batch_prompt += numbered_prompt
                numbered_items.append(item)

            # Get batch response
            batch_response = self.ai_service.batch_analyze(batch_items, batch_prompt)

            if batch_response.success:
                # Parse batch (assume dict {'1': 'A', '2': 'B'})
                parsed = batch_response.choice  # Dict of id: letter
                # Map to choices
                ai_choices = []
                for id_str, letter in parsed.items():
                    idx = int(id_str) - 1
                    item = numbered_items[idx]
                    choice_idx = ord(letter.upper()) - 65
                    chosen = (
                        item["options"][choice_idx][0]
                        if 0 <= choice_idx < len(item["options"])
                        else item["options"][0][0]
                    )
                    ai_choices.append(chosen)

                # Return first as example (or list for batch)
                return AIResponse(True, ai_choices[0], 0.8, "Batch processed")
            else:
                return AIResponse(False, "", 0.0, batch_response.reasoning)

        # Single item prompt (tight multi-choice)
        prompt = f"""Pronunciation expert for TTS. Word: {word}
Context: "...{context_before} [{word}] {context_after}..."
POS: {pos_tag} ({pos_explanation})
Guess: {best_guess}
KEYWORD CLUES:
{clues_text}

Options:
"""
        for i, (spelling, desc) in enumerate(options):
            phon = phonetics.get(spelling, "/phon/")
            prompt += f"({chr(65+i)}) {spelling} {phon}: {desc}\n"

        prompt += f"""
Respond A or B only (letter for choice). Example: A

Few-shot:
Context: "I read the book." POS: VBD (past verb) → B (/rɛd/ past)
Context: "Read this." POS: VB (base verb) → A (/ri:d/ present)
"""

        # Get AI response
        response = self.ai_service.analyze_homograph(
            word,
            contextualized_options,
            context_before,
            context_after,
            context_keywords,
        )

        if response.success:
            # Parse letter response
            if len(options) == 2:
                if "a" in response.choice.lower() or "reed" in response.choice.lower():
                    parsed_choice = options[0][0]
                else:
                    parsed_choice = options[1][0]
            else:
                parsed_choice = response.choice  # Fallback

            return AIResponse(
                True, parsed_choice, response.confidence, response.reasoning
            )
        else:
            return AIResponse(False, "", 0.0, response.reasoning)
