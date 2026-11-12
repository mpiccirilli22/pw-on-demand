"""Disegna in testo lo schema a stella leggendo le tabelle e le chiavi di warehouse.db."""
import sqlite3

con = sqlite3.connect("warehouse.db")

def colonne(tabella):
    return [(r[1], r[5]) for r in con.execute(f"PRAGMA table_info({tabella})")]

def righe(tabella):
    return con.execute(f"SELECT COUNT(*) FROM {tabella}").fetchone()[0]

# la tabella dei fatti è quella che contiene chiavi esterne
fatti = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
         if list(con.execute(f"PRAGMA foreign_key_list({t})"))][0]
collegamenti = [(r[3], r[2], r[4]) for r in con.execute(f"PRAGMA foreign_key_list({fatti})")]

print(f"\n{fatti}  ({righe(fatti)} righe)   <-- TABELLA DEI FATTI (centro della stella)")
print("   misure: " + ", ".join(n for n, pk in colonne(fatti)
                               if not pk and n not in [c[0] for c in collegamenti]))
for i, (chiave, dimensione, chiave_dim) in enumerate(collegamenti):
    ramo = "└──" if i == len(collegamenti) - 1 else "├──"
    print(f"   {ramo} {chiave:14s} ──► {dimensione}  ({righe(dimensione)} righe)")
    resto = "    " if i == len(collegamenti) - 1 else "│   "
    attributi = ", ".join(n + (" (PK)" if pk else "") for n, pk in colonne(dimensione))
    print(f"   {resto}      {attributi}")
print()
con.close()
