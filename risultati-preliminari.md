# Risultati preliminari

Primi numeri ottenuti con [`test/check_dati.py`](test/check_dati.py) sul
corpus scaricato (~25.000 documenti). **Sono un check, non un'analisi seria**:
match di parole chiave, presenza sì/no, niente contesto né sinonimi. I limiti
sono spiegati in fondo.

## Domanda di partenza

> *Papa Francesco parla solo di migranti? Ed è un po' comunista?*

## Metodo

Per ogni documento si controlla la presenza di alcune **radici di parola**
(case-insensitive). Un tema è "presente" se compare almeno una volta. Regole:

| tema | radici (basta una) |
|---|---|
| migranti | `migrant`, `rifugiat`, `profugh` |
| pace | `pace` (parola intera), `guerra`, `conflitt` |
| famiglia | `famigli` |
| ambiente | `ambient`, `creato`, `ecolog` |
| poveri | `pover`, `emarginat` |

## Volumi

| Papa | Documenti |
|---|---|
| Giovanni Paolo II | 15.368 |
| Francesco | 6.057 |
| Benedetto XVI | 3.001 |
| Leone XIV | 639 |

## Temi: % di documenti che li citano

| tema | GP2 | Benedetto | Francesco | Leone XIV |
|---|---|---|---|---|
| pace | 51% | 53% | 54% | 78% |
| famiglia | 55% | 55% | 52% | 51% |
| poveri | 30% | 31% | **42%** | 39% |
| ambiente | 32% | 33% | 26% | 30% |
| migranti | 5% | 5% | **12%** | 8% |

## Lift (% del Papa / media fra i Papi)

`> 1,00` = sopra la media dei quattro Papi; `< 1,00` = sotto.

| tema | media | GP2 | Benedetto | Francesco | Leone XIV |
|---|---|---|---|---|---|
| pace | 58,9% | 0,87 | 0,89 | 0,91 | **1,33** |
| famiglia | 53,1% | 1,03 | 1,04 | 0,97 | 0,96 |
| poveri | 35,5% | 0,83 | 0,89 | **1,19** | 1,09 |
| ambiente | 30,0% | 1,05 | 1,09 | 0,87 | 0,99 |
| migranti | 7,5% | 0,68 | 0,70 | **1,58** | 1,04 |

## Lettura

- **"Solo migranti?" → falso.** È il tema *meno* citato anche da Francesco
  (12%). I suoi temi principali, come per tutti, sono **pace** (54%) e
  **famiglia** (52%).
- **Una differenza però c'è.** Il lift mostra che Francesco si stacca dai
  predecessori proprio su **migranti** (1,58: +58% sulla media) e **poveri**
  (1,19). Giovanni Paolo II e Benedetto sono sotto la media su entrambi
  (~0,68 su migranti, ~0,83-0,89 su poveri).
- **"Un po' comunista?"** I numeri spiegano da dove nasce la fama (accento più
  marcato su poveri e migranti), ma resta un'enfasi *relativa*: in valore
  assoluto pace e famiglia dominano comunque, esattamente come per gli altri.
- **Leone XIV**: pace a lift 1,32, molto alta (campione piccolo, 639 doc).
- **Continuità**: famiglia, pace, ambiente sono stabili fra i pontificati.

## Limiti di queste analisi (e perché servono gli embedding)

Queste percentuali nascono da **parole chiave scelte a mano**: catturano solo
le formulazioni che abbiamo previsto, e mancano tutto ciò che dice la stessa
cosa con parole diverse.

**Esempio concreto.** Francesco parla di ambiente quasi sempre in chiave di
*"casa comune"*, *"sorella madre terra"*, *"custodia del creato"* (linguaggio
della *Laudato si'*), non con i termini tecnici `ambient`/`ecolog`. La regola
keyword **non coglie questo legame**: una frase come *"dobbiamo prenderci cura
della nostra casa comune"* parla chiaramente di ambiente, ma non contiene
nessuna delle radici cercate → il documento risulterebbe "non sul tema
ambiente". Risultato: il vero peso del tema ambientale in Francesco è
**sottostimato**.

Altri limiti dello stesso tipo:
- **Sinonimi/perifrasi** non catturati: "gli ultimi", "i più deboli", "chi
  fugge dalla guerra" non contano come poveri/migranti.
- **Nessun contesto né negazioni**: "non c'è pace" conta come "pace".
- **Temi imposti, non scoperti**: vediamo solo i 5 temi che abbiamo deciso noi.

## Aggiornamento (2026-06-12): cosa abbiamo provato e cosa abbiamo capito

Prima di costruire, abbiamo fatto un **esperimento** per verificare l'ipotesi
"gli embedding battono le parole chiave su *ambiente*" (script
[`prove/ambiente_semantico.py`](https://github.com/martinocrippa/vectordatabase-documenti-papi)
nel repo del vector database). Tracciamo l'esito perché ha cambiato il piano.

- **Fatto.** Campione di documenti, embedding multilingue (provati MiniLM e
  `multilingual-e5-base`), per ogni documento la similarità massima col concetto
  "ambiente/creato/casa comune", confronto con la regex.
- **Problema 1 — la soglia non funziona.** Le similarità coseno **non sono
  calibrate**: non c'è un cutoff "naturale" che separi on-topic/off-topic, e con
  e5 stanno tutte schiacciate in alto (0,78–0,85). Classificare i documenti con
  una soglia fissa è statisticamente fragile: il numero di "positivi" dipende
  dalla soglia, non dai dati.
- **Problema 2 — a livello di documento il recall keyword è già buono.** Un
  discorso lungo che parla d'ambiente, *da qualche parte* usa anche
  `ambient`/`creato`/`ecolog`: quindi la regex **lo prende lo stesso**. Il
  vantaggio del semantico **non è** sul recall per-documento, come avevamo
  scritto sopra: quel limite è reale ma **meno grave del previsto**.

**Dove il semantico vince davvero (la correzione di rotta):**
1. **Precisione.** La regex conta "Dio ha *creato*" o l'*ambiente* inteso come
   stanza: falsi positivi che il significato scarta.
2. **Retrieval di passaggi.** Trovare *la frase* "prenderci cura della casa
   comune", non "il documento" — è il livello giusto per le citazioni (RAG).
3. **Temi emergenti.** Far **emergere** i temi dai dati (clustering/topic
   modeling) invece di imporne 5 scelti a mano.

**Come lo realizziamo (prossimo step): ricerca ibrida + reranking.** Non
embedding *contro* parole chiave, ma **insieme**, alla MongoDB Atlas:
- **keyword** con **BM25** (forte sui termini esatti e i nomi propri),
- **vettori** per la vicinanza di significato,
- fusione dei due ranking con **Reciprocal Rank Fusion (RRF)**,
- **reranking** finale dei primi risultati con un cross-encoder.

Così precisione e recall si coprono a vicenda, senza dover scegliere una soglia.
È il lavoro dei repository a valle: **vectordatabase-documenti-papi** (ricerca
ibrida e retrieval) e **textmining-documenti-papi** (analisi e viste aggregate).
