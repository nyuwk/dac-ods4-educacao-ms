"""Conexão com o SQLite, criação do schema e gravação dos objetos."""
import sqlite3
from pathlib import Path

DB_PATH = Path("educacao_ms.db")


def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def criar_schema(con: sqlite3.Connection) -> None:
    con.executescript(Path("sql/schema.sql").read_text(encoding="utf-8"))


def salvar(con: sqlite3.Connection, municipios: dict) -> None:
    for mun in municipios.values():
        mun_id = con.execute("INSERT INTO municipio (nome) VALUES (?)", (mun.nome,)).lastrowid
        for esc in mun.escolas.values():
            esc_id = con.execute(
                "INSERT INTO escola (nome, municipio_id) VALUES (?, ?)", (esc.nome, mun_id)
            ).lastrowid
            con.executemany(
                """INSERT INTO registro_anual (escola_id, ano, matriculas_total, matricula_inicial,
                       matricula_apos_censo, transferidos, cancelados, falecidos, abandono,
                       aprovados, reprovados, cursando, outras_situacoes)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [(esc_id, r.ano, r.matriculas_total, r.matricula_inicial, r.matricula_apos_censo,
                  r.transferidos, r.cancelados, r.falecidos, r.abandono, r.aprovados,
                  r.reprovados, r.cursando, r.outras_situacoes) for r in esc.serie_historica()],
            )
    con.commit()
