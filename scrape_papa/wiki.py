"""Generazione della wiki markdown e orchestrazione del download."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Sequence

from .modello import PAPI, TIPOLOGIE, Documento, Papa
from .scraping import leggi_documento, logger, nuova_sessione, trova_documenti


# --------------------------------------------------------------------------- #
# Output markdown
# --------------------------------------------------------------------------- #

def _yaml(s: str) -> str:
    """Mette tra virgolette un valore YAML, con escape minimo."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_markdown(doc: Documento) -> str:
    """Compone il contenuto markdown (frontmatter + testo) di un documento."""
    return "\n".join([
        "---",
        f"papa: {_yaml(doc.papa)}",
        f"tipologia: {doc.tipologia}",
        f"data: {doc.data or ''}",
        f"titolo: {_yaml(doc.titolo)}",
        f"url: {doc.url}",
        f"parole: {doc.n_parole}",
        "---",
        "",
        f"# {doc.titolo}",
        "",
        f"- **Papa:** {doc.papa}",
        f"- **Tipologia:** {doc.tipologia}",
        f"- **Data:** {doc.data or 'n/d'}",
        f"- **Fonte:** <{doc.url}>",
        "",
        "---",
        "",
        doc.testo,
        "",
    ])


def nome_file(url: str) -> str:
    """Nome file markdown a partire dall'URL del documento."""
    stem = url.rsplit("/", 1)[-1].removesuffix(".html")
    return re.sub(r"[^\w.-]", "_", stem) + ".md"


# --------------------------------------------------------------------------- #
# Orchestrazione
# --------------------------------------------------------------------------- #

def scarica_papa(papa: Papa,
                 tipologie: Sequence[str] = TIPOLOGIE,
                 anni: Iterable[int] | None = None,
                 output_dir: str | Path = "data",
                 max_per_tipo: int | None = None,
                 delay: float = 0.3) -> list[Documento]:
    """Scarica e salva in markdown i documenti di un Papa.

    Parameters
    ----------
    papa : oggetto Papa (vedi dizionario PAPI).
    tipologie : tipologie di documenti da scaricare.
    anni : se indicato, limita agli anni in elenco (per test/sottoinsiemi).
    output_dir : cartella radice di output.
    max_per_tipo : cap di documenti per tipologia (utile per i test).
    delay : pausa fra le richieste HTTP (gentilezza verso il server).
    """
    anni_set = set(anni) if anni is not None else None
    sess = nuova_sessione()
    raccolti: list[Documento] = []

    for tipo in tipologie:
        urls = trova_documenti(papa, tipo, sess, anni_set, delay)
        if max_per_tipo:
            urls = urls[:max_per_tipo]
        if not urls:
            continue

        cartella = Path(output_dir) / papa.cartella / tipo
        cartella.mkdir(parents=True, exist_ok=True)

        n = 0
        for url in urls:
            doc = leggi_documento(url, papa, tipo, sess, delay)
            if doc is None or not doc.testo.strip():
                continue
            (cartella / nome_file(url)).write_text(
                to_markdown(doc), encoding="utf-8")
            raccolti.append(doc)
            n += 1
            if n % 25 == 0:
                logger.info("[%s/%s] salvati %d/%d",
                            papa.cartella, tipo, n, len(urls))

        logger.info("[%s/%s] completato: %d documenti",
                    papa.cartella, tipo, n)

    return raccolti


def scrivi_index(documenti: list[Documento],
                 output_dir: str | Path = "data") -> Path:
    """Genera l'INDEX.md della wiki, raggruppato per Papa e tipologia."""
    righe = [
        "# Wiki documenti dei Papi", "",
        f"Totale documenti indicizzati: **{len(documenti)}**", "",
    ]
    cartella_di = {p.nome: p.cartella for p in PAPI.values()}

    per_papa: dict[str, list[Documento]] = {}
    for d in documenti:
        per_papa.setdefault(d.papa, []).append(d)

    for papa in sorted(per_papa):
        docs = per_papa[papa]
        righe += [f"## {papa} ({len(docs)} documenti)", ""]
        per_tipo: dict[str, list[Documento]] = {}
        for d in docs:
            per_tipo.setdefault(d.tipologia, []).append(d)
        for tipo in sorted(per_tipo):
            tdocs = sorted(per_tipo[tipo],
                           key=lambda x: x.data or "", reverse=True)
            righe += [f"### {tipo} ({len(tdocs)})", ""]
            for d in tdocs:
                rel = f"{cartella_di[d.papa]}/{d.tipologia}/{nome_file(d.url)}"
                righe.append(f"- [{d.data or 'n/d'} — {d.titolo}]({rel})")
            righe.append("")

    percorso = Path(output_dir) / "INDEX.md"
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text("\n".join(righe), encoding="utf-8")
    logger.info("scritto %s", percorso)
    return percorso


def scarica_tutti(papi: Iterable[str] = tuple(PAPI),
                  tipologie: Sequence[str] = TIPOLOGIE,
                  anni: Iterable[int] | None = None,
                  output_dir: str | Path = "data",
                  max_per_tipo: int | None = None,
                  delay: float = 0.3) -> list[Documento]:
    """Scarica i Papi richiesti e scrive l'INDEX.md complessivo."""
    tutti: list[Documento] = []
    for chiave in papi:
        papa = PAPI[chiave]
        logger.info("===== PAPA: %s =====", papa.nome)
        tutti += scarica_papa(papa, tipologie, anni, output_dir,
                              max_per_tipo, delay)
    scrivi_index(tutti, output_dir)
    return tutti
