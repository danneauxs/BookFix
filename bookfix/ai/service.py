"""
Core AI Service for Bookfix.

Provides a unified interface for multiple AI providers (OpenAI, Gemini, Claude, etc.)
with fallback handling and context-aware text analysis.
"""

import json
import requests
import time
import os
import re

# from typing import Dict, Any, Optional, List, Tuple
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass

from ..logging import log_message


@dataclass
class AIResponse:
    """Response from AI analysis."""

    success: bool
    content: str
    confidence: float = 0.0
    reasoning: str = ""
    error_message: str = ""


class BookfixAIService:
    """
    Central AI service supporting multiple providers.

    Supports:
    - OpenAI (GPT-3.5, GPT-4)
    - Google Gemini API (paid tier)
    - Google Gemini CLI (free tier, CLI-based)
    - Anthropic Claude
    - Groq (fast, free tier)
    - Ollama (local models)
    - Together.ai (various open source models)
    """

    def __init__(self, model_path: str = None, **kwargs):
        """
        Initialize the AI service supporting multiple providers.

        Args:
            model_path: Absolute path to the GGUF model file (for llama-cpp only).
            **kwargs: Additional configuration including:
                - provider: AI provider ('llama-cpp', 'huggingface', 'openai', 'gemini', etc.)
                - model: Model name/ID
                - api_key: API key for remote providers
                - confidence_threshold: AI confidence threshold
                - max_retries: Number of retries for failed requests
                - rate_limit: Rate limit in requests per second
        """
        import os
        import requests

        self.model_path = model_path
        self.llm = None
        self.provider = kwargs.get("provider", "llama-cpp")
        self.model = kwargs.get("model", "")
        self.api_key = kwargs.get("api_key", "")

        # Session for HTTP-based providers
        self.session = requests.Session()
        # Only set Bearer token for OpenAI-compatible APIs
        # Gemini uses query parameter authentication (?key=...), not Bearer tokens
        if self.api_key and self.provider in ("openai", "groq", "together", "mistral"):
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

        # Extract common AI config parameters from kwargs
        self.confidence_threshold = kwargs.get("confidence_threshold", 0.8)
        self.max_retries = kwargs.get("max_retries", 3)
        self.rate_limit = kwargs.get("rate_limit", 0.0)

        # Provider-specific base URLs
        self.base_url = kwargs.get("base_url", "")
        if not self.base_url:
            if self.provider == "huggingface":
                # Using new Inference Providers API (migrated from api-inference.huggingface.co)
                self.base_url = "https://router.huggingface.co/hf-inference"
            elif self.provider == "openai":
                self.base_url = "https://api.openai.com/v1"
            elif self.provider == "mistral":
                self.base_url = "https://api.mistral.ai/v1"
            elif self.provider == "groq":
                self.base_url = "https://api.groq.com/openai/v1"
            elif self.provider == "together":
                self.base_url = "https://api.together.xyz/v1"
            elif self.provider == "gemini":
                self.base_url = "https://generativelanguage.googleapis.com/v1beta"
            elif self.provider == "anthropic":
                self.base_url = "https://api.anthropic.com/v1"
            elif self.provider == "ollama":
                self.base_url = "http://localhost:11434/api"

        app_root_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        self.prompts_dir = os.path.join(app_root_dir, "prompts")
        self.prompt_cache = {}
        # Few-shot examples from choices_learning.json removed — AI now receives
        # curated examples from choices.json via the batch prompt instead.

        # Only load llama-cpp if that's the provider being used
        if self.provider == "llama-cpp":
            if not model_path:
                log_message(
                    "WARNING: model_path required for llama-cpp provider - will use API fallback",
                    level="WARNING",
                )
            else:
                try:
                    from llama_cpp import Llama

                    # Extract model name from path (e.g., "/path/to/mistral-7b.gguf" -> "mistral-7b")
                    self.model = os.path.splitext(os.path.basename(model_path))[0]

                    log_message(
                        f"Attempting to load model from: {model_path}", level="DEBUG"
                    )
                    import traceback

                    # Use GPU if available (n_gpu_layers=50 offloads ~all layers to GPU for 8GB+ VRAM)
                    # For RTX 4060 Ti with 8GB VRAM, Mistral 7B Q4_K_M (~4.6GB) fits comfortably
                    n_gpu_layers = kwargs.get("n_gpu_layers", 50)
                    log_message(
                        f"Loading model with n_gpu_layers={n_gpu_layers} (GPU acceleration enabled)",
                        level="DEBUG",
                    )
                    self.llm = Llama(
                        model_path=model_path,
                        n_gpu_layers=n_gpu_layers,
                        n_ctx=4096,  # Context size
                        verbose=False,
                    )
                    log_message("Model loaded successfully.", level="DEBUG")
                except Exception as e:
                    import traceback

                    log_message(
                        f"FATAL: Model failed to load from {model_path}. Error: {e}",
                        level="ERROR",
                    )
                    log_message(
                        f"Full traceback:\n{traceback.format_exc()}", level="ERROR"
                    )
        else:
            # Non-llama-cpp providers are initialized on-demand during requests
            log_message(
                f"Initializing {self.provider} provider (model: {self.model})",
                level="DEBUG",
            )

        # Initialize analyzers (ALWAYS, regardless of provider or model loading status)
        from .analyzers import (
            HomographAnalyzer,
            CapsAnalyzer,
            RomanAnalyzer,
            NumberAnalyzer,
            PageAnalyzer,
            FragmentAnalyzer,
        )

        self.homograph = HomographAnalyzer(self)
        self.caps = CapsAnalyzer(self)
        self.roman = RomanAnalyzer(self)
        self.numbers = NumberAnalyzer(self)
        self.pages = PageAnalyzer(self)
        self.fragments = FragmentAnalyzer(self)

        log_message(f"=== AI Service Initialized ({self.provider}) ===", level="INFO")

    def _debug_log(self, message: str):
        """Debug logging method for analyzers."""
        log_message(message, level="DEBUG")

    def _load_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt template from the prompts directory.

        Args:
            prompt_name: Name of the prompt file (without .txt extension)

        Returns:
            Prompt template string
        """
        if prompt_name in self.prompt_cache:
            return self.prompt_cache[prompt_name]

        prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
            self.prompt_cache[prompt_name] = prompt
            return prompt
        except FileNotFoundError:
            log_message(f"Prompt file not found: {prompt_path}", level="WARNING")
            return ""
        except Exception as e:
            log_message(f"Error loading prompt {prompt_name}: {e}", level="ERROR")
            return ""

    def _enforce_rate_limit(self):
        """Enforce rate limiting between API requests."""
        if self.rate_limit <= 0:
            return  # No rate limiting

        # Sleep to enforce rate limit (requests per second)
        wait_time = 1.0 / self.rate_limit
        time.sleep(wait_time)

    def _make_request(self, prompt: str) -> AIResponse:
        """Make a request to the loaded Llama model."""
        if not self.llm:
            log_message("LLM not loaded, cannot make request.", level="ERROR")
            return AIResponse(False, "", 0.0, "", "LLM not loaded.")

        try:
            output = self.llm(
                prompt,
                max_tokens=500,
                temperature=0.0,  # Deterministic output
                stop=["\n"],  # Stop generation at newline for classification tasks
            )
            content = output["choices"][0]["text"].strip()
            # Confidence is high by default as we rely on prompt structure
            return AIResponse(True, content, confidence=0.9)
        except Exception as e:
            log_message(f"Error during LLM inference: {e}", level="ERROR")
            return AIResponse(False, "", 0.0, "", str(e))

        response = self._make_request(prompt)
        if response.success:
            # Extract the chosen option and calculate confidence
            chosen = response.content.strip()
            if chosen in options:
                # High confidence for clear grammatical contexts
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

    def analyze_contextualized_homograph(
        self,
        word: str,
        context: str,
        contextualized_options: List[Tuple[str, str]],
        show_reasoning: bool = False,
        best_guess: Optional[str] = None,
        detected_pos_tag: Optional[str] = None,
        context_keywords: Optional[Dict[str, List[str]]] = None,
    ) -> AIResponse:
        """
        Analyze homograph with structured linguistic clues (POS tags, keywords, history).
        AI is the final arbiter - uses all clues to determine correct pronunciation.

        Args:
            word: The homograph to analyze
            context: Surrounding text context
            contextualized_options: List of (spelling, _) tuples (descriptions ignored)
            show_reasoning: If True, request detailed reasoning from AI (slower, more tokens)
            best_guess: A preliminary guess from local rules to be verified by the AI
            detected_pos_tag: POS tag from spaCy (VB, NN, VBD, etc.) - a clue, not a rule
            context_keywords: Dict mapping spelling to keywords that indicate that pronunciation
        """
        if not contextualized_options:
            return AIResponse(
                False, "", 0.0, "No contextualized options were provided."
            )

        log_message(f"\n=== ANALYZING HOMOGRAPH ===", level="DEBUG")
        log_message(f"Word: '{word}'", level="DEBUG")
        log_message(f"Context: '{context}'", level="DEBUG")
        log_message(f"Options: {contextualized_options}", level="DEBUG")
        if best_guess:
            log_message(f"Best guess from local rules: '{best_guess}'", level="DEBUG")

        options_text = "\n".join(
            [
                f"- {spelling} ({meaning})"
                for spelling, meaning in contextualized_options
            ]
        )
        option_spellings = [spelling for spelling, _ in contextualized_options]

        # Add verification step to prompt if best_guess is available
        verification_text = ""
        if best_guess and best_guess in option_spellings:
            verification_text = f"""**Verification:**
A local grammar analysis suggests the choice should be '{best_guess}'.
First, verify if this choice is correct. If it is, use it. If not, choose the better option.
"""

        # Determine which prompt format to use
        if show_reasoning:
            # Verbose prompt with reasoning (for debugging)
            prompt = f"""You are analyzing HOMOGRAPHS (words with multiple pronunciations) for a text-to-speech system.

**CRITICAL: This is a CUSTOM PHONETIC DICTIONARY**
- The spellings below are AUTHORITATIVE and SUPERSEDE normal English spelling
- These are the ONLY valid options - ignore what you think is "correct" spelling
- Your ONLY job: match the pronunciation to how the word is used grammatically

**Sentence context:**
"{context}"

**Custom phonetic dictionary entries (AUTHORITATIVE - use EXACTLY as defined):**
{options_text}
**Your task:**
1. Identify if the word is a NOUN, VERB, or ADJECTIVE using standard grammar rules
2. Match that grammar role to the correct pronunciation definition above
3. IGNORE normal English spelling - use ONLY the definitions provided

**Example:** "last-minute supplies" → "minute" modifies "supplies" = adjective? NO, it's a compound using "minute" as NOUN (unit of time) = "minit"

**Task:** Return a JSON object with "reasoning" and "choice" keys.
- "reasoning": State which grammar role and why. DO NOT quote the context text.
- "choice": Must be EXACTLY one of these: {', '.join(option_spellings)}

Example with options "refuze (verb, to decline)" vs "refuse (noun, trash or garbage)":
Context: "I must [refuse] to answer that question."
{{
  "reasoning": "The word follows 'must' making it an infinitive verb meaning to decline. This matches the refuze definition.",
  "choice": "refuze"
}}
"""
        else:
            # ATTEMPT-FIRST approach: Make initial guess, then evaluate clues
            # Step 1: AI makes initial guess based on context alone
            initial_guess_prompt = f"""You are analyzing a word for text-to-speech pronunciation.

Sentence context: "{context}"
Word to pronounce: "{word}"
Possible pronunciations (pick ONE):
- {', '.join(option_spellings)}

IMPORTANT: Your answer MUST be exactly ONE of the options listed above. No other answers are valid.

Analyze the sentence context to determine which pronunciation fits best. You may reason through this as much as needed, but your final answer must be one of the exact options provided.

Output your FINAL_INITIAL_GUESS as:
{{"FINAL_INITIAL_GUESS": "your_choice"}}

Remember: "your_choice" must be exactly one of the pronunciation options listed above."""

            log_message(
                f"\n--- ATTEMPT 1: Initial Guess (context only) ---", level="DEBUG"
            )
            log_message(f"Prompt:\n{initial_guess_prompt}", level="DEBUG")

            initial_response = self._make_request(initial_guess_prompt)
            initial_guess = None

            if initial_response.success:
                try:
                    clean_response = initial_response.content.strip()
                    log_message(
                        f"Raw initial response (first 500 chars): {clean_response[:500]}",
                        level="DEBUG",
                    )

                    if clean_response.startswith("```"):
                        lines = clean_response.split("\n")
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].strip() == "```":
                            lines = lines[:-1]
                        clean_response = "\n".join(lines).strip()

                    # Extract FINAL_INITIAL_GUESS using regex to get the labeled final answer
                    import re

                    final_match = re.search(
                        r'"FINAL_INITIAL_GUESS"\s*:\s*"([^"]+)"', clean_response
                    )
                    if final_match:
                        initial_guess = final_match.group(1).strip()
                        if "(" in initial_guess:
                            initial_guess = initial_guess.split("(")[0].strip()

                        if initial_guess in option_spellings:
                            log_message(
                                f"✓ Initial guess: '{initial_guess}'", level="DEBUG"
                            )
                        else:
                            log_message(
                                f"⚠ Initial guess invalid: '{initial_guess}'",
                                level="WARNING",
                            )
                            initial_guess = None
                    else:
                        log_message(
                            f"⚠ Failed to find FINAL_INITIAL_GUESS in response",
                            level="WARNING",
                        )
                        initial_guess = None

                except Exception as e:
                    log_message(
                        f"⚠ Failed to parse initial guess: {type(e).__name__}: {str(e)}",
                        level="WARNING",
                    )
                    log_message(
                        f"Raw response was (first 500 chars): {clean_response[:500]}",
                        level="DEBUG",
                    )
                    initial_guess = None

            # Step 2: Evaluate with clues - does AI still agree?
            clues = []

            if detected_pos_tag:
                clues.append(f"GRAMMAR CLUE: Detected as {detected_pos_tag}")

            if context_keywords:
                clues_text = ""
                for spelling, keywords in context_keywords.items():
                    if keywords:
                        clues_text += f"  {spelling}: {', '.join(keywords)}\n"
                if clues_text:
                    clues.append(f"KEYWORD CLUES:\n{clues_text}")

            clues_section = "\n".join(clues) if clues else "(No additional clues)"

            # Build evaluation prompt based on whether we got an initial guess
            if initial_guess:
                evaluation_prompt = f"""Review your pronunciation choice for text-to-speech.

Word to pronounce: "{word}"
Your initial choice: {initial_guess}
Sentence context: "{context}"
Valid pronunciation options: {', '.join(option_spellings)}

Additional clues to consider:
{clues_section}

**CRITICAL INSTRUCTIONS:**
1.  **Keywords are high priority:** If `KEYWORD CLUES` are present for a specific choice, you should strongly favor that choice. These are user-provided hints that override general language patterns.
2.  **Grammar is a strong signal:** If `GRAMMAR CLUE` (a POS tag) is present, it is also a very strong signal.
3.  Use these clues to confirm or correct your initial choice.

Your final answer MUST be one of the valid options listed above.

Output your FINAL_DECISION as:
{{"FINAL_DECISION": "your_choice", "changed": true/false, "reason": "brief explanation"}}

CRITICAL: "your_choice" must be exactly one of: {', '.join(option_spellings)}"""
            else:
                # Fallback if initial guess failed
                evaluation_prompt = f"""Choose the correct pronunciation for text-to-speech.

Word to pronounce: "{word}"
Sentence context: "{context}"
Valid pronunciation options: {', '.join(option_spellings)}

Clues to consider:
{clues_section}

**CRITICAL INSTRUCTIONS:**
1.  **Keywords are high priority:** If `KEYWORD CLUES` are present for a specific choice, you must prioritize that choice. These are user-provided hints that override general language patterns.
2.  **Grammar is a strong signal:** If `GRAMMAR CLUE` (a POS tag) is present, it is also a very strong signal.
3.  Analyze the clues and select the best pronunciation from the valid options only.

Your answer MUST be one of the valid options listed above.

Output your FINAL_DECISION as:
{{"FINAL_DECISION": "your_choice"}}

CRITICAL: "your_choice" must be exactly one of: {', '.join(option_spellings)}"""

            log_message(f"\n--- ATTEMPT 2: Evaluate with Clues ---", level="DEBUG")
            log_message(f"Prompt:\n{evaluation_prompt}", level="DEBUG")

            prompt = evaluation_prompt

        log_message(
            f"Prompt sent to AI (Provider: {self.provider}):\n{prompt}", level="DEBUG"
        )

        # Save prompt to file for debugging (APPEND mode to save all prompts)
        try:
            import os
            from pathlib import Path

            log_dir = Path(__file__).parent.parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            prompt_file = log_dir / "aiprompt.txt"

            # Append mode to keep all prompts
            mode = "a" if prompt_file.exists() else "w"
            with open(prompt_file, mode, encoding="utf-8") as f:
                if mode == "w":
                    # First prompt - add header
                    f.write(f"Provider: {self.provider}\n")
                    f.write(f"Model: {self.model}\n")
                    f.write(f"Temperature: 0.3\n")
                    f.write("=" * 80 + "\n\n")

                # Write this prompt with separator
                f.write(f"\n{'='*80}\n")
                f.write(f"WORD: {word}\n")
                f.write(f"{'='*80}\n")
                f.write(prompt)
                f.write(f"\n\n")
        except Exception as e:
            pass  # Don't fail if logging doesn't work

        response = self._make_request(prompt)

        if response.success:
            # Handle JSON response from providers
            try:
                clean_response = response.content.strip()

                # Remove markdown code fences if present
                if clean_response.startswith("```"):
                    # Remove opening fence (```json or ```)
                    lines = clean_response.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]  # Remove first line
                    # Remove closing fence (```)
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]  # Remove last line
                    clean_response = "\n".join(lines).strip()

                # First try to extract labeled FINAL_DECISION or FINAL_INITIAL_GUESS using regex
                import re

                final_decision_match = re.search(
                    r'"FINAL_DECISION"\s*:\s*"([^"]+)"', clean_response
                )
                final_initial_match = re.search(
                    r'"FINAL_INITIAL_GUESS"\s*:\s*"([^"]+)"', clean_response
                )

                data = {}  # Initialize data dict for logging purposes

                if final_decision_match:
                    chosen = final_decision_match.group(1).strip()
                    # Also try to get changed and reason if present
                    changed_match = re.search(
                        r'"changed"\s*:\s*(true|false)', clean_response
                    )
                    reason_match = re.search(
                        r'"reason"\s*:\s*"([^"]+)"', clean_response
                    )
                    reasoning = reason_match.group(1) if reason_match else ""
                    changed = (
                        changed_match.group(1).lower() == "true"
                        if changed_match
                        else False
                    )
                    # Store extracted values in data dict for logging
                    data = {
                        "final_decision": chosen,
                        "changed": changed,
                        "reason": reasoning,
                    }
                elif final_initial_match:
                    chosen = final_initial_match.group(1).strip()
                    reasoning = ""
                    changed = False
                    data = {"final_initial_guess": chosen}
                else:
                    # Fallback to parsing JSON normally
                    data = json.loads(clean_response)
                    chosen = data.get("final_choice", "") or data.get("choice", "")
                    chosen = chosen.strip()
                    reasoning = data.get("reasoning", "")
                    changed = data.get("changed", False)

                # Extract just the spelling if AI included the definition
                # e.g. "close (adjective, near or nearby)" -> "close"
                if "(" in chosen:
                    chosen = chosen.split("(")[0].strip()

                log_message(f"AI Response JSON: {data}", level="DEBUG")

                # Log attempt-first specific info if available
                if initial_guess and changed is not None:
                    log_message(
                        f"Initial guess: '{initial_guess}' → Final choice: '{chosen}' (Changed: {changed})",
                        level="DEBUG",
                    )
                    if "reason" in data:
                        log_message(
                            f"Reason for change: {data.get('reason', '')}",
                            level="DEBUG",
                        )

                if chosen in option_spellings:
                    log_message(
                        f"✅ VALID CHOICE: '{chosen}' (confidence: 0.95)", level="DEBUG"
                    )
                    if reasoning:
                        log_message(f"Reasoning: {reasoning}", level="DEBUG")
                    return AIResponse(True, chosen, 0.95, reasoning)
                else:
                    log_message(
                        f"❌ INVALID CHOICE: '{chosen}' not in {option_spellings}",
                        level="WARNING",
                    )
                    return AIResponse(
                        False, "", 0.0, f"AI returned invalid option: {chosen}"
                    )

            except json.JSONDecodeError as e:
                log_message(f"❌ JSON DECODE ERROR: {e}", level="ERROR")
                log_message(f"Raw response was: {response.content}", level="DEBUG")

                # Try to extract JSON from the response using regex as fallback
                import re

                json_match = re.search(
                    r'\{{[^{{}}]*("final_choice"|"initial_guess"|"choice")[^{{}}]*\}}',
                    clean_response,
                    re.DOTALL,
                )
                if json_match:
                    try:
                        data = json.loads(json_match.group(0))
                        chosen = (
                            data.get("final_choice", "")
                            or data.get("initial_guess", "")
                            or data.get("choice", "")
                        )
                        chosen = chosen.strip()
                        if "(" in chosen:
                            chosen = chosen.split("(")[0].strip()

                        if chosen in option_spellings:
                            log_message(
                                f"✅ RECOVERED CHOICE via regex: '{chosen}'",
                                level="DEBUG",
                            )
                            return AIResponse(
                                True, chosen, 0.85, "Extracted from malformed response"
                            )
                    except:
                        pass

                return AIResponse(False, "", 0.0, "AI returned malformed JSON")
        else:
            log_message(
                f"❌ AI REQUEST FAILED: {response.error_message}", level="ERROR"
            )

        return response

    def analyze_homographs_batch(self, items: List[Dict], word_examples: Dict = None) -> Dict[int, AIResponse]:
        """
        Analyze a batch of homographs with a single AI call.

        Args:
            items: A list of dictionaries, where each dict contains:
                   'id', 'word', 'context', 'options' (list of spellings)
            word_examples: Optional dict mapping word -> {spelling: [example sentences]}

        Returns:
            A dictionary mapping each item's id to its AIResponse.
        """
        if not items:
            return {}

        # Ollama can't reliably handle multi-item JSON batches — process one at a time
        if self.provider == "ollama" and len(items) > 1:
            all_decisions = {}
            for item in items:
                original_id = item["id"]
                # Remap to id=1 so AI always matches the prompt template example
                remapped = dict(item)
                remapped["id"] = 1
                single_result = self.analyze_homographs_batch([remapped], word_examples)
                if 1 in single_result:
                    all_decisions[original_id] = single_result[1]
            return all_decisions

        log_message(
            f"\n=== ANALYZING HOMOGRAPH BATCH ({len(items)} items) ===", level="DEBUG"
        )

        # Format the batch items for the prompt
        batch_items_text = []
        for item in items:
            # Use json.dumps to properly escape special characters
            item_dict = {
                "id": item["id"],
                "word": item["word"],
                "context": item["context"],
                "options": item["options"],  # Keep as a list, not a string
            }
            item_text = json.dumps(item_dict, ensure_ascii=False)
            batch_items_text.append(item_text)

        # Build examples section from curated choices.json examples
        examples_section = ""
        if word_examples:
            lines = ["**REFERENCE EXAMPLES (correct usage for each word):**"]
            for word, spellings in sorted(word_examples.items()):
                for spelling, examples in spellings.items():
                    for ex in examples:
                        lines.append(f'  {word} → "{spelling}": "{ex}"')
            examples_section = "\n".join(lines) + "\n"

        batch_prompt = self._load_prompt("homograph_batch")
        if not batch_prompt:
            return {
                item["id"]: AIResponse(False, "", 0.0, "Batch prompt not found.")
                for item in items
            }

        prompt = batch_prompt.replace("WORD_EXAMPLES", examples_section)
        prompt = prompt.replace("BATCH_ITEMS", "[\n" + ",\n".join(batch_items_text) + "\n]")

        log_message(
            f"Batch prompt sent to AI (Provider: {self.provider}):\n{prompt}",
            level="DEBUG",
        )

        # Build a map of item_id -> valid spellings for validation
        valid_spellings_by_id = {}
        for item in items:
            item_id = item["id"]
            valid_spellings = {opt["spelling"] for opt in item.get("options", [])}
            valid_spellings_by_id[item_id] = valid_spellings

        response = self._make_request(prompt)
        decisions = {}

        if response.success:
            try:
                clean_response = response.content.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    clean_response = "\n".join(lines).strip()

                # Fix invalid \' escape sequences Ollama emits for apostrophes in spellings
                clean_response = clean_response.replace("\\'", "'")

                log_message(f"Raw AI batch response: {clean_response}", level="DEBUG")
                batch_data = json.loads(clean_response)

                if not isinstance(batch_data, list):
                    raise ValueError("AI response is not a JSON array.")

                # Validate that list contains dicts
                for idx, item in enumerate(batch_data):
                    if not isinstance(item, dict):
                        raise ValueError(
                            f"Item {idx} in batch response is not a dict: {type(item).__name__}"
                        )

                for result in batch_data:
                    item_id = result.get("id")
                    decision = result.get("decision", {})
                    choice = decision.get("choice")
                    reasoning = decision.get("reasoning", "")

                    if item_id is not None and choice:
                        # Validate that the choice is one of the valid spellings
                        valid_spellings = valid_spellings_by_id.get(item_id, set())
                        if choice not in valid_spellings:
                            log_message(
                                f"AI returned invalid choice '{choice}' for item {item_id}. Valid spellings: {valid_spellings}",
                                level="WARNING",
                            )
                            decisions[item_id] = AIResponse(False, "", 0.0, f"Invalid choice: {choice}")
                        else:
                            decisions[item_id] = AIResponse(True, choice, 0.95, reasoning)
                    else:
                        log_message(
                            f"Skipping malformed item in batch response: {result}",
                            level="WARNING",
                        )

            except (
                json.JSONDecodeError,
                ValueError,
                KeyError,
                AttributeError,
                TypeError,
            ) as e:
                error_msg = f"Failed to parse batch response: {e}"
                log_message(error_msg, level="ERROR")
                # Create a failure response for all items in the batch
                for item in items:
                    decisions[item["id"]] = AIResponse(False, "", 0.0, error_msg)
        else:
            # If the entire request fails, create a failure response for all items
            for item in items:
                decisions[item["id"]] = AIResponse(
                    False, "", 0.0, response.error_message
                )

        return decisions

    def analyze_roman_numeral(self, roman: str, context: str) -> AIResponse:
        """
        Determine if a Roman numeral should be converted to words or kept as-is.

        Args:
            roman: The Roman numeral text (e.g., "IV", "DC", "CD")
            context: Surrounding text

        Returns:
            AIResponse with "CONVERT" or "KEEP" decision
        """
        prompt = f"""Determine if this Roman numeral should be converted to words or kept as abbreviation.

Roman numeral: "{roman}"
Context: "{context}"

CONVERT to words if:
- Chapter numbers (Chapter IV → Chapter Four)
- Ordinal names (John XXIII → John the Twenty-third)
- Dates or years (MMXX → Two Thousand Twenty)
- Sequence numbers in text

KEEP as abbreviation if:
- Location codes (Washington DC, New York City)
- Technology abbreviations (DVD, CD, LCD)
- Company/organization names
- Common abbreviations that aren't numbers

Examples:
- "Chapter IV of the book" → CONVERT
- "Washington DC area" → KEEP
- "Pope John XXIII" → CONVERT
- "bought a new CD" → KEEP

Respond with only: CONVERT or KEEP"""

        response = self._make_request(prompt)
        if response.success:
            decision = response.content.strip().upper()
            if decision in ["CONVERT", "KEEP"]:
                confidence = (
                    0.9
                    if any(
                        indicator in context.lower()
                        for indicator in [
                            "chapter",
                            "pope",
                            "king",
                            "queen",
                            "washington",
                            "cd ",
                            "dvd",
                            "lcd",
                        ]
                    )
                    else 0.7
                )
                return AIResponse(True, decision, confidence, f"Decision: {decision}")

        return AIResponse(False, "KEEP", 0.0, "AI analysis failed, defaulting to KEEP")

    def analyze_roman_conversion(
        self, roman: str, arabic: str, context: str
    ) -> AIResponse:
        """
        Determine if a Roman numeral should be converted to its Arabic equivalent.

        Args:
            roman: The Roman numeral text (e.g., "IV", "XII")
            arabic: The Arabic equivalent (e.g., "4", "12")
            context: Surrounding text context

        Returns:
            AIResponse with "yes" or "no" for conversion decision
        """
        prompt = f"""Should this Roman numeral be converted?

Roman numeral: "{roman}"
Arabic equivalent: "{arabic}"
Context: "{context}"

ANALYZE THE IMMEDIATE WORDS AROUND "{roman}":
Look at what comes directly before and after this specific Roman numeral.

CONVERT (respond "yes") if:
- Chapter/section numbers in books: "Chapter IV" → "Chapter 4"
- Sequential numbering: "Part III" → "Part 3", "Tallos IV" → "Tallos 4"
- Dates or years: "Founded in MCMXC" → "Founded in 1990", "dated to MCMLXXXIV" → "dated to 1984"
- Page numbers: "See page XII" → "See page 12"
- Arena/venue numbers: "arena LXXX" → "arena 80"
- Royal names: "Henry VIII" → "Henry the Eighth"
- Pope names: "Pope John V" → "Pope John the Fifth"

DO NOT CONVERT (respond "no") if:
- Personal initials or single letters: "Mrs. C", "Dr. V", "John D"
- Abbreviations: "Washington DC", "DVD player", "LCD screen"
- Common acronyms: "IV drip" (intravenous), "XO brandy"
- Brand names or product codes: "iPhone X", "Windows XI"
- Chemical or technical notations

Key rules:
1. If it's a single letter after Mrs./Mr./Dr./Ms. → DO NOT CONVERT (highest priority)
2. If it appears after a person's name (Henry, John, Charles, etc.) → CONVERT
3. If it appears after "Pope" → CONVERT
4. If it's in a date/year context → CONVERT
5. If it's a chapter/part/section → CONVERT

IMPORTANT: Check the immediate context around the Roman numeral. Personal initials like "Mrs. C" should NEVER be converted, even if there are other convertible Roman numerals elsewhere in the text.

Respond with only: yes or no"""

        response = self._make_request(prompt)
        if response.success:
            decision = response.content.strip().lower()
            if decision in ["yes", "no", "convert", "don't convert", "do not convert"]:
                # Map various responses to yes/no
                should_convert = decision in ["yes", "convert"]

                # Confidence based on context indicators
                context_lower = context.lower()

                # High confidence indicators
                high_confidence_indicators = [
                    "chapter",
                    "section",
                    "part",
                    "volume",
                    "book",
                    "page",
                    "henry",
                    "john",
                    "pope",
                    "arena",
                    "dated to",
                    "year",
                    "founded in",
                ]

                # Personal initial indicators (high confidence for NOT converting)
                personal_indicators = ["mrs.", "mr.", "dr.", "ms."]

                if any(
                    indicator in context_lower
                    for indicator in high_confidence_indicators
                ):
                    confidence = 0.9
                elif any(
                    indicator in context_lower for indicator in personal_indicators
                ):
                    confidence = 0.95  # Very high confidence for personal initials
                else:
                    confidence = 0.85  # Default higher than threshold

                return AIResponse(
                    True,
                    "yes" if should_convert else "no",
                    confidence,
                    f"Decision: {'convert' if should_convert else 'keep'} based on context",
                )

        return AIResponse(
            False, "no", 0.0, "AI analysis failed, defaulting to no conversion"
        )

    def analyze_allcaps_sequence(self, caps_text: str, context: str) -> AIResponse:
        """
        Determine if an all-caps sequence should be converted to lowercase.

        Args:
            caps_text: The all-caps text sequence (e.g., "NASA", "FBI", "HELLO WORLD")
            context: Surrounding text context

        Returns:
            AIResponse with "lowercase", "keep", or "ignore" decision
        """
        prompt = f"""Should this all-caps sequence be converted to lowercase?

All-caps text: "{caps_text}"
Context: "{context}"

LOWERCASE (respond "lowercase") if:
- Shouting or emphasis: "I'M SO EXCITED" → "I'm so excited"
- Mistaken caps lock: "THIS IS A SENTENCE" → "This is a sentence"
- Names/titles that aren't abbreviations: "JOHN SMITH" → "John Smith"
- Common words typed in caps: "THE QUICK BROWN FOX" → "The quick brown fox"

KEEP (respond "keep") if:
- Acronyms and abbreviations: "NASA", "FBI", "USA", "CEO"
- Technical terms: "CPU", "RAM", "HTML", "API"
- Military/government codes: "NATO", "AWOL", "KIA"
- Proper nouns that are commonly capitalized: "NYC", "UK"

IGNORE (respond "ignore") if:
- Should be permanently ignored in future processing
- Common abbreviations that appear frequently

Consider:
1. Is this an acronym/abbreviation or regular text in caps?
2. Does the context suggest this is emphasis/shouting vs. a proper abbreviation?
3. How long is the sequence? (longer sequences more likely to be emphasis)
4. Are these common words that were likely typed in caps accidentally?

Examples:
- "I LOVE THIS BOOK" in casual text → lowercase
- "Contact the FBI immediately" → keep
- "New York, NY" → keep
- "CHAPTER ONE" → lowercase
- "He said I'M NOT GOING" → lowercase

Respond with only: lowercase, keep, or ignore"""

        response = self._make_request(prompt)
        if response.success:
            decision = response.content.strip().lower()
            valid_decisions = ["lowercase", "keep", "ignore"]

            if decision in valid_decisions:
                # Confidence based on context and characteristics
                confidence = 0.9

                # Lower confidence for borderline cases
                if len(caps_text) <= 5 and caps_text.replace(" ", "").isalpha():
                    # Short sequences could be acronyms or emphasis
                    confidence = 0.7
                elif any(
                    indicator in context.lower()
                    for indicator in ["said", "shouted", "yelled", "screamed"]
                ):
                    # Speech context suggests emphasis
                    confidence = 0.9
                elif caps_text.count(" ") > 2:
                    # Long sequences more likely to be emphasis
                    confidence = 0.9

                return AIResponse(
                    True,
                    decision,
                    confidence,
                    f"Decision: {decision} based on context analysis",
                )

        return AIResponse(False, "keep", 0.0, "AI analysis failed, defaulting to keep")

    def analyze_numbered_line(self, line: str, numbers: List[str]) -> AIResponse:
        """
        Analyze a line with numbers and suggest formatting improvements.

        Args:
            line: The line containing numbers
            numbers: List of number strings found in the line

        Returns:
            AIResponse with suggested line formatting or "keep" to leave unchanged
        """
        prompt = f"""Analyze this line and suggest formatting improvements for the numbers:

Line: "{line}"
Numbers found: {numbers}

Common improvements:
1. Roman numeral conversion: "Chapter 12" might need "Chapter XII" → "Chapter 12"
2. Page number formatting: "page 1234" → "page 1,234"
3. Date formatting: "year 1995" → "year 1995" (usually correct)
4. Number word conversion: "Chapter 1" → "Chapter One"
5. Ordinal formatting: "1st edition" → "first edition"

Consider:
- Is this a chapter/section number that should be written as words?
- Are these page numbers that need comma formatting?
- Are these dates that should remain as numbers?
- Are these Roman numerals that were already converted and should stay as numbers?
- Should large numbers have comma separators?

If improvements are needed, provide the corrected line.
If the line is fine as-is, respond "keep".

Examples:
- "Chapter 12 discusses the topic" → "Chapter Twelve discusses the topic"
- "See page 1234 for details" → "See page 1,234 for details"
- "In year 1995 something happened" → keep (dates usually stay as numbers)
- "The 1st time he tried" → "The first time he tried"

Respond with either:
- "keep" (if no changes needed)
- The corrected line (if improvements needed)"""

        response = self._make_request(prompt)
        if response.success:
            suggestion = response.content.strip()

            if suggestion.lower() == "keep":
                return AIResponse(True, "keep", 0.8, "Line formatting is appropriate")
            elif suggestion != line:  # AI suggests a change
                confidence = 0.7  # Moderate confidence for formatting changes
                return AIResponse(
                    True, suggestion, confidence, f"Suggested formatting improvement"
                )

        return AIResponse(
            False, "keep", 0.0, "AI analysis failed, keeping line unchanged"
        )

    def analyze_number_formatting(
        self, number: str, context: str, rules: Dict[str, str]
    ) -> AIResponse:
        """Delegate to NumberAnalyzer."""
        return self.numbers.analyze_formatting(number, context, rules)

    def classify_number(self, number: str, context: str) -> AIResponse:
        """Ask the AI to classify the type of a number based on its context."""
        prompt_template = self._load_prompt("number_classification")
        if not prompt_template:
            return AIResponse(False, "general_number", 0.0, "Prompt not found")

        prompt = prompt_template.format(number=number, context=context)
        response = self._make_request(prompt)

        if response.success:
            # The response should be a single word, e.g., "year"
            classification = response.content.strip().lower().replace(".", "")
            return AIResponse(
                True, classification, response.confidence, "Classification successful"
            )

        # Fallback to a general type if AI fails
        return AIResponse(False, "general_number", 0.0, "AI classification failed")

    def _repair_json(self, content: str) -> str:
        """Attempt to repair malformed JSON from AI responses."""
        # Strip trailing commas before closing braces/brackets
        content = re.sub(r',\s*([}\]])', r'\1', content)

        # Fix missing commas between objects in arrays
        content = re.sub(r'}\s*{', '}, {', content)
        content = re.sub(r'}\s*\[', '}, [', content)

        # Fix indentation-based structural errors: when "reasoning" line is followed by
        # a closing brace at the wrong indentation level (closing outer object instead of nested object)
        lines = content.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            if '"reasoning":' in line:
                fixed_lines.append(line)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    curr_indent = len(line) - len(line.lstrip())
                    next_indent = len(next_line) - len(next_line.lstrip())

                    # Check if next line is a closing brace
                    if next_line.strip() in ('}', '},'):
                        expected_indent = curr_indent - 4
                        if next_indent == expected_indent - 4:
                            fixed_lines.append(' ' * expected_indent + '}')
                continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def classify_numbers_batch(self, items: List[Dict]) -> Dict[int, AIResponse]:
        """
        Classify a batch of numbers with a single AI call.

        Args:
            items: A list of dictionaries, where each dict contains:
                   'id', 'number', 'context'

        Returns:
            A dictionary mapping each item's id to its AIResponse containing the classification type.
        """
        if not items:
            return {}

        log_message(
            f"\n=== CLASSIFYING NUMBER BATCH ({len(items)} items) ===", level="DEBUG"
        )

        # Validate all items have required keys
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"Item {idx} is not a dict: {type(item)}")
            for key in ["id", "number", "context"]:
                if key not in item:
                    raise ValueError(f"Item {idx} missing required key '{key}': {item}")

        # Format the batch items for the prompt
        batch_items_text = []
        for item in items:
            # Use json.dumps to properly escape special characters
            item_dict = {
                "id": item["id"],
                "number": item["number"],
                "context": item["context"],
            }
            item_text = json.dumps(item_dict, ensure_ascii=False)
            batch_items_text.append(item_text)

        batch_prompt = self._load_prompt("number_classification_batch")
        if not batch_prompt:
            return {
                item["id"]: AIResponse(
                    False, "general_number", 0.0, "Batch prompt not found."
                )
                for item in items
            }

        prompt = batch_prompt.format(
            batch_items_text="[\n" + ",\n".join(batch_items_text) + "\n]"
        )

        log_message(
            f"Number batch prompt sent to AI (Provider: {self.provider}):\n{prompt}",
            level="DEBUG",
        )
        response = self._make_request(prompt)
        classifications = {}

        if response.success:
            try:
                clean_response = response.content.strip()
                # Remove markdown code blocks if present
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    clean_response = "\n".join(lines).strip()

                log_message(f"Raw AI batch response: {clean_response}", level="DEBUG")
                # Repair common JSON formatting issues from AI responses
                clean_response = self._repair_json(clean_response)
                batch_data = json.loads(clean_response)

                if not isinstance(batch_data, list):
                    raise ValueError("AI response is not a JSON array.")

                # Validate that list contains dicts
                for idx, item in enumerate(batch_data):
                    if not isinstance(item, dict):
                        raise ValueError(
                            f"Item {idx} in batch response is not a dict: {type(item).__name__}"
                        )

                for result in batch_data:
                    item_id = result.get("id")
                    classification = result.get("classification", {})
                    type_str = classification.get("type")
                    reasoning = classification.get("reasoning", "")

                    if item_id is not None and type_str:
                        # Normalize the classification type
                        type_str = type_str.strip().lower().replace(".", "")
                        classifications[item_id] = AIResponse(
                            True, type_str, 0.95, reasoning
                        )
                    else:
                        log_message(
                            f"Skipping malformed item in batch response: {result}",
                            level="WARNING",
                        )

            except (
                json.JSONDecodeError,
                ValueError,
                KeyError,
                AttributeError,
                TypeError,
            ) as e:
                error_msg = f"Failed to parse number batch response: {e}"
                log_message(error_msg, level="ERROR")
                log_message(f"Raw response: {response.content}", level="ERROR")
                # Return failure for all items
                return {
                    item["id"]: AIResponse(False, "general_number", 0.0, error_msg)
                    for item in items
                }
        else:
            error_msg = f"Batch request failed: {response.error_message}"
            log_message(error_msg, level="ERROR")
            return {
                item["id"]: AIResponse(False, "general_number", 0.0, error_msg)
                for item in items
            }

        # Fill in any missing items with default responses
        for item in items:
            if item["id"] not in classifications:
                log_message(
                    f"Item ID {item['id']} not found in AI response, using default",
                    level="WARNING",
                )
                classifications[item["id"]] = AIResponse(
                    False, "general_number", 0.0, "Not found in AI response"
                )

        log_message(
            f"Batch classification complete: {len(classifications)} items processed",
            level="DEBUG",
        )
        return classifications

    def analyze_caps_sequence(
        self, caps_text: str, context: str, cap_ignore_list: List[str]
    ) -> AIResponse:
        """Delegate to CapsAnalyzer."""
        return self.caps.analyze_sequence(caps_text, context, cap_ignore_list)

    def extract_context_keywords(
        self,
        word: str,
        chosen_pronunciation: str,
        pronunciation_description: str,
        context: str,
    ) -> List[str]:
        """
        Extract context keywords that indicate a specific pronunciation.

        Args:
            word: The heteronym (e.g., "close")
            chosen_pronunciation: The pronunciation chosen by user (e.g., "klohz")
            pronunciation_description: Description of meaning (e.g., "verb: to shut")
            context: Full context (sentence or paragraph)

        Returns:
            List of 3-5 keywords that strongly indicate this pronunciation

        Example:
            word="close", pronunciation="klohz", description="verb: to shut",
            context="walked over and tried to close the heavy wooden door"
            → Returns: ["door", "shut", "tried"]
        """
        prompt = f"""You are a keyword extraction system. Your ONLY job is to return a JSON array.

Word: "{word}"
Pronunciation: "{chosen_pronunciation}" ({pronunciation_description})
Context: {context}

Task: Extract 3-5 keywords from the context that strongly indicate this pronunciation.

Rules:
- Content words only (nouns, verbs, adjectives)
- No articles, conjunctions, or generic words ("the", "and", "was", "very")
- Must appear in the context
- Rank by relevance (strongest first)
- 3+ character words
- Maximum 5 keywords

CRITICAL: Respond with ONLY a JSON array, nothing else. No explanation. No text. Just the array.
["keyword1", "keyword2", "keyword3"]"""

        try:
            response = self._make_request(prompt)
            log_message(
                f"Keyword extraction response: success={response.success}, content={response.content[:100]}",
                level="DEBUG",
            )

            if response.success:
                content = response.content.strip()
                log_message(f"Raw AI response: {content}", level="DEBUG")

                # Remove markdown code fences if present
                if content.startswith("```"):
                    lines = content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    content = "\n".join(lines).strip()
                    log_message(f"After removing code fences: {content}", level="DEBUG")

                # Extract JSON array from content (even if there's extra text)
                import json
                import re

                # Try direct JSON parsing first
                try:
                    keywords = json.loads(content)
                    log_message(f"Parsed JSON directly: {keywords}", level="DEBUG")
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON array from text
                    log_message(
                        f"Direct JSON parsing failed, attempting to extract array from text",
                        level="DEBUG",
                    )
                    # Look for [...] pattern
                    match = re.search(r"\[.*?\]", content, re.DOTALL)
                    if match:
                        json_str = match.group(0)
                        log_message(
                            f"Extracted JSON string: {json_str[:100]}", level="DEBUG"
                        )
                        try:
                            keywords = json.loads(json_str)
                            log_message(
                                f"Parsed extracted JSON: {keywords}", level="DEBUG"
                            )
                        except json.JSONDecodeError as e:
                            log_message(
                                f"Failed to parse extracted JSON: {e}", level="ERROR"
                            )
                            keywords = None
                    else:
                        log_message(f"No JSON array found in response", level="DEBUG")
                        keywords = None

                if not keywords:
                    keywords = None

                log_message(
                    f"Final keywords: {keywords}, type: {type(keywords) if keywords else 'None'}",
                    level="DEBUG",
                )

                if isinstance(keywords, list):
                    # Filter out short/generic keywords
                    filtered = [
                        k
                        for k in keywords
                        if len(k) >= 3
                        and k.lower()
                        not in {
                            "the",
                            "and",
                            "but",
                            "was",
                            "were",
                            "has",
                            "have",
                            "this",
                            "that",
                            "with",
                        }
                    ]
                    log_message(f"After filtering: {filtered}", level="DEBUG")

                    # Limit to 5 keywords
                    return filtered[:5]
                else:
                    log_message(
                        f"Response is not a list, it's: {type(keywords)}",
                        level="WARNING",
                    )
            else:
                log_message(
                    f"AI response not successful: {response.error_message}",
                    level="WARNING",
                )

        except Exception as e:
            import traceback

            log_message(f"Keyword extraction failed: {e}", level="ERROR")
            log_message(f"Full traceback: {traceback.format_exc()}", level="ERROR")

        return []

    def analyze_caps_sequence_old(
        self, caps_text: str, context: str, cap_ignore_list: List[str]
    ) -> AIResponse:
        """
        OLD VERSION - Analyze an all-caps sequence and determine how to handle it.

        Args:
            caps_text: The all-caps sequence (e.g., "NASA", "CHAPTER ONE", "XPS-12")
            context: Surrounding text context
            cap_ignore_list: Current CAP_IGNORE list

        Returns:
            AIResponse with suggestion and reasoning
        """
        # Format the CAP_IGNORE list for the prompt
        ignore_examples = ", ".join(cap_ignore_list[:20])  # Show first 20
        if len(cap_ignore_list) > 20:
            ignore_examples += f", ... ({len(cap_ignore_list)} total)"

        prompt = f"""Analyze this all-caps sequence and determine how to handle it for Text-To-Speech (TTS).

Caps Sequence: "{caps_text}"
Context: "{context}"

## CURRENT CAP_IGNORE LIST:
These sequences should STAY in all-caps (they're legitimate acronyms/codes):
{ignore_examples}

## RULES:

**CONTEXT: This is an ISOLATED caps word (surrounded by lowercase text).**
**Groups of caps words have already been auto-lowercased.**

**KEEP AS-IS (suggest: "keep"):**
- **Certain acronyms**: FBI, CIA, NASA, AI, DVD, CD, LCD, HUD, GPS, DNA, RNA
- **Technical terms**: VASIMR, LFTR, EMP, SJ (appears in technical context)
- **Ship prefixes**: USC, ESX, USS, HMS (when before ship name)
- **Military/tech abbreviations**: EVA, MRI, PDA, CIC, AU
- **Indicators**:
  - 2-5 letters AND appears with technical context words (drive, system, unit, reactor, weapon, sensor)
  - Known abbreviation pattern
  - In CAP_IGNORE list or similar to existing entries

**LOWERCASE (suggest: "lowercase"):**
- **Emphasis words that slipped through** (rare - most already handled)
- **Unknown caps words** with no clear technical context
- **Possible typos**: HTE, TTHE (misspelled common words)

**UNCERTAIN (suggest: "keep" if leaning acronym, "lowercase" if unsure):**
- **New technical terms**: Not in CAP_IGNORE but looks like acronym
- **Ambiguous context**: Could be acronym or emphasis
- **When in doubt**: Suggest "keep" and let user decide (they can add to CAP_IGNORE or lowercase)

## YOUR TASK:
1. Determine if this sequence is in the CAP_IGNORE list or similar to items in it
2. If it's a legitimate acronym/code NOT in the list, suggest "keep" (it will be added)
3. If it's emphasis/shouting/titles, suggest "lowercase" or "title"
4. Respond in JSON format:

{{
  "suggestion": "keep|lowercase|title",
  "reasoning": "brief explanation of your decision"
}}

Be concise in reasoning (1-2 sentences max)."""

        response = self._make_request(prompt)
        if response.success:
            try:
                # Parse JSON response
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
                suggestion = result.get("suggestion", "keep")
                reasoning = result.get("reasoning", "Analysis completed")

                # Confidence based on suggestion type
                confidence = (
                    0.85 if suggestion in ("keep", "lowercase", "title") else 0.6
                )

                return AIResponse(True, suggestion, confidence, reasoning)

            except json.JSONDecodeError:
                # Fallback: treat response as plain suggestion
                suggestion = response.content.strip().lower()
                if suggestion in ("keep", "lowercase", "title"):
                    return AIResponse(
                        True, suggestion, 0.7, "Analysis completed (non-JSON response)"
                    )
                else:
                    return AIResponse(False, "keep", 0.0, "Invalid response format")

        return AIResponse(False, "keep", 0.0, "AI analysis failed, keeping original")

    def analyze_page_number(self, number: str, context: str) -> AIResponse:
        """
        Analyze if a standalone number is a page number.

        Args:
            number: The number to analyze
            context: Surrounding text context

        Returns:
            AIResponse with suggestion "page_number" or "content_number"
        """
        prompt = f"""Analyze if the number in brackets is a page number or part of the content.

Context:
{context}

PAGE NUMBER indicators:
- Appears alone on a line or with minimal text
- No meaningful relationship to surrounding content
- Likely part of sequential pagination
- Common positions: top/bottom of section, between paragraphs

CONTENT NUMBER indicators:
- Part of a date, time, measurement, or identifier
- Referenced in surrounding text
- Part of a list or enumeration
- Has semantic meaning in context

Respond with ONLY one word:
- "page_number" if this is pagination
- "content_number" if this is meaningful content

Response:"""

        response = self._make_request(prompt)

        if response.success:
            suggestion = response.content.strip().lower()
            if "page" in suggestion:
                return AIResponse(True, "page_number", 0.8, "Identified as page number")
            else:
                return AIResponse(True, "content_number", 0.8, "Identified as content")

        return AIResponse(
            False, "content_number", 0.0, "AI analysis failed, keeping number"
        )

    def analyze_line_fragment(self, text_block: str) -> AIResponse:
        """
        Analyze text block to identify and rejoin broken line fragments.

        Args:
            text_block: Block of text with potential line breaks

        Returns:
            AIResponse with suggestion for rejoined text
        """
        prompt = f"""Analyze this text block and fix broken line fragments from OCR or ebook formatting.

Text block:
{text_block}

RULES:
1. Join incomplete sentences split across lines
2. Remove hyphenation artifacts (e.g., "re-\nactor" → "reactor")
3. Preserve intentional paragraph breaks
4. Fix fragments like "Frank\nchuckled\nagain" → "Frank chuckled again"
5. Keep proper sentence structure

Respond with the corrected text ONLY, no explanation."""

        response = self._make_request(prompt)

        if response.success:
            corrected = response.content.strip()
            if corrected and corrected != text_block:
                return AIResponse(True, corrected, 0.9, "Line fragments rejoined")

        return AIResponse(False, text_block, 0.0, "No changes needed or AI failed")

    def _make_request(self, prompt: str) -> AIResponse:
        """Make API request to the configured provider."""
        for attempt in range(self.max_retries):
            try:
                if self.provider == "llama-cpp":
                    return self._llama_cpp_request(prompt)
                elif self.provider in ("openai", "groq", "together", "mistral"):
                    return self._openai_request(prompt)
                elif self.provider == "gemini":
                    return self._gemini_request(prompt)
                elif self.provider == "anthropic":
                    return self._anthropic_request(prompt)
                elif self.provider == "ollama":
                    return self._ollama_request(prompt)
                elif self.provider == "huggingface":
                    return self._huggingface_request(prompt)
                else:
                    return AIResponse(
                        False, "", 0.0, "", f"Unsupported provider: {self.provider}"
                    )

            except Exception as e:
                error_msg = f"Request failed (attempt {attempt + 1}): {str(e)}"
                print(f"DEBUG: {error_msg}")  # Debug output
                # Don't retry quota exhaustion — daily limit won't recover in seconds
                if "QUOTA_EXHAUSTED" in str(e):
                    log_message(
                        "Gemini daily quota exhausted — skipping remaining AI calls. Quota resets daily.",
                        level="WARNING",
                    )
                    return AIResponse(False, "", 0.0, "", f"Quota exhausted: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                    continue
                return AIResponse(False, "", 0.0, "", error_msg)

        return AIResponse(False, "", 0.0, "", "Max retries exceeded")

    def _llama_cpp_request(self, prompt: str) -> AIResponse:
        """Make request to local llama-cpp model."""
        if not self.llm:
            log_message("LLM not loaded, cannot make request.", level="ERROR")
            return AIResponse(False, "", 0.0, "", "LLM not loaded.")

        try:
            # For multi-line prompts, don't stop at first newline
            # Use empty stop list to let model generate complete responses
            output = self.llm(
                prompt,
                max_tokens=500,
                temperature=0.0,  # Deterministic output
                stop=[],  # Don't stop at newline for multi-line prompts
            )
            content = output["choices"][0]["text"].strip()
            # Confidence is high by default as we rely on prompt structure
            return AIResponse(True, content, confidence=0.9)
        except Exception as e:
            log_message(f"Error during LLM inference: {e}", level="ERROR")
            return AIResponse(False, "", 0.0, "", str(e))

    def _openai_request(self, prompt: str) -> AIResponse:
        """Make request to OpenAI/Groq/Together API."""
        # Enforce rate limiting
        self._enforce_rate_limit()

        url = f"{self.base_url}/chat/completions"

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,  # Increased to allow reasoning output
            "temperature": 0.0,  # Zero temperature for deterministic results
        }

        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return AIResponse(True, content)

    def _gemini_request(self, prompt: str) -> AIResponse:
        """Make request to Google Gemini API."""
        # Enforce rate limiting
        self._enforce_rate_limit()

        url = f"{self.base_url}/models/{self.model}:generateContent"

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 4000,
                "response_mime_type": "application/json",
            },
        }

        params = {"key": self.api_key}

        print(f"DEBUG: Gemini URL: {url}")
        print(f"DEBUG: Gemini request prepared (API key hidden for security)")
        print(f"DEBUG: Gemini data: {data}")

        response = self.session.post(url, json=data, params=params, timeout=30)

        print(f"DEBUG: Gemini response status: {response.status_code}")
        print(f"DEBUG: Gemini full response: {response.text}")

        if response.status_code == 429:
            try:
                err_body = response.json()
                err_msg = err_body.get("error", {}).get("message", "Rate limit exceeded")
            except Exception:
                err_msg = "Rate limit exceeded (429)"
            log_message(f"Gemini quota/rate limit: {err_msg}", level="WARNING")
            raise requests.exceptions.HTTPError(
                f"QUOTA_EXHAUSTED: {err_msg}", response=response
            )

        response.raise_for_status()

        result = response.json()

        # Handle incomplete responses (MAX_TOKENS, SAFETY, etc.)
        if "candidates" not in result or not result["candidates"]:
            return AIResponse(False, "", 0.0, "", "Gemini API returned no candidates")

        candidate = result["candidates"][0]
        finish_reason = candidate.get("finishReason", "UNKNOWN")

        # Check if response is complete
        if finish_reason == "MAX_TOKENS":
            return AIResponse(
                False,
                "",
                0.0,
                "",
                "Gemini response truncated (MAX_TOKENS). Prompt may be too long.",
            )

        if finish_reason == "SAFETY":
            return AIResponse(
                False, "", 0.0, "", "Gemini blocked response due to safety filters"
            )

        # Try to extract content
        content_obj = candidate.get("content", {})
        parts = content_obj.get("parts", [])

        if not parts or "text" not in parts[0]:
            return AIResponse(
                False,
                "",
                0.0,
                "",
                f"Gemini response incomplete (finishReason: {finish_reason})",
            )

        content = parts[0]["text"]
        return AIResponse(True, content)

    def _anthropic_request(self, prompt: str) -> AIResponse:
        """Make request to Anthropic Claude API."""
        # Enforce rate limiting
        self._enforce_rate_limit()

        url = f"{self.base_url}/messages"

        data = {
            "model": self.model,
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        content = result["content"][0]["text"]

        return AIResponse(True, content)

    def _ollama_request(self, prompt: str) -> AIResponse:
        """Make request to local Ollama API."""
        # Enforce rate limiting (no delay for local)
        self._enforce_rate_limit()

        url = f"{self.base_url}/generate"

        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,  # Low but not zero - allows reasoning while maintaining consistency
                "num_predict": 2500,  # Increased from 50 to allow reasoning output
            },
        }

        response = self.session.post(url, json=data, timeout=300)
        response.raise_for_status()

        result = response.json()
        content = result["response"]

        if not content or not content.strip():
            log_path = Path(__file__).parent.parent / "logs" / "ollama_debug.txt"
            with open(log_path, "a") as f:
                f.write("=== EMPTY RESPONSE ===\n")
                f.write(f"done_reason: {result.get('done_reason', 'unknown')}\n")
                f.write(f"done: {result.get('done')}\n")
                f.write(f"prompt_eval_count: {result.get('prompt_eval_count')}\n")
                f.write(f"eval_count: {result.get('eval_count')}\n")
                f.write(f"prompt (last 500 chars): {prompt[-500:]}\n\n")

        return AIResponse(True, content)

    def _huggingface_request(self, prompt: str) -> AIResponse:
        """Make request to Hugging Face Inference API."""
        # Enforce rate limiting
        self._enforce_rate_limit()

        url = f"{self.base_url}/{self.model}"

        data = {
            "inputs": prompt,
            "parameters": {"max_length": 100, "temperature": 0.0, "do_sample": False},
            "options": {"wait_for_model": True},
        }

        print(f"DEBUG: HuggingFace URL: {url}")
        print(f"DEBUG: HuggingFace data: {data}")

        response = self.session.post(url, json=data, timeout=30)

        print(f"DEBUG: HuggingFace response status: {response.status_code}")
        print(f"DEBUG: HuggingFace response: {response.text[:200]}...")

        response.raise_for_status()

        result = response.json()

        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            # Text generation models typically return a list
            content = result[0].get("generated_text", "").replace(prompt, "").strip()
        elif isinstance(result, dict):
            # Some models return different formats
            content = result.get("generated_text", result.get("text", str(result)))
        else:
            content = str(result)

        return AIResponse(True, content)

    def test_connection(self) -> AIResponse:
        """Test the AI service connection.

        For llama-cpp: checks if model is loaded.
        For API providers: validates configuration (actual API test happens on first request).
        """
        if self.provider == "llama-cpp":
            # For local models, check if actually loaded
            if self.llm:
                return AIResponse(
                    True, f"Model loaded successfully from {self.model_path}"
                )
            else:
                return AIResponse(
                    False, "", 0.0, "", "Model failed to load during initialization."
                )

        # For API-based providers, validate configuration
        elif self.provider in (
            "gemini",
            "openai",
            "groq",
            "together",
            "mistral",
            "anthropic",
            "huggingface",
            "ollama",
        ):
            # Check required configuration
            if not self.provider:
                return AIResponse(False, "", 0.0, "", "No AI provider configured")

            if not self.model:
                return AIResponse(
                    False,
                    "",
                    0.0,
                    "",
                    f"No model specified for {self.provider} provider",
                )

            # Check API key requirement for cloud providers
            cloud_providers = (
                "gemini",
                "openai",
                "groq",
                "together",
                "anthropic",
                "huggingface",
            )
            if self.provider in cloud_providers and not self.api_key:
                return AIResponse(
                    False, "", 0.0, "", f"{self.provider} provider requires an API key"
                )

            # Configuration looks good - actual API test will happen on first request
            return AIResponse(
                True, f"{self.provider} provider configured (model: {self.model})"
            )

        else:
            return AIResponse(
                False, "", 0.0, "", f"Unknown or unconfigured provider: {self.provider}"
            )

    def unload_model(self):
        """
        Sends a request to the Ollama API to unload the current model from VRAM.
        This is a no-op for other providers.
        """
        if self.provider != "ollama":
            return

        if not self.model:
            log_message("No model specified, cannot unload.", level="WARNING")
            return

        log_message(f"Attempting to unload Ollama model: {self.model}", level="DEBUG")

        try:
            url = f"{self.base_url}/generate"
            data = {
                "model": self.model,
                "keep_alive": 0,
                "prompt": "",  # Prompt is required but can be empty
            }

            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            log_message(
                f"Successfully sent unload request for model: {self.model}",
                level="DEBUG",
            )

        except Exception as e:
            log_message(
                f"Failed to send unload request for model {self.model}: {e}",
                level="ERROR",
            )


# Global singleton
_ai_service_instance = None


def get_ai_service() -> "BookfixAIService":
    """
    Get global AI service instance (singleton).

    Returns:
        Shared BookfixAIService instance

    Note: The service must be initialized with configure() before use.
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = BookfixAIService()
    return _ai_service_instance
