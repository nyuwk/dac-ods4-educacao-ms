import urllib.request
from pathlib import Path

ANOS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2026]  # 2025 não existe no portal
BASE = "https://www.dados.ms.gov.br/datastore/dump/matriculas-por-unidade-escolar-{}"

destino = Path("data/raw")
destino.mkdir(parents=True, exist_ok=True)
for ano in ANOS:
    arquivo = destino / f"matriculas_{ano}.csv"
    urllib.request.urlretrieve(BASE.format(ano), arquivo)
    print(f"{ano}: {arquivo.stat().st_size / 1024:.0f} KB")