#!/usr/bin/env python3
"""Controlla se ci sono nuovi documenti sul sito vaticano.

Confronta i documenti online con il corpus gia' scaricato in `data/` e
segnala i mancanti. Con --scarica li scarica e aggiorna l'INDEX.md.

Uso:
    python test/controlla_nuovi.py            # solo report
    python test/controlla_nuovi.py --scarica  # scarica i nuovi
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrape_papa import controlla_nuovi  # noqa: E402


def main() -> int:
    scarica = "--scarica" in sys.argv
    nuovi = controlla_nuovi(output_dir="data", scarica=scarica)

    if not nuovi:
        print("\nNessun nuovo documento: il corpus e' aggiornato.")
        return 0

    print("\n=== NUOVI DOCUMENTI ===")
    for (papa, tipo), urls in sorted(nuovi.items()):
        print(f"\n{papa} / {tipo} ({len(urls)}):")
        for u in urls:
            print(f"  {u}")
    print(f"\nTotale: {sum(len(v) for v in nuovi.values())} nuovi"
          f"{' (scaricati)' if scarica else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
