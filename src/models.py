"""Classes de domínio: Municipio, Escola e RegistroAnual."""
from dataclasses import dataclass, field

# Um ano só tem rendimento (aprovação/reprovação) depois que fecha.
# Se mais de 5% das matrículas ainda estão "Cursando", o arquivo é um retrato
# do meio do ano letivo (caso de 2024 e 2026 no portal).
LIMITE_CURSANDO = 0.05


@dataclass
class RegistroAnual:
    ano: int
    matriculas_total: int
    matricula_inicial: int
    matricula_apos_censo: int
    transferidos: int
    cancelados: int
    falecidos: int
    abandono: int
    aprovados: int
    reprovados: int
    cursando: int
    outras_situacoes: int

    @property
    def base_rendimento(self) -> int:
        # padrão INEP: transferidos e falecidos ficam fora do denominador
        return self.aprovados + self.reprovados + self.abandono

    @property
    def ano_completo(self) -> bool:
        return self.matriculas_total > 0 and self.cursando / self.matriculas_total < LIMITE_CURSANDO

    def _taxa(self, parte: int) -> float | None:
        b = self.base_rendimento
        return parte / b * 100 if b and self.ano_completo else None

    def taxa_aprovacao(self) -> float | None:
        return self._taxa(self.aprovados)

    def taxa_reprovacao(self) -> float | None:
        return self._taxa(self.reprovados)

    def taxa_abandono(self) -> float | None:
        return self._taxa(self.abandono)

    def taxa_cancelamento(self) -> float | None:
        # indicador complementar: o portal registra abandono = 0 a partir de 2020
        b = self.base_rendimento + self.cancelados
        return self.cancelados / b * 100 if b and self.ano_completo else None


@dataclass
class Escola:
    nome: str
    municipio: str
    registros: dict[int, RegistroAnual] = field(default_factory=dict)  # ano -> registro

    def adicionar(self, r: RegistroAnual) -> None:
        self.registros[r.ano] = r

    def serie_historica(self) -> list[RegistroAnual]:
        return [self.registros[a] for a in sorted(self.registros)]


@dataclass
class Municipio:
    nome: str
    escolas: dict[str, Escola] = field(default_factory=dict)  # nome normalizado -> escola

    def total_matriculas(self, ano: int) -> int:
        return sum(e.registros[ano].matriculas_total for e in self.escolas.values() if ano in e.registros)
