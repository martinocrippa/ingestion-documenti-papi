#!/usr/bin/env python3
"""Smoke test: scarica pochi angelus per ciascun Papa e verifica.

Controllo rapido che lo scraper funzioni (4 Papi, 2 schemi di URL) prima di
lanciare il download completo. Scarica in data_test/.

Uso: python test/smoke_test.py
"""

import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from papi import scarica  # noqa: E402

CASI = [
    ("francesco", [2025]),          # schema URL nuovo
    ("leone-xiv", [2025]),          # schema URL nuovo
    ("benedetto-xvi", [2006]),      # schema URL vecchio
    ("giovanni-paolo-ii", [2003]),  # schema URL vecchio
]


def main():
    shutil.rmtree("data_test", ignore_errors=True)
    tot = 0
    for papa, anni in CASI:
        tot += scarica(papa, "angelus", anni=anni,
                       out="data_test", max_n=3, delay=0.2)
    ok = tot >= 6
    print("\nESITO:", "OK" if ok else "FALLITO", f"({tot} documenti)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
