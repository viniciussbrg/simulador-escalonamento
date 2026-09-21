import os, tempfile
from tarefa import Tarefa
from politicas import prio, fcfs
from motor import simular
from diagrama import diagrama_de_tempo
import cenarios

def aula6():
    return [Tarefa(1,0,6,1,(1,4)), Tarefa(2,4,4,2),
            Tarefa(3,6,3,3), Tarefa(4,2,3,4,(1,1))]

for prot in [None, "heranca", "teto"]:
    ts = aula6()
    r = simular(ts, prio, preemptivo=True, protocolo=prot)
    print(f"=== PRIOp, protocolo = {prot} ===")
    print(diagrama_de_tempo(ts, r["eventos"]).split("\n\n")[0])
    print()

print("=== RR q=2 ttc=1 (mostra as trocas de contexto) ===")
ts = [Tarefa(1,0,5,2), Tarefa(2,0,2,3), Tarefa(3,1,4,1)]
r = simular(ts, ttc=1, tq=2)
print(diagrama_de_tempo(ts, r["eventos"]))

print("\n=== gravar e recarregar ===")
dados = [(1,0,5,2,None), (2,0,6,1,(1,4))]
caminho = os.path.join(tempfile.gettempdir(), "cenario_teste.json")
cenarios.gravar(caminho, dados, tq=2, ttc=1, alfa=3)
voltou, params = cenarios.carregar(caminho)
print("dados iguais :", voltou == dados)
print("parametros   :", params)
print("conteudo do arquivo:")
print(open(caminho, encoding="utf-8").read())
