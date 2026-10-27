# Notas sobre os dados

Fonte: Portal de Dados Abertos de MS, dataset "Matrículas por Unidade Escolar" (SED/MS, licença CC-BY).
Arquivos baixados em 27/10/2026.

## Visão geral dos arquivos

| Ano  | Linhas (escolas) | Matrículas | Cursando | Situação do ano |
|------|-----------------:|-----------:|---------:|-----------------|
| 2018 | 485 | 326.367 | 369 | Completo |
| 2019 | 475 | 293.195 | 100 | Completo |
| 2020 | 441 | 242.028 | 179 | Completo |
| 2021 | 442 | 248.780 | 51 | Completo |
| 2022 | 472 | 247.646 | 93 | Completo |
| 2023 | 467 | 237.574 | 412 | Completo |
| 2024 | 461 | 220.926 | 184.949 | Incompleto (retrato do meio do ano) |
| 2026 | 460 | 199.489 | 187.470 | Incompleto (retrato de março) |

- 15 colunas iguais em todos os anos (14 do dicionário de dados + `_id`, criada pelo portal).
- Nenhum valor nulo. 79 municípios em todos os anos, sem grafias diferentes.
- Consistência interna verificada: em todos os anos, Transferidos + Cancelados + Falecido + Abandono +
  Aprovados + Reprovados + Cursando + OutrasSituacoes = MatriculasTotal, e
  MatriculaInicial + MatriculaAposCenso = MatriculasTotal.
- São dados da **rede estadual** (cerca de 460 escolas por ano), não de toda a rede pública.
- Carga no banco: 3.703 registros, 598 escolas distintas, 79 municípios. 374 escolas aparecem nos 8 arquivos.

## Problemas encontrados e decisões

1. **2025 não existe no portal.** A série tem lacuna entre 2024 e 2026.
2. **2024 e 2026 estão incompletos.** O de 2024 foi publicado em julho de 2024 e o de 2026 em março de 2026:
   84% e 94% dos alunos ainda aparecem como "Cursando". Calcular aprovação nesses anos daria valor falso
   (2024 daria 77%, com base em menos de 5 mil alunos). Decisão: ano é considerado completo quando menos de
   5% das matrículas estão "Cursando"; anos incompletos mostram matrículas, mas não taxas.
   Série de rendimento válida: 2018 a 2023.
3. **Abandono zerado a partir de 2020.** Foram 10.490 abandonos em 2018, 158 em 2019 e zero em todas as escolas
   de 2020 a 2026. Provavelmente mudança na forma de registro da SED, não ausência real de abandono.
   Decisão: manter a taxa de abandono e acrescentar a taxa de cancelamento (matrículas canceladas) como
   indicador complementar, deixando a limitação explícita na interface.
4. **Sem código INEP da escola.** A identificação é feita pelo par (nome normalizado, município). Nomes foram
   normalizados (maiúsculas, sem acento, sem espaços repetidos). 74 escolas aparecem em um só ano, o que pode
   indicar escola nova, fechada ou nome alterado.
5. **Pandemia (2020-2021).** Aprovação sobe de 86,7% (2019) para 89,4% (2020), em linha com as regras de
   promoção flexibilizadas no ensino remoto.

## Indicadores (estado, anos completos)

Taxas calculadas no padrão INEP: base = Aprovados + Reprovados + Abandono (transferidos e falecidos fora).
Cancelamento = Cancelados / (base + Cancelados).

| Ano  | Aprovação | Reprovação | Abandono | Cancelamento |
|------|----------:|-----------:|---------:|-------------:|
| 2018 | 81,34% | 14,62% | 4,04% | 3,75% |
| 2019 | 86,68% | 13,25% | 0,07% | 3,36% |
| 2020 | 89,37% | 10,63% | 0,00% | 3,77% |
| 2021 | 88,45% | 11,55% | 0,00% | 3,08% |
| 2022 | 88,04% | 11,96% | 0,00% | 3,80% |
| 2023 | 88,68% | 11,32% | 0,00% | 3,66% |

- Aprovação: +7,3 p.p. entre 2018 e 2023. Reprovação: -3,3 p.p.
- Matrículas caem 27% entre 2018 e 2023 (326.367 para 237.574).
- Campo Grande: aprovação de 81,4% (2018) para 87,0% (2023), +5,6 p.p.
