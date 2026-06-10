// ============================================================
// IEEE-style Draft Laporan — Typst
// ============================================================

#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 1.7cm, right: 1.7cm),
)
#set text(
  font: "Times New Roman",
  size: 10pt,
  weight: "regular",
)
#set par(justify: true, leading: 0.55em)
#set figure(supplement: "Gambar")

// Heading styles — bold only on headings, IEEE sizing
#show heading.where(level: 1): it => [
  #v(0.8em)
  #align(center)[
    #text(weight: "bold", size: 10pt)[#upper(it.body)]
  ]
  #v(0.4em)
]
#show heading.where(level: 2): it => [
  #v(0.6em)
  #text(weight: "bold", style: "italic", size: 10pt)[#it.body]
  #v(0.3em)
]

// Remove bold/emphasis from body text — ensure italic-only for emphasis
#show emph: it => text(style: "italic", it.body)

// ============================================================
// Title and Authors
// ============================================================
#align(center)[
  #text(size: 14pt, weight: "bold")[
    Penerapan _Particle Swarm Optimization_ (PSO) untuk _Traveling Salesperson Problem_: Studi Kasus Kabupaten/Kota di Jawa Barat
  ]
  #v(1em)

  #grid(
    columns: (1fr),
    row-gutter: 0.4em,
    [#text(size: 11pt)[
      Naufal Akmal Rizqulloh#super[1], Adhiya Radhin Fasya#super[2], Faiz Naufal Huda#super[3], Insan Anshary Rasul#super[4], Daffa Naufal Mumtaz#super[5]
    ]],
    [#v(0.3em)],
    [#text(size: 10pt, style: "italic")[Departemen Ilmu Komputer, Sekolah Sains Data, Matematika, dan Informatika]],
    [#text(size: 10pt, style: "italic")[IPB University, Bogor, Indonesia]],
    [#v(0.3em)],
    [#text(size: 9pt, font: "Courier New")[
      #super[1]G6401231065 #h(0.4em) #super[2]G6401231068 #h(0.4em) #super[3]G6401231124 #h(0.4em) #super[4]G6401231132 #h(0.4em) #super[5]G6401231168
    ]],
  )

  #v(0.4em)
  #text(size: 9pt, style: "italic")[Mata Kuliah: Pengantar Kecerdasan Komputasional (KOM1326)]
]

#v(1.5em)

// ============================================================
// Abstract Block
// ============================================================
#grid(
  columns: (1fr),
  inset: (x: 1.2cm),
  [
    #text(weight: "bold", style: "italic")[Abstract]---This paper presents a hybrid Discrete Particle Swarm Optimization (PSO) combined with Greedy Nearest Neighbor seeding and 2-opt local search to solve the Traveling Salesperson Problem (TSP) on 27 real-world locations in West Java. The TSP is NP-hard; exact algorithms become intractable beyond 15 cities due to factorial state-space explosion. Our Memetic PSO seeds one particle with a Greedy route and periodically applies 2-opt sweeps to eliminate edge crossovers. An auto-tuning module selects optimal hyperparameters from four presets. The system is implemented as a modular Python pipeline with an interactive Streamlit dashboard and a Jupyter Notebook for academic analysis. Experiments show that the hybrid PSO reduces the Greedy baseline from 891.94 km to 788.08 km (11.64% improvement) in 9.79 s, with early stopping triggered by swarm convergence validated through particle diversity metrics.
    
    #v(0.4em)
    #text(weight: "bold", style: "italic")[Keywords]---Particle Swarm Optimization, Traveling Salesperson Problem, 2-opt, Greedy Nearest Neighbor.
    
    #v(0.8em)
    #text(weight: "bold", style: "italic")[Abstrak]---Makalah ini menyajikan hibridisasi Particle Swarm Optimization (PSO) Diskrit dengan penyemaian Greedy Nearest Neighbor dan pencarian lokal 2-opt untuk menyelesaikan Traveling Salesperson Problem (TSP) pada 27 lokasi riil di Jawa Barat. TSP merupakan masalah NP-hard di mana algoritma eksak tidak layak secara komputasi pada skala besar akibat ledakan ruang keadaan faktorial. PSO Memetik kami menyemai satu partikel dengan rute Greedy dan secara periodik menerapkan 2-opt untuk menghilangkan persilangan jalur. Modul auto-tuning memilih hyperparameter optimal dari empat preset. Sistem diimplementasikan sebagai pipeline Python modular dengan dashboard Streamlit interaktif dan Jupyter Notebook untuk analisis akademis. Hasil eksperimen menunjukkan PSO hibrida mengoptimalkan baseline Greedy dari 891.94 km menjadi 788.08 km (peningkatan 11.64%) dalam 9.79 s, dengan early stopping dipicu oleh konvergensi swarm yang divalidasi melalui metrik diversitas partikel.
    
    #v(0.4em)
    #text(weight: "bold", style: "italic")[Kata Kunci]---Particle Swarm Optimization, Traveling Salesperson Problem, 2-opt, Greedy Nearest Neighbor.
  ]
)

#v(1.5em)

// ============================================================
// Double column layout
// ============================================================
#show: rest => columns(2, gutter: 0.6cm, rest)

= I. Pendahuluan
_Traveling Salesperson Problem_ (TSP) merupakan salah satu masalah optimasi kombinatorial tertua dan paling intensif dipelajari dalam ilmu komputer [4]. Tujuan TSP adalah menemukan rute siklik terpendek (_Hamiltonian cycle_) yang mengunjungi sekumpulan kota masing-masing tepat satu kali dan kembali ke kota asal. TSP diklasifikasikan sebagai masalah _NP-hard_, yang berarti tidak ada algoritma waktu polinomial yang diketahui dapat memecahkan seluruh instansi masalah secara eksak.

Untuk jumlah kota kecil ($N < 12$), algoritma eksak seperti _Branch and Bound_ atau A\* dapat menemukan rute optimal mutlak. Namun, ketika jumlah kota bertambah ($N >= 15$), ruang pencarian membengkak secara faktorial ($N!$). Sebagai contoh, untuk 27 lokasi di Jawa Barat, terdapat $27! approx 1.08 times 10^(28)$ kemungkinan rute, sehingga algoritma eksak mengalami kehabisan memori dan waktu komputasi yang tidak terbatas.

Oleh karena itu, algoritma metaheuristik seperti _Particle Swarm Optimization_ (PSO) [1] menjadi solusi praktis. PSO merupakan bagian dari paradigma kecerdasan komputasional (_computational intelligence_) [5] yang terinspirasi dari perilaku kolektif kawanan burung. Algoritma heuristik _Greedy Nearest Neighbor_ memberikan solusi cepat namun sering terjebak pada optimum lokal. Makalah ini mengintegrasikan PSO diskrit dengan penyemaian _Greedy_ dan pencarian lokal _2-opt_ (_Memetic PSO_) untuk menyelesaikan TSP riil di Jawa Barat.

Tujuan penelitian ini adalah: (1) mengimplementasikan algoritma _Discrete Memetic PSO_ berbasis _swap operator_, (2) membandingkan efisiensi rute antara _Greedy Nearest Neighbor_ dan PSO Memetik, (3) membangun sistem interaktif berbasis _Streamlit_ untuk visualisasi proses optimasi, dan (4) memvalidasi konvergensi algoritma menggunakan metrik diversitas partikel.

= II. Tinjauan Pustaka
== A. Traveling Salesperson Problem (TSP)
Secara matematis, TSP direpresentasikan sebagai graf $G = (V, E)$ di mana $V$ adalah himpunan kota dan $E$ adalah himpunan jalur penghubung [4]. Jarak antara kota $i$ dan $j$ dilambangkan $d(i, j)$. Tujuan TSP adalah menemukan permutasi $pi$ yang meminimalkan total jarak rute siklik:
$ min sum_(i=1)^(N-1) d(pi(i), pi(i+1)) + d(pi(N), pi(1)) $

TSP termasuk kelas _NP-hard_ berdasarkan teorema Cook–Karp, sehingga pendekatan metaheuristik diperlukan untuk instansi berskala besar.

== B. _Particle Swarm Optimization_ (PSO)
PSO diperkenalkan oleh Kennedy dan Eberhart [1], terinspirasi oleh perilaku sosial kawanan burung. Setiap partikel memperbarui kecepatan ($V$) dan posisi ($X$) berdasarkan memori pribadinya (_pbest_) dan memori kelompok (_gbest_). PSO termasuk dalam keluarga algoritma kecerdasan komputasional (_computational intelligence_) [5] yang tidak memerlukan informasi gradien dan mampu menjelajahi ruang pencarian secara global.

== C. _Discrete PSO_ (_Permutation-Based_)
Karena TSP memiliki ruang keadaan diskrit berupa permutasi, pembaruan vektor standar tidak dapat diterapkan. Model aljabar _swap operator_ yang diperkenalkan Clerc [2] mengadaptasi PSO untuk domain permutasi, di mana posisi direpresentasikan sebagai urutan indeks kota dan kecepatan sebagai barisan operasi pertukaran.

== D. Pencarian Lokal _2-Opt_
Algoritma _2-opt_ [3] merupakan teknik pencarian lokal untuk memperbaiki rute TSP dengan memilih dua sisi rute non-bersebelahan dan membalik segmen di antaranya. Proses diulang hingga tidak ada perbaikan, menghasilkan rute bebas persilangan jalur (_crossing edges_).

= III. Metodologi Penelitian
== A. Pengumpulan Data
Data diperoleh dari _file_ CSV yang berisi nama, _latitude_, dan _longitude_ 27 kabupaten/kota di Jawa Barat. Data dimuat dan dibersihkan menggunakan fungsi `load_and_filter_data()` yang memvalidasi struktur, menghapus kolom tidak relevan, dan menangani nilai kosong. Daftar koordinat ditampilkan pada Tabel I.

// Tabel 1 — IEEE horizontal-only lines
#align(center)[
  #block(width: 100%)[
    #set text(size: 8pt)
    #v(0.3em)
    #text(size: 7.5pt, weight: "bold")[TABEL I]
    #v(-0.3em)
    #text(size: 7.5pt)[Daftar 27 Titik Koordinat Wilayah Jawa Barat]
    #v(0.3em)
    #table(
      columns: (1fr, 4fr, 2.5fr, 2.5fr),
      align: (center, left, center, center),
      stroke: none,
      table.hline(stroke: 1pt),
      table.header(
        [No.], [Kabupaten / Kota], [Latitude], [Longitude],
      ),
      table.hline(stroke: 0.5pt),
      [1], [Bandung], [-7.0635], [107.6338],
      [2], [Bandung Barat], [-6.9054], [107.4124],
      [3], [Banjar], [-7.3805], [108.5610],
      [4], [Bekasi], [-6.1979], [107.1598],
      [5], [Bogor], [-6.5454], [107.0021],
      [6], [Ciamis], [-7.4375], [108.6452],
      [7], [Cianjur], [-7.0538], [107.0692],
      [8], [Cimahi], [-6.8823], [107.5445],
      [9], [Cirebon], [-6.7614], [108.4559],
      [10], [Depok], [-6.3879], [106.8161],
      [11], [Garut], [-7.3429], [107.7031],
      [12], [Indramayu], [-6.4537], [108.1853],
      [13], [Karawang], [-6.2634], [107.4294],
      [14], [Kota Bandung], [-6.9033], [107.6299],
      [15], [Kota Bekasi], [-6.2849], [106.9735],
      [16], [Kota Bogor], [-6.5952], [106.8000],
      [17], [Kota Cirebon], [-6.7436], [108.5562],
      [18], [Kota Sukabumi], [-6.9357], [106.9315],
      [19], [Kota Tasikmalaya], [-7.3600], [108.2279],
      [20], [Kuningan], [-6.9876], [108.5538],
      [21], [Majalengka], [-6.8077], [108.2836],
      [22], [Purwakarta], [-6.5925], [107.4036],
      [23], [Subang], [-6.5007], [107.7343],
      [24], [Sukabumi], [-7.0782], [106.7377],
      [25], [Sumedang], [-6.8102], [107.9617],
      [26], [Tasikmalaya], [-7.4280], [108.0691],
      [27], [Waduk Cirata], [-6.7552], [107.2857],
      table.hline(stroke: 1pt),
    )
  ]
]


== B. Perhitungan Jarak Geodesik (_Haversine_)
Untuk rute geografis riil, metrik _Euclidean_ tidak akurat karena kelengkungan bumi. Formula _Haversine_ digunakan:
$ a = sin^2((Delta phi)/2) + cos(phi_1) dot cos(phi_2) dot sin^2((Delta lambda)/2) $
$ c = 2 dot arcsin(sqrt(a)) $
$ d = R dot c $
di mana $R approx 6371$ km adalah radius rata-rata bumi, $phi$ adalah _latitude_, dan $lambda$ adalah _longitude_.

== C. Algoritma _Greedy Nearest Neighbor_
Mulai dari kota indeks 0, rute dibangun dengan memilih kota terdekat yang belum dikunjungi secara berulang:
$ v_("next") = arg min_(u in "Unvisited") d(v_("current"), u) $
Algoritma ini memiliki kompleksitas $O(N^2)$ dan menjadi _baseline_ pembanding.

== D. Aljabar _Swap Operator_ untuk PSO Diskrit
Representasi diskrit PSO menggunakan aljabar _swap operator_ [2]:

1. _Swap Operation_ $S O(i, j)$: pertukaran elemen pada indeks $i$ dan $j$ dalam permutasi rute.
2. _Velocity_ ($V$): barisan berurutan dari _swap operations_: $V = [S O(i_1, j_1), S O(i_2, j_2), ...]$
3. Pengurangan posisi ($X_2 - X_1$): menghasilkan barisan _swap_ yang mengubah $X_1$ menjadi $X_2$.
4. Perkalian skalar ($p dot V$): mempertahankan setiap _swap_ dengan probabilitas $p in [0, 1]$.
5. Pembaruan kecepatan:
    $ V_(t+1) = w V_t + c_1 r_1 (P_("best") - X_t) + c_2 r_2 (G_("best") - X_t) $
    di mana $w$ adalah bobot inersia, $c_1, c_2$ adalah faktor kognitif dan sosial, $r_1, r_2$ adalah bilangan acak $[0, 1]$.
6. Pembaruan posisi: $X_(t+1) = X_t + V_(t+1)$.

== E. Optimasi Hibrida & _Memetic_
Lima teknik kunci dirancang untuk meningkatkan kualitas solusi dan mencegah konvergensi prematur:

1. _Heuristic Seeding_: partikel ke-0 disemai dengan rute _Greedy_, menjamin pencarian dimulai dari _baseline_ kuat, sementara partikel lainnya diinisialisasi acak untuk menjaga diversitas awal.
2. _Velocity Cap_: panjang barisan _swap_ dibatasi hingga $floor(N\/2)$ operasi per iterasi, mencegah perubahan posisi yang terlalu ekstrem dan menstabilkan dinamika pencarian.
3. _Periodic 2-Opt_: setiap 5 iterasi, pencarian lokal _2-opt_ [3] diterapkan pada 25% partikel _elite_ (jarak terbaik saat itu) untuk menghilangkan persilangan jalur secara periodik:
    $ "Jalur Baru" = [v_1, ..., v_(i-1), v_j, v_(j-1), ..., v_i, v_(j+1), ...] $
4. _Adaptive Mutation Decay_: laju mutasi diturunkan secara linier terhadap kemajuan iterasi sehingga eksplorasi tinggi di awal berangsur bergeser menjadi eksploitasi di akhir:
    $ mu_t = mu_0 dot (1 - 0.9 dot t\/T) $
    di mana $mu_0 = 0.05$, $t$ adalah iterasi saat ini, dan $T$ adalah batas iterasi maksimum.
5. _Diversity-Based Partial Restart_: jika koefisien variasi (_CoV_) jarak seluruh partikel turun di bawah ambang 1%, sebanyak 25% partikel dengan kinerja terburuk diinisialisasi ulang secara acak untuk memulihkan eksplorasi dan mencegah stagnasi prematur.

== F. _Auto-Tuning_ Parameter
Modul _auto-tuning_ mengevaluasi empat _preset_ konfigurasi melalui _grid search_, sebagaimana ditampilkan pada Tabel II. Setiap _preset_ dievaluasi dengan 3 _trial_ sesi PSO singkat (30 iterasi). _Preset_ dengan rata-rata jarak akhir terendah dipilih sebagai konfigurasi optimal [4].

// Tabel II — IEEE horizontal-only lines
#align(center)[
  #block(width: 100%)[
    #set text(size: 8pt)
    #v(0.3em)
    #text(size: 7.5pt, weight: "bold")[TABEL II]
    #v(-0.3em)
    #text(size: 7.5pt)[_Preset_ Konfigurasi Parameter _Auto-Tuning_]
    #v(0.3em)
    #table(
      columns: (2.5fr, 1.5fr, 1.5fr, 1.5fr, 2fr),
      align: (left, center, center, center, center),
      stroke: none,
      table.hline(stroke: 1pt),
      table.header(
        [_Preset_], [$w$], [$c_1$], [$c_2$], [Partikel],
      ),
      table.hline(stroke: 0.5pt),
      [Balanced], [0.7], [1.5], [1.5], [20],
      [Exploration-Heavy], [0.9], [2.0], [1.0], [30],
      [Exploitation-Heavy], [0.4], [1.0], [2.0], [15],
      [Lightweight], [0.6], [1.2], [1.2], [10],
      table.hline(stroke: 1pt),
    )
  ]
]

== G. Kriteria Berhenti Awal (_Early Stopping_)
Jika jarak $G_("best")$ tidak berkurang lebih dari 0.01 km selama $K$ iterasi berturut-turut (_default_ $K=20$), _loop_ dihentikan untuk menghemat waktu komputasi.

= IV. Implementasi Sistem
Sistem dibangun dalam arsitektur modular terintegrasi yang terdiri dari tiga komponen utama [5]:

== A. Mesin Perhitungan (pso\_engine.py)
Modul komputasi dirancang dengan prinsip _Object-Oriented Programming_ dan _type hints_ penuh. Komponen utamanya: (1) fungsi `haversine_distance()` dan `euclidean_distance()` sebagai dua metrik jarak yang dapat dipilih; (2) fungsi aljabar _swap_ `get_swap_sequence()`, `scale_velocity()` dengan klamping probabilitas ke $[0,1]$, dan `apply_velocity()`; (3) kelas `GreedyTSPSolver` sebagai _baseline_ $O(N^2)$; (4) kelas `Particle` yang merepresentasikan posisi rute, kecepatan _swap_, dan memori _pbest_; (5) kelas `PSOSolver` sebagai _orchestrator_ yang mengintegrasikan kelima teknik optimasi hibrida; dan (6) fungsi `auto_tune_pso()` untuk seleksi _preset_ otomatis berbasis _grid search_. Kebenaran seluruh komponen diverifikasi melalui 18 kasus uji pada `test_engine.py` dengan _pipeline_ CI/CD berbasis _GitHub Actions_.

== B. _Dashboard_ Interaktif (app.py)
Antarmuka _Streamlit_ dibangun modular dengan fungsi terpisah untuk tiap komponen visual. _Sidebar_ menyediakan: unggah _dataset_ CSV dengan deteksi kolom otomatis, pemilihan jumlah kota, metrik jarak, mode Auto-Tune/Manual, parameter $w$, $c_1$, $c_2$, _mutation rate_, _early stopping_, dan kontrol _seed_ untuk reprodusibilitas. Panel utama menampilkan: peta interaktif _Plotly_ pada _OpenStreetMap_ dengan _toggle_ rute Greedy dan PSO, _slider iteration playback_ untuk menelusuri evolusi rute per iterasi, grafik konvergensi _real-time_, tabel perbandingan, dan tiga panel analisis performa akademik.

== C. _Notebook_ Akademis (pso\_tsp\_demo.ipynb)
_Notebook Jupyter_ menyajikan analisis visual statis lengkap menggunakan _Matplotlib_ dan _Seaborn_ dalam tujuh seksi: (1) landasan teori aljabar _swap operator_; (2) pemuatan dan verifikasi data; (3) eksekusi _baseline Greedy_; (4) _auto-tuning_ dan eksekusi PSO; (5) kurva konvergensi dan peta perbandingan rute; (6) tiga panel analisis kinerja (_bar chart_ jarak, waktu komputasi, kurva diversitas partikel); dan (7) analisis spasial berupa _heatmap_ matriks jarak _pairwise_ dan distribusi _edge hop length_.

= V. Hasil dan Diskusi
Eksperimen dijalankan pada 27 lokasi Jawa Barat. Modul _auto-tuning_ memilih _preset_ Exploitation-Heavy dengan parameter $w=0.4$, $c_1=1.0$, $c_2=2.0$, 15 partikel, _mutation rate_ 0.05, batas 150 iterasi, dan _seed_ 42 untuk reprodusibilitas.

== A. Perbandingan Efisiensi Jarak Rute
Rangkuman perbandingan disajikan pada Tabel III.

// Tabel III — IEEE horizontal-only lines
#align(center)[
  #block(width: 100%)[
    #set text(size: 8pt)
    #v(0.3em)
    #text(size: 7.5pt, weight: "bold")[TABEL III]
    #v(-0.3em)
    #text(size: 7.5pt)[Perbandingan Performa Hasil Optimasi TSP]
    #v(0.3em)
    #table(
      columns: (2.5fr, 2fr, 2fr, 1.5fr, 1.5fr),
      align: (center, center, center, center, center),
      stroke: none,
      table.hline(stroke: 1pt),
      table.header(
        [Metode], [Jarak (km)], [Selisih (km)], [Efisiensi], [Waktu],
      ),
      table.hline(stroke: 0.5pt),
      [Jalur Acak], [2701.19], [+1809.25], [-202.83%], [N/A],
      [Greedy NN], [891.94], [0.00 (Ref)], [0.00%], [2.00 ms],
      [Memetic PSO], [788.08], [-103.86], [11.64%], [9.79 s],
      table.hline(stroke: 1pt),
    )
  ]
]

_Memetic PSO_ berhasil memotong panjang rute sebesar 103.86 km (peningkatan efisiensi 11.64%) dibandingkan _baseline Greedy_. Peningkatan ini terjadi karena _Greedy_ hanya mengambil keputusan lokal terbaik tanpa mempertimbangkan dampak jangka panjang rute, sehingga sering menyisakan kota-kota terjauh di akhir pencarian yang mengakibatkan lompatan rute balik sangat jauh. _Memetic PSO_ mampu mematangkan rute secara global melalui kolaborasi antar partikel [1].

Perbandingan jarak rute antara ketiga metode (jalur acak, _Greedy_ NN, dan PSO) ditampilkan secara visual pada @fig-kinerja (panel kiri), yang secara jelas menunjukkan reduksi jarak bertahap dari pendekatan tanpa kecerdasan menuju optimasi PSO.

== B. Analisis Waktu Komputasi
_Greedy_ menyelesaikan pencarian dalam 2.00 ms karena kompleksitasnya $O(N^2)$, sedangkan _Memetic PSO_ membutuhkan 9.79 s. Selisih waktu ini merupakan _trade-off_ yang dapat diterima mengingat keuntungan penghematan rute 11.64%. Sebagian besar waktu PSO dihabiskan oleh operasi _2-opt_ periodik setiap 5 iterasi; _Early Stopping_ menghentikan _loop_ pada iterasi ke-60 dari 150 iterasi maksimum. Perbandingan waktu komputasi kedua metode divisualisasikan pada @fig-kinerja (panel tengah).

== C. Analisis Konvergensi dan Diversitas _Swarm_
Kurva konvergensi pada @fig-konvergensi menunjukkan bahwa rute $G_("best")$ langsung dimulai dari jarak _Greedy_ (891.94 km) karena _heuristic seeding_ pada partikel ke-0. Operasi _2-opt_ periodik secara bertahap mengeliminasi persilangan jalur, sehingga jarak turun progresif hingga 788.08 km ketika _early stopping_ terpicu pada iterasi ke-60.

#figure(
  image("out/01_kurva_konvergensi_pso_vs_greedy.png", width: 100%),
  caption: [Kurva konvergensi PSO vs. _baseline Greedy_.],
) <fig-konvergensi>

Dari perspektif diversitas _swarm_ (@fig-kinerja, panel kanan), standar deviasi _fitness_ partikel dimulai tinggi ($approx 600$ km) dan menyusut bertahap mendekati 0 setelah iterasi ke-60, menandakan konvergensi stabil [5].

== D. Visualisasi Perbandingan Rute
@fig-rute menampilkan perbandingan visual rute _Greedy_ (kiri) dan PSO (kanan) pada peta koordinat Jawa Barat. Terlihat bahwa rute _Greedy_ memiliki beberapa persilangan jalur, sementara rute PSO lebih teratur dan menghindari lompatan jauh.

#figure(
  image("out/02_perbandingan_rute_greedy_vs_pso.png", width: 100%),
  caption: [Perbandingan rute TSP: _Greedy_ (kiri, 891.94 km) vs. PSO (kanan, 788.08 km).],
) <fig-rute>

== E. Analisis Performa Akademik
@fig-kinerja menyajikan tiga panel analisis kinerja: (1) perbandingan jarak rute menunjukkan reduksi dari jalur acak (rata-rata 2701.2 km) ke _Greedy_ (891.94 km) dan PSO (788.08 km); (2) perbandingan waktu komputasi menunjukkan _trade-off_ antara kecepatan _Greedy_ dan kualitas PSO; (3) kurva diversitas partikel memvalidasi konvergensi _swarm_ secara matematis.

#figure(
  image("out/03_analisis_kinerja_pso_vs_greedy.png", width: 100%),
  caption: [Analisis kinerja akademik: perbandingan jarak, waktu, dan diversitas _swarm_.],
) <fig-kinerja>

== F. Analisis Spasial
Matriks jarak _pairwise_ pada @fig-heatmap mengonfirmasi adanya dua kluster padat: kluster metropolitan barat (Depok, Bogor, Bekasi) dan kluster Bandung Raya (Kota Bandung, Cimahi, Bandung Barat) dengan jarak < 20 km. Pola kluster ini menjelaskan mengapa rute optimal cenderung menyelesaikan kunjungan dalam satu kluster sebelum berpindah.

#figure(
  image("out/04_matriks_jarak_geografis.png", width: 100%),
  caption: [Matriks jarak geodesik _pairwise_ antar 27 kota/kabupaten (km).],
) <fig-heatmap>

Distribusi panjang langkah (_edge hop_) pada @fig-hop menunjukkan bahwa _Greedy_ NN memiliki lompatan sangat jauh (> 100 km) pada _hop_ ke-14, sedangkan PSO memiliki distribusi lebih merata dengan standar deviasi lebih rendah (12.4 km vs. 22.5 km), membuktikan rute PSO lebih efisien [4].

#figure(
  image("out/05_distribusi_panjang_langkah_rute.png", width: 100%),
  caption: [Distribusi panjang langkah (_edge hop length_) rute _Greedy_ vs. PSO.],
) <fig-hop>

= VI. Kesimpulan
Penelitian ini membuktikan bahwa _Discrete PSO_ yang dihibridisasi dengan _Greedy seeding_ dan _2-opt_ [3] merupakan solusi efektif untuk TSP riil. Metode hibrida ini menjamin rute selalu lebih optimal dari heuristik _Greedy_ klasik, dengan peningkatan efisiensi 11.64% dan waktu komputasi ~10 detik untuk 27 lokasi Jawa Barat.

Kontribusi utama meliputi: (1) implementasi PSO Diskrit berbasis _swap operator_ [2] yang modular dengan _type hints_ penuh dan 18 kasus uji terverifikasi; (2) lima teknik optimasi hibrida — _heuristic seeding_, _velocity cap_, _periodic 2-opt memetic_, _adaptive mutation decay_, dan _diversity-based partial restart_ — yang secara kolektif meningkatkan kualitas solusi dan mencegah konvergensi prematur; (3) modul _auto-tuning_ berbasis _grid search_ empat _preset_; dan (4) sistem _dashboard_ interaktif _Streamlit_ dengan _iteration playback_ dan analisis performa _real-time_.

Untuk penelitian selanjutnya, disarankan pengujian pada data dinamis menggunakan model _Haversine-Time_, perluasan jumlah kota ke skala nasional, serta eksplorasi algoritma metaheuristik lain seperti _Genetic Algorithm_ [4] atau _Ant Colony Optimization_ sebagai pembanding.

= Referensi
[1] J. Kennedy and R. Eberhart, "Particle swarm optimization," in _Proceedings of ICNN'95_, vol. 4, pp. 1942-1948, 1995.\
[2] M. Clerc, "Discrete Particle Swarm Optimization, illustrated by the Traveling Salesman Problem," _New Optimization Techniques in Engineering_, pp. 219-239, 2004.\
[3] G. Croes, "A method for solving traveling-salesman problems," _Operations Research_, vol. 6, no. 6, pp. 791-812, 1958.\
[4] X.-S. Yang, _Nature-Inspired Metaheuristic Algorithms_, 2nd ed. Luniver Press, 2010.\
[5] A. P. Engelbrecht, _Computational Intelligence: An Introduction_, 2nd ed. Wiley, 2007.
