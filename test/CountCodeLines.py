import os
from pathlib import Path

def analyze_python_file(filepath: str):
    """Analyze a single .py file and return line statistics."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        total_lines = len(lines)
        comment_lines = 0
        code_lines = 0

        for line in lines:
            stripped = line.strip()
            if stripped:
                if stripped.startswith('#'):
                    comment_lines += 1
                else:
                    code_lines += 1  # Any non-empty, non-pure-comment line is code

        return {
            'total': total_lines,
            'code': code_lines,
            'comments': comment_lines
        }

    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def main():
    """Scans the current directory and its subdirectories for Python files (.py) to calculate statistics such as total files, lines of code, and comments.
    Args:
    None
    Returns:
    None
    """
    root_dir = Path('.')  # Run this script in the parent directory

    print("🔍 Scanning for .py files recursively...\n")

    total_stats = {
        'files': 0,
        'total': 0,
        'code': 0,
        'comments': 0
    }

    file_results = []

    # Find all .py files recursively
    for py_file in sorted(root_dir.rglob("*.py")):
        rel_path = py_file.relative_to(root_dir)
        stats = analyze_python_file(py_file)

        if stats:
            file_results.append((rel_path, stats))

            total_stats['files'] += 1
            total_stats['total'] += stats['total']
            total_stats['code'] += stats['code']
            total_stats['comments'] += stats['comments']

    # === Itemized List ===
    print("=" * 85)
    print("PYTHON FILES - LINE COUNT")
    print("=" * 85)

    for filepath, stats in file_results:
        print(f"{filepath}")
        print(f"   Total lines     : {stats['total']:6d}")
        print(f"   Code lines      : {stats['code']:6d}")
        print(f"   Comment lines   : {stats['comments']:6d}")
        print("-" * 60)

    # === Summary ===
    print("\n" + "=" * 85)
    print("SUMMARY")
    print("=" * 85)
    print(f"Total Python files : {total_stats['files']}")
    print(f"Total lines        : {total_stats['total']}")
    print(f"Total code lines   : {total_stats['code']}")
    print(f"Total comment lines: {total_stats['comments']}")

    if total_stats['total'] > 0:
        code_pct = (total_stats['code'] / total_stats['total']) * 100
        comment_pct = (total_stats['comments'] / total_stats['total']) * 100
        print(f"\nCode     : {code_pct:.1f}%")
        print(f"Comments : {comment_pct:.1f}%")


if __name__ == "__main__":
    main()
