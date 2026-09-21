#!/usr/bin/env python3
"""Pre-commit hook: every staged SVG must start with an SPDX-License-Identifier comment.

Default license is the project license (LGPL-3.0-only OR CC-BY-SA-3.0).
Icons taken from other projects keep their own license; keep SPDX_BY_NAME in
sync with the "Exceptions" table in README.md.

    ./add_spdx.py          # check staged SVGs, exit 1 if any lacks the header
    ./add_spdx.py --apply  # add the header to staged SVGs that lack it
"""
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Sequence

SPDX_DEFAULT: str = "LGPL-3.0-only OR CC-BY-SA-3.0"
SPDX_BY_NAME: Dict[str, str] = {
    "logviewer.svg": "GPL-3.0-or-later",    # gnome-logs
    "sticky-note.svg": "GPL-2.0-only",      # Tomboy app icon (license stated inside the source SVG)
    "tomboy-tag.svg": "LGPL-2.1-only",      # Tomboy
    "text-x-readme.svg": "GPL-2.0-only",    # Humanity, see FIXME.md
}
HEAD_SCAN_BYTES: int = 1024


def spdx_line(file_path: Path) -> str:
    return f"<!-- SPDX-License-Identifier: {SPDX_BY_NAME.get(file_path.name, SPDX_DEFAULT)} -->"


def run_git(args: Sequence[str]) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def get_staged_svg_file_paths() -> List[Path]:
    output: str = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACM"])
    return [
        Path(p) for p in output.splitlines()
        if p.lower().endswith(".svg") and Path(p).is_file()
    ]


def has_spdx_in_file_header(file_path: Path) -> bool:
    with file_path.open("rb") as f:
        return b"SPDX-License-Identifier:" in f.read(HEAD_SCAN_BYTES)


def insert_spdx_header_to_file(file_path: Path) -> None:
    ori_svg: str = file_path.read_text(encoding="utf-8", errors="ignore")
    line: str = spdx_line(file_path)
    if ori_svg.lstrip().startswith("<?xml"):
        idx: int = ori_svg.find("?>")
        if idx != -1:
            idx += 2
            new_svg = ori_svg[:idx] + "\n" + line + "\n" + ori_svg[idx:]
        else:
            new_svg = line + "\n" + ori_svg
    else:
        new_svg = line + "\n" + ori_svg
    file_path.write_text(new_svg, encoding="utf-8")


def main() -> int:
    to_apply = "--apply" in sys.argv
    files: List[Path] = get_staged_svg_file_paths()
    files_without_spdx: List[Path] = []
    for f in files:
        if has_spdx_in_file_header(f):
            continue
        files_without_spdx.append(f)
        if to_apply:
            print(f"[LOG] Add SPDX to {f}")
            insert_spdx_header_to_file(f)
        else:
            print(f"[WARN] {f} missing SPDX.")
    if files_without_spdx and not to_apply:
        print("[WARN] Some staged SVG files have no SPDX comment. Please run `./add_spdx.py --apply` and stage them again.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
