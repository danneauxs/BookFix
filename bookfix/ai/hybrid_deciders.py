"""
Hybrid homograph disambiguation engine.

Uses spaCy transformer (en_core_web_trf) for POS/dependency, RoBERTa-large-MNLI NLI for
hard cases. 22 hand-tuned per-word deciders for accuracy on common homographs.

Deciders return (pronunciation_spelling, route_explanation).
"""

import re
from typing import Optional, Tuple

# POS tag categories for rules
VERB_PRESENT = {"VB", "VBP", "VBZ", "VBG", "VBN"}
VERB_PAST = {"VBD"}
ADJ_TAGS = {"JJ", "JJR", "JJS"}
ADV_TAGS = {"RB", "RBR", "RBS"}


def is_verb_context(tag: str, dep: str, head: str, sentence: str) -> bool:
    """Return True if the token is likely the verb sense of 'live' (to liv).

    Supplements spaCy's often-wrong tag (frequently JJ) and dep (frequently amod)
    by using verb-like dependency frames plus sentence-level look-ahead/look-behind
    cues for common verb frames: "that live here", "live longer than", "do somehow live",
    "people that live", etc.

    This is the core of the requested heuristic that scans context beyond pure
    whitespace or spaCy POS.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        sentence: Context sentence (may contain [live] brackets).

    Returns:
        True if 'liv' (verb) should be chosen.
    """
    # Normalize sentence for reliable pattern matching (strip target brackets).
    norm = re.sub(r'[\[\]]', '', sentence.lower())

    # 1. Verb-clause dependency frames are strong signals for verb, even under JJ mis-tag.
    # Covers "to live", "live longer", relative clauses "that live", "advcl" infinitives, etc.
    verb_clause_deps = {"ROOT", "xcomp", "ccomp", "advcl", "relcl", "acl"}
    if dep in verb_clause_deps:
        # Non-obvious branch: we trust the dep over the tag here because the parser
        # often mis-tags the verb as JJ but still assigns a correct clausal dep.
        return True

    # 2. If the syntactic head is a clear verbal auxiliary or infinitive marker,
    # treat as verb. E.g. heads like "do", "had", "to" in "had to live", "do live".
    verb_heads = {"do", "does", "did", "can", "could", "will", "would", "must",
                  "have", "has", "had", "be", "is", "are", "was", "were", "to"}
    if head in verb_heads:
        return True

    # 3. Sentence-level heuristic: scan for common verb complement/relative patterns
    # around the target word. This provides the "look ahead/behind" the user requested.
    # These patterns catch the exact failing cases even when dep == "amod".
    verb_patterns = [
        r'\bthat\s+live\b',                    # relative: "people that live here"
        r'\blive\s+(here|there|longer|long|in|on|with|for|to|as)\b',  # "live here", "live longer"
        r'\blive\s+than\b',                    # "live longer than me"
        r'\bdo\s+.*?\blive\b',                 # "if you do somehow live"
        r'\bpeople\s+.*?\blive\b',             # "fifty thousand people ... live"
        r'\byou\s+.*?\blive\b',                # "if you ... live longer"
        r'\bsomehow\s+live\b',
        r'\blive\s+longer\b',
    ]
    for pat in verb_patterns:
        if re.search(pat, norm):
            # Non-obvious: we return True for verb even if the immediate dep looks adjectival.
            return True

    # 4. Fall back to the tag only if nothing else matched (original simple behavior).
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return True

    return False


def is_noun_context(tag: str, dep: str, head: str, has_det: bool, sentence: str) -> bool:
    """Return True if the token is likely the noun sense of 'invalid' (a disabled person).

    Provides sentence-scanning heuristic for bare/copular noun uses such as
    "an invalid.", "being an invalid", "as an invalid" that spaCy often tags JJ+amod.

    This complements the dep_rules in the JSON (which cannot see full sentence context).

    Args:
        tag: Fine-grained POS tag.
        dep: Dependency relation.
        head: Head word (lowercased).
        has_det: Whether a determiner child is present.
        sentence: Context sentence (may contain [invalid]).

    Returns:
        True if noun pronunciation 'invalid' should be chosen.
    """
    norm = re.sub(r'[\[\]]', '', sentence.lower())

    # Strong noun cues via surface pattern (the requested heuristic scanning).
    # "an invalid" or "a invalid" (with or without following period) almost always
    # means the disabled-person noun, regardless of what spaCy tagged the token.
    if re.search(r'\ban? invalid\b', norm):
        return True
    if re.search(r'\binvalid\s*\.\s*$', norm) or re.search(r'\binvalid\s*\.', norm):
        return True
    if re.search(r'\b(being an invalid|as an invalid)\b', norm):
        return True

    # Dep-based noun positions (extended from prior fixes). These still help when
    # the parse is correct.
    noun_deps = {"nsubj", "dobj", "pobj", "attr", "appos", "conj", "nsubjpass", "ROOT"}
    if dep in noun_deps:
        return True
    if has_det and dep in {"nsubj", "dobj", "pobj", "attr", "acomp", "appos"}:
        return True

    return False


def nli_decide(nli, sentence: str, word: str, q_a: str, label_a: str, q_b: str, label_b: str) -> Tuple[str, str]:
    """
    Run RoBERTa NLI (zero-shot) to pick between two pronunciation hypotheses for a homograph.

    Used by several deciders as fallback when POS rules are insufficient.

    Args:
        nli: The zero-shot classification pipeline (or None if disabled).
        sentence: The full context sentence containing the target word.
        word: The homograph word being decided (for logging in route).
        q_a: First hypothesis/question string for NLI.
        label_a: Pronunciation to return if q_a wins.
        q_b: Second hypothesis/question string for NLI.
        label_b: Pronunciation to return if q_b wins.

    Returns:
        Tuple (chosen_pronunciation, route_string) e.g. ("tair", "nli=tair(0.92)")
    """
    # If NLI pipeline not available, default to first hypothesis (label_a).
    if not nli:
        return label_a, f"nli-disabled"
    try:
        result = nli(sentence, candidate_labels=[q_a, q_b], multi_label=False)
        scores = dict(zip(result["labels"], result["scores"]))
        if scores[q_a] > scores[q_b]:
            return label_a, f"nli={label_a}({scores[q_a]:.2f})"
        else:
            return label_b, f"nli={label_b}({scores[q_b]:.2f})"
    except Exception:
        # On any error (model issues, etc.) safely default to label_a.
        return label_a, f"nli-error"


# ── 22 Word-Specific Deciders ────────────────────────────────────────────────────────

def decide_record(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'record': verb sense 'rekord' vs noun sense 'rekkurd'.

    Uses simple POS tag check; verb forms get 'rekord', everything else 'rekkurd'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for record).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("rekord", "pos-verb")
    """
    # Verb tags indicate action sense.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "rekord", "pos-verb"
    # Default to noun sense for all other tags (including mis-tags).
    return "rekkurd", "pos-noun"


def decide_records(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'records' (plural): verb → 'rekords'; noun → 'rekkurds'.

    Includes special case for NNS mis-tags on verbs in clausal positions
    (e.g. spaCy tagging verb "records" as NNS in "history records").

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for records).
        sentence: Full sentence context (used for special phrase check).

    Returns:
        Tuple of (pronunciation, route) e.g. ("rekords", "pos-verb")
    """
    # Strong context bias for known verb uses like "history records" even on NNS mistag.
    sent_lower = sentence.lower()
    if "history records" in sent_lower or re.search(r'\bit records\b', sent_lower):
        return "rekords", "pos-verb-context"

    # Verb for plural: if verb tag, or NNS but in core verbal dep position (mis-tag case).
    if tag in VERB_PRESENT or tag in VERB_PAST or (tag == "NNS" and dep in ("ROOT", "xcomp", "ccomp", "advcl", "relcl", "nsubj", "dobj")):
        return "rekords", "pos-verb"
    # Default to noun plural.
    return "rekkurds", "pos-noun"


def decide_close(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'close': verb → 'cloze'; adj/adv → 'close'; noun → 'close'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for close).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("cloze", "pos-verb")
    """
    # Verb tags indicate the 'cloze' pronunciation.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "cloze", "pos-verb"
    # Adjective or adverb tags get the 'close' pronunciation.
    if tag in ADJ_TAGS or tag in ADV_TAGS:
        return "close", "pos-adj/adv"
    # Default (including noun and other tags) to 'close'.
    return "close", "pos-default"


def decide_read(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'read': past/VBN → 'red'; present → 'reed'; default → 'red'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for read).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("red", "pos-past")
    """
    # Past tense or VBN participle uses the 'red' pronunciation.
    if tag in VERB_PAST or tag == "VBN":
        return "red", "pos-past"
    # Present tense verb forms use 'reed'.
    if tag in VERB_PRESENT:
        return "reed", "pos-verb"
    # Default for nouns, adjectives, etc. to 'red'.
    return "red", "pos-default"


def decide_live(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    live: verb → liv; adj/adv → lyve; noun → liv.

    Uses a robust context-aware heuristic (is_verb_context) that performs
    dependency checks plus sentence scanning (look-ahead/look-behind) for
    verb cues. This protects against spaCy's frequent JJ + amod mis-tags on
    true verbs like "people that live here" and "live longer than me".

    The heuristic is the primary decision path; adjective branch is guarded
    to never override a detected verb context.

    Args:
        tag: Fine-grained POS tag.
        dep: Dependency relation.
        head: Head word (lowercased).
        has_det: Has determiner child.
        nli: NLI pipeline (unused for live).
        sentence: Context sentence for heuristics.

    Returns:
        (pronunciation, route)
    """
    # Normalize once for all pattern checks (removes [live] brackets).
    norm = re.sub(r'[\[\]]', '', sentence.lower())

    # Primary decision: use the new sentence-scanning heuristic.
    # This is deliberately first and comprehensive so that even when dep=="amod"
    # and tag=="JJ" the verb cases are caught via patterns like "live here" or "that live".
    if is_verb_context(tag, dep, head, sentence):
        # Guard the one idiom that looks like a verb frame but is actually adj: "go live".
        if not (head == "go" and "go live" in norm):
            return "liv", "pos-verb-heuristic"

    # 'go live' idiom for launch/broadcast: 'lyve'.
    # Explicitly checked after the verb heuristic so "go live in ..." (place) stays verb.
    if head == "go" and re.search(r'\bgo\s*live\b', norm, re.IGNORECASE) and not re.search(r'\bgo\s*live\s+in\b', norm, re.IGNORECASE):
        return "lyve", "pos-go-live-idiom"

    # Adjective/adverb 'lyve': only when the heuristic did NOT claim verb,
    # and the attachment is consistent with modification (amod/advmod/compound)
    # or a clear predicative adjective slot (with matching tag).
    # The extra "not is_verb_context" guard is redundant after the early return
    # above but kept for clarity and future maintenance.
    if dep in ("amod", "compound", "advmod") or ((tag in ADJ_TAGS or tag in ADV_TAGS) and dep in ("acomp", "attr")):
        if not is_verb_context(tag, dep, head, sentence):
            return "lyve", "pos-adj"

    # Phrase-level bias for common "live person/people/body/specimen" as the alive sense.
    if re.search(r'\blive (person|people|body|specimen)', norm, re.IGNORECASE):
        return "lyve", "pos-live-adj-phrase"

    # Default to the verb sense for everything else (including most mis-tags).
    return "liv", "pos-default"


def decide_object(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'object': verb → 'ubjekt'; noun → 'objekt'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for object).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("ubjekt", "pos-verb")
    """
    # Verb tags indicate the stressed-first-syllable verb pronunciation.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "ubjekt", "pos-verb"
    # Default to noun pronunciation for other tags.
    return "objekt", "pos-noun"


def decide_present(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'present': verb → 'prezent'; noun/adj → 'present'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for present).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("prezent", "pos-verb")
    """
    # Verb tags indicate the verb pronunciation 'prezent'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "prezent", "pos-verb"
    # Default to noun/adj pronunciation 'present' for other tags.
    return "present", "pos-noun/adj"


def decide_sow(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'sow': verb → 'soh'; noun → 'sow'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for sow).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("soh", "pos-verb")
    """
    # Verb tags indicate the verb pronunciation 'soh'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "soh", "pos-verb"
    # Default to noun pronunciation 'sow' for other tags.
    return "sow", "pos-noun"


def decide_resume(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'resume': verb → 'rezoom'; noun → 'resume'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for resume).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("rezoom", "pos-verb")
    """
    # Verb tags indicate the verb pronunciation 'rezoom'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "rezoom", "pos-verb"
    # Default to noun pronunciation 'resume' for other tags.
    return "resume", "pos-noun"


def decide_refuse(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'refuse': verb → 'refuze'; noun → 'refuse'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for refuse).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("refuze", "pos-verb")
    """
    # Verb tags indicate the verb pronunciation 'refuze'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "refuze", "pos-verb"
    # Default to noun pronunciation 'refuse' for other tags.
    return "refuse", "pos-noun"


def decide_elaborate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'elaborate': verb → 'elaboreight'; adj → 'elaborit'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for elaborate).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("elaboreight", "pos-verb")
    """
    # Verb tags indicate the verb pronunciation 'elaboreight'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "elaboreight", "pos-verb"
    # Default (adj and others) to 'elaborit'.
    return "elaborit", "pos-adj"


def decide_estimate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'estimate': verb → 'estimeight'; noun → 'estimit'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for estimate).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("estimeight", "pos-verb")
    """
    # Verb tags indicate the verb pronunciation 'estimeight'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "estimeight", "pos-verb"
    # Default to noun pronunciation 'estimit' for other tags.
    return "estimit", "pos-noun"


def decide_wind(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'wind': verb sense 'why'nd' (to coil/twist) vs noun sense 'win'd' (moving air).

    Args:
        tag: Fine-grained POS tag from spaCy (e.g. 'VBG', 'NN').
        dep: Dependency relation of the token (e.g. 'ROOT', 'advcl', 'nsubj').
        head: Lowercased head word text.
        has_det: True if the token has a determiner child (e.g. "the wind").
        nli: Optional zero-shot NLI pipeline (not used for wind).
        sentence: Full sentence context for additional checks.

    Returns:
        Tuple of (pronunciation, route) where pronunciation is 'why'nd' or 'win'd',
        and route describes the decision path for logging.
    """
    # Core verb rule: only return the verb pronunciation ('why'nd') when the tag
    # indicates a verb form AND the dependency is a core verbal governor.
    # This aligns exactly with the tightened complex_pos dep_rules for why'nd
    # (only ROOT/xcomp/ccomp with match_mode "all"). It prevents spaCy mis-tags
    # of noun "wind" as VBG/VBN in reduced clauses (e.g. "wind flinging", "wind rushing",
    # "Wind ripped") which commonly attach with advcl/relcl/acl.
    if (tag in VERB_PRESENT or tag in VERB_PAST) and dep in ("ROOT", "xcomp", "ccomp"):
        return "why'nd", "pos-verb-core"

    # Strong noun bias via determiner: phrases like "the wind", "a wind", or "this wind"
    # are almost always the noun sense. Prefer 'win'd' even if spaCy mis-tagged the POS.
    if has_det:
        return "win'd", "det-noun"

    # Default to noun for everything else. This includes:
    # - Correct noun tags (NN/NNS)
    # - Mis-tagged verbs in non-core dependencies (the common failure mode for these cases)
    # - Any other ambiguous or non-verbal attachments
    # The goal is to never let a non-core verbal attachment force the verb spelling for 'wind'.
    return "win'd", "pos-noun"


def decide_lead(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'lead': VBD → 'led'; verb → 'leed'; adj/nn + nli → nli decision; noun → 'led'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (used for adj/NN cases).
        sentence: Full sentence context (passed to nli_decide).

    Returns:
        Tuple of (pronunciation, route) e.g. ("led", "pos-verb-past") or nli result.
    """
    # Explicit past tense tag gets 'led'.
    if tag == "VBD":
        return "led", "pos-verb-past"
    # Present verb tags get 'leed'.
    if tag in VERB_PRESENT:
        return "leed", "pos-verb"
    # For adjectives or nouns, fall back to NLI if available to disambiguate.
    if (tag in ADJ_TAGS or tag == "NN") and nli:
        return nli_decide(nli, sentence, "lead",
            "a person in a leading/supervising role",
            "leed",
            "the metal lead (Pb)",
            "led")
    # Default to noun sense 'led'.
    return "led", "pos-noun"


def decide_invalid(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    invalid: noun 'invalid' (disabled person) vs adj 'in-valid' (not valid).

    The primary path is now the sentence-scanning is_noun_context heuristic
    which detects "an invalid.", "being an invalid" etc. even when spaCy
    assigns JJ + amod. This is the context heuristic requested to go beyond
    pure spaCy tag/dep (and the limited dep_rules in the JSON).

    Args:
        tag, dep, head, has_det, nli, sentence: standard decider parameters.

    Returns:
        (pronunciation, route)
    """
    # Run the noun heuristic first. It looks for surface patterns ("an invalid")
    # and common noun deps. This catches the bare-NP cases that previously
    # fell through to the adj branch because of amod mis-parses.
    if is_noun_context(tag, dep, head, has_det, sentence):
        return "invalid", "noun-heuristic"

    if tag in ADJ_TAGS:
        # "of" prepositional object is a special noun case even under JJ tag.
        if dep == "pobj" and head == "of":
            return "invalid", "jj-pobj-of-noun"

        # The remaining JJ cases that also have certain deps + det are treated
        # as the noun sense (copular/predicative "being an invalid" etc.).
        # These are kept for when the heuristic above didn't trigger but the
        # structural signals are still strong.
        if has_det and dep in {"nsubj", "dobj", "pobj", "nsubjpass", "attr", "acomp", "appos"}:
            return "invalid", "jj-but-noun"
        if dep in {"attr", "acomp", "appos"}:
            return "invalid", "jj-attr-noun"

        # True adjective use (or any JJ that didn't match the noun patterns above).
        return "in-valid", "pos-adj"

    # Default non-adjective tag → noun sense.
    return "invalid", "pos-noun"


_TEAR_EYES_AWAY = re.compile(
    r'\btear\b.{0,40}?\b(eyes?|gaze|attention|focus|sight)\b.{0,20}?\baway\b',
    re.IGNORECASE | re.DOTALL
)


def decide_tear(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'tear': verb+eyes-away → 'tair'; verb+nli → nli; noun+through → 'tair'; noun+nli → nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for most cases).
        sentence: Full sentence context (for special pattern and nli_decide).

    Returns:
        Tuple of (pronunciation, route) e.g. ("tair", "pos-tear-eyes-away")
    """
    # Verb forms: special "tear ... eyes away" pattern takes 'tair'; else NLI.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        if _TEAR_EYES_AWAY.search(sentence):
            return "tair", "pos-tear-eyes-away"
        return nli_decide(nli, sentence, "tear",
            "an action of ripping, shredding, or physically pulling something apart",
            "tair",
            "eyes watering, filling with tears, or about to cry",
            "teer")
    # Noun "through" object gets 'tair'.
    if dep == "pobj" and head == "through":
        return "tair", "pos-pobj-through"
    # Otherwise NLI for noun sense disambiguation.
    return nli_decide(nli, sentence, "tear",
        "a rip, hole, cut, wound, injury, or physical damage in material or flesh, or a rift, gap, tunnel, throughway, or transitional opening",
        "tair",
        "a teardrop, teardrop shape, liquid from the eye, or emotional response",
        "teer")


def decide_polish(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'polish': capitalized+NNP → 'pole-ish'; verb → 'pollish'; adj → 'pole-ish'; default → 'pollish'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for polish).
        sentence: Full sentence context (used for capitalization check).

    Returns:
        Tuple of (pronunciation, route) e.g. ("pole-ish", "cap-proper")
    """
    # Detect capitalized proper-noun usage of "Polish" (the nationality/language).
    word_in_sent = next((w for w in sentence.split() if w.lower() == "polish"), None)
    if word_in_sent and word_in_sent[0].isupper() and tag == "NNP":
        return "pole-ish", "cap-proper"
    # Verb tags get 'pollish'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "pollish", "pos-verb"
    # Adjective tags get 'pole-ish'.
    if tag in ADJ_TAGS:
        return "pole-ish", "pos-adj"
    # Default to 'pollish' for nouns etc.
    return "pollish", "pos-default"


BASS_MUSIC_HEADS = {"case", "player", "guitar", "drum", "line", "clef", "man", "solo", "note"}
BASS_FISH_HEADS = {"boat", "fishing", "tournament", "lure", "angling", "farming"}
BASS_FISH_VERBS = {
    "caught", "catch", "fry", "frying", "fried", "cook", "cooking", "cooked",
    "ate", "eat", "eating", "hook", "hooked", "reel", "reeled", "land", "landed"
}


def decide_bass(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'bass': compound+music → 'base'; compound+fish → 'bass'; verb+fish → 'bass'; else nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word (used for compound/verb heads).
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for fallback disambiguation).
        sentence: Full sentence context (passed to nli).

    Returns:
        Tuple of (pronunciation, route) e.g. ("base", "pos-compound-music") or nli result.
    """
    # Compound modifier: check head word lists for music vs fish.
    if dep == "compound":
        if head in BASS_MUSIC_HEADS:
            return "base", "pos-compound-music"
        if head in BASS_FISH_HEADS:
            return "bass", "pos-compound-fish"
    # Head verb related to fish activity → 'bass'.
    if head in BASS_FISH_VERBS:
        return "bass", "pos-verb-fish"
    # Fallback to NLI if no nli available.
    if not nli:
        return "base", "nli-disabled"
    try:
        q_music = "low-pitched sound, bass tones in music, a bass instrument (guitar, drum, etc.), or a bass musician"
        q_fish = "a species of fish (largemouth bass, sea bass, striped bass, etc.) caught in fishing"
        result = nli(sentence, candidate_labels=[q_music, q_fish], multi_label=False)
        scores = dict(zip(result["labels"], result["scores"]))
        if scores[q_fish] > 0.70:
            return "bass", f"nli=bass({scores[q_fish]:.2f})"
        return "base", f"nli=base({scores[q_music]:.2f})"
    except Exception:
        return "base", "nli-error"


_POSITIONAL_ROW = re.compile(r'\b(front|back|first|last|middle)\s+row\b', re.IGNORECASE)
_ROW_OF = re.compile(r'\brow\s+of\b', re.IGNORECASE)


def decide_row(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'row': compound → 'ro'; npadvmod → 'ro'; verb → 'ro'; positional → 'ro'; row-of → 'ro'; else nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for fallback).
        sentence: Full sentence context (for patterns and nli).

    Returns:
        Tuple of (pronunciation, route) e.g. ("ro", "pos-compound") or nli result.
    """
    # Compound attachment → 'ro' (as in "row house").
    if dep == "compound":
        return "ro", "pos-compound"
    # npadvmod (e.g. "row after row") → 'ro'.
    if dep == "npadvmod":
        return "ro", "pos-npadvmod"
    # Verb tags → 'ro'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "ro", "pos-verb"
    # Positional phrases like "front row" → 'ro'.
    if _POSITIONAL_ROW.search(sentence):
        return "ro", "pos-positional"
    # "row of" construction → 'ro'.
    if _ROW_OF.search(sentence):
        return "ro", "pos-row-of"
    # Fallback NLI for "row" (argument) vs "ro" (line).
    return nli_decide(nli, sentence, "row",
        "a line, sequence, or series of things arranged in order, or in a row meaning one after another consecutively",
        "ro",
        "a loud verbal argument, quarrel, or shouting match between people",
        "rau")


def decide_bowed(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'bowed': VBN+no-heads → 'boed'; else nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for fallback).
        sentence: Full sentence context (for heads check and nli).

    Returns:
        Tuple of (pronunciation, route) e.g. ("boed", "pos-vbn-deformation") or nli result.
    """
    # VBN without "head(s)" in sentence → deformation sense 'boed'.
    if tag == "VBN" and not re.search(r'\bheads?\b', sentence, re.IGNORECASE):
        return "boed", "pos-vbn-deformation"
    # Otherwise use NLI to choose between bent vs bowed (greeting).
    return nli_decide(nli, sentence, "bowed",
        "a physical object or structure (shelf, fence, roof, wood, limb) has been bent or curved by weight or force",
        "boed",
        "a person deliberately lowered their head or body as a gesture of respect or greeting",
        "boughed")


def decide_wound(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'wound': noun/injury → 'woond'; past of 'wind' (coil) → 'wow'nd'; special case for 'wound its way'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for wound).
        sentence: Full sentence context (used for special idiom check).

    Returns:
        Tuple of (pronunciation, route) e.g. ("woond", "pos-noun")
    """
    # Special case for the common verb idiom "wound its way" (past of 'wind').
    # This overrides even if spaCy mis-tags as NNS/NN (as seen in logs for "A tube ... wound its way").
    # User confirmed treating "wound the clock" / "wound its way" as past of 'wind' (wow'nd) is acceptable.
    if re.search(r'\bwound its way\b', sentence, re.IGNORECASE):
        return "wow'nd", "pos-verb-wind-its-way"

    # Non-verb tags default to noun/injury sense 'woond'.
    if tag not in VERB_PAST and tag not in VERB_PRESENT:
        return "woond", "pos-noun"
    # Bare "VB" (base form) in this context treated as injure sense 'woond'.
    if tag == "VB":
        return "woond", "pos-vb-injure"
    # Otherwise (VBD etc.) treat as past of 'wind' → 'wow'nd'.
    return "wow'nd", "pos-verb-wind"


def decide_recreation(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'recreation': compound → 'rek-reation'; else nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for non-compound cases).
        sentence: Full sentence context (passed to nli).

    Returns:
        Tuple of (pronunciation, route) e.g. ("rek-reation", "pos-compound-leisure") or nli result.
    """
    # Compound (e.g. "recreation room" meaning leisure) uses 'rek-reation'.
    if dep == "compound":
        return "rek-reation", "pos-compound-leisure"
    # Otherwise NLI between "re-kreation" (rebuilding) and "rek-reation" (leisure).
    return nli_decide(nli, sentence, "recreation",
        "the act of recreating or rebuilding something that previously existed",
        "re-kreation",
        "a hobby, pastime, leisure activity, sport, or something done for enjoyment and relaxation",
        "rek-reation")


def decide_jesus(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'Jesus': biblical/exclamation vs Spanish name via nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (required for this decider).
        sentence: Full sentence context (passed to nli).

    Returns:
        Tuple of (pronunciation, route) from nli_decide.
    """
    # Always delegate to NLI for biblical vs personal name disambiguation.
    return nli_decide(nli, sentence, "jesus",
        "the biblical Christian figure or used as a religious exclamation",
        "Jesus",
        "a Latin American or Spanish personal name (Jesús)",
        "heysous")


DECIDERS = {
    "record": decide_record,
    "records": decide_records,  # dedicated plural handler returning rekords/rekkurds + NNS-mistag gate
    "close": decide_close,
    "read": decide_read,
    "live": decide_live,
    "object": decide_object,
    "present": decide_present,
    "sow": decide_sow,
    "resume": decide_resume,
    "refuse": decide_refuse,
    "elaborate": decide_elaborate,
    "estimate": decide_estimate,
    "wind": decide_wind,
    "lead": decide_lead,
    "invalid": decide_invalid,
    "tear": decide_tear,
    "polish": decide_polish,
    "row": decide_row,
    "bass": decide_bass,
    "bowed": decide_bowed,
    "wound": decide_wound,
    "recreation": decide_recreation,
    "jesus": decide_jesus,
}

NLI_WORDS = {"row", "bass", "bowed", "recreation", "jesus", "tear", "lead"}
