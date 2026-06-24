# ingestion-documenti-papi

Scarica i documenti dei Papi dal sito vaticano e li salva come **file
markdown** (un file per documento, con frontmatter YAML e testo pulito).

**Questo repository fa una cosa sola: l'ingestion dei dati raw.** Niente
arricchimento, niente analisi, niente database. Quelli vivono in repository
separati (vedi [Prossimi passi](#prossimi-passi)).

**Papi:** Francesco · Leone XIV · Benedetto XVI · Giovanni Paolo II.

---

## Da dove nasce

Nasce da una di quelle domande grandi che capita di farsi tra amici, leggendo i
giornali: di che cosa parlano *davvero* i Papi? C'è una continuità tra un
pontificato e l'altro, o ognuno tira da un'altra parte? Quando un titolo dice
"il Papa parla solo di migranti" o "di ambiente", è vero o è il taglio del
giornale? Sono discorsi che finiscono in fretta sul senso della vita, sulla
fede, su che cosa la Chiesa dice al mondo — e a un certo punto è venuta voglia
di **smettere di tirare a indovinare e guardare i dati**.

I dati ci sono: decenni di Angelus, omelie, discorsi, messaggi, tutti pubblicati
sul sito del Vaticano. Bastava raccoglierli in modo ordinato per poterci poi
fare sopra domande serie — confronti tra Papi, temi nel tempo, ricerca per
significato. Questo repository è il **primo gradino**: portare a casa quei testi,
puliti e in un formato su cui si può lavorare. Le risposte vere arrivano dopo,
negli stadi successivi del progetto.

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
python papi.py              # scarica tutto in data/ (diverse ore: Crawl-delay 2s)
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

## Il disegno: poche primitive che si compongono

L'idea di fondo è semplice e dichiarata: **niente sovrastrutture**. Non c'è un
package, non ci sono classi, non c'è un framework. C'è un solo file fatto di
**poche primitive** — piccole funzioni che fanno una cosa sola e si combinano,
appoggiate su strutture dati elementari (un dizionario per i Papi, una tupla per
le tipologie). Si legge dall'alto verso il basso come una ricetta: `_get`
scarica, `_data`/`_anno` leggono la data, `trova_documenti` raccoglie gli URL,
`_corpo`/`_markdown` costruiscono il file, `scarica` mette tutto insieme.

Il vantaggio non è estetico: quando ogni pezzo è piccolo e isolato, capirlo,
testarlo e cambiarlo costa poco. Funzionalità che altrove richiederebbero codice
qui escono "gratis" dalla composizione — per esempio il download incrementale è
semplicemente *"se il file esiste, salta"*, non un sistema di sincronizzazione.
Si aggiunge complessità solo quando il sito reale la impone (vedi i due fatti
qui sotto), mai per principio.

Tutto `papi.py` si regge quindi su pochi mattoni:

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

## Robots.txt e copyright

Lo scraping qui è pensato per essere **educato e a norma**, per uso personale e
di studio:

- **robots.txt** — il [robots.txt di vatican.va](https://www.vatican.va/robots.txt)
  consente la scansione di tutto (`Allow: *`) ma chiede `Crawl-delay: 2`. Lo
  script rispetta la pausa di **2 secondi** tra una richiesta e l'altra
  (costante `CRAWL_DELAY` in `papi.py`); per questo un download completo richiede
  diverse ore. Un `User-Agent` esplicito identifica il client.
- **Copyright** — i testi sono di **© Libreria Editrice Vaticana / Dicastero per
  la Comunicazione**. Per questo **non vengono ridistribuiti**: la cartella
  `data/` è in `.gitignore` e nel repo non è pubblicato nessun testo reale (solo
  un documento finto di esempio negli altri repo). I file si rigenerano in
  locale dalla fonte ufficiale e servono ad analisi personali e di ricerca, con
  citazione della fonte (l'`url` originale è nel frontmatter di ogni file). Per
  usi diversi (es. ripubblicazione o usi commerciali) va richiesta
  l'autorizzazione alla Libreria Editrice Vaticana.

In breve: scarichiamo ciò che il sito permette, alla velocità che chiede, e
teniamo i testi protetti fuori dal versionamento.

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
è esattamente il compito dell'analisi semantica (embeddings) nei repo a valle.

👉 Tabelle complete (%, lift per Papa) e i limiti nel dettaglio in
[`risultati-preliminari.md`](risultati-preliminari.md).

## Prossimi passi

L'analisi non vive qui. Prosegue in repository separati, alimentati da questo
corpus markdown:

- **enrichment** — carica e arricchisce i documenti in un **vector database
  embedded e locale** (LanceDB): embeddings + ricerca ibrida, e a seguire topic,
  entità, sentiment, frame morali/valoriali, metriche di stile;
- **analisi & esposizione** — trend e narrazioni nel tempo, keyness tra Papi,
  RAG/Q&A, confronto fra pontificati, dashboard.

Lì confluiranno anche la rassegna delle tecniche e i risultati preliminari,
tenuti fuori da questo repo che resta dedicato al solo download.
