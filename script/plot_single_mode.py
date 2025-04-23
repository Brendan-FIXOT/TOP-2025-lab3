import matplotlib.pyplot as plt
import csv
import sys
import os

if len(sys.argv) < 4:
    print("Usage: python plot_single_all.py <chemin_csv> <label_version> <mode> [low|high]")
    sys.exit(1)

csv_path_file = sys.argv[1]
version_label = sys.argv[2]
mode = sys.argv[3]
size_range = sys.argv[4] if len(sys.argv) >= 5 else "all"

gflops_col = f"{version_label}_gflops"
time_col = f"{version_label}_time"

if not os.path.exists(csv_path_file):
    print(f"Fichier introuvable : {csv_path_file}")
    sys.exit(1)

sizes, gflops, times = [], [], []

with open(csv_path_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        size = int(row["size"])
        if size_range == "low" and size > 128:
            continue
        if size_range == "high" and size < 64:
            continue
        sizes.append(size)
        gflops.append(float(row[gflops_col]) if gflops_col in row and row[gflops_col] else None)
        t = float(row[time_col]) if time_col in row and row[time_col] else None
        if size_range == "low" and t is not None:
            t *= 1000  # conversion en ms si low
        times.append(t)

if mode == "combined":
    fig, ax1 = plt.subplots(figsize=(9, 6))
    ax2 = ax1.twinx()
    ax1.plot(sizes, gflops, marker='o', color='tab:blue', label='GFLOP/s')
    ax2.plot(sizes, times, marker='x', linestyle='--', color='tab:red', label='Temps (ms)' if size_range == "low" else 'Temps (s)')
    ax1.set_xlabel("Taille de matrice (M=N=K)")
    ax1.set_ylabel("GFLOP/s", color='tab:blue')
    ax2.set_ylabel("Temps (millisecondes)" if size_range == "low" else "Temps (secondes)", color='tab:red')
    ax1.set_title(f"Performance combinée - {version_label}")
    ax1.set_xticks(sizes)
    ax1.grid(True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    output_name = f"assets/plots/combined/plot_single_combined_{version_label}_{size_range}.png"
elif mode == "gflops":
    plt.figure(figsize=(9, 6))
    plt.plot(sizes, gflops, marker='o', color='tab:blue', label=version_label)
    plt.title(f"Performance GFLOP/s - Version '{version_label}'")
    plt.xlabel("Taille de matrice (M=N=K)")
    plt.ylabel("GFLOP/s")
    plt.xticks(sizes)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    output_name = f"assets/plots/gflops/plot_single_gflops_{version_label}_{size_range}.png"
elif mode == "time":
    plt.figure(figsize=(9, 6))
    plt.plot(sizes, times, marker='o', color='tab:red', label=f"{version_label} ({'ms' if size_range == 'low' else 's'})")
    plt.title(f"Temps d'exécution - Version '{version_label}'")
    plt.xlabel("Taille de matrice (M=N=K)")
    plt.ylabel("Temps (millisecondes)" if size_range == "low" else "Temps (secondes)")
    plt.xticks(sizes)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    output_name = f"assets/plots/time/plot_single_time_{version_label}_{size_range}.png"
else:
    print("Mode invalide. Utilisez 'combined', 'gflops' ou 'time'.")
    sys.exit(1)

os.makedirs(os.path.dirname(output_name), exist_ok=True)
plt.savefig(output_name, dpi=300)
print(f"Graphe sauvegardé : {output_name}")
plt.show()
