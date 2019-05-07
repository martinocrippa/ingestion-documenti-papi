#' Scrape of all italian Pope's Documents
#' 
#' @param link_pagina_papa Char, hyper link Vatican Papa website (default "http://w2.vatican.va/content/francesco/it.html").
#' @nome_papa Char, Pope's name (default "PAPA FRANCESCO").
#' @contenuti_interesse Vector, filter documents contents type (default c("angelus", "audiences", "cotidie", "homilies", "letters", "travels", "messages", "speeches ")).
#' @stringa_filtro_per_pulizia Char,  filter value to keep only documents hyperlink (default "/content/francesco/it/cotidie/").
#' @tipo_discorso Char,  html value for speech type (default "cotidie")
#' @scrivo_su_disco Char,  write tibble on disk (default "NO")
#' @return tb_contenuti Tibble with documents scraped.
#' @examples
#' ImportPapaDocument(link_pagina_papa = "http://w2.vatican.va/content/francesco/it.html",
#'                   nome_papa = "PAPA FRANCESCO",
#'                   contenuti_interesse = c("angelus", "audiences", "cotidie", "homilies", "letters", "travels", "messages", "speeches "),
#'                   stringa_filtro_per_pulizia = "/content/francesco/it/cotidie/", 
#'                   tipo_discorso = "cotidie",
#'                   scrivo_su_disco = "NO")
#'
#'

ImportPapaDocument <- function(link_pagina_papa,
                               nome_papa,
                               contenuti_interesse,
                               stringa_filtro_per_pulizia,
                               tipo_discorso,
                               scrivo_su_disco = "NO"
                               ){
 
  # libraries
  require(here)
  require(rvest)
  require(tidyverse)

 
  # ######################################### #
  # ESTRAZIONE LINK INDICI dei LINK DOCUMENTI #
  # ######################################### #
 
  # log
  message(paste0("NOTE: ===> ESTRAZIONE LINK INDICI dei LINK DOCUMENTI ", link_pagina_papa))
 
  # parsing pagina principale: crea una lista con xml dell'html
  lista_xml_pagina_principale <- read_html(paste0(link_pagina_papa))
 
  # estrazione nodi - solo oggetti a dove posso trovare i link alla trascrizione dei documenti
  lista_nodi_link <- html_nodes(lista_xml_pagina_principale, 'a')
 
  # estrazione attributo del riferimento html per link
  tb_link <- as.tibble(html_attr(lista_nodi_link, "href"))
 
  # pulizia link per utilizzo
  tb_link <- tb_link %>%
              # pulizia link
              filter(grepl("/content/", value)) %>%
              # creazione nuove variabili
              mutate(link = ifelse(substr(value,1, 4) == "http",
                                   value,
                                   paste0("http://w2.vatican.va", value)),
                     # estraggo tipologia contenuto
                     tipologia_contenuto = str_split(link, "/", simplify = T)[,7]) %>%
              # filtro solo contenuti di interesse
              filter(tipologia_contenuto %in% contenuti_interesse) %>%
              # remove duplicates
              unique() %>%
              select(-value)
 
 
  # ######################################### #
  # ESTRAZIONE LINK DOCUMENTI da LINK INDICI  #
  # ######################################### #
 
  # log
  message(paste0("NOTE: ===> ESTRAZIONE LINK DOCUMENTI da LINK INDICI per ", tipo_discorso))
 
  # estraggo solo link indici dei link ai documenti scelti dal parametro
  tb_link_in_analisi <- tb_link %>%
                        filter(tipologia_contenuto %in% c(paste0(tipo_discorso))) %>%
                        select(link) %>%
                        # remove duplicates
                        unique()
 
  # inizializzo lista con i tibble dei link
  lista_link_documenti <- list()
 
  # per ogni indice di ogni anno estraggo i link con i singoli angelus
  for(i in 1 : nrow(tb_link_in_analisi)) {
   
    # trasformo in un tibble estrazione dell'attributo HREF dal nodo "a"  -> che contengono i LINK dei documenti
    lista_link_documenti[[i]] <-  as.tibble(html_attr( html_nodes( read_html( paste0(tb_link_in_analisi[i,])), 'a'), "href"))
   
    # cerco oggetto che indica un indice multipagina
    ricerca_multipagine <- html_text(html_nodes( read_html( paste0(tb_link_in_analisi[i,])), 'span'), trim = TRUE)
   
    # verifico se indice multipagina
    if (identical(ricerca_multipagine, character(0))) {
     
      message( paste0("NOTE: indice in esame ", tb_link_in_analisi[i,], " non ha pagine multiple" ))
     
    } else {
     
      # considero il max dei numeri pagina
      max_pagina_indice <- max(ricerca_multipagine)
      message( paste0("NOTE: indice in esame ", tb_link_in_analisi[i,], " ha ", max_pagina_indice, " pagine multiple") )
     
      # inizializzo tibble con link risultanti da indici a pagine multiple
      link_da_indici_con_pagine_multiple <- as.tibble()
     
      # estraggo link da indice multipagina
      for (z in 2 : max_pagina_indice) {

        # log
        message( paste0("NOTE: pagina in analisi numero ", z))

        # costruisco link di pagina_ link indice ( - html) + iteratore ciclo + ".html"
        link_pagina_tmp <- paste0(substr(tb_link_in_analisi[i,], 0, nchar(tb_link_in_analisi[i,])-4 ), z, ".html")
       
        # estraggo da pagine multiple
        link_da_indici_con_pagine_multiple_temporaneo <-  as.tibble(html_attr(html_nodes(read_html(link_pagina_tmp), 'a'), "href"))

        # appendo risultato da pagine multiple
        link_da_indici_con_pagine_multiple <- link_da_indici_con_pagine_multiple_temporaneo %>%
                                              bind_rows(link_da_indici_con_pagine_multiple)

        }
     
      # appendo link pagine multiple a quelli risultanti dalla prima
      lista_link_documenti[[i]] <- lista_link_documenti[[i]] %>% bind_rows(link_da_indici_con_pagine_multiple)
     
      # pulizia tibble temporaneo
      rm(list = c("link_da_indici_con_pagine_multiple_temporaneo",
                  "link_da_indici_con_pagine_multiple",
                  "link_pagina_tmp"))
     
    }

    # puliza link per mantenere solo quelli relativi ai documenti
    lista_link_documenti[[i]] <- lista_link_documenti[[i]] %>%
                                 # pulizia link
                                 filter(grepl(stringa_filtro_per_pulizia, value) &
                                        !grepl("index", value)) %>%
                                  # creazione variabile LINK e correzione nel caso di spazi nell'URL
                                  # perchè vengano risolti - sostituisco con "%20"
                                  mutate(link = gsub(" ", "%20", paste0("http://w2.vatican.va", value))) %>%
                                  select(-value) %>%
                                  # remove duplicates
                                  unique()
   
  }
 
  # nomino elementi lista con anno (nome dell'indice)
  names(lista_link_documenti) <- gsub("\\.", " ", str_split(tb_link_in_analisi$link, "/", simplify = T)[,8])
 
 
  # ############################################ #
  # ESTRAZIONE CONTENUTI da LISTA LINK DOCUMENTI #
  # ############################################ #
 
  # log
  message(paste0("NOTE: ===> ESTRAZIONE CONTENUTI da LISTA LINK DOCUMENTI", tipo_discorso))
 
  # ciclo sui indici/anni
  tb_contenuti <- as.tibble()
 
  for (j in 1 : length(lista_link_documenti)) {

    # log message
    message(paste0("NOTE: ===> ESTRAZIONE CONTENUTI da indice ", j))
   
    # ciclo nei momenti dell'anno
    for(i in 1 : nrow(lista_link_documenti[[j]])) {

      # log message
      message(paste0("NOTE: ==> ESTRAZIONE CONTENUTI da doc ", i))
     
      # leggo da link html e estraggo solo i paragrafi (ove c'è contenuto)
      contenuto_temporaneo <- html_nodes(read_html(paste(lista_link_documenti[[j]][["link"]][[i]])), 'p')
     
      # estraggo contenuti e creo tibble --> diversifico per tipologia
      tb_contenuti_temporaneo <- tibble( link = paste(lista_link_documenti[[j]][["link"]][[i]]),
                                         nome_papa = paste0(nome_papa),
                                         tipologia = paste0(tipo_discorso),
                                         titolo = gsub(".html", "", str_split(link, "_", simplify = T)[,3]),
                                         data = as.Date(substr(str_split(link, "_", simplify = T)[,2],0,8), format = "%Y%m%d"),
                                         raw = str_replace_all(paste(html_text(contenuto_temporaneo), collapse =" "), "à", "a"),
                                         testo = paste(html_text(contenuto_temporaneo[8:(length(contenuto_temporaneo)-4)], trim = TRUE), collapse =" ")
      )
     
      # aggiungo informazioni
      tb_contenuti <- tb_contenuti %>% bind_rows(tb_contenuti_temporaneo)
      # pulizia 
      rm(list = c("tb_contenuti_temporaneo", "contenuto_temporaneo"))
     
    }
  }
 
  # aggiugno id al documento
  tb_contenuti <- tb_contenuti %>%
                  mutate(# creo codice documento aggiungendo 0 al numero di riga sino a 8 cifre
                        ID_document = paste0(tipologia, str_pad(row_number(), 8, pad = "0")),
                        # conto numero parole documento
                        number_words = str_count(testo,'\\w+'),
                        # verifico presenza parola
                        flg_migranti = ifelse(grepl("migranti|rifugiati", testo), 1, 0)
                        )
  # outputs
  return (c("tb_contenuti"))

  # write results on csv
  if (scrivo_su_disco == "YES"){
    write.csv(tb_contenuti_audiences, file = paste0(here(),"/_csv/TB_audiences_francesco.csv")) 
  }

 
}