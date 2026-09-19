# tools/

Small utilities for keeping the icons rendering correctly in renderers other
than Inkscape. Inkscape is by far the most forgiving SVG implementation in
common use, so "it looks right in Inkscape" says very little: a file can be
perfect there and lose whole shapes in a file manager or a browser.

| | |
|---|---|
| `fix_defs_order.py` | Reorders `<defs>` so a definition precedes its users. Repairs artwork that disappears in Qt applications. `--check` for a dry run. |
| `render_qtsvg.py` | Renders a file through QtSvg, the renderer Dolphin's thumbnails use. |
| `scan_qtsvg.py` | Lists files whose references QtSvg cannot resolve. |

Requirements: `python3-lxml` for the first, `python3-pyqt6.qtsvg` for the other
two (no display needed). ImageMagick and Inkscape are handy for comparing
renders but are not imported by anything here.

Related, in the parent repository: `tools/fix_svg_for_browsers.py`, which
repairs two defects that break browsers instead of Qt - a `<g>` directly inside
`<clipPath>`, and `<mask maskUnits="userSpaceOnUse">` without an explicit
region.

## The defect `fix_defs_order.py` repairs

QtSvg resolves references while it parses. A `<mask>` whose content is painted
with `fill="url(#someGradient)"` therefore needs that gradient to appear
*earlier* in the document. When it appears later, the gradient is not there yet,
the mask renders empty, and **everything the mask covers disappears**. The file
is valid SVG and renders correctly everywhere else, so nothing warns you: QtSvg
does not even log it.

Inkscape writes `<defs>` in whatever order editing happened to leave behind, so
which files are affected is pure chance. In this theme it hit 43 of 1991 files,
including four that lost their entire subject:

- `object-rotate-left` / `object-rotate-right` - the whole arrow
- `view-sort-ascending` / `view-sort-descending` - the whole arrow
- `x-office-presentation-template` - everything except the green ruler
- `applications-multimedia` - the film strip behind the music note

Only `<mask>` is affected in practice. Qt resolves a forward `<use>` reference
without trouble (59 files here do that and are fine), and a gradient inheriting
stops from a later gradient through `xlink:href` also works (1450 files).
Ordering every definition before its users is harmless, so the tool does that
rather than special-casing masks.

This is also what `96031b4` repaired on `document-properties.svg`, by re-saving
the file in Inkscape. The re-save shuffled `<defs>` as a side effect; that is
why the commit message could not name the cause.

## How to verify a change like this

One renderer alone will mislead you in both directions. Inkscape accepts almost
anything, so it cannot tell you whether a file is portable. QtSvg rasterises
gradients and antialiases edges differently from Inkscape, so a perfectly
correct file still differs from it by thousands of pixels - "matches Inkscape"
is not a usable standard either.

So judge a renderer fix on two statements instead:

1. **Inkscape renders the file identically before and after** - exactly 0
   differing pixels. This proves the change is a no-op for a conforming
   renderer, which is what makes it safe to apply in bulk.
2. **QtSvg ends up closer to Inkscape than it started.** Flatten both renders
   onto an opaque background and compare them with Inkscape's own render; the
   distance has to shrink. Never compare the absolute numbers - QtSvg differs
   from Inkscape by thousands of pixels even on a file with nothing wrong.

The second one is worth stating carefully, because the obvious shortcut is
wrong. Measuring whether QtSvg *draws more* - comparing how much of the canvas
is painted - misses every case where the lost artwork sits inside the shape
that survived: the clock hands in `document-open-recent` came back with the
painted area unchanged to four decimal places, because the arrow lies entirely
within the clock face. Compare colour, not coverage.

Applied that way over this theme: Inkscape identical for all 2022 files, and
QtSvg closer to it for 57 of them.

`fix_defs_order.py` moves the definitions as blocks of text rather than
re-serialising the document, so the diff shows the moved definitions and
nothing else. That matters for review, and it keeps the Inkscape formatting the
rest of `src/` uses. Each edit is checked by re-parsing the result and comparing
it element by element with the original; a file that cannot be edited safely is
reported and left alone.

## Reorder what is broken, not everything

Most files have a definition sitting after something that refers to it without
any visible consequence - `--check` over `src/` reports well over a thousand of
them. Only the ones where a `<mask>` is involved actually lose artwork.

Running the tool over the whole theme would therefore rewrite the `<defs>` of
most files to fix 43, which buries a real repair in noise and makes the result
impossible to review. Find the files that render differently first, then run the
tool on those. `render_qtsvg.py` gives you the before-and-after coverage to
decide with.

## Reordering is not always an improvement

`apps/256/logviewer.svg` is the counter-example, and the reason the check above
is worded as "closer to Inkscape" rather than "the mask now works". Its second
mask does point at a gradient defined later, so the tool reorders it and QtSvg
duly starts applying the mask - and the result is further from Inkscape than
leaving it broken was (RMSE 0.044 to 0.094): the page fills with hard black
text and loses its shading and punched edge. Qt gets that mask wrong in some
other way, and resolving the reference only lets the second bug through.

So the tool finding something to reorder is not a reason to commit the result.
Measure, and keep the change only where the measurement improves.

## Things that look like the cause and are not

Each of these was measured and ruled out. They are recorded because every one of
them is plausible enough to waste a day on.

- **Removing the root `viewBox`.** 25 of the 26 files in this theme without a
  `viewBox` contain a mask, which makes a compelling correlation. It is not the
  cause: taking only the `viewBox` off a known-broken file changes its QtSvg
  rendering not at all.
- **QtSvg not supporting `<mask>`.** It supports it. Give the same mask a solid
  white rectangle instead of a gradient and the artwork comes back.
- **Qt failing to resolve `xlink:href` between gradients.** Reordering only the
  gradients, leaving the mask where it was, changes nothing.
- **The icon being cut out of the drawing sheet incorrectly.** The affected
  files match their region of the sheet pixel for pixel.

## Known, not repaired

`scan_qtsvg.py` reports around a hundred files here with references QtSvg cannot
resolve. Nearly all of them point at an id the original GNOME drawing never
contained; Inkscape ignores them identically, and reordering cannot invent a
missing definition. A few point at an id that does exist and are worth a closer
look. Qt also logs `link #... is undefined!` for the `network-*` icons and
`The requested mask size is too big, ignoring` for a handful of others; neither
has been investigated.
