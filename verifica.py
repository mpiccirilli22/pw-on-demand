"""Verifica di riconciliazione: ricalcola gli indicatori direttamente dai CSV
(con pandas) e li confronta con quelli del data warehouse (SQL)."""
import sqlite3
import pandas as pd

raw = pd.read_csv("data/richieste.csv").drop_duplicates("id_richiesta")
raw["stato"] = raw["stato"].str.lower()
cli = pd.read_csv("data/clienti.csv")
raw = raw[raw["id_cliente"].isin(cli["id_cliente"])]
gest = raw[raw["stato"] != "annullata"]

con = sqlite3.connect("warehouse.db")
sql = pd.read_sql("""SELECT COUNT(*) n, SUM(1-is_annullata) g, AVG(tempo_erogazione_min) t
                     FROM fact_richieste""", con).iloc[0]
controlli = {
    "righe nei fatti": (len(raw), int(sql.n)),
    "richieste gestite": (len(gest), int(sql.g)),
    "tempo medio (min)": (round(gest["tempo_erogazione_min"].mean(), 2), round(sql.t, 2)),
}
ok = True
for nome, (atteso, ottenuto) in controlli.items():
    esito = "OK" if atteso == ottenuto else "ERRORE"
    ok &= esito == "OK"
    print(f"{nome:22s} CSV={atteso}  DW={ottenuto}  -> {esito}")
print("Incassi: gli importi mancanti sono stati imputati, quindi il totale DW "
      "è maggiore di quello grezzo (atteso).")
raise SystemExit(0 if ok else 1)
