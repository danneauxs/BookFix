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


def nli_decide(nli, sentence: str, word: str, q_a: str, label_a: str, q_b: str, label_b: str) -> Tuple[str, str]:
    """Run RoBERTa NLI to pick between two hypotheses.

    Returns (pronunciation, route_string).
    """
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
        return label_a, f"nli-error"


# ── 22 Word-Specific Deciders ────────────────────────────────────────────────────────

def decide_record(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """record: verb → rekord; noun → rekkurd."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "rekord", "pos-verb"
    return "rekkurd", "pos-noun"


def decide_close(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """close: verb → cloze; adj/adv → close; noun → close."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "cloze", "pos-verb"
    if tag in ADJ_TAGS or tag in ADV_TAGS:
        return "close", "pos-adj/adv"
    return "close", "pos-default"


def decide_read(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """read: past/VBN → red; present → reed; default → red."""
    if tag in VERB_PAST or tag == "VBN":
        return "red", "pos-past"
    if tag in VERB_PRESENT:
        return "reed", "pos-verb"
    return "red", "pos-default"


def decide_live(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """live: verb → liv; adj/adv → lyve; noun → liv."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "liv", "pos-verb"
    if tag in ADJ_TAGS or tag in ADV_TAGS:
        return "lyve", "pos-adj/adv"
    return "liv", "pos-default"


def decide_object(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """object: verb → ubjekt; noun → objekt."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "ubjekt", "pos-verb"
    return "objekt", "pos-noun"


def decide_present(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """present: verb → prezent; noun/adj → present."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "prezent", "pos-verb"
    return "present", "pos-noun/adj"


def decide_sow(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """sow: verb → soh; noun → sow."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "soh", "pos-verb"
    return "sow", "pos-noun"


def decide_resume(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """resume: verb → rezoom; noun → resume."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "rezoom", "pos-verb"
    return "resume", "pos-noun"


def decide_refuse(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """refuse: verb → refuze; noun → refuse."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "refuze", "pos-verb"
    return "refuse", "pos-noun"


def decide_elaborate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """elaborate: verb → elaboreight; adj → elaborit."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "elaboreight", "pos-verb"
    return "elaborit", "pos-adj"


def decide_estimate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """estimate: verb → estimeight; noun → estimit."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "estimeight", "pos-verb"
    return "estimit", "pos-noun"


def decide_wind(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """wind: verb → why'nd; noun → win'd."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "why'nd", "pos-verb"
    return "win'd", "pos-noun"


def decide_lead(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """lead: VBD → led; verb → leed; adj/nn+nli → nli decision; noun → led."""
    if tag == "VBD":
        return "led", "pos-verb-past"
    if tag in VERB_PRESENT:
        return "leed", "pos-verb"
    if (tag in ADJ_TAGS or tag == "NN") and nli:
        return nli_decide(nli, sentence, "lead",
            "a person in a leading/supervising role",
            "leed",
            "the metal lead (Pb)",
            "led")
    return "led", "pos-noun"


def decide_invalid(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """invalid: special adj rules; else noun."""
    if tag in ADJ_TAGS:
        if dep == "pobj" and head == "of":
            return "invalid", "jj-pobj-of-noun"
        if has_det and dep in {"nsubj", "dobj", "pobj", "nsubjpass"}:
            return "invalid", "jj-but-noun"
        return "in-valid", "pos-adj"
    return "invalid", "pos-noun"


_TEAR_EYES_AWAY = re.compile(
    r'\btear\b.{0,40}?\b(eyes?|gaze|attention|focus|sight)\b.{0,20}?\baway\b',
    re.IGNORECASE | re.DOTALL
)


def decide_tear(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """tear: verb+eyes-away → tair; verb+nli → nli; noun+through → tair; noun+nli → nli."""
    if tag in VERB_PRESENT or tag in VERB_PAST:
        if _TEAR_EYES_AWAY.search(sentence):
            return "tair", "pos-tear-eyes-away"
        return nli_decide(nli, sentence, "tear",
            "an action of ripping, shredding, or physically pulling something apart",
            "tair",
            "eyes watering, filling with tears, or about to cry",
            "teer")
    if dep == "pobj" and head == "through":
        return "tair", "pos-pobj-through"
    return nli_decide(nli, sentence, "tear",
        "a rip, hole, cut, wound, injury, or physical damage in material or flesh, or a rift, gap, tunnel, throughway, or transitional opening",
        "tair",
        "a teardrop, teardrop shape, liquid from the eye, or emotional response",
        "teer")


def decide_polish(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """polish: capitalized+NNP → pole-ish; verb → pollish; adj → pole-ish; default → pollish."""
    word_in_sent = next((w for w in sentence.split() if w.lower() == "polish"), None)
    if word_in_sent and word_in_sent[0].isupper() and tag == "NNP":
        return "pole-ish", "cap-proper"
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "pollish", "pos-verb"
    if tag in ADJ_TAGS:
        return "pole-ish", "pos-adj"
    return "pollish", "pos-default"


BASS_MUSIC_HEADS = {"case", "player", "guitar", "drum", "line", "clef", "man", "solo", "note"}
BASS_FISH_HEADS = {"boat", "fishing", "tournament", "lure", "angling", "farming"}
BASS_FISH_VERBS = {
    "caught", "catch", "fry", "frying", "fried", "cook", "cooking", "cooked",
    "ate", "eat", "eating", "hook", "hooked", "reel", "reeled", "land", "landed"
}


def decide_bass(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """bass: compound+music → base; compound+fish → bass; verb+fish → bass; else nli."""
    if dep == "compound":
        if head in BASS_MUSIC_HEADS:
            return "base", "pos-compound-music"
        if head in BASS_FISH_HEADS:
            return "bass", "pos-compound-fish"
    if head in BASS_FISH_VERBS:
        return "bass", "pos-verb-fish"
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
    """row: compound → ro; npadvmod → ro; verb → ro; positional → ro; row-of → ro; else nli."""
    if dep == "compound":
        return "ro", "pos-compound"
    if dep == "npadvmod":
        return "ro", "pos-npadvmod"
    if tag in VERB_PRESENT or tag in VERB_PAST:
        return "ro", "pos-verb"
    if _POSITIONAL_ROW.search(sentence):
        return "ro", "pos-positional"
    if _ROW_OF.search(sentence):
        return "ro", "pos-row-of"
    return nli_decide(nli, sentence, "row",
        "a line, sequence, or series of things arranged in order, or in a row meaning one after another consecutively",
        "ro",
        "a loud verbal argument, quarrel, or shouting match between people",
        "rau")


def decide_bowed(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """bowed: VBN+no-heads → boed; else nli."""
    if tag == "VBN" and not re.search(r'\bheads?\b', sentence, re.IGNORECASE):
        return "boed", "pos-vbn-deformation"
    return nli_decide(nli, sentence, "bowed",
        "a physical object or structure (shelf, fence, roof, wood, limb) has been bent or curved by weight or force",
        "boed",
        "a person deliberately lowered their head or body as a gesture of respect or greeting",
        "boughed")


def decide_wound(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """wound: not-verb → woond; VB → woond; else → wow'nd."""
    if tag not in VERB_PAST and tag not in VERB_PRESENT:
        return "woond", "pos-noun"
    if tag == "VB":
        return "woond", "pos-vb-injure"
    return "wow'nd", "pos-verb-wind"


def decide_recreation(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """recreation: compound → rek-reation; else nli."""
    if dep == "compound":
        return "rek-reation", "pos-compound-leisure"
    return nli_decide(nli, sentence, "recreation",
        "the act of recreating or rebuilding something that previously existed",
        "re-kreation",
        "a hobby, pastime, leisure activity, sport, or something done for enjoyment and relaxation",
        "rek-reation")


def decide_jesus(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
    """Jesus: biblical/exclamation vs Spanish name via nli."""
    return nli_decide(nli, sentence, "jesus",
        "the biblical Christian figure or used as a religious exclamation",
        "Jesus",
        "a Latin American or Spanish personal name (Jesús)",
        "heysous")


DECIDERS = {
    "record": decide_record,
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
