"""
BERT-based POS Tagging Service for Bookfix AI.

Provides Part-of-Speech tagging using BERT transformers for better accuracy
on homograph disambiguation compared to spaCy.
"""

from transformers import pipeline
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# Reuse the same dataclasses from pos_tagger for compatibility
from .pos_tagger import POSToken, DependencyInfo


class BERTPOSTaggerService:
    """
    BERT-based POS tagging service using Hugging Face transformers.

    Provides the same interface as POSTaggerService but uses BERT
    for more accurate contextual POS tagging.
    """

    def __init__(self, model_name: str = "vblagoje/bert-english-uncased-finetuned-pos"):
        """
        Initialize BERT POS tagger.

        Args:
            model_name: Hugging Face model ID for POS tagging
        """
        try:
            # Load BERT model for token classification (POS tagging)
            self.nlp = pipeline(
                "token-classification",
                model=model_name,
                aggregation_strategy="simple",  # Aggregate subword tokens
            )
            self.model_name = model_name
        except Exception as e:
            raise RuntimeError(
                f"Failed to load BERT model '{model_name}': {e}\n"
                f"Install with: pip install transformers torch"
            )

    def tag_text(self, text: str) -> List[POSToken]:
        """
        Tag all tokens in text with POS information using BERT.

        Args:
            text: Text to analyze

        Returns:
            List of POSToken objects with POS information
        """
        # Get BERT predictions
        results = self.nlp(text)

        tokens = []
        for i, result in enumerate(results):
            # BERT returns entity_group which is the POS tag
            pos_tag = result["entity_group"]

            tokens.append(
                POSToken(
                    text=result["word"],
                    pos_tag=pos_tag,  # Fine-grained: VBN, VBP, NN, etc.
                    pos_category=self._get_pos_category(
                        pos_tag
                    ),  # Coarse: VERB, NOUN, etc.
                    index=i,
                )
            )

        return tokens

    def _get_pos_category(self, pos_tag: str) -> str:
        """
        Convert BERT's Universal POS tag to coarse category.

        BERT returns Universal POS tags (NOUN, VERB, ADJ, etc.), not Penn Treebank tags.
        Most can be returned as-is, with a few mappings for compatibility.

        Args:
            pos_tag: Universal POS tag from BERT (e.g., "NOUN", "VERB", "ADJ")

        Returns:
            Coarse category (e.g., "VERB", "NOUN", "ADJ")
        """
        # BERT uses Universal POS tags - most map directly
        if pos_tag in ["NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "NUM"]:
            return pos_tag

        # Special mappings for BERT's Universal tags
        elif pos_tag == "AUX":  # Auxiliary verb (have, be, etc.)
            return "VERB"
        elif pos_tag == "ADP":  # Adposition (preposition)
            return "ADP"
        elif (
            pos_tag == "CCONJ" or pos_tag == "SCONJ"
        ):  # Coordinating/subordinating conjunction
            return "CONJ"
        elif pos_tag == "PUNCT":  # Punctuation
            return "PUNCT"
        elif pos_tag == "PROPN":  # Proper noun
            return "NOUN"
        elif pos_tag == "PART":  # Particle
            return "PART"
        elif pos_tag == "INTJ":  # Interjection
            return "INTJ"
        elif pos_tag == "SYM" or pos_tag == "X":  # Symbol or other
            return "OTHER"
        else:
            return "OTHER"

    def get_word_tag(self, text: str, word: str, word_position: int = None) -> str:
        """
        Get POS tag for a specific word in context.

        Args:
            text: Full text context
            word: Word to get tag for
            word_position: Optional position hint (index in text)

        Returns:
            Fine-grained POS tag (VBN, NN, etc.) or empty string if not found
        """
        tokens = self.tag_text(text)

        # If position hint provided, check that token first
        if word_position is not None and 0 <= word_position < len(tokens):
            token = tokens[word_position]
            if token.text.lower() == word.lower():
                return token.pos_tag

        # Otherwise search for word in tokens
        for token in tokens:
            if token.text.lower() == word.lower():
                return token.pos_tag

        return ""

    def tag_with_context(
        self, context_before: str, word: str, context_after: str
    ) -> str:
        """
        Get POS tag for word given before/after context.

        Args:
            context_before: Text before the target word
            context_after: Text after the target word
            word: Target word to tag

        Returns:
            Fine-grained POS tag (VBN, NN, etc.)
        """
        # Reconstruct full sentence
        full_text = f"{context_before} {word} {context_after}"

        # Use BERT to tag the full context
        results = self.nlp(full_text)

        # Find the target word in BERT's output
        # BERT may split words into subwords, so we need to find the right token
        target_word_lower = word.lower()

        for result in results:
            # Check if this token matches our target word
            # Handle subword tokens (they start with ##)
            token_text = result["word"].replace("##", "").lower()
            if token_text == target_word_lower or target_word_lower in token_text:
                return result["entity_group"]

        # Fallback: if not found in results, try full text tagging
        return self.get_word_tag(full_text, word)

    def get_token_and_dependency(
        self, context_before: str, word: str, context_after: str
    ) -> Tuple[Optional[POSToken], Optional[DependencyInfo], Optional[object]]:
        """
        Get the POSToken, DependencyInfo, and full doc for a target word in context.

        Note: BERT doesn't provide dependency parsing, so dep_info will be minimal.
        This method exists for compatibility with spaCy's interface.

        Args:
            context_before: Text before the target word
            word: Target word to analyze
            context_after: Text after the target word

        Returns:
            Tuple of (POSToken, None, None) - dependency parsing not available with BERT
        """
        # Reconstruct full text
        full_text = f"{context_before} {word} {context_after}"

        # Get BERT predictions
        results = self.nlp(full_text)

        # Find target word
        target_word_lower = word.lower()
        target_token = None

        for i, result in enumerate(results):
            token_text = result["word"].replace("##", "").lower()
            if token_text == target_word_lower or target_word_lower in token_text:
                pos_tag = result["entity_group"]
                target_token = POSToken(
                    text=result["word"],
                    pos_tag=pos_tag,
                    pos_category=self._get_pos_category(pos_tag),
                    index=i,
                )
                break

        if not target_token:
            return None, None, None

        # Create minimal DependencyInfo (BERT doesn't do dependency parsing)
        dep_info = DependencyInfo(
            word=target_token.text,
            dep_relation="unknown",  # BERT doesn't provide this
            head_word="unknown",
            head_pos="unknown",
            head_dep="unknown",
            children=[],
            entity_type=None,
        )

        # Return token, dep_info, and None for doc (BERT doesn't have a doc object)
        return target_token, dep_info, None

    def explain_tag(self, pos_tag: str) -> str:
        """
        Get human-readable explanation of POS tag.

        Args:
            pos_tag: POS tag to explain (e.g., "VBN", "NN")

        Returns:
            Human-readable description
        """
        explanations = {
            # Verbs
            "VB": "verb, base form",
            "VBD": "verb, past tense",
            "VBG": "verb, gerund/present participle",
            "VBN": "verb, past participle",
            "VBP": "verb, non-3rd person singular present",
            "VBZ": "verb, 3rd person singular present",
            # Nouns
            "NN": "noun, singular",
            "NNS": "noun, plural",
            "NNP": "proper noun, singular",
            "NNPS": "proper noun, plural",
            # Adjectives
            "JJ": "adjective",
            "JJR": "adjective, comparative",
            "JJS": "adjective, superlative",
            # Adverbs
            "RB": "adverb",
            "RBR": "adverb, comparative",
            "RBS": "adverb, superlative",
            # Other
            "IN": "preposition/subordinating conjunction",
            "CC": "coordinating conjunction",
            "TO": "to",
            "MD": "modal",
            "CD": "cardinal number",
        }

        return explanations.get(pos_tag, pos_tag)


# Global singleton instance (lazy loaded)
_bert_tagger = None


def get_bert_tagger() -> BERTPOSTaggerService:
    """
    Get global BERT POS tagger instance (singleton pattern).

    Returns:
        Shared BERTPOSTaggerService instance
    """
    global _bert_tagger
    if _bert_tagger is None:
        _bert_tagger = BERTPOSTaggerService()
    return _bert_tagger
