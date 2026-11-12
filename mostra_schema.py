"""Mostra lo schema a stella di warehouse.db: tabelle, colonne, chiavi e un esempio (R00110)."""
import sqlite3

con = sqlite3.connect("warehouse.db")
tabelle = [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]

print("=== TABELLE E COLONNE ===")
for t in tabelle:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"\n{t}  ({n} righe)")
    for _, nome, tipo, notnull, _, pk in con.execute(f"PRAGMA table_info({t})"):
        print(f"   {nome:22s} {tipo:8s} {'PK' if pk else ''}")

print("\n=== COLLEGAMENTI (chiavi esterne) ===")
for t in tabelle:
    for r in con.execute(f"PRAGMA foreign_key_list({t})"):
        print(f"   {t}.{r[3]}  ->  {r[2]}.{r[4]}")

print("\n=== ESEMPIO: la richiesta R00110 con il suo contesto ===")
cur = con.execute("""
SELECT f.id_richiesta, f.importo, f.tempo_erogazione_min, f.stato,
       c.id_cliente, c.zona, fo.id_fornitore, fo.categoria_servizio, fo.zona,
       o.id_operatore, o.tipo_attivita, t.data, t.giorno_settimana, t.ora, t.fascia_oraria
FROM fact_richieste f
JOIN dim_cliente c    ON c.cliente_key = f.cliente_key
JOIN dim_fornitore fo ON fo.fornitore_key = f.fornitore_key
JOIN dim_operatore o  ON o.operatore_key = f.operatore_key
JOIN dim_tempo t      ON t.tempo_key = f.tempo_key
WHERE f.id_richiesta = 'R00110'""")
etichette = ["richiesta", "importo", "minuti", "stato", "cliente", "zona cliente",
             "fornitore", "categoria", "zona fornitore", "operatore", "attività",
             "data", "giorno", "ora", "fascia"]
for e, v in zip(etichette, cur.fetchone()):
    print(f"   {e:15s} {v}")
con.close()
