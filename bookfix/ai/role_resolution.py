"""Grammar-first candidate filtering for homograph pronunciation choices."""

from dataclasses import dataclass
import re
from typing import Iterable, Optional, Set


@dataclass(frozen=True)
class SyntacticResolution:
    """Describe whether grammar uniquely identifies one pronunciation candidate."""

    choice: Optional[str]
    confidence: float
    reason: str
    needs_semantic_resolution: bool = False


def resolve_syntactic_choice(token, dep_info, doc, options: Iterable[dict]) -> SyntacticResolution:
    """Return a choice only when target grammar uniquely permits one candidate.

    Args:
        token: Target POS token produced by the parser.
        dep_info: Dependency data for the target token.
        doc: Parsed sentence containing the target token.
        options: Canonical pronunciation option dictionaries.

    Returns:
        A resolution, or a semantic-resolution marker for same-role meanings.
    """
    option_list = list(options or [])
    role = _token_role(token, dep_info)
    # Parsing failed to identify a stable role, so no candidate is safe.
    if role is None:
        return SyntacticResolution(None, 0.0, "No reliable syntactic role")

    matches = [option for option in option_list if role in _option_roles(option)]
    # One role-compatible candidate is grammar-determined.
    if len(matches) == 1:
        return SyntacticResolution(
            matches[0]["spelling"],
            0.98,
            f"Grammar uniquely identifies {role.lower()} candidate",
        )
    # Lexicon lacks an option for this parser role.
    if len(matches) < 2:
        return SyntacticResolution(None, 0.0, f"No candidate declares {role.lower()} role")

    # Same-role verbs can still be resolved by explicitly marked inflection.
    if role == "VERB":
        form = _verb_form(token, doc)
        form_matches = [
            option
            for option in matches
            if form and form in option.get("grammar", {}).get("verb_forms", [])
        ]
        # One candidate declares the observed form.
        if len(form_matches) == 1:
            return SyntacticResolution(
                form_matches[0]["spelling"],
                0.98,
                f"Grammar uniquely identifies {form} verb form",
            )

    return SyntacticResolution(
        None,
        0.0,
        f"Multiple candidates share {role.lower()} role; meaning required",
        needs_semantic_resolution=True,
    )


def _token_role(token, dep_info) -> Optional[str]:
    """Map parser POS and dependency evidence to one coarse grammatical role."""
    tag = (getattr(token, "pos_tag", "") or "").upper()
    category = (getattr(token, "pos_category", "") or "").upper()
    dependency = (getattr(dep_info, "dep_relation", "") or "").lower()
    # Modifier attachment is stronger than a lexical tag for contextual adverbs.
    if dependency in {"advmod", "amod", "acomp", "attr"} or category in {"ADJ", "ADV"}:
        return "MODIFIER"
    # Nominal parser evidence identifies a noun role.
    if category in {"NOUN", "PROPN"} or tag.startswith("NN"):
        return "NOUN"
    # Verb parser evidence identifies a verbal role.
    if category in {"VERB", "AUX"} or tag.startswith("VB"):
        return "VERB"
    return None


def _option_roles(option: dict) -> Set[str]:
    """Return coarse roles declared by one canonical lexicon option."""
    labels = set(re.split(r"[/,;\\s]+", (option.get("pos") or "").upper()))
    roles: Set[str] = set()
    # Adjectives and adverbs both modify another constituent for this decision.
    if labels & {"ADJECTIVE", "ADVERB", "ADJ", "ADV"}:
        roles.add("MODIFIER")
    # Noun labels map directly to nominal syntax.
    if "NOUN" in labels:
        roles.add("NOUN")
    # Verb labels map directly to verbal syntax.
    if "VERB" in labels:
        roles.add("VERB")
    return roles


def _verb_form(token, doc) -> Optional[str]:
    """Return a reliably marked English verb form, otherwise leave tense unresolved."""
    if doc is None:
        return None
    target = doc[token.index]
    tag = (getattr(token, "pos_tag", "") or "").upper()
    # Past finite morphology distinguishes past pronunciation.
    if tag == "VBD":
        return "past"
    # Participial morphology distinguishes perfect and passive pronunciation.
    if tag == "VBN":
        return "participle"

    child_words = {child.text.lower() for child in target.children}
    # Infinitival and modal auxiliaries explicitly fix the base-form pronunciation.
    if "to" in child_words or child_words & {
        "can", "could", "may", "might", "must", "shall", "should", "will", "would",
    }:
        return "base"
    # A root base verb without a subject is an imperative, not a finite past reading.
    if tag == "VB" and target.dep_ == "ROOT" and not any(
        child.dep_ in {"nsubj", "nsubjpass"} for child in target.children
    ):
        return "imperative"
    return None
