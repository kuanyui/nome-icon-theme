# gnome-icon-theme-fork

A fork of GNOME 2/3 default XDG icon theme, provided as SVG files. For people who feel nostalgic about Freedesktop Tango style icon.

## What is This?

I prefer the icons following Tango design guidelines over flat design. Yes I know flat design looks more unified but they are really hard to distinguish as icon.

Tango design guidelines was promoted by Freedesktop.org, and was adopted by GNOME Project and Canonical Ubuntu in GNOME 2.x era.

GNOME Project provides [gnome-icon-theme-3.12.0.tar.xz](https://download.gnome.org/sources/gnome-icon-theme/3.12/gnome-icon-theme-3.12.0.tar.xz), which is the last release of [gnome-icon-theme](https://download.gnome.org/sources/gnome-icon-theme/). but its SVG files are... multiple icons accumulated in one SVG file, and after some struggling, I found it's nerely impossible to extract the icons separately **as SVG** (instead of rasterized PNG) via script...

> I've struggling with SVG.js but its `rbox()` cannot get correct bounding rectangle of the icons...
> Python even don't have any mature enough SVG library.
> Also tried to write an Inkscape extension to do this but... failed.

So this project is to... manually separate these icons of variable sizes in SVG into multiple independent SVG files...

`3.12.0` Seems to be the last version of `gnome-icon-theme`.

Tarball can be downloaded from [download.gnome.org](https://download.gnome.org/sources/gnome-icon-theme/3.12/)

> [!NOTE]
> The directory structure of `/src` follows XDG icon theme standard, but it doesn't provide `index.theme`, you have to write by yourself if you want to use this project as a XDG-compatible icon theme. See my another project [tango-icons-collection](https://github.com/kuanyui/tango-icons-collection) for detailed information.

## Differences against The Original GNOME Icon Theme
Besides the independence of icons of each sizes, other differences are, including but not limited to:

### Bug fixes
Some icons have some problems (e.g. Wrong colors) so fixed them manually:
- `categories/{16,22}/applications-science`
- `actions/16/system-search`

### Vectorization
Some icons provide only rasterized/pixmap version in some sizes, so redraw them manually:
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

## References
Original download links of GNOME Icon Theme(for reference only):

- [gnome-icon-theme-2.20.0.tar.bz2](https://download.gnome.org/sources/gnome-icon-theme/2.20/gnome-icon-theme-2.20.0.tar.bz2)
  - Downloaded from [download.gnome.org](https://download.gnome.org/sources/gnome-icon-theme/2.20/)
  - (Found in [Wikimedia](https://commons.wikimedia.org/wiki/GNOME_Desktop_icons), **but all icons are in PNG only, except 48x48 are in SVG.**)

- [gnome-icon-theme-2.91.93.tar.gz](https://download.gnome.org/sources/gnome-icon-theme/2.91/gnome-icon-theme-2.91.93.tar.bz2)
  - Downloaded from [download.gnome.org](https://download.gnome.org/sources/gnome-icon-theme/2.91/)
  - Started from this version, it provides variable sizes, but all sizes of each icons are drawn in the same SVG file... need extra process to extract them...

- [gnome-icon-theme-3.9.5.tar.xz](https://download.gnome.org/sources/gnome-icon-theme/3.9/gnome-icon-theme-3.9.5.tar.xz)
  - Downloaded from [download.gnome.org](https://download.gnome.org/sources/gnome-icon-theme/3.9/)

- [gnome-icon-theme-3.12.0.tar.xz](https://download.gnome.org/sources/gnome-icon-theme/3.12/gnome-icon-theme-3.12.0.tar.xz)
  - Seems to be the last version of `gnome-icon-theme`.
  - Downloaded from [download.gnome.org](https://download.gnome.org/sources/gnome-icon-theme/3.12/)

- [gnome-icon-theme-extras](https://gitlab.gnome.org/Archive/gnome-icon-theme-extras)
  - Totally unused. For reference only.
  - Dwonloaded from [gitlat.gnome.org](https://gitlab.gnome.org/Archive/gnome-icon-theme-extras)

# License
GPLv3

gnome-icon-theme-fork, Fork of GNOME 2/3 Default Icon Theme.

Copyright (C) 2024, 2025 ono ono (kuanyui) <azazabc123 АТ GМАIL dot СОМ>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
