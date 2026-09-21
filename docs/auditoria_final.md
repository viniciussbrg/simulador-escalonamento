# Auditoria Final da Entrega

## Estado inicial observado

| Item | Situacao inicial |
|---|---|
| Repositorio | Clonado de `gscarabeli/gerenciador-de-processos`; remoto local alterado depois para `nicholasbirochi/Task-Scheduling-Simulator`. |
| Arquitetura | Seis algoritmos separados, cada um com parte do mecanismo de simulacao. |
| Metricas | `tw` era calculado como tempo ate a primeira execucao em alguns casos. |
| Troca de contexto | Nao era cobrada no primeiro despacho e era somada ao tempo do RR em vez de descontada da fatia. |
| Recurso R | Nao havia secao critica configuravel; a logica antiga inferia recurso por paridade de prioridade. |
| Documentacao | README incompleto; documentacao tecnica e tutoriais ausentes. |
| Entrega | Havia `myenv`, `build`, `dist` antigo, `.vscode` e caches versionados. |

## Matriz R1-R10

| Requisito | Situacao final | Evidencia | Pendencia |
|---|---|---|---|
| R1 | ATENDE | `simulador/motor.py`; `tests/test_motor.py::test_aula5_seis_algoritmos` valida os seis algoritmos. | Nenhuma conhecida. |
| R2 | ATENDE | `simulador/gui.py` permite quantidade, cadastro, sorteio, salvar e carregar JSON. | Nenhuma conhecida. |
| R3 | ATENDE | `ResultadoSimulacao.metricas`; tabela de resultados; testes conferem `tt`, `tp`, `tw` e primeira execucao. | Nenhuma conhecida. |
| R4 | ATENDE | `ttc` e `quantum` configuraveis; valida `quantum > ttc`; eficiencia calculada so no RR. | Nenhuma conhecida. |
| R5 | ATENDE | Secao critica por execucao propria; bloqueio de `t4` em `[3,13)` no cenario oficial. | Nenhuma conhecida. |
| R6 | ATENDE | Heranca temporaria reduz bloqueio de `t4` para `[3,6)`. | Nenhuma conhecida. |
| R7 | ATENDE | Teto calculado pelas tarefas que declaram R; sequencia oficial `t1[0,5) t4[5,8) ...`. | Nenhuma conhecida. |
| R8 | ATENDE | Envelhecimento com `alpha=1` e `alpha=2` reproduz sequencias e medias oficiais. | Nenhuma conhecida. |
| R9 | ATENDE | Aba de lote e `comparar_lote()` executam os seis algoritmos e exibem medias. | Ordenacao depende do sorteio, conforme o PDF. |
| R10 | ATENDE PARCIALMENTE | `dist/Simulador.exe` foi gerado e passou smoke test local. | Testar em maquina limpa diferente. |

## Materiais de entrega

| Item | Situacao final | Evidencia | Pendencia |
|---|---|---|---|
| README | ATENDE | `README.md` com execucao em destaque, autoria, estrutura, funcionalidades e links. | Nenhuma conhecida. |
| Documentacao tecnica | ATENDE | `docs/documentacao_projeto.md` e `docs/documentacao_projeto.pdf`. | Nenhuma conhecida. |
| Tutorial de execucao | ATENDE | `docs/tutorial_execucao.md`, `docs/tutorial_execucao.pdf` e capturas em `docs/imagens/`. | Nenhuma conhecida. |
| Tutorial de uso | ATENDE | `docs/tutorial_uso.md`, `docs/tutorial_uso.pdf` e capturas em `docs/imagens/`. | Nenhuma conhecida. |
| Organizacao | ATENDE | Codigo, cenarios, testes e docs separados; `.gitignore` criado. | Nenhuma conhecida. |
| Executavel | ATENDE PARCIALMENTE | `dist/Simulador.exe`, smoke test via `SIMULADOR_SMOKE=1`. | Abrir por duplo clique em maquina limpa. |
| Cenarios de validacao | ATENDE | `cenarios/*.json` e `tests/test_motor.py`. | Nenhuma conhecida. |
| Tratamento de erros | ATENDE | `SimulacaoErro` e mensagens na GUI. | Nenhuma conhecida. |
| Interface grafica | ATENDE | Tkinter com abas de tarefas, resultados e lote. | Capturas pendentes para tutoriais. |
| Historico Git | ATENDE PARCIALMENTE | Commits descritivos serao criados nesta entrega. | Historico original tinha apenas dois commits. |

## Rubrica

| Criterio | Pontuacao maxima | Status | Evidencia | Pendencia |
|---|---:|---|---|---|
| BLOCO A - Funcionamento | 5,0 | ATENDE | Testes oficiais passam; GUI cobre R1-R9. | Validacao manual completa pela interface. |
| BLOCO B - Entrega e organizacao | 2,0 | ATENDE PARCIALMENTE | Executavel gerado; repo limpo de `myenv`, build e caches. | Teste em maquina limpa; historico anterior era curto. |
| BLOCO C - Documentacao | 2,0 | ATENDE | README e documentacao tecnica em Markdown e PDF criados. | Nenhuma conhecida. |
| BLOCO D - Tutoriais | 1,0 | ATENDE | Tutoriais criados com passos, resultados esperados e capturas de tela reais. | Nenhuma conhecida. |

Estimativa conservadora de pontuacao: **9,5 / 10,0**. A principal verificacao ainda pendente e abrir o executavel por duplo clique em uma maquina limpa diferente da maquina de desenvolvimento.

## Checklist final

| Item | Status |
|---|---|
| FCFS validado | OK |
| SJF validado | OK |
| SRTF validado | OK |
| RR validado | OK |
| PRIOc validado | OK |
| PRIOp validado | OK |
| entrada manual | OK |
| entrada aleatoria | OK |
| valores invalidos tratados | OK |
| salvar cenario | OK |
| carregar cenario | OK |
| tt | OK |
| tp | OK |
| tw | OK |
| primeira execucao | OK |
| medias | OK |
| quantum configuravel | OK |
| ttc configuravel | OK |
| tq > ttc validado | OK |
| eficiencia correta | OK |
| recurso exclusivo | OK |
| bloqueio/suspensao | OK |
| inversao de prioridades | OK |
| heranca | OK |
| reversao da heranca | OK |
| teto | OK |
| heranca e teto mutuamente exclusivos | OK |
| envelhecimento | OK |
| alpha configuravel | OK |
| geracao em lote | OK |
| diagrama temporal | OK |
| convencoes C1-C10 | OK |
| cenarios oficiais reproduzidos | OK |
| executavel por duplo clique | OK local |
| execucao em pasta limpa | RISCO RESIDUAL: testar em outra maquina |
| README | OK |
| documentacao tecnica | OK |
| tutorial de execucao | OK |
| tutorial de uso | OK |
| screenshots inseridas | OK |
| .gitignore adequado | OK |
| myenv fora do versionamento | OK |
| caches fora do versionamento | OK |
| arquivos intermediarios de build tratados | OK |
| requirements revisado | OK |
| codigo explicavel pelos integrantes | OK |
