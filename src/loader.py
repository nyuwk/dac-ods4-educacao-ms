"""Leitura e tratamento dos CSVs do Portal de Dados Abertos de MS."""
import csv
from pathlib import Path

from unidecode import unidecode

from src.models import Escola, Municipio, RegistroAnual


def normalizar(texto: str) -> str:
    """Maiúsculas, sem acento e sem espaços repetidos (o dataset não tem código INEP)."""
    return " ".join(unidecode(texto or "").upper().split())


def inteiro(valor) -> int:
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return 0


class CarregadorCSV:
    def __init__(self, pasta: str = "data/raw"):
        self.pasta = Path(pasta)
        self.municipios: dict[str, Municipio] = {}
        self.linhas_lidas = 0

    def carregar(self) -> dict[str, Municipio]:
        for arquivo in sorted(self.pasta.glob("*.csv")):
            # utf-8-sig remove o BOM; a coluna "_id" do portal é ignorada
            with open(arquivo, encoding="utf-8-sig", newline="") as f:
                for linha in csv.DictReader(f):
                    self._processar(linha)
                    self.linhas_lidas += 1
        return self.municipios

    def _processar(self, l: dict) -> None:
        nome_mun = normalizar(l["NomeMunicipio"])
        nome_esc = normalizar(l["NomeUnidadeEscolar"])
        mun = self.municipios.setdefault(nome_mun, Municipio(nome_mun))
        esc = mun.escolas.setdefault(nome_esc, Escola(nome_esc, nome_mun))
        esc.adicionar(RegistroAnual(
            ano=inteiro(l["AnoReferencia"]),
            matriculas_total=inteiro(l["MatriculasTotal"]),
            matricula_inicial=inteiro(l["MatriculaInicial"]),
            matricula_apos_censo=inteiro(l["MatriculaAposCenso"]),
            transferidos=inteiro(l["Transferidos"]),
            cancelados=inteiro(l["Cancelados"]),
            falecidos=inteiro(l["Falecido"]),
            abandono=inteiro(l["Abandono"]),
            aprovados=inteiro(l["Aprovados"]),
            reprovados=inteiro(l["Reprovados"]),
            cursando=inteiro(l["Cursando"]),
            outras_situacoes=inteiro(l["OutrasSituacoes"]),
        ))
