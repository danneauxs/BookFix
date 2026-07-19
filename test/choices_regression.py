#!/usr/bin/env python3
"""Run canonical choices rules against the labeled homograph corpus."""

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from bookfix.processors.ai_choices import AIChoiceProcessor


def load_regression_data() -> Tuple[List[dict], Dict[str, dict]]:
    """Load labeled examples and current canonical choices definitions."""
    project_root = Path(__file__).resolve().parent.parent
    training_data = json.loads((project_root / "data" / "training_data.json").read_text())
    choices = json.loads((project_root / "data" / "choices.json").read_text())
    lexicon = {entry["word"].lower(): entry for entry in choices}
    return training_data, lexicon


def canonical_expected_spelling(label: str, entry: dict) -> str:
    """Map legacy sense labels to current choices.json option spellings."""
    sense_number = int(label.rsplit("_sense", 1)[1])
    options = entry.get("options", [])
    return options[sense_number - 1]["spelling"]


def run_regression() -> Tuple[Counter, Dict[str, Counter], List[Tuple]]:
    """Run local rules and return totals, per-word results, and wrong cases."""
    training_data, lexicon = load_regression_data()
    processor = AIChoiceProcessor()
    processor.initialize_ai(
        {
            "ai_enabled": False,
            "choices_nli_model": "roberta-large-mnli",
            "choices_nli_secondary_model": "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
            "choices_nli_dual_verify": True,
        }
    )
    processor._ensure_pos_services()
    totals = Counter()
    by_word = defaultdict(Counter)
    wrong_cases = []

    for item in training_data:
        target_indices = [
            index for index, label in enumerate(item["labels"]) if label != "O"
        ]
        # Skip malformed or multi-target records rather than inventing context.
        if len(target_indices) != 1:
            totals["skipped"] += 1
            continue
        target_index = target_indices[0]
        label = item["labels"][target_index]
        word = label.rsplit("_sense", 1)[0].lower()
        entry = lexicon.get(word)
        if not entry:
            totals["skipped"] += 1
            continue
        expected = canonical_expected_spelling(label, entry)
        tokens = [str(token) for token in item["tokens"]]
        tokens[target_index] = f"[{tokens[target_index]}]"
        context = " ".join(tokens)
        options = [option["spelling"] for option in entry.get("options", [])]

        try:
            rules, _ = processor._run_all_rules(word, context, None)
            decision, source = processor._get_consensus_from_rules(
                rules, context, word, options
            )
        except Exception as error:
            totals["error"] += 1
            by_word[word]["error"] += 1
            wrong_cases.append((word, context, expected, None, repr(error)))
            continue

        actual = decision.get("choice") if decision else None
        outcome = "defer" if actual is None else "correct" if actual == expected else "wrong"
        totals[outcome] += 1
        by_word[word][outcome] += 1
        by_word[word]["total"] += 1
        if outcome == "wrong":
            wrong_cases.append((word, context, expected, actual, source))

    return totals, by_word, wrong_cases


def main() -> None:
    """Print canonical regression totals and per-word rule performance."""
    totals, by_word, wrong_cases = run_regression()
    autonomous = totals["correct"] + totals["wrong"]
    coverage = autonomous / max(1, autonomous + totals["defer"])
    accuracy = totals["correct"] / max(1, autonomous)
    print(f"TOTAL {dict(totals)}")
    print(f"AUTO_APPLY_ACCURACY {accuracy:.4f}")
    print(f"COVERAGE {coverage:.4f}")
    for word in sorted(by_word):
        print(f"{word} {dict(by_word[word])}")
    print(f"WRONG_CASES {len(wrong_cases)}")
    for case in wrong_cases[:20]:
        print("WRONG", case)


if __name__ == "__main__":
    main()
