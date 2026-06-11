#!/usr/bin/env python3
"""TextMiningPapa - scarica i documenti dei Papi dal sito vaticano come
file markdown (dati raw). Un solo file, struttura piatta.

Due verita' del sito, scoperte sul campo:
  - l'header HTTP dichiara ISO-8859-1, ma il contenuto e' UTF-8;
  - i Papi recenti e quelli vecchi usano due schemi di URL per la data
    (a inizio nome file, oppure incastrata col prefisso hf_...).

Uso:
    python papi.py                       # scarica tutto in data/ (ore)
    from papi import scarica, scarica_tutto, PAPI
    scarica("francesco", "angelus", anni=[2025])
"""

from __future__ import annotations

import pathlib
import re
import time
from collections import deque
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.vatican.va"

# chiave (= cartella di output) -> (slug sul sito, nome leggibile)
PAPI = {
    "francesco":         ("francesco", "Papa Francesco"),
    "leone-xiv":         ("leo-xiv", "Papa Leone XIV"),
    "benedetto-xvi":     ("benedict-xvi", "Papa Benedetto XVI"),
    "giovanni-paolo-ii": ("john-paul-ii", "Papa Giovanni Paolo II"),
}
TIPOLOGIE = ("angelus", "audiences", "homilies", "speeches",
             "messages", "letters", "cotidie", "travels")

_SESS = requests.Session()
_SESS.headers["User-Agent"] = "TextMiningPapa/2.0 (+python)"


def _get(url, delay=0.3):
    """Scarica e fa il parse di una pagina (None se fallisce)."""
    try:
        r = _SESS.get(url, timeout=30)
        r.raise_for_status()
    except requests.RequestException:
        return None
    r.encoding = "utf-8"        # l'header HTTP mente, il sito e' UTF-8
    time.sleep(delay)           # gentile col server
    return BeautifulSoup(r.text, "lxml")


def _data(url):
    """Data YYYY-MM-DD dal nome file (gestisce entrambi gli schemi)."""
    for blocco in re.findall(r"\d{8}", url.rsplit("/", 1)[-1]):
        try:
            d = datetime.strptime(blocco, "%Y%m%d")
        except ValueError:
            continue
        if 1900 <= d.year <= 2100:
            return d.strftime("%Y-%m-%d")
    return ""


def _anno(url):
    """Anno di un URL: prima dalla data nel nome, poi dal path."""
    iso = _data(url)
    if iso:
        return int(iso[:4])
    m = re.search(r"/(\d{4})(?:\.index|/)", url)
    return int(m.group(1)) if m else None


def trova_documenti(slug, tipo, anni=None, delay=0.3):
    """Crawl ricorsivo degli indici: ritorna gli URL dei documenti.

    Segue i sotto-indici (anni, trimestri) perche' gli indici grandi
    sono spezzati su piu' pagine.
    """
    radice = f"{BASE}/content/{slug}/it/{tipo}"
    coda = deque([f"{radice}.index.html"])
    visti, docs = set(), set()
    while coda and len(visti) < 500:
        url = coda.popleft()
        if url in visti:
            continue
        visti.add(url)
        sp = _get(url, delay)
        if sp is None:
            continue
        for a in sp.find_all("a", href=True):
            link = urljoin(BASE, a["href"])
            if f"/content/{slug}/it/" not in link:
                continue
            if f"/{tipo}/" not in link and f"/{tipo}." not in link:
                continue
            if "/documents/" in link and link.endswith(".html"):
                if not anni or _anno(link) in anni:
                    docs.add(link)
            elif link.endswith(".index.html") and link not in visti:
                an = _anno(link)
                if not anni or an is None or an in anni:
                    coda.append(link)
    return sorted(docs)


_RUMORE = re.compile(r"^(\[?\s*multimedia\s*\]?|_{3,}|copyright\b)", re.I)


def _corpo(sp):
    """Testo dal contenitore div.testo (corpo pulito del sito)."""
    cont = sp.select_one("div.testo") or sp.select_one("div.documento")
    if cont is None:
        return ""
    par = [p.get_text(" ", strip=True) for p in cont.find_all("p")]
    return "\n\n".join(p for p in par if p and not _RUMORE.match(p))


def _q(s):
    """Valore YAML tra virgolette, con escape minimo."""
    return '"' + s.replace('"', '\\"') + '"'


def _markdown(url, nome, tipo, sp):
    """Costruisce il markdown del documento; ritorna (testo, ha_corpo)."""
    titolo = (sp.title.get_text(strip=True)
              if sp.title else url.rsplit("/", 1)[-1])
    corpo = _corpo(sp)
    parole = len(re.findall(r"\w+", corpo))
    testo = "\n".join([
        "---",
        f"papa: {_q(nome)}",
        f"tipologia: {tipo}",
        f"data: {_data(url)}",
        f"titolo: {_q(titolo)}",
        f"url: {url}",
        f"parole: {parole}",
        "---",
        "",
        f"# {titolo}",
        "",
        corpo,
        "",
    ])
    return testo, bool(corpo.strip())


def scarica(papa, tipo, anni=None, out="data", max_n=None, delay=0.3):
    """Scarica i documenti di (papa, tipo), saltando quelli gia' presenti.

    Lo skip-se-esiste rende il download incrementale: rilanciare scarica
    solo i documenti nuovi.
    """
    slug, nome = PAPI[papa]
    cartella = pathlib.Path(out) / papa / tipo
    urls = trova_documenti(slug, tipo, set(anni) if anni else None, delay)
    if max_n:
        urls = urls[:max_n]
    n = 0
    for url in urls:
        f = cartella / url.rsplit("/", 1)[-1].replace(".html", ".md")
        if f.exists():
            continue
        sp = _get(url, delay)
        if sp is None:
            continue
        testo, ok = _markdown(url, nome, tipo, sp)
        if not ok:
            continue
        cartella.mkdir(parents=True, exist_ok=True)
        f.write_text(testo, encoding="utf-8")
        n += 1
    print(f"[{papa}/{tipo}] {n} nuovi, {len(urls)} totali online")
    return n


def scarica_tutto(papi=tuple(PAPI), tipologie=TIPOLOGIE, anni=None,
                  out="data", max_n=None, delay=0.3):
    """Scarica tutte le combinazioni (papa, tipologia) richieste."""
    tot = sum(scarica(p, t, anni, out, max_n, delay)
              for p in papi for t in tipologie)
    print(f"Totale nuovi documenti: {tot}")
    return tot


if __name__ == "__main__":
    scarica_tutto()
