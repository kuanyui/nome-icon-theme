#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render an SVG through QtSvg - the renderer behind Dolphin's thumbnails.

Qt applications do not use librsvg or resvg; they use QtSvg, which is stricter
and less complete than either. An icon can be perfect in Inkscape, correct in
Firefox, and still lose entire shapes in a file manager. This renders a file the
way Qt would, so that can be checked without leaving the terminal.

Needs `python3-pyqt6.qtsvg` (Debian/Ubuntu) or the equivalent PyQt6 package.
No display is required; the offscreen platform plugin is selected here.

Usage:
    python3 tools/render_qtsvg.py IN.svg OUT.png [PIXELS]

PIXELS defaults to 128. Compare the result against Inkscape's own export to see
what Qt drops:

    inkscape IN.svg -o ink.png --export-width 128 --export-height 128
    python3 tools/render_qtsvg.py IN.svg qt.png 128
    compare -metric AE ink.png qt.png null:

Do not expect zero: the two rasterise gradients and antialias edges
differently, so a correct file still differs by a few thousand pixels at 128px.
Look at the images, or compare coverage (see tools/README.md).
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtGui import QGuiApplication, QImage, QPainter
    from PyQt6.QtSvg import QSvgRenderer
except ImportError:                                            # pragma: no cover
    sys.exit("PyQt6 with the QtSvg module is required "
             "(Debian/Ubuntu: apt install python3-pyqt6.qtsvg)")


def render(source: str, dest: str, pixels: int = 128) -> None:
    renderer = QSvgRenderer(source)
    if not renderer.isValid():
        raise SystemExit(f"QtSvg rejected {source}")
    image = QImage(pixels, pixels, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    if not image.save(dest):
        raise SystemExit(f"could not write {dest}")


def main() -> None:
    if not 3 <= len(sys.argv) <= 4:
        sys.exit(__doc__.strip().splitlines()[-1] if __doc__ else "bad arguments")
    app = QGuiApplication(sys.argv[:1])                        # noqa: F841
    render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 128)


if __name__ == "__main__":
    main()
