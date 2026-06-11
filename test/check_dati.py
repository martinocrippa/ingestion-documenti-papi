#!/usr/bin/env python3
"""Check sui dati scaricati: conteggi, presenza di temi e lift fra i Papi.

Verifica veloce sul corpus (solo stdlib): quanti documenti per Papa, in quanti
compare ciascun tema, e il "lift" = % del Papa diviso la media fra i Papi
(>1 = sopra la media, <1 = sotto).

NON e' un'analisi seria: e' un match di parole chiave (presenza si'/no, niente
contesto ne' sinonimi). L'analisi vera vivra' nel repo di ingestion/analisi.

Uso: python test/check_dati.py
"""

import collections
import pathlib
import re

# tema -> regex (basta una occorrenza, case-insensitive, su radici di parola)
TEMI = {
    "migranti": r"migrant|rifugiat|profugh",
    "pace": r"\bpace\b|guerra|conflitt",
    "famiglia": r"famigli",
    "ambiente": r"ambient|creato|ecolog",
    "poveri": r"pover|emarginat",
}


def main(data="data"):
    radice = pathlib.Path(data)
    if not radice.is_dir():
        print(f"Cartella {data}/ assente: scarica prima con `python papi.py`.")
        return 1

    per_papa = collections.Counter()
    per_tema = collections.Counter()   # (papa, tema) -> n documenti
    for f in radice.rglob("*.md"):
        parti = f.relative_to(radice).parts
        if len(parti) < 2:             # salta INDEX.md e file di root
            continue
        papa = parti[0]
        per_papa[papa] += 1
        testo = f.read_text(encoding="utf-8").lower()
        for tema, rx in TEMI.items():
            if re.search(rx, testo):
                per_tema[(papa, tema)] += 1

    papi = sorted(per_papa)

    print("Documenti per Papa:")
    for papa in papi:
        print(f"  {papa:22} {per_papa[papa]}")

    # percentuale di documenti che citano il tema, per Papa
    pct = {(papa, tema): 100 * per_tema[(papa, tema)] / per_papa[papa]
           for papa in papi for tema in TEMI}

    print("\nTemi: % che li citano e lift (% / media fra i Papi):")
    for tema in TEMI:
        media = sum(pct[(p, tema)] for p in papi) / len(papi)
        print(f"\n  {tema}  (media {media:.1f}%)")
        for p in papi:
            lift = pct[(p, tema)] / media if media else 0
            print(f"    {p:22} {pct[(p, tema)]:4.0f}%   lift {lift:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
