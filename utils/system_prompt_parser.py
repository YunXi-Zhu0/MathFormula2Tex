from pathlib import Path

def parse_system_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")
