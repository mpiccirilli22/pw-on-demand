"""Dashboard interattiva (Streamlit) sul data warehouse SQLite.

Avvio:  streamlit run dashboard.py
"""
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

DB = Path(__file__).parent / "warehouse.db"
st.set_page_config(page_title="Dashboard richieste", layout="wide")


@st.cache_data
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB) as con:
        return pd.read_sql(sql, con, params=params)


# ----------------------------- FILTRI -----------------------------
st.title("Dashboard – Startup di servizi on-demand")
limiti = query("SELECT MIN(data) AS da, MAX(data) AS a FROM dim_tempo")
zone = query("SELECT DISTINCT zona FROM dim_cliente ORDER BY zona")["zona"].tolist()
categorie = query("SELECT DISTINCT categoria_servizio AS c FROM dim_fornitore ORDER BY c")["c"].tolist()

with st.sidebar:
    st.header("Filtri")
    periodo = st.date_input("Periodo", (pd.to_datetime(limiti.da[0]), pd.to_datetime(limiti.a[0])),
                            min_value=pd.to_datetime(limiti.da[0]), max_value=pd.to_datetime(limiti.a[0]))
    sel_zone = st.multiselect("Zona del cliente", zone, default=zone)
    sel_cat = st.multiselect("Categoria di servizio", categorie, default=categorie)

if len(periodo) != 2 or not sel_zone or not sel_cat:
    st.info("Seleziona un periodo completo, almeno una zona e almeno una categoria.")
    st.stop()

# Clausola WHERE comune a tutte le interrogazioni (parametri, mai testo concatenato)
ph = lambda v: ",".join("?" * len(v))
FROM = f"""
FROM fact_richieste f
JOIN dim_tempo t      ON t.tempo_key = f.tempo_key
JOIN dim_cliente c    ON c.cliente_key = f.cliente_key
JOIN dim_fornitore fo ON fo.fornitore_key = f.fornitore_key
WHERE t.data BETWEEN ? AND ?
  AND c.zona IN ({ph(sel_zone)})
  AND fo.categoria_servizio IN ({ph(sel_cat)})
"""
P = (str(periodo[0]), str(periodo[1]), *sel_zone, *sel_cat)

# ----------------------------- INDICATORI -----------------------------
k = query(f"""SELECT COUNT(*) AS tot, SUM(1 - f.is_annullata) AS gestite,
                     COALESCE(SUM(f.importo),0) AS incassi,
                     AVG(f.tempo_erogazione_min) AS tempo,
                     COUNT(DISTINCT CASE WHEN f.is_annullata = 0 THEN f.cliente_key END) AS attivi
              {FROM}""", P).iloc[0]
ritorno = query(f"""SELECT f.cliente_key, COUNT(*) AS n {FROM} AND f.is_annullata = 0
                    GROUP BY f.cliente_key""", P)
pct_ritorno = 100 * (ritorno["n"] >= 2).mean() if len(ritorno) else 0

c0, c1, c2, c3, c4, c5 = st.columns(6)
c0.metric("Richieste totali", f"{int(k.tot):,}".replace(",", "."))
c1.metric("Richieste gestite", f"{int(k.gestite or 0):,}".replace(",", "."))
c2.metric("Incassi", f"€ {k.incassi:,.0f}".replace(",", "."))
c3.metric("Tempo medio (min)", "–" if pd.isna(k.tempo) else f"{k.tempo:.0f}")
c4.metric("Clienti attivi", int(k.attivi))
c5.metric("Clienti che tornano", f"{pct_ritorno:.0f}%")
st.caption("Richieste totali = tutte le richieste ricevute; richiesta gestita = non annullata. Clienti che tornano = clienti attivi con almeno 2 richieste "
           "nel periodo selezionato. La zona è quella del cliente.")

# ----------------------------- GRAFICI -----------------------------
a, b = st.columns(2)
with a:
    st.subheader("Andamento mensile delle richieste")
    m = query(f"SELECT t.anno*100+t.mese AS mese, COUNT(*) AS richieste {FROM} GROUP BY 1 ORDER BY 1", P)
    st.line_chart(m.set_index("mese")["richieste"])
with b:
    st.subheader("Primi 5 fornitori per incassi (€)")
    f5 = query(f"""SELECT fo.nome, ROUND(SUM(f.importo),2) AS incassi {FROM}
                   GROUP BY fo.fornitore_key ORDER BY incassi DESC LIMIT 5""", P)
    st.bar_chart(f5.set_index("nome")["incassi"])

a, b = st.columns(2)
with a:
    st.subheader("Richieste per zona")
    z = query(f"SELECT c.zona, COUNT(*) AS richieste {FROM} GROUP BY c.zona ORDER BY richieste DESC", P)
    st.bar_chart(z.set_index("zona")["richieste"])
with b:
    st.subheader("Richieste per categoria di servizio")
    cat = query(f"""SELECT fo.categoria_servizio AS categoria, COUNT(*) AS richieste {FROM}
                    GROUP BY 1 ORDER BY richieste DESC""", P)
    st.bar_chart(cat.set_index("categoria")["richieste"])

with st.expander("Analisi di base: giorno della settimana e fascia oraria"):
    g = query(f"SELECT t.fascia_oraria AS fascia, COUNT(*) AS richieste {FROM} GROUP BY 1", P)
    st.bar_chart(g.set_index("fascia")["richieste"])
