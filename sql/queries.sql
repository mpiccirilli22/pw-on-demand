-- ============================================================
-- Interrogazioni SQL per gli indicatori principali
-- Convenzioni: "richiesta gestita" = non annullata.
-- La zona di riferimento è quella del CLIENTE (dove si eroga il servizio).
-- ============================================================

-- Q1. Indicatori di sintesi
SELECT
    COUNT(*)                                              AS richieste_totali,
    SUM(1 - f.is_annullata)                               AS richieste_gestite,
    SUM(f.is_annullata)                                   AS richieste_annullate,
    ROUND(100.0 * SUM(f.is_annullata) / COUNT(*), 1)      AS pct_annullate,
    ROUND(SUM(f.importo), 2)                              AS incassi_totali,
    ROUND(AVG(f.tempo_erogazione_min), 1)                 AS tempo_medio_min,
    ROUND(100.0 * SUM(f.is_in_ritardo) / SUM(1 - f.is_annullata), 1) AS pct_in_ritardo
FROM fact_richieste f;

-- Q2. Clienti attivi e percentuale di clienti che tornano
WITH per_cliente AS (
    SELECT cliente_key, COUNT(*) AS n
    FROM fact_richieste
    WHERE is_annullata = 0
    GROUP BY cliente_key
)
SELECT
    COUNT(*)                                                AS clienti_attivi,
    SUM(CASE WHEN n >= 2 THEN 1 ELSE 0 END)                 AS clienti_che_tornano,
    ROUND(100.0 * SUM(CASE WHEN n >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_clienti_che_tornano
FROM per_cliente;

-- Q3. Andamento mensile delle richieste e degli incassi
SELECT t.anno, t.mese, t.nome_mese,
       COUNT(*)                         AS richieste,
       SUM(1 - f.is_annullata)          AS gestite,
       ROUND(SUM(f.importo), 2)         AS incassi
FROM fact_richieste f
JOIN dim_tempo t ON t.tempo_key = f.tempo_key
GROUP BY t.anno, t.mese, t.nome_mese
ORDER BY t.anno, t.mese;

-- Q4. Primi 5 fornitori per incassi
SELECT fo.nome, fo.categoria_servizio,
       COUNT(*)                 AS richieste,
       ROUND(SUM(f.importo), 2) AS incassi
FROM fact_richieste f
JOIN dim_fornitore fo ON fo.fornitore_key = f.fornitore_key
GROUP BY fo.fornitore_key
ORDER BY incassi DESC
LIMIT 5;

-- Q5. Incassi e richieste per zona del cliente
SELECT c.zona,
       COUNT(*)                 AS richieste,
       ROUND(SUM(f.importo), 2) AS incassi,
       ROUND(AVG(f.tempo_erogazione_min), 1) AS tempo_medio_min
FROM fact_richieste f
JOIN dim_cliente c ON c.cliente_key = f.cliente_key
GROUP BY c.zona
ORDER BY incassi DESC;

-- Q6. Richieste e incassi per categoria di servizio
SELECT fo.categoria_servizio,
       COUNT(*)                 AS richieste,
       ROUND(SUM(f.importo), 2) AS incassi,
       ROUND(AVG(f.tempo_erogazione_min), 1) AS tempo_medio_min,
       ROUND(100.0 * SUM(f.is_annullata) / COUNT(*), 1) AS pct_annullate
FROM fact_richieste f
JOIN dim_fornitore fo ON fo.fornitore_key = f.fornitore_key
GROUP BY fo.categoria_servizio
ORDER BY incassi DESC;

-- Q7. Richieste per giorno della settimana e fascia oraria
SELECT t.giorno_settimana, t.fascia_oraria, COUNT(*) AS richieste
FROM fact_richieste f
JOIN dim_tempo t ON t.tempo_key = f.tempo_key
GROUP BY t.giorno_settimana, t.fascia_oraria;
