from comparacao import rodar, ALGORITMOS
from motor import eficiencia

DADOS = [(1,0,5,2,None),(2,0,2,3,None),(3,1,4,1,None),
         (4,3,1,4,None),(5,5,2,5,None)]

esperado = {"FCFS":(8.0,5.2), "RR":(8.4,5.6), "SJF":(5.8,3.0),
            "SRTF":(5.4,2.6), "PRIOc":(6.6,3.8), "PRIOp":(5.6,2.8)}

print("tabela ALGORITMOS contra o cenario 4.1 (tq=2, ttc=0):\n")
for nome in ALGORITMOS:
    r = rodar(DADOS, nome, tq=2, ttc=0)
    eTt, eTw = esperado[nome]
    ok = round(r["Tt"],4)==eTt and round(r["Tw"],4)==eTw
    e = eficiencia(2 if ALGORITMOS[nome]["usa_quantum"] else None, 0)
    rot = "nao definida" if e is None else f"{e:.3f}"
    print(f"  {nome:7} Tt={r['Tt']:<5.2f} Tw={r['Tw']:<5.2f} "
          f"E={rot:<13} {'OK' if ok else 'ERRO'}")
