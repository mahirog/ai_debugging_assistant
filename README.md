# ai_debugging_assistant

A Python debugging tool that catches errors before you run your code. It parses your files, finds syntax errors, undefined variables, type mismatches, and bad patterns — then explains each one in plain English and optionally writes a fixed version.

When you have an `ANTHROPIC_API_KEY` set, it uses Claude to give smarter, more contextual explanations and to generate AI-powered fixes. Without a key it still works fine using the built-in static analyzer.

---

## What it catches

- **SyntaxError** — missing colons, unclosed brackets, broken string literals
- **NameError** — variables used before they're defined (with typo detection)
- **TypeError** — string + number concatenation and similar type mismatches
- **BareExcept** — `except:` with no exception type
- **MutableDefault** — mutable default arguments like `def foo(items=[])`
- **ShadowedBuiltin** — variables named `list`, `dict`, `str`, etc.
- **UnreachableCode** — code after a `return`, `raise`, `break`, or `continue`

---

## Setup

```bash
git clone https://github.com/mahirog/ai_debugging_assistant
cd ai_debugging_assistant
pip install -r requirements.txt
```

For AI-powered explanations and fixes, add your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

On Windows:

```cmd
set ANTHROPIC_API_KEY=sk-ant-...
```

---

## Usage

**Analyze a file:**
```bash
python src/cli.py example.py
```

**Analyze and write a fixed version:**
```bash
python src/cli.py example.py --fix
```

**Scan an entire directory:**
```bash
python src/cli.py src/
```

**Run without the API (offline mode):**
```bash
python src/cli.py example.py --no-ai
```

**Output as JSON (for piping into other tools):**
```bash
python src/cli.py example.py --json
```

**Filter by severity:**
```bash
python src/cli.py example.py --severity error
python src/cli.py example.py --severity warning
```

---

## Example

Given this `example.py`:

```python
x = 10
print(y)

z = "hello" + 5

def foo()
    print("Missing colon")
```

Running:

```bash
python src/cli.py example.py --fix
```

Output:

```
  Analyzing: example.py
  ──────────────────────────────────────────────────

  Errors (3)

   SyntaxError   line 6
    expected ':'
    ↳ You're missing a colon at the end of a def statement.

   NameError   line 2
    name 'y' is not defined
    ↳ 'y' hasn't been defined yet. Did you mean 'x'?

   TypeError   line 4
    can only concatenate str (not 'int') to str
    ↳ You can't add a string and a number. Try str(5) or use an f-string.

  ──────────────────────────────────────────────────
  3 issues found

  Fixed code written to: example_fixed.py
```

---

## Running tests

```bash
python -m unittest discover tests
```

All tests use only stdlib — no API key needed.

---

## File structure

```
ai_debugging_assistant/
├── src/
│   ├── __init__.py
│   ├── analyzer.py       # AST-based static analysis
│   ├── ai_explainer.py   # Anthropic API integration
│   ├── reporter.py       # Terminal output formatting
│   └── cli.py            # CLI entrypoint
├── tests/
│   ├── __init__.py
│   └── test_analyzer.py  # Unit tests for all checks
├── example.py            # Sample file with intentional bugs
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How the AI part works

When `ANTHROPIC_API_KEY` is set, the tool sends your code and the list of detected issues to Claude. Claude returns a plain-English explanation for each issue and a concrete fix example. With `--fix`, it also asks Claude to rewrite the whole file with corrections applied.

Without a key, the tool falls back to the built-in explanations and rule-based auto-fix (currently handles missing colons).
