"""Generatore di dati sintetici per la startup di servizi on-demand.

Produce 4 file CSV in data/ (clienti, fornitori, operatori, richieste).
I dati sono inventati, privi di informazioni personali e riproducibili
grazie al seed fisso. Alcuni errori vengono inseriti di proposito
(duplicati, zone scritte in modo diverso, importi mancanti, riferimenti
orfani) per mostrare il lavoro di pulizia dell'ETL.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_CLIENTI, N_FORNITORI, N_OPERATORI, N_RICHIESTE = 320, 300, 300, 600
INIZIO, FINE = "2025-07-01", "2025-12-31"
ZONE = ["Nord", "Centro", "Sud", "Est", "Ovest"]
CATEGORIE = ["Pulizie", "Riparazioni", "Consegne", "Assistenza IT", "Giardinaggio"]
ATTIVITA = ["A domicilio", "Da remoto", "In sede"]
# prezzo medio per categoria (euro), usato per importi realistici
PREZZO = {"Pulizie": 55, "Riparazioni": 90, "Consegne": 25,
          "Assistenza IT": 70, "Giardinaggio": 65}
# tempo medio di erogazione per categoria (minuti)
TEMPO = {"Pulizie": 120, "Riparazioni": 95, "Consegne": 40,
         "Assistenza IT": 60, "Giardinaggio": 150}

rng = np.random.default_rng(SEED)
out = Path(__file__).parent / "data"
out.mkdir(exist_ok=True)


def pesi_popolarita(n, esponente=1.1):
    """Pesi 'a coda lunga': pochi elementi molto usati, molti poco usati."""
    p = 1 / np.arange(1, n + 1) ** esponente
    rng.shuffle(p)
    return p / p.sum()


# ---------- clienti ----------
date_iscr = pd.to_datetime(INIZIO) - pd.to_timedelta(rng.integers(0, 400, N_CLIENTI), unit="D")
clienti = pd.DataFrame({
    "id_cliente": [f"C{i:04d}" for i in range(1, N_CLIENTI + 1)],
    "zona": rng.choice(ZONE, N_CLIENTI, p=[.28, .26, .18, .14, .14]),
    "data_iscrizione": date_iscr.strftime("%Y-%m-%d"),
})

# ---------- fornitori ----------
fornitori = pd.DataFrame({
    "id_fornitore": [f"F{i:04d}" for i in range(1, N_FORNITORI + 1)],
    "nome": [f"Fornitore {i:03d}" for i in range(1, N_FORNITORI + 1)],
    "categoria_servizio": rng.choice(CATEGORIE, N_FORNITORI, p=[.26, .2, .22, .14, .18]),
    "zona": rng.choice(ZONE, N_FORNITORI),
})

# ---------- operatori ----------
operatori = pd.DataFrame({
    "id_operatore": [f"O{i:04d}" for i in range(1, N_OPERATORI + 1)],
    "zona": rng.choice(ZONE, N_OPERATORI),
    "tipo_attivita": rng.choice(ATTIVITA, N_OPERATORI, p=[.6, .25, .15]),
})

# ---------- richieste ----------
giorni = pd.date_range(INIZIO, FINE, freq="D")
# più richieste nei giorni feriali, picco il venerdì, calo la domenica
peso_giorno = np.array([{0: 1.0, 1: 1.0, 2: 1.05, 3: 1.1, 4: 1.3, 5: 1.15, 6: 0.6}[d.dayofweek]
                        for d in giorni])
# leggera crescita nel tempo (la startup si sta sviluppando)
peso_giorno = peso_giorno * np.linspace(0.8, 1.3, len(giorni))
peso_giorno /= peso_giorno.sum()
# fasce orarie: picchi 9-12 e 17-20
ore = np.arange(7, 22)
peso_ora = np.array([1, 2, 4, 5, 4, 2, 1.5, 1.5, 2, 3, 5, 5, 4, 2, 1], dtype=float)
peso_ora /= peso_ora.sum()

giorno = rng.choice(giorni, N_RICHIESTE, p=peso_giorno)
ora = rng.choice(ore, N_RICHIESTE, p=peso_ora)
minuti = rng.integers(0, 60, N_RICHIESTE)
data_ora = pd.to_datetime(giorno) + pd.to_timedelta(ora, unit="h") + pd.to_timedelta(minuti, unit="m")

id_cli = rng.choice(clienti["id_cliente"], N_RICHIESTE, p=pesi_popolarita(N_CLIENTI, 0.9))
id_for = rng.choice(fornitori["id_fornitore"], N_RICHIESTE, p=pesi_popolarita(N_FORNITORI, 1.1))
id_ope = rng.choice(operatori["id_operatore"], N_RICHIESTE)
cat = fornitori.set_index("id_fornitore").loc[id_for, "categoria_servizio"].to_numpy()

importo = np.array([rng.lognormal(np.log(PREZZO[c]), 0.35) for c in cat]).round(2)
tempo = np.array([rng.lognormal(np.log(TEMPO[c]), 0.30) for c in cat]).round(0)
stato = rng.choice(["completata", "in_ritardo", "annullata"], N_RICHIESTE, p=[.78, .12, .10])
# i ritardi durano di più; le annullate non hanno tempo né incasso
tempo = np.where(stato == "in_ritardo", tempo * 1.6, tempo).round(0)
importo = np.where(stato == "annullata", 0.0, importo)
tempo = np.where(stato == "annullata", np.nan, tempo)

richieste = pd.DataFrame({
    "id_richiesta": [f"R{i:05d}" for i in range(1, N_RICHIESTE + 1)],
    "id_cliente": id_cli, "id_fornitore": id_for, "id_operatore": id_ope,
    "data_ora": data_ora.strftime("%Y-%m-%d %H:%M"),
    "importo": importo, "tempo_erogazione_min": tempo, "stato": stato,
}).sort_values("data_ora", ignore_index=True)
richieste["id_richiesta"] = [f"R{i:05d}" for i in range(1, N_RICHIESTE + 1)]

# ---------- errori inseriti di proposito ----------
# 1) zone scritte in modo incoerente (maiuscole, spazi)
idx = rng.choice(N_CLIENTI, 25, replace=False)
clienti.loc[idx, "zona"] = clienti.loc[idx, "zona"].str.upper() + " "
# 2) importi mancanti su richieste non annullate
ok = richieste.index[richieste["stato"] != "annullata"]
richieste.loc[rng.choice(ok, 10, replace=False), "importo"] = np.nan
# 3) richieste con cliente inesistente
richieste.loc[rng.choice(len(richieste), 4, replace=False), "id_cliente"] = "C9999"
# 4) righe duplicate
richieste = pd.concat([richieste, richieste.sample(8, random_state=SEED)], ignore_index=True)
# 5) stato scritto in modo diverso
comp = richieste.index[richieste["stato"] == "completata"]
richieste.loc[rng.choice(comp, 12, replace=False), "stato"] = "Completata"

for nome, df in [("clienti", clienti), ("fornitori", fornitori),
                 ("operatori", operatori), ("richieste", richieste)]:
    df.to_csv(out / f"{nome}.csv", index=False)
    print(f"{nome}.csv: {len(df)} righe")
