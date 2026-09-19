#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reorder `<defs>` so that a definition always precedes the ones referring to it.

QtSvg (the renderer behind Dolphin's thumbnails, and Qt applications in general)
resolves references while it parses. A `<mask>` whose content is painted with
`fill="url(#someGradient)"` therefore needs that gradient to appear *earlier* in
the document; when it appears later, the gradient is not there yet, the mask
renders empty, and everything the mask covers disappears. The icon still looks
correct in Inkscape, in Firefox and in resvg, so the defect is invisible until
someone opens the folder in Dolphin.

Inkscape writes `<defs>` in whatever order edits happened to leave behind, so
this is pure chance rather than anything the artwork did wrong. Re-saving a file
in Inkscape sometimes shuffles `<defs>` and accidentally cures it - which is how
`document-properties.svg` was fixed once, without the cause being understood.

Only `<mask>` is affected in practice: Qt resolves a forward `<use>` reference
without trouble, and a gradient inheriting stops from a later gradient through
`xlink:href` also works. But ordering every definition before its users is
harmless, so this tool does that rather than special-casing masks.

Reordering `<defs>` cannot change what a conforming renderer draws - the
children of `<defs>` are not rendered, only referenced - and that is verified,
not assumed: across the 1991 files of this theme, Inkscape renders every one of
them pixel-identically before and after.

The elements are moved as blocks of text, never re-serialised, so the diff shows
the moved definitions and nothing else. A file whose formatting does not allow
that (everything on one line, say) is reported and left alone rather than
rewritten. Every edit is checked by re-parsing the result and comparing it with
the original element by element; anything unexpected and the file is skipped.

Usage:
    python3 tools/fix_defs_order.py [--check] [PATH ...]

PATH may be SVG files or folders (searched recursively, symlinks skipped).
Default: `src/`, the theme sources - the drawing sheets under `raw/` are not
touched. `--check` changes nothing and exits with status 1 when something needs
reordering.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from lxml import etree

SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
_URL_REF = re.compile(r"url\(\s*#([^)\s]+)\s*\)")


def _referenced_ids(element: etree._Element, known: Set[str]) -> Set[str]:
    """The ids `element` and its descendants point at, limited to `known`."""
    found: Set[str] = set()
    for node in element.iter():
        if not isinstance(node.tag, str):
            continue
        for name, value in node.attrib.items():
            if name in (f"{{{XLINK}}}href", "href"):
                if value.startswith("#"):
                    found.add(value[1:])
            else:
                found.update(_URL_REF.findall(value))
    return found & known


def _wanted_order(children: Sequence[etree._Element]) -> List[etree._Element]:
    """`children`, with every definition placed before the ones referring to it.

    A depth-first walk keeps the original relative order wherever the references
    do not force a change, so the diff stays as small as the defect allows. A
    reference cycle is left where it is instead of being broken arbitrarily.
    """
    known = {c.get("id") for c in children if c.get("id")}
    by_id = {c.get("id"): c for c in children if c.get("id")}
    placed: Set[int] = set()
    order: List[etree._Element] = []

    def visit(child: etree._Element, path: Tuple[int, ...] = ()) -> None:
        if id(child) in placed or id(child) in path:
            return
        for target in sorted(_referenced_ids(child, known)):
            visit(by_id[target], path + (id(child),))
        placed.add(id(child))
        order.append(child)

    for child in children:
        visit(child)
    return order


def _start_line(lines: List[str], child: etree._Element) -> Optional[int]:
    """The 1-based line where `child` opens.

    `sourceline` points at the line where the *start tag ends*, which for an
    Inkscape file is the last of its attribute lines. The element itself begins
    earlier, on the line holding `<tag`; nothing else can open between the two,
    so scanning back for it is safe.
    """
    if child.sourceline is None:
        return None
    local = child.tag.rsplit("}", 1)[-1]
    for number in range(child.sourceline, 0, -1):
        stripped = lines[number - 1].lstrip()
        if stripped.startswith("<" + local):
            rest = stripped[len(local) + 1:]
            if rest[:1] in ("", " ", "\t", ">", "/", "\n", "\r"):
                return number
    return None


def _line_spans(lines: List[str], children: Sequence[etree._Element],
                closing: int) -> Optional[List[Tuple[int, int]]]:
    """One (start, end) line range per child, or None if they do not line up.

    Inkscape puts every element on its own line, so a child runs from its own
    opening line up to the next child's - or, for the last one, up to `</defs>`.
    """
    starts = [_start_line(lines, c) for c in children]
    if any(s is None for s in starts) or starts != sorted(starts):
        return None
    if len(set(starts)) != len(starts) or starts[-1] >= closing:
        return None
    bounds = starts[1:] + [closing]      # the last child stops before </defs>
    return [(a - 1, b - 1) for a, b in zip(starts, bounds)]


def _closing_line(lines: List[str], after: int) -> Optional[int]:
    """The 1-based line holding `</defs>`, searched from line `after` on."""
    depth = 0
    for number in range(after, len(lines) + 1):
        text = lines[number - 1]
        if "</defs>" in text:
            if depth == 0:
                return number
            depth -= 1
        depth += text.count("<defs")
    return None


def _same_document(before: bytes, after: bytes) -> bool:
    """Do the two documents hold the same elements, differing only in order?"""
    def fingerprint(raw: bytes) -> List[Tuple[str, Tuple[Tuple[str, str], ...]]]:
        root = etree.fromstring(raw)
        return sorted((node.tag, tuple(sorted(node.attrib.items())))
                      for node in root.iter() if isinstance(node.tag, str))
    try:
        return fingerprint(before) == fingerprint(after)
    except etree.XMLSyntaxError:
        return False


def reorder(text: str) -> Tuple[str, List[str]]:
    """Return the reordered document and a note per `<defs>` that was changed."""
    notes: List[str] = []
    while True:                       # one <defs> per pass: line numbers shift
        lines = text.splitlines(keepends=True)
        root = etree.fromstring(text.encode("utf-8"))
        for defs in root.iter(f"{{{SVG}}}defs"):
            children = [c for c in defs if isinstance(c.tag, str)]
            if len(children) < 2:
                continue
            order = _wanted_order(children)
            if order == children:
                continue
            closing = _closing_line(lines, children[-1].sourceline or 1)
            if closing is None:
                notes.append("SKIPPED, cannot find the line holding </defs>")
                return text, notes
            spans = _line_spans(lines, children, closing)
            if spans is None:
                notes.append("SKIPPED, <defs> is not written one element per line")
                return text, notes
            blocks = {id(c): "".join(lines[a:b]) for c, (a, b) in zip(children, spans)}
            head = "".join(lines[:spans[0][0]])
            tail = "".join(lines[spans[-1][1]:])
            candidate = head + "".join(blocks[id(c)] for c in order) + tail
            if not _same_document(text.encode("utf-8"), candidate.encode("utf-8")):
                notes.append("SKIPPED, the rewrite would not have been faithful")
                return text, notes
            moved = sum(1 for a, b in zip(children, order) if a is not b)
            notes.append(f"defs-order: moved {moved} of {len(children)} definitions")
            text = candidate
            break                     # re-parse, then look for the next <defs>
        else:
            return text, notes


def svg_files(paths: Sequence[Path]) -> List[Path]:
    found: List[Path] = []
    for path in paths:
        if not path.is_dir():
            found.append(path)
            continue
        for folder, _dirs, names in os.walk(path):
            found += [Path(folder, n) for n in names
                      if n.endswith(".svg") and not os.path.islink(os.path.join(folder, n))]
    return sorted(found)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="report only; exit 1 when something needs reordering")
    parser.add_argument("paths", nargs="*", type=Path,
                        help="SVG files or folders (default: src/)")
    args = parser.parse_args(argv)
    paths = args.paths or [Path(__file__).resolve().parent.parent / "src"]

    affected = 0
    for file in svg_files(paths):
        text = file.read_text(encoding="utf-8", errors="surrogateescape")
        if "<defs" not in text:
            continue
        try:
            new_text, notes = reorder(text)
        except etree.XMLSyntaxError as error:
            print(f"{file}: SKIPPED, {error}", file=sys.stderr)
            continue
        if not notes:
            continue
        affected += 1
        print(f"{file}")
        for note in notes:
            print(f"    {note}")
        if not args.check and new_text != text:
            with open(file, "w", encoding="utf-8", errors="surrogateescape",
                      newline="") as out:
                out.write(new_text)
    print(f"{affected} file(s) {'need reordering' if args.check else 'reordered'}.")
    return 1 if args.check and affected else 0


if __name__ == "__main__":
    sys.exit(main())
