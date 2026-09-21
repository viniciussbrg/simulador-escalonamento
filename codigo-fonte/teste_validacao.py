from validacao import (EntradaInvalida, inteiro, validar_quantum,
                       validar_secao_critica, ler_tarefa)

def recusa(fn, *a, **k):
    try:
        fn(*a, **k)
        return None
    except EntradaInvalida as e:
        return str(e)

casos = [
    ("vazio",            lambda: inteiro("", "Ingresso")),
    ("texto",            lambda: inteiro("abc", "Duracao")),
    ("decimal",          lambda: inteiro("2.5", "Custo")),
    ("negativo",         lambda: inteiro("-3", "Ingresso", 0)),
    ("duracao zero",     lambda: inteiro("0", "Duracao", 1)),
    ("quantum <= custo", lambda: validar_quantum(1, 1)),
    ("quantum < custo",  lambda: validar_quantum(2, 5)),
    ("sc fora da tarefa",lambda: validar_secao_critica(3, 4, 5)),
    ("tarefa sem prio",  lambda: ler_tarefa(1, "0", "5", "")),
]
print("valores invalidos recusados com mensagem:\n")
for nome, fn in casos:
    msg = recusa(fn)
    print(f"  {nome:20} {'OK  ' if msg else 'ERRO'} {msg or '<aceitou!>'}")

print("\nvalores validos aceitos:\n")
validos = [
    ("tarefa simples",   lambda: ler_tarefa(1, "0", "5", "2")),
    ("tarefa com R",     lambda: ler_tarefa(1, "0", "6", "1", "1", "4")),
    ("sc no limite",     lambda: ler_tarefa(2, "0", "5", "1", "1", "4")),
    ("quantum ok",       lambda: validar_quantum(4, 1)),
    ("custo zero",       lambda: inteiro("0", "Custo", 0)),
]
for nome, fn in validos:
    try:
        print(f"  {nome:20} OK   {fn()}")
    except EntradaInvalida as e:
        print(f"  {nome:20} ERRO recusou: {e}")
