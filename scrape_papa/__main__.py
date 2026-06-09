"""Esecuzione diretta: python -m scrape_papa

Esempio dimostrativo: scarica gli Angelus 2025 di tutti i Papi che ne hanno.
"""

from . import scarica_tutti

if __name__ == "__main__":
    docs = scarica_tutti(tipologie=["angelus"], anni=[2025])
    print(f"\nTotale documenti scaricati: {len(docs)}")
