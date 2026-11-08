"""
Fail if a module or class body defines the same function or class name twice.

Python keeps only the last definition, so the earlier one silently stops
working. This is how several of this repository's merge conflict resolutions
went wrong: both sides of a conflict were kept, the file still compiled, and
the older code quietly replaced the newer code.

Definitions inside if/try blocks are not checked (they are usually deliberate
alternatives), and property setters/deleters and typing.overload are allowed.

Usage: python check_duplicate_definitions.py FILE...
"""

import ast
import sys
from collections import defaultdict

ALLOWED_DECORATOR_SUFFIXES = (".setter", ".deleter")
ALLOWED_DECORATORS = ("overload", "typing.overload")


def is_allowed_redefinition(node):
    for decorator in getattr(node, "decorator_list", []):
        name = ast.unparse(decorator)
        if name.endswith(ALLOWED_DECORATOR_SUFFIXES) or name in ALLOWED_DECORATORS:
            return True
    return False


def find_duplicates(body, scope, path, problems):
    seen = defaultdict(list)
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not is_allowed_redefinition(node):
                seen[node.name].append(node.lineno)
            if isinstance(node, ast.ClassDef):
                find_duplicates(node.body, f"{scope}{node.name}.", path, problems)
    for name, lines in seen.items():
        if len(lines) > 1:
            where = ", ".join(str(line) for line in lines)
            problems.append(f"{path}: {scope}{name} is defined {len(lines)} times (lines {where})")


def main(paths):
    problems = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as error:
            problems.append(f"{path}: cannot parse ({error.msg}, line {error.lineno})")
            continue
        find_duplicates(tree.body, "", path, problems)
    for problem in problems:
        print(problem)
    if problems:
        print(f"\n{len(problems)} problem(s). Keep one definition of each name.")
        return 1
    print(f"No duplicate definitions in {len(paths)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
