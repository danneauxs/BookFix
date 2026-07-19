"""Unit tests for choices evidence scoring and phrase matching."""

from pathlib import Path
from unittest.mock import MagicMock

from bookfix.ai.choice_evidence import ChoiceEvidenceScorer
from bookfix.ai.choices_learning import ChoiceLearningEntry, ChoicePattern, ChoicesLearningStorage
from bookfix.ai.choices_corpus import extract_context_records
from bookfix.ai.choices_holdout import build_holdout_records
from bookfix.ai.service import BookfixAIService
from bookfix.ai.hybrid_deciders import (
    decide_bass,
    decide_bowed,
    decide_close,
    decide_elaborate,
    decide_lead,
    decide_live,
    decide_polish,
    decide_read,
    decide_recreation,
    decide_row,
    decide_tear,
    decide_wound,
)
from bookfix.ai.pos_dictionary import POSDictionary


def test_phrase_evidence_beats_weak_context() -> None:
    """Confirm exact phrase evidence can decide over weak semantic hints."""
    scorer = ChoiceEvidenceScorer(
        {"Thresholds": {"EVIDENCE_AUTO_APPLY_MIN_SCORE": 2.4, "EVIDENCE_MIN_MARGIN": 0.75}}
    )
    decision, source, _ = scorer.choose(
        "lead",
        {
            "phrase": {
                "choice": "led",
                "confidence": 0.97,
                "reason": "lead pipe",
                "kind": "phrase",
            },
            "semantic": {
                "choice": "leed",
                "confidence": 0.80,
                "reason": "nearby context",
                "kind": "semantic",
            },
        },
        ["led", "leed"],
    )
    assert decision["choice"] == "led"
    assert source == "phrase"


def test_conflicting_hard_evidence_defers() -> None:
    """Confirm contradictory high-confidence rules never auto-apply."""
    scorer = ChoiceEvidenceScorer()
    decision, source, _ = scorer.choose(
        "read",
        {
            "complex_pos": {"choice": "red", "confidence": 0.98},
            "dependency": {"choice": "reed", "confidence": 0.98},
        },
        ["red", "reed"],
    )
    assert decision is None
    assert source is None


def test_context_clue_cannot_override_structural_conflict() -> None:
    """Confirm sense evidence defers when grammar selects another role."""
    scorer = ChoiceEvidenceScorer()
    decision, source, _ = scorer.choose(
        "lead",
        {
            "complex_pos": {"choice": "led", "confidence": 0.98},
            "keyword_strong": {
                "choice": "leed",
                "confidence": 0.88,
                "reason": "cruiser",
            },
        },
        ["led", "leed"],
    )
    assert decision is None
    assert source is None


def test_correlated_structural_rules_count_once() -> None:
    """Confirm one parser result cannot gain confidence from duplicate routes."""
    scorer = ChoiceEvidenceScorer()
    decision, source, scores = scorer.choose(
        "live",
        {
            "complex_pos": {"choice": "lyve", "confidence": 0.98},
            "hybrid": {"choice": "lyve", "confidence": 0.95},
            "pos": {"choice": "lyve", "confidence": 0.80},
        },
        ["liv", "lyve"],
    )
    assert scores["lyve"].total_score == 4.9
    assert decision["choice"] == "lyve"
    assert source == "complex_pos"


def test_strong_keyword_conflict_with_hybrid_defers() -> None:
    """Confirm broad strong keywords cannot override contradictory grammar."""
    scorer = ChoiceEvidenceScorer()
    decision, source, _ = scorer.choose(
        "lead",
        {
            "hybrid": {"choice": "leed", "confidence": 0.95},
            "keyword_strong": {"choice": "led", "confidence": 0.88},
        },
        ["led", "leed"],
    )
    assert decision is None
    assert source is None


def test_role_first_resolution_uses_grammar_or_defers_same_role_meanings() -> None:
    """Confirm grammar selects unique roles and defers semantic homographs safely."""
    from bookfix.ai.pos_tagger import POSTaggerService
    from bookfix.ai.role_resolution import resolve_syntactic_choice
    import json

    entries = {
        entry["word"]: entry["options"]
        for entry in json.load(open("data/choices.json", encoding="utf-8"))
        if "word" in entry
    }
    cases = [
        ("As the month drew towards its ", "close", ".", "close", False),
        ("The station is broadcasting ", "live", " from town.", "lyve", False),
        ("She was able to ", "read", " the map.", "reed", False),
        ("He felt the gaping ", "tear", " in the earth.", None, True),
        ("Thanks for the ", "lead", ".", None, True),
        ("Gunny, are you telling me you ", "read", " the handout on local flora and fauna", None, True),
    ]
    tagger = POSTaggerService()
    for before, word, after, expected, ambiguous in cases:
        token, dependency, doc = tagger.get_token_and_dependency(before, word, after)
        result = resolve_syntactic_choice(token, dependency, doc, entries[word])
        assert result.choice == expected
        assert result.needs_semantic_resolution is ambiguous


def test_rule_collection_preserves_syntax_and_ambiguity_evidence() -> None:
    """Confirm syntax never suppresses phrase, dependency, or semantic rules."""
    from bookfix.ai.pos_tagger import DependencyInfo, POSToken
    from bookfix.processors.ai_choices import AIChoiceProcessor

    processor = object.__new__(AIChoiceProcessor)
    processor.use_pos_tagging = True
    processor.rules_only_mode = True
    processor._ensure_learning_services = MagicMock()
    processor._get_pos_based_choice = MagicMock(return_value=None)
    processor._log_rule_evaluation = MagicMock()
    processor.learning_storage = MagicMock()
    processor.learning_storage.get_phrase_suggestion.return_value = {
        "candidate": "first",
        "phrase": "sample river",
    }
    processor.learning_storage.get_dependency_suggestion.return_value = None
    processor.pos_tagger = MagicMock()
    processor.pos_tagger.get_token_and_dependency.return_value = (
        POSToken("sample", "NN", "NOUN", 0),
        DependencyInfo("sample", "nsubj", "sample", "NN", "ROOT"),
        MagicMock(),
    )
    processor.pos_dictionary = MagicMock()
    processor.pos_dictionary.get_pronunciations_by_complex_pos_rules.return_value = [
        "first",
        "second",
    ]
    processor.pos_dictionary.get_pronunciation_by_strong_keywords.return_value = None
    processor.pos_dictionary.get_pronunciations_by_semantic.return_value = [
        ("first", "river", 0.85),
        ("second", "water", 0.85),
    ]
    processor.pos_dictionary.check_entity_context.return_value = None
    processor.lexicon_loader = MagicMock()

    cases = [
        (
            [
                {"spelling": "first", "pos": "noun"},
                {"spelling": "second", "pos": "verb"},
            ],
            "syntax",
        ),
        (
            [
                {"spelling": "first", "pos": "noun"},
                {"spelling": "second", "pos": "noun"},
            ],
            "semantic_ambiguity",
        ),
    ]
    for options, expected_syntax_key in cases:
        processor.lexicon_loader.get_options.return_value = options
        rules, _ = processor._run_all_rules("sample", "A [sample] river.", None)

        assert "phrase" in rules
        assert expected_syntax_key in rules
        assert {"complex_pos:first", "complex_pos:second"} <= rules.keys()
        assert {"semantic:first", "semantic:second"} <= rules.keys()


def test_pos_dictionary_collects_competing_rule_candidates() -> None:
    """Confirm POS and semantic evaluators return all conflicting candidates."""
    from bookfix.ai.pos_tagger import DependencyInfo, POSToken

    dictionary = object.__new__(POSDictionary)
    dictionary.words = {
        "sample": {
            "first": {
                "dep_rules": [{"type": "pos_category", "values": ["NOUN"]}],
                "semantic_tags": ["river"],
            },
            "second": {
                "dep_rules": [{"type": "pos_category", "values": ["NOUN"]}],
                "semantic_tags": ["water"],
            },
        }
    }
    token = POSToken("sample", "NN", "NOUN", 0)
    dependency = DependencyInfo("sample", "nsubj", "sample", "NN", "ROOT")

    complex_matches = dictionary.get_pronunciations_by_complex_pos_rules(
        "sample", token, dependency, []
    )
    semantic_matches = dictionary.get_pronunciations_by_semantic(
        "sample", ["river", "water"]
    )

    assert complex_matches == ["first", "second"]
    assert [choice for choice, _, _ in semantic_matches] == ["first", "second"]


def test_competing_complex_pos_candidates_defer_to_conflict_scoring() -> None:
    """Confirm competing dependency matches cannot select dictionary order."""
    decision, source, _ = ChoiceEvidenceScorer().choose(
        "sample",
        {
            "complex_pos:first": {
                "choice": "first",
                "confidence": 0.98,
                "kind": "complex_pos",
            },
            "complex_pos:second": {
                "choice": "second",
                "confidence": 0.98,
                "kind": "complex_pos",
            },
        },
        ["first", "second"],
    )

    assert decision is None
    assert source is None


def test_rules_only_ambiguity_returns_canonical_choice() -> None:
    """Confirm unresolved rules-only input still returns one canonical spelling."""
    from bookfix.processors.ai_choices import AIChoiceProcessor
    from bookfix.ai.review_window import AIChangesReviewWindow

    processor = object.__new__(AIChoiceProcessor)
    processor.evidence_scorer = ChoiceEvidenceScorer()
    processor.rules_only_mode = True
    decision, source = processor._get_consensus_from_rules(
        {"semantic_ambiguity": {"choice": None, "confidence": 0.0}},
        "",
        "lead",
        ["leed", "led"],
    )
    assert decision["choice"] in {"leed", "led"}
    assert decision["choice"] != "lead"
    assert source.startswith("rules_only_")
    assert AIChangesReviewWindow._next_choice(["leed", "led"], "lead") == "leed"


def test_phrase_storage_requires_confirmed_status(tmp_path) -> None:
    """Confirm phrase matcher ignores unconfirmed candidates."""
    storage = ChoicesLearningStorage(storage_dir=str(tmp_path))
    storage.phrase_rules = [
        {
            "word": "lead",
            "candidate": "led",
            "phrase": "lead pipe",
            "confidence": 0.95,
            "status": "confirmed",
        },
        {
            "word": "lead",
            "candidate": "leed",
            "phrase": "lead wire",
            "confidence": 0.95,
            "status": "candidate",
        },
    ]
    match = storage.get_phrase_suggestion("lead", "Use [lead] pipe here.")
    assert match["candidate"] == "led"
    assert storage.get_phrase_suggestion("lead", "Use [lead] wire here.") is None


def test_context_keywords_helper_filters_empty_lists() -> None:
    """Confirm batch/context prompts only carry non-empty keyword hints."""
    from bookfix.processors.ai_choices import AIChoiceProcessor

    class FakePosDictionary:
        """Provide deterministic option metadata for one homograph."""

        def get_option_info(self, word, spelling):
            """Return keyword hints for lead spellings."""
            if word == "lead" and spelling == "led":
                return {"context_keywords": ["bullet", "ship"]}
            if word == "lead" and spelling == "leed":
                return {"context_keywords": []}
            return None

    processor = object.__new__(AIChoiceProcessor)
    processor.pos_dictionary = FakePosDictionary()
    processor._ensure_pos_services = lambda: None

    keywords = processor._build_context_keywords("lead", ["leed", "led"])
    assert keywords == {"led": ["bullet", "ship"]}


def test_lead_attributive_use_uses_structure() -> None:
    """Confirm adjective-like attributive lead uses the front-position spelling."""
    pronunciation, route = decide_lead(
        "JJ", "amod", "account", False, None, "The lead account was listed first."
    )
    assert pronunciation == "leed"
    assert route == "jj-attributive-front-position"


def test_target_local_rules_cover_five_review_corrections() -> None:
    """Confirm generalized grammar resolves five corrected runtime choices."""
    cases = [
        (
            decide_lead,
            ("NN", "conj", "steel", False, None),
            "The steel-and-[lead]-and-plastic gear entered the ship.",
            "led",
        ),
        (
            decide_read,
            ("VBN", "xcomp", "be", False, None),
            "It can be [read], although we can read another message.",
            "red",
        ),
        (
            decide_read,
            ("VBD", "ROOT", "message", False, None),
            "We can read it now. The message [read]: proceed.",
            "red",
        ),
        (
            decide_live,
            ("JJ", "amod", "camera", False, None),
            "Footage came from a [live] helicopter camera downtown.",
            "lyve",
        ),
        (
            decide_polish,
            ("NN", "compound", "knife", False, None),
            "The advertisement named Oakey's Knife [Polish].",
            "pollish",
        ),
    ]
    for decider, args, sentence, expected in cases:
        result, _route = decider(*args, sentence)
        assert result == expected, (decider.__name__, sentence, result)


def test_nominal_read_patterns_override_verb_tag() -> None:
    """Confirm noun read constructions survive incorrect verb POS tags."""
    cases = [
        "A closer [read] of the file revealed the answer.",
        "The console [read]-outs flickered.",
        "I could get a [read] on her intentions.",
    ]
    for sentence in cases:
        pronunciation, _route = decide_read("VBD", "ROOT", "read", False, None, sentence)
        assert pronunciation == "reed"


def test_past_relative_lead_rule_preserves_present_counterpart() -> None:
    """Confirm narrative past changes lead while present relative clauses remain present."""
    past, _route = decide_lead(
        "VBP", "relcl", "ones", False, None,
        "Eduard was a Dark Hand, one of the ones who [lead] the sacrificial rituals.",
    )
    present, _route = decide_lead(
        "VBP", "relcl", "ones", False, None,
        "They are among the people who [lead] the rituals today.",
    )
    assert past == "led"
    assert present == "leed"


def test_review_log_marks_selected_repeated_target() -> None:
    """Confirm review logging brackets only selected occurrence of a repeated word."""
    from bookfix.ai.review_window import AIChangesReviewWindow

    text = "She had read before. He will read again."
    start = text.rindex("read")

    assert AIChangesReviewWindow._extract_full_sentence(None, text, "read", start) == "He will [read] again"


def test_review_context_stops_at_question_and_paragraph_boundaries() -> None:
    """Confirm review context never merges neighboring sentences or paragraphs."""
    from bookfix.ai.review_window import AIChangesReviewWindow

    text = "Did she read it? He will read again.\nThey read daily."
    start = text.index("read", text.index("He will"))
    sentence = AIChangesReviewWindow._extract_full_sentence(None, text, "read", start)
    assert sentence == "He will [read] again"


def test_generalized_rules_preserve_opposite_senses() -> None:
    """Confirm new local rules do not steal common opposite pronunciations."""
    cases = [
        (decide_read, ("VB", "xcomp", "can", False, None), "We can [read] it.", "reed"),
        (decide_live, ("VBP", "ROOT", "people", False, None), "People [live] downtown.", "liv"),
        (decide_polish, ("JJ", "amod", "language", False, None), "The [Polish] language.", "pole-ish"),
    ]
    for decider, args, sentence, expected in cases:
        result, _route = decider(*args, sentence)
        assert result == expected, (decider.__name__, sentence, result)


def test_reviewed_flip_rules_cover_general_language_patterns() -> None:
    """Confirm generalized syntax resolves verified flips without sentence-specific rules."""
    cases = [
        (decide_read, ("VB", "ROOT", "did", False, None), "Did you [read] it?", "red"),
        (decide_live, ("VB", "ROOT", "let", False, None), "Let them [live]-stream this.", "lyve"),
        (decide_live, ("RB", "advmod", "broadcasting", False, None), "A station is [live] broadcasting from town.", "lyve"),
        (decide_live, ("JJ", "amod", "book", False, None), "It became a real [live] book.", "lyve"),
        (decide_live, ("JJ", "amod", "friend", False, None), "He had a [live] in girlfriend.", "liv"),
        (decide_read, ("VB", "xcomp", "able", False, None), "He was being able to [read] the sign.", "reed"),
        (decide_lead, ("NN", "compound", "engineer", False, None), "She is our [lead] engineer.", "leed"),
        (decide_lead, ("NN", "dobj", "found", False, None), "This is the best [lead] I found.", "leed"),
        (decide_lead, ("NN", "dobj", "for", False, None), "Thanks for the [lead].", "leed"),
        (decide_lead, ("NN", "pobj", "against", False, None), "Once I stop struggling against his [lead], we make better progress.", "leed"),
        (decide_tear, ("NN", "dobj", "heard", True, None), "He heard a [tear] in the metal.", "tair"),
        (decide_tear, ("NN", "dobj", "shed", True, None), "He shed a [tear].", "teer"),
        (decide_close, ("JJ", "acomp", "whir", False, None), "The doors whir [close].", "cloze"),
        (decide_row, ("NN", "dobj", "want", True, None), "I don't want a [row].", "rau"),
        (decide_bowed, ("VBN", "acomp", "head", False, None), "He stood with his head [bowed].", "boughed"),
        (decide_bowed, ("VBD", "ROOT", "wing", False, None), "Long wings [bowed] inward.", "boed"),
        (decide_elaborate, ("JJ", "ROOT", "elaborate", False, None), "[Elaborate], Zoe.", "elaborayt"),
    ]
    for decider, args, sentence, expected in cases:
        result, _route = decider(*args, sentence)
        assert result == expected, (decider.__name__, sentence, result)


def test_new_flip_rules_preserve_opposite_senses() -> None:
    """Confirm new structural rules retain valid competing pronunciations."""
    cases = [
        (decide_close, ("JJ", "acomp", "be", False, None), "The station is [close].", "close"),
        (decide_live, ("VBP", "ROOT", "people", False, None), "People [live] in cities.", "liv"),
        (decide_live, ("JJ", "amod", "radio", False, None), "They reported [live] radio coverage.", "lyve"),
        (decide_read, ("VBG", "ROOT", "able", False, None), "He was being able to [read] the sign.", "reed"),
        (decide_lead, ("NN", "compound", "pipe", False, None), "A [lead] pipe is heavy.", "led"),
        (decide_tear, ("NN", "dobj", "eye", True, None), "A [tear] filled her eye.", "teer"),
        (decide_row, ("NN", "pobj", "in", True, None), "They sat in a [row].", "ro"),
        (decide_bowed, ("VBN", "acomp", "shelf", False, None), "The shelf was [bowed].", "boed"),
        (decide_elaborate, ("JJ", "amod", "design", False, None), "An [elaborate] design.", "elaborit"),
    ]
    for decider, args, sentence, expected in cases:
        result, _route = decider(*args, sentence)
        assert result == expected, (decider.__name__, sentence, result)


def test_strong_keywords_are_local_to_marked_target() -> None:
    """Confirm distant keywords cannot control a marked homograph occurrence."""
    dictionary = POSDictionary()
    options = [
        {"spelling": "leed", "strong_keywords": ["ship"]},
        {"spelling": "led", "strong_keywords": ["steel"]},
    ]
    result = dictionary.get_pronunciation_by_strong_keywords(
        "lead",
        "steel-and-[lead]-and-plastic gear moved like a tiny vessel into the ship",
        options,
    )
    assert result and result[0] == "led"


def test_rules_only_conflict_uses_evidence_not_option_order() -> None:
    """Confirm rules-only recommendation follows evidence rather than first option."""
    from bookfix.processors.ai_choices import AIChoiceProcessor

    processor = object.__new__(AIChoiceProcessor)
    processor.evidence_scorer = ChoiceEvidenceScorer()
    decision, source = processor._get_rules_only_recommendation(
        "read",
        {
            "hybrid": {"choice": "red", "confidence": 0.95},
            "pos": {"choice": "red", "confidence": 0.80},
            "semantic": {"choice": "reed", "confidence": 0.70},
        },
        ["reed", "red"],
    )
    assert decision["choice"] == "red"
    assert source == "hybrid"


def test_rules_only_never_loads_nli(monkeypatch) -> None:
    """Confirm rules-only guard prevents transformer model initialization."""
    from bookfix.processors.ai_choices import AIChoiceProcessor

    processor = object.__new__(AIChoiceProcessor)
    processor.rules_only_mode = True
    processor.nli = None
    monkeypatch.setitem(__import__("sys").modules, "transformers", None)

    processor._ensure_nli_services()

    assert processor.nli is None


def test_learned_keyword_fallback_has_no_stale_dependency_state(tmp_path) -> None:
    """Confirm keyword learning works after dependency lookup returns no match."""
    storage = ChoicesLearningStorage(storage_dir=str(tmp_path))
    storage.get_dependency_suggestion = lambda _word, _context: None
    storage.patterns = [
        ChoicePattern(
            word="lead",
            preferred_choice="led",
            context_indicators=["steel"],
            pattern_type="context_words",
            confidence=0.9,
            usage_count=3,
            last_used="2026-07-12",
            context_weights={"steel": 1.0},
        )
    ]
    assert storage.get_best_suggestion("lead", "steel [lead] shielding") == ("led", 0.9)


def test_structural_phrase_deciders_cover_reviewed_failures() -> None:
    """Confirm narrow grammar and collocation rules resolve known holdout failures."""
    cases = [
        (decide_lead, ("NN", "poss", "dog", False), "The dog's [lead] was short.", "leed"),
        (decide_lead, ("NN", "dobj", "away", False), "They would [lead] her away.", "leed"),
        (decide_lead, ("NN", "dobj", "away", False), "She could [lead] Peri out.", "leed"),
        (decide_lead, ("NN", "dobj", "rein", False), "He cut the [lead] rein.", "leed"),
        (decide_lead, ("NN", "dobj", "lead", False), "Following her [lead], they moved.", "leed"),
        (decide_lead, ("NN", "dobj", "had", False), "His replies had given him a [lead].", "leed"),
        (decide_bass, ("NN", "dobj", "was", False), "It was a muted [bass].", "base"),
        (decide_bowed, ("VBD", "ROOT", "bow", False), "Susan [bowed] her head.", "boughed"),
        (decide_bowed, ("VBD", "ROOT", "bow", False), "He [bowed] elaborately.", "boughed"),
        (decide_bowed, ("VBN", "acomp", "was", False), "His head was [bowed] in sorrow.", "boughed"),
        (decide_close, ("VB", "ROOT", "be", False), "Somewhere [close].", "close"),
        (decide_row, ("NN", "pobj", "of", True), "At the end of the [row].", "ro"),
        (decide_tear, ("NN", "compound", "face", False), "Her [tear]-stained face was red.", "teer"),
        (decide_tear, ("NN", "dobj", "will", False), "They will [tear] us to pieces.", "tair"),
        (decide_wound, ("NN", "dobj", "down", False), "He [wound] his window down.", "wow'nd"),
        (decide_wound, ("NN", "dobj", "down", False), "Behind her [wound] the corridor.", "wow'nd"),
        (decide_recreation, ("NN", "dobj", "used", False), "They used it for [recreation] and relaxation.", "wreckre-ation"),
    ]
    for decider, args, sentence, expected in cases:
        result, _route = decider(*args, None, sentence)
        assert result == expected, (decider.__name__, sentence, result)


def test_corpus_extractor_emits_normalized_phrase_context() -> None:
    """Confirm corpus extraction preserves target context and normalized phrase windows."""
    records = extract_context_records(
        "The lead ship passed the lead pipe.",
        "sample.txt",
        ["lead"],
        window_words=2,
    )
    assert len(records) == 2
    assert records[0]["context"] == "the [lead] ship passed"
    assert records[0]["phrase_window"] == "the lead ship passed"
    assert records[1]["context"] == "passed the [lead] pipe"


def test_corpus_extractor_rejects_empty_source_directory(tmp_path) -> None:
    """Confirm CLI source discovery can distinguish empty directories from valid corpora."""
    from bookfix.ai.choices_corpus import iter_source_files

    assert list(iter_source_files([str(tmp_path)])) == []


def test_dual_nli_disagreement_suppresses_hybrid_evidence() -> None:
    """Confirm conflicting NLI models cannot create an automatic hybrid decision."""
    from bookfix.processors.ai_choices import AIChoiceProcessor

    processor = object.__new__(AIChoiceProcessor)
    processor.nli = object()
    processor.nli_secondary = object()
    processor.nli_model_name = "primary"
    processor.nli_secondary_model_name = "secondary"
    processor.use_nli_dual_verification = True

    def disagreeing_decider(tag, dep, head, has_det, nli, sentence, options):
        """Return different spellings for the fake primary and secondary models."""
        return ("led", "nli=primary") if nli is processor.nli else ("leed", "nli=secondary")

    choice, route = processor._decide_with_dual_nli(
        disagreeing_decider, "JJ", "amod", "account", False, "lead account", []
    )
    assert choice is None
    assert route == "nli-disagreement:primary=led;secondary=leed"


def test_dual_nli_agreement_preserves_hybrid_evidence() -> None:
    """Confirm matching NLI models can contribute one agreed spelling."""
    from bookfix.processors.ai_choices import AIChoiceProcessor

    processor = object.__new__(AIChoiceProcessor)
    processor.nli = object()
    processor.nli_secondary = object()
    processor.nli_model_name = "primary"
    processor.nli_secondary_model_name = "secondary"
    processor.use_nli_dual_verification = True

    def agreeing_decider(tag, dep, head, has_det, nli, sentence, options):
        """Return the same spelling for both fake models."""
        return "led", "nli=led(0.90)"

    choice, route = processor._decide_with_dual_nli(
        agreeing_decider, "NN", "compound", "pipe", False, "lead pipe", []
    )
    assert choice == "led"
    assert route.startswith("nli-agree:")


def test_ollama_batch_fallback_scopes_examples_to_one_word(monkeypatch) -> None:
    """Confirm Ollama fallback drops unrelated chunk examples for single-item calls."""
    from bookfix.ai.service import AIResponse, BookfixAIService

    calls = []
    original = BookfixAIService.analyze_homographs_batch

    def spy(self, items, word_examples=None):
        """Record recursive batch calls and short-circuit single-item responses."""
        calls.append((tuple(item["id"] for item in items), word_examples))
        if len(items) > 1:
            return original(self, items, word_examples)
        return {items[0]["id"]: AIResponse(True, items[0]["options"][0]["spelling"], 0.95, "ok")}

    monkeypatch.setattr(BookfixAIService, "analyze_homographs_batch", spy)
    service = BookfixAIService(provider="ollama", model="qwen3:8b", max_retries=1, rate_limit=0.0)
    items = [
        {
            "id": 7,
            "word": "lead",
            "context": "The lead ship arrived first.",
            "options": [
                {"spelling": "leed", "meaning": "front"},
                {"spelling": "led", "meaning": "metal"},
            ],
        },
        {
            "id": 8,
            "word": "read",
            "context": "They read the book.",
            "options": [
                {"spelling": "reed", "meaning": "present"},
                {"spelling": "red", "meaning": "past"},
            ],
        },
    ]
    word_examples = {
        "lead": {"leed": ["lead the team"], "led": ["lead pipe"]},
        "read": {"reed": ["read now"], "red": ["read yesterday"]},
    }

    result = service.analyze_homographs_batch(items, word_examples)

    assert result[7].content == "leed"
    assert result[8].content == "reed"
    assert calls[0][0] == (7, 8)
    assert calls[0][1] == word_examples
    assert calls[1][0] == (1,)
    assert calls[1][1] == {"lead": {"leed": ["lead the team"], "led": ["lead pipe"]}}
    assert calls[2][0] == (1,)
    assert calls[2][1] == {"read": {"reed": ["read now"], "red": ["read yesterday"]}}


def test_single_item_batch_accepts_unwrapped_decision(monkeypatch) -> None:
    """Confirm a single-item fallback accepts an otherwise valid decision object."""
    from bookfix.ai.service import AIResponse

    service = BookfixAIService(provider="test", model="test", rate_limit=0.0)

    def fake_request(prompt):
        """Return a model reply without the optional batch array envelope."""
        return AIResponse(
            True,
            '{"choice":"led","confidence":0.95,"agrees_with_rules":true,'
            '"justification":"Pipe identifies metal.","abstain":false}',
        )

    monkeypatch.setattr(service, "_make_request", fake_request)
    result = service.analyze_homographs_batch(
        [
            {
                "id": 1,
                "word": "lead",
                "context": "The [lead] pipe cracked.",
                "options": [
                    {"spelling": "leed", "meaning": "to guide"},
                    {"spelling": "led", "meaning": "a metal"},
                ],
            }
        ]
    )

    assert result[1].success is True
    assert result[1].content == "led"


def test_ollama_fallback_preserves_evidence_packet(monkeypatch) -> None:
    """Confirm recursive Ollama calls retain each item's original evidence packet."""
    from bookfix.ai.service import AIResponse

    prompts = []
    service = BookfixAIService(provider="ollama", model="test", rate_limit=0.0)

    def fake_request(prompt):
        """Return canonical replies while retaining prompts for context assertions."""
        prompts.append(prompt)
        # Each packet has different valid spellings, so reply follows its word.
        choice = "leed" if '"word": "lead"' in prompt else "reed"
        return AIResponse(
            True,
            '{"id":1,"decision":{"choice":"'
            + choice
            + '","confidence":0.95,"agrees_with_rules":true,'
            '"justification":"Sentence context identifies usage.","abstain":false}}',
        )

    monkeypatch.setattr(service, "_make_request", fake_request)
    result = service.analyze_homographs_batch(
        [
            {
                "id": 1,
                "word": "lead",
                "context": "The [lead] ship arrived.",
                "options": [{"spelling": "leed"}, {"spelling": "led"}],
            },
            {
                "id": 2,
                "word": "read",
                "context": "They [read] every day.",
                "options": [{"spelling": "reed"}, {"spelling": "red"}],
            },
        ]
    )

    assert result[1].content == "leed"
    assert result[2].content == "reed"
    assert '"sentence": "The [lead] ship arrived."' in prompts[0]
    assert '"sentence": "They [read] every day."' in prompts[1]


def test_holdout_builder_keeps_only_canonical_reviewed_records() -> None:
    """Confirm holdout builder keeps corrections and trusted acceptances only."""
    canonical = {
        "lead": {
            "word": "lead",
            "options": [{"spelling": "leed"}, {"spelling": "led"}],
        }
    }
    entries = [
        {
            "original_word": "lead",
            "user_choice": "led",
            "context_before": "The ",
            "context_after": " pipe.",
            "was_user_correction": True,
        },
        {
            "original_word": "lead",
            "user_choice": "leed",
            "context_before": "The ",
            "context_after": " ship.",
            "was_user_correction": False,
            "original_decision_source": "hybrid",
            "original_confidence": 0.95,
        },
        {
            "original_word": "lead",
            "user_choice": "stale",
            "context_before": "The ",
            "context_after": " case.",
            "was_user_correction": True,
        },
    ]
    records = build_holdout_records(entries, canonical)
    assert len(records) == 2
    assert {record["choice"] for record in records} == {"led", "leed"}


def test_homograph_evidence_packet_includes_rules_and_examples() -> None:
    """Confirm evidence packets carry structured rule and learning context."""
    service = object.__new__(BookfixAIService)
    packet = service.build_homograph_evidence_packet(
        word="lead",
        context="The [lead] ship entered the harbor.",
        contextualized_options=[("leed", "foremost"), ("led", "metal")],
        rule_evidence={
            "hybrid": {
                "choice": "leed",
                "confidence": 0.95,
                "reason": "amod ship",
                "kind": "hybrid",
            }
        },
        best_guess="leed",
        detected_pos_tag="JJ",
        context_keywords={"leed": ["ship"], "led": ["pipe"]},
        learned_examples=[{"sentence": "The lead ship sailed.", "choice": "leed"}],
        contrasting_examples=[{"sentence": "The lead pipe bent.", "choice": "led"}],
    )

    assert packet["word"] == "lead"
    assert packet["candidates"][0]["choice"] == "leed"
    assert packet["rule_summary"][0]["choice"] == "leed"
    assert packet["learned_examples"][0]["choice"] == "leed"
    assert packet["contrasting_examples"][0]["choice"] == "led"
    assert packet["response_schema"]["choice"] == "one of option_spellings"


def test_nested_choice_payload_parses_compact_response() -> None:
    """Confirm compact nested choice payload parses into usable fields."""
    service = object.__new__(BookfixAIService)
    choice, reasoning, confidence, agrees = service._parse_choice_payload(
        {
            "id": 1,
            "decision": {
                "choice": "leed",
                "confidence": 0.91,
                "agrees_with_rules": False,
                "justification": "modifier of ship",
                "disagreement_reason": "rule set missed an attributive use",
            },
        },
        ["leed", "led"],
    )

    assert choice == "leed"
    assert reasoning == "modifier of ship Disagreement: rule set missed an attributive use"
    assert confidence == 0.91
    assert agrees is False


def test_choice_payload_rejects_missing_confidence() -> None:
    """Confirm incomplete AI output cannot inherit trusted default confidence."""
    service = object.__new__(BookfixAIService)

    choice, reasoning, confidence, agrees = service._parse_choice_payload(
        {
            "choice": "leed",
            "agrees_with_rules": True,
            "justification": "Lead modifies ship.",
        },
        ["leed", "led"],
    )

    assert choice is None
    assert reasoning == ""
    assert confidence == 0.0
    assert agrees is False


def test_choice_payload_rejects_string_boolean() -> None:
    """Confirm JSON strings cannot masquerade as agreement booleans."""
    service = object.__new__(BookfixAIService)

    choice, _, confidence, agrees = service._parse_choice_payload(
        {
            "choice": "leed",
            "confidence": 0.91,
            "agrees_with_rules": "false",
            "justification": "Lead modifies ship.",
            "disagreement_reason": "Rules missed syntax.",
        },
        ["leed", "led"],
    )

    assert choice is None
    assert confidence == 0.0
    assert agrees is False


def test_choice_payload_accepts_explicit_abstention() -> None:
    """Confirm ambiguous evidence produces a safe non-decision."""
    service = object.__new__(BookfixAIService)

    choice, reasoning, confidence, agrees, error = service._validate_choice_payload(
        {
            "abstain": True,
            "justification": "Context does not distinguish candidates.",
        },
        ["leed", "led"],
    )

    assert choice is None
    assert reasoning == "Context does not distinguish candidates."
    assert confidence == 0.0
    assert agrees is False
    assert error == "AI abstained"


def test_reviewed_learning_accepts_only_canonical_choice(tmp_path: Path) -> None:
    """Confirm reviewed choices persist only when spelling belongs to canonical lexicon."""
    storage = ChoicesLearningStorage(storage_dir=str(tmp_path))
    accepted = ChoiceLearningEntry.create(
        original_word="lead",
        lemma="lead",
        options=["leed", "led"],
        context_before="The ",
        context_after=" ship arrived.",
        user_choice="LEED",
        line_number=1,
    )
    rejected = ChoiceLearningEntry.create(
        original_word="lead",
        lemma="lead",
        options=["leed", "led"],
        context_before="The ",
        context_after=" ship arrived.",
        user_choice="invented",
        line_number=1,
    )

    assert storage.add_learning_entry(accepted) is True
    assert storage.add_learning_entry(rejected) is False
    assert len(storage.entries) == 1
    assert storage.entries[0].user_choice == "leed"


def test_ai_decision_is_not_learning_entry_without_review(tmp_path: Path) -> None:
    """Confirm an AI recommendation alone cannot enter reviewed learning storage."""
    storage = ChoicesLearningStorage(storage_dir=str(tmp_path))

    assert storage.entries == []


def test_contextualized_service_enforces_review_safe_contract(monkeypatch) -> None:
    """Confirm one reference-model response path accepts only safe structured decisions."""
    from bookfix.ai.service import AIResponse

    service = BookfixAIService(provider="ollama", model="qwen3:8b", max_retries=1)
    options = [("leed", "front or guide"), ("led", "metal")]
    monkeypatch.setattr(
        service,
        "_make_request",
        lambda prompt: AIResponse(
            True,
            '{"choice":"leed","confidence":0.91,"agrees_with_rules":true,"justification":"ship context"}',
        ),
    )
    accepted = service.analyze_contextualized_homograph(
        "lead", "The [lead] ship arrived.", options
    )
    assert accepted.success is True
    assert accepted.content == "leed"

    monkeypatch.setattr(
        service,
        "_make_request",
        lambda prompt: AIResponse(
            True,
            '{"abstain":true,"justification":"context is ambiguous"}',
        ),
    )
    abstained = service.analyze_contextualized_homograph(
        "lead", "The [lead] arrived.", options
    )
    assert abstained.success is False
    assert abstained.confidence == 0.0


def test_ollama_request_disables_thinking() -> None:
    """Confirm production Ollama requests disable Qwen3 hidden reasoning."""
    service = BookfixAIService(provider="ollama", model="qwen3:8b", rate_limit=0.0)
    response = MagicMock()
    response.json.return_value = {"response": "{}"}
    service.session.post = MagicMock(return_value=response)

    service._ollama_request("Choose one spelling.")

    payload = service.session.post.call_args.kwargs["json"]
    assert payload["think"] is False
