"""
POS Tagging Service for Bookfix AI.

Provides Part-of-Speech tagging using spaCy for grammar-aware text processing.
"""

import spacy
import spacy.tokens.doc
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class POSToken:
    """Token with POS information."""

    text: str
    pos_tag: str  # Fine-grained tag (VBN, VBP, NN, etc.)
    pos_category: str  # Coarse tag (VERB, NOUN, etc.)
    index: int  # Position in sentence


@dataclass
class DependencyInfo:
    """Dependency parsing information for a token."""

    word: str
    dep_relation: str  # Dependency relation (dobj, nsubj, ROOT, etc.)
    head_word: str  # Syntactic parent word
    head_pos: str  # POS tag of head
    head_dep: str  # Dependency of head
    children: List[str] = field(default_factory=list)  # Child tokens
    entity_type: Optional[str] = None  # Named entity type if applicable


class POSTaggerService:
    """
    Shared POS tagging service using spaCy.

    Provides grammar analysis for AI modules to make more accurate decisions.
    """

    def __init__(self, model_name: str = "en_core_web_trf"):
        """
        Initialize POS tagger with spaCy model.

        Args:
            model_name: Name of spaCy model to load (default: en_core_web_trf)
        """
        try:
            self.nlp = spacy.load(model_name)
            self.model_name = model_name
        except OSError:
            raise RuntimeError(
                f"spaCy model '{model_name}' not found. "
                f"Install with: python -m spacy download {model_name}"
            )

    def tag_text(self, text: str) -> List[POSToken]:
        """
        Tag all tokens in text with POS information.

        Args:
            text: Text to analyze

        Returns:
            List of POSToken objects with POS information
        """
        doc = self.nlp(text)

        tokens = []
        for i, token in enumerate(doc):
            tokens.append(
                POSToken(
                    text=token.text,
                    pos_tag=token.tag_,  # Fine-grained: VBN, VBP, NN, etc.
                    pos_category=token.pos_,  # Coarse: VERB, NOUN, etc.
                    index=i,
                )
            )

        return tokens

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

        # Calculate approximate word position
        words_before = len(context_before.split())

        return self.get_word_tag(full_text, word, word_position=words_before)

    def detect_phrasal_verb(
        self, context_before: str, word: str, context_after: str
    ) -> bool:
        """
        Detect if word is part of a phrasal verb (like "wound up", "tear apart").

        Phrasal verbs are verb + particle combinations where the meaning differs
        from the individual words.

        Args:
            context_before: Text before the target word
            word: Target word (e.g., "wound")
            context_after: Text after the target word (should contain particle like "up")

        Returns:
            True if this appears to be a phrasal verb
        """
        # Common particles that form phrasal verbs
        particles = {
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "away",
            "back",
            "over",
            "through",
            "around",
            "apart",
            "aside",
            "along",
        }

        # Reconstruct full text
        full_text = f"{context_before} {word} {context_after}"
        doc = self.nlp(full_text)

        # Find the target word token
        words_before = len(context_before.split())

        for i, token in enumerate(doc):
            if token.text.lower() == word.lower() and i == words_before:
                # Check if next token is a particle
                if i + 1 < len(doc):
                    next_token = doc[i + 1]
                    next_word = next_token.text.lower()

                    # Check if next word is a particle
                    if next_word in particles:
                        # Additional check: ensure next token is tagged as particle (RP) or preposition (IN)
                        if next_token.tag_ in ["RP", "IN"] or next_token.pos_ in [
                            "ADP",
                            "PART",
                        ]:
                            return True

                break

        return False

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
            # Pronouns
            "PRP": "personal pronoun",
            "PRP$": "possessive pronoun",
            "WP": "wh-pronoun",
            "WP$": "possessive wh-pronoun",
            # Determiners
            "DT": "determiner",
            "PDT": "predeterminer",
            "WDT": "wh-determiner",
            # Numbers
            "CD": "cardinal number",
            # Other
            "IN": "preposition/subordinating conjunction",
            "CC": "coordinating conjunction",
            "TO": "to",
            "UH": "interjection",
            "MD": "modal",
            "EX": "existential there",
            "RP": "particle",
            "POS": "possessive ending",
        }

        return explanations.get(pos_tag, pos_tag)

    def get_tag_category(self, pos_tag: str) -> str:
        """
        Get general category for a POS tag.

        Args:
            pos_tag: Fine-grained POS tag

        Returns:
            Category: verb, noun, adjective, etc.
        """
        if pos_tag.startswith("VB"):
            return "verb"
        elif pos_tag.startswith("NN"):
            return "noun"
        elif pos_tag.startswith("JJ"):
            return "adjective"
        elif pos_tag.startswith("RB"):
            return "adverb"
        elif pos_tag in ["PRP", "PRP$", "WP", "WP$"]:
            return "pronoun"
        elif pos_tag in ["DT", "PDT", "WDT"]:
            return "determiner"
        elif pos_tag == "CD":
            return "number"
        elif pos_tag in ["IN", "CC", "TO"]:
            return "conjunction/preposition"
        else:
            return "other"

    def get_dependency_info(
        self, context_before: str, word: str, context_after: str
    ) -> Optional[DependencyInfo]:
        """
        Get dependency parsing information for word in context.

        Provides syntactic relationships:
        - Dependency relation (dobj, nsubj, ROOT, etc.)
        - Head word (syntactic parent)
        - Children (syntactic dependents)
        - Named entity type

        Args:
            context_before: Text before the target word
            word: Target word to analyze
            context_after: Text after the target word

        Returns:
            DependencyInfo object with syntactic information, or None if word not found

        Examples:
            "I read the book"
            - read: dep=ROOT, head=read (itself), children=[I, book]
            - book: dep=dobj, head=read, children=[the]

            "The book I read was good"
            - read: dep=relcl, head=book, children=[I]
        """
        # Reconstruct full sentence
        full_text = f"{context_before} {word} {context_after}"
        doc = self.nlp(full_text)

        # Find target word token
        words_before = len(context_before.split())
        target_token = None

        for i, token in enumerate(doc):
            if token.text.lower() == word.lower() and i == words_before:
                target_token = token
                break

        if not target_token:
            return None

        # Extract dependency information
        return DependencyInfo(
            word=target_token.text,
            dep_relation=target_token.dep_,
            head_word=target_token.head.text,
            head_pos=target_token.head.tag_,
            head_dep=target_token.head.dep_,
            children=[child.text for child in target_token.children],
            entity_type=target_token.ent_type_ if target_token.ent_type_ else None,
        )

    def get_token_and_dependency(
        self, context_before: str, word: str, context_after: str
    ) -> Tuple[
        Optional[POSToken], Optional[DependencyInfo], Optional[spacy.tokens.doc.Doc]
    ]:
        """
        Get the POSToken, DependencyInfo, and full spaCy Doc for a target word in context.

        Args:
            context_before: Text before the target word
            word: Target word to analyze
            context_after: Text after the target word

        Returns:
            Tuple of (POSToken, DependencyInfo, spaCy.Doc) or (None, None, None) if word not found
        """
        full_text = f"{context_before} {word} {context_after}"
        doc = self.nlp(full_text)

        # Find target word token using character position (spaCy's token.idx)
        # This is reliable even with punctuation, contractions, and newlines
        word_char_start = len(context_before) + 1  # +1 for the space we added
        word_char_end = word_char_start + len(word)

        target_token = None

        # Method 1: Find token by character position overlap
        for token in doc:
            # Check if token overlaps with expected character range
            if token.idx <= word_char_start < token.idx + len(token.text):
                if token.text.lower() == word.lower():
                    target_token = token
                    break

        # Method 2: Fallback - search by text match near expected position
        if not target_token:
            # Try tokens in a small window around expected position
            for token in doc:
                if abs(token.idx - word_char_start) < 50:  # Within 50 chars
                    if token.text.lower() == word.lower():
                        target_token = token
                        break

        # Method 3: Last resort - linear search through all tokens
        if not target_token:
            for token in doc:
                if token.text.lower() == word.lower():
                    target_token = token
                    break

        if not target_token:
            return None, None, None

        pos_token = POSToken(
            text=target_token.text,
            pos_tag=target_token.tag_,
            pos_category=target_token.pos_,
            index=target_token.i,
        )

        dep_info = DependencyInfo(
            word=target_token.text,
            dep_relation=target_token.dep_,
            head_word=target_token.head.text,
            head_pos=target_token.head.tag_,
            head_dep=target_token.head.dep_,
            children=[child.text for child in target_token.children],
            entity_type=target_token.ent_type_ if target_token.ent_type_ else None,
        )

        return pos_token, dep_info, doc

    def get_syntactic_confidence(self, dep_info: DependencyInfo, pos_tag: str) -> float:
        """
        Calculate confidence boost based on syntactic clarity.

        Strong syntactic signals indicate clear grammatical role:
        - Direct object (dobj) → clearly a verb
        - Subject (nsubj) → clearly a verb's subject
        - Modifier relationships → clear noun/adjective usage

        Args:
            dep_info: Dependency information
            pos_tag: POS tag of the word

        Returns:
            Confidence boost (0.0 to 0.1) - add to base confidence

        Examples:
            dobj with VBD tag → +0.08 (very clear past verb usage)
            nsubj with NN tag → +0.06 (clear noun as subject)
            ROOT with VB tag → +0.05 (clear main verb)
        """
        if not dep_info:
            return 0.0

        dep = dep_info.dep_relation
        boost = 0.0

        # Direct object - very clear verb signal
        if dep == "dobj":
            if pos_tag.startswith("VB"):
                boost = 0.08  # "I read the book" - read is clearly verb

        # Subject - clear noun signal
        elif dep in ("nsubj", "nsubjpass"):
            if pos_tag.startswith("NN"):
                boost = 0.06  # "The book was read" - book is clearly noun

        # Main verb (ROOT)
        elif dep == "ROOT":
            if pos_tag.startswith("VB"):
                boost = 0.05  # Main verb of sentence

        # Object of preposition - clear noun signal
        elif dep == "pobj":
            if pos_tag.startswith("NN"):
                boost = 0.07  # "made of lead" - lead is clearly noun

        # Attributive modifier - clear adjective/noun signal
        elif dep == "amod":
            if pos_tag.startswith("JJ"):
                boost = 0.06  # Modifying noun

        # Compound - clear noun signal
        elif dep == "compound":
            if pos_tag.startswith("NN"):
                boost = 0.05  # "lead pipe" - lead is compound noun

        # Consider head word for additional context
        if dep_info.head_pos and boost > 0:
            # If head is auxiliary, strengthen verb signal
            if dep_info.head_pos == "MD" and pos_tag.startswith("VB"):
                boost += 0.02  # "can read" - read must be verb

            # If head is preposition and we're object, strengthen noun
            if dep_info.head_pos == "IN" and dep == "pobj":
                boost += 0.02  # "of lead" - lead must be noun

        return min(0.10, boost)  # Cap at 0.10 boost


# Global singleton instance (lazy loaded)
_pos_tagger = None


def get_pos_tagger() -> POSTaggerService:
    """
    Get global POS tagger instance (singleton pattern).

    Returns:
        Shared POSTaggerService instance
    """
    global _pos_tagger
    if _pos_tagger is None:
        _pos_tagger = POSTaggerService()
    return _pos_tagger
