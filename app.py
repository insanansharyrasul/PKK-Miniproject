import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pso_engine as engine
import time
import importlib

# Force reload engine to prevent caching issues when editing pso_engine.py
importlib.reload(engine)

# Set page configurations
st.set_page_config(
    page_title="PSO vs Greedy TSP Optimizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for premium aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Gradient Banner */
    .banner {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 50%, #1e3a8a 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .banner h1 {
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
        color: white !important;
    }
    .banner p {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Modern Card Overrides */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* Metric Card Custom Styles */
    .metric-container {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    .m-card {
        flex: 1;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        color: #1e293b;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 6px solid #e2e8f0;
    }
    .m-card-title {
        font-size: 0.875rem;
        text-transform: uppercase;
        font-weight: 600;
        color: #64748b;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .m-card-value {
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    .m-card-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    .pso-theme {
        border-left-color: #2563eb;
        background: linear-gradient(to right, #eff6ff, #ffffff);
    }
    .greedy-theme {
        border-left-color: #dc2626;
        background: linear-gradient(to right, #fef2f2, #ffffff);
    }
    .improve-theme {
        border-left-color: #16a34a;
        background: linear-gradient(to right, #f0fdf4, #ffffff);
    }
</style>
""", unsafe_allow_html=True)

# Main Dashboard Banner
st.markdown("""
<div class="banner">
    <h1>Optimasi Rute TSP Menggunakan Discrete PSO</h1>
    <p>Penerapan komputasi cerdas berbasis swarm intelligence untuk rute optimal di Jawa Barat</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# Sidebar Configuration
# ==========================================
st.sidebar.image("https://img.icons8.com/clouds/100/swarm.png", width=80)
st.sidebar.markdown("### ⚙️ Pengaturan Solver")

# 1. Load data from the West Java dataset
try:
    df_raw = engine.load_and_filter_data("kabupaten_kota_jawa_barat.csv")
    region_choice = 'jabar' # Kept as constant for map zoom logic
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.warning("💡 **Tips:** Jika error berkaitan dengan kolom `'id'` atau caching, silakan restart server Streamlit Anda (tekan **Ctrl+C** di terminal tempat Streamlit berjalan, lalu jalankan kembali **`streamlit run app.py`**) untuk membersihkan cache impor Python.")
    st.stop()

# 2. Number of cities sampler
max_cities = len(df_raw)
num_cities = st.sidebar.slider(
    "🔢 Batasi Jumlah Kota",
    min_value=5,
    max_value=max_cities,
    value=max_cities,
    help="Gunakan jumlah kota yang lebih kecil untuk mempercepat running & demo."
)

# Slice dataset
df = df_raw.iloc[:num_cities].reset_index(drop=True)
coords = list(zip(df['lat'], df['long']))
city_names = df['name'].tolist()

# Show statistics in sidebar
st.sidebar.markdown(f"**Total Kota Terpilih:** `{num_cities}`")

# 3. Distance Metric
metric_choice = st.sidebar.selectbox(
    "📏 Metrik Jarak",
    options=["haversine", "euclidean"],
    format_func=lambda x: "Haversine (Rute Bola Bumi - km)" if x == "haversine" else "Euclidean (Jarak 2D Rata)"
)

# 4. Parameter Tuning Mode
tune_mode = st.sidebar.radio(
    "🧠 Mode Parameter PSO",
    options=["Auto-Tune (Direkomendasikan)", "Manual Tuning"]
)

# Default parameter configurations
w, c1, c2, num_particles, max_iter = 0.7, 1.5, 1.5, 20, 100
mutation_rate = 0.05
best_preset_name = "Default"
preset_desc = ""

if tune_mode == "Auto-Tune (Direkomendasikan)":
    st.sidebar.info("Auto-Tuning akan melakukan evaluasi cepat untuk memilih parameter terbaik.")
    if st.sidebar.button("⚙️ Jalankan Auto-Tune"):
        with st.spinner("Mengevaluasi preset parameter..."):
            best_config, tuning_log = engine.auto_tune_pso(coords, metric_choice)
            st.session_state['auto_pso_params'] = best_config
            st.session_state['tuning_log'] = tuning_log
            st.sidebar.success(f"Tuned: {best_config['name']}")
            
    if 'auto_pso_params' in st.session_state:
        cfg = st.session_state['auto_pso_params']
        best_preset_name = cfg['name']
        w, c1, c2, num_particles = cfg['w'], cfg['c1'], cfg['c2'], cfg['num_particles']
        preset_desc = cfg['description']
        st.sidebar.markdown(f"**Preset Aktif:** `{best_preset_name}`")
        st.sidebar.markdown(f"<small>{preset_desc}</small>", unsafe_allow_html=True)
else:
    # Manual Sliders
    num_particles = st.sidebar.slider("👥 Jumlah Partikel", 10, 40, 20, step=5)
    max_iter = st.sidebar.slider("🔄 Maksimum Iterasi", 30, 200, 100, step=10)
    w = st.sidebar.slider("🧱 Inertia Weight (w)", 0.3, 1.0, 0.7, step=0.05)
    c1 = st.sidebar.slider("👤 Cognitive Coefficient (c1)", 0.5, 2.5, 1.5, step=0.1)
    c2 = st.sidebar.slider("👥 Social Coefficient (c2)", 0.5, 2.5, 1.5, step=0.1)
    mutation_rate = st.sidebar.slider("🧬 Mutation Rate", 0.0, 0.3, 0.05, step=0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛑 Pengendalian Swarm (Early Stopping)")
enable_early_stopping = st.sidebar.checkbox("Aktifkan Early Stopping", value=True)
early_stopping_rounds = None
if enable_early_stopping:
    early_stopping_rounds = st.sidebar.slider("Batas Iterasi Tanpa Peningkatan", 5, 50, 20, step=5)

# Run button
run_pso = st.sidebar.button("🚀 Run Optimasi TSP", use_container_width=True)

# ==========================================
# Main Layout Logic
# ==========================================
col_map, col_analysis = st.columns([3, 2])

# Initialize session state for solutions
if 'pso_solved' not in st.session_state:
    st.session_state['pso_solved'] = False
    st.session_state['greedy_solved'] = False

# Run calculations when button is clicked
if run_pso:
    # 1. Solve Greedy (Instant)
    greedy_solver = engine.GreedyTSPSolver(coords, metric_choice)
    g_route, g_distance, g_time = greedy_solver.solve()
    st.session_state['greedy_route'] = g_route
    st.session_state['greedy_distance'] = g_distance
    st.session_state['greedy_time'] = g_time
    st.session_state['greedy_solved'] = True
    
    # 2. Solve PSO (Show progress bar)
    progress_bar = st.progress(0, text="Menginisialisasi swarm...")
    status_text = st.empty()
    
    def pso_callback(it, max_it, dist):
        pct = int((it / max_it) * 100)
        progress_bar.progress(pct, text=f"Iterasi {it}/{max_it} | Best Jarak: {dist:.2f} km")
        
    pso_solver = engine.PSOSolver(
        coords=coords,
        metric=metric_choice,
        num_particles=num_particles,
        max_iter=max_iter,
        w=w,
        c1=c1,
        c2=c2,
        mutation_rate=mutation_rate,
        seed=42,
        early_stopping_rounds=early_stopping_rounds
    )
    st.session_state['max_iter'] = max_iter
    st.session_state['early_stopping_rounds'] = early_stopping_rounds
    
    pso_route, pso_distance, pso_time = pso_solver.solve(progress_callback=pso_callback)
    
    st.session_state['pso_route'] = pso_route
    st.session_state['pso_distance'] = pso_distance
    st.session_state['pso_time'] = pso_time
    st.session_state['pso_history'] = pso_solver.history
    st.session_state['pso_route_history'] = pso_solver.route_history
    st.session_state['pso_diversity'] = pso_solver.diversity_history
    st.session_state['pso_solved'] = True
    
    status_text.empty()
    progress_bar.empty()

# ==========================================
# Rendering Output UI
# ==========================================
if st.session_state['pso_solved'] and st.session_state['greedy_solved']:
    p_dist = st.session_state['pso_distance']
    g_dist = st.session_state['greedy_distance']
    p_history = st.session_state['pso_history']
    
    # Early Stopping Notification
    actual_iters = len(p_history) - 1
    target_iters = st.session_state.get('max_iter', 100)
    es_rounds = st.session_state.get('early_stopping_rounds', None)
    if es_rounds is not None and actual_iters < target_iters:
        st.success(f"🛑 **Early Stopping Dipicu:** Proses optimasi dihentikan lebih awal pada iterasi **{actual_iters}** karena rute tidak mengalami peningkatan jarak selama **{es_rounds}** iterasi berturut-turut (konvergen).")
    p_time = st.session_state['pso_time']
    g_time = st.session_state['greedy_time']
    p_route = st.session_state['pso_route']
    g_route = st.session_state['greedy_route']
    p_history = st.session_state['pso_history']
    p_route_history = st.session_state['pso_route_history']
    
    improvement = ((g_dist - p_dist) / g_dist) * 100 if g_dist > 0 else 0
    
    # Render Metrics Section
    st.markdown(f"""
    <div class="metric-container">
        <div class="m-card greedy-theme">
            <div class="m-card-title">🔴 Greedy Baseline</div>
            <div class="m-card-value">{g_dist:.2f} km</div>
            <div class="m-card-sub">Waktu: {g_time*1000:.2f} ms (Nearest Neighbor)</div>
        </div>
        <div class="m-card pso-theme">
            <div class="m-card-title">🔵 Optimasi PSO</div>
            <div class="m-card-value">{p_dist:.2f} km</div>
            <div class="m-card-sub">Waktu: {p_time:.3f} s (Swarm Intelligence)</div>
        </div>
        <div class="m-card improve-theme">
            <div class="m-card-title">🟢 Efisiensi Rute</div>
            <div class="m-card-value">{improvement:.2f}% Lebih Pendek</div>
            <div class="m-card-sub">Jalur PSO lebih optimal dibanding Greedy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Map Column ---
    with col_map:
        st.markdown("### 🗺️ Peta Interaktif Rute")
        
        # Checkboxes for layers
        show_pso = st.checkbox("Tampilkan Rute PSO (Biru)", value=True)
        show_greedy = st.checkbox("Tampilkan Rute Greedy (Merah)", value=False)
        
        # Build Map figure
        fig = go.Figure()
        
        # Draw Greedy Route
        if show_greedy:
            g_lats = [coords[i][0] for i in g_route] + [coords[g_route[0]][0]]
            g_lons = [coords[i][1] for i in g_route] + [coords[g_route[0]][1]]
            g_names = [city_names[i] for i in g_route] + [city_names[g_route[0]]]
            
            fig.add_trace(go.Scattermapbox(
                lat=g_lats,
                lon=g_lons,
                mode="lines+markers",
                marker=go.scattermapbox.Marker(size=8, color="#ef4444"),
                line=dict(width=2.5, color="#f87171"),
                text=g_names,
                hoverinfo="text",
                name="Rute Greedy"
            ))
            
        # Draw PSO Route
        if show_pso:
            p_lats = [coords[i][0] for i in p_route] + [coords[p_route[0]][0]]
            p_lons = [coords[i][1] for i in p_route] + [coords[p_route[0]][1]]
            p_names = [city_names[i] for i in p_route] + [city_names[p_route[0]]]
            
            fig.add_trace(go.Scattermapbox(
                lat=p_lats,
                lon=p_lons,
                mode="lines+markers",
                marker=go.scattermapbox.Marker(size=10, color="#2563eb"),
                line=dict(width=3.5, color="#3b82f6"),
                text=p_names,
                hoverinfo="text",
                name="Rute PSO"
            ))
            
        # Highlight Start City (Asterisk or Big Marker)
        start_idx = p_route[0] if show_pso else g_route[0]
        fig.add_trace(go.Scattermapbox(
            lat=[coords[start_idx][0]],
            lon=[coords[start_idx][1]],
            mode="markers",
            marker=go.scattermapbox.Marker(size=16, color="#1e293b", symbol="circle"),
            text=[f"📍 Mulai & Akhir: {city_names[start_idx]}"],
            hoverinfo="text",
            showlegend=False
        ))
        
        # Center coordinates
        center_lat = np.mean([c[0] for c in coords])
        center_lon = np.mean([c[1] for c in coords])
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=7.8 if region_choice == 'jabar' else 8.8,
            mapbox_center={"lat": center_lat, "lon": center_lon},
            margin={"r":0,"t":0,"l":0,"b":0},
            height=500,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255, 255, 255, 0.8)"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Playback Evolution Slider
        st.markdown("### 🔄 Iteration Playback (Evolusi Rute PSO)")
        playback_iter = st.slider(
            "Geser slider untuk melihat peningkatan rute di setiap iterasi PSO:",
            min_value=0,
            max_value=len(p_route_history) - 1,
            value=len(p_route_history) - 1
        )
        
        iter_route = p_route_history[playback_iter]
        iter_dist = p_history[playback_iter]
        
        # Build playback map
        fig_play = go.Figure()
        play_lats = [coords[i][0] for i in iter_route] + [coords[iter_route[0]][0]]
        play_lons = [coords[i][1] for i in iter_route] + [coords[iter_route[0]][1]]
        play_names = [city_names[i] for i in iter_route] + [city_names[iter_route[0]]]
        
        fig_play.add_trace(go.Scattermapbox(
            lat=play_lats,
            lon=play_lons,
            mode="lines+markers",
            marker=go.scattermapbox.Marker(size=9, color="#10b981"),
            line=dict(width=3, color="#34d399"),
            text=play_names,
            hoverinfo="text",
            name="Route"
        ))
        
        fig_play.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=7.8 if region_choice == 'jabar' else 8.8,
            mapbox_center={"lat": center_lat, "lon": center_lon},
            margin={"r":0,"t":0,"l":0,"b":0},
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_play, use_container_width=True)
        st.caption(f"**Iterasi ke-{playback_iter}** | Jarak rute pada iterasi ini: `{iter_dist:.2f} km`")

    # --- Analysis Column ---
    with col_analysis:
        st.markdown("### 📈 Grafik Konvergensi")
        
        # Line plot for convergence
        fig_conv = go.Figure()
        fig_conv.add_trace(go.Scatter(
            y=p_history,
            mode='lines',
            line=dict(color='#2563eb', width=3),
            name='PSO Convergence'
        ))
        # Horizontal line for Greedy
        fig_conv.add_trace(go.Scatter(
            x=[0, len(p_history)-1],
            y=[g_dist, g_dist],
            mode='lines',
            line=dict(color='#dc2626', width=2, dash='dash'),
            name=f'Greedy Baseline ({g_dist:.1f} km)'
        ))
        
        fig_conv.update_layout(
            title="Peningkatan Rute terhadap Waktu (Iterasi)",
            xaxis_title="Iterasi",
            yaxis_title="Jarak Tempuh (km)",
            height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_conv, use_container_width=True)
        
        # Detailed stats comparison
        st.markdown("### 📊 Statistik Perbandingan Detail")
        data_table = {
            "Metrik": ["Jarak Rute (Lebih Pendek = Baik)", "Waktu Proses (Lebih Cepat = Baik)", "Jumlah Titik Kota"],
            "Greedy Baseline": [f"{g_dist:.2f} km", f"{g_time*1000:.2f} ms", f"{num_cities} Kota"],
            "PSO Optimizer": [f"{p_dist:.2f} km", f"{p_time:.3f} s", f"{num_cities} Kota"]
        }
        st.table(pd.DataFrame(data_table))
        
        # Parameters information card
        st.markdown("### 🧠 Detail Konfigurasi PSO")
        param_data = {
            "Parameter": ["Preset Aktif", "Inertia Weight (w)", "Cognitive (c1)", "Social (c2)", "Partikel Swarm", "Maks Iterasi", "Mutation Rate"],
            "Nilai": [best_preset_name, f"{w:.2f}", f"{c1:.2f}", f"{c2:.2f}", str(num_particles), str(max_iter), f"{mutation_rate:.2f}"]
        }
        st.dataframe(pd.DataFrame(param_data), use_container_width=True, hide_index=True)
        
        # Explanations
        st.markdown("""
        <div class="card">
            <h4>💡 Mengapa Rute PSO Lebih Baik?</h4>
            <p style='font-size: 0.9rem; color: #475569;'>
                Algoritma <b>Greedy</b> hanya melihat opsi terbaik secara lokal (kota terdekat dari kota saat ini). 
                Hal ini sering menghasilkan jalur putar balik yang sangat panjang di akhir rute karena kota-kota yang tersisa letaknya saling berjauhan.
                <br><br>
                <b>PSO</b> memelihara sekumpulan solusi alternatif (partikel) yang saling bertukar informasi. 
                Melalui interaksi antara kecerdasan individual (personal best) dan sosial (global best), 
                partikel melakukan pencarian rute global yang jauh lebih optimal, menghindari jebakan optimum lokal.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'tuning_log' in st.session_state:
            with st.expander("🔍 Lihat Hasil Auto-Tuning Preset"):
                log_df = pd.DataFrame(st.session_state['tuning_log'])
                st.dataframe(
                    log_df[['name', 'w', 'c1', 'c2', 'num_particles', 'score']],
                    column_config={
                        "name": "Nama Preset",
                        "w": "w", "c1": "c1", "c2": "c2", 
                        "num_particles": "Partikel",
                        "score": "Skor Evaluasi (Jarak Rute Akhir)"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                st.caption("Skor evaluasi lebih kecil berarti preset tersebut menghasilkan jarak rute akhir yang lebih pendek.")
                
        # --- Full Width Academic Performance Analysis Section ---
        st.markdown("---")
        st.markdown("## 📊 Analisis Performa Akademik (Laporan & Dokumentasi)")
        st.caption("Gunakan data dan diagram di bawah ini untuk disertakan dalam laporan tugas akhir atau slide presentasi Anda.")
        
        col_perf1, col_perf2, col_perf3 = st.columns(3)
        
        # 1. Distance Bar Chart
        with col_perf1:
            # Compute average random route distance for context
            random_dists = []
            for _ in range(30):
                r_perm = list(range(len(coords)))
                random.shuffle(r_perm)
                random_dists.append(engine.calculate_route_distance(r_perm, coords, metric_choice))
            avg_random_dist = np.mean(random_dists)
            
            fig_bar_dist = go.Figure([go.Bar(
                x=['Jalur Acak (Avg)', 'Greedy NN', 'PSO Optimized'],
                y=[avg_random_dist, g_dist, p_dist],
                text=[f"{avg_random_dist:.1f} km", f"{g_dist:.1f} km", f"{p_dist:.1f} km"],
                textposition='auto',
                marker_color=['#94a3b8', '#f87171', '#3b82f6']
            )])
            fig_bar_dist.update_layout(
                title="<b>Perbandingan Jarak Rute</b>",
                yaxis_title="Jarak Tempuh (km)",
                height=320,
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=False
            )
            st.plotly_chart(fig_bar_dist, use_container_width=True)
            st.caption("Menunjukkan reduksi jarak dari rute acak (tanpa kecerdasan), greedy, hingga optimasi final PSO.")

        # 2. Time Bar Chart
        with col_perf2:
            fig_bar_time = go.Figure([go.Bar(
                x=['Greedy Solver', 'PSO Solver'],
                y=[g_time * 1000, p_time * 1000],
                text=[f"{g_time*1000:.2f} ms", f"{p_time*1000:.1f} ms"],
                textposition='auto',
                marker_color=['#f87171', '#3b82f6']
            )])
            fig_bar_time.update_layout(
                title="<b>Perbandingan Waktu Komputasi</b>",
                yaxis_title="Waktu Proses (milidetik)",
                height=320,
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=False
            )
            st.plotly_chart(fig_bar_time, use_container_width=True)
            st.caption("Menunjukkan trade-off komputasi: Greedy sangat cepat, sedangkan PSO membutuhkan lebih banyak waktu untuk optimasi global.")

        # 3. Particle Diversity Line Chart
        with col_perf3:
            if 'pso_diversity' in st.session_state:
                fig_line_div = go.Figure()
                fig_line_div.add_trace(go.Scatter(
                    y=st.session_state['pso_diversity'],
                    mode='lines',
                    line=dict(color='#10b981', width=3),
                    name='Swarm Diversity'
                ))
                fig_line_div.update_layout(
                    title="<b>Kurva Diversitas Swarm (Konvergensi)</b>",
                    xaxis_title="Iterasi",
                    yaxis_title="Std Dev Jarak Partikel (km)",
                    height=320,
                    margin=dict(l=20, r=20, t=50, b=20),
                    showlegend=False
                )
                st.plotly_chart(fig_line_div, use_container_width=True)
                st.caption("Mengukur konvergensi matematika: Seiring bertambahnya iterasi, diversitas menyusut mendekati 0 karena seluruh partikel berkumpul ke rute terbaik.")
 
else:
    # App initial state (waiting for run)
    st.info("👈 Silakan atur konfigurasi solver di sidebar lalu klik tombol **Run Optimasi TSP** untuk memulai perhitungan dan visualisasi.")
    
    st.markdown("### 📋 Gambaran Dataset Kota Terpilih")
    st.dataframe(
        df[['id', 'name', 'lat', 'long']],
        column_config={
            "id": "ID Wilayah",
            "name": "Nama Kabupaten / Kota",
            "lat": "Latitude (Lintang)",
            "long": "Longitude (Bujur)"
        },
        use_container_width=True
    )
    
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("""
        ### 🧠 Konsep Swarm Intelligence
        Metode ini meniru perilaku alamiah koloni hewan seperti kawanan burung atau sekolah ikan dalam mencari sumber makanan. 
        Masing-masing individu (partikel) berkolaborasi mencari koordinat terbaik dalam ruang dimensi-N dengan menyesuaikan arah terbangnya 
        berdasarkan pengalaman pribadi suksesnya sendiri serta kesuksesan kawanan secara kolektif.
        """)
    with col_2:
        st.markdown("""
        ### ⚙️ Operator Swap Permutasi
        Karena rute TSP adalah masalah urutan (diskrit), representasi kecepatan diubah menjadi urutan operasi pertukaran indeks (*swap sequence*). 
        Setiap partikel memperbarui rutenya dengan menerapkan serangkaian pertukaran kota agar rute miliknya secara bertahap menyerupai 
        rute terbaik milik pribadinya (*pbest*) dan rute terbaik dari seluruh populasi (*gbest*).
        """)
