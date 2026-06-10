#!/usr/bin/env python3
"""Smoke test: scarica pochi documenti per ciascun Papa e verifica.

Esegue un controllo rapido (3 angelus per Papa, anni campione) per
confermare che lo scraping funzioni prima di lanciare il download completo.

Uso:
    python test/smoke_test.py
"""

import sys
from pathlib import Path

# rende importabile scrape_papa anche lanciando dalla cartella test/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrape_papa import scarica_papa, scrivi_index, PAPI  # noqa: E402

CASI = [
    ("francesco", [2025]),          # schema URL nuovo
    ("leone-xiv", [2025]),          # schema URL nuovo
    ("benedetto-xvi", [2006]),      # schema URL vecchio
    ("giovanni-paolo-ii", [2003]),  # schema URL vecchio
]


def main() -> int:
    tutti = []
    for chiave, anni in CASI:
        tutti += scarica_papa(
            PAPI[chiave], tipologie=["angelus"], anni=anni,
            output_dir="data_test", max_per_tipo=3, delay=0.2,
        )
    scrivi_index(tutti, output_dir="data_test")

    print(f"\n=== RISULTATO: {len(tutti)} documenti ===")
    for d in tutti:
        print(f"  {d.papa:24} {str(d.data):12} "
              f"{d.n_parole:5}w  {d.titolo[:45]}")

    # verifiche minime
    ok = len(tutti) >= 9 and all(d.testo.strip() for d in tutti)
    print("\nESITO:", "OK" if ok else "FALLITO")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
