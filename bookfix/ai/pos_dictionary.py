"""
POS-Tagged Dictionary Service for Choices.

Maps words to pronunciations based on POS tags.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .pos_tagger import POSToken, DependencyInfo


class POSDictionary:
    """
    Dictionary that maps words to pronunciations using POS tags.

    Example:
        "read" + VBN tag → "red" (past participle)
        "read" + VBP tag → "reed" (present tense)
    """

    def __init__(self, dictionary_path: Path = None):
        """
        Initialize POS dictionary.

        Args:
            dictionary_path: Path to JSON dictionary file
        """
        if dictionary_path is None:
            # Default location
            dictionary_path = (
                Path(__file__).parent.parent.parent
                / ".ai_learning"
                / "choices_pos_dictionary.json"
            )

        self.dictionary_path = dictionary_path
        self.words = {}
        self._load_dictionary()

        # Lazy load spaCy for entity detection
        self._nlp = None

    def _load_dictionary(self):
        """Load dictionary from JSON file."""
        try:
            with open(self.dictionary_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.words = data.get("words", {})
        except FileNotFoundError:
            print(f"Warning: POS dictionary not found at {self.dictionary_path}")
            self.words = {}
        except json.JSONDecodeError as e:
            print(f"Error loading POS dictionary: {e}")
            self.words = {}

    def reload(self):
        """Reload the dictionary from the JSON file."""
        from ..logging import log_message

        log_message("Reloading POS dictionary...")
        self._load_dictionary()

    def get_pronunciation_by_pos(self, word: str, pos_tag: str) -> Optional[str]:
        """
        Get pronunciation for word based on POS tag.

        Args:
            word: The word to look up (e.g., "read")
            pos_tag: POS tag (e.g., "VBN")

        Returns:
            Pronunciation (e.g., "red") or None if not found or ambiguous

        Note: Returns None if multiple pronunciations share the same POS tag,
        allowing context keywords or semantic matching to disambiguate instead.
        """
        word_lower = word.lower()

        if word_lower not in self.words:
            return None

        # Skip disabled entries
        if self.words[word_lower].get("disabled", False):
            return None

        # Find all pronunciations that match this POS tag
        matching_pronunciations = []
        for pronunciation, info in self.words[word_lower].items():
            # Skip metadata keys
            if pronunciation == "disabled":
                continue
            if pos_tag in info.get("pos_tags", []):
                matching_pronunciations.append(pronunciation)

        # If multiple pronunciations match the same POS tag, it's ambiguous
        # Return None and let context keywords/semantic matching decide
        if len(matching_pronunciations) > 1:
            return None

        # Return the unique match, or None if no match
        return matching_pronunciations[0] if matching_pronunciations else None

    def get_all_options(self, word: str) -> List[str]:
        """
        Get all pronunciation options for a word.

        Args:
            word: The word to look up

        Returns:
            List of pronunciation options
        """
        word_lower = word.lower()

        if word_lower not in self.words:
            return []

        # Skip disabled entries
        if self.words[word_lower].get("disabled", False):
            return []

        # Return all keys except metadata keys
        return [k for k in self.words[word_lower].keys() if k != "disabled"]

    def get_option_info(self, word: str, pronunciation: str) -> Optional[Dict]:
        """
        Get detailed info about a pronunciation option.

        Args:
            word: The word (e.g., "read")
            pronunciation: The pronunciation (e.g., "red")

        Returns:
            Dictionary with pos_tags, description, examples
        """
        word_lower = word.lower()

        if word_lower not in self.words:
            return None

        # Skip disabled entries
        if self.words[word_lower].get("disabled", False):
            return None

        return self.words[word_lower].get(pronunciation)

    def explain_choice(self, word: str, pos_tag: str) -> str:
        """
        Get explanation for why a pronunciation was chosen.

        Args:
            word: The word
            pos_tag: POS tag that was detected

        Returns:
            Human-readable explanation
        """
        pronunciation = self.get_pronunciation_by_pos(word, pos_tag)

        if pronunciation is None:
            return f"No pronunciation mapping found for '{word}' with tag {pos_tag}"

        info = self.get_option_info(word, pronunciation)
        if info:
            description = info.get("description", "")
            return f"'{word}' tagged as {pos_tag} → '{pronunciation}' ({description})"

        return f"'{word}' tagged as {pos_tag} → '{pronunciation}'"

    def has_word(self, word: str) -> bool:
        """Check if word is in dictionary and not disabled."""
        word_lower = word.lower()
        if word_lower not in self.words:
            return False
        return not self.words[word_lower].get("disabled", False)

    def get_pronunciation_by_semantic(
        self, word: str, nearby_words: List[str]
    ) -> Optional[Tuple[str, str, float]]:
        """
        Get pronunciation based on semantic tag matching with nearby words.

        Args:
            word: The word to look up (e.g., "refuse")
            nearby_words: Words near the target word (e.g., ["through", "heaps", "in"])

        Returns:
            Tuple of (pronunciation, matched_tag, confidence) or None if no match
            Example: ("refuse", "heap", 0.9)
        """
        word_lower = word.lower()

        if word_lower not in self.words:
            return None

        # Skip disabled entries
        if self.words[word_lower].get("disabled", False):
            return None

        # Convert nearby words to lowercase for matching
        nearby_lower = [w.lower() for w in nearby_words]

        # Check each pronunciation option for semantic tag matches
        matches = []
        for pronunciation, info in self.words[word_lower].items():
            # Skip metadata keys
            if pronunciation == "disabled":
                continue

            semantic_tags = info.get("semantic_tags", [])

            if not semantic_tags:
                continue

            # Check if any nearby word matches a semantic tag
            for nearby in nearby_lower:
                if nearby in semantic_tags:
                    # Found a semantic match
                    # Confidence based on how specific the match is
                    # Common words like "the", "a" get lower confidence
                    confidence = 0.85 if len(nearby) > 3 else 0.6
                    matches.append((pronunciation, nearby, confidence))

        # Return the first match (most relevant)
        if matches:
            return matches[0]

        return None

    def get_pronunciation_by_keywords(
        self, word: str, context: str, window: int = 100
    ) -> Optional[Tuple[str, str, float]]:
        """
        Get pronunciation based on context keyword matching.

        Context keywords are strong indicators of meaning. For example:
        - "close" near "door", "hatch", "window" → KLOHZ (verb: to shut)
        - "close" near "friend", "relationship", "proximity" → KLOHS (adjective: near)

        Args:
            word: The word to look up (e.g., "close")
            context: Full context text (typically 100-200 chars before/after)
            window: Character window to search (default: 100 chars each side)

        Returns:
            Tuple of (pronunciation, matched_keyword, confidence) or None if no match
            Example: ("klohz", "door", 0.90)
        """
        word_lower = word.lower()

        if word_lower not in self.words:
            return None

        # Skip disabled entries
        if self.words[word_lower].get("disabled", False):
            return None

        context_lower = context.lower()

        # Find the actual position of the target word in the context, using the
        # bracketed form produced by _extract_context (e.g. "[read]"). This
        # avoids assuming the word is always at the midpoint of the context
        # window.
        word_pos = len(context) // 2  # Fallback if we cannot find the brackets
        try:
            pattern = r"\[" + re.escape(word_lower) + r"\]"
            match = re.search(pattern, context_lower)
            if match:
                word_pos = (match.start() + match.end()) // 2
        except Exception:
            # If anything goes wrong, keep the conservative midpoint fallback
            pass

        # Check each pronunciation option for keyword matches
        best_match = None
        best_confidence = 0.0

        for pronunciation, info in self.words[word_lower].items():
            # Skip metadata keys
            if pronunciation == "disabled":
                continue

            # Get context keywords for this pronunciation
            context_keywords = info.get("context_keywords", [])

            if not context_keywords:
                continue

            # Check if any keyword appears in context
            for keyword in context_keywords:
                keyword_lower = keyword.lower()

                # Skip if keyword is the same as the target word itself
                # This prevents false matches (e.g., "wound" keyword matching the word "wound")
                if keyword_lower == word_lower:
                    continue

                # For multi-word keywords, match as substring
                # For single-word keywords, match as whole word only
                if " " in keyword_lower:
                    # Multi-word keyword: "lift doors", "lead weight"
                    # Match as exact substring (phrase must appear together)
                    match = keyword_lower in context_lower
                else:
                    # Single-word keyword: "door", "shut"
                    # Match as whole word (not as substring of another word)
                    # Use word boundaries: \b matches word boundaries
                    pattern = r"\b" + re.escape(keyword_lower) + r"\b"
                    match = re.search(pattern, context_lower) is not None

                if match:
                    # Calculate confidence based on:
                    # 1. Proximity to target word (closer = higher confidence)
                    # 2. Keyword specificity (longer words = higher confidence)

                    # Find position of keyword in context (first occurrence)
                    keyword_pos = context_lower.find(keyword_lower)
                    if keyword_pos == -1:
                        continue

                    # Distance from word (in characters)
                    distance = abs(keyword_pos - word_pos)

                    # Base confidence from keyword length (specific words are better)
                    # Cap to keep keyword strictly below POS/complex POS layers.
                    base_confidence = min(0.83, 0.70 + (len(keyword_lower) * 0.02))

                    # Proximity adjustment: reward only genuinely close matches.
                    if distance < 10:
                        proximity_boost = 0.05  # Very close
                    elif distance < 25:
                        proximity_boost = 0.03  # Close
                    elif distance < 50:
                        proximity_boost = 0.01  # Nearby
                    else:
                        proximity_boost = 0.0  # Far – no boost

                    confidence = base_confidence + proximity_boost

                    # Final safety cap for keyword confidence.
                    if confidence > 0.85:
                        confidence = 0.85

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = (pronunciation, keyword, confidence)

        return best_match

    def get_pronunciation_by_complex_pos_rules(
        self, word: str, token: "POSToken", dep_info: "DependencyInfo", doc: Any
    ) -> Optional[str]:
        """
        Generic data-driven evaluator for dependency rules.
        Reads dep_rules from JSON and evaluates them without hardcoded per-word logic.
        """
        word_lower = word.lower()
        if word_lower not in self.words:
            return None

        # First pass: check pronunciations with dep_rules
        for pronunciation, info in self.words[word_lower].items():
            dep_rules = info.get("dep_rules")
            if not dep_rules:
                continue  # skip default/fallback entries in first pass

            match_mode = info.get("match_mode", "all")
            results = [self._evaluate_dep_rule(r, word, token, dep_info, doc) for r in dep_rules]

            if (match_mode == "all" and all(results)) or (match_mode == "any" and any(results)):
                return pronunciation

        return None  # falls through to pos_tags lookup

    def _evaluate_dep_rule(self, rule: Dict, word: str, token: "POSToken", dep_info: "DependencyInfo", doc: Any) -> bool:
        """Evaluate a single dependency rule. Returns True if it matches."""
        rule_type = rule.get("type")
        word_lower = word.lower()

        if rule_type == "capitalized":
            return word[0].isupper() if word else False

        elif rule_type == "dep_relation":
            values = rule.get("values", [])
            return dep_info.dep_relation in values if dep_info else False

        elif rule_type == "pos_category":
            values = rule.get("values", [])
            return token.pos_category in values if token else False

        elif rule_type == "pos_tag":
            values = rule.get("values", [])
            return token.pos_tag in values if token else False

        elif rule_type == "prep_child":
            values = set(v.lower() for v in rule.get("values", []))
            for child_token in doc:
                if child_token.head.i == token.index and child_token.dep_ == "prep":
                    if child_token.text.lower() in values:
                        return True
            return False

        elif rule_type == "advmod_child":
            values = set(v.lower() for v in rule.get("values", []))
            for child_token in doc:
                if child_token.head.i == token.index and child_token.dep_ == "advmod":
                    if values and child_token.text.lower() not in values:
                        continue
                    return True
            return False

        elif rule_type == "cop_child":
            for child_token in doc:
                if child_token.head.i == token.index and child_token.dep_ == "cop":
                    return True
            return False

        elif rule_type == "prev_token":
            values = set(v.lower() for v in rule.get("values", []))
            if token and token.index > 0:
                prev_text = doc[token.index - 1].text.lower()
                return prev_text in values
            return False

        return False

    def get_pos_tags_for_option(self, word: str, pronunciation: str) -> List[str]:
        """
        Get all POS tags that map to a pronunciation.

        Args:
            word: The word
            pronunciation: The pronunciation option

        Returns:
            List of POS tags (e.g., ["VBD", "VBN"])
        """
        info = self.get_option_info(word, pronunciation)
        if info:
            return info.get("pos_tags", [])
        return []

    def _ensure_nlp(self):
        """Lazy load spaCy model for entity detection."""
        if self._nlp is None:
            try:
                import spacy

                self._nlp = spacy.load("en_core_web_trf")
            except Exception:
                # If spaCy not available, entity detection will be skipped
                self._nlp = False

    def check_entity_context(
        self, word: str, context_before: str, context_after: str
    ) -> Optional[Tuple[str, str]]:
        """
        Check if word appears in named entity context.

        This helps disambiguate cases like:
        - "Lead guitarist" (PERSON) → verb "leed"
        - "lead pipe" (OBJECT) → noun "led"
        - "Lead investigator" (PERSON/ROLE) → verb "leed"

        Args:
            word: The target word (e.g., "lead")
            context_before: Text before word
            context_after: Text after word

        Returns:
            Tuple of (pronunciation, explanation) or None if no entity signal

        Examples:
            "Lead" + "guitarist John" → ("leed", "Precedes PERSON entity")
            "lead" + "pipe made" → ("led", "Precedes object noun")
        """
        self._ensure_nlp()

        # If spaCy unavailable, skip entity detection
        if not self._nlp:
            return None

        word_lower = word.lower()

        # Only process words in our dictionary
        if not self.has_word(word):
            return None

        # Analyze context after the word (next 50 chars)
        doc = self._nlp(context_after[:50])

        if not doc or len(doc) == 0:
            return None

        first_token = doc[0]

        # Check for named entities
        if first_token.ent_type_:
            entity_type = first_token.ent_type_

            # PERSON, ORG, ROLE entities suggest action/verb meaning
            if entity_type in ("PERSON", "ORG", "GPE"):
                # "Lead guitarist" - lead is verb (to lead the band)
                if word_lower == "lead":
                    return (
                        "leed",
                        f"Precedes {entity_type} entity '{first_token.text}'",
                    )

                # "refuse collector" - refuse is noun (garbage)
                elif word_lower == "refuse":
                    # But PERSON can be ambiguous, check POS
                    if first_token.pos_ == "NOUN":
                        return ("refuse", f"Precedes role noun '{first_token.text}'")

        # Check POS of following word for additional signals
        if first_token.pos_ == "NOUN" and not first_token.ent_type_:
            # Following word is regular noun (not named entity)

            # "lead pipe" - lead is probably noun (the metal)
            if word_lower == "lead":
                return ("led", f"Precedes object noun '{first_token.text}'")

            # "refuse pile" - refuse is probably noun (garbage)
            elif word_lower == "refuse":
                return ("refuse", f"Precedes object noun '{first_token.text}'")

        # Check if word precedes a role/title word
        role_indicators = {
            "guitarist",
            "singer",
            "investigator",
            "developer",
            "engineer",
            "manager",
            "director",
            "officer",
            "scientist",
            "researcher",
        }

        first_word_lower = first_token.text.lower()
        if first_word_lower in role_indicators:
            # "Lead guitarist" - verb form
            if word_lower == "lead":
                return ("leed", f"Precedes role/title '{first_token.text}'")

        return None

    def add_context_keyword(self, word: str, pronunciation: str, keyword: str) -> bool:
        """
        Add a context keyword to a pronunciation option.

        Args:
            word: The word (e.g., "tear")
            pronunciation: The pronunciation option (e.g., "teer")
            keyword: The keyword to add (e.g., "through")

        Returns:
            True if keyword was added successfully
        """
        word_lower = word.lower()

        if word_lower not in self.words:
            return False

        if pronunciation not in self.words[word_lower]:
            return False

        info = self.words[word_lower][pronunciation]

        # Initialize context_keywords if it doesn't exist
        if "context_keywords" not in info:
            info["context_keywords"] = []

        # Add keyword if not already present (case-insensitive check)
        keyword_lower = keyword.lower()
        if not any(kw.lower() == keyword_lower for kw in info["context_keywords"]):
            info["context_keywords"].append(keyword)
            return True

        return False

    def remove_context_keyword(
        self, word: str, pronunciation: str, keyword: str
    ) -> bool:
        """
        Remove a context keyword from a pronunciation option.

        Args:
            word: The word (e.g., "tear")
            pronunciation: The pronunciation option (e.g., "teer")
            keyword: The keyword to remove

        Returns:
            True if keyword was removed successfully
        """
        word_lower = word.lower()

        if word_lower not in self.words:
            return False

        if pronunciation not in self.words[word_lower]:
            return False

        info = self.words[word_lower][pronunciation]

        if "context_keywords" not in info:
            return False

        # Remove keyword (case-insensitive match)
        keyword_lower = keyword.lower()
        initial_length = len(info["context_keywords"])
        info["context_keywords"] = [
            kw for kw in info["context_keywords"] if kw.lower() != keyword_lower
        ]

        return len(info["context_keywords"]) < initial_length

    def save_dictionary(self) -> bool:
        """
        Save dictionary changes back to JSON file.

        Returns:
            True if save was successful
        """
        try:
            with open(self.dictionary_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "version": "1.0",
                        "description": "POS-tagged pronunciation dictionary for heteronyms",
                        "created": (
                            self.dictionary_path.stat().st_mtime
                            if self.dictionary_path.exists()
                            else ""
                        ),
                        "words": self.words,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            return True
        except Exception as e:
            from ..logging import log_message

            log_message(f"Error saving POS dictionary: {e}", level="ERROR")
            return False

    def has_word(self, word: str) -> bool:
        """
        Check if a word exists in the dictionary.

        Args:
            word: The word to check

        Returns:
            True if word is in dictionary and not disabled
        """
        word_lower = word.lower()
        if word_lower not in self.words:
            return False
        return not self.words[word_lower].get("disabled", False)


# Global singleton
_pos_dictionary = None


def get_pos_dictionary() -> POSDictionary:
    """
    Get global POS dictionary instance (singleton).

    Returns:
        Shared POSDictionary instance
    """
    global _pos_dictionary
    if _pos_dictionary is None:
        _pos_dictionary = POSDictionary()
    return _pos_dictionary


def reset_pos_dictionary() -> None:
    """
    Reset the global POS dictionary singleton and reload from file.

    Use this when keywords have been edited and saved to ensure
    the program picks up the updated keyword definitions.
    """
    global _pos_dictionary
    if _pos_dictionary is not None:
        _pos_dictionary.reload()
    else:
        _pos_dictionary = POSDictionary()
    from ..logging import log_message

    log_message("POS dictionary reset and reloaded from file")
