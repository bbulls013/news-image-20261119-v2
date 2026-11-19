#!/usr/bin/env python3
"""Entry program for make.fun bounty news-image-20261119.

Writes the front-page image stored in this repository (entry.png) to
/output/entry.png. Standard library only, no network access, and fully
deterministic: every run produces the same bytes.
"""
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
TARGET = Path("/output/entry.png")


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    print(f"wrote {TARGET} ({TARGET.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
