# gnome-icon-theme-fork

## What is This?
I prefer the icons following Tango design guidelines over flat design.

Tango design guidelines was promoted by Freedesktop.org, and was adopted by GNOME Project and Canonical Ubuntu in GNOME 2.x era.

GNOME Project provides [gnome-icon-theme-3.12.0.tar.xz](https://download.gnome.org/sources/gnome-icon-theme/3.12/gnome-icon-theme-3.12.0.tar.xz), which is the last release of [gnome-icon-theme](https://download.gnome.org/sources/gnome-icon-theme/). but its SVG files are... multiple icons accumulated in one SVG file, and after some struggling, I found it's nerely impossible to extract the icons separately **as SVG** (instead of rasterized PNG) via script...

> I've struggling with SVG.js but its `rbox()` cannot get correct bounding rectangle of the icons...
> Python even don't have any mature enough SVG library.
> Also tried to write an Inkscape extension to do this but... failed.

So this project is to... manually separate these icons of variable sizes in SVG into multiple independent SVG files...

`3.12.0` Seems to be the last version of `gnome-icon-theme`.

Tarball can be downloaded from [download.gnome.org](https://download.gnome.org/sources/gnome-icon-theme/3.12/)

## Differences against The Original GNOME Icon Theme
Besides the independence of icons of each sizes, other differences, including but not limited to:

### Bug fixes
Some icons have some problems (e.g. Wrong colors) so I fixed them manually:
- `categories/{16,22}/applications-science`
- `actions/16/system-search`

### Vectorization
Some icons provide rasterized/pixmap version in some size, so redraw them manually:
- `categorizes/16/applications-graphics`

### Color adjust
The color of some icons are adjusted according to my personal preference:
- `apps/*/preferences-system-windows`

### New icons
This project also contains some icons I drew (and some of them are forked from Ubuntu Humanity and GNOME Icon Theme):
- `apps/*/code-viewer-c-liked`
- `apps/*/logview`
- `mimetypes/*/text-x-readme`
- `mimetypes/*/text-x-ini`

# License
GPLv3
