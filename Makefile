default: merge-to-src

merge-to-src:
	cp -r ./workspace/__prefix__/* src/

init-workspace:
	python3 ./script/gen_template.py

clear-workspace:
	rm -rf ./workspace/__prefix__
