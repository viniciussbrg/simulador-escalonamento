from comparacao import comparar_lote

print("lote de 50 cenarios de 5 tarefas, tq=2, ttc=0\n")
print("alg      Tt      Tw      1a exec")
medias = comparar_lote()
for nome, m in medias.items():
    print(f"{nome:7} {m['Tt']:<7.2f} {m['Tw']:<7.2f} {m['primeira']:.2f}")

menor_tw = min(medias, key=lambda n: medias[n]["Tw"])
menor_1a = min(medias, key=lambda n: medias[n]["primeira"])
print(f"\nmenor Tw: {menor_tw}  (esperado SRTF)")
print(f"menor 1a exec: {menor_1a}  (esperado RR)")

print("\nordenacao se mantem em 10 execucoes sucessivas?")
falhas = 0
for i in range(10):
    m = comparar_lote()
    a = min(m, key=lambda n: m[n]["Tw"])
    b = min(m, key=lambda n: m[n]["primeira"])
    if (a, b) != ("SRTF", "RR"):
        falhas += 1
        print(f"  execucao {i+1}: menor Tw={a}, menor 1a={b}  <-- divergiu")
print("  OK, 10/10 mantiveram a ordenacao" if falhas == 0
      else f"  {falhas} de 10 divergiram")
