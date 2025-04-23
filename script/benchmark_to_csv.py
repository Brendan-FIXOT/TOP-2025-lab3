import subprocess
import time
import csv
import sys
import os
import re
from tqdm import tqdm

if len(sys.argv) < 5:
    print("Usage: python benchmark_to_combined_csv.py <chemin_exécutable> <label_version> <nb_repetitions> <right|left>")
    sys.exit(1)

executable = sys.argv[1]
version_label = sys.argv[2]
repeats = int(sys.argv[3])
layout_arg = sys.argv[4]

csv_path_name = "assets/datas/results_comparaison128-2048.csv"
sizes = [128, 192, 256, 384, 512, 768, 1024]

gflops_col = f"{version_label}_gflops"
time_col = f"{version_label}_time"

results = {}
print(f"Benchmarking version '{version_label}' ({layout_arg}) sur {repeats} répétitions...\n")
for n in tqdm(sizes, desc="Progression", unit="taille"):
    durations = []
    for _ in range(repeats):
        result = subprocess.run([executable, str(n), str(n), str(n), layout_arg], check=True, capture_output=True, text=True)
        # Extraction du temps avec une regex
        match = re.search(r"Time:\s*([0-9.]+)\s*s", result.stdout)
        durations.append(float(match.group(1)))
    duration_mean = sum(durations) / repeats    
    gflops = (2 * n**3) / duration_mean / 1e9
    results[n] = {gflops_col: round(gflops, 4), time_col: round(duration_mean, 4)}

data = {}
if os.path.exists(csv_path_name):
    with open(csv_path_name, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            size = int(row['size'])
            data[size] = row

for size in sizes:
    if size not in data:
        data[size] = {'size': size}
    data[size][gflops_col] = results[size][gflops_col]
    data[size][time_col] = results[size][time_col]

seen = set()
all_columns = ['size']
for row in data.values():
    for col in row:
        if col != 'size' and col not in seen:
            all_columns.append(col)
            seen.add(col)

os.makedirs(os.path.dirname(csv_path_name), exist_ok=True) # vérification de si le path existe
with open(csv_path_name, mode='w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=all_columns)
    writer.writeheader()
    for size in sorted(data):
        writer.writerow(data[size])

print(f"\nDonnées mises à jour dans {csv_path_name}")
