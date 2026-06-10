# Review: tecniche per l'analisi di testi e narrazioni nel tempo

Review accademica orientata al progetto **TextMiningPapa** (corpus markdown di
~25k documenti papali). Le affermazioni sono verificate con fonti primarie
(arXiv / peer-reviewed); ogni voce riporta link, anno e rilevanza.

> Metodo: ricerca multi-fonte con verifica avversariale (25 fonti, 106
> affermazioni estratte, 25 verificate con voto a 3, 23 confermate).

---

## 1. Il filone Quattrociocchi (Sapienza) — cautele sull'uso degli LLM

Filone più rilevante e **cautelativo**: utile non perché studia i Papi, ma
perché definisce *come (non) usare gli LLM* per analizzare testi.

| Paper | Anno | Link | Rilevanza |
|---|---|---|---|
| **The simulation of judgment in LLMs** / *Decoding AI Judgment* | 2025 | [arXiv 2502.04426](https://arxiv.org/abs/2502.04426) · PNAS `10.1073/pnas.2518443122` | Gli LLM come giudici di credibilità si basano su **associazioni lessicali e priori statistici**, non sul ragionamento contestuale. Bias politici sistematici ed effetto **"epistemia"** (plausibilità linguistica scambiata per affidabilità). → *Monito per la Fase 3: valida sempre l'LLM-annotatore contro un gold set umano.* |
| **Generative Exaggeration in LLM Social Agents** | 2025 | [arXiv 2507.00657](https://arxiv.org/abs/2507.00657) · Online Social Networks and Media | Gli LLM "ricostruiscono" gli utenti invece di emularli, **esagerando** polarizzazione e tossicità. *"LLMs do not emulate users, they reconstruct them."* Repertorio di metriche: tossicità (Perspective API), diversità lessicale (LogTTR), coerenza ideologica. |
| **The Statistical Signature of LLMs** | feb 2026 | [arXiv 2602.18152](https://arxiv.org/abs/2602.18152) | Il testo LLM ha **maggiore regolarità/compressibilità** (misura via compressione lossless Lempel-Ziv, model-agnostic). Metrica quantitativa di regolarità lessicale e per distinguere testo sintetico da umano. Caveat: il segnale si attenua sotto ~25 frasi. |
| **The echo chamber effect on social media** | 2021 | [arXiv 2004.09603](https://arxiv.org/abs/2004.09603) · PNAS `10.1073/pnas.2023301118` | Definizione operativa canonica di echo chamber: **omofilia** + **bias di diffusione**. ⚠️ Richiede un grafo di interazioni: **non applicabile** al corpus papale (puro testo, niente rete) — va reinterpretato come analisi di contenuto/narrazione. |

---

## 2. Topic modeling: vecchia scuola vs moderna

| Approccio | Paper / fonte | Note per il progetto |
|---|---|---|
| **LDA, NMF (classici)** | [Egger & Yu, Frontiers in Sociology 2022](https://www.frontiersin.org/journals/sociology/articles/10.3389/fsoc.2022.886498/full) | Su tweet: ranking BERTopic/NMF > Top2Vec > **LDA (peggiore)**. NMF regge bene su testi brevi/sparsi. Ma i passi papali sono **medio-lunghi**: LDA torna competitivo e più interpretabile. |
| **BERTopic** | [Grootendorst 2022, arXiv 2203.05794](https://arxiv.org/abs/2203.05794) | Pipeline: embeddings transformer → UMAP → HDBSCAN → **c-TF-IDF**. Topic coerenti e interpretabili. **Scelta robusta consigliata** con sentence-transformers multilingue. |
| **Neural Topic Models (NTM)** | [Wu, Nguyen, Luu — Survey 2024, arXiv 2401.15351](https://arxiv.org/html/2401.15351v2) | Migliore **scalabilità/flessibilità** di LDA, ma ⚠️ **non** necessariamente migliore qualità/coerenza ([cfr. "Are Neural Topic Models Broken?" arXiv:2210.16162](https://arxiv.org/abs/2210.16162) — LDA/MALLET più stabile). |
| **Embedding-based (ETM)** | [Dieng et al. 2019, arXiv 1907.04907](https://arxiv.org/abs/1907.04907) | Topic in spazio di embedding; i **D-ETM** fanno evolvere i topic nel tempo (es. topic Ucraina che cambia 2020→2022). |

---

## 3. Trend / dinamica temporale delle narrazioni (cuore del progetto)

| Paper | Anno | Link | Cosa offre |
|---|---|---|---|
| **Narrative Shift Detection (DTM + LLM)** | 2025 | [arXiv 2506.20269](https://arxiv.org/html/2506.20269) | Pipeline ibrida a 2 stadi: **RollingLDA + change-point detection** restringe a pochi documenti sospetti, poi un **LLM li interpreta**. Usa il *Narrative Policy Framework* (setting, characters, plot, moral). **Direttamente trasponibile** sul corpus papale per individuare svolte narrative nel tempo. |
| **DTECT — Dynamic Topic Explorer & Context Tracker** | 2025 | [arXiv 2507.07910](https://arxiv.org/html/2507.07910) · [GitHub](https://github.com/AdhyaSuman/DTECT) | Sistema **open end-to-end**: dynamic topic modeling, rilevamento parole **trending** (burstiness × specificity × uniqueness), **labeling LLM**, summarization, interfaccia **RAG** conversazionale. Quasi pronto all'uso per la Fase 3. |

---

## 4. LLM come annotatori / RAG

| Paper | Link | Rilevanza |
|---|---|---|
| **LLMs-as-Judges: A Comprehensive Survey** | [arXiv 2412.05579](https://arxiv.org/abs/2412.05579) | Paradigma scalabile per valutare testi; documenta bias (position/verbosity/self-enhancement). Da combinare col monito empirico di Quattrociocchi (epistemia). |
| **Can LLMs Transform Computational Social Science?** | [arXiv 2305.03514](https://arxiv.org/abs/2305.03514) | LLM come zero-shot annotatori per task di scienze sociali; quadro di riferimento e limiti. |
| **Retrieval-Augmented Generation — Survey** | [arXiv 2312.10997](https://arxiv.org/pdf/2312.10997) | Stato dell'arte RAG: come interrogare un corpus in linguaggio naturale ancorando le risposte ai documenti. Per il Q&A sul corpus papale. |

---

## 5. Valerio Capraro — il linguaggio morale che muove i comportamenti

Filone molto rilevante per analizzare **frame morali e valori** nei testi
papali. Contributo centrale: le **"language-based preferences"** — il *modo*
in cui un'azione è descritta (specie con linguaggio morale) influenza
causalmente il comportamento, **a parità di esiti**. Ricerca verificata
(25/25 affermazioni confermate, 0 refutate).

| Paper | Anno | Link | Rilevanza / metodo |
|---|---|---|---|
| **The power of moral words: Loaded language…** (Capraro & Vanzo) | 2019 | [arXiv 1901.02314](https://arxiv.org/abs/1901.02314) · J. Decision Making | 🔑 Metodo trasferibile: far **valutare a annotatori indipendenti la valenza morale** delle parole ("extremely wrong"→"extremely right"); quei punteggi spiegano l'effetto (design *rate-then-predict*). |
| **Do the Right Thing** (Capraro & Rand) | 2018 | SSRN `2965067` | Seminale: è l'**etichetta morale**, non l'allocazione, a predire la cooperazione. Trattare il frame morale come variabile operativa. |
| **Increasing… behaviour with simple moral nudges** (Capraro et al.) | 2019 | [arXiv 1711.05492](https://arxiv.org/abs/1711.05492) · Sci. Reports | Distingue appello a **morale personale** vs **norma sociale** — utile per annotare il tipo di appello nelle omelie. |
| **From Outcome-Based to Language-Based Preferences** (Capraro, Halpern, Perc) | 2022 | [arXiv 2206.07300](https://arxiv.org/abs/2206.07300) · J. Econ. Literature 2024 | Sintesi teorica del paradigma: il **linguaggio** è un driver misurabile, distinto dagli esiti. |
| **Human behaviour through a LENS** (Capraro) | 2024 | [arXiv 2403.15293](https://arxiv.org/abs/2403.15293) · Curr. Opinion Psych. | 🔑 Modello **LENS**: Linguistic content → Emotions + Norms → Strategy. Fornisce **dimensioni di annotazione** (emozione evocata, norma invocata). |
| **Language-based game theory in the age of AI** (Capraro et al.) | 2024 | [arXiv 2403.08944](https://arxiv.org/abs/2403.08944) · J. R. Soc. Interface | 🔑 Propone la **sentiment analysis** come strumento centrale per quantificare il carico emotivo/normativo del testo oltre il contenuto letterale. |
| **Assessing LLMs' ability to predict prosocial behavior** (Capraro et al.) | 2023/25 | [arXiv 2307.12776](https://arxiv.org/abs/2307.12776) · Sci. Reports 2025 | Solo GPT-4 riproduce i pattern umani, ma con **optimism bias**. → cautela nell'usare LLM come annotatori morali. |
| **Impact of generative AI on inequalities and policy** (Capraro, …, Acemoglu) | 2024 | [arXiv 2401.05377](https://arxiv.org/abs/2401.05377) · PNAS Nexus | L'AI generativa produce disinformazione più convincente degli umani; pilastro società/policy. |

**Come integrarlo nella pipeline (Fase 2/3):**
1. Costruire un **lessico morale/affettivo** dei termini valoriali del corpus e
   assegnarne la valenza (design *rate-then-predict* di Capraro & Vanzo).
2. **Sentiment analysis** per quantificare carico emotivo/normativo dei passi.
3. Annotare le **3 dimensioni LENS** (frame linguistico, emozione, norma).
4. Tracciare lo **shift diacronico** dei frame morali (morale personale vs
   norma sociale) tra Papi e nel tempo.
5. LLM come annotatori **solo con validazione umana** (optimism bias misurato).

> ⚠️ Caveat: i metodi di Capraro sono validati su giochi economici con
> etichette d'azione brevi; il trasferimento a discorsi lunghi e retorici
> (omelie) è ragionevole ma **non ancora testato**.

---

## 6. Raccomandazioni operative (workflow a 3 fasi)

**Fase 1 — Abbiamo i testi.** ✅ Corpus markdown con frontmatter
(papa/tipologia/data/url/parole). Base solida.

**Fase 2 — Arricchimento (database di analisi).** Per ogni documento
aggiungere:
- **Topic + keywords** → BERTopic (sentence-transformers multilingue) + c-TF-IDF
- **Entità** → NER (persone, luoghi, organizzazioni, concetti teologici)
- **Sentiment/tono e frame morali** → metriche emotive/morali (vedi anche il
  filone *moral outrage* in [arXiv 2409.08829](https://arxiv.org/pdf/2409.08829))
- **Embeddings** → vettori in un vector store per RAG e similarità
- **Metriche di stile** → diversità lessicale (LogTTR), leggibilità,
  regolarità (compressione)
- *(Opzionale)* **labeling/sintesi LLM** dei topic — **sotto validazione umana**

Formato consigliato: **frontmatter esteso** per la leggibilità +
**SQLite/Parquet** per le query aggregate + **indice vettoriale** affiancato.

**Fase 3 — Analisi.**
- **Trend temporali**: dynamic topic modeling + change-point (stile
  *Narrative Shift Detection* / DTECT) per individuare svolte narrative
- **Keyness / frequenze**: confronto tra Papi e nel tempo (TF-IDF, log-likelihood)
- **Evoluzione di concetti**: traiettoria di temi (pace, migranti, ambiente,
  misericordia) per anno e pontificato
- **Q&A / RAG**: interrogazione in linguaggio naturale del corpus
- **Confronto comparativo** tra pontificati, con citazioni puntuali (via `url`)

**Principio guida (dal filone Quattrociocchi):** statistica classica come
**baseline**, LLM per **interpretazione/etichettatura** ma **mai come giudice
autonomo affidabile** → validare sempre su gold set umano.

---

## 7. Caveat principali

- **Dominio diverso**: gran parte delle fonti riguarda social/news (X, Reddit).
  Il corpus papale è curato, medio-lungo, multilingue, **senza grafo di
  interazioni** → le tecniche di rete (echo chamber) vanno reinterpretate come
  analisi di contenuto. Metriche come tossicità/polarizzazione sono poco
  pertinenti; meglio **shift tematici, frame morali, frequenza di concetti**.
- **Time-sensitivity**: campo in rapida evoluzione; diverse fonti sono preprint
  2025-2026.
- **NTM ≠ sempre meglio**: il vantaggio è scalabilità, non coerenza; per un
  corpus medio LDA resta interpretabile.

## 8. Domande aperte / prossimi passi
1. Ricerca mirata sui lavori di **Valerio Capraro** (non coperti).
2. Quali **sentence-transformers multilingue** rendono meglio su testi
   religiosi/dottrinali in italiano (es. `paraphrase-multilingual-mpnet`,
   `LaBSE`, `multilingual-e5`)?
3. Quali **metriche di narrazione** sono significative per testi dottrinali
   (al posto di polarizzazione/tossicità)?
4. Come **validare l'LLM-as-annotator** su questo corpus (gold set, accordo
   inter-annotatore, controllo dell'effetto "epistemia")?

---

## Lista paper da scaricare (in questa cartella)

Scaricati come PDF (gitignorati, vedi `.gitignore`):

1. `2502.04426` — Decoding AI Judgment / The simulation of judgment in LLMs
2. `2507.00657` — Generative Exaggeration in LLM Social Agents
3. `2602.18152` — The Statistical Signature of LLMs
4. `2004.09603` — The echo chamber effect on social media
5. `2203.05794` — BERTopic
6. `2506.20269` — Narrative Shift Detection (DTM + LLM)
7. `2401.15351` — Survey on Neural Topic Models
8. `2507.07910` — DTECT
9. `2412.05579` — LLMs-as-Judges: A Comprehensive Survey
10. `2305.03514` — Can LLMs Transform Computational Social Science?
11. `2312.10997` — Retrieval-Augmented Generation: A Survey

**Valerio Capraro (frame morali / valori nel linguaggio):**

12. `2206.07300` — From Outcome-Based to Language-Based Preferences
13. `1901.02314` — The power of moral words (rate-then-predict)
14. `1711.05492` — Increasing behaviour with simple moral nudges
15. `2403.15293` — Human behaviour through a LENS
16. `2403.08944` — Language-based game theory in the age of AI (sentiment analysis)
17. `2307.12776` — Assessing LLMs' ability to predict prosocial behavior
18. `2401.05377` — Impact of generative AI on inequalities and policy (PNAS Nexus)
