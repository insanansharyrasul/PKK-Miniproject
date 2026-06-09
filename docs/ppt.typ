#import "@preview/touying:0.6.3": *
#import "@preview/simple-inria-touying-theme:0.1.2": *

#show: inria-theme.with(
  aspect-ratio: "16-9",
  config-info(
    title: [Penerapan Discrete PSO untuk\ Traveling Salesman Problem],
    subtitle: [Memetic PSO dengan Greedy Seeding dan 2-Opt Local Search],
    author: [Insan Anshari Rasul],
    date: datetime.today(),
  ),
  footer-progress: true,
  section-slides: true,
  black-title: true,
)

#title-slide()


// ══════════════════════════════════════════════════════════════
//  SECTION 1 — LATAR BELAKANG
// ══════════════════════════════════════════════════════════════

= Latar Belakang <touying:hidden>
#new-section-slide([Latar Belakang])

= Traveling Salesperson Problem (TSP)

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Definisi Masalah
    Cari *Hamiltonian Cycle* terpendek yang mengunjungi $N$ kota masing-masing *tepat satu kali*, lalu kembali ke kota asal.

    $
    min sum_(i=0)^(N-1) d lr((r_i,, r_((i+1) mod N)))
    $

    === Mengapa Sulit?
    TSP termasuk *NP-Hard*. Kompleksitas faktorial membuat pencarian eksak tidak layak untuk $N$ besar.

    #v(0.5em)
    Untuk 27 kota Jawa Barat:\
    $27! approx 1.08 times 10^(28)$ kemungkinan rute.
  ],
  [
    #v(0.5em)
    #table(
      columns: (1fr, 1.5fr, 1.5fr),
      stroke: 0.5pt + luma(170),
      align: (center, center, center),
      fill: (_, row) => if row == 4 { blue.lighten(80%) } else if calc.odd(row) { luma(245) } else { white },
      [*N Kota*], [*Rute Mungkin*], [*Waktu A\**],
      [10], [$3.6 times 10^6$], [< 1 ms],
      [15], [$1.3 times 10^(12)$], [> 1 jam],
      [20], [$2.4 times 10^(18)$], [tidak layak],
      [*27*], [$bold(1.1 times 10^(28))$], [*mustahil*],
    )

    #v(0.7em)
    #rect(
      fill: blue.lighten(85%),
      stroke: blue.lighten(40%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      #text(size: 0.88em)[*Solusi Praktis:* Gunakan algoritma _metaheuristik_ seperti PSO untuk menemukan rute yang "cukup baik" dalam waktu komputasi yang wajar.]
    ]
  ],
)

= Motivasi: Mengapa PSO?

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Perbandingan Pendekatan

    #table(
      columns: (1.5fr, 2.5fr, 1.5fr),
      stroke: 0.5pt + luma(170),
      align: (left, left, center),
      fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
      [*Metode*], [*Karakteristik*], [*Kelayakan*],
      [Brute Force], [Eksak, semua rute], [Tidak],
      [A\* / B&B], [Eksak + pruning], [$N < 15$],
      [Greedy NN], [Cepat, lokal saja], [Suboptimal],
      [*PSO*], [*Global, kolaboratif*], [*Ya ✓*],
    )

    #v(0.6em)
    PSO terinspirasi perilaku kawanan burung atau sekolah ikan dalam menemukan sumber makanan secara kolektif.
  ],
  [
    === Keunggulan PSO untuk TSP

    #set list(marker: [•])
    - *Eksplorasi global*: menghindari jebakan optimum lokal
    - *Pembelajaran kolektif*: partikel berbagi informasi tentang solusi terbaik yang pernah ditemukan (_gbest_)
    - *Adaptif*: parameter dapat di-_tune_ otomatis
    - *Hibridisasi mudah*: dapat digabungkan dengan 2-opt local search (_Memetic PSO_)

    #v(0.5em)
    #rect(
      fill: green.lighten(85%),
      stroke: green.lighten(40%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      #text(size: 0.88em)[Tujuan proyek ini: mengimplementasikan *Memetic PSO* untuk TSP rill di 27 kab/kota Jawa Barat dengan dashboard interaktif Streamlit.]
    ]
  ],
)


// ══════════════════════════════════════════════════════════════
//  SECTION 2 — LANDASAN TEORI
// ══════════════════════════════════════════════════════════════

= Landasan Teori <touying:hidden>
#new-section-slide([Landasan Teori])

= Particle Swarm Optimization (PSO)

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Inspirasi Biologis
    Kennedy & Eberhart (1995) meniru perilaku sosial kawanan burung. Setiap *partikel* merepresentasikan satu solusi kandidat dan bergerak di ruang pencarian berdasarkan:

    - *pbest* — posisi terbaik pribadi partikel
    - *gbest* — posisi terbaik dari seluruh kawanan

    === Persamaan Update (Kontinu)

    $
    V_(t+1) = underbrace(w V_t, "inersia") + underbrace(c_1 r_1 (P_"best" - X_t), "kognitif") + underbrace(c_2 r_2 (G_"best" - X_t), "sosial")
    $

    $
    X_(t+1) = X_t + V_(t+1)
    $
  ],
  [
    === Peran Parameter PSO

    #table(
      columns: (1.2fr, 2.8fr),
      stroke: 0.5pt + luma(170),
      align: (center, left),
      fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
      [*Param*], [*Fungsi*],
      [$w$], [Bobot inersia — kontrol keseimbangan eksplorasi vs. eksploitasi],
      [$c_1$], [Koefisien kognitif — daya tarik ke rute terbaik pribadi (_pbest_)],
      [$c_2$], [Koefisien sosial — daya tarik ke rute terbaik global (_gbest_)],
      [$r_1, r_2$], [Bilangan acak $in [0, 1]$ — menjaga stokastisitas pencarian],
    )

    #v(0.5em)
    #rect(
      fill: orange.lighten(85%),
      stroke: orange.lighten(40%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      #text(size: 0.88em)[*Masalah:* TSP bersifat *diskrit* (permutasi kota). Operasi aritmatika vektor standar tidak dapat diterapkan langsung.]
    ]
  ],
)

= Discrete PSO — Swap Operator

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Representasi Diskrit

    Karena TSP adalah masalah permutasi, kita adaptasi PSO menggunakan *aljabar swap*:

    #v(0.3em)
    #table(
      columns: (1.2fr, 2.8fr),
      stroke: 0.5pt + luma(170),
      align: (center, left),
      fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
      [*Konsep*], [*Representasi*],
      [Posisi $X$], [Permutasi indeks kota: `[0, 3, 1, 2, ...]`],
      [Velocity $V$], [Barisan swap operations: `[SO(0,3), SO(1,2)]`],
      [$X_2 - X_1$], [Swap sequence yang mengubah rute $X_1 → X_2$],
      [$p dot V$], [Pertahankan setiap swap dengan probabilitas $p$],
      [$X + V$], [Terapkan barisan swap pada permutasi $X$],
    )
  ],
  [
    === Pembaruan Kecepatan (Diskrit)

    $
    V_(t+1) = & [w dot V_t]\
              & + [c_1 r_1 dot (P_"best" - X_t)]\
              & + [c_2 r_2 dot (G_"best" - X_t)]
    $

    $
    X_(t+1) = X_t + V_(t+1)
    $

    #v(0.5em)
    === Contoh Swap Operation SO(1, 3)
    #table(
      columns: (1fr, 1fr),
      stroke: 0.5pt + luma(170),
      align: center,
      [*Sebelum*], [*Sesudah*],
      [`[0, 3, 1, 2]`], [`[0, 2, 1, 3]`],
    )

    #v(0.4em)
    Jika $r < p$: swap dipertahankan (bergerak ke target)\
    Jika $r >= p$: swap dibuang (eksplorasi bebas)
  ],
)

= Haversine Distance

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Formula Haversine

    Jarak geodesik antara dua titik di permukaan bumi:

    $
    a = sin^2 lr((frac(Delta phi, 2))) + cos phi_1 dot cos phi_2 dot sin^2 lr((frac(Delta lambda, 2)))
    $

    $
    c = 2 dot arcsin(sqrt(a))
    $

    $
    d = R dot c quad (R = 6371 "km")
    $

    di mana $phi$ = latitude, $lambda$ = longitude.
  ],
  [
    === Mengapa Haversine?

    #set list(marker: [•])
    - Bumi tidak rata — Euclidean tidak akurat untuk jarak > 50 km
    - Haversine memperhitungkan kelengkungan permukaan bumi
    - Menghasilkan jarak dalam *kilometer* yang akurat secara geografis

    #v(0.5em)
    #table(
      columns: (2fr, 1.5fr, 1.5fr),
      stroke: 0.5pt + luma(170),
      align: (left, center, center),
      fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
      [*Rute*], [*Euclidean*], [*Haversine*],
      [Bandung → Cirebon], [~1.76 °], [~157 km],
      [Depok → Garut], [~1.11 °], [~129 km],
      [Bekasi → Tasikmalaya], [~1.83 °], [~208 km],
    )
  ],
)


// ══════════════════════════════════════════════════════════════
//  SECTION 3 — METODOLOGI
// ══════════════════════════════════════════════════════════════

= Metodologi <touying:hidden>
#new-section-slide([Metodologi Penelitian])

= Dataset dan Pipeline Sistem

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Dataset: 27 Kab/Kota Jawa Barat
    - Sumber: `kabupaten_kota_jawa_barat.csv`
    - Kolom: `Kabupaten_Kota`, `Latitude`, `Longitude`
    - Cakupan: dari Depok (Barat) hingga Ciamis (Timur)

    === Pipeline Sistem

    #rect(
      fill: blue.lighten(92%),
      stroke: blue.lighten(55%),
      radius: 5pt,
      inset: 0.8em,
      width: 100%,
    )[
      #set text(size: 0.87em)
      *CSV Input* → Validasi & Cleaning → Seleksi 27 Kota\
      → *Greedy Seeding* (rute awal)\
      → *PSO Initialization* (swarm 20 partikel)\
      → *Optimization Loop* (kecepatan swap + 2-opt)\
      → *Early Stopping* → *Best Route* → Visualisasi
    ]
  ],
  [
    #set text(size: 0.78em)
    #table(
      columns: (0.5fr, 1.8fr, 1fr, 1fr),
      stroke: 0.5pt + luma(170),
      align: (center, left, center, center),
      fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
      [*No*], [*Kota / Kabupaten*], [*Lat*], [*Long*],
      [1], [Bandung], [-7.064], [107.634],
      [2], [Bandung Barat], [-6.905], [107.412],
      [3], [Banjar], [-7.381], [108.561],
      [4], [Bekasi], [-6.198], [107.160],
      [5], [Bogor], [-6.545], [107.002],
      [6], [Ciamis], [-7.438], [108.645],
      [7], [Cianjur], [-7.054], [107.069],
      [8], [Cimahi], [-6.882], [107.545],
      [9], [Cirebon], [-6.761], [108.456],
      [10], [Depok], [-6.388], [106.816],
      [⋮], [⋮ (17 kota lainnya)], [⋮], [⋮],
      [27], [Waduk Cirata], [-6.755], [107.286],
    )
  ],
)

= Algoritma Greedy Nearest Neighbor

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Cara Kerja Greedy NN

    Mulai dari kota indeks 0, pilih kota terdekat berikutnya yang belum dikunjungi secara berulang:

    $
    v_"next" = arg min_(u in "Unvisited") d(v_"current",, u)
    $

    Ulangi sampai semua kota terkunjungi, lalu kembali ke kota awal.

    === Kompleksitas
    - Waktu: $O(N^2)$ — sangat cepat
    - Hasil: *2.0 ms* untuk 27 kota

    === Kelemahan
    Karena selalu memilih opsi terbaik secara *lokal*, Greedy sering menyisakan kota-kota yang berjauhan di akhir rute, menciptakan "lompatan balik" yang sangat panjang.
  ],
  [
    === Peran dalam Sistem

    Greedy NN berfungsi sebagai:

    1. *Baseline* pembanding performa PSO
    2. *Heuristic Seed* untuk partikel ke-0 PSO

    #v(0.5em)
    #rect(
      fill: red.lighten(88%),
      stroke: red.lighten(50%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      *Contoh kegagalan Greedy:* Setelah mengunjungi kota-kota di barat Jawa Barat, kota-kota timur (Ciamis, Banjar) yang tersisa memaksa rute balik yang sangat jauh.
    ]

    #v(0.5em)
    #rect(
      fill: green.lighten(88%),
      stroke: green.lighten(50%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      Dengan *seeding*, PSO dimulai dari Greedy route (891.94 km) — bukan dari permutasi acak — sehingga konvergensi lebih cepat dan terukur.
    ]
  ],
)

= Algoritma Memetic PSO (Hibrida)

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Tiga Komponen Hybrid

    *1. Greedy Seeding*\
    Partikel ke-0 disemai dengan rute Greedy NN. Menjamin _gbest_ awal ≠ acak.

    #v(0.4em)
    *2. 2-Opt Local Search*\
    Setiap kali partikel menemukan _gbest_ baru, operasi 2-opt membalik sub-rute untuk menghilangkan persilangan jalur:
    $
    "Rute Baru" = [r_1, ..., r_(i-1), r_j, ..., r_i, r_(j+1), ...]
    $

    #v(0.4em)
    *3. Early Stopping*\
    Hentikan loop jika _gbest_ tidak membaik selama $K$ iterasi berturut-turut (default $K = 20$).
  ],
  [
    === Parameter PSO (4 Preset)

    #table(
      columns: (2fr, 1fr, 1fr, 1fr, 0.8fr),
      stroke: 0.5pt + luma(170),
      align: (left, center, center, center, center),
      fill: (_, row) => if row == 1 { blue.lighten(80%) } else if calc.odd(row) { luma(245) } else { white },
      [*Preset*], [*w*], [*c₁*], [*c₂*], [*N*],
      [Balanced ★], [0.7], [1.5], [1.5], [20],
      [Exploration], [0.9], [2.0], [1.0], [30],
      [Exploitation], [0.4], [1.0], [2.0], [15],
      [Lightweight], [0.6], [1.2], [1.2], [10],
    )

    #v(0.5em)
    *Auto-Tuning*: sistem menjalankan grid search dengan 3 _trial_ per preset, memilih konfigurasi dengan *jarak rute akhir terkecil*.

    #v(0.3em)
    _Preset "Balanced" dipilih dalam eksperimen utama._
  ],
)


// ══════════════════════════════════════════════════════════════
//  SECTION 4 — IMPLEMENTASI
// ══════════════════════════════════════════════════════════════

= Implementasi <touying:hidden>
#new-section-slide([Implementasi Sistem])

= Arsitektur dan Komponen Sistem

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Komponen Utama

    #table(
      columns: (1.5fr, 2.5fr),
      stroke: 0.5pt + luma(170),
      align: (left, left),
      fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
      [*File*], [*Fungsi*],
      [`pso_engine.py`], [Mesin PSO berbasis OOP: data loading, Greedy solver, Discrete PSO + 2-opt, Auto-Tuning],
      [`app.py`], [Dashboard Streamlit: peta Plotly interaktif, grafik konvergensi, iteration playback slider],
      [`pso_tsp_demo.ipynb`], [Notebook analisis akademis: Matplotlib, Seaborn, heatmap, distribusi hop],
    )

    === Kelas OOP Utama
    - `GreedyTSPSolver` — baseline nearest neighbor
    - `Particle` — satu partikel swarm (posisi + velocity)
    - `PSOSolver` — loop optimasi + 2-opt + early stopping
    - `auto_tune_pso()` — grid search 4 preset

    === Tech Stack
    Python 3 · NumPy · Pandas · Streamlit · Plotly · Matplotlib · Seaborn
  ],
  [
    === Fitur Dashboard Streamlit

    #rect(
      fill: blue.lighten(90%),
      stroke: blue.lighten(55%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      *Sidebar Controls:*\
      • Slider jumlah kota (5–27)\
      • Metrik jarak (Haversine / Euclidean)\
      • Mode Auto-Tune / Manual PSO\
      • Early stopping toggle
    ]

    #v(0.5em)
    #rect(
      fill: green.lighten(88%),
      stroke: green.lighten(50%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      *Main Panel:*\
      • Peta interaktif PSO vs. Greedy (OpenStreetMap)\
      • Metrik jarak & persentase efisiensi\
      • Grafik konvergensi real-time\
      • *Iteration playback slider* — lihat evolusi rute per iterasi\
      • Tabel perbandingan & analisis performa
    ]
  ],
)

= Implementasi Swap Operator (Kode)

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === get\_swap\_sequence()

    ```python
    def get_swap_sequence(route1, route2):
        """Hasilkan daftar SwapOp yang mengubah
           route1 menjadi route2."""
        temp = list(route1)
        sequence = []
        for idx in range(len(route2)):
            if temp[idx] != route2[idx]:
                val = route2[idx]
                swap_idx = temp.index(val)
                sequence.append(SwapOperation(idx, swap_idx))
                temp[idx], temp[swap_idx] = \
                    temp[swap_idx], temp[idx]
        return sequence
    ```

    ```python
    def scale_velocity(swap_seq, p):
        """Pertahankan setiap swap dengan prob p."""
        return [s for s in swap_seq
                if random.random() < p]
    ```
  ],
  [
    === Particle.update\_position()

    ```python
    def update_position(self, gbest, w, c1, c2):
        # Cognitive: menuju pbest
        cog = get_swap_sequence(
            self.position, self.best_position)
        cog_vel = scale_velocity(cog, c1 * random())

        # Social: menuju gbest
        soc = get_swap_sequence(
            self.position, gbest)
        soc_vel = scale_velocity(soc, c2 * random())

        # Inertia: pertahankan kecepatan lama
        inertia = scale_velocity(self.velocity, w)

        self.velocity = inertia + cog_vel + soc_vel
        self.position = apply_velocity(
            self.position, self.velocity)
    ```
  ],
)


// ══════════════════════════════════════════════════════════════
//  SECTION 5 — HASIL DAN DISKUSI
// ══════════════════════════════════════════════════════════════

= Hasil dan Diskusi <touying:hidden>
#new-section-slide([Hasil dan Diskusi])

= Perbandingan Efisiensi Rute

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Rangkuman Eksperimen

    *Konfigurasi:* $w=0.7$, $c_1=1.5$, $c_2=1.5$, 20 partikel, maks. 150 iterasi, _seed_ = 42.

    #v(0.4em)
    #table(
      columns: (2fr, 1.5fr, 1.2fr, 1.2fr),
      stroke: 0.5pt + luma(170),
      align: (left, center, center, center),
      fill: (_, row) => if row == 3 { blue.lighten(80%) } else if calc.odd(row) { luma(245) } else { white },
      [*Metode*], [*Jarak (km)*], [*Efisiensi*], [*Waktu*],
      [Jalur Acak], [3120.40], [−250%], [N/A],
      [Greedy NN], [891.94], [Baseline], [2.0 ms],
      [*Memetic PSO*], [*864.93*], [*+3.03%*], [*140 ms*],
    )

    #v(0.5em)
    === Analisis

    Memetic PSO memotong rute *27.01 km* (3.03%) di bawah Greedy. Greedy gagal karena *greedy choice property*: tanpa memandang dampak jangka panjang, kota-kota terjauh terpaksa dikunjungi via lompatan rute yang sangat panjang di akhir.
  ],
  [
    === Visualisasi Perbandingan Jarak

    #v(0.6em)
    #rect(
      fill: luma(247),
      stroke: luma(200),
      radius: 5pt,
      inset: 1em,
      width: 100%,
    )[
      #set text(size: 0.82em)
      #grid(
        columns: (2.5fr, 4.5fr, 2fr),
        row-gutter: 0.45em,
        align: (right, left, left),
        [Jalur Acak], rect(width: 100%, height: 0.9em, fill: luma(180), radius: 2pt)[], [3120 km],
        [], [], [],
        [Greedy NN], rect(width: 28.6%, height: 0.9em, fill: rgb("#ef4444"), radius: 2pt)[], [891.94 km],
        [], [], [],
        [*Memetic PSO*], rect(width: 27.7%, height: 0.9em, fill: rgb("#2563eb"), radius: 2pt)[], [*864.93 km ✓*],
      )
    ]

    #v(0.5em)
    #rect(
      fill: green.lighten(85%),
      stroke: green.lighten(40%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      #text(size: 0.88em)[*Kunci keunggulan PSO:* Eksplorasi global + 2-opt lokal menghilangkan persilangan jalur yang dibiarkan oleh Greedy. Swarm berkolaborasi menemukan rute tanpa "lompatan balik" jauh.]
    ]
  ],
)

= Analisis Waktu Komputasi dan Konvergensi

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Trade-off Waktu vs. Kualitas

    #table(
      columns: (2fr, 1.5fr, 2fr),
      stroke: 0.5pt + luma(170),
      align: (left, center, center),
      fill: (_, row) => if calc.odd(row) { luma(245) } else { white },
      [*Solver*], [*Waktu*], [*Kompleksitas*],
      [Greedy NN], [2.0 ms], [$O(N^2)$],
      [Memetic PSO], [140.0 ms], [$O(P dot I dot N^2)$],
    )

    #v(0.4em)
    - PSO ~70× lebih lambat, namun *140 ms* sangat layak untuk demo real-time
    - *Early stopping* aktif di iterasi ke-*21* (dari 150 batas)
    - Penghematan 3.03% bermakna nyata di logistik riil (penghematan bensin, waktu tempuh)

    === Konvergensi Global Best
    - *Iterasi 0*: Dimulai dari Greedy seed — 891.94 km
    - *Iterasi 1*: 2-opt langsung diterapkan → turun ke *864.93 km*
    - *Iterasi 2–21*: Stabil, tidak ada peningkatan
    - *Early stopping aktif* di iterasi 21
  ],
  [
    === Kurva Konvergensi (Ilustrasi)

    #rect(
      fill: luma(247),
      stroke: luma(200),
      radius: 5pt,
      inset: 0.9em,
      width: 100%,
    )[
      #set text(size: 0.8em, font: "DejaVu Sans Mono")
      Jarak Global Best (km)\
      #v(0.3em)
      ```
      891.94 |●─╮  ← Greedy seed (iter 0)
             |  ╰─────── ← 2-opt (iter 1)
      864.93 |   ●━━━━━━━━━━━━━━━ ← konvergen
             |
             +──────────────────→ Iterasi
              0  1  5  10  15  21
      ```
      #v(0.2em)
      Garis putus-putus merah = Greedy baseline\
      Kurva biru = PSO global best
    ]

    #v(0.4em)
    === Diversitas Swarm
    - Std dev partikel dimulai dari *~600 km* (eksplorasi)
    - Menyusut ke *≈ 0 km* setelah iterasi ke-20
    - Menandakan *konsensus swarm* — konvergensi terverifikasi secara matematis
  ],
)

= Visualisasi Performa Akademik

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Pairwise Distance Heatmap
    Matriks jarak antar 27 kota mengonfirmasi dua kluster padat:

    - *Kluster Barat:* Depok, Bogor, Bekasi, Kota Bekasi ($d < 20$ km)
    - *Kluster Bandung Raya:* Kota Bandung, Cimahi, Bandung Barat ($d < 15$ km)

    Rute optimal secara natural menyelesaikan seluruh kunjungan dalam satu kluster *sebelum* melompat ke kluster berikutnya.

    === Edge Hop Length Distribution
    - Rute Greedy: distribusi _hop_ memiliki ekor panjang — lompatan *> 150 km* di akhir rute
    - Rute PSO: distribusi terpusat pada *15–50 km*, puncak frekuensi di rentang *15–30 km*
    - Bukti: PSO menghasilkan rute lebih "efisien" tanpa lompatan jauh
  ],
  [
    === Kurva Diversitas Swarm

    #rect(
      fill: luma(247),
      stroke: luma(200),
      radius: 5pt,
      inset: 0.9em,
      width: 100%,
    )[
      #set text(size: 0.8em, font: "DejaVu Sans Mono")
      Std Dev Partikel (km)\
      #v(0.3em)
      ```
      ~600 |●
           | ╲
      ~300 |  ╲
           |   ╲──
      ~100 |      ╲──
           |         ╲───── ≈ 0
         0 +────────────────────→ Iterasi
           0    5    10   15   20
      ```
    ]

    #v(0.4em)
    #rect(
      fill: blue.lighten(85%),
      stroke: blue.lighten(40%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      #text(size: 0.88em)[Penurunan diversitas ke ≈ 0 adalah *bukti matematis* bahwa seluruh partikel benar-benar konvergen ke solusi yang sama — bukan sekadar berhenti karena batas iterasi.]
    ]
  ],
)


// ══════════════════════════════════════════════════════════════
//  SECTION 6 — KESIMPULAN
// ══════════════════════════════════════════════════════════════

= Kesimpulan <touying:hidden>
#new-section-slide([Kesimpulan])

= Kesimpulan dan Saran Pengembangan

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    === Kesimpulan

    #set list(marker: [✓])
    - *Memetic PSO* terbukti lebih optimal dari Greedy NN:\
      *891.94 km → 864.93 km (−3.03%, −27.01 km)*
    - *Greedy Seeding* memastikan PSO dimulai dari baseline kuat — konvergensi lebih cepat dan terukur
    - *2-Opt Local Search* berhasil mengeliminasi persilangan jalur secara efektif di iterasi pertama
    - *Early Stopping* mempersingkat komputasi dari 150 ke *21 iterasi* tanpa kehilangan kualitas solusi
    - Diversitas partikel turun ke ≈ 0, mengonfirmasi *konvergensi global* yang valid secara matematis
    - Dashboard Streamlit berhasil mendemonstrasikan algoritma secara *interaktif dan visual*
  ],
  [
    === Saran Pengembangan

    #set list(marker: [→])
    - Integrasikan data *kemacetan real-time* untuk TSP dinamis (Dynamic TSP)
    - Tambahkan *Haversine-Time model* yang memperhitungkan waktu tempuh, bukan hanya jarak
    - Uji skala lebih besar: seluruh Jawa atau Indonesia ($N > 100$)
    - Eksplorasi varian PSO: *APSO*, *CPSO*, atau kombinasi dengan *Simulated Annealing*
    - Implementasi *Multi-Objective TSP*: minimisasi jarak + waktu + biaya sekaligus

    #v(0.5em)
    #rect(
      fill: blue.lighten(85%),
      stroke: blue.lighten(40%),
      radius: 5pt,
      inset: 0.75em,
      width: 100%,
    )[
      Penelitian ini membuktikan bahwa algoritma berbasis *swarm intelligence* mampu menyelesaikan problem optimasi rute rill secara efektif dan efisien dalam waktu komputasi yang sangat layak.
    ]
  ],
)


// ══════════════════════════════════════════════════════════════
//  REFERENSI
// ══════════════════════════════════════════════════════════════

= Referensi <touying:hidden>

#set par(leading: 1.4em)
#v(1em)

*\[1\]* J. Kennedy and R. Eberhart, "Particle swarm optimization," in _Proceedings of ICNN'95 — International Conference on Neural Networks_, vol. 4, pp. 1942–1948, 1995.

#v(0.4em)
*\[2\]* M. Clerc, "Discrete Particle Swarm Optimization, illustrated by the Traveling Salesman Problem," in _New Optimization Techniques in Engineering_, Springer, pp. 219–239, 2004.

#v(0.4em)
*\[3\]* G. A. Croes, "A method for solving traveling-salesman problems," _Operations Research_, vol. 6, no. 6, pp. 791–812, 1958.

#v(0.4em)
*\[4\]* W. Banzhaf _et al._, _Genetic Programming: An Introduction_, Morgan Kaufmann, 1998.

#v(0.4em)
*\[5\]* W. Sinnott, "Virtues of the Haversine," _Sky and Telescope_, vol. 68, no. 2, p. 159, 1984.


// ══════════════════════════════════════════════════════════════
//  TERIMA KASIH
// ══════════════════════════════════════════════════════════════

= Terima Kasih <touying:hidden>

#align(center + horizon)[
  #v(1fr)
  #text(size: 3em, weight: "bold")[Terima Kasih]
  #v(1em)
  #text(size: 1.3em, style: "italic")[Ada Pertanyaan?]
  #v(2em)
  #text(size: 0.9em)[
    Kode sumber tersedia di:\ `github.com/insanansharyrasul/PKK-Miniproject`
  ]
  #v(1fr)
]
