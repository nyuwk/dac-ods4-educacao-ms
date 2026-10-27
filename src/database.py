"""Conexão com o SQLite, criação do schema e gravação dos objetos."""
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent  # pasta do projeto, de onde quer que o código rode
DB_PATH = RAIZ / "educacao_ms.db"


def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def criar_schema(con: sqlite3.Connection) -> None:
    con.executescript((RAIZ / "sql" / "schema.sql").read_text(encoding="utf-8"))


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


def banco_pronto() -> bool:
    """True se o banco existe e já tem a série histórica carregada."""
    if not DB_PATH.exists():
        return False
    try:
        with sqlite3.connect(DB_PATH) as con:
            return con.execute("SELECT COUNT(*) FROM registro_anual").fetchone()[0] > 0
    except sqlite3.Error:
        return False


def garantir_banco() -> None:
    """Cria e carrega o banco a partir dos CSVs se ele ainda não existir (ex.: na hospedagem online)."""
    if banco_pronto():
        return
    from src.loader import CarregadorCSV  # import local evita dependência circular

    municipios = CarregadorCSV(RAIZ / "data" / "raw").carregar()
    con = conectar()
    criar_schema(con)
    salvar(con, municipios)
    con.close()
