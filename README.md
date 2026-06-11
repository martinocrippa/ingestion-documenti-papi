# ingestion-documenti-papi

Scarica i documenti dei Papi dal sito vaticano e li salva come **file
markdown** (un file per documento, con frontmatter YAML e testo pulito).

**Questo repository fa una cosa sola: l'ingestion dei dati raw.** Niente
arricchimento, niente analisi, niente database. Quelli vivono in repository
separati (vedi [Prossimi passi](#prossimi-passi)).

**Papi:** Francesco · Leone XIV · Benedetto XVI · Giovanni Paolo II.

---

## Come è nato e come l'abbiamo rivisto

**Cosa avevamo pensato (2019).** Un progetto in R che faceva tutto insieme:
scraping dei documenti *e* text mining (pulizia, frequenze, topic modeling con
LSA/LDA/NMF), con l'idea di arrivare a un'app Shiny e a un articolo.

**Cosa abbiamo fatto (2026).** Ripreso dopo ~7 anni: porting a Python,
aggiornamento al sito vaticano attuale, scaricati ~25.000 documenti dei 4 Papi
in markdown. Poi abbiamo valutato le tecniche moderne di analisi e pianificato
una pipeline ricca.

**Come l'abbiamo rivisto.** Quella pipeline era sproporzionata rispetto
all'obiettivo, e mescolava cose diverse nello stesso posto. Abbiamo separato le
responsabilità in stadi, un repository ciascuno:

1. **ingestion** (questo repo) — scaricare i dati raw, in modo semplice e robusto;
2. **dati raw** — la cartella `data/`, tenuta in locale (rigenerabile);
3. **enrichment** — database arricchito (in un repo dedicato);
4. **analisi & esposizione** — analisi e dashboard (in un repo dedicato).

Di conseguenza il codice è stato ridotto a **un solo file** per linguaggio
(`papi.py`, `ImportPapaDocument.r`), con strutture dati elementari e senza
sovrastrutture (niente package, niente classi, niente indice da mantenere). Il
controllo dei "nuovi documenti" è diventato gratuito: lo scraper **salta i file
già presenti**, quindi rilanciarlo scarica solo ciò che manca.

---

## Installazione

Richiede **Python ≥ 3.9** (consigliato 3.12) e le librerie `requests`,
`beautifulsoup4`, `lxml`.

```bash
# Opzione A — conda (consigliata)
conda env create -f setup/environment.yml
conda activate textminingpapa

# Opzione B — venv + pip
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Dettagli in [setup/README.md](setup/README.md). Con l'ambiente attivo,
`python` è Python 3.

## Uso

```bash
python papi.py              # scarica tutto in data/ (alcune ore)
python test/smoke_test.py   # test rapido (3 angelus x 4 Papi -> data_test/)
python test/check_dati.py   # check sui dati: conteggi e temi nel corpus
```

Oppure come libreria:

```python
from papi import scarica, scarica_tutto, PAPI

scarica("francesco", "angelus", anni=[2025])   # un Papa, un tipo, un anno
scarica_tutto(anni=range(2013, 2025))           # sottoinsieme
scarica_tutto()                                  # tutto
```

Rilanciare `python papi.py` riscarica **solo i documenti nuovi** (gli altri
esistono già su disco).

---

## Le primitive del progetto

Tutto `papi.py` si regge su pochi mattoni:

| Primitiva | Cosa fa |
|---|---|
| `PAPI` | dizionario `chiave → (slug sul sito, nome)`. La chiave è anche la cartella. |
| `TIPOLOGIE` | tupla dei tipi di documento (`angelus`, `homilies`, …). |
| `_get(url)` | scarica una pagina e la fa parsare; forza UTF-8, pausa fra le richieste. |
| `_data(url)` / `_anno(url)` | estraggono la data dal nome file (gestendo i **due schemi di URL** del sito). |
| `trova_documenti(slug, tipo)` | crawl ricorsivo degli indici → lista di URL dei documenti (segue i sotto-indici annuali/trimestrali). |
| `_corpo(sp)` | estrae il testo pulito dal contenitore `div.testo`. |
| `_markdown(...)` | compone frontmatter + corpo. |
| `scarica(papa, tipo)` | mette tutto insieme e scrive i file, **saltando quelli esistenti**. |

Due fatti del sito, scoperti sul campo e annotati nel codice:

1. l'header HTTP dichiara `ISO-8859-1`, ma il contenuto è **UTF-8**;
2. i Papi recenti e quelli vecchi usano **due schemi di URL** diversi per la
   data (`20250101-angelus.html` vs `hf_ben-xvi_..._20050424_...html`).

## Output

```
data/
  francesco/angelus/20250101-angelus.md
  giovanni-paolo-ii/angelus/hf_jp-ii_ang_20030101.md
  ...
```

```markdown
---
papa: "Papa Francesco"
tipologia: angelus
data: 2025-01-01
titolo: "Angelus, 1° gennaio 2025, Solennità di Maria SS.ma Madre di Dio"
url: https://www.vatican.va/content/francesco/it/angelus/2025/documents/20250101-angelus.html
parole: 862
---

# Angelus, 1° gennaio 2025, ...

Cari fratelli e sorelle, buon anno! ...
```

I dati non sono versionati in git (rigenerabili, ~260 MB, testi sotto
copyright): chiunque li ricrea con `python papi.py`.

---

## Versione R

`ImportPapaDocument.r` è l'equivalente monofile in R (rvest): stessa logica,
stesso output markdown, stesso skip-se-esiste. La versione di riferimento
testata è quella Python.

```r
Rscript ImportPapaDocument.r            # scarica tutto in data/
# oppure: source("ImportPapaDocument.r"); scarica("francesco", "angelus", 2025)
```

---

## Primi risultati (solo un check, non un'analisi)

`test/check_dati.py` dà un primo sguardo al corpus con un semplice conteggio di
parole chiave. Esempio — *"Papa Francesco parla solo di migranti?"* → **no**: è
il tema meno citato anche da lui (12% dei documenti), mentre pace (54%) e
famiglia (52%) dominano come per tutti i Papi. Rispetto ai predecessori si
stacca però su **migranti** e **poveri** (lift ~1,2-1,6).

⚠️ È solo un conteggio di stringhe, con limiti precisi: non coglie il
significato. Quando Francesco parla di ambiente come *"casa comune"* o *"sorella
madre terra"*, la regola non lo riconosce come tema "ambiente". Superare questo
è esattamente il compito dell'analisi semantica (embeddings) nel repo di
enrichment.

## Prossimi passi

L'analisi non vive qui. Prosegue in repository separati, alimentati da questo
corpus markdown:

- **enrichment** — carica e arricchisce i documenti in un database (topic,
  entità, sentiment, frame morali/valoriali, embeddings, metriche di stile);
- **analisi & esposizione** — trend e narrazioni nel tempo, keyness tra Papi,
  RAG/Q&A, confronto fra pontificati, dashboard.

Lì confluiranno anche la rassegna delle tecniche e i risultati preliminari,
tenuti fuori da questo repo che resta dedicato al solo download.
