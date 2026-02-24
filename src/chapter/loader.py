from dataclasses import dataclass
from pathlib import Path
from typing import List
from src.core.config import IMAGE_EXTENSIONS

@dataclass
class Chapter:
    title: str
    images: List[Path]

def load_chapters(root: Path) -> List[Chapter]:
    """
    扫描子目录，获取各板块的图片路径
    """

    if not root.exists():
        raise FileNotFoundError(f"{root} 不存在")

    if not root.is_dir():
        raise NotADirectoryError(f"{root} 不是目录")

    chapters: List[Chapter] = []

    for chapter_dir in sorted(root.iterdir()):
        if not chapter_dir.is_dir():
            continue

        images = sorted(
            [
                p for p in chapter_dir.iterdir()
                if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
            ]
        )

        if not images:
            continue

        chapters.append(
            Chapter(
                title=chapter_dir.name,
                images=images
            )
        )

    return chapters

if __name__ == "__main__":
    from pprint import pprint
    from src.core.config import TEST_IMG_DIR
    chapters = load_chapters(TEST_IMG_DIR)
    pprint(chapters, indent=2)
