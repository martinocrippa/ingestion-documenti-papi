"""Costruzione del corpus markdown, indice e controllo aggiornamenti."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Sequence

from .modello import PAPI, TIPOLOGIE, Documento, Papa
from .scraping import leggi_documento, logger, nuova_sessione, trova_documenti


# --------------------------------------------------------------------------- #
# Markdown di un documento
# --------------------------------------------------------------------------- #

def _yaml(s: str) -> str:
    """Mette tra virgolette un valore YAML, con escape minimo."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_markdown(doc: Documento) -> str:
    """Compone il markdown (frontmatter + testo) di un documento."""
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
# Scrittura su disco
# --------------------------------------------------------------------------- #

def _salva(urls, papa, tipo, sess, output_dir, delay) -> list[Documento]:
    """Scarica e scrive su disco una lista di URL; ritorna i documenti."""
    cartella = Path(output_dir) / papa.cartella / tipo
    cartella.mkdir(parents=True, exist_ok=True)
    docs: list[Documento] = []
    for url in urls:
        doc = leggi_documento(url, papa, tipo, sess, delay)
        if doc is None or not doc.testo.strip():
            continue
        (cartella / nome_file(url)).write_text(
            to_markdown(doc), encoding="utf-8")
        docs.append(doc)
        if len(docs) % 25 == 0:
            logger.info("[%s/%s] salvati %d/%d",
                        papa.cartella, tipo, len(docs), len(urls))
    return docs


def scarica_papa(papa: Papa,
                 tipologie: Sequence[str] = TIPOLOGIE,
                 anni: Iterable[int] | None = None,
                 output_dir: str | Path = "data",
                 max_per_tipo: int | None = None,
                 delay: float = 0.3) -> list[Documento]:
    """Scarica e salva in markdown i documenti di un Papa.

    anni : se indicato, limita agli anni in elenco (per test/sottoinsiemi).
    max_per_tipo : tetto di documenti per tipologia (utile per i test).
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
        docs = _salva(urls, papa, tipo, sess, output_dir, delay)
        raccolti += docs
        logger.info("[%s/%s] completato: %d documenti",
                    papa.cartella, tipo, len(docs))

    return raccolti


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


# --------------------------------------------------------------------------- #
# Indice
# --------------------------------------------------------------------------- #

def scrivi_index(documenti: list[Documento],
                 output_dir: str | Path = "data") -> Path:
    """Genera l'INDEX.md raggruppato per Papa e tipologia."""
    righe = [
        "# Documenti dei Papi", "",
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


def _leggi_frontmatter(path: Path) -> dict[str, str]:
    """Legge le coppie chiave: valore del frontmatter YAML di un file .md."""
    testo = path.read_text(encoding="utf-8")
    if not testo.startswith("---"):
        return {}
    fine = testo.find("\n---", 3)
    dati: dict[str, str] = {}
    for riga in testo[3:fine if fine != -1 else None].splitlines():
        chiave, sep, valore = riga.partition(":")
        if not sep:
            continue
        valore = valore.strip()
        if len(valore) >= 2 and valore[0] == '"' and valore[-1] == '"':
            valore = valore[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        dati[chiave.strip()] = valore
    return dati


def ricostruisci_index(output_dir: str | Path = "data") -> Path:
    """Ricostruisce l'INDEX.md leggendo il frontmatter dei file su disco.

    Utile dopo aggiornamenti incrementali: l'indice resta coerente con tutti
    i documenti presenti, senza tenerli in memoria.
    """
    docs: list[Documento] = []
    for md in Path(output_dir).rglob("*.md"):
        if md.name == "INDEX.md":
            continue
        fm = _leggi_frontmatter(md)
        docs.append(Documento(
            url=fm.get("url", ""),
            papa=fm.get("papa", ""),
            tipologia=fm.get("tipologia", ""),
            titolo=fm.get("titolo", md.stem),
            data=fm.get("data") or None,
            testo="",
            n_parole=int(fm.get("parole") or 0),
        ))
    return scrivi_index(docs, output_dir)


# --------------------------------------------------------------------------- #
# Controllo dei nuovi documenti
# --------------------------------------------------------------------------- #

def _file_locali(output_dir: str | Path, papa: Papa, tipo: str) -> set[str]:
    """Nomi dei file markdown gia' presenti per (papa, tipo)."""
    cartella = Path(output_dir) / papa.cartella / tipo
    if not cartella.is_dir():
        return set()
    return {p.name for p in cartella.glob("*.md")}


def controlla_nuovi(papi: Iterable[str] = tuple(PAPI),
                    tipologie: Sequence[str] = TIPOLOGIE,
                    output_dir: str | Path = "data",
                    delay: float = 0.3,
                    scarica: bool = False) -> dict[tuple[str, str], list[str]]:
    """Segnala (e opzionalmente scarica) i documenti nuovi rispetto a data/.

    Confronta gli indici online con i file gia' presenti: visita solo le
    pagine indice, quindi e' leggero (non riscarica l'intero corpus).
    Con scarica=True salva i nuovi e ricostruisce l'INDEX.md.

    Returns: {(papa, tipo): [url nuovi]} per le sole coppie con novita'.
    """
    sess = nuova_sessione()
    nuovi: dict[tuple[str, str], list[str]] = {}
    scaricati: list[Documento] = []

    for chiave in papi:
        papa = PAPI[chiave]
        for tipo in tipologie:
            urls = trova_documenti(papa, tipo, sess, delay=delay)
            locali = _file_locali(output_dir, papa, tipo)
            mancanti = [u for u in urls if nome_file(u) not in locali]
            if not mancanti:
                continue
            nuovi[(papa.cartella, tipo)] = mancanti
            logger.info("[%s/%s] %d nuovi documenti",
                        papa.cartella, tipo, len(mancanti))
            if scarica:
                scaricati += _salva(
                    mancanti, papa, tipo, sess, output_dir, delay)

    tot = sum(len(v) for v in nuovi.values())
    if tot == 0:
        logger.info("Nessun nuovo documento: il corpus e' aggiornato.")
    elif scarica and scaricati:
        logger.info("Scaricati %d nuovi documenti; ricostruisco l'INDEX.md.",
                    len(scaricati))
        ricostruisci_index(output_dir)
    else:
        logger.info("Totale nuovi documenti: %d", tot)

    return nuovi
