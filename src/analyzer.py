import ast
import sys
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Issue:
    kind: str
    line: Optional[int]
    col: Optional[int]
    message: str
    suggestion: str
    severity: str = "error"
    fixable: bool = False
    fix: Optional[str] = None


def analyze(source: str) -> list[Issue]:
    issues = []
    issues.extend(_check_syntax(source))
    if not any(i.kind == "SyntaxError" for i in issues):
        try:
            tree = ast.parse(source)
            issues.extend(_check_undefined_names(tree, source))
            issues.extend(_check_type_ops(tree))
            issues.extend(_check_bare_except(tree))
            issues.extend(_check_mutable_defaults(tree))
            issues.extend(_check_shadowed_builtins(tree))
            issues.extend(_check_unreachable(tree))
        except Exception:
            pass
    return issues


def _check_syntax(source: str) -> list[Issue]:
    issues = []
    try:
        ast.parse(source)
    except SyntaxError as e:
        fix = None
        if "expected ':'" in str(e) or "was never closed" in str(e):
            fix = _attempt_colon_fix(source, e.lineno)

        issues.append(Issue(
            kind="SyntaxError",
            line=e.lineno,
            col=e.offset,
            message=str(e.msg),
            suggestion=_syntax_suggestion(str(e.msg)),
            fixable=fix is not None,
            fix=fix,
        ))
    return issues


def _syntax_suggestion(msg: str) -> str:
    if "expected ':'" in msg:
        return "You're missing a colon at the end of a def, class, if, for, while, or with statement."
    if "invalid syntax" in msg:
        return "Double check for mismatched parentheses, missing operators, or stray characters."
    if "EOL while scanning string literal" in msg:
        return "You opened a string but never closed it. Check your quote marks."
    if "unexpected EOF" in msg:
        return "The file ended unexpectedly — you probably have an unclosed bracket or parenthesis."
    return "Check that line carefully for typos or missing punctuation."


def _attempt_colon_fix(source: str, lineno: int) -> Optional[str]:
    lines = source.splitlines()
    if lineno and lineno <= len(lines):
        target = lines[lineno - 1]
        stripped = target.rstrip()
        keywords = ("def ", "class ", "if ", "elif ", "else", "for ", "while ", "with ", "try", "except", "finally")
        if any(stripped.lstrip().startswith(k) for k in keywords) and not stripped.endswith(":"):
            lines[lineno - 1] = stripped + ":"
            return "\n".join(lines)
    return None


def _check_undefined_names(tree: ast.AST, source: str) -> list[Issue]:
    issues = []

    import builtins as _builtins_module
    defined: set[str] = set(dir(_builtins_module))

    class Collector(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            defined.add(node.name)
            for arg in node.args.args:
                defined.add(arg.arg)
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            defined.add(node.name)
            self.generic_visit(node)

        def visit_Import(self, node):
            for alias in node.names:
                defined.add(alias.asname or alias.name.split(".")[0])

        def visit_ImportFrom(self, node):
            for alias in node.names:
                defined.add(alias.asname or alias.name)

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined.add(target.id)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            defined.add(elt.id)
            self.generic_visit(node)

        def visit_AnnAssign(self, node):
            if isinstance(node.target, ast.Name):
                defined.add(node.target.id)
            self.generic_visit(node)

        def visit_For(self, node):
            if isinstance(node.target, ast.Name):
                defined.add(node.target.id)
            self.generic_visit(node)

        def visit_With(self, node):
            for item in node.items:
                if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                    defined.add(item.optional_vars.id)
            self.generic_visit(node)

        def visit_ExceptHandler(self, node):
            if node.name:
                defined.add(node.name)
            self.generic_visit(node)

        def visit_comprehension(self, node):
            if isinstance(node.target, ast.Name):
                defined.add(node.target.id)

    collector = Collector()
    collector.visit(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in defined and not node.id.startswith("_") and node.id not in {"True", "False", "None"}:
                closest = _closest_match(node.id, defined)
                suggestion = f"'{node.id}' hasn't been defined yet."
                if closest:
                    suggestion += f" Did you mean '{closest}'?"
                issues.append(Issue(
                    kind="NameError",
                    line=node.lineno,
                    col=node.col_offset,
                    message=f"name '{node.id}' is not defined",
                    suggestion=suggestion,
                    severity="error",
                ))
    return issues


def _closest_match(name: str, candidates: set[str]) -> Optional[str]:
    def distance(a, b):
        if len(a) > len(b):
            a, b = b, a
        row = list(range(len(a) + 1))
        for c in b:
            new_row = [row[0] + 1]
            for j, d in enumerate(a):
                new_row.append(min(new_row[-1] + 1, row[j + 1] + 1, row[j] + (c != d)))
            row = new_row
        return row[-1]

    close = [(distance(name, c), c) for c in candidates if abs(len(c) - len(name)) <= 3]
    close.sort()
    if close and close[0][0] <= 2:
        return close[0][1]
    return None


def _check_type_ops(tree: ast.AST) -> list[Issue]:
    issues = []
    str_type = (ast.Constant,)

    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left_is_str = isinstance(node.left, ast.Constant) and isinstance(node.left.value, str)
            right_is_num = isinstance(node.right, ast.Constant) and isinstance(node.right.value, (int, float))
            left_is_num = isinstance(node.left, ast.Constant) and isinstance(node.left.value, (int, float))
            right_is_str = isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)

            if left_is_str and right_is_num:
                issues.append(Issue(
                    kind="TypeError",
                    line=node.lineno,
                    col=node.col_offset,
                    message="can only concatenate str (not 'int') to str",
                    suggestion=f"You can't add a string and a number directly. Try: str({ast.unparse(node.right)}) or use an f-string.",
                    severity="error",
                    fixable=True,
                    fix=None,
                ))
            elif left_is_num and right_is_str:
                issues.append(Issue(
                    kind="TypeError",
                    line=node.lineno,
                    col=node.col_offset,
                    message="unsupported operand type(s) for +: 'int' and 'str'",
                    suggestion=f"Can't add a number and a string. Wrap the number in str() or use an f-string.",
                    severity="error",
                    fixable=True,
                    fix=None,
                ))
    return issues


def _check_bare_except(tree: ast.AST) -> list[Issue]:
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(Issue(
                kind="BareExcept",
                line=node.lineno,
                col=node.col_offset,
                message="bare 'except' catches everything including KeyboardInterrupt and SystemExit",
                suggestion="Catch a specific exception instead: 'except Exception:' or 'except ValueError:'",
                severity="warning",
            ))
    return issues


def _check_mutable_defaults(tree: ast.AST) -> list[Issue]:
    issues = []
    mutable_types = (ast.List, ast.Dict, ast.Set)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, mutable_types):
                    issues.append(Issue(
                        kind="MutableDefault",
                        line=default.lineno,
                        col=default.col_offset,
                        message=f"mutable default argument in '{node.name}'",
                        suggestion="Don't use [] or {} as default values — they're shared across all calls. Use None and set the value inside the function.",
                        severity="warning",
                    ))
    return issues


def _check_shadowed_builtins(tree: ast.AST) -> list[Issue]:
    builtins = {"list", "dict", "set", "tuple", "str", "int", "float", "bool", "type", "id", "input", "print", "len", "range", "open", "map", "filter", "zip", "sum", "min", "max", "sorted", "reversed"}
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in builtins:
                    issues.append(Issue(
                        kind="ShadowedBuiltin",
                        line=target.lineno,
                        col=target.col_offset,
                        message=f"variable name '{target.id}' shadows a Python builtin",
                        suggestion=f"Rename this variable — using '{target.id}' as a variable name hides the built-in function, which can cause confusing bugs.",
                        severity="warning",
                    ))
    return issues


def _check_unreachable(tree: ast.AST) -> list[Issue]:
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.For, ast.While, ast.If)):
            body = getattr(node, "body", [])
            for i, stmt in enumerate(body[:-1]):
                if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                    next_stmt = body[i + 1]
                    issues.append(Issue(
                        kind="UnreachableCode",
                        line=getattr(next_stmt, "lineno", None),
                        col=getattr(next_stmt, "col_offset", None),
                        message="unreachable code after return/raise/break/continue",
                        suggestion="This code will never run. Remove it or move it before the return/raise statement.",
                        severity="warning",
                    ))
    return issues


def apply_fixes(source: str, issues: list[Issue]) -> str:
    result = source
    for issue in issues:
        if issue.fixable and issue.fix:
            result = issue.fix
            break
    return result
