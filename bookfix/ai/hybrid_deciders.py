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


def _target_pattern(word: str, sentence: str) -> str:
    """Return regex matching only marked target, with single-word fallback.

    Args:
        word: Homograph text expected at target position.
        sentence: Context that normally contains ``[word]`` marker.

    Returns:
        Regex fragment matching marked occurrence or a whole unmarked word.
    """
    marked = rf"\[{re.escape(word)}\]"
    # Runtime contexts preserve brackets; direct unit calls may omit them.
    if re.search(marked, sentence, re.IGNORECASE):
        return marked
    return rf"\b{re.escape(word)}\b"


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
        r'\bthat\s+(?:can|could|will|would|shall|should|must|may|might)\s+live\b',  # modal between "that" and "live"
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
        True if noun pronunciation 'inva lid' should be chosen.
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


def _get_nli_definition(options_list: list, spelling: str) -> str:
    """Look up the NLI hypothesis string for a spelling from the options list.

    Checks nli_hypothesis first (short, model-optimised string stored in choices.json).
    Falls back to definition if nli_hypothesis is absent, then to spelling as last resort.
    Keeping nli_hypothesis separate from definition lets the review window show human-readable
    text while the NLI model receives the concise targeted string it performs best with.
    """
    for opt in (options_list or []):
        if opt.get("spelling") == spelling:
            return opt.get("nli_hypothesis") or opt.get("definition", spelling)
    return spelling


def nli_decide(nli, sentence: str, word: str, label_a: str, label_b: str, options_list: list) -> Tuple[str, str]:
    """
    Run RoBERTa NLI (zero-shot) to pick between two pronunciation hypotheses for a homograph.

    Hypothesis strings are read from the options list (choices.json definitions) so there is a
    single source of truth for what each pronunciation means — no separate hardcoded strings.

    Args:
        nli: The zero-shot classification pipeline (or None if disabled).
        sentence: The full context sentence containing the target word.
        word: The homograph word being decided (for logging in route).
        label_a: Pronunciation spelling for first hypothesis; its definition is looked up from options_list.
        label_b: Pronunciation spelling for second hypothesis; its definition is looked up from options_list.
        options_list: List of option dicts from LexiconLoader.get_options(word).

    Returns:
        Tuple (chosen_pronunciation, route_string) e.g. ("tair", "nli=tair(0.92)")
    """
    q_a = _get_nli_definition(options_list, label_a)
    q_b = _get_nli_definition(options_list, label_b)
    # If NLI pipeline not available, default to first hypothesis (label_a).
    if not nli:
        return label_a, "nli-disabled"
    try:
        result = nli(sentence, candidate_labels=[q_a, q_b], multi_label=False)
        scores = dict(zip(result["labels"], result["scores"]))
        if scores[q_a] > scores[q_b]:
            return label_a, f"nli={label_a}({scores[q_a]:.2f})"
        else:
            return label_b, f"nli={label_b}({scores[q_b]:.2f})"
    except Exception:
        # On any error (model issues, etc.) safely default to label_a.
        return label_a, "nli-error"


# ── 22 Word-Specific Deciders ────────────────────────────────────────────────────────

def decide_record(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'record': verb sense 're cord' vs noun sense 'rec urd'.

    Uses simple POS tag check; verb forms get 're cord', everything else 'rec urd'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for record).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("re cord", "pos-verb")
    """
    # Infinitive "to record" is always the verb sense regardless of spaCy's tag.
    # spaCy sometimes tags "record" as NNP after "to" — the preposition is reliable.
    if re.search(r'\bto\s+record\b', sentence.lower()):
        return "re cord", "regex-infinitive"
    # Verb tags indicate action sense.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "re cord", "pos-verb"
    # Default to noun sense for all other tags (including mis-tags).
    return "rec urd", "pos-noun"


def decide_records(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'records' (plural): verb → 're cords'; noun → 'rec urds'.

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
        Tuple of (pronunciation, route) e.g. ("re cords", "pos-verb")
    """
    # Strong context bias for known verb uses like "history records" even on NNS mistag.
    sent_lower = sentence.lower()
    if "history records" in sent_lower or re.search(r'\bit records\b', sent_lower):
        return "re cords", "pos-verb-context"

    # Verb for plural: if verb tag, or NNS but in core verbal dep position (mis-tag case).
    # Excluded nsubj and dobj: genuine noun "records" (medical/office records) is often
    # dobj or nsubj, so those deps are unreliable indicators of the verb sense.
    if tag in VERB_PRESENT or tag in VERB_PAST or (tag == "NNS" and dep in ("ROOT", "xcomp", "ccomp", "advcl", "relcl")):
        return "re cords", "pos-verb"
    # Default to noun plural.
    return "rec urds", "pos-noun"


def decide_close(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'close': verb → 'cloze'; adj/adv → 'close'; noun → 'close'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for close).
        sentence: Full sentence context used for proximity phrase checks.

    Returns:
        Tuple of (pronunciation, route) e.g. ("cloze", "pos-verb")
    """
    normalized = re.sub(r"[\[\]]", "", sentence.lower())
    target = _target_pattern("close", sentence.lower())

    # Adverbial proximity phrases such as "somewhere close" cannot be a verb.
    if re.search(r'\b(?:somewhere|nearby|quite|very|too)\s+close\b', normalized):
        return "close", "regex-proximity"
    # Closure subjects and manner verbs identify intransitive closing despite bad POS tags.
    closure_heads = r"(?:doors?|gates?|hatches?|lids?|shutters?|windows?)"
    closure_motion = r"(?:whir|slide|swing|slam|click|snap|roll|draw|pull)(?:s|ed|ing)?"
    if re.search(rf'\b{closure_heads}\s+{target}|\b{closure_motion}\s+{target}', sentence.lower()):
        return "cloze", "regex-intransitive-closure"
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
    Decide pronunciation for 'read': regex grammar first, then POS tag, default 'red'.

    Sentence regex catches grammatical frames that spaCy mis-tags.
    Order matters: perfect aspect is checked before modals because
    "must have read" matches both — perfect wins (past tense pronunciation).
    - Perfect aspect (have/has/had + 'read') → 'red' (past)
    - Passive (to be read) → 'red' (past)
    - Infinitive/modal (including contractions) + 'read' → 'reed' (present)
    POS tag fallback handles remaining clear cases.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for read).
        sentence: Full sentence context (used for grammar regex).

    Returns:
        Tuple of (pronunciation, route) e.g. ("red", "pos-past")
    """
    norm = sentence.lower()
    target = _target_pattern("read", norm)

    # Perfect aspect FIRST: have/has/had + "read" → past tense.
    # Must precede the modal check — "must have read" matches both patterns
    # but perfect aspect wins: it is always past tense pronunciation.
    # (?!to\b) excludes obligation phrases like "have to read" — those are present tense.
    if re.search(rf'\b(have|has|had)\s+(?!to\b)(?:\w+\s+){{0,2}}{target}', norm):
        return "red", "regex-perfect"

    # "being able to read" is capability, not passive voice, so keep present pronunciation.
    if re.search(rf'\b(?:am|is|are|was|were|be|been|being)\s+able\s+to\s+(?:\w+\s+){{0,2}}{target}', norm):
        return "reed", "regex-able-to-read"

    # Any local be-auxiliary chain makes target a passive participle.
    if re.search(rf'\b(?:am|is|are|was|were|be|been|being)\s+(?:\w+\s+){{0,2}}{target}', norm):
        return "red", "regex-passive"

    # Reporting subjects such as "the message read" use past pronunciation.
    if re.search(rf'\b(?:message|letter|notice|sign|headline|caption|text)\s+{target}', norm):
        return "red", "regex-reporting"

    # Nominal read constructions name an inspection, never a past-tense verb.
    if re.search(rf'\b(?:a|an|the)\s+(?:closer|close|quick|key|careful|first|second|final|full|thorough|fresh|initial)\s+{target}(?=\s|[.,;:!?]|$)', norm):
        return "reed", "regex-nominal-modifier"
    # Hyphen compounds and "get a read on" are noun phrases even when tagging fails.
    if re.search(rf'{target}\s*-\s*(?:out|outs|through)\b|\b(?:get|got|getting)\s+(?:a|an|the)\s+{target}\s+on\b', norm):
        return "reed", "regex-nominal-compound"

    # Past do-support carries tense on "did", leaving "read" in its base spelling.
    if re.search(rf'\bdid(?:n\'t|\s+not)?\s+(?:\w+\s+){{0,3}}{target}', norm):
        return "red", "regex-did-support"
    # Present do-support keeps present pronunciation despite unreliable tagging.
    if re.search(rf'\b(?:do|does)(?:n\'t|\s+not)?\s+(?:\w+\s+){{0,3}}{target}', norm):
        return "reed", "regex-present-do-support"

    # Infinitive "to read" → always present tense pronunciation.
    if re.search(rf'\bto\s+{target}', norm):
        return "reed", "regex-infinitive"

    # Modal auxiliary (including contractions) + "read" → present tense.
    # Contractions (couldn't, won't, etc.) are included because the apostrophe
    # breaks the word boundary and they would otherwise fall through to POS.
    if re.search(rf'\b(would|wouldn\'t|could|couldn\'t|should|shouldn\'t|will|won\'t|can|can\'t|might|mightn\'t|must|mustn\'t|shall|shan\'t|may)\s+(?:\w+\s+){{0,2}}{target}', norm):
        return "reed", "regex-modal"

    # "want/like/going/plan/need to read" patterns → present tense.
    if re.search(rf'\b(want|like|going|plan|need|seem|seems|seemed)\s+to\s+(?:\w+\s+)?{target}', norm):
        return "reed", "regex-want-to"

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
    # Keep marker for target-local collocations; heuristics normalize internally.
    norm = sentence.lower()
    target = _target_pattern("live", norm)

    # Unhyphenated live-in compounds retain verb pronunciation in imperfect source text.
    resident_heads = r"(?:girl\s*friend|boy\s*friend|partner|maid|nanny|carer|caregiver|tenant|employee|staff)"
    if re.search(rf'{target}\s+in\s+{resident_heads}\b', norm):
        return "liv", "regex-live-in-resident"

    # Broadcast frames make live an on-air adjective/adverb, not verb.
    if re.search(
        rf'\b(?:broadcast|broadcasting|stream|streaming|air(?:ing|ed)?)\s+(?:to\s+you\s+)?{target}\b',
        norm,
    ):
        return "lyve", "regex-live-broadcast-frame"
    if re.search(rf'\b(?:coming\s+to\s+you\s+)?{target}\s+from\b', norm):
        return "lyve", "regex-live-from-frame"
    if re.search(rf'\b{target}\s+on\s+air\b', norm):
        return "lyve", "regex-live-on-air"

    # Hyphenated broadcast compounds always use adjective pronunciation.
    if re.search(rf'{target}\s*-\s*(?:stream|streamed|streaming|broadcast|broadcasting)\b', norm):
        return "lyve", "regex-live-media-compound"

    # Media and event heads identify adjective/adverb sense regardless of location words.
    media_heads = r"(?:camera|feed|footage|broadcast|stream|coverage|performance|concert|transmission)"
    if re.search(rf'{target}(?:\s+[\w\'-]+){{0,2}}\s+{media_heads}\b', norm):
        return "lyve", "regex-live-media"

    # Living, active, and energized noun heads identify adjective sense across documents.
    adjective_heads = r"(?:book|person|people|animal|creature|specimen|audience|rounds?|ammunition|wire|circuit|current|microphone)"
    if re.search(rf'{target}(?:\s+[\w\'-]+)?\s+{adjective_heads}\b', norm):
        return "lyve", "regex-live-adjective-head"

    # Primary decision: use the new sentence-scanning heuristic.
    # This is deliberately first and comprehensive so that even when dep=="amod"
    # and tag=="JJ" the verb cases are caught via patterns like "live here" or "that live".
    if is_verb_context(tag, dep, head, sentence):
        # Guard the one idiom that looks like a verb frame but is actually adj: "go live".
        if not (head == "go" and re.search(rf'\bgo\s+{target}', norm)):
            return "liv", "pos-verb-heuristic"

    # 'go live' idiom for launch/broadcast: 'lyve'.
    # Explicitly checked after the verb heuristic so "go live in ..." (place) stays verb.
    if head == "go" and re.search(rf'\bgo\s*{target}', norm) and not re.search(rf'\bgo\s*{target}\s+in\b', norm):
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
    if re.search(rf'{target}\s+(?:person|people|body|specimen)\b', norm):
        return "lyve", "pos-live-adj-phrase"

    # Default to the verb sense for everything else (including most mis-tags).
    return "liv", "pos-default"


def decide_object(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'object': verb → 'ub-ject'; noun → 'objekt'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for object).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("ub-ject", "pos-verb")
    """
    # Verb tags indicate the stressed-first-syllable verb pronunciation.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "ub-ject", "pos-verb"
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
    Decide pronunciation for 'elaborate': verb → 'elaborayt'; adj → 'elaborit'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for elaborate).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("elaborayt", "pos-verb")
    """
    normalized = sentence.strip()
    # Standalone or vocative sentence openings are imperatives, not adjectives.
    if re.match(r'^[\s\"\'“”‘’]*\[?elaborate\]?(?:\s*,\s*[^,.!?]+)?[.!?\"\'”’]*$', normalized, re.IGNORECASE):
        return "elaborayt", "regex-imperative"
    # Verb tags indicate the verb pronunciation 'elaborayt'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "elaborayt", "pos-verb"
    # Default (adj and others) to 'elaborit'.
    return "elaborit", "pos-adj"


def decide_estimate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'estimate': verb → 'estim 8'; noun → 'estimit'.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (unused for estimate).
        sentence: Full sentence context (unused here).

    Returns:
        Tuple of (pronunciation, route) e.g. ("estim 8", "pos-verb")
    """
    # Verb tags indicate the verb pronunciation 'estim 8'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "estim 8", "pos-verb"
    # Default to noun pronunciation 'estimit' for other tags.
    return "estimit", "pos-noun"


def decide_wind(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """
    Decide pronunciation for 'wind': verb sense 'whined' (to coil/twist) vs noun sense 'wind' (moving air).

    Args:
        tag: Fine-grained POS tag from spaCy (e.g. 'VBG', 'NN').
        dep: Dependency relation of the token (e.g. 'ROOT', 'advcl', 'nsubj').
        head: Lowercased head word text.
        has_det: True if the token has a determiner child (e.g. "the wind").
        nli: Optional zero-shot NLI pipeline (not used for wind).
        sentence: Full sentence context for additional checks.

    Returns:
        Tuple of (pronunciation, route) where pronunciation is 'whined' or 'wind',
        and route describes the decision path for logging.
    """
    # Core verb rule: only return the verb pronunciation ('whined') when the tag
    # indicates a verb form AND the dependency is a core verbal governor.
    # This aligns exactly with the tightened complex_pos dep_rules for whined
    # (only ROOT/xcomp/ccomp with match_mode "all"). It prevents spaCy mis-tags
    # of noun "wind" as VBG/VBN in reduced clauses (e.g. "wind flinging", "wind rushing",
    # "Wind ripped") which commonly attach with advcl/relcl/acl.
    if (tag in VERB_PRESENT or tag in VERB_PAST) and dep in ("ROOT", "xcomp", "ccomp"):
        return "whined", "pos-verb-core"

    # Strong noun bias via determiner: phrases like "the wind", "a wind", or "this wind"
    # are almost always the noun sense. Prefer 'wind' even if spaCy mis-tagged the POS.
    if has_det:
        return "wind", "det-noun"

    # Default to noun for everything else. This includes:
    # - Correct noun tags (NN/NNS)
    # - Mis-tagged verbs in non-core dependencies (the common failure mode for these cases)
    # - Any other ambiguous or non-verbal attachments
    # The goal is to never let a non-core verbal attachment force the verb spelling for 'wind'.
    return "wind", "pos-noun"


def decide_lead(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str, options_list: list = None) -> Tuple[str, str]:
    """
    Decide pronunciation for 'lead' using tense, attributive syntax, and semantic fallback.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline (used for adj/NN cases).
        sentence: Full sentence context (passed to nli_decide).
        options_list: Options from LexiconLoader.get_options('lead') for NLI hypothesis lookup.

    Returns:
        Tuple of (pronunciation, route) e.g. ("led", "pos-verb-past") or nli result.
    """
    normalized = re.sub(r"[\[\]]", "", sentence.lower())
    marked = sentence.lower()
    target = _target_pattern("lead", marked)

    # Coordinated material siblings identify metallic lead, including hyphen chains.
    materials = r"(?:steel|plastic|copper|tin|iron|metal|glass|wood|alloy|brass|bronze|zinc)"
    connector = r"(?:\s*-\s*and\s*-\s*|\s+and\s+|\s*[,/]\s*)"
    if re.search(rf'\b{materials}{connector}{target}{connector}{materials}\b', marked):
        return "led", "regex-material-coordination"

    # Primary-role modifiers identify supervisory or first-position sense, not metal.
    role_heads = r"(?:engineer|developer|designer|investigator|scientist|analyst|researcher|technician|architect|officer|detective|counsel|singer|actor|hybrid|ai)"
    if re.search(rf'{target}\s+(?:[\w\'-]+\s+)?{role_heads}\b', marked):
        return "leed", "regex-primary-role"

    # A lead attached to a person or animal is a cable or leash, not metal.
    if re.search(r"\b(?:dog|puppy|horse|pet|animal)(?:'s|s)?\s+lead\b", normalized):
        return "leed", "regex-leash"
    # A lead followed by an object pronoun is the present-tense verb "guide".
    if re.search(r"\blead\s+(?:me|you|him|her|it|us|them)\b", normalized):
        return "leed", "regex-verb-object"
    # Proper-name objects and directional complements still form the verb frame.
    if re.search(r"\blead\s+\w+(?:\s+\w+){0,2}\s+(?:away|back|out|over|to|into|through)\b", normalized):
        return "leed", "regex-verb-direction"
    # A lead rein is an animal-control strap, not the metallic spelling.
    if re.search(r"\blead\s+rein\b", normalized):
        return "leed", "regex-lead-rein"
    # Possessive lead in resistance frames is guidance or leash-like control, not metal.
    if re.search(
        r"\b(?:struggl(?:e|ing|ed)|resist(?:s|ed|ing)?|fight(?:s|ed|ing)?|pull(?:s|ed|ing)?|push(?:es|ed|ing)?|tug(?:s|ged|ging)?)\s+against\s+(?:his|her|their|my|our|your)\s+lead\b",
        normalized,
    ):
        return "leed", "regex-guidance-lead"
    # Gratitude around lead usually points at clue/tip sense.
    if re.search(r"\b(?:thanks?|thank(?:s|ed|ing)?|appreciate(?:d|s|ing)?|grateful)\b.{0,24}\bfor\s+(?:the\s+)?lead\b", normalized):
        return "leed", "regex-tip-lead"
    # Common clue and advantage constructions identify the non-metal noun sense.
    if re.search(r"\blead\b.{0,35}\b(?:clue|hint|advantage|start|connection|given)\b", normalized):
        return "leed", "regex-clue-noun"
    # Passive or reporting constructions can place the clue word before "lead".
    if re.search(r"\b(?:given|got|received|provided|offered)\b.{0,35}\blead\b", normalized):
        return "leed", "regex-clue-noun-reversed"
    # Quality modifiers identify an investigative or informational lead.
    if re.search(rf'\b(?:best|strongest|only|promising|new|fresh|solid)\s+{target}', marked):
        return "leed", "regex-qualified-lead"
    # A standalone imperative or noun label is not the metallic spelling.
    if re.search(r"\blead\s*[.!?]\s*(?:i|you|we|he|she|they)\b", normalized):
        return "leed", "regex-standalone-lead"
    # Following or holding a person's lead names guidance or precedence.
    if re.search(r"\b(?:following|follow|take|took|taking|keep|kept|in)\b.{0,20}\blead\b", normalized):
        return "leed", "regex-guidance-lead"
    # Score and advantage verbs identify competitive lead rather than material lead.
    if re.search(rf'\b(?:build|built|cut|collapse|collapsed|collapsing|erase|erased|extend|extended|hold|held|lose|lost|narrow|narrowed)\b[^.!?]{{0,45}}{target}', marked):
        return "leed", "regex-advantage-lead"
    # Past copular framing fixes relative clauses whose present-form tag hides past narrative time.
    if re.search(rf'\b(?:was|were|had been)\b[^.!?]{{0,160}}\bone of (?:the )?(?:ones|people|those) who\s+{target}', marked):
        return "led", "regex-past-relative-clause"
    # Explicit past tense tag gets 'led'.
    if tag == "VBD":
        return "led", "pos-verb-past"
    # Present verb tags get 'leed'.
    if tag in VERB_PRESENT:
        return "leed", "pos-verb"
    # Attributive adjective parses such as "lead account" mean primary/front-position lead.
    if tag in ADJ_TAGS and dep in {"amod", "compound"}:
        return "leed", "jj-attributive-front-position"
    # For adjectives or nouns, fall back to NLI if available to disambiguate.
    if (tag in ADJ_TAGS or tag == "NN") and nli:
        return nli_decide(nli, sentence, "lead", "leed", "led", options_list)
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
        return "inva lid", "noun-heuristic"

    if tag in ADJ_TAGS:
        # "of" prepositional object is a special noun case even under JJ tag.
        if dep == "pobj" and head == "of":
            return "inva lid", "jj-pobj-of-noun"

        # The remaining JJ cases that also have certain deps + det are treated
        # as the noun sense (copular/predicative "being an invalid" etc.).
        # These are kept for when the heuristic above didn't trigger but the
        # structural signals are still strong.
        if has_det and dep in {"nsubj", "dobj", "pobj", "nsubjpass", "attr", "acomp", "appos"}:
            return "inva lid", "jj-but-noun"
        if dep in {"attr", "acomp", "appos"}:
            return "inva lid", "jj-attr-noun"

        # True adjective use (or any JJ that didn't match the noun patterns above).
        return "in-valid", "pos-adj"

    # Default non-adjective tag → noun sense.
    return "inva lid", "pos-noun"


_TEAR_EYES_AWAY = re.compile(
    r'\btear\b.{0,40}?\b(eyes?|gaze|attention|focus|sight)\b.{0,20}?\baway\b',
    re.IGNORECASE | re.DOTALL
)


def decide_tear(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str, options_list: list = None) -> Tuple[str, str]:
    """
    Decide pronunciation for 'tear': verb+eyes-away → 'tair'; verb+nli → nli; noun+through → 'tair'; noun+nli → nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for most cases).
        sentence: Full sentence context (for special pattern and nli_decide).
        options_list: Options from LexiconLoader.get_options('tear') for NLI hypothesis lookup.

    Returns:
        Tuple of (pronunciation, route) e.g. ("tair", "pos-tear-eyes-away")
    """
    normalized = re.sub(r"[\[\]]", "", sentence.lower())
    marked = sentence.lower()
    target = _target_pattern("tear", marked)

    # Hyphenated facial descriptions refer to tears from the eyes.
    if re.search(r"\btear\s*-\s*stained\b", normalized):
        return "teer", "regex-tear-stained"
    # Shedding or falling identifies liquid from an eye even when syntax is mis-tagged.
    if re.search(rf'\b(?:shed|sheds|shedding)\s+(?:a|one|another)?\s*{target}|{target}\s+(?:fell|falls|filled|fills|rolled|rolls|formed|welled)\b', marked):
        return "teer", "regex-eye-liquid"
    # Damage nouns take ripping pronunciation when followed by damaged material or origin.
    if re.search(rf'\b(?:a|an|the|small|large|ragged|fresh)\s+{target}\s+(?:in|of|along|across)\b', marked):
        return "tair", "regex-damage-noun"
    # Particles and physical objects identify ripping action despite weak POS evidence.
    if re.search(rf'{target}\s+(?:apart|down|off|open|through|up|your|my|his|her|its|our|their|flesh)\b', marked):
        return "tair", "regex-ripping-frame"
    # A direct object frame is the ripping verb, even when POS tagging fails.
    if re.search(r"\btear\s+(?:me|you|him|her|it|us|them)\b", normalized):
        return "tair", "regex-verb-object"
    # Verb forms: special "tear ... eyes away" pattern takes 'tair'; else NLI.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        if _TEAR_EYES_AWAY.search(sentence):
            return "tair", "pos-tear-eyes-away"
        return nli_decide(nli, sentence, "tear", "tair", "teer", options_list)
    # Noun "through" object gets 'tair'.
    if dep == "pobj" and head == "through":
        return "tair", "pos-pobj-through"
    # Otherwise NLI for noun sense disambiguation.
    return nli_decide(nli, sentence, "tear", "tair", "teer", options_list)


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
    normalized = sentence.lower()
    target = _target_pattern("polish", normalized)
    marked_match = re.search(r"\[([^\]]+)\]", sentence)
    # Marker preserves exact target capitalization despite lowercased lookup key.
    if marked_match:
        target_text = marked_match.group(1)
    else:
        target_match = re.search(r"\bpolish\b", sentence, re.IGNORECASE)
        target_text = target_match.group(0) if target_match else "polish"

    # Product/substance compounds outrank title capitalization in names and headings.
    product_heads = r"(?:knife|shoe|boot|furniture|silver|metal|car|floor|nail|wood|leather|brass|copper)"
    if re.search(rf'\b{product_heads}(?:\s+[\w\'-]+)?\s+{target}', normalized):
        return "pollish", "regex-product-compound"
    # Verb tags get 'pollish'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "pollish", "pos-verb"

    capitalized = bool(target_text and target_text[0].isupper())
    # Capitalized adjective modifying a noun denotes Polish nationality/origin.
    if capitalized and tag in ADJ_TAGS:
        return "pole-ish", "pos-adj"
    # Proper-noun language uses need nearby linguistic or nationality evidence.
    nationality_context = r"(?:poland|warsaw|krakow|language|nationality|citizen|community|people|speaks?|fluent|translate|translation)"
    if capitalized and tag == "NNP" and re.search(nationality_context, normalized):
        return "pole-ish", "proper-nationality-context"
    # Default to 'pollish' for nouns etc.
    return "pollish", "pos-default"


BASS_MUSIC_HEADS = {"case", "player", "guitar", "drum", "line", "clef", "man", "solo", "note"}
BASS_FISH_HEADS = {"boat", "fishing", "tournament", "lure", "angling", "farming"}
BASS_FISH_VERBS = {
    "caught", "catch", "fry", "frying", "fried", "cook", "cooking", "cooked",
    "ate", "eat", "eating", "hook", "hooked", "reel", "reeled", "land", "landed"
}


def decide_bass(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str, options_list: list = None) -> Tuple[str, str]:
    """
    Decide pronunciation for 'bass': compound+music → 'base'; compound+fish → 'bas'; verb+fish → 'bas'; else nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word (used for compound/verb heads).
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for fallback disambiguation).
        sentence: Full sentence context (passed to nli).
        options_list: Options from LexiconLoader.get_options('bass') for NLI hypothesis lookup.

    Returns:
        Tuple of (pronunciation, route) e.g. ("base", "pos-compound-music") or nli result.
    """
    normalized = re.sub(r"[\[\]]", "", sentence.lower())

    # Fixed musical collocations are more reliable than broad context keywords.
    if re.search(
        r"\b(?:bass\s+(?:line|guitar|drum|clef|player|solo|note|music|sound)|"
        r"(?:muted|electric|acoustic|double|upright)\s+bass)\b",
        normalized,
    ):
        return "base", "regex-music-collocation"
    # Compound modifier: check head word lists for music vs fish.
    if dep == "compound":
        if head in BASS_MUSIC_HEADS:
            return "base", "pos-compound-music"
        if head in BASS_FISH_HEADS:
            return "bas", "pos-compound-fish"
    # Head verb related to fish activity → 'bass'.
    if head in BASS_FISH_VERBS:
        return "bas", "pos-verb-fish"
    # Fallback to NLI using definitions from choices.json.
    if not nli:
        return "base", "nli-disabled"
    try:
        q_music = _get_nli_definition(options_list, "base")
        q_fish = _get_nli_definition(options_list, "bas")
        result = nli(sentence, candidate_labels=[q_music, q_fish], multi_label=False)
        scores = dict(zip(result["labels"], result["scores"]))
        if scores[q_fish] > 0.70:
            return "bas", f"nli=bas({scores[q_fish]:.2f})"
        return "base", f"nli=base({scores[q_music]:.2f})"
    except Exception:
        return "base", "nli-error"


_POSITIONAL_ROW = re.compile(r'\b(front|back|first|last|middle)\s+row\b', re.IGNORECASE)
_ROW_OF = re.compile(r'\brow\s+of\b', re.IGNORECASE)
_ROW_LINE = re.compile(r'\b(?:whole|entire|end\s+of|front\s+of|back\s+of)\s+(?:the\s+)?row\b', re.IGNORECASE)


def decide_row(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str, options_list: list = None) -> Tuple[str, str]:
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
    normalized = re.sub(r"[\[\]]", "", sentence.lower())

    # Determined argument nouns and negative invitations identify quarrelling sense.
    if re.search(r"\b(?:have|had|start|started|cause|caused|avoid|avoided|want|wanted)\s+(?:a|another|the)\s+row\b|\b(?:don\'t|do not)\s+let(?:\'s| us)\s+row\b", normalized):
        return "rau", "regex-argument"

    # Compound attachment → 'ro' (as in "row house").
    if dep == "compound":
        return "ro", "pos-compound"
    # npadvmod (e.g. "row after row") → 'ro'.
    if dep == "npadvmod":
        return "ro", "pos-npadvmod"
    # Verb tags → 'ro'.
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "ro", "pos-verb"
    # Line/sequence phrases like "whole row" and "end of the row" → 'ro'.
    if _ROW_LINE.search(normalized):
        return "ro", "pos-row-line"
    # Positional phrases like "front row" → 'ro'.
    if _POSITIONAL_ROW.search(normalized):
        return "ro", "pos-positional"
    # "row of" construction → 'ro'.
    if _ROW_OF.search(normalized):
        return "ro", "pos-row-of"
    # Fallback NLI for "row" (argument) vs "ro" (line).
    return nli_decide(nli, sentence, "row", "ro", "rau", options_list)


def decide_bowed(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str, options_list: list = None) -> Tuple[str, str]:
    """
    Decide pronunciation for 'bowed': VBN+no-heads → 'boed'; else nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for fallback).
        sentence: Full sentence context (for heads check and nli).
        options_list: Options from LexiconLoader.get_options('bowed') for NLI hypothesis lookup.

    Returns:
        Tuple of (pronunciation, route) e.g. ("boed", "pos-vbn-deformation") or nli result.
    """
    normalized = re.sub(r"[\[\]]", "", sentence.lower())

    # "bowed her/his head" is a deliberate gesture, despite frequent VBN mistags.
    if re.search(r"\bbowed\s+(?:my|your|his|her|its|our|their|the)\s+head\b", normalized):
        return "boughed", "regex-gesture-head"
    # Lowered heads and human-agent directional bows describe posture or gesture.
    if re.search(r"\bheads?\s+(?:was|were|is|are)?\s*bowed\b|\b(?:person|man|woman|waiter|guest|visitor|priest|reverend|he|she|they)\s+bowed\s+(?:at|before|over|to|toward)\b", normalized):
        return "boughed", "regex-lowered-head-or-gesture"
    # Structures and body shapes curved by force use deformation pronunciation.
    if re.search(r"\b(?:back|body|neck|shoulders?|wings?|beam|board|shelf|roof|wall|metal|wood)\s+(?:was|were|is|are|stood|lay|lying)?\s*bowed(?:\s+(?:inward|outward|under))?\b", normalized):
        return "boed", "regex-deformation"
    # Past-tense human actions such as "bowed elaborately" are gestures.
    if tag in VERB_PAST and not re.search(r"\b(?:not|never)\s+bowed\b", normalized):
        return "boughed", "regex-gesture-past"
    # VBN without "head(s)" in sentence → deformation sense 'boed'.
    if tag == "VBN" and not re.search(r'\bheads?\b', sentence, re.IGNORECASE):
        return "boed", "pos-vbn-deformation"
    # Otherwise use NLI to choose between bent vs bowed (greeting).
    return nli_decide(nli, sentence, "bowed", "boed", "boughed", options_list)


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
    normalized = re.sub(r"[\[\]]", "", sentence.lower())

    # Mechanical objects and directional complements identify past tense of "wind".
    if re.search(
        r"\bwound\s+(?:his|her|the|a|an|my|your|their|its)?\s*"
        r"(?:window|windows|clock|watch|spring|ribbon|thread|yarn|rope|coil|way)\b",
        normalized,
    ) or re.search(r"\bwound\s+(?:around|up|down|through|along|over|under)\b", normalized) or re.search(
        r"\bwound\b.{0,35}\b(?:window|wyndo|corridor|road|path|track|street|passage|trail|river|route)\b.{0,20}\b(?:down|around|through|along)?\b",
        normalized,
    ):
        return "wow'nd", "regex-wind-object"
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


def decide_recreation(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str, options_list: list = None) -> Tuple[str, str]:
    """
    Decide pronunciation for 'recreation' using leisure phrases before NLI fallback.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (used for non-compound cases).
        sentence: Full sentence context (passed to nli).
        options_list: Options from LexiconLoader.get_options('recreation') for NLI hypothesis lookup.

    Returns:
        Tuple of (pronunciation, route) e.g. ("wreckre-ation", "pos-compound-leisure") or NLI result.
    """
    normalized = re.sub(r"[\[\]]", "", sentence.lower())

    # Relaxation and leisure collocations identify the hobby pronunciation.
    if re.search(
        r"\brecreation\s+(?:and|or)\s+(?:relaxation|enjoyment|amusement|leisure|fun)\b"
        r"|\b(?:for|during|in)\s+recreation\b",
        normalized,
    ):
        return "wreckre-ation", "regex-leisure"
    # Compound (e.g. "recreation room" meaning leisure) uses the leisure spelling.
    if dep == "compound":
        return "wreckre-ation", "pos-compound-leisure"
    # Otherwise NLI between rebuilding and leisure pronunciations.
    return nli_decide(nli, sentence, "recreation", "re-kreation", "wreckre-ation", options_list)


def decide_jesus(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str, options_list: list = None) -> Tuple[str, str]:
    """
    Decide pronunciation for 'Jesus': biblical/exclamation vs Spanish name via nli.

    Args:
        tag: Fine-grained POS tag from spaCy.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: NLI pipeline (required for this decider).
        sentence: Full sentence context (passed to nli).
        options_list: Options from LexiconLoader.get_options('Jesus') for NLI hypothesis lookup.

    Returns:
        Tuple of (pronunciation, route) from nli_decide.
    """
    # Always delegate to NLI for biblical vs personal name disambiguation.
    return nli_decide(nli, sentence, "jesus", "Jesus", "heysous", options_list)


def decide_generic(
    tag: str,
    dep: str,
    head: str,
    has_det: bool,
    nli,
    sentence: str,
    options_list: list = None,
) -> Tuple[str, str]:
    """Generic hybrid decider for words without a hand-tuned DECIDERS entry.

    Uses spaCy POS tag to match against the 'pos' field on each choices.json option.
    Falls back to NLI if the tag is ambiguous and nli_hypothesis strings are present.
    Used for new words (buffet, crooked, dogged, intimate, minute) until custom deciders
    are written or the word is resolved via complex_pos dep_rules alone.

    Args:
        tag: Fine-grained spaCy POS tag.
        dep: Dependency relation.
        head: Lowercased head word.
        has_det: Whether a determiner child is present.
        nli: Optional NLI pipeline.
        sentence: Full sentence context.
        options_list: Options from LexiconLoader.get_options(word).

    Returns:
        Tuple of (pronunciation, route).
    """
    if not options_list:
        return options_list[0]["spelling"] if options_list else ("", "generic-empty")

    # Map spaCy fine tag to coarse category
    coarse = None
    if tag in VERB_PRESENT or tag in VERB_PAST:
        coarse = "VERB"
    elif tag in ("NN", "NNS", "NNP", "NNPS"):
        coarse = "NOUN"
    elif tag == "JJ":
        coarse = "ADJ"

    if coarse:
        matches = [
            opt for opt in options_list
            if (opt.get("pos") or "").upper().startswith(coarse)
        ]
        if len(matches) == 1:
            return matches[0]["spelling"], "generic-pos"

    # Ambiguous or unknown tag — try NLI if available and hypotheses exist
    if nli and len(options_list) == 2:
        a, b = options_list[0], options_list[1]
        if a.get("nli_hypothesis") and b.get("nli_hypothesis"):
            return nli_decide(nli, sentence, "", a["spelling"], b["spelling"], options_list)

    # Last resort: return first option (lowest confidence; will surface for review)
    return options_list[0]["spelling"], "generic-default"


DECIDERS = {
    "record": decide_record,
    "records": decide_records,  # dedicated plural handler returning re ords/rec urds + NNS-mistag gate
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
