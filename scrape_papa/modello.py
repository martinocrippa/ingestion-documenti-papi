"""Modelli dati e anagrafica dei Papi."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Papa:
    """Un Papa: slug sul sito, nome leggibile, nome cartella di output."""

    slug: str
    nome: str
    cartella: str


PAPI: dict[str, Papa] = {
    "francesco": Papa("francesco", "Papa Francesco", "francesco"),
    "leone-xiv": Papa("leo-xiv", "Papa Leone XIV", "leone-xiv"),
    "benedetto-xvi": Papa(
        "benedict-xvi", "Papa Benedetto XVI", "benedetto-xvi"),
    "giovanni-paolo-ii": Papa(
        "john-paul-ii", "Papa Giovanni Paolo II", "giovanni-paolo-ii"),
}

# tipologie disponibili (segmento URL del sito vaticano)
TIPOLOGIE = (
    "angelus", "audiences", "homilies", "speeches",
    "messages", "letters", "cotidie", "travels",
)


@dataclass
class Documento:
    """Un documento estratto, pronto per essere scritto in markdown."""

    url: str
    papa: str
    tipologia: str
    titolo: str
    data: str | None          # ISO YYYY-MM-DD
    testo: str
    n_parole: int
