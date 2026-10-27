"""Consultas usadas pela interface."""
import pandas as pd

from src.database import conectar, garantir_banco


class RepositorioEscolar:
    def __init__(self):
        garantir_banco()
        self.con = conectar()

    def municipios(self) -> list[str]:
        return [r[0] for r in self.con.execute("SELECT nome FROM municipio ORDER BY nome")]

    def anos(self) -> list[int]:
        return [r[0] for r in self.con.execute("SELECT DISTINCT ano FROM registro_anual ORDER BY ano")]

    def indicadores(self, municipios: list[str], ano_ini: int, ano_fim: int) -> pd.DataFrame:
        sql = "SELECT * FROM vw_indicadores_municipio WHERE ano BETWEEN ? AND ?"
        params: list = [ano_ini, ano_fim]
        if municipios:
            sql += f" AND municipio IN ({','.join('?' * len(municipios))})"
            params += municipios
        return pd.read_sql_query(sql + " ORDER BY municipio, ano", self.con, params=params)

    def escolas(self, municipio: str, ano_ini: int, ano_fim: int) -> pd.DataFrame:
        sql = """SELECT e.nome AS escola, r.ano, r.matriculas_total AS matriculas, r.aprovados,
                        r.reprovados, r.abandono, r.cancelados, r.transferidos, r.cursando
                 FROM registro_anual r
                 JOIN escola e ON e.id = r.escola_id
                 JOIN municipio m ON m.id = e.municipio_id
                 WHERE m.nome = ? AND r.ano BETWEEN ? AND ?
                 ORDER BY e.nome, r.ano"""
        return pd.read_sql_query(sql, self.con, params=[municipio, ano_ini, ano_fim])
