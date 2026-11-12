"""ETL: legge i CSV, pulisce i dati e li carica nel data warehouse SQLite.

Esecuzione:  python etl.py
Lo script è idempotente: ricrea il database da zero a ogni esecuzione.
"""
import sqlite3
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
DB = BASE / "warehouse.db"
log = []


def report(msg):
    log.append(msg)
    print(msg)


# ===================== 1. EXTRACT =====================
clienti = pd.read_csv(BASE / "data/clienti.csv")
fornitori = pd.read_csv(BASE / "data/fornitori.csv")
operatori = pd.read_csv(BASE / "data/operatori.csv")
richieste = pd.read_csv(BASE / "data/richieste.csv")
report(f"[EXTRACT] clienti={len(clienti)} fornitori={len(fornitori)} "
       f"operatori={len(operatori)} richieste={len(richieste)}")

# ===================== 2. TRANSFORM =====================
# --- uniformazione dei testi (spazi, maiuscole) ---
for df, col in [(clienti, "zona"), (fornitori, "zona"), (operatori, "zona")]:
    df[col] = df[col].str.strip().str.capitalize()
richieste["stato"] = richieste["stato"].str.strip().str.lower()
report("[TRANSFORM] testi uniformati (zone, stati)")

# --- duplicati ---
n = len(richieste)
richieste = richieste.drop_duplicates(subset="id_richiesta", keep="first")
report(f"[TRANSFORM] duplicati rimossi: {n - len(richieste)}")

# --- integrità referenziale: scarta richieste con riferimenti inesistenti ---
n = len(richieste)
valide = (richieste["id_cliente"].isin(clienti["id_cliente"])
          & richieste["id_fornitore"].isin(fornitori["id_fornitore"])
          & richieste["id_operatore"].isin(operatori["id_operatore"]))
scartate = richieste[~valide]
scartate.to_csv(BASE / "data/richieste_scartate.csv", index=False)
richieste = richieste[valide]
report(f"[TRANSFORM] richieste con riferimenti orfani scartate: {n - len(richieste)} "
       f"(salvate in data/richieste_scartate.csv)")

# --- valori mancanti: l'importo mancante di una richiesta NON annullata
#     viene imputato con la mediana della categoria del fornitore ---
richieste = richieste.merge(fornitori[["id_fornitore", "categoria_servizio"]],
                            on="id_fornitore", how="left")
mancanti = richieste["importo"].isna() & (richieste["stato"] != "annullata")
mediane = richieste.groupby("categoria_servizio")["importo"].transform("median")
richieste.loc[mancanti, "importo"] = mediane[mancanti].round(2)
richieste["importo"] = richieste["importo"].fillna(0.0)
report(f"[TRANSFORM] importi mancanti imputati (mediana per categoria): {int(mancanti.sum())}")

# --- campi derivati ---
richieste["data_ora"] = pd.to_datetime(richieste["data_ora"])
richieste["is_annullata"] = (richieste["stato"] == "annullata").astype(int)
richieste["is_in_ritardo"] = (richieste["stato"] == "in_ritardo").astype(int)

# --- dimensione tempo (una riga per ogni ora del periodo) ---
mesi = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio",
        "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ore = pd.date_range(richieste["data_ora"].dt.normalize().min(),
                    richieste["data_ora"].dt.normalize().max() + pd.Timedelta(hours=23),
                    freq="h")
dim_tempo = pd.DataFrame({
    "tempo_key": ore.strftime("%Y%m%d%H").astype(int),
    "data": ore.strftime("%Y-%m-%d"),
    "anno": ore.year, "mese": ore.month,
    "nome_mese": [mesi[m] for m in ore.month],
    "giorno_settimana": [giorni[d] for d in ore.dayofweek],
    "ora": ore.hour,
    "fascia_oraria": pd.cut(ore.hour, [-1, 11, 17, 23],
                            labels=["mattina", "pomeriggio", "sera"]).astype(str),
    "is_weekend": (ore.dayofweek >= 5).astype(int),
})
richieste["tempo_key"] = richieste["data_ora"].dt.strftime("%Y%m%d%H").astype(int)

# --- chiavi surrogate per le dimensioni ---
for df, nome in [(clienti, "cliente_key"), (fornitori, "fornitore_key"),
                 (operatori, "operatore_key")]:
    df.insert(0, nome, range(1, len(df) + 1))
fact = (richieste
        .merge(clienti[["cliente_key", "id_cliente"]], on="id_cliente")
        .merge(fornitori[["fornitore_key", "id_fornitore"]], on="id_fornitore")
        .merge(operatori[["operatore_key", "id_operatore"]], on="id_operatore"))
fact = fact[["id_richiesta", "cliente_key", "fornitore_key", "operatore_key", "tempo_key",
             "importo", "tempo_erogazione_min", "stato", "is_annullata", "is_in_ritardo"]]

# --- controlli di qualità prima del caricamento ---
assert fact["id_richiesta"].is_unique, "id_richiesta duplicati"
assert fact["importo"].ge(0).all(), "importi negativi"
assert fact["tempo_key"].isin(dim_tempo["tempo_key"]).all(), "tempo_key orfano"
assert fact.loc[fact["is_annullata"] == 0, "tempo_erogazione_min"].notna().all(), \
    "tempo mancante su richiesta non annullata"
report(f"[TRANSFORM] controlli di qualità superati. Righe nei fatti: {len(fact)}")

# ===================== 3. LOAD =====================
if DB.exists():
    DB.unlink()
con = sqlite3.connect(DB)
con.executescript((BASE / "sql/schema.sql").read_text(encoding="utf-8"))
# prima le dimensioni, poi i fatti (che dipendono dalle dimensioni)
clienti.to_sql("dim_cliente", con, if_exists="append", index=False)
fornitori.to_sql("dim_fornitore", con, if_exists="append", index=False)
operatori.to_sql("dim_operatore", con, if_exists="append", index=False)
dim_tempo.to_sql("dim_tempo", con, if_exists="append", index=False)
fact.to_sql("fact_richieste", con, if_exists="append", index=False)
con.commit()
fk = con.execute("PRAGMA foreign_key_check").fetchall()
assert not fk, f"violazioni di chiave esterna: {fk}"
report(f"[LOAD] database creato: {DB.name} | fatti={len(fact)} | "
       f"clienti={len(clienti)} fornitori={len(fornitori)} "
       f"operatori={len(operatori)} tempo={len(dim_tempo)}")
con.close()
(BASE / "docs").mkdir(exist_ok=True)
(BASE / "docs/etl_log.txt").write_text("\n".join(log), encoding="utf-8")
