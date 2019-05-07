# TextMiningPapa
web scraping documenti Papa e analisi

# ESEMPIO di CHIAMATA per Papa Francesco
```r
 ImportPapaDocument(link_pagina_papa = "http://w2.vatican.va/content/francesco/it.html",
                    nome_papa = "PAPA FRANCESCO",
                    contenuti_interesse = c("angelus", "audiences", "cotidie", "homilies", "letters", "travels", "messages", "speeches "),
                    stringa_filtro_per_pulizia = "/content/francesco/it/cotidie/", 
                    tipo_discorso = "cotidie",
                    scrivo_su_disco = "NO")
```

# CONCLUSIONI:
manca la gestione delle differenti tipologie di testi per estrarre il corpo correttamente, ho studiato, testato e già fatto analisi devo solo scrivere qualche riga di più (EX. gli angelus hanno il corpo da riga 7 della pagina per un tipo o dalla 6 per un altro, le udienze dalla 6..)

# EVOLUZIONE e PROSEGUI:
## 1. SVILUPPI
* test e adeguamento per gli altri PAPI, più o meno la struttura è la stessa
* possibilità di creare un unico documento
* utilizzo della famiglia di funzioni APPLY per evitare i cicli? forse no perchè non controlliamo le chiamate
* PIPE d'appertutto
* commenti iniziali dentro al codice per vignette

## 2. funzione pulizia testo con diverse fasi che letteratura propone nel text mining
* tokenizzazione
* eliminazione stop-word
* lemmizzazione
* utilizzo sinonimi
* stemmizzazione

## 3. funzione studio frequenze

## 4. funzione per estrazione ARGOMENTI/ TOPIC EXTRACTION/ TOPIC MODELING
* con LSA(latent semantic analysis basata su riduzione del piano SVD singular-value-decomposition le spiegava lovaglio in analisi dei dati), tecnica vecchia scuola (come implementata ad ora nella tecnologia SAS)
* con LDA(latent dirichlet allocation), tecnica anni '90 con statistica bayesiana (di cui non capisco una minchia) --> c'è un articolo in letteratura che mi dà una collega sull'applicazione ai twitter di TRUMP
* con NMF(non-negative matrix factorization), tecnica anni 2000 per cui si entrerebbe nel machine learning

## 5. SHINIY o PACKAGE
infilarlo dentro un applicazione SHINY

## 6. INTERESSE
chi potrebbe interessare? Giornalisti/Vaticanisti e Ricercatori di Storia contemporanea (ho trovato un paio di persone a cui chiedere), magari cmq approcio potrebbe essere interessante e utile in campo storico cazzo sò. Altrimenti magari si potrebbe pensare di pubblicare un articoletto --> questo punto al momento è tutta fantasia

## 7. Aggiungere script analisi e domande a cui rispondere
* di cosa parla ultimo Papa? solo migranti e immigrati?
* c'è continuità nella chiese negli ultimi tre Papi?
* etc..
