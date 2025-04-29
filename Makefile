default: merge-to-src

merge-to-src:
	cp -r ./workspace/__prefix__/* src/

init-workspace-by-gnome-svg:
	python3 ./script/gen_template_by_gnome_svg.py

