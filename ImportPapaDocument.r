#' Scraping dei documenti dei Papi dal sito vaticano (versione R)
#'
#' Versione semplificata e aggiornata al sito attuale
#' (https://www.vatican.va). Per la versione consigliata e testata vedi
#' lo script Python `scrape_papa.py`.
#'
#' Note rispetto all'originale storico:
#'   - dominio aggiornato da w2.vatican.va a www.vatican.va;
#'   - il corpo del testo si estrae dal contenitore `div.testo`
#'     (niente piu' slice fisso per riga);
#'   - la vecchia logica "multipagina" basata sugli <span> non esiste
#'     piu': gli indici grandi si sviluppano in sotto-indici, qui
#'     raccolti con una visita ricorsiva;
#'   - gestiti entrambi gli schemi di URL dei documenti (vecchio/nuovo).
#'
#' @param slug_papa  Char, segmento URL del Papa (es. "francesco",
#'   "leo-xiv", "benedict-xvi", "john-paul-ii").
#' @param nome_papa  Char, nome leggibile (es. "Papa Francesco").
#' @param tipologie  Vettore di tipologie (es. c("angelus", "homilies")).
#' @param anni       Vettore di anni a cui limitarsi (NULL = tutti).
#' @param delay      Numerico, pausa in secondi fra le richieste HTTP.
#' @return Un tibble con: url, papa, tipologia, titolo, data, testo,
#'   n_parole.
#' @examples
#' df <- ImportPapaDocument("francesco", "Papa Francesco",
#'                          tipologie = "angelus", anni = 2025)

library(rvest)
library(dplyr)
library(stringr)
library(purrr)

BASE_URL <- "https://www.vatican.va"


# --- date: estrae YYYYMMDD dal nome file, entrambi gli schemi URL -------- #
.estrai_data <- function(url) {
  nome <- basename(url)
  for (blocco in str_extract_all(nome, "\\d{8}")[[1]]) {
    d <- as.Date(blocco, format = "%Y%m%d")
    if (!is.na(d) && format(d, "%Y") >= "1900") {
      return(format(d, "%Y-%m-%d"))
    }
  }
  NA_character_
}

.anno <- function(url) {
  iso <- .estrai_data(url)
  if (!is.na(iso)) return(as.integer(substr(iso, 1, 4)))
  m <- str_match(url, "/(\\d{4})(?:\\.index|/)")[, 2]
  if (!is.na(m)) as.integer(m) else NA_integer_
}


# --- discovery: visita ricorsiva degli indici di una tipologia ----------- #
.trova_documenti <- function(slug_papa, tipo, anni, delay) {
  radice <- sprintf("%s/content/%s/it/%s", BASE_URL, slug_papa, tipo)
  da_visitare <- paste0(radice, ".index.html")
  visti <- character(0)
  documenti <- character(0)

  while (length(da_visitare) > 0 && length(visti) < 500) {
    url <- da_visitare[1]
    da_visitare <- da_visitare[-1]
    if (url %in% visti) next
    visti <- c(visti, url)

    pagina <- tryCatch(read_html(url), error = function(e) NULL)
    if (is.null(pagina)) next
    Sys.sleep(delay)

    href <- html_attr(html_nodes(pagina, "a"), "href")
    href <- href[!is.na(href)]
    link <- ifelse(startsWith(href, "http"), href, paste0(BASE_URL, href))

    # solo link interni a questa tipologia
    link <- link[str_detect(link, sprintf("/content/%s/it/", slug_papa)) &
                   str_detect(link, sprintf("/%s[\\./]", tipo))]

    e_doc <- str_detect(link, "/documents/") & str_detect(link, "\\.html$")
    e_idx <- str_detect(link, "\\.index\\.html$")

    docs <- link[e_doc]
    if (!is.null(anni)) {
      docs <- docs[map_int(docs, .anno) %in% anni]  # NA escluso
    }
    documenti <- union(documenti, docs)

    nuovi <- setdiff(link[e_idx], visti)
    if (!is.null(anni)) {
      a_idx <- map_int(nuovi, .anno)
      nuovi <- nuovi[is.na(a_idx) | a_idx %in% anni]
    }
    da_visitare <- union(da_visitare, nuovi)
  }
  sort(documenti)
}


# --- corpo: estratto da div.testo (fallback div.documento) --------------- #
.estrai_corpo <- function(pagina) {
  cont <- html_node(pagina, "div.testo")
  if (inherits(cont, "xml_missing") || is.na(cont)) {
    cont <- html_node(pagina, "div.documento")
  }
  par <- html_text(html_nodes(cont, "p"), trim = TRUE)
  par <- par[par != "" &
               !str_detect(par, "^(\\[?\\s*[Mm]ultimedia|_{3,}|Copyright)")]
  paste(par, collapse = "\n\n")
}


#' @rdname ImportPapaDocument
#' @export
ImportPapaDocument <- function(slug_papa,
                               nome_papa,
                               tipologie = c("angelus"),
                               anni = NULL,
                               delay = 0.3) {
  righe <- list()

  for (tipo in tipologie) {
    message(sprintf("NOTE: ===> %s / %s", slug_papa, tipo))
    urls <- .trova_documenti(slug_papa, tipo, anni, delay)
    message(sprintf("NOTE: trovati %d documenti", length(urls)))

    for (url in urls) {
      pagina <- tryCatch(read_html(url), error = function(e) NULL)
      if (is.null(pagina)) next
      Sys.sleep(delay)

      testo <- .estrai_corpo(pagina)
      righe[[length(righe) + 1]] <- tibble(
        url        = url,
        papa       = nome_papa,
        tipologia  = tipo,
        titolo     = html_text(html_node(pagina, "title"), trim = TRUE),
        data       = .estrai_data(url),
        testo      = testo,
        n_parole   = str_count(testo, "\\w+")
      )
    }
  }

  bind_rows(righe)
}
