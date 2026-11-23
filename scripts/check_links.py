"""Comprueba enlaces relativos de Markdown en el repo de specs.

Ignora enlaces absolutos (http/https), anclas y mailto. Falla si un enlace
relativo apunta a un archivo o carpeta que no existe.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\]\((?!https?:|#|mailto:)([^)]+)\)")


def main() -> int:
    broken: list[str] = []
    for md in ROOT.rglob("*.md"):
        if "node_modules" in md.parts or ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            target = match.group(1).split("#", 1)[0].strip()
            if not target:
                continue
            if not (md.parent / target).resolve().exists():
                broken.append(f"{md.relative_to(ROOT)} -> {match.group(1)}")
    if broken:
        print(f"Enlaces relativos roto(s): {len(broken)}")
        for item in broken:
            print(f" - {item}")
        return 1
    print("OK: enlaces relativos válidos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
