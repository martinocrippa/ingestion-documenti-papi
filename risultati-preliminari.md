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

**Come si supera (prossimo step).** Con gli **embedding semantici** ogni
documento diventa un vettore che cattura il *significato*, non le parole
esatte: "casa comune", "madre terra" e "ambiente" finiscono vicini nello
spazio vettoriale. Così, invece di cercare stringhe, si misura la vicinanza
concettuale e si lasciano **emergere i temi dai dati** (topic modeling
moderno, clustering, RAG). È il lavoro dei repository a valle:
**vectordatabase-documenti-papi** (embeddings, ricerca semantica) e
**textmining-documenti-papi** (analisi e viste aggregate).
