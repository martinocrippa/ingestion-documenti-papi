#!/usr/bin/env Rscript
# TextMiningPapa - scarica i documenti dei Papi dal sito vaticano come
# file markdown (dati raw). Versione R, monofile, equivalente a papi.py.
#
# Due verita' del sito: l'header HTTP mente sull'encoding (il sito e' UTF-8);
# i Papi recenti e vecchi usano due schemi di URL per la data.
#
# Uso:  Rscript ImportPapaDocument.r                 # scarica tutto in data/
#       source("ImportPapaDocument.r"); scarica("francesco", "angelus", 2025)
#
# Nota: non testato (R non disponibile in fase di sviluppo). La versione di
# riferimento e' papi.py.

library(rvest)

BASE <- "https://www.vatican.va"

# chiave (= cartella) -> c(slug sul sito, nome leggibile)
PAPI <- list(
  "francesco"         = c("francesco",    "Papa Francesco"),
  "leone-xiv"         = c("leo-xiv",       "Papa Leone XIV"),
  "benedetto-xvi"     = c("benedict-xvi",  "Papa Benedetto XVI"),
  "giovanni-paolo-ii" = c("john-paul-ii",  "Papa Giovanni Paolo II")
)
TIPOLOGIE <- c("angelus", "audiences", "homilies", "speeches",
               "messages", "letters", "cotidie", "travels")

.get <- function(url) {
  pagina <- tryCatch(read_html(url), error = function(e) NULL)
  Sys.sleep(0.3)                       # gentile col server
  pagina
}

.data <- function(url) {               # data dal nome file, entrambi gli schemi
  nome <- basename(url)
  for (b in regmatches(nome, gregexpr("[0-9]{8}", nome))[[1]]) {
    d <- as.Date(b, "%Y%m%d")
    if (!is.na(d) && format(d, "%Y") >= "1900") return(format(d, "%Y-%m-%d"))
  }
  ""
}

.anno <- function(url) {
  iso <- .data(url)
  if (nzchar(iso)) return(as.integer(substr(iso, 1, 4)))
  m <- regmatches(url, regexec("/([0-9]{4})(?:\\.index|/)", url))[[1]]
  if (length(m) >= 2) as.integer(m[2]) else NA_integer_
}

trova_documenti <- function(slug, tipo, anni = NULL) {
  radice <- sprintf("%s/content/%s/it/%s", BASE, slug, tipo)
  coda <- paste0(radice, ".index.html")
  visti <- character(0); docs <- character(0)
  while (length(coda) > 0 && length(visti) < 500) {
    url <- coda[1]; coda <- coda[-1]
    if (url %in% visti) next
    visti <- c(visti, url)
    sp <- .get(url); if (is.null(sp)) next
    href <- html_attr(html_elements(sp, "a"), "href")
    href <- href[!is.na(href)]
    link <- ifelse(startsWith(href, "http"), href, paste0(BASE, href))
    link <- link[grepl(sprintf("/content/%s/it/", slug), link) &
                   grepl(sprintf("/%s[./]", tipo), link)]
    doc <- link[grepl("/documents/", link) & grepl("\\.html$", link)]
    if (!is.null(anni)) doc <- doc[vapply(doc, .anno, 1L) %in% anni]
    docs <- union(docs, doc)
    idx <- setdiff(link[grepl("\\.index\\.html$", link)], visti)
    if (!is.null(anni)) {
      a <- vapply(idx, .anno, 1L)
      idx <- idx[is.na(a) | a %in% anni]
    }
    coda <- union(coda, idx)
  }
  sort(docs)
}

.corpo <- function(sp) {               # testo da div.testo (corpo pulito)
  cont <- html_element(sp, "div.testo")
  if (inherits(cont, "xml_missing")) cont <- html_element(sp, "div.documento")
  if (inherits(cont, "xml_missing")) return("")
  par <- html_text2(html_elements(cont, "p"))
  rumore <- "^(\\[?\\s*[Mm]ultimedia|_{3,}|Copyright)"
  par <- par[nzchar(par) & !grepl(rumore, par)]
  paste(par, collapse = "\n\n")
}

.markdown <- function(url, nome, tipo, sp) {
  titolo <- html_text2(html_element(sp, "title"))
  corpo <- .corpo(sp)
  q <- function(s) paste0('"', gsub('"', '\\\\"', s), '"')
  parole <- lengths(regmatches(corpo, gregexpr("\\w+", corpo)))
  testo <- paste(c(
    "---",
    paste("papa:", q(nome)),
    paste("tipologia:", tipo),
    paste("data:", .data(url)),
    paste("titolo:", q(titolo)),
    paste("url:", url),
    paste("parole:", parole),
    "---", "",
    paste("#", titolo), "",
    corpo, ""
  ), collapse = "\n")
  list(testo = testo, ok = nzchar(trimws(corpo)))
}

scarica <- function(papa, tipo, anni = NULL, out = "data", max_n = NULL) {
  slug <- PAPI[[papa]][1]; nome <- PAPI[[papa]][2]
  urls <- trova_documenti(slug, tipo, anni)
  if (!is.null(max_n)) urls <- head(urls, max_n)
  cartella <- file.path(out, papa, tipo)
  n <- 0
  for (url in urls) {
    f <- file.path(cartella, sub("\\.html$", ".md", basename(url)))
    if (file.exists(f)) next           # incrementale: non riscarico
    sp <- .get(url); if (is.null(sp)) next
    md <- .markdown(url, nome, tipo, sp)
    if (!md$ok) next
    dir.create(cartella, recursive = TRUE, showWarnings = FALSE)
    writeLines(md$testo, f, useBytes = TRUE)
    n <- n + 1
  }
  message(sprintf("[%s/%s] %d nuovi, %d totali online",
                  papa, tipo, n, length(urls)))
  n
}

scarica_tutto <- function(papi = names(PAPI), tipologie = TIPOLOGIE,
                          anni = NULL, out = "data", max_n = NULL) {
  tot <- 0
  for (p in papi) for (t in tipologie) {
    tot <- tot + scarica(p, t, anni, out, max_n)
  }
  message(sprintf("Totale nuovi documenti: %d", tot))
  invisible(tot)
}

if (sys.nframe() == 0) scarica_tutto()
