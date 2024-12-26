# gnome-icon-theme-cropped

GNOME Project provides [gnome-icon-theme-3.12.0.tar.xz](https://download.gnome.org/sources/gnome-icon-theme/3.12/gnome-icon-theme-3.12.0.tar.xz), but its SVG files are... multiple icons accumulated in one SVG file, and after some struggling, I found it's nerely impossible to extract the icons separately **as SVG** (instead of rasterized PNG) via script...

> I've struggling with SVG.js but its `rbox()` cannot get correct bounding rectangle of the icons...
> Python even don't have any mature enough SVG library.
> Also tried to write an Inkscape extension to do this but... failed.

So this project is to... manually separate these icons of variable sizes in SVG into multiple independent SVG files...

`3.12.0` Seems to be the last version of `gnome-icon-theme`.

Tarball can be downloaded from [download.gnome.org](https://download.gnome.org/sources/gnome-icon-theme/3.12/)

# License
GPLv3
