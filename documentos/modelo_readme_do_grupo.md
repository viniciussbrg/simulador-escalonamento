# Simulador de Escalonamento de Tarefas — Grupo XX

> Este é o modelo do `README.md` que deve ficar na **raiz do fork do grupo**.
> Copie o conteúdo, preencha todos os campos e apague estas linhas de
> orientação antes de entregar.

## Integrantes

- Nome completo
- Nome completo
- Nome completo

## Como executar

Clique duas vezes em `Simulador.exe`.

Não é necessário instalar nada.

<!-- Se a entrega não for um executável independente, informe aqui a versão do
Python e as bibliotecas necessárias, e qual arquivo receber o duplo clique. -->

## Descrição

<!-- Um ou dois parágrafos sobre o que o simulador faz. -->

## Estrutura do repositório

```
simulador-escalonamento/
├── README.md
├── Simulador.exe
├── main.py
├── simulador/
├── cenarios/
└── docs/
```

## Arquivos de código

<!-- Uma linha por arquivo, dizendo o que ele faz. -->

- `simulador/modelo.py` — estrutura de uma tarefa
- `simulador/motor.py` — laço de simulação (mecanismo)
- `simulador/politicas.py` — os seis algoritmos (política)
- `simulador/metricas.py` — cálculo de tt, tp e tw
- `simulador/interface.py` — janela do programa

## Funcionalidades

<!-- Onde cada requisito do enunciado foi implementado. -->

| O que faz | Onde |
|-----------|------|
| Os seis algoritmos | `simulador/politicas.py` |
| Métricas por tarefa | `simulador/metricas.py` |
| Recurso de uso exclusivo | `simulador/motor.py` |
| Herança e teto | `simulador/motor.py` |
| Envelhecimento | `simulador/politicas.py` |
| Sorteio de cenários | `simulador/gerador.py` |

## Documentação

- [Tutorial de execução](./docs/tutorial_execucao.pdf)
- [Tutorial de uso](./docs/tutorial_uso.pdf)
- [Documentação técnica](./docs/documentacao_projeto.pdf)

## Requisitos de ambiente

- Python X.Y
- Bibliotecas: <!-- listar, ou informar que não há -->

## Por onde começar

1. Abra o programa e siga o tutorial de execução
2. Reproduza um cenário de exemplo pelo tutorial de uso
3. Consulte a documentação técnica para entender o código

## Uso de assistentes de programação

<!-- Declare se foram usados e em quais partes. -->
