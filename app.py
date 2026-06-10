import random

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import pso_engine as engine

# ==========================================
# Chart helpers
# ==========================================

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=12),
    margin=dict(l=40, r=20, t=40, b=40),
)

_COLOR_PSO         = "#3b82f6"   # blue accent — PSO throughout
_COLOR_GREEDY_MAP  = "#1a1a2e"   # near-black — high contrast on light OSM map
_COLOR_GREEDY_CHART = "#64748b"  # mid-gray — monochrome for charts/tables
_COLOR_PLAY        = "#93c5fd"   # muted blue for playback map


def _route_trace(
    route: list[int],
    coords: list[tuple],
    city_names: list[str],
    line_color: str,
    marker_color: str,
    marker_size: int,
    line_width: float,
    name: str,
) -> go.Scattermapbox:
    lats  = [coords[i][0] for i in route] + [coords[route[0]][0]]
    lons  = [coords[i][1] for i in route] + [coords[route[0]][1]]
    names = [city_names[i] for i in route] + [city_names[route[0]]]
    return go.Scattermapbox(
        lat=lats, lon=lons, mode="lines+markers",
        marker=go.scattermapbox.Marker(size=marker_size, color=marker_color),
        line=dict(width=line_width, color=line_color),
        text=names, hoverinfo="text", name=name,
    )


def _build_mapbox_figure(
    traces: list,
    center_lat: float,
    center_lon: float,
    zoom: float = 7.8,
    height: int = 500,
    show_legend: bool = True,
) -> go.Figure:
    fig = go.Figure(data=traces)
    layout = dict(
        mapbox_style="open-street-map",
        mapbox_zoom=zoom,
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    if show_legend:
        layout["legend"] = dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01,
            bgcolor="rgba(15,17,23,0.75)", font=dict(size=12),
        )
    else:
        layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


# ==========================================
# Render functions
# ==========================================

def render_metrics(g_dist: float, p_dist: float, g_time: float, p_time: float) -> None:
    improvement = ((g_dist - p_dist) / g_dist) * 100 if g_dist > 0 else 0
    delta_km    = p_dist - g_dist
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Jarak Greedy (Nearest Neighbor)",
            f"{g_dist:.2f} km",
            delta=f"komputasi {g_time*1000:.1f} ms",
            delta_color="off",
        )
    with col2:
        st.metric(
            "Jarak PSO",
            f"{p_dist:.2f} km",
            delta=f"{delta_km:+.2f} km vs Greedy",
        )
    with col3:
        st.metric(
            "Efisiensi Rute",
            f"{improvement:.2f}%",
            delta=f"waktu PSO {p_time:.2f} s",
            delta_color="off",
        )


def render_map_section(
    coords: list[tuple],
    city_names: list[str],
    p_route: list[int],
    g_route: list[int],
    p_history: list[float],
    p_route_history: list[list[int]],
    center_lat: float,
    center_lon: float,
) -> None:
    st.markdown("#### Peta Rute")
    col_a, col_b = st.columns(2)
    show_pso    = col_a.checkbox("Rute PSO",    value=True)
    show_greedy = col_b.checkbox("Rute Greedy", value=False)

    traces = []
    if show_greedy:
        traces.append(_route_trace(
            g_route, coords, city_names,
            _COLOR_GREEDY_MAP, _COLOR_GREEDY_MAP, 7, 2.5, "Greedy",
        ))
    if show_pso:
        traces.append(_route_trace(
            p_route, coords, city_names,
            _COLOR_PSO, _COLOR_PSO, 9, 3, "PSO",
        ))

    start_idx = p_route[0] if show_pso else g_route[0]
    traces.append(go.Scattermapbox(
        lat=[coords[start_idx][0]], lon=[coords[start_idx][1]], mode="markers",
        marker=go.scattermapbox.Marker(size=14, color="#f8fafc"),
        text=[f"Start / End: {city_names[start_idx]}"],
        hoverinfo="text", showlegend=False,
    ))

    st.plotly_chart(
        _build_mapbox_figure(traces, center_lat, center_lon, zoom=7.8, height=460),
        use_container_width=True,
    )

    st.markdown("#### Evolusi Rute per Iterasi")
    playback_iter = st.slider(
        "Iterasi",
        min_value=0, max_value=len(p_route_history) - 1,
        value=len(p_route_history) - 1,
        label_visibility="collapsed",
    )
    iter_route = p_route_history[playback_iter]
    iter_dist  = p_history[playback_iter]

    play_traces = [_route_trace(
        iter_route, coords, city_names,
        _COLOR_PLAY, _COLOR_PLAY, 8, 2.5, "Route",
    )]
    st.plotly_chart(
        _build_mapbox_figure(play_traces, center_lat, center_lon, zoom=7.8, height=360, show_legend=False),
        use_container_width=True,
    )
    st.caption(f"Iterasi {playback_iter} — {iter_dist:.2f} km")


def render_analysis_section(
    p_history: list[float],
    g_dist: float,
    p_dist: float,
    g_time: float,
    p_time: float,
    num_cities: int,
    w: float,
    c1: float,
    c2: float,
    num_particles: int,
    max_iter: int,
    mutation_rate: float,
    best_preset_name: str,
) -> None:
    # Convergence chart
    st.markdown("#### Kurva Konvergensi")
    fig_conv = go.Figure()
    fig_conv.add_trace(go.Scatter(
        y=p_history, mode="lines",
        line=dict(color=_COLOR_PSO, width=2), name="PSO",
    ))
    fig_conv.add_trace(go.Scatter(
        x=[0, len(p_history) - 1], y=[g_dist, g_dist], mode="lines",
        line=dict(color=_COLOR_GREEDY_CHART, width=1.5, dash="dot"),
        name=f"Greedy ({g_dist:.0f} km)",
    ))
    fig_conv.update_layout(
        **_CHART_LAYOUT,
        xaxis_title="Iterasi", yaxis_title="Jarak (km)", height=260,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.1)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.1)"),
    )
    st.plotly_chart(fig_conv, use_container_width=True)

    # Comparison table
    st.markdown("#### Perbandingan Hasil")
    st.table(pd.DataFrame({
        "": ["Jarak rute", "Waktu komputasi", "Jumlah kota"],
        "Greedy": [f"{g_dist:.2f} km", f"{g_time*1000:.2f} ms", str(num_cities)],
        "PSO":    [f"{p_dist:.2f} km", f"{p_time:.3f} s",        str(num_cities)],
    }).set_index(""))

    # PSO config
    st.markdown("#### Konfigurasi PSO")
    st.dataframe(
        pd.DataFrame({
            "Parameter": ["Preset", "w (inertia)", "c1 (cognitive)", "c2 (social)",
                          "Partikel", "Maks iterasi", "Mutation rate awal"],
            "Nilai": [best_preset_name, f"{w:.2f}", f"{c1:.2f}", f"{c2:.2f}",
                      str(num_particles), str(max_iter), f"{mutation_rate:.2f}"],
        }),
        use_container_width=True, hide_index=True,
    )

    # Explanation
    with st.expander("Mengapa PSO menghasilkan rute lebih baik?"):
        st.markdown(
            "Greedy hanya memilih kota terdekat di setiap langkah — keputusan lokal yang sering "
            "menghasilkan jalur panjang di akhir rute.\n\n"
            "PSO memelihara banyak solusi (partikel) sekaligus dan membiarkan mereka saling "
            "berbagi informasi tentang rute terbaik yang pernah ditemukan. "
            "Kombinasi *personal best* dan *global best* mendorong eksplorasi ruang solusi "
            "secara global, bukan hanya lokal. "
            "2-opt local search yang dijalankan secara periodik membantu memoles rute "
            "dengan menghilangkan segmen yang bersilangan."
        )

    if "tuning_log" in st.session_state:
        with st.expander("Hasil Auto-Tuning"):
            log_df = pd.DataFrame(st.session_state["tuning_log"])
            st.dataframe(
                log_df[["name", "w", "c1", "c2", "num_particles", "score"]].rename(columns={
                    "name": "Preset", "num_particles": "Partikel", "score": "Skor (km)",
                }),
                use_container_width=True, hide_index=True,
            )
            st.caption("Skor lebih kecil = rute lebih pendek.")


def render_academic_section(
    coords: list[tuple],
    g_dist: float,
    p_dist: float,
    g_time: float,
    p_time: float,
    metric_choice: str,
) -> None:
    st.divider()
    st.markdown("#### Analisis Performa")
    col1, col2, col3 = st.columns(3)

    with col1:
        random_dists = []
        for _ in range(30):
            perm = list(range(len(coords)))
            random.shuffle(perm)
            random_dists.append(engine.calculate_route_distance(perm, coords, metric_choice))
        avg_random = float(np.mean(random_dists))

        fig = go.Figure([go.Bar(
            x=["Acak (avg)", "Greedy", "PSO"],
            y=[avg_random, g_dist, p_dist],
            text=[f"{avg_random:.0f}", f"{g_dist:.0f}", f"{p_dist:.0f}"],
            textposition="auto",
            marker_color=["#334155", _COLOR_GREEDY_CHART, _COLOR_PSO],
        )])
        fig.update_layout(
            **_CHART_LAYOUT,
            title="Jarak Rute (km)", height=300, showlegend=False,
            yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.1)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure([go.Bar(
            x=["Greedy", "PSO"],
            y=[g_time * 1000, p_time * 1000],
            text=[f"{g_time*1000:.1f}", f"{p_time*1000:.0f}"],
            textposition="auto",
            marker_color=[_COLOR_GREEDY_CHART, _COLOR_PSO],
        )])
        fig.update_layout(
            **_CHART_LAYOUT,
            title="Waktu Komputasi (ms)", height=300, showlegend=False,
            yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.1)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        if "pso_diversity" in st.session_state:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=st.session_state["pso_diversity"], mode="lines",
                line=dict(color=_COLOR_PSO, width=2),
            ))
            fig.update_layout(
                **_CHART_LAYOUT,
                title="Diversitas Swarm",
                xaxis_title="Iterasi", yaxis_title="Std Dev (km)",
                height=300, showlegend=False,
                xaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.1)"),
                yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.1)"),
            )
            st.plotly_chart(fig, use_container_width=True)


# ==========================================
# App
# ==========================================

st.set_page_config(
    page_title="TSP Optimizer — PSO vs Greedy",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.html("""
<style>
/* ---- Metric cards ---- */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 6px;
    padding: 1rem 1.25rem;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 600;
    letter-spacing: -0.01em;
}
[data-testid="stMetricLabel"] > div {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    opacity: 0.55;
}

/* ---- Expander ---- */
[data-testid="stExpander"] summary {
    font-size: 0.9rem;
    font-weight: 500;
    opacity: 0.75;
}

/* ---- Divider ---- */
hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 1.25rem 0;
}

/* ---- Section h4 ---- */
h4 {
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 0.5rem;
}
</style>
""")

# Header
st.markdown("## TSP Optimizer — Discrete PSO vs Greedy")
st.caption(
    "Perbandingan Particle Swarm Optimization dengan Greedy Nearest Neighbor "
    "untuk Travelling Salesman Problem · Data Kota/Kabupaten Jawa Barat"
)
st.divider()

# ==========================================
# Sidebar
# ==========================================
st.sidebar.markdown("### Pengaturan")

# Dataset
uploaded_file = st.sidebar.file_uploader(
    "Dataset CSV (opsional)",
    type=["csv"],
    help="Kolom yang dikenali: nama kota, latitude, longitude. "
         "Kosongkan untuk memakai dataset Jawa Barat bawaan.",
)
try:
    source = uploaded_file if uploaded_file is not None else "kabupaten_kota_jawa_barat.csv"
    df_raw = engine.load_and_filter_data(source)
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.stop()

# City count
max_cities = len(df_raw)
num_cities = st.sidebar.slider(
    "Jumlah kota", min_value=5, max_value=max_cities, value=max_cities,
    help="Kurangi untuk demo yang lebih cepat.",
)
df         = df_raw.iloc[:num_cities].reset_index(drop=True)
coords     = list(zip(df["lat"], df["long"]))
city_names = df["name"].tolist()
st.sidebar.caption(f"{num_cities} kota dipilih")

# Distance metric
metric_choice = st.sidebar.selectbox(
    "Metrik jarak",
    options=["haversine", "euclidean"],
    format_func=lambda x: "Haversine (km, bola bumi)" if x == "haversine" else "Euclidean (2D)",
)

st.sidebar.divider()
st.sidebar.markdown("### Parameter PSO")

tune_mode = st.sidebar.radio(
    "Mode",
    options=["Auto-Tune", "Manual"],
    horizontal=True,
)

w, c1, c2, num_particles, max_iter = 0.7, 1.5, 1.5, 20, 100
mutation_rate    = 0.05
best_preset_name = "Default"

if tune_mode == "Auto-Tune":
    if st.sidebar.button("Jalankan Auto-Tune"):
        with st.spinner("Mengevaluasi preset..."):
            best_config, tuning_log = engine.auto_tune_pso(coords, metric_choice)
            st.session_state["auto_pso_params"] = best_config
            st.session_state["tuning_log"]      = tuning_log
            st.sidebar.success(f"Preset terpilih: {best_config['name']}")
    if "auto_pso_params" in st.session_state:
        cfg              = st.session_state["auto_pso_params"]
        best_preset_name = cfg["name"]
        w, c1, c2, num_particles = cfg["w"], cfg["c1"], cfg["c2"], cfg["num_particles"]
        st.sidebar.caption(f"Aktif: **{best_preset_name}** — {cfg['description']}")
else:
    num_particles = st.sidebar.slider("Partikel",        10,  40,  20, step=5)
    max_iter      = st.sidebar.slider("Maks iterasi",    30, 200, 100, step=10)
    w             = st.sidebar.slider("Inertia (w)",    0.3, 1.0, 0.7, step=0.05)
    c1            = st.sidebar.slider("Cognitive (c1)", 0.5, 2.5, 1.5, step=0.1)
    c2            = st.sidebar.slider("Social (c2)",    0.5, 2.5, 1.5, step=0.1)
    mutation_rate = st.sidebar.slider("Mutation rate",  0.0, 0.3, 0.05, step=0.01)

st.sidebar.divider()
enable_early_stopping = st.sidebar.checkbox("Early stopping", value=True)
early_stopping_rounds = None
if enable_early_stopping:
    early_stopping_rounds = st.sidebar.slider("Toleransi (iterasi tanpa peningkatan)", 5, 50, 20, step=5)

st.sidebar.divider()
pso_seed_input = st.sidebar.number_input(
    "Seed (-1 = acak)",
    min_value=-1, max_value=9999, value=42, step=1,
    help="Seed yang sama menghasilkan rute identik — berguna untuk demo.",
)
seed_value = None if pso_seed_input == -1 else int(pso_seed_input)

run_pso = st.sidebar.button("Run", use_container_width=True, type="primary")

# ==========================================
# Computation
# ==========================================
col_map, col_analysis = st.columns([3, 2])

if "pso_solved" not in st.session_state:
    st.session_state["pso_solved"]    = False
    st.session_state["greedy_solved"] = False

if run_pso:
    greedy_solver = engine.GreedyTSPSolver(coords, metric_choice)
    g_route, g_distance, g_time = greedy_solver.solve()
    st.session_state.update({
        "greedy_route": g_route, "greedy_distance": g_distance,
        "greedy_time": g_time, "greedy_solved": True,
    })

    progress_bar = st.progress(0, text="Menginisialisasi swarm...")
    status_text  = st.empty()

    def pso_callback(it: int, max_it: int, dist: float) -> None:
        progress_bar.progress(
            int((it / max_it) * 100),
            text=f"Iterasi {it}/{max_it} — best: {dist:.2f} km",
        )

    pso_solver = engine.PSOSolver(
        coords=coords, metric=metric_choice, num_particles=num_particles,
        max_iter=max_iter, w=w, c1=c1, c2=c2, mutation_rate=mutation_rate,
        seed=seed_value, early_stopping_rounds=early_stopping_rounds,
    )
    st.session_state["max_iter"]             = max_iter
    st.session_state["early_stopping_rounds"] = early_stopping_rounds

    pso_route, pso_distance, pso_time = pso_solver.solve(progress_callback=pso_callback)
    st.session_state.update({
        "pso_route": pso_route, "pso_distance": pso_distance, "pso_time": pso_time,
        "pso_history": pso_solver.history, "pso_route_history": pso_solver.route_history,
        "pso_diversity": pso_solver.diversity_history, "pso_solved": True,
    })
    status_text.empty()
    progress_bar.empty()

# ==========================================
# Results
# ==========================================
if st.session_state["pso_solved"] and st.session_state["greedy_solved"]:
    p_dist          = st.session_state["pso_distance"]
    g_dist          = st.session_state["greedy_distance"]
    p_history       = st.session_state["pso_history"]
    p_route         = st.session_state["pso_route"]
    g_route         = st.session_state["greedy_route"]
    p_route_history = st.session_state["pso_route_history"]
    p_time          = st.session_state["pso_time"]
    g_time          = st.session_state["greedy_time"]

    actual_iters = len(p_history) - 1
    target_iters = st.session_state.get("max_iter", 100)
    es_rounds    = st.session_state.get("early_stopping_rounds", None)
    if es_rounds is not None and actual_iters < target_iters:
        st.info(
            f"Early stopping pada iterasi **{actual_iters}** "
            f"(tidak ada peningkatan selama {es_rounds} iterasi)."
        )

    render_metrics(g_dist, p_dist, g_time, p_time)

    center_lat = float(np.mean([c[0] for c in coords]))
    center_lon = float(np.mean([c[1] for c in coords]))

    with col_map:
        render_map_section(
            coords, city_names, p_route, g_route,
            p_history, p_route_history, center_lat, center_lon,
        )

    with col_analysis:
        render_analysis_section(
            p_history, g_dist, p_dist, g_time, p_time,
            num_cities, w, c1, c2, num_particles, max_iter,
            mutation_rate, best_preset_name,
        )

    render_academic_section(coords, g_dist, p_dist, g_time, p_time, metric_choice)

else:
    st.info("Atur parameter di sidebar lalu klik **Run**.")
    st.markdown("#### Dataset")
    st.dataframe(
        df[["name", "lat", "long"]].rename(columns={
            "name": "Kota / Kabupaten", "lat": "Latitude", "long": "Longitude",
        }),
        use_container_width=True,
    )
    st.divider()
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("**Swarm Intelligence**")
        st.markdown(
            "Meniru perilaku kawanan burung atau ikan dalam mencari sumber makanan. "
            "Tiap partikel menyesuaikan arahnya berdasarkan pengalaman pribadi "
            "(*personal best*) dan kesuksesan kawanan (*global best*)."
        )
    with col_2:
        st.markdown("**Operator Swap Permutasi**")
        st.markdown(
            "Rute TSP adalah masalah urutan (diskrit), sehingga kecepatan partikel "
            "direpresentasikan sebagai urutan operasi tukar-posisi (*swap sequence*). "
            "Setiap partikel memperbarui rutenya dengan menerapkan swap agar "
            "mendekati *pbest* dan *gbest*."
        )
