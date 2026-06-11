# Setup dell'ambiente

Il progetto richiede **Python ≥ 3.9** (consigliato 3.12) e tre librerie:
`requests`, `beautifulsoup4`, `lxml`.

## Opzione A — conda (consigliata)

Crea l'ambiente dal file `environment.yml`:

```bash
conda env create -f setup/environment.yml
conda activate textminingpapa
```

Per aggiornarlo dopo una modifica al file:

```bash
conda env update -f setup/environment.yml --prune
```

Per rimuoverlo:

```bash
conda env remove -n textminingpapa
```

## Opzione B — venv + pip

```bash
python -m venv .venv
# Windows:        .venv\Scripts\activate
# Linux/macOS:    source .venv/bin/activate
pip install -r requirements.txt
```

## Verifica e uso

Con l'ambiente **attivo**, `python` è l'interprete Python 3 dell'ambiente:

```bash
python -c "import requests, bs4, lxml; print('ok')"   # verifica librerie
python test/smoke_test.py                              # test rapido
python papi.py                                         # download completo
python test/check_dati.py                              # check sui dati
```

Rilanciare `python papi.py` scarica solo i documenti nuovi (gli altri esistono
già su disco).

> Nota: usa `python` (non `python3`) dopo aver attivato l'ambiente conda/venv —
> al suo interno `python` punta sempre a Python 3. Gli script hanno comunque lo
> shebang `#!/usr/bin/env python3` per l'esecuzione diretta su Linux/macOS.
