import matplotlib.pyplot as plt
import csv
import sys
import os

if len(sys.argv) < 3:
    print("Usage: python plot_single_time.py <chemin_csv> <label_version>")
    print("Exemple : python plot_single_time.py results_comparaison.csv naive")
    sys.exit(1)

csv_path_file = sys.argv[1]
version_label = sys.argv[2]

time_col = f"{version_label}_time"

if not os.path.exists(csv_path_file):
    print(f"Fichier introuvable : {csv_path_file}")
    sys.exit(1)

sizes, times = [], []

with open(csv_path_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        sizes.append(int(row["size"]))
        val = row[time_col]
        times.append(float(val) if val else None)

plt.figure(figsize=(9, 6))
plt.plot(sizes, times, marker='o', color='tab:red', label=f"{version_label} (s)")
plt.title(f"Temps d'exécution - Version '{version_label}'")
plt.xlabel("Taille de matrice (M=N=K)")
plt.ylabel("Temps (secondes)")
plt.xticks(sizes)
plt.grid(True)
plt.legend()
plt.tight_layout()

output_name = f"assets/plots/time/plot_single_time_{version_label}.png"
os.makedirs(os.path.dirname(output_name), exist_ok=True)
plt.savefig(output_name, dpi=300)
print(f"Graphe sauvegardé : {output_name}")
plt.show()
