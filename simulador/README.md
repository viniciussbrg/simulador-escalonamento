# Simulador de Escalonamento de Tarefas

Projeto prático da disciplina de Sistemas Operacionais, ministrada pelo professor Vinicius Borges. 8º semestre.

## Autoria

- João Andrade
- Roger Rocha
- Samar Victor

## Descrição

Simulador de escalonamento de tarefas em um processador. Implementa seis algoritmos (FCFS, SJF, SRTF, Round-Robin, prioridade cooperativa e prioridade preemptiva), trata recurso de uso exclusivo e reproduz o fenômeno da inversão de prioridades, com os mecanismos de herança e teto de prioridade.

O projeto também permite configurar quantum, custo de troca de contexto e envelhecimento de prioridade, além de gravar, carregar, sortear e comparar cenários de escalonamento.

## Como executar

No Windows, clique duas vezes em `EXECUTAR.bat`.

No macOS ou Linux, clique duas vezes em `EXECUTAR.command`.

O programa também pode ser iniciado por `main.pyw`. É necessário possuir Python 3.10 ou superior com `tkinter` disponível no sistema.

## Estrutura do repositório

```text
simulador_escalonamento/
|-- EXECUTAR.bat                  Abertura do programa no Windows
|-- EXECUTAR.command              Abertura do programa no macOS/Linux
|-- main.py                       Ponto de entrada do código-fonte
|-- main.pyw                      Ponto de entrada sem console no Windows
|-- model/                        Estruturas de tarefa e cenário
|-- control/                      Motor, políticas e geração de cenários
|-- view/                         Interface gráfica e relatórios
|-- cenarios/                     Conjuntos de tarefas em JSON
|-- tests/                        Testes automatizados
|-- assets/                       Recursos visuais do programa
`-- docs/                         Tutoriais e documentação técnica
```

## Arquivos de código

- `main.py` - ponto de entrada do programa
- `main.pyw` - ponto de entrada da interface sem janela de console
- `model/tarefa.py` - estrutura, validação e serialização de uma tarefa
- `model/cenario.py` - gravação e carregamento dos cenários em JSON
- `control/motor.py` - laço de simulação, recurso, métricas e mecanismos de correção
- `control/politicas.py` - os seis algoritmos de escalonamento
- `control/gerador.py` - sorteio, comparação e execução em lote de cenários
- `view/janela.py` - janela e comandos da interface gráfica
- `view/relatorio.py` - apresentação das métricas e do diagrama de tempo
- `tests/test_cenarios.py` - testes dos cenários de referência
- `tests/test_entrada.py` - testes de entrada, configuração e persistência

## Funcionalidades

| O que faz | Onde |
|-----------|------|
| Os seis algoritmos | `control/politicas.py` |
| Laço de simulação | `control/motor.py` |
| Métricas por tarefa | `control/motor.py` e `view/relatorio.py` |
| Recurso exclusivo | `control/motor.py` |
| Herança e teto | `control/motor.py` |
| Envelhecimento de prioridade | `control/motor.py` |
| Sorteio de cenários | `control/gerador.py` |
| Comparação dos algoritmos | `control/gerador.py` |
| Execução em lote | `control/gerador.py` |
| Gravação e carregamento de cenários | `model/cenario.py` |
| Interface gráfica | `view/janela.py` |
| Diagrama de tempo | `view/relatorio.py` |

## Documentação

- [Tutorial de execução](./docs/tutorial_execucao.pdf)
- [Tutorial de uso](./docs/tutorial_uso.pdf)
- [Documentação técnica](./docs/documentacao_projeto.pdf)

## Por onde começar

1. Abra o programa e siga o tutorial de execução.
2. Reproduza um cenário de exemplo pelo tutorial de uso.
3. Consulte a documentação técnica para entender o código.
