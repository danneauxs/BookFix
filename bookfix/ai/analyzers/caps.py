"""All-caps sequence analyzer."""

import json
import os
import re
from typing import List, Dict, Optional
from .base import BaseAnalyzer
from ..service import AIResponse


class CapsAnalyzer(BaseAnalyzer):
    """Analyzes all-caps sequences for TTS."""

    def analyze_batch(
        self, caps_context_file: str, cap_ignore_list: List[str]
    ) -> Optional[Dict[str, str]]:
        """
        Analyze all caps words in a batch using a single API call.

        Args:
            caps_context_file: Path to caps_context.txt file with all contexts
            cap_ignore_list: List of caps to ignore

        Returns:
            Dict mapping word -> decision ('keep' or 'lowercase'), or None if batch fails
        """
        if not os.path.exists(caps_context_file):
            self.service._debug_log(f"Batch file not found: {caps_context_file}")
            return None

        try:
            # Read context file with structured format:
            # WORD1
            # Context: ...before word after...
            #
            # WORD2
            # Context: ...before word after...
            with open(caps_context_file, "r", encoding="utf-8") as f:
                context_content = f.read()

            # Parse structured format: extract words and their contexts
            words_with_contexts = {}  # word -> context line
            lines = context_content.strip().split("\n")
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line and re.match(r"^[A-Z]{2,}(?:\'[A-Z]+)?$", line):
                    # Found a caps word
                    word = line
                    # Next line should be context
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith(
                        "Context:"
                    ):
                        context_line = lines[i + 1].strip()
                        words_with_contexts[word] = context_line
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1

            if not words_with_contexts:
                self.service._debug_log("No structured caps words found in batch file")
                return None

            # Extract unique words
            caps_words = set(words_with_contexts.keys())
            self.service._debug_log(
                f"Batch analyzing {len(caps_words)} caps words from structured format"
            )

            # Sort for consistency
            sorted_words = sorted(caps_words)

            # Build context snippets from all parsed contexts
            context_snippets = "\n".join(
                [words_with_contexts[word] for word in sorted_words]
            )

            # Format words list for prompt
            words_list = "\n".join([f"- {word}" for word in sorted_words])

            # Load batch prompt template
            prompt_template = self._load_prompt("caps_sequence_batch")
            if not prompt_template:
                self.service._debug_log("Batch prompt template not found")
                return None

            # Build prompt with structured context snippets
            prompt = prompt_template.format(
                context_snippets=context_snippets,  # Pre-formatted context from structured data
                words_list=words_list,
            )

            self.service._debug_log(
                f"\n=== BATCH CAPS ANALYZER: Analyzing {len(sorted_words)} words ==="
            )

            # Make API request
            response = self.service._make_request(prompt)
            self.service._debug_log(
                f"Batch AI Raw Response: success={response.success}, content_len={len(response.content)}"
            )

            if not response.success:
                self.service._debug_log(
                    f"Batch request failed: {response.error_message}"
                )
                return None

            # Parse JSON array response
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

                # Parse JSON array
                results = json.loads(content)

                if not isinstance(results, list):
                    self.service._debug_log(
                        f"Batch response is not a list: {type(results)}"
                    )
                    return None

                # Convert to dict: word -> decision
                batch_results = {}
                for item in results:
                    if isinstance(item, dict) and "word" in item and "decision" in item:
                        word = item["word"].upper()
                        decision = item["decision"].lower()
                        # Convert decision to matching format (spell -> keep, pronounce -> lowercase)
                        if decision == "spell":
                            batch_results[word] = "keep"
                        elif decision == "pronounce":
                            batch_results[word] = "lowercase"
                        else:
                            batch_results[word] = (
                                "lowercase"  # Default to pronounce/lowercase
                            )

                self.service._debug_log(
                    f"Batch analysis complete: {len(batch_results)} words processed"
                )
                return batch_results if batch_results else None

            except json.JSONDecodeError as e:
                self.service._debug_log(f"Failed to parse batch JSON response: {e}")
                self.service._debug_log(
                    f"Response content (first 500 chars): {response.content[:500]}"
                )
                return None

        except Exception as e:
            self.service._debug_log(f"Batch analysis error: {e}")
            import traceback

            self.service._debug_log(f"Traceback: {traceback.format_exc()}")
            return None

    def analyze_sequence(
        self, caps_text: str, context: str, cap_ignore_list: List[str]
    ) -> AIResponse:
        """Analyze caps sequence and determine handling."""
        ignore_examples = (
            "\n".join([f"- {item}" for item in cap_ignore_list[:10]])
            if cap_ignore_list
            else "- (none yet)"
        )

        prompt_template = self._load_prompt("caps_sequence")
        if not prompt_template:
            return AIResponse(False, "keep", 0.0, "Prompt not found")

        prompt = prompt_template.format(
            caps_text=caps_text, context=context, ignore_examples=ignore_examples
        )

        self.service._debug_log(f"\n=== CAPS ANALYZER: Analyzing '{caps_text}' ===")
        self.service._debug_log(f"Context: {context[:100]}...")

        response = self.service._make_request(prompt)
        self.service._debug_log(
            f"AI Raw Response: success={response.success}, content='{response.content}'"
        )
        if response.success:
            try:
                content = response.content.strip().lower()

                # Remove code fences if present
                if content.startswith("```"):
                    lines = content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    content = "\n".join(lines).strip().lower()

                # Check for "spell" or "pronounce" in the response (not just exact match)
                # Model may include extra text, so search for the keywords
                import re

                # Look for "spell" or "pronounce" as a word (not substring)
                spell_match = re.search(r"\bspell\b", content)
                pronounce_match = re.search(r"\bpronounce\b", content)

                # Determine which was chosen
                if spell_match and not pronounce_match:
                    suggestion = "keep"
                    reasoning = f"TTS analysis: spell"
                    confidence = 0.85
                    self.service._debug_log(f"Extracted decision: spell → keep")
                    return AIResponse(True, suggestion, confidence, reasoning)
                elif pronounce_match and not spell_match:
                    suggestion = "lowercase"
                    reasoning = f"TTS analysis: pronounce"
                    confidence = 0.85
                    self.service._debug_log(
                        f"Extracted decision: pronounce → lowercase"
                    )
                    return AIResponse(True, suggestion, confidence, reasoning)
                elif pronounce_match:
                    # If both appear, use "pronounce" (more specific instruction)
                    suggestion = "lowercase"
                    reasoning = f"TTS analysis: pronounce (found in response)"
                    confidence = 0.75
                    self.service._debug_log(f"Both found, using pronounce → lowercase")
                    return AIResponse(True, suggestion, confidence, reasoning)
                elif spell_match:
                    # Fallback to spell if pronounce not found
                    suggestion = "keep"
                    reasoning = f"TTS analysis: spell (found in response)"
                    confidence = 0.75
                    self.service._debug_log(f"Only spell found → keep")
                    return AIResponse(True, suggestion, confidence, reasoning)

                # Fallback to old JSON format for compatibility
                if "{" in content:
                    try:
                        result = json.loads(content)
                        suggestion = result.get("suggestion", "keep")
                        reasoning = result.get("reasoning", "Analysis completed")
                        confidence = (
                            0.85
                            if suggestion in ("keep", "lowercase", "title")
                            else 0.6
                        )
                        return AIResponse(True, suggestion, confidence, reasoning)
                    except json.JSONDecodeError:
                        pass

                # If no keyword found, default to lowercase (prefer "pronounce" as safer default)
                self.service._debug_log(
                    f"No keyword found, defaulting to lowercase (pronounce)"
                )
                return AIResponse(
                    False,
                    "lowercase",
                    0.5,
                    f"Could not parse response, defaulting to pronounce",
                )

            except Exception as e:
                return AIResponse(False, "keep", 0.0, f"Error parsing response: {e}")

        return AIResponse(False, "keep", 0.0, "AI analysis failed, keeping original")
