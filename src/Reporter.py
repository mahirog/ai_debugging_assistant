import sys
from .analyzer import Issue


RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
GREEN = "\033[32m"
DIM = "\033[2m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(text: str, *codes: str) -> str:
    if not _supports_color():
        return text
    return "".join(codes) + text + RESET


def print_header(filename: str):
    print()
    print(_c(f"  Analyzing: {filename}", BOLD, CYAN))
    print(_c("  " + "─" * 50, DIM))
    print()


def print_issues(issues: list[Issue], ai_explanations: list[dict] = None):
    if not issues:
        print(_c("  ✓ No issues found.", GREEN, BOLD))
        print()
        return

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    ai_map = {}
    if ai_explanations:
        for entry in ai_explanations:
            key = (entry.get("kind"), entry.get("line"))
            ai_map[key] = entry

    if errors:
        print(_c(f"  Errors ({len(errors)})", RED, BOLD))
        print()
        for issue in errors:
            _print_single(issue, ai_map)

    if warnings:
        print(_c(f"  Warnings ({len(warnings)})", YELLOW, BOLD))
        print()
        for issue in warnings:
            _print_single(issue, ai_map)

    total = len(issues)
    label = f"  {total} issue{'s' if total != 1 else ''} found"
    print(_c("  " + "─" * 50, DIM))
    print(_c(label, BOLD))
    print()


def _print_single(issue: Issue, ai_map: dict):
    loc = f"line {issue.line}" if issue.line else "?"
    color = RED if issue.severity == "error" else YELLOW
    badge = _c(f" {issue.kind} ", color, BOLD)

    print(f"  {badge}  {_c(loc, DIM)}")
    print(f"    {issue.message}")

    ai_entry = ai_map.get((issue.kind, issue.line))
    if ai_entry and ai_entry.get("explanation"):
        print()
        print(f"    {_c('↳', CYAN)} {ai_entry['explanation']}")
        if ai_entry.get("fix_example"):
            print()
            print(_c("    Example fix:", DIM))
            for line in ai_entry["fix_example"].splitlines():
                print(f"      {_c(line, GREEN)}")
    else:
        print()
        print(f"    {_c('↳', CYAN)} {issue.suggestion}")

    print()


def print_fixed_code(fixed: str, filename: str):
    outfile = filename.replace(".py", "_fixed.py")
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(fixed)
    print(_c(f"  Fixed code written to: {outfile}", GREEN, BOLD))
    print()


def print_summary(issues: list[Issue], filename: str):
    errors = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")
    parts = []
    if errors:
        parts.append(_c(f"{errors} error{'s' if errors != 1 else ''}", RED))
    if warnings:
        parts.append(_c(f"{warnings} warning{'s' if warnings != 1 else ''}", YELLOW))
    if not parts:
        parts.append(_c("clean", GREEN))
    print(f"  {filename}: {', '.join(parts)}")
