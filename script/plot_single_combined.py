import matplotlib.pyplot as plt
import csv
import sys
import os

if len(sys.argv) < 3:
    print("Usage: python plot_single_combined.py <chemin_csv> <label_version>")
    print("Exemple : python plot_single_combined.py results_comparaison.csv naive")
    sys.exit(1)

csv_path_file = sys.argv[1]
version_label = sys.argv[2]

gflops_col = f"{version_label}_gflops"
time_col = f"{version_label}_time"

if not os.path.exists(csv_path_file):
    print(f"Fichier introuvable : {csv_path_file}")
    sys.exit(1)

sizes, gflops, times = [], [], []

with open(csv_path_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        sizes.append(int(row["size"]))
        gflops.append(float(row[gflops_col]))
        times.append(float(row[time_col]))

fig, ax1 = plt.subplots(figsize=(9, 6))
ax2 = ax1.twinx()
ax1.plot(sizes, gflops, marker='o', color='tab:blue', label='GFLOP/s')
ax2.plot(sizes, times, marker='x', linestyle='--', color='tab:red', label='Temps (s)')
ax1.set_xlabel("Taille de matrice (M=N=K)")
ax1.set_ylabel("GFLOP/s", color='tab:blue')
ax2.set_ylabel("Temps (secondes)", color='tab:red')
ax1.set_title(f"Performance combinée - {version_label}")
ax1.set_xticks(sizes)
ax1.grid(True)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

output_name = f"assets/plots/combined/plot_single_combined_{version_label}.png"
os.makedirs(os.path.dirname(output_name), exist_ok=True)
plt.tight_layout()
plt.savefig(output_name, dpi=300)
print(f"Graphe combiné sauvegardé : {output_name}")
plt.show()
