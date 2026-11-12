-- Schema a stella del data warehouse (SQLite)
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fact_richieste;
DROP TABLE IF EXISTS dim_cliente;
DROP TABLE IF EXISTS dim_fornitore;
DROP TABLE IF EXISTS dim_operatore;
DROP TABLE IF EXISTS dim_tempo;

CREATE TABLE dim_cliente (
    cliente_key      INTEGER PRIMARY KEY,   -- chiave surrogata
    id_cliente       TEXT NOT NULL UNIQUE,  -- chiave naturale (sistema sorgente)
    zona             TEXT NOT NULL,
    data_iscrizione  TEXT NOT NULL
);

CREATE TABLE dim_fornitore (
    fornitore_key       INTEGER PRIMARY KEY,
    id_fornitore        TEXT NOT NULL UNIQUE,
    nome                TEXT NOT NULL,
    categoria_servizio  TEXT NOT NULL,
    zona                TEXT NOT NULL
);

CREATE TABLE dim_operatore (
    operatore_key  INTEGER PRIMARY KEY,
    id_operatore   TEXT NOT NULL UNIQUE,
    zona           TEXT NOT NULL,
    tipo_attivita  TEXT NOT NULL
);

CREATE TABLE dim_tempo (
    tempo_key        INTEGER PRIMARY KEY,   -- formato AAAAMMGGHH
    data             TEXT NOT NULL,         -- AAAA-MM-GG
    anno             INTEGER NOT NULL,
    mese             INTEGER NOT NULL,
    nome_mese        TEXT NOT NULL,
    giorno_settimana TEXT NOT NULL,
    ora              INTEGER NOT NULL,
    fascia_oraria    TEXT NOT NULL,         -- mattina / pomeriggio / sera
    is_weekend       INTEGER NOT NULL
);

-- Granularità: una riga per ogni richiesta di servizio
CREATE TABLE fact_richieste (
    id_richiesta          TEXT PRIMARY KEY,
    cliente_key           INTEGER NOT NULL REFERENCES dim_cliente(cliente_key),
    fornitore_key         INTEGER NOT NULL REFERENCES dim_fornitore(fornitore_key),
    operatore_key         INTEGER NOT NULL REFERENCES dim_operatore(operatore_key),
    tempo_key             INTEGER NOT NULL REFERENCES dim_tempo(tempo_key),
    importo               REAL NOT NULL,     -- misura additiva (euro)
    tempo_erogazione_min  REAL,              -- misura (NULL se annullata)
    stato                 TEXT NOT NULL,     -- completata / in_ritardo / annullata
    is_annullata          INTEGER NOT NULL,
    is_in_ritardo         INTEGER NOT NULL
);

CREATE INDEX idx_fact_cliente   ON fact_richieste(cliente_key);
CREATE INDEX idx_fact_fornitore ON fact_richieste(fornitore_key);
CREATE INDEX idx_fact_tempo     ON fact_richieste(tempo_key);
