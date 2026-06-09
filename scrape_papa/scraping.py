"""Rete, discovery degli indici e parsing dei documenti."""

from __future__ import annotations

import logging
import re
import time
from collections import deque
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .modello import Documento, Papa

BASE_URL = "https://www.vatican.va"

logger = logging.getLogger("scrape_papa")


# --------------------------------------------------------------------------- #
# Rete
# --------------------------------------------------------------------------- #

def nuova_sessione() -> requests.Session:
    """Crea una sessione requests con User-Agent dichiarato."""
    s = requests.Session()
    s.headers.update({"User-Agent": "TextMiningPapa/1.0 (+python)"})
    return s


def scarica(url: str, sess: requests.Session,
            delay: float = 0.3) -> BeautifulSoup | None:
    """Scarica una pagina e ne restituisce il parse, o None se fallisce.

    Il sito dichiara UTF-8 nel meta ma l'header HTTP mente (ISO-8859-1):
    forziamo UTF-8 per avere gli accenti corretti.
    """
    try:
        r = sess.get(url, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        logger.warning("fetch fallito %s: %s", url, e)
        return None
    r.encoding = "utf-8"
    if delay:
        time.sleep(delay)
    return BeautifulSoup(r.text, "lxml")


# --------------------------------------------------------------------------- #
# Date e anni (il sito usa due schemi di URL, gestiamo entrambi)
# --------------------------------------------------------------------------- #

def data_iso(url: str) -> str | None:
    """Estrae una data YYYYMMDD dal nome file -> ISO YYYY-MM-DD.

    Schema nuovo:  .../documents/20250101-angelus.html
    Schema vecchio: .../documents/hf_ben-xvi_reg_20050424_inizio.html
    """
    nome = url.rsplit("/", 1)[-1]
    for blocco in re.findall(r"\d{8}", nome):
        try:
            d = datetime.strptime(blocco, "%Y%m%d")
        except ValueError:
            continue
        if 1900 <= d.year <= 2100:
            return d.strftime("%Y-%m-%d")
    return None


def anno(url: str) -> int | None:
    """Anno di un URL: prima dalla data nel nome, poi dal path."""
    iso = data_iso(url)
    if iso:
        return int(iso[:4])
    m = re.search(r"/(\d{4})(?:\.index|/)", url)
    return int(m.group(1)) if m else None


# --------------------------------------------------------------------------- #
# Discovery: crawl ricorsivo degli indici
# --------------------------------------------------------------------------- #

def trova_documenti(papa: Papa, tipo: str, sess: requests.Session,
                    anni: set[int] | None = None,
                    delay: float = 0.3,
                    max_indici: int = 500) -> list[str]:
    """Trova tutti gli URL dei documenti di una tipologia per un Papa.

    Parte da `/content/<papa>/it/<tipo>.index.html` e segue ricorsivamente
    i sotto-indici (anni, trimestri) raccogliendo i link `/documents/...`.
    Cosi gestisce sia gli indici annuali semplici sia quelli suddivisi.
    """
    radice = f"{BASE_URL}/content/{papa.slug}/it/{tipo}"
    da_visitare: deque[str] = deque([f"{radice}.index.html"])
    visti: set[str] = set()
    documenti: set[str] = set()

    while da_visitare and len(visti) < max_indici:
        url = da_visitare.popleft()
        if url in visti:
            continue
        visti.add(url)

        soup = scarica(url, sess, delay)
        if soup is None:
            continue

        for a in soup.find_all("a", href=True):
            link = urljoin(BASE_URL, a["href"])
            # solo link interni a questa tipologia
            if f"/{tipo}/" not in link and f"/{tipo}." not in link:
                continue
            if f"/content/{papa.slug}/it/" not in link:
                continue

            if "/documents/" in link and link.endswith(".html"):
                # se filtro per anno, escludo i documenti senza anno
                if anni and (anno(link) not in anni):
                    continue
                documenti.add(link)
            elif link.endswith(".index.html") and link not in visti:
                if anni:
                    a_idx = anno(link)
                    if a_idx is not None and a_idx not in anni:
                        continue
                da_visitare.append(link)

    logger.info("[%s/%s] trovati %d documenti (%d indici visitati)",
                papa.cartella, tipo, len(documenti), len(visti))
    return sorted(documenti)


# --------------------------------------------------------------------------- #
# Parsing di un singolo documento
# --------------------------------------------------------------------------- #

# paragrafi di servizio da scartare (multimedia, separatori, copyright)
_RUMORE = re.compile(r"^(\[?\s*multimedia\s*\]?|_{3,}|copyright\b)", re.I)


def estrai_corpo(soup: BeautifulSoup) -> str:
    """Estrae il corpo preservando i paragrafi.

    Usa `div.testo` (corpo pulito del sito); fallback a `div.documento`;
    ultimo fallback ai <p> della pagina con lo slice ereditato dall'R.
    """
    cont = soup.select_one("div.testo") or soup.select_one("div.documento")
    if cont is not None:
        par = [p.get_text(" ", strip=True) for p in cont.find_all("p")]
        par = [p for p in par if p and not _RUMORE.match(p)]
        if par:
            return "\n\n".join(par)
        return cont.get_text(" ", strip=True)

    # fallback storico (come nel codice R)
    ps = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    corpo = ps[7:-4] if len(ps) > 11 else ps
    return "\n\n".join(p for p in corpo if p)


def leggi_documento(url: str, papa: Papa, tipo: str,
                    sess: requests.Session,
                    delay: float = 0.3) -> Documento | None:
    """Scarica un documento ed estrae titolo, data, testo."""
    soup = scarica(url, sess, delay)
    if soup is None:
        return None
    titolo = (soup.title.get_text(strip=True)
              if soup.title else url.rsplit("/", 1)[-1])
    testo = estrai_corpo(soup)
    return Documento(
        url=url,
        papa=papa.nome,
        tipologia=tipo,
        titolo=titolo,
        data=data_iso(url),
        testo=testo,
        n_parole=len(re.findall(r"\w+", testo)),
    )
