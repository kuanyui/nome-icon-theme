#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from typing import List, Optional, cast
from pathlib import Path
from pprint import pprint
import os
import sys
import shutil

REPO_PATH = Path(os.path.dirname(__file__)).parent
SRC_PATH = REPO_PATH / 'src'
WORKSPACE_PATH = REPO_PATH / 'workspace'
WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)

CONTEXT_NAME = "__CONTEXT__"
ICON_NAME = "__NAME__"

def validate() -> None:
    svg_files = [file for file in WORKSPACE_PATH.iterdir() if file.is_file() and file.name.endswith('.svg')]
    if len(svg_files) != 0:
        print(f"Don't place any svg files in {WORKSPACE_PATH}")
        sys.exit(1)
    if (len(sys.argv) < 3):
        print("Usage: ./gen_template_by_name.py CONTEXT_NAME ICON_NAME")
        print(f"Available contexts: {', '.join([p.name for p in SRC_PATH.iterdir() if p.is_dir()])}")
        sys.exit(2)
    else:
        global CONTEXT_NAME, ICON_NAME
        CONTEXT_NAME = sys.argv[1]
        ICON_NAME = sys.argv[2]
        if not (SRC_PATH / CONTEXT_NAME).exists():
            print(f"Context {CONTEXT_NAME} does not exist in {SRC_PATH}")
            sys.exit(3)


def main() -> None:
    ori_svg_file_path = validate()
    for size_label in ['16x16', '22x22', '24x24', '32x32', '48x48']:
        create_empty_svg_file(CONTEXT_NAME, size_label, ICON_NAME)
    print('==============================================================================================')
    print(f' (inkscape `find workspace/__prefix__ -name "{ICON_NAME}.svg" | sort`) &')
    print('==============================================================================================')

def create_empty_svg_file(context_name: str, size_label: str, icon_name: str):
    size = size_label.split('x')[0]
    template_file = REPO_PATH / 'templates' / f'_empty_{size}.svg'
    output_file = WORKSPACE_PATH / '__prefix__' / context_name / size / f"{icon_name}.svg"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if not output_file.exists():
        shutil.copy(template_file, output_file)
        print(f"Create empty file: {template_file} => {output_file}")

main()
