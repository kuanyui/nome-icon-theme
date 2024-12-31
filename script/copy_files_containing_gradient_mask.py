#!/usr/bin/env python3

from pathlib import Path
from typing import List, Set
import sys
import re
import os
import shutil

REPO_PATH = Path(os.path.dirname(__file__)).parent
TARGET_PATH = REPO_PATH / 'src'
WORKSPACE_PATH = REPO_PATH / 'workspace'
WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)


def get_available_sizes(context: str) -> List[str]:
    base_path: Path = TARGET_PATH / context
    return [ p.name for p in base_path.iterdir() if p.is_dir() and p.name in ["16", "22", "24", "32", "48"] ]

def get_resized_svg_content(source_file: Path, size: str) -> str:
    content: str = source_file.read_text()
    pattern: str = r'(width|height)="[0-9]+"'
    return re.sub(pattern, f'\\1="{size}"', content, count=2)

def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: ./copy_files_containing_gradient_mask.py <source_file> <context>")
        sys.exit(1)

    source_file_path: Path = Path(sys.argv[1])
    if not source_file_path.exists():
        print(f"File {source_file_path} does not exist")
        sys.exit(1)
    if source_file_path.suffix != ".svg":
        print(f"File {source_file_path} is not an svg file")
        sys.exit(1)
    icon_name: str = source_file_path.name
    context: str = sys.argv[2]
    sizes: List[str] = get_available_sizes(context)

    for size in sizes:
        modified_svg_content: str = get_resized_svg_content(source_file_path, size)
        target_path: Path = Path.cwd() / "src" / context / size / icon_name
        target_path.write_text(modified_svg_content)

if __name__ == "__main__":
    main()