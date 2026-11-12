# Project work – Analisi dei dati per una startup digitale di servizi on-demand

Prototipo interamente in **Python** (+ SQL su SQLite): dati sintetici → ETL → data warehouse a stella → SQL → dashboard.

## Strumenti
Python 3 · VS Code · `sqlite3` (incluso in Python) · `pandas` · `streamlit`

## Esecuzione (circa 2 minuti, da terminale di VS Code)
**nota** tutti i backtick contengono strumenti spiegati nella relazione
**NOTA ESECUTIVA**  se il comando `python` non va in terminale sostituirlo con `py`
```bash
python -m venv .venv                 # ambiente virtuale (una volta sola)
.venv\Scripts\activate               # Windows   (su Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt      # installa pandas e streamlit
python generate_data.py              # 1. genera i CSV in data/ (seed fisso = 42)
python etl.py                        # 2. pulisce e carica warehouse.db
python verifica.py                   # 3. confronta CSV e data warehouse
streamlit run dashboard.py           # 4. apre la dashboard nel browser

```


Per pratica strumenti: `python esempi_base.py`.

## Struttura
| File | Contenuto |
|---|---|
| `generate_data.py` | generatore di dati sintetici (300–600 record per tipologia) |
| `sql/schema.sql` | schema a stella (1 tabella dei fatti, 4 dimensioni) |
| `etl.py` | Extract – Transform – Load, con controlli di qualità |
| `sql/queries.sql` | interrogazioni per gli indicatori |
| `dashboard.py` | dashboard con filtri per periodo, zona, categoria |
| `verifica.py` | riconciliazione tra CSV e data warehouse |
| `esempi_base.py` | esempi minimi di pandas e sqlite3 |

## Parametri
Seed 42 · periodo 01/07/2025–31/12/2025 · 320 clienti, 300 fornitori, 300 operatori, 600 richieste.

## Definizioni degli indicatori
- **Richiesta gestita**: non annullata.
- **Tempo medio**: media di `tempo_erogazione_min` sulle richieste gestite.
- **Clienti che tornano**: clienti con ≥ 2 richieste gestite sul totale dei clienti con ≥ 1.
- **Zona**: zona del cliente.

dati privi di informazioni personali.
