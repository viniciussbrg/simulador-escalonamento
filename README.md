# Simulador de Escalonamento de Tarefas

Projeto pratico da disciplina de Sistemas Operacionais - Grupo 2, semestre 2026.2.

Repositorio GitHub: **Task-Scheduling-Simulator**

Descricao GitHub: **Python desktop simulator for CPU scheduling algorithms with priority inversion, priority inheritance, ceiling protocol, aging, scenario persistence, and validation tests.**

## Como executar

Clique duas vezes em:

```text
dist/Simulador.exe
```

Nao e necessario abrir terminal, criar ambiente virtual, instalar bibliotecas ou passar argumentos. A aplicacao abre uma janela grafica e permanece aberta apos a simulacao e diante de erros de entrada.

Durante desenvolvimento, tambem e possivel executar:

```powershell
python main.py
```

## Identificacao

| Item | Valor |
|---|---|
| Projeto | Simulador de Escalonamento de Tarefas |
| Disciplina | Sistemas Operacionais |
| Grupo | Grupo 2 |
| Semestre | 2026.2 |
| Professor(a) | Vinicius S. Borges |

## Autoria

- Nicholas Birochi - 081230038
- Henrico Birochi - 081230027
- Edgar Camacho Seabra Ribeiro - 081230039
- Vitor Agostino Braghittoni - 081230024

## Descricao

O projeto implementa um simulador de escalonamento de tarefas em Python, com interface grafica em Tkinter. A aplicacao permite cadastrar ou sortear tarefas, escolher parametros de escalonamento, executar os seis algoritmos exigidos e visualizar metricas e diagrama temporal.

O simulador reproduz os cenarios de validacao do enunciado, incluindo custo de troca de contexto, recurso exclusivo R, inversao de prioridades, heranca, teto de prioridade e envelhecimento.

## Estrutura do repositorio

```text
.
|-- main.py                    Ponto de entrada da aplicacao
|-- simulador/                 Codigo principal do simulador
|-- control/                   Wrappers de compatibilidade da estrutura original
|-- model/                     Modelo antigo preservado para compatibilidade
|-- view/                      Wrappers de compatibilidade da interface antiga
|-- cenarios/                  Cenarios oficiais em JSON
|-- tests/                     Testes automatizados
|-- docs/                      Documentacao tecnica e tutoriais
|-- scripts/                   Scripts auxiliares de documentacao
|-- assets/                    Icone do executavel
|-- dist/Simulador.exe         Executavel final para duplo clique
|-- Simulador.spec             Configuracao de build com PyInstaller
|-- requirements.txt           Dependencias de runtime
|-- requirements-dev.txt       Dependencias de build
`-- .gitignore                 Regras para ignorar caches, venv e build
```

## Arquivos de codigo

| Arquivo | Funcao |
|---|---|
| `main.py` | Abre a interface grafica. |
| `simulador/modelos.py` | Define tarefas, intervalos, metricas e resultado da simulacao. |
| `simulador/motor.py` | Contem o laco de simulacao, as politicas e as convencoes C1-C10. |
| `simulador/cenarios.py` | Gera cenarios, executa lotes e salva/carrega JSON. |
| `simulador/gui.py` | Implementa a janela Tkinter, tabela de tarefas, resultados e diagrama temporal. |
| `control/simular_escalonamento.py` | Adapta chamadas antigas para o motor novo. |
| `tests/test_motor.py` | Valida os cenarios oficiais e regras de entrada. |
| `scripts/gerar_pdfs.py` | Gera os PDFs a partir dos documentos Markdown. |
| `scripts/gerar_capturas.py` | Gera capturas de tela usadas nos tutoriais. |

## Requisitos de ambiente

Para usar o executavel final, nao ha requisitos de ambiente alem do Windows.

Para executar pelo codigo-fonte:

- Python testado: 3.12.6
- Dependencias de runtime: nenhuma biblioteca externa
- Biblioteca grafica: Tkinter, incluida na instalacao padrao do Python

Para gerar o executavel:

```powershell
python -m pip install -r requirements-dev.txt
pyinstaller Simulador.spec --clean --noconfirm
```

Para regenerar os PDFs da documentacao:

```powershell
python scripts/gerar_capturas.py
python scripts/gerar_pdfs.py
```

## Funcionalidades

| Funcionalidade | Onde esta implementada |
|---|---|
| FCFS, SJF, SRTF, RR, PRIOc e PRIOp | `simulador/motor.py` |
| Empates por menor ingresso e menor identificador | `simulador/motor.py` |
| Quantum e custo de troca configuraveis | `simulador/gui.py`, `simulador/motor.py` |
| Validacao `quantum > ttc` no RR | `simulador/motor.py` |
| Metricas por tarefa e medias | `simulador/motor.py`, `simulador/gui.py` |
| Diagrama temporal | `simulador/gui.py` |
| Recurso exclusivo R e suspensao | `simulador/motor.py` |
| Inversao de prioridades | `simulador/motor.py`, `cenarios/inversao_prioridade.json` |
| Heranca de prioridade | `simulador/motor.py` |
| Teto de prioridade | `simulador/motor.py` |
| Envelhecimento com `alpha` configuravel | `simulador/motor.py`, `simulador/gui.py` |
| Sorteio de tarefas | `simulador/cenarios.py`, `simulador/gui.py` |
| Salvamento e carregamento de cenarios | `simulador/cenarios.py`, `simulador/gui.py` |
| Comparacao em lote | `simulador/cenarios.py`, `simulador/gui.py` |
| Testes dos cenarios oficiais | `tests/test_motor.py` |

## Documentacao

- [Documentacao tecnica PDF](./docs/documentacao_projeto.pdf) ([fonte Markdown](./docs/documentacao_projeto.md))
- [Tutorial de execucao PDF](./docs/tutorial_execucao.pdf) ([fonte Markdown](./docs/tutorial_execucao.md))
- [Tutorial de uso PDF](./docs/tutorial_uso.pdf) ([fonte Markdown](./docs/tutorial_uso.md))
- [Auditoria final](./docs/auditoria_final.md)

## Por onde comecar

1. Abra `dist/Simulador.exe`.
2. Siga o [Tutorial de execucao](./docs/tutorial_execucao.pdf).
3. Reproduza os cenarios conhecidos pelo [Tutorial de uso](./docs/tutorial_uso.pdf).
4. Consulte a [Documentacao tecnica](./docs/documentacao_projeto.pdf) para entender o codigo.
5. Execute `python -m unittest discover -v` para conferir os testes automatizados pelo codigo-fonte.
