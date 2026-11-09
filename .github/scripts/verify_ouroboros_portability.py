"""Check that platform CI actually exercised all 14 Rust extension tests.

This verifier runs only in GitHub Actions after the repository's *unmodified*
build_ouroboros_sync.sh. It never removes/rewrites tracked binaries.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def verify(junit_path: Path) -> dict[str, object]:
    root = ET.parse(junit_path).getroot()
    cases = root.findall(".//testcase")
    total = len(cases)
    skipped = sum(case.find("skipped") is not None for case in cases)
    failed = sum(case.find("failure") is not None for case in cases)
    errored = sum(case.find("error") is not None for case in cases)
    if (total, skipped, failed, errored) != (14, 0, 0, 0):
        raise ValueError(
            f"expected 14 passing native test cases, got total={total}, "
            f"skipped={skipped}, failed={failed}, errors={errored}"
        )

    import ouroboros_sync  # noqa: PLC0415 - import after native build only

    native_path = Path(ouroboros_sync.__file__).resolve()
    repository_root = Path(__file__).resolve().parents[2]
    if not native_path.is_relative_to(repository_root):
        raise ValueError(f"native extension imported from outside checkout: {native_path}")

    system = platform.system()
    suffix = ".pyd" if system == "Windows" else ".so"
    if native_path.suffix.lower() != suffix:
        raise ValueError(f"expected {suffix} native extension on {system}: {native_path}")

    if system == "Darwin":
        # The checkout's tracked .so is a Linux binary. A native macOS
        # build must replace it in CI's disposable workspace.
        changed = subprocess.run(
            ["git", "status", "--porcelain", "--", "ouroboros_sync.so"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
        if not changed.stdout.strip():
            raise ValueError("macOS build did not replace the checked-in Linux extension")
    elif system == "Windows":
        if native_path.name != "ouroboros_sync.pyd":
            raise ValueError("Windows build did not import its .pyd output")
    else:
        raise ValueError(f"portability gate requires macOS or Windows, got {system}")

    return {
        "authority": "NONE",
        "verification_scope": "local_native_build_and_tests_only",
        "platform": system,
        "python": platform.python_version(),
        "native_extension": native_path.name,
        "native_extension_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
        "executed_tests": total,
        "skipped_tests": skipped,
        "failed_tests": failed,
        "error_tests": errored,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_ouroboros_portability.py TEST_RESULTS.xml", file=sys.stderr)
        return 2
    try:
        receipt = verify(Path(sys.argv[1]))
    except (OSError, ValueError, ImportError, ET.ParseError) as exc:
        print(f"FAIL: native portability evidence incomplete: {exc}", file=sys.stderr)
        return 1
    Path("ouroboros-portability-receipt.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print("PASS: freshly built native extension imported; 14/14 tests executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
