from tarefa import Tarefa
from politicas import prio
from motor import simular

def cenario_aula6():
    return [
        Tarefa(1, 0, 6, 1, (1, 4)),
        Tarefa(2, 4, 4, 2),
        Tarefa(3, 6, 3, 3),
        Tarefa(4, 2, 3, 4, (1, 1)),
    ]

ts = cenario_aula6()
simular(ts, prio, preemptivo=True)
esp = {1:(16,16,10), 2:(11,7,3), 3:(9,3,0), 4:(15,13,10)}
print("tar  concl  tt  tw     esperado")
for t in ts:
    e = esp[t.id]
    ok = "OK " if (t.conclusao, t.tt(), t.tw()) == e else "ERRO"
    print(f"t{t.id}   {t.conclusao:<6} {t.tt():<3} {t.tw():<6} {e}  {ok}")
Tt = round(sum(t.tt() for t in ts)/4, 2)
Tw = round(sum(t.tw() for t in ts)/4, 2)
print(f"\nTt={Tt} Tw={Tw}  esperado 9.75/5.75",
      "OK" if (Tt, Tw) == (9.75, 5.75) else "ERRO")
