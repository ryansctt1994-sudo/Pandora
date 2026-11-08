"""
Fail if a tracked path cannot be checked out correctly on Windows or macOS.

- Paths that differ only in case are one file on those systems, so checkouts
  overwrite one with the other (Launch_AI.py and launch_ai.py did).
- Windows cannot create names that end in a space or dot, contain <>:"|?*\\
  or control characters, or use a reserved device name (CON, NUL, COM1...),
  so git refuses to check them out there ("Zorel " did this).

Usage: git ls-files -z | python check_portable_paths.py
"""

import re
import sys
from collections import defaultdict

RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"{name}{i}" for name in ("COM", "LPT") for i in range(1, 10)}
FORBIDDEN = re.compile(r'[<>:"|?*\\\x00-\x1f]')


def windows_problems(path):
    for part in path.split("/"):
        if part != part.rstrip(" ."):
            yield f"{part!r} ends with a space or dot"
        if FORBIDDEN.search(part):
            yield f"{part!r} contains a character Windows forbids"
        if part.split(".")[0].upper() in RESERVED:
            yield f"{part!r} is a reserved Windows name"


def main():
    paths = [p for p in sys.stdin.read().split("\0") if p]
    problems = []

    by_folded = defaultdict(list)
    for path in paths:
        by_folded[path.casefold()].append(path)
        problems.extend(f"{path!r}: {why}" for why in windows_problems(path))
    for group in by_folded.values():
        if len(group) > 1:
            problems.append("differ only in case: " + ", ".join(repr(p) for p in sorted(group)))

    for problem in problems:
        print(problem)
    if problems:
        print(f"\n{len(problems)} non-portable path(s). Rename them so Windows and macOS can check them out.")
        return 1
    print(f"All {len(paths)} paths are portable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
