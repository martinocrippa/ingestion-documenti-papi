#!/usr/bin/env python3
"""Download completo: tutti i Papi, tutte le tipologie, tutti gli anni.

ATTENZIONE: scarica decine di migliaia di documenti dal sito vaticano,
puo' richiedere diverse ore. Salva il corpus markdown in `data/`.

Uso:
    python test/scarica_tutto.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrape_papa import scarica_tutti  # noqa: E402


def main() -> int:
    docs = scarica_tutti(output_dir="data", delay=0.3)
    print(f"\nTotale documenti scaricati: {len(docs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
