import matplotlib.pyplot as plt
import csv
import sys
import os
import re

if len(sys.argv) < 3:
    print("Usage: python plot_multi_all.py <chemin_csv> <mode> [low|high] <version1> <version2> ...")
    sys.exit(1)

csv_path_file = sys.argv[1]
mode = sys.argv[2]

remaining_args = sys.argv[3:]
size_range = "all"
if remaining_args and remaining_args[0] in ["low", "high"]:
    size_range = remaining_args.pop(0)

selected_versions = remaining_args  # Peut être vide

if not os.path.exists(csv_path_file):
    print(f"Fichier introuvable : {csv_path_file}")
    sys.exit(1)

gflops_data = {}
time_data = {}
sizes = []

with open(csv_path_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    headers = reader.fieldnames

    all_gflops_versions = [re.match(r"(.+)_gflops", h).group(1) for h in headers if h.endswith("_gflops")]
    all_time_versions = [re.match(r"(.+)_time", h).group(1) for h in headers if h.endswith("_time")]

    if not selected_versions:
        selected_versions = list(set(all_gflops_versions) & set(all_time_versions))

    for version in selected_versions:
        gflops_data[version] = []
        time_data[version] = []

    for row in reader:
        size = int(row["size"])
        if size_range == "low" and size > 128:
            continue
        if size_range == "high" and size < 64:
            continue
        sizes.append(size)
        for version in selected_versions:
            val_gf = row.get(f"{version}_gflops", "")
            gflops_data[version].append(float(val_gf) if val_gf else None)
            val_t = row.get(f"{version}_time", "")
            t = float(val_t) if val_t else None
            if size_range == "low" and t is not None:
                t *= 1000
            time_data[version].append(t)

colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

if mode == "combined":
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    for i, version in enumerate(selected_versions):
        ax1.plot(sizes, gflops_data[version], marker='o', linestyle='-', color=colors[i % len(colors)], label=f"{version} GFLOP/s")
        ax2.plot(sizes, time_data[version], marker='x', linestyle='--', color=colors[i % len(colors)], label=f"{version} Temps")
    ax1.set_xlabel("Taille de matrice (M=N=K)")
    ax1.set_ylabel("GFLOP/s", color="black")
    ax2.set_ylabel("Temps (millisecondes)" if size_range == "low" else "Temps (secondes)", color="black")
    ax1.set_title("Comparaison combinée des performances (GFLOP/s vs Temps)")
    ax1.set_xticks(sizes)
    ax1.grid(True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right")
    output_name = f"assets/plots/combined/plot_multi_combined_{os.path.splitext(os.path.basename(csv_path_file))[0]}_{size_range}.png"

elif mode == "gflops":
    plt.figure(figsize=(9, 6))
    for i, version in enumerate(selected_versions):
        if any(v is not None for v in gflops_data[version]):
            plt.plot(sizes, gflops_data[version], marker='o', linestyle='-', color=colors[i % len(colors)], label=version.capitalize())
    plt.title("Comparaison des performances - Produit matriciel")
    plt.xlabel("Taille de matrice (M=N=K)")
    plt.ylabel("GFLOP/s")
    plt.xticks(sizes)
    plt.grid(True)
    plt.legend(loc="lower right")
    plt.tight_layout()
    output_name = f"assets/plots/gflops/plot_multi_gflops_{os.path.splitext(os.path.basename(csv_path_file))[0]}_{size_range}.png"

elif mode == "time":
    plt.figure(figsize=(9, 6))
    for i, version in enumerate(selected_versions):
        if any(v is not None for v in time_data[version]):
            label = f"{version} (ms)" if size_range == "low" else f"{version} (s)"
            plt.plot(sizes, time_data[version], marker='o', linestyle='-', color=colors[i % len(colors)], label=label)
    plt.title("Temps d’exécution - Produit matriciel")
    plt.xlabel("Taille de matrice (M=N=K)")
    plt.ylabel("Temps (millisecondes)" if size_range == "low" else "Temps (secondes)")
    plt.xticks(sizes)
    plt.grid(True)
    plt.legend(loc="lower right")
    plt.tight_layout()
    output_name = f"assets/plots/time/plot_multi_times_{os.path.splitext(os.path.basename(csv_path_file))[0]}_{size_range}.png"

else:
    print("Mode invalide. Utilisez 'combined', 'gflops' ou 'time'.")
    sys.exit(1)

os.makedirs(os.path.dirname(output_name), exist_ok=True)
plt.savefig(output_name, dpi=300)
print(f"Graphe sauvegardé : {output_name}")
plt.show()
