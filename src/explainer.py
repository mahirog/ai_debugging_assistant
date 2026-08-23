import os
import json
import urllib.request
import urllib.error
from typing import Optional
from .analyzer import Issue


ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"


def explain_issues(source: str, issues: list[Issue]) -> list[dict]:
    if not ANTHROPIC_API_KEY:
        return []

    if not issues:
        return []

    formatted = []
    for i in issues:
        loc = f"line {i.line}" if i.line else "unknown location"
        formatted.append(f"- [{i.kind}] at {loc}: {i.message}")

    issues_text = "\n".join(formatted)

    prompt = f"""You're reviewing Python code that has some bugs. Here's the code:

```python
{source}
```

The static analyzer found these issues:
{issues_text}

For each issue, give a short plain-English explanation of what went wrong and how to fix it. Be direct and practical — like a senior dev doing a code review, not a textbook. Don't repeat the error message back. Format your response as a JSON array like this:

[
  {{
    "kind": "IssueKind",
    "line": 3,
    "explanation": "...",
    "fix_example": "..."
  }}
]

Only return the JSON. No preamble."""

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["content"][0]["text"].strip()
            raw = raw.strip("```json").strip("```").strip()
            return json.loads(raw)
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError):
        return []


def ai_fix_suggestion(source: str, issue: Issue) -> Optional[str]:
    if not ANTHROPIC_API_KEY:
        return None

    loc = f"line {issue.line}" if issue.line else "unknown location"

    prompt = f"""Fix this Python code. There's a {issue.kind} at {loc}: {issue.message}

```python
{source}
```

Return only the fixed Python code with no explanation, no markdown fences, nothing else."""

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"].strip()
    except Exception:
        return None
