import matplotlib.pyplot as plt

sizes = [32, 64, 128, 256, 512, 1024]
cache_refs_naive = [77694, 530156, 2706692, 29540939, 275431124, 2197862242]
cache_misses_naive = [321254, 81242, 93994, 4366617, 137871607, 1096828055]

cache_refs_opt = [317025, 515296, 2721771, 20567689, 160820039, 1284484541]
cache_misses_opt = [73991, 76300, 86849, 766773, 18951550, 121936534]

# Calcul des taux de cache-miss (%)
miss_rate_naive = [(m / r) * 100 if r != 0 else 0 for m, r in zip(cache_misses_naive, cache_refs_naive)]
miss_rate_opt = [(m / r) * 100 if r != 0 else 0 for m, r in zip(cache_misses_opt, cache_refs_opt)]

# Tracé du graphe
plt.figure(figsize=(10, 6))
plt.plot(sizes, miss_rate_naive, marker='o', label='Sans optimisation')
plt.plot(sizes, miss_rate_opt, marker='s', label='Avec cache blocking')
plt.title("Taux de cache-miss selon la taille de matrice")
plt.xlabel("Taille de matrice (M=N=K)")
plt.ylabel("Cache-miss rate (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()