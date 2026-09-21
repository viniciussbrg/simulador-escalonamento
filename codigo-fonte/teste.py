from tarefa import Tarefa
from politicas import fcfs, sjf, srtf, prio
from motor import simular

def cenario():
    d = [(1,0,5,2),(2,0,2,3),(3,1,4,1),(4,3,1,4),(5,5,2,5)]
    return [Tarefa(*x) for x in d]

def medias(ts):
    n = len(ts)
    return (round(sum(t.tt() for t in ts)/n, 4),
            round(sum(t.tw() for t in ts)/n, 4),
            round(sum(t.primeira_exec for t in ts)/n, 4))

esperado = {
 "FCFS":  (fcfs, False, 0, 8.0, 5.2, 5.2, 5),
 "SJF":   (sjf,  False, 0, 5.8, 3.0, 3.0, 5),
 "SRTF":  (srtf, True,  0, 5.4, 2.6, 2.4, 6),
 "PRIOc": (prio, False, 0, 6.6, 3.8, 3.8, 5),
 "PRIOp": (prio, True,  0, 5.6, 2.8, 2.2, 7),
}
print("alg    Tt     Tw     1a     trocas   esperado")
for nome,(pol,pre,ttc,eTt,eTw,e1,etr) in esperado.items():
    ts = cenario()
    r = simular(ts, pol, pre, ttc)
    Tt,Tw,P1 = medias(ts)
    ok = "OK " if (Tt==eTt and Tw==eTw and P1==e1 and r["trocas"]==etr) else "ERRO"
    print(f"{nome:6} {Tt:<6} {Tw:<6} {P1:<6} {r['trocas']:<8} {eTt}/{eTw}/{e1}/{etr}  {ok}")

# cenario 4.2: FCFS com ttc=1 -> Tt 11.0, Tw 8.2
ts = cenario()
simular(ts, fcfs, False, 1)
Tt,Tw,P1 = medias(ts)
print(f"\nFCFS ttc=1: Tt={Tt} Tw={Tw}  esperado 11.0/8.2", "OK" if (Tt==11.0 and Tw==8.2) else "ERRO")

print()
for q, c, eTt, eTw, e1, etr in [(2,0,8.4,5.6,2.8,8), (4,1,13.4,10.6,None,None)]:
    ts = cenario()
    r = simular(ts, ttc=c, tq=q)
    Tt,Tw,P1 = medias(ts)
    ok = (Tt==eTt and Tw==eTw)
    if e1 is not None:
        ok = ok and P1==e1 and r["trocas"]==etr
    print(f"RR q={q} ttc={c}: Tt={Tt} Tw={Tw} 1a={P1} trocas={r['trocas']}"
          f"  esperado {eTt}/{eTw}/{e1}/{etr}", "OK" if ok else "ERRO")

from motor import eficiencia
print(f"\nE(tq=4, ttc=1) = {eficiencia(4,1)}  esperado 0.8")
print(f"E sem quantum  = {eficiencia(None,1)}  esperado None (nao definida)")
