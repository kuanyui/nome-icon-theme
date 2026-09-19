#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""List the files whose references QtSvg cannot resolve.

QtSvg complains on stderr when it meets `url(#something)` it cannot find. That
makes a cheap detector for one class of defect - but only one class, and not the
worst: a `<mask>` that comes before the gradient painting it fails *silently*,
with the masked artwork simply gone. `tools/fix_defs_order.py` is what finds and
repairs that one; this script catches the rest.

Most of what it reports here is an id the original GNOME drawing never had.
Inkscape ignores those exactly the same way, so they are not ours to fix - they
are listed to keep them apart from the ones that matter.

Needs `python3-pyqt6.qtsvg`. No display required.

Usage:
    python3 tools/scan_qtsvg.py [PATH ...]

PATH may be SVG files or folders (default: `src/`). One tab-separated line per
affected file: path, number of distinct unresolved ids, then the first few.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtCore import qInstallMessageHandler
    from PyQt6.QtGui import QGuiApplication
    from PyQt6.QtSvg import QSvgRenderer
except ImportError:                                            # pragma: no cover
    sys.exit("PyQt6 with the QtSvg module is required "
             "(Debian/Ubuntu: apt install python3-pyqt6.qtsvg)")

MESSAGES: List[str] = []


def svg_files(paths: List[Path]) -> List[Path]:
    found: List[Path] = []
    for path in paths:
        if not path.is_dir():
            found.append(path)
            continue
        for folder, _dirs, names in os.walk(path):
            found += [Path(folder, n) for n in names
                      if n.endswith(".svg") and not os.path.islink(os.path.join(folder, n))]
    return sorted(found)


def main() -> int:
    qInstallMessageHandler(lambda mode, context, message: MESSAGES.append(message))
    app = QGuiApplication(sys.argv[:1])                        # noqa: F841

    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        paths = [Path(__file__).resolve().parent.parent / "src"]

    affected = 0
    checked = 0
    for file in svg_files(paths):
        MESSAGES.clear()
        QSvgRenderer(str(file))
        checked += 1
        missing = sorted({m.rsplit(":", 1)[-1].strip() for m in MESSAGES
                          if "Could not resolve" in m})
        if not missing:
            continue
        affected += 1
        print(f"{file}\t{len(missing)}\t{','.join(missing[:3])}")
    print(f"# {checked} file(s) checked, {affected} with unresolved references",
          file=sys.stderr)
    return 1 if affected else 0


if __name__ == "__main__":
    sys.exit(main())
