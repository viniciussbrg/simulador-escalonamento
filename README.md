# Simulador de Escalonamento de Tarefas

Projeto prático da disciplina de Sistemas Operacionais, do 8º semestre do curso de Engenharia de Computação, ministrada por Vinicius Borges no 2º semestre de 2026.

## Autoria
- Henrique Alves Ferreira
- Gabriel Melo Santos
- Matheus da Silva Souza
- Rafael Ruppert Barrocal

## Descrição
Simulador de escalonamento de tarefas em um processador. Implementa seis algoritmos (FCFS, SJF, SRTF, Round-Robin e prioridade cooperativa e preemptiva), trata recursos de uso exclusivo e reproduz o fenômeno da inversão de prioridades, com os mecanismos de herança e teto de prioridade. Também sorteia tarefas e lotes de cenários para comparar os algoritmos, aplica envelhecimento de prioridade para eliminar inanição, e permite salvar e recarregar um cenário em JSON.

## Como executar

### Arquivo Executável

Clique duas vezes em `Simulador.exe`.
Nao e necessario instalar nada.

### Script Python

- Requisitos:
    - Python >=3.10
    - `python-tk`
        - Windows: incluso no Python por padrão;
        - Linux e MacOS: pode ser necessário instalar via gerenciador de pacotes; 

Rode o script `main.py`:

```
python main.py
```

## Estrutura do repositório

```
simulador_escalonamento/
|-- Simulador.exe       Programa pronto para executar
|-- main.py             Ponto de entrada do codigo-fonte
|-- src/                Codigo-fonte do simulador
|-- cenarios/           Conjuntos de tarefas em JSON
`-- docs/               Tutoriais e documentacao tecnica
```

## Arquivos de código

- `src/view/` - interface gráfica
- `src/model/processo.py` - estrutura da tarefa
- `src/model/prioridade.py` - modelagem da prioridade da tarefa
- `src/control/simular_escalonamento.py` - raiz de chamada do simulador
- `src/control/motor.py` - motor de simulação
- `src/control/politicas.py` - modelagem das políticas de escalonamento
- `src/control/gerador.py` - gerador de tarefas e simulação em lotes
- `src/control/persistencia.py` - importação e exportação de tarefas em json
- `src/control/algoritmos/_base.py` - funções comuns dos algoritmos
- `src/control/algoritmos/nomes.py` - enumerador de nomes dos algoritmos
- `src/control/algoritmos/recursos.py` - funções para tratativa de uso de recursos

## Funcionalidades

| O que faz | Onde |
|-----------|------|
| Os seis algoritmos | `src/control/politicas.py`, `src/control/motor.py` |
| Métricas por tarefa | `src/model/processo.py` |
| Recurso exclusivo, herança e teto | `src/control/algoritmos/recursos.py`, `src/control/motor.py` |
| Envelhecimento de prioridade | `src/control/politicas.py`, `src/control/motor.py` |
| Sorteio de tarefas e de lotes de cenários | `src/control/gerador.py` |
| Salvar/carregar cenário | `src/control/persistencia.py` |

## Documentação

- [Tutorial de execucao](./docs/tutorial_execucao.pdf)
- [Tutorial de uso](./docs/tutorial_uso.pdf)
- [Documentacao tecnica](./docs/documentacao_projeto.pdf)

## Por onde começar

1. Abra o arquivo executável (ou clone o projeto e rode `python main.py`) e explore as abas: Tarefas, Parâmetros, Resultado e Lote de Cenários.
2. Cadastre um conjunto de tarefas (manualmente ou por sorteio) e simule com os diferentes algoritmos.
3. Consulte o código em `src/` para entender a implementação — veja "Arquivos de código" acima.
4. Consulte a documentacao tecnica para entender o codigo.
