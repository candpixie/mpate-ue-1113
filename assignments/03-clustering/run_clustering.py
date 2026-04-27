import os
import librosa
import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for saving plots
import matplotlib.pyplot as plt
import sklearn
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore")

# path to the songs folder
song_folder = "./Songs"

song_files = sorted(os.listdir(song_folder))
file_ext = ['.mp3', '.wav', '.aiff']
song_files = [file for file in song_files if any(file.endswith(ext) for ext in file_ext)]

print(f"Found {len(song_files)} tracks:")
for f in song_files:
    print(f"  - {f}")

features = []
for song_file in song_files:
    song_path = os.path.join(song_folder, song_file)
    print(f"\nProcessing: {song_file}...")
    y, sr = librosa.load(song_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=y))
    rms = np.mean(librosa.feature.rms(y=y))
    print(f"  Tempo: {tempo:.1f} BPM | Spectral Flatness: {spectral_flatness:.6f} | RMS: {rms:.4f}")
    features.append([tempo, spectral_flatness, rms])

features = np.array(features)

# Scale features
min_max_scaler = sklearn.preprocessing.MinMaxScaler(feature_range=(0, 1))
features_scaled = min_max_scaler.fit_transform(features)

# --- Elbow method to find optimal K ---
print("\n--- Elbow Method ---")
inertias = []
K_range = range(2, 7)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=0, n_init=10).fit(features_scaled)
    inertias.append(km.inertia_)
    print(f"  K={k}: inertia={km.inertia_:.4f}")

fig_elbow, ax_elbow = plt.subplots(figsize=(8, 5))
ax_elbow.plot(list(K_range), inertias, 'bo-')
ax_elbow.set_xlabel('Number of Clusters (K)')
ax_elbow.set_ylabel('Inertia')
ax_elbow.set_title('Elbow Method for Optimal K')
fig_elbow.savefig('elbow_plot.png', dpi=150, bbox_inches='tight')
print("Saved elbow_plot.png")

# --- K=3 clustering ---
OPTIMAL_K = 3
kmeans = KMeans(n_clusters=OPTIMAL_K, random_state=0, n_init=10).fit(features_scaled)
labels = kmeans.labels_

print(f"\n--- K-Means Clusters (K={OPTIMAL_K}) ---")
for i in range(OPTIMAL_K):
    cluster_songs = np.array(song_files)[labels == i]
    print(f"\nCluster {i+1}:")
    for s in cluster_songs:
        print(f"  - {s}")

# --- 3D scatter plot with labels ---
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

color_map = {0: 'red', 1: 'blue', 2: 'green'}
colors = [color_map[l] for l in labels]

ax.scatter(features_scaled[:, 0], features_scaled[:, 2], features_scaled[:, 1],
           c=colors, s=100, edgecolors='black', linewidths=0.5)

# Add song name labels to each point
for idx, song in enumerate(song_files):
    name = song.rsplit('.', 1)[0]  # remove extension
    ax.text(features_scaled[idx, 0], features_scaled[idx, 2], features_scaled[idx, 1] + 0.03,
            name, fontsize=7, ha='center')

ax.set_xlabel('Tempo')
ax.set_ylabel('Average RMS')
ax.set_zlabel('Average Spectral Flatness')
ax.set_title(f'K-Means Clustering (K={OPTIMAL_K})')

# Legend
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map[i],
                          markersize=10, label=f'Cluster {i+1}') for i in range(OPTIMAL_K)]
ax.legend(handles=legend_elements, loc='upper left')

fig.savefig('cluster_3d_plot.png', dpi=150, bbox_inches='tight')
print("\nSaved cluster_3d_plot.png")

# --- Raw feature table ---
print("\n--- Raw Feature Table ---")
print(f"{'Track':<30} {'Tempo':>8} {'Spec.Flat':>12} {'RMS':>8} {'Cluster':>8}")
print("-" * 70)
for idx, song in enumerate(song_files):
    name = song.rsplit('.', 1)[0]
    print(f"{name:<30} {features[idx,0]:>8.1f} {features[idx,1]:>12.6f} {features[idx,2]:>8.4f} {labels[idx]+1:>8}")

print("\nDone! Screenshots ready: cluster_3d_plot.png and elbow_plot.png")
