# PSO TSP Optimizer — Jawa Barat

Aplikasi demo akademik untuk memvisualisasikan penyelesaian **Traveling Salesman Problem (TSP)** menggunakan **Discrete Particle Swarm Optimization (PSO)** pada data geografis kota/kabupaten Jawa Barat.

## Fitur

- Perbandingan rute **PSO vs Greedy (Nearest Neighbor)**
- Peta interaktif berbasis OpenStreetMap
- **Iteration Playback** — slider untuk melihat evolusi rute tiap iterasi
- Grafik konvergensi dan diversitas swarm
- **Auto-Tuning** parameter PSO (grid search 4 preset)
- Early stopping otomatis saat konvergensi tercapai
- Analisis performa akademik lengkap

## Instalasi

```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```bash
streamlit run app.py
```

Buka browser di `http://localhost:8501`.

## Cara Pakai

1. Atur jumlah kota dan metrik jarak di sidebar
2. Pilih mode parameter: **Auto-Tune** atau **Manual**
3. Klik **Run Optimasi TSP**
4. Eksplorasi peta interaktif dan grafik analisis

## Dataset

- `kabupaten_kota_jawa_barat.csv` — 27 kabupaten/kota Jawa Barat dengan koordinat lat/long
- `kota_kab_lat_long.csv` — Data koordinat referensi alternatif

## Struktur Project

```
├── app.py              # UI Streamlit
├── pso_engine.py       # Engine algoritma PSO & Greedy
├── kabupaten_kota_jawa_barat.csv
├── kota_kab_lat_long.csv
├── requirements.txt
└── out/                # Output visualisasi statis
```

## Teknologi

- **Streamlit** — UI framework
- **Plotly** — Visualisasi interaktif
- **NumPy / Pandas** — Komputasi numerik & data

## Referensi Algoritma

- Kennedy & Eberhart (1995) — Particle Swarm Optimization
- Discrete PSO untuk TSP: representasi permutasi dengan operator swap sequence
- 2-opt local search sebagai memetic enhancement
