# TextMiningPapa

Scraping dei documenti dei Papi dal sito vaticano e costruzione di un
**corpus markdown** pronto per l'analisi e per l'uso con LLM/RAG.

Ogni documento (angelus, omelia, discorso, ecc.) viene salvato come file
`.md` con frontmatter YAML e testo pulito, più un `INDEX.md` di navigazione.

**Papi supportati:** Francesco · Leone XIV · Benedetto XVI · Giovanni Paolo II
(gestiti entrambi gli schemi di URL del sito, vecchio e nuovo).

> 📌 **Nota.** Progetto nato in R nel **2019** e ripreso/modernizzato nel
> **2026**, dopo circa **7 anni**: porting a Python, aggiornamento al sito
> vaticano attuale e output in formato markdown per l'uso con gli LLM.

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

Istruzioni complete in **[setup/README.md](setup/README.md)**. Con l'ambiente
attivo, `python` punta sempre a Python 3.

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
python test/smoke_test.py        # test rapido (3 angelus x 4 Papi -> data_test/)
python test/scarica_tutto.py     # download completo -> data/ (richiede ore)
python test/controlla_nuovi.py   # controlla nuovi documenti sul sito vaticano
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
  corpus.py     # markdown, indice, download e controllo aggiornamenti
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

## Controllo dei nuovi documenti

Per tenere il corpus aggiornato senza riscaricare tutto (confronta gli indici
online con i `.md` locali):

```bash
python test/controlla_nuovi.py            # report dei nuovi documenti
python test/controlla_nuovi.py --scarica  # scarica e ricostruisce l'INDEX.md
```

---

# Stato e piano

La raccolta dati è completa e modernizzata. L'analisi text-mining proseguirà in
un **nuovo repository** basato su questo corpus. Questo repo resta come base di
**raccolta dati + ricerca/pianificazione**.

## Dove eravamo (2019) → dove siamo (2026)

| Obiettivo originale (2019) | Stato | Approccio moderno (2026) |
|---|---|---|
| Scraping documenti dei Papi | ✅ fatto | Python, sito attuale, 4 Papi, ~25k doc in markdown |
| Estrazione corpo per tipologia | ✅ risolto | `div.testo` invece dello slice fisso |
| Pulizia testo (token, stop-word, lemmi, stemming) | 🔄 ripensato | spaCy `it`/multilingue per la baseline; per gli embedding spesso **non serve** pulizia aggressiva |
| Studio delle frequenze | ⬜ → nuovo repo | TF-IDF + **keyness** tra Papi/anni + embeddings semantici |
| Topic modeling (LSA/LDA/NMF/reti neurali) | ⬜ → nuovo repo | **BERTopic** + **dynamic topic models** (trend nel tempo) |
| App Shiny / packaging | ⬜ → nuovo repo | App/dashboard (Streamlit/Gradio) |
| Domande di analisi (migranti, continuità) | ⬜ → nuovo repo | **RAG** + dynamic topic modeling + keyness |

## Obiettivi riletti con tecniche moderne

- **Pulizia testo.** La pipeline classica (token → stop-word → lemmi → stemming)
  serve *solo* per le analisi statistiche; per l'italiano **lemmi sì, stemming
  no**. Gli approcci a embedding lavorano sul **testo grezzo**.
- **Frequenze.** Conteggi + **keyness** (log-likelihood) per "cosa caratterizza
  ciascun Papa", n-grammi, e **similarità semantica** via embeddings.
- **Topic modeling.** Da LSA/LDA/NMF a **BERTopic** + **dynamic topic models**
  (RollingLDA + change-point, o il sistema open *DTECT*) per l'evoluzione
  temporale, con **labeling LLM** sotto validazione umana. Su corpus medio LDA
  resta competitivo per interpretabilità.

## Domande di ricerca, riformulate

| Domanda (2019) | Come rispondere oggi |
|---|---|
| Di cosa parla l'ultimo Papa? Solo migranti? | Topic modeling + keyness + conteggio concetti nel tempo; RAG per citazioni |
| C'è continuità tra gli ultimi tre Papi? | Confronto topic/lessico per pontificato; distanza semantica fra corpora |
| *(nuove)* Evoluzione di pace, ambiente, misericordia? | **Dynamic topic modeling** con change-point sulle date |
| *(nuove)* Quali frame morali/valoriali ricorrono? | Annotazione frame morali (Capraro, *language-based preferences* / LENS) |

> **Principio guida (filone Quattrociocchi):** statistica classica come
> baseline, LLM per interpretazione/etichettatura, **mai come giudice autonomo**
> → validazione su gold set umano (effetto "epistemia", bias documentati).

## Architettura proposta per il nuovo repo

Workflow a 3 fasi (la Fase 1 è già completa qui):

1. **Testi** ✅ — input: il corpus markdown di questo repo.
2. **Arricchimento → database di analisi.** Per ogni documento: topic+keywords
   (BERTopic), entità (NER), sentiment + **frame morali/valoriali** (dimensioni
   **LENS** di Capraro: frame linguistico, emozione, norma), embeddings (vector
   store), metriche di stile. Storage: **frontmatter esteso** + **SQLite/Parquet**
   + **indice vettoriale**.
3. **Analisi.** Trend temporali, keyness tra Papi, evoluzione di concetti,
   **RAG/Q&A**, confronto comparativo, dashboard.

**Stack suggerito:** `sentence-transformers` (multilingue), `BERTopic`, `spaCy`
(it), `scikit-learn`, un vector store (Chroma/FAISS), un LLM per labeling/RAG.

## Documentazione

- **[resources/review-tecniche-analisi-testi.md](resources/review-tecniche-analisi-testi.md)**
  — review accademica delle tecniche, con citazioni verificate.
- **[resources/README.md](resources/README.md)** — catalogo dei paper
  (Quattrociocchi, Capraro, topic modeling, LLM-as-judge, RAG).

## Checklist di chiusura

- [x] Scraping completo (25k documenti) e corpus markdown
- [x] Tool di controllo nuovi documenti
- [x] Review delle tecniche con paper di riferimento
- [x] Ricerca mirata su Valerio Capraro (frame morali / LENS / sentiment)
- [ ] Revisione manuale di codice e documenti
- [ ] Commit finale di questo repo
- [ ] Creazione del **nuovo repository di analisi** basato su questi dati

---

## Versione R (storica)

`ImportPapaDocument.r` è il porting in R della stessa logica, aggiornato al
sito attuale e semplificato. La versione di riferimento testata è quella
Python (package `scrape_papa/`).

```r
df <- ImportPapaDocument("francesco", "Papa Francesco",
                         tipologie = "angelus", anni = 2025)
```
