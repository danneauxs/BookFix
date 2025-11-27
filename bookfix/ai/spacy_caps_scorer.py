"""
spaCy-based weighted scoring for caps word analysis.

Combines POS tagging and character patterns to score whether a caps word
should be kept (acronym) or lowercased (regular word/emphasis).
"""

import spacy
from typing import Optional, Tuple
from ..logging import log_message


class SpacyCapsScorer:
    """Score caps words using spaCy POS tagging and weighted signals."""

    # POS tag weights
    POS_WEIGHTS = {
        # Definitely lowercase (function words)
        "PRON": -3,  # pronouns: HE, SHE, WE, IT, etc.
        "ADP": -3,  # prepositions: IN, ON, BY, TO, AT, etc.
        "AUX": -3,  # auxiliaries: IS, ARE, HAVE, DO, etc.
        "INTJ": -3,  # interjections: OH, AH, etc.
        "CCONJ": -2,  # coordinating conjunctions: AND, BUT, OR, etc.
        "SCONJ": -2,  # subordinating conjunctions: IF, BECAUSE, etc.
        "DET": -2,  # determiners: THE, A, AN, etc.
        "VERB": -2,  # verbs: GO, RUN, ATTACK, etc. (unless context suggests acronym)
        "ADV": -2,  # adverbs
        # Could be either way
        "NOUN": +1,  # nouns: could be acronym or regular word
        "PROPN": +1,  # proper nouns: could be person/place/brand
        # Less common
        "ADJ": -1,  # adjectives: usually not acronyms
        "NUM": +1,  # numbers
    }

    CHARACTER_WEIGHTS = {
        "all_consonants": +2,  # FBI, CNN, BBC, etc.
        "two_three_letter": +1,  # base score for 2-3 letter words
        "high_vowels": -1,  # words with 60%+ vowels
        "long_word": -1,  # 4+ characters without clear pattern
    }

    def __init__(self):
        """Initialize spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            log_message("DEBUG: spaCy model loaded successfully")
        except OSError:
            log_message(
                "ERROR: spaCy model not found. Run: python -m spacy download en_core_web_sm"
            )
            self.nlp = None

    def score(
        self, word: str, context_before: str = "", context_after: str = ""
    ) -> Optional[Tuple[float, float, str, str]]:
        """
        Score a caps word using weighted signals.

        Args:
            word: The capitalized word to score
            context_before: Text before the word
            context_after: Text after the word

        Returns:
            Tuple of (score, confidence, reasoning, pos_tag) or None if error
            - score: negative = lowercase, positive = keep uppercase
            - confidence: 0.0 to 1.0
            - reasoning: explanation of score
            - pos_tag: spaCy's POS tag
        """
        if not self.nlp:
            return None

        try:
            # Get POS tag from spaCy - use lowercase version for better tagging
            lowercase_word = word.lower()
            full_context = f"{context_before} {lowercase_word} {context_after}"
            doc = self.nlp(full_context)

            # Find the word in the parsed context
            pos_tag = None
            for token in doc:
                if token.text.lower() == lowercase_word:
                    pos_tag = token.pos_
                    break

            log_message(f"DEBUG: spaCy POS for '{word}': {pos_tag}")

            # Start with POS weight
            score = 0.0
            signals = []

            if pos_tag and pos_tag in self.POS_WEIGHTS:
                pos_weight = self.POS_WEIGHTS[pos_tag]
                score += pos_weight
                signals.append(f"{pos_tag}({pos_weight:+.1f})")
            elif pos_tag:
                # Unknown POS tag, neutral
                signals.append(f"{pos_tag}(0)")

            # Add character pattern signals
            word_len = len(word)
            vowel_count = sum(1 for c in word if c in "AEIOUY")

            if word_len == 2 or word_len == 3:
                score += self.CHARACTER_WEIGHTS["two_three_letter"]
                signals.append(f"2-3-letter(+1.0)")

            if vowel_count == 0 and word_len >= 2:
                # All consonants
                score += self.CHARACTER_WEIGHTS["all_consonants"]
                signals.append(f"all-consonants(+2.0)")
            elif word_len > 3 and vowel_count >= word_len * 0.6:
                # High vowel ratio in 4+ letter word
                score += self.CHARACTER_WEIGHTS["high_vowels"]
                vowel_ratio = vowel_count / word_len
                signals.append(f"high-vowels({vowel_ratio:.1%}, -1.0)")

            # Determine confidence based on score magnitude
            abs_score = abs(score)
            if abs_score >= 3:
                confidence = 0.95
            elif abs_score >= 2:
                confidence = 0.85
            elif abs_score >= 1:
                confidence = 0.75
            else:
                confidence = 0.60

            reasoning = f"spaCy: {' + '.join(signals)} = {score:.1f}"
            log_message(
                f"DEBUG: Score for '{word}': {score:.1f} (conf: {confidence:.2f})"
            )

            return (score, confidence, reasoning, pos_tag if pos_tag else "UNKNOWN")

        except Exception as e:
            log_message(f"ERROR: spaCy scoring failed for '{word}': {e}")
            return None

    def decide(
        self, word: str, context_before: str = "", context_after: str = ""
    ) -> Optional[Tuple[str, float, str]]:
        """
        Make a decision based on score.

        Args:
            word: The capitalized word
            context_before: Text before the word
            context_after: Text after the word

        Returns:
            Tuple of (decision, confidence, reasoning) where:
            - decision: 'keep', 'lowercase', or None (ambiguous)
            - confidence: 0.0 to 1.0
            - reasoning: explanation
        """
        result = self.score(word, context_before, context_after)
        if not result:
            return None

        score, confidence, reasoning, pos_tag = result

        # Decision thresholds
        if score < -1.0:
            decision = "lowercase"
        elif score > 1.0:
            decision = "keep"
        else:
            # Ambiguous - return None to let caller decide (or send to AI)
            decision = None

        return (decision, confidence, reasoning)
