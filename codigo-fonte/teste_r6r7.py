from tarefa import Tarefa
from politicas import prio
from motor import simular

def aula6():
    return [Tarefa(1,0,6,1,(1,4)), Tarefa(2,4,4,2),
            Tarefa(3,6,3,3), Tarefa(4,2,3,4,(1,1))]

esp = {
 None:      {1:(16,16,10), 2:(11,7,3),  3:(9,3,0),  4:(15,13,10)},
 "heranca": {1:(16,16,10), 2:(15,11,7), 3:(11,5,2), 4:(8,6,3)},
 "teto":    {1:(16,16,10), 2:(15,11,7), 3:(11,5,2), 4:(8,6,3)},
}
for prot in [None, "heranca", "teto"]:
    ts = aula6()
    simular(ts, prio, preemptivo=True, protocolo=prot)
    e = esp[prot]
    ok = all((t.conclusao, t.tt(), t.tw()) == e[t.id] for t in ts)
    Tt = round(sum(t.tt() for t in ts)/4, 2)
    Tw = round(sum(t.tw() for t in ts)/4, 2)
    nome = prot or "sem protocolo"
    print(f"{nome:14} Tt={Tt:<5} Tw={Tw:<5} tw(t4)={ts[3].tw():<3}",
          "OK" if ok else "ERRO")

print("\npreco do teto (t4 ingressa no 12, nunca disputa):")
def preco():
    return [Tarefa(1,0,6,1,(1,4)), Tarefa(2,2,3,2), Tarefa(4,12,2,4,(0,1))]
for prot, etw2, eTw in [("heranca",0,1.0), ("teto",3,2.0)]:
    ts = preco()
    simular(ts, prio, preemptivo=True, protocolo=prot)
    tw2 = ts[1].tw()
    Tw = round(sum(t.tw() for t in ts)/3, 2)
    print(f"  {prot:9} tw(t2)={tw2}  Tw={Tw}   esperado {etw2}/{eTw}",
          "OK" if (tw2 == etw2 and Tw == eTw) else "ERRO")
