import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Optional, cast
from pathlib import Path
from pprint import pprint
import os
import sys
import shutil

REPO_PATH = Path(os.path.dirname(__file__)).parent
WORKSPACE_PATH = REPO_PATH / 'workspace'
WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)

def ensure_only_one_svg_in_workspace() -> Path:
    svg_files = [file for file in WORKSPACE_PATH.iterdir() if file.is_file() and file.name.endswith('.svg')]
    if len(svg_files) == 1:
        return svg_files[0]
    else:
        print(f"Expect only one source todo svg file in /workspace, but got {len(svg_files)}")
        sys.exit(1)

def init_workspace() -> None:
    ori_svg_file_path = ensure_only_one_svg_in_workspace()
    dom = minidom.parse(str(ori_svg_file_path))
    icon_name = ori_svg_file_path.stem
    context_name = ''
    baseplates: List[minidom.Element] = []
    for g in dom.getElementsByTagName("g"):
        if g.getAttribute("inkscape:label") == "baseplate":
            baseplates.append(g)

    for baseplate in baseplates:
        # baseplate_parent = cast(minidom.Element, baseplate.parentNode)
        texts = baseplate.getElementsByTagName('text')
        for text in texts:
            text_label = text.getAttribute('inkscape:label')
            if text_label == 'icon-name':
                tspan_node = text.getElementsByTagName('tspan')[0].firstChild
                if tspan_node is None:
                    continue
                icon_name = str(tspan_node.nodeValue)
            elif text_label == 'context':
                tspan_node = text.getElementsByTagName('tspan')[0].firstChild
                if tspan_node is None:
                    continue
                context_name = str(tspan_node.nodeValue)
        rects = baseplate.getElementsByTagName('rect')
        print('==============================================================================================')
        print(f' (inkscape `find workspace/__prefix__ -name "{icon_name}.svg" | sort`) &')
        print('==============================================================================================')
        for rect in rects:
            size_label = rect.getAttribute('inkscape:label')
            if size_label not in ['16x16', '22x22', '24x24', '32x32', '48x48']:
                continue
            x = float(rect.getAttribute("x"))
            y = float(rect.getAttribute("y"))
            width = float(rect.getAttribute("width"))
            height = float(rect.getAttribute("height"))
            # print(f"[baseplate] {icon_name} {size_label} ==> {x}, {y}, {width}, {height}")
            create_empty_svg_file(context_name, size_label, icon_name)
            # create_svg_file(x, y, width, height, dom, output_dir, icon_name)

def create_empty_svg_file(context_name: str, size_label: str, icon_name: str):
    size = size_label.split('x')[0]
    template_file = Path('templates') / f'_empty_{size}.svg'
    output_file = WORKSPACE_PATH / '__prefix__' / context_name / size / f"{icon_name}.svg"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if not output_file.exists():
        shutil.copy(template_file, output_file)
        print(f"Create empty file: {template_file} => {output_file}")

init_workspace()
