"""TextMiningPapa - scraping dei documenti dei Papi dal sito vaticano.

Produce una *wiki markdown* (un file .md per documento + INDEX.md) pronta
per l'analisi e per l'uso con LLM/RAG.

Uso tipico::

    from scrape_papa import scarica_papa, scarica_tutti, scrivi_index, PAPI

    scarica_papa(PAPI["francesco"], tipologie=["angelus"], anni=[2025])
    scarica_tutti()  # tutti i Papi, tutte le tipologie, tutti gli anni

Moduli:
    modello   - dati: Papa, PAPI, TIPOLOGIE, Documento
    scraping  - rete, discovery degli indici, parsing dei documenti
    wiki      - generazione markdown e orchestrazione del download
"""

import logging

from .modello import PAPI, TIPOLOGIE, Documento, Papa
from .scraping import (
    anno,
    data_iso,
    estrai_corpo,
    leggi_documento,
    nuova_sessione,
    scarica,
    trova_documenti,
)
from .wiki import (
    nome_file,
    scarica_papa,
    scarica_tutti,
    scrivi_index,
    to_markdown,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

__all__ = [
    "Papa", "PAPI", "TIPOLOGIE", "Documento",
    "nuova_sessione", "scarica", "data_iso", "anno",
    "trova_documenti", "estrai_corpo", "leggi_documento",
    "to_markdown", "nome_file",
    "scarica_papa", "scrivi_index", "scarica_tutti",
]
