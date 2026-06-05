"""
AI Learning Data Storage for Bookfix Choices (Homograph) Processing.

Stores user decisions for homograph disambiguation to improve AI suggestions over time.
Cross-AI compatible format that survives model changes.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from ..logging import log_message


@dataclass
class ChoiceLearningEntry:
    """Single learning entry capturing user's homograph choice."""

    timestamp: str
    original_word: str  # The homograph (e.g., "lead")
    lemma: str  # Base form (e.g., "lead" for "leading", "leads")
    options: List[str]  # Available choices (e.g., ["leed", "led"])
    context_before: str  # 50 chars before
    context_after: str  # 50 chars after
    user_choice: str  # What user selected (e.g., "leed")
    confidence_score: float  # How confident user was (future use)
    line_number: int  # Line in document
    pos_tag: str = ""  # POS tag from spaCy (e.g., "VBN", "NN")
    dep_info: Optional[Dict] = (
        None  # Dependency info (e.g., {'dep': 'dobj', 'head_lemma': 'mine', 'syntactic_confidence': 0.08})
    )
    window_features: Optional[Dict] = (
        None  # {'left_words': list, 'right_words': list, 'top_noun': str, 'top_verb': str}
    )

    @classmethod
    def create(
        cls,
        original_word: str,
        lemma: str,
        options: List[str],
        context_before: str,
        context_after: str,
        user_choice: str,
        line_number: int,
        pos_tag: str = "",
        dep_info: Optional[Dict] = None,
        window_features: Optional[Dict] = None,
    ) -> "ChoiceLearningEntry":
        """Create a new learning entry with current timestamp."""
        return cls(
            timestamp=datetime.now().isoformat(),
            original_word=original_word,
            lemma=lemma,
            options=options,
            context_before=context_before,
            context_after=context_after,
            user_choice=user_choice,
            confidence_score=1.0,  # Default full confidence
            line_number=line_number,
            pos_tag=pos_tag,
            dep_info=dep_info,
            window_features=window_features,
        )


@dataclass
class ChoicePattern:
    """Extracted pattern from user's homograph choices."""

    word: str  # The homograph word
    preferred_choice: str  # User's typical choice in this context
    context_indicators: List[str]  # Words that indicate this choice
    pattern_type: str  # "context_words", "position", "sentence_type", "dependency", "weighted_keywords"
    confidence: float  # 0.0 to 1.0 based on consistency
    usage_count: int  # How many times observed
    last_used: str  # Last timestamp
    dep_rules: Optional[List[Dict]] = (
        None  # e.g., [{'dep': 'dobj', 'head_lemma': 'mine', 'choice': 'led'}]
    )
    context_weights: Optional[Dict[str, float]] = (
        None  # e.g., {'pencil': 5.0, 'guide': 4.0}
    )

    def update_usage(self, choice: str) -> None:
        """Update pattern usage and confidence."""
        self.usage_count += 1
        self.last_used = datetime.now().isoformat()

        if choice == self.preferred_choice:
            # Reinforcement - increase confidence
            self.confidence = min(0.95, self.confidence + 0.05)
        else:
            # Contradiction - decrease confidence
            self.confidence = max(0.1, self.confidence - 0.1)


class ChoicesLearningStorage:
    """Manages storage and retrieval of choices learning data."""

    def __init__(self, storage_dir: str = None):
        """Initialize choices learning storage."""
        if storage_dir is None:
            # Default to main app directory
            app_dir = Path(__file__).parent.parent.parent
            storage_dir = app_dir / ".ai_learning"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.entries_file = self.storage_dir / "choices_learning.json"
        self.patterns_file = self.storage_dir / "choices_patterns.json"

        # Load existing data
        self.entries: List[ChoiceLearningEntry] = self._load_entries()
        self.patterns: List[ChoicePattern] = self._load_patterns()

        # Lazy load spaCy for lemmatization
        self._nlp = None

    def _ensure_nlp(self):
        """Lazy load spaCy model for lemmatization."""
        if self._nlp is None:
            try:
                import spacy

                self._nlp = spacy.load("en_core_web_sm")
            except Exception:
                # If spaCy not available, lemmatization will use original word
                self._nlp = False

    def _get_lemma(self, word: str) -> str:
        """
        Get lemma (base form) of a word.

        Examples:
            "reading" → "read"
            "leads" → "lead"
            "refused" → "refuse"

        Args:
            word: Word to lemmatize

        Returns:
            Lemma (base form) or original word if lemmatization unavailable
        """
        self._ensure_nlp()

        if not self._nlp:
            return word.lower()

        doc = self._nlp(word)
        if doc and len(doc) > 0:
            return doc[0].lemma_.lower()

        return word.lower()

    def _load_entries(self) -> List[ChoiceLearningEntry]:
        """Load learning entries from file."""
        if not self.entries_file.exists():
            return []

        try:
            with open(self.entries_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            entries = []
            for entry_dict in data.get("entries", []):
                # Backwards compatibility: add lemma if missing
                if "lemma" not in entry_dict:
                    entry_dict["lemma"] = entry_dict.get("original_word", "").lower()
                # Backwards compatibility: add dep_info if missing
                if "dep_info" not in entry_dict:
                    entry_dict["dep_info"] = None
                # Backwards compatibility: add window_features if missing
                if "window_features" not in entry_dict:
                    entry_dict["window_features"] = None

                entries.append(ChoiceLearningEntry(**entry_dict))

            log_message(f"Loaded {len(entries)} choice learning entries")
            return entries

        except Exception as e:
            log_message(f"Error loading choice learning entries: {e}", level="ERROR")
            return []

    def _load_patterns(self) -> List[ChoicePattern]:
        """Load learned patterns from file."""
        if not self.patterns_file.exists():
            return []

        try:
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            patterns = []
            for pattern_dict in data.get("patterns", []):
                patterns.append(ChoicePattern(**pattern_dict))

            log_message(f"Loaded {len(patterns)} choice patterns")
            return patterns

        except Exception as e:
            log_message(f"Error loading choice patterns: {e}", level="ERROR")
            return []

    def save_entries(self):
        """Save learning entries to file."""
        try:
            log_message(f"save_entries: Writing {len(self.entries)} entries to {self.entries_file}")
            data = {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "entries": [asdict(entry) for entry in self.entries],
            }

            with open(self.entries_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            log_message(f"save_entries: Successfully saved {len(self.entries)} entries")
            log_message(f"Saved {len(self.entries)} choice learning entries")

        except Exception as e:
            log_message(f"Error saving choice learning entries: {e}", level="ERROR")

    def save_patterns(self):
        """Save learned patterns to file."""
        try:
            data = {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "patterns": [asdict(pattern) for pattern in self.patterns],
            }

            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            log_message(f"Saved {len(self.patterns)} choice patterns")

        except Exception as e:
            log_message(f"Error saving choice patterns: {e}", level="ERROR")

    def add_learning_entry(self, entry: ChoiceLearningEntry):
        """Add a new learning entry and save."""
        self.entries.append(entry)
        self.save_entries()
        log_message(
            f"Added learning entry: '{entry.original_word}' → '{entry.user_choice}'"
        )

    def get_patterns_for_word(self, word: str) -> List[ChoicePattern]:
        """Get all learned patterns for a specific word."""
        return [p for p in self.patterns if p.word.lower() == word.lower()]

    def get_best_suggestion(
        self, word: str, context: str
    ) -> Optional[Tuple[str, float]]:
        """
        Get the best suggestion for a word based on learned patterns.

        Now uses lemma matching to generalize across word forms.
        "reading" will match patterns learned from "read", "reads", "reader", etc.

        Returns:
            Tuple of (suggested_choice, confidence) or None if no pattern matches
        """
        from .pos_tagger import get_pos_tagger
        from collections import Counter

        # Get lemma for word
        lemma = self._get_lemma(word)

        # Layer 1: Dependency Parsing Rules (strongest syntactic signals first)
        pos_tagger = get_pos_tagger()
        # Reconstruct context for dep parsing (assume full context available; if not, use provided)
        full_context = f"{context} {word} {context}"  # Simplified; in practice, use before/after if available
        dep_info = pos_tagger.get_dependency_info(
            context, word, context
        )  # Use symmetric context

        if dep_info:
            syntactic_conf = pos_tagger.get_syntactic_confidence(
                dep_info, self._get_pos_from_context(pos_tagger, full_context, word)
            )
            # Simple dep rules for common homographs (expand based on config words)
            dep_rules = self._get_dep_rules_for_word(word.lower())
            for rule in dep_rules:
                if (
                    dep_info.dep_relation == rule["dep"]
                    and self._get_lemma(dep_info.head_word) == rule["head_lemma"]
                ):
                    # High confidence syntactic match
                    choice = rule["preferred_choice"]
                    total_conf = min(1.0, syntactic_conf + 0.2)  # Base + dep boost
                    log_message(
                        f"Dep rule match for '{word}': {dep_info.dep_relation} under '{dep_info.head_word}' → '{choice}' (conf {total_conf})"
                    )
                    return (choice, total_conf)

        # Find patterns matching either exact word or lemma (fallback to keywords if no dep match)
        patterns = []

        # First try exact word match
        patterns.extend(self.get_patterns_for_word(word))

        # Then try lemma match (if different from word)
        if lemma != word.lower():
            patterns.extend(self.get_patterns_for_word(lemma))

        if not patterns:
            return None

        # Layer 2: Weighted Keyword Scoring (enhanced with syntactic boost if available)
        best_match = None
        best_score = 0.0
        dep_boost = syntactic_conf if dep_info else 0.0

        for pattern in patterns:
            if pattern.context_weights:
                # Tally weights in context window (150-char approx)
                context_lower = context.lower()
                weight_sum = 0.0
                match_count = 0
                for indicator, w in pattern.context_weights.items():
                    if indicator.lower() in context_lower:
                        weight_sum += w
                        match_count += 1

                if match_count > 0:
                    # Score: average weight * confidence + dep boost
                    base_score = (weight_sum / match_count) * pattern.confidence
                    score = base_score + dep_boost

                    if score > best_score:
                        best_score = score
                        best_match = pattern
            else:
                # Fallback to unweighted (existing logic)
                context_lower = context.lower()
                indicator_matches = sum(
                    1
                    for indicator in pattern.context_indicators
                    if indicator.lower() in context_lower
                )

                if indicator_matches > 0:
                    # Calculate score: (matches * confidence) / total_indicators + dep boost
                    base_score = (indicator_matches * pattern.confidence) / len(
                        pattern.context_indicators
                    )
                    score = base_score + dep_boost

                    if score > best_score:
                        best_score = score
                        best_match = pattern

        if best_match and best_score > 0.6:  # Raised threshold for weights
            return (best_match.preferred_choice, best_match.confidence + dep_boost)

        return None

    def _get_pos_from_context(self, pos_tagger, full_context: str, word: str) -> str:
        """Helper to get POS tag from context."""
        return pos_tagger.get_word_tag(full_context, word)

    def _get_dep_rules_for_word(self, word_lower: str) -> List[Dict]:
        """Get predefined or learned dep rules for a word (Layer 1)."""
        # Initial hardcoded rules for common homographs; expand with learned dep_rules from patterns
        rules = {
            "lead": [
                {
                    "dep": "dobj",
                    "head_lemma": "mine",
                    "preferred_choice": "led",
                },  # Noun (metal)
                {
                    "dep": "pobj",
                    "head_lemma": "of",
                    "preferred_choice": "led",
                },  # "made of lead"
                {
                    "dep": "ROOT",
                    "head_lemma": "lead",
                    "preferred_choice": "leed",
                },  # Verb base
                # Add more based on config (e.g., from ctx.choices keys)
            ],
            "read": [
                {
                    "dep": "VBD",
                    "head_lemma": "read",
                    "preferred_choice": "red",
                },  # Past tense
                {
                    "dep": "VB",
                    "head_lemma": "read",
                    "preferred_choice": "reed",
                },  # Present
            ],
            # Expand for other words like 'bass', 'tear', etc.
        }.get(word_lower, [])

        # Merge with learned dep_rules from patterns
        for pattern in self.patterns:
            if pattern.word.lower() == word_lower and pattern.dep_rules:
                rules.extend(pattern.dep_rules)

        return rules

    def get_learning_stats(self) -> Dict:
        """Get statistics about learning data."""
        words_learned = set(entry.original_word for entry in self.entries)

        return {
            "total_entries": len(self.entries),
            "total_patterns": len(self.patterns),
            "words_learned": len(words_learned),
            "words_list": sorted(words_learned),
        }


class ChoicesLearningAnalyzer:
    """Analyzes user decisions to extract patterns for choices."""

    def __init__(self, storage: ChoicesLearningStorage):
        """Initialize a new instance of ChoicePatternExtractor.
        Args:
        storage (ChoicesLearningStorage): The storage for learning entries.
        Returns:
        None
        """
        self.storage = storage
        self._patterns: List = []

    def _extract_patterns_for_word(self, word: str, entries: List["ChoiceLearningEntry"]) -> List["ChoicePattern"]:
        """Extract ChoicePattern objects for a word from learning entries."""
        if not entries:
            return []

        from collections import Counter

        STOPWORDS = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'to', 'of', 'in',
            'and', 'or', 'for', 'with', 'at', 'by', 'it', 'its', 'his', 'her',
            'their', 'they', 'this', 'that', 'we', 'he', 'she', 'you', 'i',
            'has', 'have', 'had', 'not', 'no', 'so', 'but', 'as', 'if', 'on',
            'before', 'after', 'during', 'while', 'from', 'into', 'about',
        }

        # Group entries by user_choice
        by_choice: Dict[str, List] = {}
        for entry in entries:
            by_choice.setdefault(entry.user_choice, []).append(entry)

        patterns = []
        for choice, choice_entries in by_choice.items():
            all_words = []
            dep_rules = []

            word_lower = word.lower()
            for entry in choice_entries:
                for text in [entry.context_before, entry.context_after]:
                    for w in text.lower().split():
                        w = w.strip('.,;:!?"\'()-')
                        if len(w) >= 3 and w not in STOPWORDS and w != word_lower:
                            all_words.append(w)

                if entry.dep_info and entry.dep_info.get('dep_relation'):
                    rule = {
                        'dep': entry.dep_info['dep_relation'],
                        'head_lemma': entry.dep_info.get('head_lemma', ''),
                        'choice': choice,
                    }
                    if rule not in dep_rules:
                        dep_rules.append(rule)

            counts = Counter(all_words)
            context_weights = {w: float(c) for w, c in counts.most_common(10) if c >= 1}
            confidence = min(0.90, 0.60 + len(choice_entries) * 0.05)

            patterns.append(ChoicePattern(
                word=word,
                preferred_choice=choice,
                context_indicators=list(context_weights.keys()),
                pattern_type="weighted_keywords",
                confidence=confidence,
                usage_count=len(choice_entries),
                last_used=choice_entries[-1].timestamp,
                dep_rules=dep_rules or None,
                context_weights=context_weights or None,
            ))

        return patterns

    def analyze_and_update_patterns(self):
        """Analyze entries and update patterns."""
        if not self.storage.entries:
            log_message("No learning entries to analyze")
            return

        log_message(f"analyze_and_update_patterns: Starting analysis of {len(self.storage.entries)} entries")
        log_message(f"Analyzing {len(self.storage.entries)} choice learning entries...")

        # Group entries by word
        word_entries: Dict[str, List[ChoiceLearningEntry]] = {}
        for entry in self.storage.entries:
            word_lower = entry.original_word.lower()
            if word_lower not in word_entries:
                word_entries[word_lower] = []
            word_entries[word_lower].append(entry)

        # Extract patterns for each word
        new_patterns = []
        for word, entries in word_entries.items():
            patterns = self._extract_patterns_for_word(word, entries)
            new_patterns.extend(patterns)

        # Update storage
        self.storage.patterns = new_patterns
        self.storage.save_patterns()

        log_message(f"Extracted {len(new_patterns)} choice patterns")

        # Sync patterns to POS dictionary context_keywords

        try:
            from .pos_dictionary import get_pos_dictionary

            pos_dict = get_pos_dictionary()

            # Track how many keywords we add
            keywords_added = 0

            for pattern in new_patterns:
                word = pattern.word
                pronunciation = pattern.preferred_choice
                keywords = pattern.context_indicators

                log_message(
                    f"DEBUG: Processing pattern for {word}→{pronunciation}, confidence={pattern.confidence}, keywords={len(keywords)}",
                    level="DEBUG",
                )

                # Only sync patterns with sufficient confidence
                # Lowered from 0.70 to 0.55 to allow syncing of moderately consistent patterns
                if pattern.confidence < 0.55:
                    log_message(
                        f"DEBUG: Skipping pattern for {word}→{pronunciation} (confidence {pattern.confidence} < 0.55)",
                        level="DEBUG",
                    )
                    continue

                # Check if word exists in POS dictionary
                if not pos_dict.has_word(word):
                    log_message(
                        f"DEBUG: Skipping pattern for {word} (not in POS dictionary)",
                        level="DEBUG",
                    )
                    continue

                # Add each context indicator as a keyword
                for keyword in keywords:
                    # Skip very short or common words
                    if len(keyword) < 3:
                        continue

                    # Add keyword to POS dictionary
                    success = pos_dict.add_context_keyword(word, pronunciation, keyword)
                    if success:
                        keywords_added += 1
                        log_message(
                            f"Synced keyword '{keyword}' for {word}→{pronunciation} from learned pattern"
                        )

            # Save POS dictionary with new keywords
            if keywords_added > 0:
                pos_dict.save_dictionary()
                log_message(
                    f"Synced {keywords_added} learned keywords to POS dictionary"
                )
            else:
                log_message(
                    "DEBUG: No keywords were added to POS dictionary", level="DEBUG"
                )

        except Exception as e:
            log_message(f"Error syncing patterns to POS dictionary: {e}", level="ERROR")
            import traceback

        # Sync patterns to choices.json context_keywords for rule learning
        self._sync_patterns_to_choices_json(new_patterns)

    def _sync_patterns_to_choices_json(self, patterns: List[ChoicePattern]):
        """
        Sync learned patterns to choices.json context_keywords for rule-based learning.

        This allows the static choices.json to be updated with learned distinguishing keywords
        from user corrections, making rules smarter over time.
        """
        log_message(
            f"DEBUG: _sync_patterns_to_choices_json called with {len(patterns)} patterns",
            level="DEBUG",
        )

        try:
            import json
            import os
            choices_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "choices.json")

            if not os.path.exists(choices_path):
                log_message(f"choices.json not found at {choices_path}, skipping sync", level="WARNING")
                return

            with open(choices_path, "r", encoding="utf-8") as f:
                choices_data = json.load(f)

            keywords_added = 0

            for pattern in patterns:
                word = pattern.word.lower()
                pronunciation = pattern.preferred_choice
                learned_keywords = pattern.context_indicators

                log_message(
                    f"DEBUG: Processing learned pattern for {word}→{pronunciation}, keywords={len(learned_keywords)}",
                    level="DEBUG",
                )

                # Find the entry in choices.json
                entry = None
                for e in choices_data:
                    if e["word"].lower() == word:
                        entry = e
                        break

                if not entry:
                    log_message(f"DEBUG: Word '{word}' not found in choices.json, skipping", level="DEBUG")
                    continue

                # Find the option with matching spelling
                option = None
                for opt in entry.get("options", []):
                    if opt["spelling"] == pronunciation:
                        option = opt
                        break

                if not option:
                    log_message(f"DEBUG: Pronunciation '{pronunciation}' not found for '{word}', skipping", level="DEBUG")
                    continue

                # Only add if confidence is sufficient
                if pattern.confidence < 0.55:
                    log_message(f"DEBUG: Pattern confidence {pattern.confidence} < 0.55, skipping", level="DEBUG")
                    continue

                # Initialize context_keywords if not present
                if "context_keywords" not in option:
                    option["context_keywords"] = []

                # Add new keywords, avoiding duplicates
                existing = set(option["context_keywords"])
                for kw in learned_keywords:
                    if len(kw) >= 3 and kw not in existing and kw.lower() not in ['the', 'and', 'or', 'is', 'are', 'was', 'were']:
                        option["context_keywords"].append(kw)
                        existing.add(kw)
                        keywords_added += 1
                        log_message(f"Added learned keyword '{kw}' to {word}→{pronunciation}")

            # Save updated choices.json
            if keywords_added > 0:
                with open(choices_path, "w", encoding="utf-8") as f:
                    json.dump(choices_data, f, indent=2, ensure_ascii=False)
                log_message(f"Synced {keywords_added} learned keywords to choices.json")
            else:
                log_message("DEBUG: No keywords were added to choices.json", level="DEBUG")

        except Exception as e:
            log_message(f"Error syncing patterns to choices.json: {e}", level="ERROR")
            import traceback
            log_message(traceback.format_exc(), level="DEBUG")

            log_message(f"Traceback: {traceback.format_exc()}", level="ERROR")

    def get_suggestion_for_word(self, word: str, context: str) -> Optional[str]:
        """Get AI-enhanced suggestion based on learned patterns."""
        suggestion = self.storage.get_best_suggestion(word, context)
        if suggestion:
            return suggestion[0]
        return None

    def add_user_decision(
        self,
        word: str,
        options: List[str],
        context_before: str,
        context_after: str,
        user_choice: str,
        line_number: int = 0,
        pos_tag: str = "",
    ):
        """
        Record a user decision for learning.
        This should be called when user manually selects a choice.
        """
        log_message(f"add_user_decision: Starting for word '{word}', choice '{user_choice}', options {options}")
        from .pos_tagger import get_pos_tagger

        # Get lemma for word to enable cross-form learning
        lemma = self.storage._get_lemma(word)

        # Auto-extract dependency info
        dep_info = None
        try:
            pos_tagger = get_pos_tagger()
            dep_info_raw = pos_tagger.get_dependency_info(
                context_before, word, context_after
            )
            dep_info = (
                {
                    "dep_relation": dep_info_raw.dep_relation if dep_info_raw else None,
                    "head_lemma": (
                        self.storage._get_lemma(dep_info_raw.head_word)
                        if dep_info_raw and dep_info_raw.head_word
                        else None
                    ),
                    "syntactic_confidence": (
                        pos_tagger.get_syntactic_confidence(dep_info_raw, pos_tag)
                        if dep_info_raw
                        else 0.0
                    ),
                }
                if dep_info_raw
                else None
            )
        except Exception as e:
            log_message(f"Dep extraction failed for '{word}': {e}", level="WARNING")
            dep_info = None  # Fallback to None, still save entry

        # Auto-extract window features for weights
        window_features = {
            "left_words": [],
            "right_words": [],
            "top_noun": "",
            "top_verb": "",
        }
        try:
            pos_tagger = get_pos_tagger()
            full_window = f"{context_before} {word} {context_after}"
            doc = pos_tagger.nlp(full_window)
            left_words = [
                token.text for token in list(doc)[:2] if token.pos_ != "PUNCT"
            ]  # Immediate left 1-2
            right_words = [
                token.text for token in list(doc)[-2:] if token.pos_ != "PUNCT"
            ]  # Immediate right 1-2

            nouns = [token.text.lower() for token in doc if token.pos_ == "NOUN"]
            verbs = [token.text.lower() for token in doc if token.pos_ == "VERB"]
            top_noun = max(set(nouns), key=nouns.count, default="") if nouns else ""
            top_verb = max(set(verbs), key=verbs.count, default="") if verbs else ""

            window_features = {
                "left_words": left_words,
                "right_words": right_words,
                "top_noun": top_noun,
                "top_verb": top_verb,
            }
        except Exception as e:
            log_message(f"Window features extraction failed for '{word}': {e}", level="WARNING")
            # Keep default empty dict, still save entry

        entry = ChoiceLearningEntry.create(
            original_word=word,
            lemma=lemma,
            options=options,
            context_before=context_before,
            context_after=context_after,
            user_choice=user_choice,
            line_number=line_number,
            pos_tag=pos_tag,
            dep_info=dep_info,
            window_features=window_features,
        )

        self.storage.add_learning_entry(entry)

        # Log the saved entry for debugging
        log_message(f"Saved learning entry for '{word}': choice='{user_choice}', dep_info={dep_info}, window_features={window_features}")

        # Update patterns after each decision
        self.analyze_and_update_patterns()
        log_message(f"add_user_decision: Completed successfully for '{word}'")
