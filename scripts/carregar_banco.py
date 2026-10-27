from src.database import conectar, criar_schema, salvar
from src.loader import CarregadorCSV

carregador = CarregadorCSV()
municipios = carregador.carregar()
print(f"Linhas lidas dos CSVs: {carregador.linhas_lidas}")
print(f"Municípios: {len(municipios)} | Escolas: {sum(len(m.escolas) for m in municipios.values())}")

con = conectar()
criar_schema(con)
salvar(con, municipios)

print("\nRegistros gravados por ano:")
for ano, qtd in con.execute("SELECT ano, COUNT(*) FROM registro_anual GROUP BY ano"):
    print(f"  {ano}: {qtd}")
