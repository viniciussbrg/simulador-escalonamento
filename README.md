# Simulador de Escalonamento de Tarefas

Projeto prático da disciplina de Sistemas Operacionais, ministrada por
Vinicius da Silva Borges.
Semestre: 8°.

## Como executar

Clique duas vezes em **`Simulador.exe`**, na raiz desta pasta.

Não é necessário instalar nada, montar ambiente nem digitar comando algum. O
programa abre em uma janela e toda a interação acontece dentro dela.

Se o Windows exibir um aviso de aplicativo não reconhecido, escolha
**Mais informações** e depois **Executar assim mesmo**. O executável não é
assinado digitalmente, e esse aviso é o comportamento padrão do sistema para
programas sem assinatura.

## Autoria

- Arthur Destro - [@ArthurDestro](https://github.com/ArthurDestro)
- Alex Saifi - [@Alexssn10](https://github.com/Alexssn10)
- Gustavo Mauriz - [@GuMauriz](https://github.com/GuMauriz)
- Vinicius Strazza — [@ViniciusStrazza](https://github.com/ViniciusStrazza)

## Descrição

Simulador de escalonamento de tarefas em um processador único, com tempo
discreto. Implementa os seis algoritmos estudados em sala — FCFS, SJF, SRTF,
Round-Robin, prioridade cooperativa e prioridade preemptiva — e apresenta,
por tarefa e em média, o tempo de execução, o tempo de processamento, o tempo
de espera e o tempo até a primeira execução.

O simulador trata recursos de uso exclusivo e reproduz o fenômeno da inversão
de prioridades, com os dois protocolos de correção estudados: herança de
prioridade e teto de prioridade. Implementa também o envelhecimento como
tratamento da inanição sob prioridade cooperativa. Um gerador de cenários
permite sortear conjuntos de tarefas e comparar os seis algoritmos sobre um
lote de cenários.

O programa reproduz os quatro cenários de validação do enunciado. Os valores
conferidos estão em [`testes/cenarios_referencia.json`](./testes/cenarios_referencia.json).

## Requisitos de ambiente

Para executar o `Simulador.exe`: nenhum. Ele é independente e não exige Python
instalado.

Para executar a partir do código-fonte:

- Python 3.10 ou superior (desenvolvido e testado em 3.14)
- `tkinter`, que acompanha a instalação padrão do Python no Windows

**O projeto não usa nenhuma biblioteca externa.** Todos os módulos importados
fazem parte da biblioteca padrão: `tkinter`, `json`, `os`, `sys` e `random`.

```
cd codigo-fonte
python main.py
```

O executável foi gerado com PyInstaller, a partir da pasta `codigo-fonte`:

```
python -m PyInstaller --onefile --windowed --name Simulador main.py
```

## Estrutura do repositório

```
simulador-escalonamento/
|-- README.md              este arquivo
|-- Simulador.exe          programa pronto para executar (duplo clique)
|-- codigo-fonte/          o programa em si
|-- cenarios/              conjuntos de tarefas gravados, em JSON
|-- testes/                valores de referencia do enunciado
|-- docs/                  tutoriais, documentacao tecnica e capturas
'-- documentos/            enunciado e guias da disciplina
```

## Arquivos de código

Todos em `codigo-fonte/`.

| Arquivo | O que faz |
|---|---|
| `main.py` | Ponto de entrada. Abre a janela do programa. |
| `tarefa.py` | A classe `Tarefa`: os dados de entrada de uma tarefa, o seu estado durante a simulação e o cálculo das métricas. |
| `politicas.py` | As políticas de escalonamento. Cada uma recebe o conjunto de tarefas prontas e devolve a escolhida. |
| `motor.py` | O laço de simulação, comum aos seis algoritmos: avança o relógio, monta o conjunto de prontas, cobra a troca de contexto, concede e libera o recurso, aplica herança, teto e envelhecimento, e registra as métricas. |
| `gerador.py` | Sorteio de conjuntos de tarefas, dentro das faixas válidas. |
| `comparacao.py` | A tabela dos seis algoritmos e a comparação por lote de cenários sorteados. |
| `diagrama.py` | Monta o diagrama de tempo a partir dos eventos registrados pelo motor. |
| `cenarios.py` | Gravação e leitura de conjuntos de tarefas em JSON. |
| `validacao.py` | Validação dos valores digitados, com as mensagens de recusa. |
| `interface.py` | A janela do programa, em tkinter. |

### Arquivos de teste

Também em `codigo-fonte/`. Cada um confere o simulador contra os valores do
enunciado. Rode com `python <arquivo>` de dentro da pasta.

| Arquivo | O que confere |
|---|---|
| `teste.py` | Os seis algoritmos no cenário da Aula 5, e o cenário com custo de troca. |
| `teste_r5.py` | A inversão de prioridades, tarefa por tarefa. |
| `teste_r6r7.py` | Herança e teto, incluindo o cenário em que a disputa nunca ocorre. |
| `teste_r8.py` | Inanição e envelhecimento, conferindo também a sequência de execução. |
| `teste_r9.py` | A comparação por lote e a estabilidade da ordenação entre execuções. |
| `teste_validacao.py` | A recusa de valores inválidos e a aceitação dos válidos. |
| `teste_interface.py` | A tabela de algoritmos que a interface usa. |
| `teste_diagrama.py` | O diagrama de tempo e o ciclo de gravar e recarregar. |

## Funcionalidades

| Requisito | O que faz | Onde |
|---|---|---|
| R1 | Os seis algoritmos de escalonamento | `politicas.py`, `comparacao.py` |
| R2 | Entrada de tarefas campo por campo, sorteio, gravação e recarga | `interface.py`, `gerador.py`, `cenarios.py` |
| R3 | Métricas por tarefa e em média | `tarefa.py`, `interface.py` |
| R4 | Quantum, custo da troca de contexto e eficiência | `motor.py`, `validacao.py` |
| R5 | Recurso de uso exclusivo e inversão de prioridades | `motor.py`, `tarefa.py` |
| R6 | Herança de prioridade | `motor.py` |
| R7 | Teto de prioridade | `motor.py` |
| R8 | Envelhecimento com passo configurável | `motor.py`, `tarefa.py` |
| R9 | Gerador de cenários, comparação por lote e diagrama de tempo | `gerador.py`, `comparacao.py`, `diagrama.py` |
| R10 | Execução por duplo clique | `Simulador.exe` |

A separação entre política e mecanismo é o eixo do projeto: `motor.py` contém
o único laço de simulação, e `politicas.py` contém as decisões específicas de
cada algoritmo. O motor não conhece o critério de escolha, e a política não
conhece o relógio.

## Documentação

- [Tutorial de execução](./docs/tutorial_execucao.pdf) — como colocar o
  programa para funcionar
- [Tutorial de uso](./docs/tutorial_uso.pdf) — como operar cada função
- [Documentação técnica](./docs/documentacao_projeto.pdf) — como o simulador
  funciona internamente, e as convenções de simulação adotadas

## Por onde começar

1. Abra o programa seguindo o tutorial de execução;
2. Reproduza o cenário de exemplo pelo tutorial de uso e confira os valores;
3. Consulte a documentação técnica para entender o funcionamento interno e as
   convenções que determinam os números produzidos.
