"""Build a trusted, canonical holdout set from reviewed choices decisions."""

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional


TRUSTED_DECISION_SOURCES = {"hybrid", "complex_pos", "keyword_strong", "llm"}


def load_canonical_choices(path: Optional[str] = None) -> Dict[str, Dict]:
    """Load choices.json into a lowercase word-to-entry mapping.

    Args:
        path: Optional choices.json path; defaults to the project data file.

    Returns:
        Mapping from lowercase homograph to its canonical choices entry.
    """
    choices_path = Path(path) if path else Path(__file__).parent.parent.parent / "data" / "choices.json"
    entries = json.loads(choices_path.read_text(encoding="utf-8"))
    return {entry["word"].lower(): entry for entry in entries}


def canonicalize_choice(word: str, choice: str, canonical: Dict[str, Dict]) -> Optional[str]:
    """Return canonical spelling for a word-choice pair, or None when stale.

    Args:
        word: Homograph whose spelling is being checked.
        choice: User or runtime spelling to validate.
        canonical: Lowercase word-to-entry mapping from choices.json.

    Returns:
        Canonical spelling with original casing, or None for stale data.
    """
    entry = canonical.get(word.lower())
    if not entry:
        return None
    for option in entry.get("options", []):
        if option.get("spelling", "").lower() == choice.lower():
            return option["spelling"]
    return None


def load_adjudications(path: Optional[str] = None) -> Dict[str, Dict]:
    """Load manual benchmark adjudications keyed by source timestamp.

    Args:
        path: Optional JSON path; defaults to the active holdout adjudications file.

    Returns:
        Mapping from reviewed-record timestamp to adjudication metadata.
    """
    adjudications_path = (
        Path(path)
        if path
        else Path(__file__).parent.parent.parent
        / ".ai_learning"
        / "choices_holdout_adjudications.json"
    )
    if not adjudications_path.exists():
        return {}
    return json.loads(adjudications_path.read_text(encoding="utf-8"))


def is_trusted_review(entry: Dict, canonical: Dict[str, Dict], min_confidence: float) -> bool:
    """Return whether one learning record is a valid reviewed holdout example.

    Args:
        entry: Raw reviewed learning record.
        canonical: Canonical choices mapping used to reject stale spellings.
        min_confidence: Minimum confidence for accepted, non-corrected records.

    Returns:
        True when record has context, canonical spelling, and trusted provenance.
    """
    word = str(entry.get("original_word", "")).strip()
    choice = str(entry.get("user_choice", "")).strip()
    if not word or not choice or not (entry.get("context_before", "").strip() or entry.get("context_after", "").strip()):
        return False
    if canonicalize_choice(word, choice, canonical) is None:
        return False
    if bool(entry.get("was_user_correction")):
        return True
    return (
        entry.get("original_decision_source") in TRUSTED_DECISION_SOURCES
        and float(entry.get("original_confidence") or 0.0) >= min_confidence
    )


def build_holdout_records(
    entries: Iterable[Dict],
    canonical: Dict[str, Dict],
    min_confidence: float = 0.88,
    adjudications: Optional[Dict[str, Dict]] = None,
) -> List[Dict]:
    """Create deduplicated canonical holdout records from reviewed decisions.

    Args:
        entries: Raw reviewed learning records.
        canonical: Lowercase word-to-entry mapping from choices.json.
        min_confidence: Minimum confidence for accepted, non-corrected records.
        adjudications: Manual benchmark metadata keyed by source timestamp.

    Returns:
        Sorted canonical JSON-compatible holdout records.
    """
    records = []
    seen = set()
    for entry in entries:
        if not is_trusted_review(entry, canonical, min_confidence):
            continue
        word = str(entry["original_word"])
        choice = canonicalize_choice(word, str(entry["user_choice"]), canonical)
        context_before = str(entry.get("context_before", ""))
        context_after = str(entry.get("context_after", ""))
        key = (word.lower(), choice.lower(), context_before, context_after)
        if key in seen:
            continue
        seen.add(key)
        record = {
                "word": canonical[word.lower()]["word"],
                "choice": choice,
                "options": [
                    option["spelling"]
                    for option in canonical[word.lower()].get("options", [])
                ],
                "context": f"{context_before}[{word}]{context_after}",
                "context_before": context_before,
                "context_after": context_after,
                "pos_tag": entry.get("pos_tag", ""),
                "dep_info": entry.get("dep_info"),
                "review_type": (
                    "user_correction"
                    if entry.get("was_user_correction")
                    else "user_accepted_high_confidence"
                ),
                "source_timestamp": entry.get("timestamp", ""),
                "original_decision_source": entry.get("original_decision_source", ""),
                "original_confidence": entry.get("original_confidence", 0.0),
            }
        record.update((adjudications or {}).get(record["source_timestamp"], {}))
        records.append(record)
    return sorted(records, key=lambda item: (item["word"].lower(), item["source_timestamp"]))


def write_holdout(records: Iterable[Dict], output_path: str) -> int:
    """Write holdout records as JSONL and return the number written.

    Args:
        records: Canonical holdout records to serialize.
        output_path: Destination JSONL path.

    Returns:
        Number of records written.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    """Build the local trusted choices holdout from active reviewed learning data."""
    project_root = Path(__file__).parent.parent.parent
    parser = argparse.ArgumentParser(description="Build canonical BookFix choices holdout data.")
    parser.add_argument(
        "--input",
        default=str(project_root / ".ai_learning" / "choices_learning.json"),
        help="Reviewed choices learning JSON",
    )
    parser.add_argument(
        "--output",
        default=str(project_root / ".ai_learning" / "choices_holdout.jsonl"),
        help="Canonical JSONL holdout output",
    )
    parser.add_argument("--min-confidence", type=float, default=0.88)
    parser.add_argument(
        "--adjudications",
        default=str(project_root / ".ai_learning" / "choices_holdout_adjudications.json"),
        help="Manual benchmark adjudications keyed by source timestamp",
    )
    args = parser.parse_args()
    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    records = build_holdout_records(
        source.get("entries", []),
        load_canonical_choices(),
        args.min_confidence,
        load_adjudications(args.adjudications),
    )
    count = write_holdout(records, args.output)
    print(f"Wrote {count} trusted holdout records to {args.output}")


if __name__ == "__main__":
    main()
