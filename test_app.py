"""
Smoke tests for app.py — syntax check and pure-helper coverage.

Streamlit is stubbed before import so tests run without a live server.
Assumes the working directory is the project root (CSV file must exist there).
"""
import py_compile
import sys
from unittest.mock import MagicMock


# ── Stub streamlit before importing app ───────────────────────────────────────
_st = MagicMock()
_st.sidebar.button.return_value = False          # prevent the PSO computation block
_st.sidebar.file_uploader.return_value = None    # use default CSV, not mock file
_st.sidebar.slider.return_value = 27             # realistic int for city count / iters
_st.sidebar.selectbox.return_value = "haversine" # valid metric string
_st.sidebar.radio.return_value = "Manual"        # skip auto-tune branch
_st.sidebar.checkbox.return_value = True
_st.sidebar.number_input.return_value = 42
# session_state as a plain dict so `in` / `[]` behave correctly
_st.session_state = {"pso_solved": False, "greedy_solved": False}
_st.columns.return_value = (MagicMock(), MagicMock())
sys.modules["streamlit"] = _st

import app  # noqa: E402 — must follow mock setup


# ── Syntax ────────────────────────────────────────────────────────────────────

def test_app_syntax():
    py_compile.compile("app.py", doraise=True)


# ── Pure helpers ──────────────────────────────────────────────────────────────

def test_route_trace_structure():
    import plotly.graph_objects as go
    coords = [(-6.9, 107.6), (-7.0, 108.0), (-7.5, 109.0)]
    trace = app._route_trace(
        route=[0, 1, 2],
        coords=coords,
        city_names=["A", "B", "C"],
        line_color="#3b82f6",
        marker_color="#3b82f6",
        marker_size=8,
        line_width=2.0,
        name="PSO",
    )
    assert isinstance(trace, go.Scattermapbox)
    assert len(trace.lat) == len(coords) + 1  # +1 for closed loop


def test_route_trace_closes_loop():
    coords = [(-6.9, 107.6), (-7.0, 108.0)]
    trace = app._route_trace(
        route=[0, 1],
        coords=coords,
        city_names=["A", "B"],
        line_color="#000",
        marker_color="#000",
        marker_size=5,
        line_width=1.0,
        name="t",
    )
    assert trace.lat[0] == trace.lat[-1]
    assert trace.lon[0] == trace.lon[-1]


def test_build_mapbox_figure_returns_figure():
    import plotly.graph_objects as go
    fig = app._build_mapbox_figure([], center_lat=-7.0, center_lon=107.6)
    assert isinstance(fig, go.Figure)


def test_build_mapbox_no_legend():
    import plotly.graph_objects as go
    fig = app._build_mapbox_figure([], center_lat=-7.0, center_lon=107.6, show_legend=False)
    assert isinstance(fig, go.Figure)
    assert fig.layout.showlegend is False


def test_chart_constants_defined():
    assert isinstance(app._CHART_LAYOUT, dict)
    assert "paper_bgcolor" in app._CHART_LAYOUT
    assert isinstance(app._COLOR_PSO, str)
    assert app._COLOR_PSO.startswith("#")
    assert isinstance(app._COLOR_GREEDY_MAP, str)
    assert app._COLOR_GREEDY_MAP.startswith("#")


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_app_syntax,
        test_route_trace_structure,
        test_route_trace_closes_loop,
        test_build_mapbox_figure_returns_figure,
        test_build_mapbox_no_legend,
        test_chart_constants_defined,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
