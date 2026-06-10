# PSO TSP Optimizer — Jawa Barat

[![Tests](https://github.com/insanansharyrasul/PKK-Miniproject/actions/workflows/test.yml/badge.svg)](https://github.com/insanansharyrasul/PKK-Miniproject/actions/workflows/test.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red)

Implementasi akademik **Discrete Particle Swarm Optimization (PSO)** untuk menyelesaikan **Traveling Salesperson Problem (TSP)** pada data geografis nyata 27 kabupaten/kota di Jawa Barat. Dibuat sebagai proyek mata kuliah **Pengantar Kecerdasan Komputasional (KOM1326)**, IPB University.

---

## Hasil Utama

| Metode | Jarak | Waktu | vs. Greedy |
|---|---|---|---|
| Jalur Acak (avg, 50 sampel) | 2.701,19 km | — | −202,83% |
| Greedy Nearest Neighbor | 891,94 km | 2 ms | baseline |
| **Memetic PSO** | **788,08 km** | **~9,79 s** | **+11,64%** |

PSO berhasil menghemat **103,86 km** dibanding baseline Greedy dengan _seed_ 42, preset Exploitation-Heavy (`w=0.4, c1=1.0, c2=2.0`, 15 partikel), dan _early stopping_ di iterasi ke-60.

---

## Fitur

- **Perbandingan PSO vs Greedy** — rute, jarak, dan waktu komputasi secara berdampingan
- **Peta interaktif** berbasis OpenStreetMap (Plotly Mapbox)
- **Iteration Playback** — slider untuk menelusuri evolusi rute tiap iterasi
- **Auto-Tuning** — grid search 4 preset, memilih konfigurasi terbaik otomatis
- **Early stopping** — berhenti saat swarm konvergen, menghemat waktu
- **Analisis akademik** — kurva konvergensi, diversitas swarm, distribusi hop jarak
- **Upload CSV kustom** — deteksi kolom otomatis (nama/lat/long dalam berbagai format)
- **Seed control** — reprodusibilitas penuh

---

## Arsitektur

```
┌─────────────────────────────────────────────────────┐
│                   app.py (Streamlit UI)             │
│  sidebar params → render_map → render_analysis      │
└───────────────────────┬─────────────────────────────┘
                        │ calls
┌───────────────────────▼─────────────────────────────┐
│              pso_engine.py (core algorithm)         │
│                                                     │
│  load_and_filter_data()   haversine / euclidean     │
│  GreedyTSPSolver          PSOSolver                 │
│  auto_tune_pso()          evaluate_parameters()     │
└───────────────────────┬─────────────────────────────┘
                        │ uses
┌───────────────────────▼─────────────────────────────┐
│          kabupaten_kota_jawa_barat.csv               │
│          27 kabupaten/kota Jawa Barat (lat/long)    │
└─────────────────────────────────────────────────────┘
```

---

## Algoritma

### Discrete PSO dengan Swap Operator

TSP bersifat diskrit (ruang pencarian berupa permutasi), sehingga PSO kontinu standar tidak dapat diterapkan langsung. Implementasi ini menggunakan **aljabar swap operator** (Clerc, 2004):

- **Posisi** = permutasi urutan kota: `[0, 3, 1, 2, ...]`
- **Kecepatan** = barisan operasi swap: `[SO(0,3), SO(1,2)]`
- **Pembaruan kecepatan**: `V(t+1) = w·Vt + c1·r1·(Pbest − Xt) + c2·r2·(Gbest − Xt)`

### Lima Teknik Optimasi Hibrida

| # | Teknik | Efek |
|---|---|---|
| 1 | **Heuristic Seeding** | Partikel-0 diinisialisasi dengan rute Greedy → titik awal kuat |
| 2 | **Velocity Cap** `⌊N/2⌋` | Batasi panjang swap sequence → cegah perubahan posisi ekstrem |
| 3 | **Periodic 2-Opt** (tiap 5 iter, top 25%) | Eliminasi persilangan jalur secara periodik |
| 4 | **Adaptive Mutation Decay** `μt = μ0·(1−0.9·t/T)` | Eksplorasi tinggi di awal → eksploitasi di akhir |
| 5 | **Diversity-Based Partial Restart** (CoV < 1%) | Reinisialisasi 25% partikel terburuk saat swarm stagnan |

### Auto-Tuning (Grid Search 4 Preset)

| Preset | w | c1 | c2 | Partikel | Skor (27 kota) |
|---|---|---|---|---|---|
| Balanced | 0.7 | 1.5 | 1.5 | 20 | 851.61 km |
| Exploration-Heavy | 0.9 | 2.0 | 1.0 | 30 | 864.93 km |
| **Exploitation-Heavy** | **0.4** | **1.0** | **2.0** | **15** | **838.28 km ✓** |
| Lightweight | 0.6 | 1.2 | 1.2 | 10 | 851.61 km |

---

## Instalasi

**Prasyarat:** Python 3.11+

```bash
pip install -r requirements.txt
```

---

## Penggunaan

### Dashboard Streamlit

```bash
streamlit run app.py
```

Buka browser di `http://localhost:8501`.

1. Pilih jumlah kota dan metrik jarak di sidebar
2. Pilih mode **Auto-Tune** atau **Manual**
3. Klik **Run**
4. Eksplorasi peta interaktif, slider playback, dan grafik analisis

### Notebook Akademis

```bash
jupyter notebook pso_tsp_demo.ipynb
```

Jalankan **Restart & Run All** untuk mereproduksi seluruh analisis dan menyimpan gambar ke `out/`.

---

## Testing

```bash
# Engine tests (18 kasus uji)
python test_engine.py

# App smoke tests (6 kasus uji)
python test_app.py

# Lint
ruff check pso_engine.py test_engine.py test_app.py
```

CI/CD berjalan otomatis via **GitHub Actions** pada setiap push/PR ke `main`.

---

## Struktur Project

```
PKK-Miniproject/
├── app.py                          # Dashboard Streamlit
├── pso_engine.py                   # Engine algoritma PSO & Greedy
├── pso_tsp_demo.ipynb              # Notebook analisis akademis
├── test_engine.py                  # 18 unit test pso_engine
├── test_app.py                     # 6 smoke test app.py
├── draftlaporan.typ                # Paper IEEE (Typst)
├── draftlaporan.pdf                # Paper IEEE (compiled)
├── kabupaten_kota_jawa_barat.csv   # Dataset utama (27 kota)
├── kota_kab_lat_long.csv           # Dataset referensi alternatif
├── requirements.txt
├── pyproject.toml                  # Konfigurasi ruff
├── .github/
│   └── workflows/
│       └── test.yml                # CI/CD pipeline
└── out/
    ├── 01_kurva_konvergensi_pso_vs_greedy.png
    ├── 02_perbandingan_rute_greedy_vs_pso.png
    ├── 03_analisis_kinerja_pso_vs_greedy.png
    ├── 04_matriks_jarak_geografis.png
    └── 05_distribusi_panjang_langkah_rute.png
```

---

## Dataset

`kabupaten_kota_jawa_barat.csv` berisi 27 kabupaten/kota Jawa Barat dengan koordinat latitude/longitude (WGS84). Jarak dihitung menggunakan formula **Haversine** untuk akurasi geodesik di permukaan bumi.

Untuk menggunakan dataset kustom, unggah CSV melalui sidebar. Kolom yang dikenali otomatis:

| Tipe | Nama kolom yang dikenali |
|---|---|
| Nama kota | `Kabupaten_Kota`, `name`, `kota`, `city`, `wilayah` |
| Latitude | `Latitude`, `lat`, `y` |
| Longitude | `Longitude`, `long`, `lon`, `x` |

---

## Teknologi

| Library | Kegunaan |
|---|---|
| [Streamlit](https://streamlit.io) | UI framework |
| [Plotly](https://plotly.com/python/) | Visualisasi interaktif & peta |
| [NumPy](https://numpy.org) | Komputasi numerik |
| [Pandas](https://pandas.pydata.org) | Manajemen data |
| [Matplotlib / Seaborn](https://matplotlib.org) | Visualisasi statis (notebook) |
| [Ruff](https://docs.astral.sh/ruff/) | Linting |

---

## Tim

| Nama | NIM |
|---|---|
| Naufal Akmal Rizqulloh | G6401231065 |
| Adhiya Radhin Fasya | G6401231068 |
| Faiz Naufal Huda | G6401231124 |
| Insan Anshary Rasul | G6401231132 |
| Daffa Naufal Mumtaz | G6401231168 |

**Departemen Ilmu Komputer, Sekolah Sains Data, Matematika, dan Informatika — IPB University**

---

## Referensi

1. Kennedy, J. & Eberhart, R. (1995). Particle swarm optimization. *ICNN'95*, vol. 4, pp. 1942–1948.
2. Clerc, M. (2004). Discrete Particle Swarm Optimization, illustrated by the Traveling Salesman Problem. *New Optimization Techniques in Engineering*, pp. 219–239.
3. Croes, G. (1958). A method for solving traveling-salesman problems. *Operations Research*, 6(6), 791–812.
4. Yang, X.-S. (2010). *Nature-Inspired Metaheuristic Algorithms* (2nd ed.). Luniver Press.
5. Engelbrecht, A. P. (2007). *Computational Intelligence: An Introduction* (2nd ed.). Wiley.
