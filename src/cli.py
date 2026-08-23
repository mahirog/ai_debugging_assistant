import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import analyze, apply_fixes
from src.reporter import print_header, print_issues, print_fixed_code, print_summary
from src.ai_explainer import explain_issues, ai_fix_suggestion


def build_parser():
    parser = argparse.ArgumentParser(
        prog="debug",
        description="AI-powered Python debugger — finds errors, explains them, and suggests fixes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python src/cli.py example.py
  python src/cli.py example.py --fix
  python src/cli.py example.py --no-ai
  python src/cli.py src/ --fix
        """,
    )
    parser.add_argument("paths", nargs="+", help="Python file(s) or directory to analyze")
    parser.add_argument("--fix", action="store_true", help="write a _fixed.py version with auto-corrections applied")
    parser.add_argument("--no-ai", action="store_true", help="skip the Anthropic API call (faster, offline)")
    parser.add_argument("--json", action="store_true", help="output results as JSON (useful for piping)")
    parser.add_argument("--severity", choices=["error", "warning", "all"], default="all", help="filter by severity")
    return parser


def collect_files(paths: list[str]) -> list[str]:
    files = []
    for path in paths:
        if os.path.isdir(path):
            for root, _, names in os.walk(path):
                for name in names:
                    if name.endswith(".py"):
                        files.append(os.path.join(root, name))
        elif os.path.isfile(path):
            if path.endswith(".py"):
                files.append(path)
            else:
                print(f"Skipping non-Python file: {path}", file=sys.stderr)
        else:
            print(f"Path not found: {path}", file=sys.stderr)
    return files


def analyze_file(filepath: str, args) -> int:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"Could not read {filepath}: {e}", file=sys.stderr)
        return 1

    issues = analyze(source)

    if args.severity != "all":
        issues = [i for i in issues if i.severity == args.severity]

    if args.json:
        import json
        data = {
            "file": filepath,
            "issues": [
                {
                    "kind": i.kind,
                    "line": i.line,
                    "col": i.col,
                    "message": i.message,
                    "suggestion": i.suggestion,
                    "severity": i.severity,
                    "fixable": i.fixable,
                }
                for i in issues
            ],
        }
        print(json.dumps(data, indent=2))
        return 0

    print_header(filepath)

    ai_explanations = []
    if not args.no_ai and issues:
        ai_explanations = explain_issues(source, issues)

    print_issues(issues, ai_explanations)

    if args.fix and issues:
        fixed = source
        ai_fixed = None

        fixable = [i for i in issues if i.fixable]
        if fixable and not args.no_ai:
            ai_fixed = ai_fix_suggestion(source, fixable[0])

        if ai_fixed:
            fixed = ai_fixed
        else:
            fixed = apply_fixes(source, issues)

        if fixed != source:
            print_fixed_code(fixed, filepath)
        else:
            print("  No automatic fix could be applied for these errors.\n")

    return 1 if any(i.severity == "error" for i in issues) else 0


def main():
    parser = build_parser()
    args = parser.parse_args()

    files = collect_files(args.paths)
    if not files:
        print("No Python files found.", file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    for filepath in files:
        code = analyze_file(filepath, args)
        if code != 0:
            exit_code = code

    if len(files) > 1:
        print()
        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            issues = analyze(source)
            print_summary(issues, filepath)
        print()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
