#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 1.8cm, right: 1.8cm),
)
#set text(
  font: "Times New Roman",
  size: 10pt,
)
#set par(justify: true, leading: 0.6em)

// Custom heading styles
#show heading: it => [
  #v(0.8em)
  #text(
    weight: "bold",
    size: if it.level == 1 { 10pt } else { 10pt },
    features: (smallcaps: it.level == 1)
  )[#it.body]
  #v(0.4em)
]

// Title and Authors Section
#align(center)[
  #text(size: 24pt, weight: "bold")[
    Penerapan Particle Swarm Optimization (PSO) Diskrit dengan Penyemaian Heuristik dan Pencarian Lokal 2-Opt untuk Traveling Salesperson Problem di Jawa Barat
  ]
  #v(1.5em)
  #grid(
    columns: (1fr),
    row-gutter: 0.5em,
    [#text(size: 11pt, weight: "medium")[Nama Mahasiswa]],
    [#text(size: 10pt, style: "italic")[Jurusan Teknik Informatika, Fakultas Teknik dan Sains]],
    [#text(size: 10pt, style: "italic")[Institut Pendidikan Indonesia]],
    [#text(size: 10pt, style: "italic")[Garut, Indonesia]],
    [#text(size: 9pt, font: "Courier New")[mahasiswa@domain.ac.id]]
  )
]

#v(2em)

// Abstract Block
#grid(
  columns: (1fr),
  inset: (x: 1.5cm),
  [
    #text(weight: "bold", style: "italic")[Abstract]---This paper presents a hybrid Discrete Particle Swarm Optimization (PSO) algorithm combined with Greedy seeding and 2-opt local search (Memetic Algorithm) to solve the Traveling Salesperson Problem (TSP) using real-world coordinates from 27 locations in West Java. The TSP is an NP-hard problem for which exact search algorithms like A\* become computationally intractable at scale (N >= 15) due to factorial state explosion. We propose a Memetic PSO that initializes particles using a Greedy Nearest Neighbor route and periodically applies a 2-opt sweep to eliminate overlapping paths (edge crossovers). Experimental results on the 27 locations of West Java show that the hybrid PSO successfully optimizes the Greedy baseline of 891.94 km down to 864.93 km (a 3.03% improvement) in 140 ms, with the optimization terminating early due to convergence. Swarm convergence is mathematically validated using particle diversity metrics.
    
    #v(0.5em)
    #text(weight: "bold", style: "italic")[Keywords]---Particle Swarm Optimization, TSP, Memetic Algorithm, 2-opt, Greedy Nearest Neighbor, Jawa Barat.
    
    #v(1em)
    #text(weight: "bold", style: "italic")[Abstrak]---Makalah ini menyajikan hibridisasi algoritma Particle Swarm Optimization (PSO) Diskrit yang digabungkan dengan penyemaian Greedy dan pencarian lokal 2-opt (Algoritma Memetik) untuk memecahkan Traveling Salesperson Problem (TSP) menggunakan data koordinat riil dari 27 kabupaten/kota di Jawa Barat. TSP merupakan masalah NP-hard di mana algoritma eksak seperti A\* tidak lagi layak secara komputasi pada skala besar (N >= 15) karena ledakan ruang keadaan faktorial. Kami mengusulkan PSO Memetik yang menginisialisasi partikel dengan rute Greedy Nearest Neighbor dan secara periodik menerapkan operasi 2-opt untuk menghilangkan persilangan jalur rute. Hasil eksperimen pada 27 lokasi Jawa Barat menunjukkan bahwa PSO hibrida berhasil mengoptimalkan baseline Greedy sebesar 891.94 km menjadi 864.93 km (peningkatan efisiensi 3.03%) dalam waktu 140 ms, di mana optimasi terhenti lebih awal karena terdeteksi konvergen. Konvergensi divalidasi secara matematis menggunakan metrik diversitas partikel.
    
    #v(0.5em)
    #text(weight: "bold", style: "italic")[Kata Kunci]---Particle Swarm Optimization, TSP, Algoritma Memetik, 2-opt, Greedy Nearest Neighbor, Jawa Barat.
  ]
)

#v(2em)

// Double column layout starts here
#show: rest => columns(2, gutter: 0.6cm, rest)

= I. Pendahuluan
Traveling Salesperson Problem (TSP) merupakan salah satu masalah optimasi kombinatorial tertua dan paling intensif dipelajari dalam ilmu komputer. Tujuan TSP adalah menemukan rute siklik terpendek (Hamiltonian cycle) yang mengunjungi sekumpulan kota masing-masing tepat satu kali dan kembali ke kota asal. TSP diklasifikasikan sebagai masalah *NP-hard*, yang berarti tidak ada algoritma waktu polinomial yang diketahui dapat memecahkan seluruh instansi masalah secara eksak.

Untuk jumlah kota kecil ($N < 12$), algoritma eksak seperti *Breadth-First Search*, *Branch and Bound*, atau *A\** (dengan heuristik yang kuat seperti *Minimum Spanning Tree*) dapat menemukan rute optimal mutlak. Namun, ketika jumlah kota bertambah ($N >= 15$), ruang pencarian membengkak secara faktorial ($N!$). Sebagai contoh, untuk 27 lokasi di Jawa Barat, terdapat $27! approx 1.08 times 10^(28)$ kemungkinan rute. Algoritma eksak seperti A\* akan mengalami kehabisan memori (*RAM exhaustion*) dan waktu komputasi yang tidak terbatas.

Oleh karena itu, algoritma metaheuristik dan heuristik seperti *Greedy (Nearest Neighbor)* dan *Particle Swarm Optimization (PSO)* menjadi solusi praktis yang logis. Greedy memberikan solusi sangat cepat namun sering terjebak pada optimum lokal karena hanya mementingkan langkah terdekat lokal. Di sisi lain, PSO diskrit mampu menjelajahi ruang pencarian secara global. Makalah ini mengimplementasikan integrasi PSO diskrit dengan penyemaian Greedy dan pencarian lokal *2-opt* (disebut sebagai *Memetic PSO*) untuk menyelesaikan TSP rill di Jawa Barat.

= II. Tinjauan Pustaka
== A. Traveling Salesperson Problem (TSP)
Secara matematis, TSP dapat direpresentasikan sebagai graf berarah atau tidak berarah $G = (V, E)$ di mana $V$ adalah himpunan kota dan $E$ adalah himpunan jalur yang menghubungkan kota-kota tersebut. Jarak antara kota $i$ dan $j$ dilambangkan sebagai $d(i, j)$.

== B. Particle Swarm Optimization (PSO)
PSO diperkenalkan oleh Kennedy dan Eberhart pada tahun 1995, yang terinspirasi oleh perilaku sosial kawanan burung. Dalam PSO kontinu, setiap partikel memperbarui kecepatan ($V$) dan posisi ($X$) berdasarkan memori pribadinya (*pbest*) dan memori kelompok (*gbest*).

== C. Discrete PSO (Permutation-Based)
Karena TSP memiliki ruang keadaan diskrit berbentuk permutasi indeks kota, pembaruan aritmatika vektor standar tidak dapat diterapkan. Kita mengadopsi model aljabar swap operator yang diperkenalkan oleh Clerc untuk memperbarui posisi permutasi secara diskrit.

= III. Metodologi Penelitian
== A. Pengumpulan Data
Data kota diperoleh dari file #link("file:///c:/Users/naufa/OneDrive/Documents/Semester%206/PKK/project/kabupaten_kota_jawa_barat.csv")[kabupaten_kota_jawa_barat.csv] yang berisi nama kabupaten/kota, latitude, dan longitude. Data ini mencakup 27 lokasi geografis utama di wilayah Jawa Barat, termasuk wilayah administratif kabupaten, kota, dan lokasi penting seperti Waduk Cirata. Daftar koordinat selengkapnya ditampilkan pada Tabel 1.

#align(center)[
  #block(width: 100%)[
    #set text(size: 8pt)
    #table(
      columns: (1fr, 4fr, 2.5fr, 2.5fr),
      align: (center, left, center, center),
      stroke: 0.5pt + luma(150),
      [*No.*], [*Kabupaten / Kota*], [*Latitude*], [*Longitude*],
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
      [27], [Waduk Cirata], [-6.7552], [107.2857]
    )
    #v(-0.5em)
    #text(style: "italic", size: 7.5pt)[Tabel 1: Daftar 27 Titik Koordinat Wilayah Jawa Barat]
  ]
]


== B. Perhitungan Jarak Geodesik (Haversine)
Untuk rute geografis rill di permukaan bumi, metrik Euclidean tidak akurat karena bumi berbentuk bulat. Kami menggunakan formula Haversine:
$ a = sin^2((Delta "lat")/2) + cos("lat"_1) dot cos("lat"_2) dot sin^2((Delta "long")/2) $
$ c = 2 dot arcsin(sqrt(a)) $
$ d = R dot c $
di mana $R approx 6371$ km adalah radius rata-rata bumi.

== C. Algoritma Greedy Nearest Neighbor
Mulai dari kota indeks 0, rute dibangun dengan memilih kota belum dikunjungi terdekat berikutnya secara berulang:
$ v_(n e x t) = arg min_(u in "Unvisited") d(v_("current"), u) $
Algoritma ini selesai dalam waktu $O(N^2)$ dan menjadi baseline pembanding.

== D. Aljabar Swap Operator untuk PSO
1.  **Swap Operation $S O(i, j)$:** Pertukaran elemen pada indeks $i$ dan $j$.
2.  **Velocity ($V$):** Barisan berurutan dari swap operation:
    $ V = [S O(i_1, j_1), S O(i_2, j_2), ...] $
3.  **Pengurangan Posisi ($X_2 - X_1$):** Menghasilkan barisan swap yang mengubah rute $X_1$ menjadi $X_2$.
4.  **Perkalian Skalar ($p dot V$):** Menjaga setiap swap dalam $V$ dengan probabilitas $p in [0, 1]$.
5.  **Pembaruan Kecepatan:**
    $ V_(t+1) = w V_t + c_1 r_1 (P_(b e s t) - X_t) + c_2 r_2 (G_(b e s t) - X_t) $
    di mana $w$ adalah bobot inersia, $c_1, c_2$ adalah faktor kognitif dan sosial, dan $r_1, r_2$ adalah bilangan acak $[0, 1]$.
6.  **Pembaruan Posisi:**
    $ X_(t+1) = X_t + V_(t+1) $

== E. Optimasi Hibrida & Memetic
Untuk memastikan PSO dapat melompati performa Greedy, kami merancang dua teknik optimasi:
1.  **Heuristic Seeding:** Partikel ke-0 disemai dengan rute Greedy mentah. Ini menjamin pencarian PSO dimulai dari baseline yang kuat.
2.  **2-Opt Local Search:** Setiap kali partikel menemukan rute yang lebih baik dari global best ($G_(b e s t)$), operasi 2-opt dijalankan untuk "merapikan" rute dengan membalik sub-rute secara iteratif sampai tidak ada persilangan garis rute:
    $ "Jalur Baru" = [v_1, ..., v_(i-1), v_j, v_(j-1), ..., v_i, v_(j+1), ...] $

== F. Kriteria Berhenti Awal (Early Stopping)
Jika jarak $G_(b e s t)$ tidak berkurang lebih dari $0.01$ km selama $K$ iterasi berturut-turut (default $K=20$), loop dihentikan awal untuk menghemat waktu komputasi, yang menandakan kawanan partikel telah konvergen sepenuhnya.

= IV. Implementasi Sistem
Sistem dibangun dalam arsitektur terintegrasi:
-   **pso_engine.py:** Modul mesin perhitungan berbasis OOP Python.
-   **app.py:** Dashboard interaktif menggunakan Streamlit untuk memvisualisasikan peta interaktif Plotly, grafik konvergensi, playback slider, dan diagram performa.
-   **pso_tsp_demo.ipynb:** Notebook interaktif untuk analisis akademis visual statis (Matplotlib & Seaborn).

= V. Hasil dan Diskusi
Eksperimen dijalankan pada data 27 lokasi Jawa Barat menggunakan parameter inersia $w=0.7$, $c_1=1.5$, $c_2=1.5$, populasi partikel 20, dan batas iterasi 150. Pengujian dilakukan untuk membandingkan performa rute acak (random walk), algoritma heuristik Greedy (Nearest Neighbor), serta usulan algoritma Discrete Memetic PSO.

== A. Perbandingan Efisiensi Jarak Rute
Rangkuman perbandingan performa rute dan waktu komputasi disajikan pada Tabel 2.

#align(center)[
  #block(width: 100%)[
    #set text(size: 8pt)
    #table(
      columns: (2.5fr, 2.5fr, 2.5fr, 2fr, 2fr),
      align: (center, center, center, center, center),
      stroke: 0.5pt + luma(150),
      [*Metode Solver*], [*Jarak Rute (km)*], [*Selisih Jarak (km)*], [*Efisiensi (%)*], [*Waktu Run*],
      [Jalur Acak], [3120.40], [+2228.46], [-250.00%], [N/A],
      [Greedy NN], [891.94], [0.00 (Baseline)], [0.00% (Ref)], [2.00 ms],
      [Memetic PSO], [864.93], [-27.01], [3.03%], [140.00 ms]
    )
    #v(-0.5em)
    #text(style: "italic", size: 7.5pt)[Tabel 2: Perbandingan Performa Hasil Optimasi TSP]
  ]
]

Algoritma Memetic PSO berhasil memotong panjang rute sebesar *27.01 km* (meningkat *3.03%* lebih efisien) dibandingkan baseline Greedy. Peningkatan ini terjadi karena Greedy hanya mengambil keputusan lokal terbaik (*greedy choice property*) tanpa melihat dampak jangka panjang rute, sehingga sering kali menyisakan kota-kota terjauh di akhir pencarian yang berakibat pada "jumper" rute balik yang sangat jauh. Sebaliknya, Memetic PSO mampu mematangkan rute secara global.

== B. Analisis Waktu Komputasi
Dari aspek waktu komputasi (Tabel 2), Greedy menyelesaikan pencarian dalam waktu sangat cepat yaitu *2.00 ms* karena kompleksitasnya yang rendah ($O(N^2)$). Di lain pihak, Memetic PSO membutuhkan waktu *140.00 ms*. Perbedaan waktu ini dalam hitungan milidetik sangat tidak signifikan dibandingkan dengan keuntungan penghematan rute logistik sebesar 3.03% pada dunia nyata. Waktu komputasi PSO ini juga ditekan oleh implementasi Early Stopping yang menghentikan loop di awal pada iterasi ke-21 dari 150 batas iterasi maksimum.

== C. Analisis Konvergensi dan Diversitas Swarm
Kurva konvergensi menunjukkan bahwa semenjak iterasi awal, rute global terbaik ($G_(b e s t)$) langsung dimulai dari jarak rute Greedy ($891.94$ km) karena teknik *heuristic seeding* yang kita lakukan pada partikel ke-0. Pada iterasi ke-1, operasi 2-opt yang diterapkan pada $G_(b e s t)$ berhasil merapikan persilangan jalur rute sehingga jarak langsung turun tajam ke $864.93$ km, di mana nilai tersebut terus dipertahankan secara stabil.

== D. Analisis Visualisasi Performa Pendukung
Untuk mempermudah dosen penguji dan akademisi dalam menafsirkan performa algoritma secara komprehensif, kami menyertakan tiga visualisasi pendukung:
1. *Pairwise Distance Heatmap:* Matriks visualisasi jarak antar 27 kota Jawa Barat mengonfirmasi adanya dua kluster padat: kluster metropolitan barat (Depok, Bogor, Bekasi) dan kluster Bandung Raya (Kota Bandung, Cimahi, Bandung Barat). Kota-kota ini terhubung erat dengan jarak < 20 km. Peta panas ini membantu memahami mengapa rute optimal cenderung menyelesaikan seluruh kunjungan di dalam satu kluster sebelum melompat ke kluster berikutnya.
2. *Edge Hop Length Distribution:* Analisis frekuensi panjang sisi rute ("hop") menunjukkan bahwa rute Greedy terpaksa mengambil sisi lompatan sangat jauh (> 150 km) pada bagian penutup rute. Sedangkan pada Memetic PSO, distribusi sisi rute terpusat rapat pada jarak pendek (15 - 50 km) dengan frekuensi puncak pada rentang 15-30 km, membuktikan bahwa rute yang dihasilkan jauh lebih efisien dan terhindar dari persilangan lintasan.
3. *Swarm Diversity Analysis:* Standar deviasi fitness partikel dimulai pada tingkat tinggi ($approx 600.0$ km) di mana partikel-partikel acak tersebar merata untuk mengeksplorasi ruang pencarian. Nilai ini menyusut tajam secara eksplisit dan mencapai nilai mendekati 0 setelah iterasi ke-20, menandakan terjadinya konsensus swarm dan konvergensi stabil yang meyakinkan.

= VI. Kesimpulan
Penelitian ini membuktikan bahwa algoritma *Discrete PSO* yang dihibridisasi dengan *Greedy seeding* dan pencarian lokal *2-opt* merupakan solusi yang sangat efektif dan efisien untuk menyelesaikan TSP rill. Metode hibrida ini menjamin rute yang dihasilkan selalu lebih optimal dari heuristik greedy klasik, dengan waktu komputasi yang sangat layak di bawah 1 detik untuk 27 lokasi Jawa Barat. Untuk penelitian selanjutnya, disarankan pengujian pada data dinamis (kemacetan lalu lintas) menggunakan model Haversine-Time.

= Referensi
[1] J. Kennedy and R. Eberhart, "Particle swarm optimization," in *Proceedings of ICNN'95*, vol. 4, pp. 1942-1948, 1995.\
[2] M. Clerc, "Discrete Particle Swarm Optimization, illustrated by the Traveling Salesman Problem," *New Optimization Techniques in Engineering*, pp. 219-239, 2004.\
[3] G. Croes, "A method for solving traveling-salesman problems," *Operations Research*, vol. 6, no. 6, pp. 791-812, 1958.
