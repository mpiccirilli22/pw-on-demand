"""Esempi minimi per fare pratica con pandas e sqlite3 sui dati del progetto.
Esegui prima generate_data.py ed etl.py.   Avvio: python esempi_base.py
"""
import sqlite3
import pandas as pd

# ---------- 1. pandas: leggere e pulire un CSV ----------
df = pd.read_csv("data/richieste.csv")
print("Righe lette:", len(df))
print(df.head(3), "\n")

df = df.drop_duplicates("id_richiesta")        # elimina i duplicati
df["stato"] = df["stato"].str.lower()          # uniforma i testi (tutta la colonna)
gestite = df[df["stato"] != "annullata"]       # selezione con condizione (come WHERE)
print("Richieste gestite (dati grezzi, prima dell'ETL):", len(gestite))
print("Primi 3 fornitori per incassi (pandas):")
print(gestite.groupby("id_fornitore")["importo"].sum().nlargest(3), "\n")   # come GROUP BY

# ---------- 2. sqlite3: connettersi e interrogare ----------
con = sqlite3.connect("warehouse.db")          # apre il file del data warehouse
righe = con.execute("""SELECT zona, COUNT(*) FROM dim_cliente
                       GROUP BY zona ORDER BY 2 DESC""").fetchall()
print("Clienti per zona (sqlite3):", righe, "\n")

# ---------- 3. sqlite3 + pandas insieme ----------
zona = "Nord"
q = """SELECT fo.categoria_servizio AS categoria, COUNT(*) AS richieste
       FROM fact_richieste f
       JOIN dim_cliente c    ON c.cliente_key = f.cliente_key
       JOIN dim_fornitore fo ON fo.fornitore_key = f.fornitore_key
       WHERE c.zona = ?                        -- il ? passa il valore in modo sicuro
       GROUP BY 1 ORDER BY 2 DESC"""
print(f"Richieste per categoria, zona {zona}:")
print(pd.read_sql(q, con, params=(zona,)))
con.close()

# ---------- 4. sqlite3: creare, inserire, salvare ----------
prova = sqlite3.connect(":memory:")            # database temporaneo in memoria
prova.execute("CREATE TABLE clienti (id INTEGER PRIMARY KEY, zona TEXT)")
prova.execute("INSERT INTO clienti (zona) VALUES (?)", ("Nord",))
prova.commit()                                 # rende definitive le modifiche
print("\nTabella di prova:", prova.execute("SELECT * FROM clienti").fetchall())
prova.close()
