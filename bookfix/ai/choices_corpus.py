"""Extract homograph contexts from source documents for choices learning."""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence

from ..lexicon_loader import LexiconLoader


SUPPORTED_SUFFIXES = {".txt", ".md", ".text", ".html", ".htm", ".xhtml"}
TOKEN_PATTERN = re.compile(r"\b[\w]+(?:['’][\w]+)?\b", re.UNICODE)


def iter_source_files(sources: Sequence[str]) -> Iterator[Path]:
    """Yield supported text files from source files and recursive directories."""
    seen = set()
    for source in sources:
        path = Path(source).expanduser().resolve()
        candidates = path.rglob("*") if path.is_dir() else [path]
        for candidate in candidates:
            if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            yield candidate


def normalize_phrase(tokens: Sequence[str]) -> str:
    """Return a stable lowercase phrase representation for rule comparison."""
    return " ".join(token.casefold() for token in tokens if token).strip()


def extract_context_records(
    text: str,
    source: str,
    words: Iterable[str],
    window_words: int = 5,
    max_per_word: Optional[int] = None,
) -> List[Dict]:
    """Extract bracketed contexts and phrase windows for configured homographs.

    Args:
        text: Source document text.
        source: Human-readable source identifier stored in each record.
        words: Homograph spellings to locate case-insensitively.
        window_words: Number of tokens before and after each target.
        max_per_word: Optional per-word output cap for large corpora.

    Returns:
        List of JSON-serializable context records.
    """
    if window_words < 1:
        raise ValueError("window_words must be at least 1")
    targets = {word.casefold() for word in words if word.strip()}
    counts = {word: 0 for word in targets}
    tokens = list(TOKEN_PATTERN.finditer(text))
    records = []

    for index, token_match in enumerate(tokens):
        token = token_match.group(0)
        word = token.casefold()
        if word not in targets:
            continue
        # Enforce per-word limits without affecting extraction of other words.
        if max_per_word is not None and counts[word] >= max_per_word:
            continue

        start_index = max(0, index - window_words)
        end_index = min(len(tokens), index + window_words + 1)
        window_tokens = [match.group(0) for match in tokens[start_index:end_index]]
        before_tokens = window_tokens[: index - start_index]
        after_tokens = window_tokens[index - start_index + 1 :]
        line_number = text.count("\n", 0, token_match.start()) + 1
        record = {
            "source": source,
            "line": line_number,
            "word": token,
            "normalized_word": word,
            "context": (
                f"{normalize_phrase(before_tokens)} [{token}] "
                f"{normalize_phrase(after_tokens)}"
            ).strip(),
            "phrase_window": normalize_phrase(window_tokens),
            "before": before_tokens,
            "after": after_tokens,
            "match_start": token_match.start(),
            "match_end": token_match.end(),
        }
        records.append(record)
        counts[word] += 1

    return records


def extract_from_sources(
    sources: Sequence[str],
    words: Optional[Iterable[str]] = None,
    window_words: int = 5,
    max_per_word: Optional[int] = None,
) -> Iterator[Dict]:
    """Yield context records from all supported source documents."""
    configured_words = list(words) if words is not None else LexiconLoader().get_all_words()
    for source_path in iter_source_files(sources):
        try:
            text = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Ignore non-UTF8 documents rather than corrupting extracted context.
            continue
        yield from extract_context_records(
            text,
            str(source_path),
            configured_words,
            window_words=window_words,
            max_per_word=max_per_word,
        )


def write_context_jsonl(records: Iterable[Dict], output_path: str) -> int:
    """Write extracted records as JSONL and return the number of records written."""
    path = Path(output_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    """Parse command-line arguments and write a choices context corpus."""
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Extract homograph context windows for BookFix choices learning."
    )
    parser.add_argument("sources", nargs="+", help="Text files or directories to scan")
    parser.add_argument(
        "--output",
        default=str(project_root / ".ai_learning" / "choices_corpus.jsonl"),
        help="JSONL output path (default: .ai_learning/choices_corpus.jsonl)",
    )
    parser.add_argument(
        "--word",
        action="append",
        dest="words",
        help="Limit extraction to this homograph; repeat for multiple words",
    )
    parser.add_argument(
        "--window-words", type=int, default=5, help="Tokens before and after target"
    )
    parser.add_argument(
        "--max-per-word", type=int, default=None, help="Optional output cap per word per file"
    )
    args = parser.parse_args()
    source_files = list(iter_source_files(args.sources))
    # Fail loudly when a directory has no supported text files instead of writing an empty corpus.
    if not source_files:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        parser.error(f"No supported source files found. Expected extensions: {supported}")
    print(f"Scanning {len(source_files)} source file(s)")
    records = extract_from_sources(
        [str(path) for path in source_files],
        words=args.words,
        window_words=args.window_words,
        max_per_word=args.max_per_word,
    )
    count = write_context_jsonl(records, args.output)
    print(f"Wrote {count} context records to {args.output}")


if __name__ == "__main__":
    main()
