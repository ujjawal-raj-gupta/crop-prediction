from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.db import init_schema


def main() -> None:
    init_schema()
    print("OK: schema initialized")


if __name__ == "__main__":
    main()

