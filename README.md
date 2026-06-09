# TextMiningPapa

Scraping dei documenti dei Papi dal sito vaticano e costruzione di una
**wiki in markdown** pronta per l'analisi e per l'uso con LLM/RAG.

Ogni documento (angelus, omelia, discorso, ecc.) viene salvato come file
`.md` con frontmatter YAML e testo pulito, più un `INDEX.md` di
navigazione.

**Papi supportati:** Francesco · Leone XIV · Benedetto XVI · Giovanni Paolo II
(gestiti entrambi gli schemi di URL del sito, vecchio e nuovo).

> 📌 **Nota.** Progetto nato in R nel **2019** e ripreso/modernizzato nel
> **2026**, dopo circa **7 anni**: porting a Python, aggiornamento al sito
> vaticano attuale e output in formato wiki markdown per l'uso con gli LLM.

---

## Installazione

```bash
pip install -r requirements.txt
```

Dipendenze: `requests`, `beautifulsoup4`, `lxml`.

## Uso

```python
from scrape_papa import scarica_papa, scarica_tutti, scrivi_index, PAPI

# Un Papa, una tipologia, un anno (ideale per provare)
docs = scarica_papa(PAPI["francesco"], tipologie=["angelus"], anni=[2025])
scrivi_index(docs)

# Sottoinsieme mirato
scarica_tutti(papi=["benedetto-xvi", "giovanni-paolo-ii"],
              tipologie=["angelus", "homilies"], anni=range(2005, 2010))

# Download completo: tutti i Papi, tutte le tipologie, tutti gli anni
scarica_tutti()
```

Script pronti all'uso nella cartella [`test/`](test/):

```bash
python test/smoke_test.py      # test rapido (3 angelus x 4 Papi -> data_test/)
python test/scarica_tutto.py   # download completo -> data/ (richiede ore)
```

### Parametri principali

| Parametro       | Descrizione                                              |
|-----------------|----------------------------------------------------------|
| `tipologie`     | `angelus, audiences, homilies, speeches, messages, letters, cotidie, travels` |
| `anni`          | lista/range di anni (omesso = tutti)                     |
| `max_per_tipo`  | tetto di documenti per tipologia (per i test)            |
| `delay`         | pausa fra richieste HTTP (default 0.3s)                  |

## Struttura del codice

```
scrape_papa/
  modello.py    # dati: Papa, PAPI, TIPOLOGIE, Documento
  scraping.py   # rete, discovery degli indici, parsing dei documenti
  wiki.py       # generazione markdown e orchestrazione del download
  __init__.py   # API pubblica
```

## Output

```
data/
  francesco/angelus/20250101-angelus.md
  leone-xiv/angelus/20250511-regina-caeli.md
  benedetto-xvi/angelus/hf_ben-xvi_ang_20060101_world-day-peace.md
  giovanni-paolo-ii/angelus/hf_jp-ii_ang_20030101.md
  INDEX.md
```

Esempio di file generato:

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

- **Papa:** Papa Francesco
- **Data:** 2025-01-01
- **Fonte:** <https://...>

---

Cari fratelli e sorelle, buon anno! ...
```

## Stato del progetto

| Fase | Stato |
|------|-------|
| Scraping di tutti i Papi (raccolta dati) | ✅ fatto |
| Estrazione del corpo per ogni tipologia | ✅ risolto (`div.testo`) |
| Documento/indice unico | 🟡 `INDEX.md` |
| Pulizia testo (tokenizzazione, stop-word, lemmi, stemming) | ⬜ da fare |
| Studio delle frequenze | ⬜ da fare |
| Topic modeling (LSA / LDA / NMF / reti neurali) | ⬜ da fare |
| App Shiny / packaging | ⬜ da fare |
| Script di analisi (es. temi migranti, continuità tra Papi) | ⬜ da fare |

La raccolta dati è completa e modernizzata; il prossimo blocco è l'analisi
text-mining sul corpus markdown prodotto.

## Evoluzione: analisi degli argomenti con gli LLM

La wiki markdown è già pensata come *knowledge base* per modelli linguistici.
Rispetto alle tecniche classiche di text mining (LSA/LDA/NMF), gli LLM
permettono analisi semantiche più ricche e in linguaggio naturale. Direzioni
di sviluppo:

- **Topic extraction con LLM.** Far estrarre a un modello i temi principali di
  ogni documento (e tag/etichette) salvandoli nel frontmatter YAML, per poi
  aggregarli per Papa, anno e tipologia.
- **RAG sul corpus.** Indicizzare i `.md` in un vector store (embeddings) e
  interrogare in linguaggio naturale: *"Cosa dice Francesco sui migranti nel
  2024?"*, *"Come cambia il tema della pace tra i tre ultimi Papi?"*.
- **Riassunti e timeline tematiche.** Sintesi automatiche per anno/tema e
  ricostruzione dell'evoluzione di un concetto (es. *misericordia*, *guerra*,
  *ambiente*) nel tempo e tra pontificati.
- **Analisi comparativa tra Papi.** Confronto di stile, lessico e priorità
  tematiche, con citazioni puntuali ai documenti di origine (grazie all'`url`
  in frontmatter).
- **Classificazione e sentiment** su scala di corpus, con il modello come
  annotatore, e validazione su un campione.

L'idea: usare le tecniche statistiche classiche come baseline e gli LLM per
l'interpretazione semantica e l'esplorazione conversazionale del corpus.

## Versione R (storica)

`ImportPapaDocument.r` è il porting in R della stessa logica, aggiornato al
sito attuale e semplificato. La versione di riferimento testata è quella
Python (package `scrape_papa/`).

```r
df <- ImportPapaDocument("francesco", "Papa Francesco",
                         tipologie = "angelus", anni = 2025)
```
