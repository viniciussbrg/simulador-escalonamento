from tarefa import Tarefa
from politicas import prio
from motor import simular

def inanicao():
    return [Tarefa(1,0,4,1), Tarefa(2,0,2,5), Tarefa(3,2,2,5),
            Tarefa(4,4,2,5), Tarefa(5,6,2,5), Tarefa(6,8,2,5)]

esperado = [
    (0, 10, 1.67, "t2[0,2) t3[2,4) t4[4,6) t5[6,8) t6[8,10) t1[10,14)"),
    (1, 4,  2.67, "t2[0,2) t3[2,4) t1[4,8) t4[8,10) t5[10,12) t6[12,14)"),
    (2, 2,  3.00, "t2[0,2) t1[2,6) t3[6,8) t4[8,10) t5[10,12) t6[12,14)"),
]

def sequencia(linha):
    fatias, atual, ini = [], None, 0
    for instante, tid in linha:
        if tid != atual:
            if atual is not None:
                fatias.append(f"t{atual}[{ini},{instante})")
            atual, ini = tid, instante
    fatias.append(f"t{atual}[{ini},{linha[-1][0]+1})")
    return " ".join(fatias)

for alfa, etw1, eTw, eseq in esperado:
    ts = inanicao()
    r = simular(ts, prio, preemptivo=False, alfa=alfa)
    tw1 = ts[0].tw()
    Tw = round(sum(t.tw() for t in ts)/6, 2)
    seq = sequencia(r["linha_do_tempo"])
    ok = (tw1 == etw1 and Tw == eTw and seq == eseq)
    print(f"alfa={alfa}: tw(t1)={tw1} Tw={Tw}  esperado {etw1}/{eTw}",
          "OK" if ok else "ERRO")
    print(f"   {seq}")
    if seq != eseq:
        print(f"   esperado: {eseq}")
