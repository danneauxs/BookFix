#!/usr/bin/env python3
"""Evaluate current choices decisions against the trusted reviewed holdout."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from bookfix.ai.choices_holdout import load_adjudications
from bookfix.processors.ai_choices import AIChoiceProcessor


def load_holdout(path: str = ".ai_learning/choices_holdout.jsonl"):
    """Load canonical holdout records from JSONL.

    Args:
        path: JSONL file containing canonical reviewed records.

    Returns:
        List of decoded holdout records.
    """
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_holdout(records, dual_verify: bool = True, load_nli: bool = True):
    """Run current choices engine against holdout records with optional NLI.

    Args:
        records: Canonical holdout records to evaluate.
        dual_verify: Whether configured primary and secondary NLI must agree.
        load_nli: Whether transformer NLI services should be initialized.

    Returns:
        Totals, per-review-type totals, and wrong autonomous cases.
    """
    processor = AIChoiceProcessor()
    processor.initialize_ai(
        {
            "ai_enabled": False,
            "choices_nli_model": "roberta-large-mnli",
            "choices_nli_secondary_model": "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
            "choices_nli_dual_verify": dual_verify,
        }
    )
    processor._ensure_pos_services()
    if not load_nli:
        # Rules-only measurement isolates grammar, phrase, dependency, and keyword evidence.
        processor._ensure_nli_services = lambda: None
    adjudications = load_adjudications()
    totals = Counter()
    by_type = defaultdict(Counter)
    wrong = []
    for record in records:
        word = record["word"]
        options = record["options"]
        context = record["context"]
        rules, _ = processor._run_all_rules(word, context, None)
        decision, source = processor._get_consensus_from_rules(
            rules, context, word, options
        )
        actual = decision.get("choice") if decision else None
        expected = record["choice"]
        review_type = record["review_type"]
        benchmark_category = record.get(
            "benchmark_category",
            adjudications.get(record.get("source_timestamp", ""), {}).get(
                "benchmark_category", "standard"
            ),
        )
        if benchmark_category == "label_dispute":
            totals[benchmark_category] += 1
            by_type[review_type][benchmark_category] += 1
            continue
        outcome = "defer" if actual is None else "correct" if actual == expected else "wrong"
        totals[outcome] += 1
        by_type[review_type][outcome] += 1
        if outcome == "wrong":
            wrong.append((word, expected, actual, source, context))
    return totals, by_type, wrong


def main() -> None:
    """Print holdout accuracy, coverage, and representative wrong decisions."""
    parser = argparse.ArgumentParser(description="Evaluate BookFix choices on trusted holdout data.")
    parser.add_argument(
        "--no-dual-nli",
        action="store_true",
        help="Load only primary NLI; useful on GPUs with limited VRAM.",
    )
    parser.add_argument(
        "--rules-only",
        action="store_true",
        help="Skip transformer loading and measure rules/POS evidence only.",
    )
    args = parser.parse_args()
    totals, by_type, wrong = run_holdout(
        load_holdout(),
        dual_verify=not args.no_dual_nli,
        load_nli=not args.rules_only,
    )
    autonomous = totals["correct"] + totals["wrong"]
    print(f"TOTAL {dict(totals)}")
    print(f"AUTO_ACCURACY {totals['correct'] / max(1, autonomous):.4f}")
    print(f"COVERAGE {autonomous / max(1, sum(totals.values())):.4f}")
    for review_type in sorted(by_type):
        print(review_type, dict(by_type[review_type]))
    print(f"WRONG_CASES {len(wrong)}")
    for case in wrong[:20]:
        print("WRONG", case)


if __name__ == "__main__":
    main()
