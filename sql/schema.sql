DROP VIEW IF EXISTS vw_indicadores_municipio;
DROP TABLE IF EXISTS registro_anual;
DROP TABLE IF EXISTS escola;
DROP TABLE IF EXISTS municipio;

CREATE TABLE municipio (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE escola (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL,
    municipio_id INTEGER NOT NULL REFERENCES municipio(id),
    UNIQUE (nome, municipio_id)
);

CREATE TABLE registro_anual (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    escola_id            INTEGER NOT NULL REFERENCES escola(id),
    ano                  INTEGER NOT NULL,
    matriculas_total     INTEGER NOT NULL,
    matricula_inicial    INTEGER,
    matricula_apos_censo INTEGER,
    transferidos         INTEGER,
    cancelados           INTEGER,
    falecidos            INTEGER,
    abandono             INTEGER,
    aprovados            INTEGER,
    reprovados           INTEGER,
    cursando             INTEGER,
    outras_situacoes     INTEGER,
    UNIQUE (escola_id, ano)
);

CREATE INDEX idx_registro_ano ON registro_anual(ano);

-- Indicadores por município e ano.
-- ano_completo = 0 quando mais de 5% das matrículas ainda estão "Cursando"
-- (retrato do meio do ano letivo): nesses anos as taxas ficam NULL.
CREATE VIEW vw_indicadores_municipio AS
WITH soma AS (
    SELECT m.nome AS municipio, r.ano,
           COUNT(DISTINCT e.id)    AS escolas,
           SUM(r.matriculas_total) AS matriculas,
           SUM(r.aprovados)        AS aprovados,
           SUM(r.reprovados)       AS reprovados,
           SUM(r.abandono)         AS abandono,
           SUM(r.cancelados)       AS cancelados,
           SUM(r.transferidos)     AS transferidos,
           SUM(r.cursando)         AS cursando
    FROM registro_anual r
    JOIN escola e    ON e.id = r.escola_id
    JOIN municipio m ON m.id = e.municipio_id
    GROUP BY m.nome, r.ano
)
SELECT *,
       CASE WHEN cursando < 0.05 * matriculas THEN 1 ELSE 0 END AS ano_completo,
       CASE WHEN cursando < 0.05 * matriculas THEN
            ROUND(100.0 * aprovados  / NULLIF(aprovados + reprovados + abandono, 0), 2) END AS taxa_aprovacao,
       CASE WHEN cursando < 0.05 * matriculas THEN
            ROUND(100.0 * reprovados / NULLIF(aprovados + reprovados + abandono, 0), 2) END AS taxa_reprovacao,
       CASE WHEN cursando < 0.05 * matriculas THEN
            ROUND(100.0 * abandono   / NULLIF(aprovados + reprovados + abandono, 0), 2) END AS taxa_abandono,
       CASE WHEN cursando < 0.05 * matriculas THEN
            ROUND(100.0 * cancelados / NULLIF(aprovados + reprovados + abandono + cancelados, 0), 2) END AS taxa_cancelamento
FROM soma;
