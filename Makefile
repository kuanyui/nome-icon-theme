default: merge-to-src

merge-to-src:
	cp -r ./workspace/__prefix__/* src/

init-workspace-by-gnome-svg:
	python3 ./script/gen_template_by_gnome_svg.py

install-git-hooks:     ## Install git hooks (pre-commit: SPDX header check for SVGs)
	ln -s ../../add_spdx.py .git/hooks/pre-commit

uninstall-git-hooks:   ## Uninstall git hooks
	rm .git/hooks/pre-commit
