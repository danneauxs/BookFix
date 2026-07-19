"""Evidence records and conservative scoring for homograph choices."""

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class EvidenceRecord:
    """Describe one rule match supporting a candidate pronunciation."""

    word: str
    candidate: str
    kind: str
    match_type: str
    confidence: float
    weight: float
    reason: str = ""
    pattern: str = ""
    hard: bool = False
    source: str = "runtime"
    family: str = ""

    @property
    def score(self) -> float:
        """Return weighted confidence contributed by this evidence record."""
        return max(0.0, self.confidence) * max(0.0, self.weight)


@dataclass
class CandidateScore:
    """Aggregate evidence and decision metadata for one candidate spelling."""

    candidate: str
    total_score: float = 0.0
    evidence: List[EvidenceRecord] = field(default_factory=list)
    hard_hits: int = 0
    soft_hits: int = 0
    family_scores: Dict[str, float] = field(default_factory=dict)

    def add(self, record: EvidenceRecord) -> None:
        """Add evidence without double-counting one evidence family."""
        self.evidence.append(record)
        family = record.family or record.kind
        previous_score = self.family_scores.get(family, 0.0)
        record_score = record.score
        # POS, dependency, and hybrid outputs share parser evidence. Keep only
        # their strongest result so one parse cannot inflate confidence.
        if record_score > previous_score:
            self.total_score += record_score - previous_score
            self.family_scores[family] = record_score
        if record.hard:
            self.hard_hits += 1
        else:
            self.soft_hits += 1


class ChoiceEvidenceScorer:
    """Score rule evidence while preserving conservative conflict handling."""

    DEFAULT_WEIGHTS = {
        "phrase": 6.5,
        "complex_pos": 5.0,
        "dependency": 5.5,
        "hybrid": 3.5,
        "keyword_strong": 6.0,
        "learned_phrase": 5.75,
        "learned": 2.0,
        "pos": 1.5,
        "semantic": 0.8,
        "entity": 0.8,
        "keyword": 0.6,
    }

    HARD_SOURCES = {
        "phrase",
        "complex_pos",
        "dependency",
        "hybrid",
        "keyword_strong",
        "learned_phrase",
    }

    EVIDENCE_FAMILIES = {
        "complex_pos": "structural",
        "dependency": "structural",
        "hybrid": "structural",
        "pos": "structural",
        "phrase": "context",
        "keyword_strong": "context",
        "learned_phrase": "context",
        "learned": "learning",
        "semantic": "semantic",
        "entity": "semantic",
        "keyword": "semantic",
    }

    def __init__(self, config: Optional[Dict] = None):
        """Initialize scorer thresholds from application configuration."""
        thresholds = (config or {}).get("Thresholds", {})
        self.min_score = float(thresholds.get("EVIDENCE_AUTO_APPLY_MIN_SCORE", 2.4))
        self.min_margin = float(thresholds.get("EVIDENCE_MIN_MARGIN", 0.75))
        self.hard_conflict_floor = float(
            thresholds.get("EVIDENCE_HARD_CONFLICT_CONFIDENCE", 0.88)
        )

    def build_scores(
        self,
        word: str,
        all_rules: Dict[str, Dict],
        options: Optional[Iterable[str]] = None,
    ) -> Dict[str, CandidateScore]:
        """Aggregate rule results into one score object per candidate spelling."""
        scores = {option: CandidateScore(option) for option in (options or [])}
        for source, rule in (all_rules or {}).items():
            candidate = rule.get("choice")
            if not candidate:
                continue
            if candidate not in scores:
                scores[candidate] = CandidateScore(candidate)
            kind = rule.get("kind", source)
            weight = float(rule.get("weight", self.DEFAULT_WEIGHTS.get(kind, 0.0)))
            hard = bool(rule.get("hard", kind in self.HARD_SOURCES))
            scores[candidate].add(
                EvidenceRecord(
                    word=word,
                    candidate=candidate,
                    kind=kind,
                    match_type=rule.get("match_type", source),
                    confidence=float(rule.get("confidence", 0.0)),
                    weight=weight,
                    reason=rule.get("reason", ""),
                    pattern=rule.get("pattern", ""),
                    hard=hard,
                    source=rule.get("source", "runtime"),
                    family=self._evidence_family(kind, rule.get("reason", "")),
                )
            )
        return scores

    def _evidence_family(self, kind: str, reason: str) -> str:
        """Return independent evidence family for one rule result."""
        # NLI is semantic evidence, not a second syntactic parse.
        if kind == "hybrid" and "nli" in reason.lower():
            return "semantic"
        return self.EVIDENCE_FAMILIES.get(kind, kind)

    def choose(
        self,
        word: str,
        all_rules: Dict[str, Dict],
        options: Optional[Iterable[str]] = None,
    ) -> Tuple[Optional[Dict], Optional[str], Dict[str, CandidateScore]]:
        """Return safe winner, source, and score ledger for current rule evidence."""
        scores = self.build_scores(word, all_rules, options)
        ranked = sorted(
            (score for score in scores.values() if score.evidence),
            key=lambda item: item.total_score,
            reverse=True,
        )
        if not ranked:
            return None, None, scores

        winner = ranked[0]
        runner = ranked[1] if len(ranked) > 1 else None
        margin = winner.total_score - runner.total_score if runner else winner.total_score

        hard_records = [record for score in ranked for record in score.evidence if record.hard]
        context_hard_choices = {
            record.candidate
            for record in hard_records
            if record.kind in {"phrase", "keyword_strong", "learned_phrase"}
            if record.confidence >= self.hard_conflict_floor
        }
        structural_hard_choices = {
            record.candidate
            for record in hard_records
            if record.kind in {"complex_pos", "dependency", "hybrid"}
            and record.confidence >= self.hard_conflict_floor
        }
        # Two contradictory exact context rules also require verification.
        if len(context_hard_choices) > 1:
            return None, None, scores

        context_override = None
        if len(context_hard_choices) == 1:
            context_candidate = next(iter(context_hard_choices))
            # Sense clues cannot override contradictory grammatical structure.
            if (
                structural_hard_choices
                and context_candidate not in structural_hard_choices
            ):
                return None, None, scores
            context_records = [
                record
                for record in scores[context_candidate].evidence
                if record.kind in {"phrase", "keyword_strong", "learned_phrase"}
            ]
            # Curated exact context is more specific than broad POS/NLI agreement.
            if context_records:
                context_override = context_candidate

        # Two contradictory structural readings remain unsafe without exact context.
        if len(structural_hard_choices) > 1 and context_override is None:
            return None, None, scores

        # Replace broad structural winner when one trusted exact-context candidate exists.
        if context_override is not None:
            winner = scores[context_override]
            ranked = [winner] + [score for score in ranked if score is not winner]
            # Broad POS/NLI evidence is intentionally not treated as a competing
            # candidate once curated exact context identifies one spelling.
            runner = None
            margin = winner.total_score

        strongest = max(winner.evidence, key=lambda record: record.score)
        learned_is_corroborated = (
            strongest.kind == "learned"
            and len(winner.evidence) >= 2
            and strongest.confidence >= 0.85
        )
        if winner.total_score < self.min_score and strongest.kind not in {
            "complex_pos",
            "hybrid",
            "keyword_strong",
            "phrase",
            "learned_phrase",
        } and not learned_is_corroborated:
            return None, None, scores
        if runner and margin < self.min_margin:
            return None, None, scores

        decision = {
            "choice": winner.candidate,
            "confidence": min(0.99, max(strongest.confidence, winner.total_score / 6.0)),
            "reason": self._format_reason(winner, margin),
            "score": winner.total_score,
            "margin": margin,
        }
        return decision, strongest.kind, scores

    def choose_best_available(
        self,
        word: str,
        all_rules: Dict[str, Dict],
        options: Iterable[str],
        priors: Optional[Dict[str, int]] = None,
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Select one canonical candidate after normal safety gates reject consensus.

        Args:
            word: Homograph being classified.
            all_rules: Rule evidence collected for the target occurrence.
            options: Canonical spellings permitted for the occurrence.
            priors: Counts from reviewed choices used to resolve score ties.

        Returns:
            A canonical decision and source label, or ``(None, None)`` when no
            canonical options were supplied.
        """
        canonical_options = [option for option in options if option]
        if not canonical_options:
            return None, None

        scores = self.build_scores(word, all_rules, canonical_options)
        prior_counts = {choice: int((priors or {}).get(choice, 0)) for choice in canonical_options}
        ranked = sorted(
            (scores[choice] for choice in canonical_options),
            key=lambda score: score.candidate.casefold(),
        )
        # Preserve strongest available evidence, then reviewed priors, never input order.
        winner = max(
            ranked,
            key=lambda score: (
                score.total_score,
                max((record.score for record in score.evidence), default=0.0),
                prior_counts[score.candidate],
            ),
        )
        strongest = max(winner.evidence, key=lambda record: record.score, default=None)
        source = strongest.kind if strongest else "canonical_tie"
        confidence = strongest.confidence if strongest else 0.0
        reason = (
            "Canonical resolution from strongest available rule evidence"
            if strongest
            else "Canonical resolution from reviewed prior or deterministic lexical tie"
        )
        return {
            "choice": winner.candidate,
            "confidence": confidence,
            "reason": reason,
            "score": winner.total_score,
            "margin": 0.0,
        }, source

    def _format_reason(self, winner: CandidateScore, margin: float) -> str:
        """Build a compact explanation showing evidence and score margin."""
        evidence = ", ".join(
            f"{record.kind}:{record.reason or record.match_type}"
            for record in winner.evidence
        )
        return f"Weighted evidence {winner.total_score:.2f}, margin {margin:.2f}: {evidence}"
