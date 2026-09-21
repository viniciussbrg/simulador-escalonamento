# Simulador de Escalonamento de Tarefas — Grupo 10

## Integrantes

* João Andrade
* Roger Rocha
* Samar Victor

## Como executar

Clique duas vezes em `Simulador.exe`.

Não é necessário instalar nada.

## Descrição

Este projeto é um simulador de algoritmos de escalonamento de processos desenvolvido em Python. Ele foi construído para reproduzir numericamente cenários de referência e expor fenômenos complexos de concorrência, como a inversão de prioridades e seus respectivos mecanismos de correção.

A arquitetura do código foi estruturada com base na separação estrita entre o mecanismo de simulação e a política de escalonamento. O sistema interage com o usuário por meio de uma interface gráfica.

## Estrutura do repositório

A entrega tem duas camadas: a raiz guarda o executável pronto e cópias dos
dados/documentação que ele usa; a pasta `simulador/` guarda o código-fonte
completo (é a partir dela que o `Simulador.exe` foi gerado).

```text
simulador-escalonamento/
├── README.md            Documentação inicial do projeto (este arquivo)
├── Simulador.exe        Executável Windows pronto (não exige Python instalado)
├── cenarios/            Cópia dos cenários de exemplo em JSON usada pelo .exe
├── docs/                Cópia dos tutoriais e da documentação técnica em PDF
└── simulador/           Código-fonte do simulador
    ├── main.py              Ponto de entrada por linha de comando
    ├── main.pyw             Ponto de entrada por duplo clique, sem console
    ├── EXECUTAR.bat         Abre o programa no Windows sem usar o terminal
    ├── EXECUTAR.command     Abre o programa no macOS/Linux sem usar o terminal
    ├── model/               Estrutura da tarefa e gravação/carregamento de cenários
    ├── control/             Mecanismo de simulação, políticas e gerador de cenários
    ├── view/                Interface gráfica e relatório de métricas/diagrama
    ├── tests/               Suíte automatizada (unittest)
    ├── cenarios/            Cenários de exemplo em JSON usados pelo código-fonte
    ├── docs/                Fonte dos tutoriais e da documentação técnica
    └── assets/icon.ico      Ícone do programa
```

## Arquivos de código

* `simulador/model/tarefa.py` — estrutura e validação de uma tarefa (ingresso, tp, prioridade, seção crítica)
* `simulador/model/cenario.py` — gravação e carregamento de cenários em JSON
* `simulador/control/motor.py` — laço de simulação (mecanismo): relógio, fila de prontas, recurso R, herança, teto, envelhecimento e métricas
* `simulador/control/politicas.py` — os seis algoritmos de escalonamento (política)
* `simulador/control/gerador.py` — sorteio de tarefas/cenários e comparação em lote
* `simulador/view/janela.py` — janela da interface gráfica (tkinter)
* `simulador/view/relatorio.py` — formatação das métricas em texto e do diagrama de tempo

## Funcionalidades

|O que faz|Onde|
|-|-|
|Os seis algoritmos|`simulador/control/politicas.py`|
|Métricas por tarefa e eficiência|`simulador/control/motor.py`|
|Recurso de uso exclusivo|`simulador/control/motor.py`|
|Herança e teto de prioridade|`simulador/control/motor.py`|
|Envelhecimento|`simulador/control/motor.py`|
|Sorteio e comparação de cenários|`simulador/control/gerador.py`|
|Gravar/carregar cenário|`simulador/model/cenario.py`|
|Interface gráfica|`simulador/view/janela.py`|

## Documentação

* [Tutorial de execução](./docs/tutorial_execucao.pdf)
* [Tutorial de uso](./docs/tutorial_uso.pdf)
* [Documentação técnica](./docs/documentacao_projeto.pdf)

## Requisitos de ambiente

* Python 3.10+
* Bibliotecas: Nenhuma biblioteca externa é necessária (apenas biblioteca padrão do Python).

## Por onde começar

1. Abra o programa e siga o tutorial de execução
2. Reproduza um cenário de exemplo pelo tutorial de uso
3. Consulte a documentação técnica para entender o código

## Uso de assistentes de programação

Os assistentes de programação foram utilizados para:

* Auxiliar na estruturação do `README.md` e da documentação técnica.
* Explicar a implementação de algoritmos específicos e mecanismos, como a herança de prioridade.
* Fornecer auxílio com o código-fonte base para o mecanismo de simulação e as políticas de escalonamento (`simulador/control/motor.py` e `simulador/control/politicas.py`).
* Fornecer auxílio com o código para a suíte de testes normativos (`simulador/tests/test\_cenarios.py` e `simulador/tests/test\_entrada.py`).
* Fornecer orientações sobre a implementação da interface com `tkinter`.

