# Analisi dei dati per una startup digitale di servizi on-demand

Prototipo di **business intelligence** realizzato in Python e SQL: dati sintetici → pulizia e caricamento (ETL) → data warehouse a stella (SQLite) → indicatori in SQL → dashboard interattiva.

Project work del corso di laurea in *Informatica per le aziende digitali* (L-31), Università Telematica Pegaso. Tema 1: *La digitalizzazione dell'impresa*. Traccia 21: *Progettare l'analisi dei dati per una startup digitale di servizi on-demand*.

- **Autore:** [PiccirilliMariachiara] · **Matricola:** [0312400560]



---

## punti principali

**startup ideata** Una piattaforma digitale che dopo aver protocollato le richieste cliente su servizi a domicilio in settori quali  pulizie, riparazioni, consegne, assistenza , giardinaggio, le affida a un **fornitore** partner e a un **operatore** che la esegue; la richiesta si chiude come *completata*, *in ritardo* o *annullata*. Per le richieste eseguite vengono inscritti importo pagato e il tempo relativo all' erogazione in min.

**clue richiesta** I dati raccolti da quattro sistemi csv non comunicanti , fondatore non ha una visione complessiva.

| Fonte (sistema simulato) | Dati raccolti | File |
|---|---|---|
| Piattaforma di gestione delle richieste | identificativo, cliente, fornitore, operatore, data e ora, importo, tempo di erogazione, stato | `data/richieste.csv` |
| App dei clienti | identificativo, zona, data di iscrizione | `data/clienti.csv` |
| Sistema di gestione degli operatori | identificativo, zona, tipo di attività (a domicilio, da remoto, in sede) | `data/operatori.csv` |
| Archivio dei fornitori partner | identificativo, nome, categoria di servizio, zona | `data/fornitori.csv` |

**soluzione.** Un prototipo racchiude in un unico archivio i dati,  a fini di analisi, calcolando gli indicatori principali inseriti in una dashboard con filtri per **periodo, zona e categoria di servizio**.

## Come funziona

```
generate_data.py  ->  data/*.csv  ->  etl.py  ->  warehouse.db  ->  sql/queries.sql  ->  dashboard.py
 (dati sintetici)    (4 fonti)      (pulizia e    (data warehouse     (indicatori)        (grafici e filtri)
                                     caricamento)   a stella)
                          \                              /
                           ---------- verifica.py -------   (confronto indipendente: OK / ERRORE)
```

Lo schema SQL (`sql/schema.sql`) viene eseguito da `etl.py` per creare le tabelle del warehouse.

## Contenuti

| File o cartella | A cosa serve |
|---|---|
| `generate_data.py` | genera i quattro file CSV con dati sintetici (seme fisso) |
| `etl.py` | legge i CSV, li pulisce, ne controlla la qualità e li carica in `warehouse.db` |
| `sql/schema.sql` | definisce lo schema a stella con tabella dei fatti centrale e 4 dimensioni connesse |
| `sql/queries.sql` | le sette interrogazioni SQL che calcolano gli indicatori |
| `dashboard.py` | la dashboard interattiva (Streamlit) |
| `verifica.py` | confronta i numeri del warehouse con quelli ricalcolati dai CSV |
| `esempi_base.py` | esercizi minimi su pandas e sqlite3, con i dati del progetto |
| `mostra_schema.py` | stampa tabelle, colonne, collegamenti e un esempio (richiesta R00110) |
| `mostra_stella.py` | disegna in testo la stella leggendo le chiavi del database |
| `warehouse.db` | il data warehouse (SQLite): già pronto, si può ricostruire con `etl.py` |
| `data/` | i CSV generati e `richieste_scartate.csv` (righe escluse dall'ETL) |
| `docs/` (registro dell'ultima esecuzione dell'ETL) || 
| `requirements.txt` | le librerie necessarie: `pandas` e `streamlit` |


**Ordine per la lettura** `generate_data.py` → `sql/schema.sql` → `etl.py` → `sql/queries.sql` → `dashboard.py` → `verifica.py`.

## Installazione 

**Che cosa serve:** Python 3.12 o successivo. Il progetto è stato testato con Python 3.12, pandas 3.0 e NumPy 2.4.

1. **aprire la cartella `project_work` in VS Code** 
2. **Apri il terminale** nella cartella (*Terminale → Nuovo terminale*) e controlla di essere nel posto giusto: `dir` deve mostrare `etl.py` e `warehouse.db`.
3. **Crea l'ambiente virtuale**  `python -m venv .venv`
4. **Attivalo:** `.venv\Scripts\activate` (Windows) oppure `source .venv/bin/activate` (Mac). Controllare se all'inizio della riga compare `(.venv)`.
5. **Installa le librerie:** `pip install -r requirements.txt`

ATTENZIONE Se `python` non viene riconosciuto, usa `py` al posto di `python` (per esempio `py -m pip install -r requirements.txt`).

## 5. Esecuzione: i quattro comandi

Sempre dalla cartella del progetto, nell'ordine:

| # | Comando | Cosa fa | Cosa vedere |
|---|---|---|---|
| 1 | `python generate_data.py` | genera i CSV (seme 42) | `clienti.csv: 320 righe`, `fornitori.csv: 300`, `operatori.csv: 300`, `richieste.csv: 608` |
| 2 | `python etl.py` | pulisce i dati e crea `warehouse.db` | l'ultima riga: `[LOAD] database creato: warehouse.db \| fatti=596 …` |
| 3 | `python verifica.py` | controlla il warehouse | tre righe con `-> OK` |
| 4 | `streamlit run dashboard.py` | avvia la dashboard | si apre il browser su `http://localhost:8501` |

Per fermare la dashboard: `Ctrl+C` nel terminale.
 I comandi 1 e 2 si possono saltare se vuoi solo guardare i risultati, perché `warehouse.db` è già incluso. Grazie al seme fisso, rilanciandoli si ottengono dati identici.

## 6. schema a stella

- **Come codice:** apri `sql/schema.sql`. La tabella dei fatti `fact_richieste` è alle righe 45-56, e le quattro righe con `REFERENCES` sono i collegamenti alle dimensioni.
- **Dal database**, in testo: `python mostra_stella.py`
- **Tabelle, colonne ed esempio completo** (richiesta R00110 con cliente, fornitore, operatore e momento): `python mostra_schema.py`


Questi script usano solo `sqlite3`.

## 7. La dashboard

Avvio: `streamlit run dashboard.py`. Nella barra laterale visiono **tre filtri**:

| Filtro | Cosa seleziona |
|---|---|
| Periodo | intervallo di date (dal 1° luglio al 31 dicembre 2025) |
| Zona del cliente | una o più tra Nord, Centro, Sud, Est, Ovest |
| Categoria di servizio | una o più tra le cinque categorie |

**Sei indicatori:** richieste totali, richieste gestite, incassi, tempo medio (minuti), clienti attivi, clienti che tornano.

**Quattro grafici:** andamento mensile delle richieste, primi cinque fornitori per incassi, richieste per zona, richieste per categoria. In più, una sezione espandibile con le richieste per fascia oraria.

Ogni volta che cambi un filtro la pagina ricalcola tutto sulle sole richieste selezionate. *Esempio:* con agosto, zona Centro e categoria Riparazioni compaiono 8 richieste per 736,68 €; scegliendo la zona Nord compaiono 5 richieste per 389,26 €.

## 8. Definizione degli indicatori

| Indicatore | Definizione |
|---|---|
| Richieste totali | tutte le richieste ricevute |
| Richiesta gestita | richiesta non annullata |
| Incassi | somma degli importi (le annullate valgono 0) |
| Tempo medio di erogazione | media del tempo sulle sole richieste gestite |
| Cliente attivo | cliente con almeno una richiesta gestita nel periodo |
| Cliente che torna | cliente attivo con almeno due richieste gestite |
| Zona | **la zona del cliente** |

Medie e percentuali non si sommano: si ricalcolano sempre dai totali. Il tasso di clienti che tornano dipende dal periodo scelto.

## 9. dati e parametri

| Parametro | Valore |
|---|---|
| Seme del generatore casuale | 42 |
| Periodo simulato | 1° luglio – 31 dicembre 2025 |
| Volumi | 320 clienti, 300 fornitori, 300 operatori, 600 richieste |
| Zone | Nord, Centro, Sud, Est, Ovest |
| Categorie | Pulizie, Riparazioni, Consegne, Assistenza IT, Giardinaggio |
| Stato delle richieste | 78% completate, 12% in ritardo, 10% annullate |

Importi e tempi seguono una distribuzione log-normale per categoria; giorni e ore hanno pesi diversi (più richieste il venerdì, meno la domenica, picchi alle 9-11 e alle 17-19) e la domanda cresce nel periodo; clienti e fornitori hanno popolarità «a coda lunga» (pochi molto attivi, molti poco attivi). Sono **ipotesi di progetto**, non dati osservati.

**Errori inseriti di proposito** (per mostrare il lavoro dell'ETL):

| Errore | Quanti | Un caso nel file |
|---|---|---|
| zone scritte male | 25 | il cliente C0005 ha la zona «SUD » |
| importi mancanti | 10 | R00009 non ha l'importo |
| clienti inesistenti | 4 | R00022, R00389, R00534, R00595 puntano al cliente C9999 |
| righe duplicate | 8 | R00011 compare due volte |
| stati scritti in modo diverso | 12 | R00021 ha stato «Completata» |

## 10. schema a stella

Al centro la **tabella dei fatti** (una riga per richiesta), intorno quattro **dimensioni**.

| Tabella | Contenuto | Righe |
|---|---|---|
| `fact_richieste` | importo, tempo di erogazione, stato, `is_annullata`, `is_in_ritardo` e quattro chiavi esterne | 596 |
| `dim_cliente` | id, zona, data di iscrizione | 320 |
| `dim_fornitore` | id, nome, categoria di servizio, zona | 300 |
| `dim_operatore` | id, zona, tipo di attività | 300 |
| `dim_tempo` | una riga per ogni ora del periodo: data, anno, mese, giorno della settimana, ora, fascia oraria, fine settimana | 4.416 |

**Granularità:** una riga dei fatti è una richiesta. Le chiavi (`cliente_key`, …) sono numeri interni al warehouse, indipendenti dai codici dei sistemi di origine (C0117 diventa 117). Le dimensioni sovrascrivono i valori che cambiano: lo storico delle modifiche non è conservato.

## 11. ETL

`etl.py` esegue tre fasi: **Extract** (legge i quattro CSV), **Transform** (pulisce e controlla), **Load** (crea le tabelle con `schema.sql` e le riempie, prima le dimensioni e poi i fatti).

| Regola | Esempio | Righe |
|---|---|---|
| uniformare zone e stati | «SUD » → Sud; «Completata» → completata | 25 e 12 |
| togliere i duplicati | R00011 compare due volte e ne resta una | 8 |
| scartare le richieste con cliente, fornitore o operatore inesistente | R00022, R00389, R00534, R00595 → `data/richieste_scartate.csv` | 4 |
| sostituire gli importi mancanti con la mediana della categoria | R00009 (pulizie): 51,50 € | 10 |

Prima del caricamento (`assert`) verificano che gli identificativi siano unici, gli importi non negativi, le chiavi esistenti e che ogni richiesta non annullata abbia un tempo. Il database viene ricostruito da zero a ogni esecuzione. Righe: **608 lette → 600 dopo i duplicati → 596 dopo le richieste orfane**.

*Nota:* mediana 

## 12. SQL

| Query | Domanda | Dimensione collegata |
|---|---|---|
| Q1 | indicatori di sintesi (richieste, incassi, tempo medio, ritardi) | nessuna |
| Q2 | clienti attivi e quota di clienti che tornano | nessuna |
| Q3 | andamento mensile di richieste e incassi | `dim_tempo` |
| Q4 | primi cinque fornitori per incassi | `dim_fornitore` |
| Q5 | richieste, incassi e tempo medio per zona del cliente | `dim_cliente` |
| Q6 | richieste, incassi, tempo medio e annullamenti per categoria | `dim_fornitore` |
| Q7 | richieste per giorno della settimana e fascia oraria | `dim_tempo` |

Ogni query parte dalla tabella dei fatti, la collega con un `JOIN` alla dimensione che serve, raggruppa con `GROUP BY` e riassume con `COUNT`, `SUM` o `AVG`. Per eseguirle puoi aprire `sql/queries.sql` o usare `sqlite3` da Python, come in `esempi_base.py`.

## 13. Verifica 

`python verifica.py` ricalcola, direttamente dai CSV e con le stesse regole di pulizia, tre valori e li confronta con quelli del warehouse:

```
righe nei fatti        CSV=596  DW=596  -> OK
richieste gestite      CSV=547  DW=547  -> OK
tempo medio (min)      CSV=120.16  DW=120.16  -> OK
```

Gli incassi non vengono confrontati, perché nel warehouse sono stati imputati dieci importi mancanti. Il controllo lavora sui totali: due errori di segno opposto che si compensano non verrebbero rilevati.

## 14. Risultati

| Indicatore | Valore |
|---|---|
| Richieste totali / gestite / annullate | 596 / 547 / 49 (8,2%) |
| Incassi totali | 35.796,54 € |
| Importo medio per richiesta gestita | 65,4 € |
| Tempo medio di erogazione | 120,2 minuti |
| Richieste gestite in ritardo | 13,0% |
| Clienti attivi | 173 |
| Clienti che tornano | 81 (46,8%) |

Poiché i dati sono inventati, questi risultati mostrano che lo strumento fa emergere i fenomeni, non che il mercato si comporti così.

## 15. Sicurezza e privacy

- **Riservatezza:** dati sintetici non personali; 
- **Integrità:** chiavi primarie ed esterne, controlli `assert`, verifica indipendente e righe scartate conservate.
- **Disponibilità:** il database si ricostruisce con gli script dai file CSV.
- **Iniezione di codice SQL:** le query della dashboard usano parametri (`?`).
- La dashboard gira in locale e **senza autenticazione**.

## 16. Limiti e implementazioni

**Limiti:** dati sintetici, le dimensioni non conservano lo storico, il database viene ricostruito a ogni esecuzione; controlli di qualità bassi; SQLite non è adatto a molti accessi sincroni, la dashboard non ha autenticazione, l'analisi è descrittiva.

**implementazioni:** dimensioni con storico delle modifiche e non sovrascrittura, caricamento incrementale, controlli di qualità ciclici, automatici e registrati; test, confronto con il periodo antecedente e analisi per coorti, dati reali anonimizzati, abbinamento per zona di prossimità tra clienti, fornitori e operatori.

## 17. eventuali errori

| Messaggio o sintomo | Probabile causa | Rimedio |
|---|---|---|
| `python` non riconosciuto, o si apre il Microsoft Store | Python non installato o non nel PATH | installa Python da python.org spuntando *Add python.exe to PATH*; riapri VS Code; prova `py` |
| `No module named pandas` (o `streamlit`) | librerie non installate o ambiente non attivo | attiva `.venv` e lancia `pip install -r requirements.txt` |
| `FileNotFoundError: data/clienti.csv` | `etl.py` lanciato prima del generatore, o cartella sbagliata | lancia prima `generate_data.py`; controlla la cartella con `dir` o `ls` |
| `no such table: dim_cliente` | `etl.py` non eseguito o fallito | rilancia `python etl.py` e leggi l'ultimo messaggio |
| `AssertionError: …` | un controllo di qualità ha trovato un dato incoerente | leggi il messaggio, che dice quale regola è violata |
| `streamlit non riconosciuto` | ambiente non attivo | `python -m streamlit run dashboard.py` |
| pagina bianca o numeri vecchi | cache o browser | premi `C` nella pagina, ricarica con F5, prova una finestra in incognito |
| `DLL load failed … Un criterio di controllo dell'applicazione ha bloccato il file` (Windows) | Windows blocca un file compilato di pandas (per esempio con Python 3.14) | prova Python 3.12; controlla il Controllo intelligente delle app; oppure usa GitHub Codespaces |
| `verifica.py` stampa `ERRORE` | incoerenza tra CSV e warehouse | rilancia generatore ed ETL nell'ordine giusto |

