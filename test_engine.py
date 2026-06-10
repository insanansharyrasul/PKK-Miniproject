"""
Smoke tests for pso_engine.py.
Run: python test_engine.py
"""
import random as _random

import pso_engine as engine


# ── Distance functions ─────────────────────────────────────────────────────────

def test_haversine_same_point():
    assert engine.haversine_distance(0, 0, 0, 0) == 0.0


def test_haversine_known_distance():
    # Jakarta (-6.2, 106.8) to Bandung (-6.9, 107.6) ~approx 120 km
    d = engine.haversine_distance(-6.2, 106.8, -6.9, 107.6)
    assert 100 < d < 150, f"Expected ~120 km, got {d:.1f}"


def test_euclidean_same_point():
    assert engine.euclidean_distance(1, 2, 1, 2) == 0.0


def test_euclidean_symmetry():
    d1 = engine.euclidean_distance(0, 0, 3, 4)
    d2 = engine.euclidean_distance(3, 4, 0, 0)
    assert abs(d1 - d2) < 1e-9


# ── Route distance ─────────────────────────────────────────────────────────────

def test_calculate_route_distance_single_city():
    assert engine.calculate_route_distance([0], [(0, 0)], 'haversine') == 0.0


def test_calculate_route_distance_positive():
    coords = [(-6.2, 106.8), (-6.9, 107.6), (-7.0, 108.0)]
    d = engine.calculate_route_distance([0, 1, 2], coords, 'haversine')
    assert d > 0


# ── Greedy solver ──────────────────────────────────────────────────────────────

def test_greedy_returns_full_route():
    coords = [(-6.2, 106.8), (-6.9, 107.6), (-7.0, 108.0), (-7.5, 109.0)]
    route, dist, t = engine.GreedyTSPSolver(coords).solve()
    assert len(route) == len(coords)
    assert dist > 0 and t >= 0


def test_greedy_visits_all_cities():
    coords = [(-6.2, 106.8), (-6.9, 107.6), (-7.0, 108.0)]
    route, _, _ = engine.GreedyTSPSolver(coords).solve()
    assert sorted(route) == list(range(len(coords)))


# ── Velocity helpers ───────────────────────────────────────────────────────────

def test_scale_velocity_clamps_high_probability():
    """With p >> 1, scale_velocity must still return at most len(input) items."""
    swaps = [engine.SwapOperation(i, i + 1) for i in range(10)]
    result = engine.scale_velocity(swaps, p=100.0)
    assert len(result) <= len(swaps)


def test_scale_velocity_zero_probability():
    swaps = [engine.SwapOperation(0, 1), engine.SwapOperation(2, 3)]
    assert engine.scale_velocity(swaps, p=0.0) == []


def test_apply_velocity_is_permutation():
    route = [0, 1, 2, 3, 4]
    swaps = [engine.SwapOperation(0, 2), engine.SwapOperation(1, 3)]
    result = engine.apply_velocity(route, swaps)
    assert sorted(result) == sorted(route)


def test_get_swap_sequence_round_trip():
    r1 = [0, 1, 2, 3, 4]
    r2 = [3, 1, 4, 0, 2]
    seq     = engine.get_swap_sequence(r1, r2)
    applied = engine.apply_velocity(r1, seq)
    assert applied == r2


# ── PSO solver ─────────────────────────────────────────────────────────────────

def test_pso_returns_valid_route():
    coords = [(-6.2, 106.8), (-6.9, 107.6), (-7.0, 108.0), (-7.5, 109.0), (-6.5, 107.0)]
    route, dist, t = engine.PSOSolver(coords, num_particles=5, max_iter=10, seed=42).solve()
    assert sorted(route) == list(range(len(coords)))
    assert dist > 0


def test_pso_velocity_cap_respected():
    """Particle velocity length must not exceed num_cities // 2 after updates."""
    coords = [(-6.2 + i * 0.1, 106.8 + i * 0.1) for i in range(10)]
    solver = engine.PSOSolver(coords, num_particles=5, max_iter=5, seed=0)
    solver.solve()
    max_vel = max(1, len(coords) // 2)
    for p in solver.particles:
        assert len(p.velocity) <= max_vel, (
            f"Velocity length {len(p.velocity)} exceeds cap {max_vel}"
        )


def test_pso_history_non_increasing():
    """Global best distance must be monotonically non-increasing."""
    coords = [(-6.2, 106.8), (-6.9, 107.6), (-7.0, 108.0), (-7.5, 109.0), (-6.5, 107.0)]
    solver = engine.PSOSolver(coords, num_particles=5, max_iter=20, seed=1)
    solver.solve()
    for i in range(1, len(solver.history)):
        assert solver.history[i] <= solver.history[i - 1] + 1e-6, (
            f"History increased at iteration {i}: {solver.history[i-1]:.2f} → {solver.history[i]:.2f}"
        )


def test_pso_improves_over_greedy():
    """PSO with 2-opt should match or beat Greedy on a mid-size instance."""
    coords = [(-6.2, 106.8), (-6.9, 107.6), (-7.0, 108.0),
              (-7.5, 109.0), (-6.5, 107.0), (-6.0, 106.5), (-7.2, 108.5)]
    _, g_dist, _ = engine.GreedyTSPSolver(coords).solve()
    _, p_dist, _ = engine.PSOSolver(coords, num_particles=10, max_iter=30, seed=42).solve()
    assert p_dist <= g_dist * 1.05, (
        f"PSO ({p_dist:.1f}) significantly worse than Greedy ({g_dist:.1f})"
    )


def test_pso_diversity_history_length():
    coords = [(-6.2 + i * 0.05, 106.8) for i in range(6)]
    solver = engine.PSOSolver(coords, num_particles=4, max_iter=10, seed=7)
    solver.solve()
    assert len(solver.diversity_history) == len(solver.history)


# ── Data loading ───────────────────────────────────────────────────────────────

def test_load_default_csv():
    df = engine.load_and_filter_data("kabupaten_kota_jawa_barat.csv")
    assert len(df) > 0
    assert set(['id', 'name', 'lat', 'long']).issubset(df.columns)
    assert df['lat'].notna().all()
    assert df['long'].notna().all()


# ── Runner ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_haversine_same_point,
        test_haversine_known_distance,
        test_euclidean_same_point,
        test_euclidean_symmetry,
        test_calculate_route_distance_single_city,
        test_calculate_route_distance_positive,
        test_greedy_returns_full_route,
        test_greedy_visits_all_cities,
        test_scale_velocity_clamps_high_probability,
        test_scale_velocity_zero_probability,
        test_apply_velocity_is_permutation,
        test_get_swap_sequence_round_trip,
        test_pso_returns_valid_route,
        test_pso_velocity_cap_respected,
        test_pso_history_non_increasing,
        test_pso_improves_over_greedy,
        test_pso_diversity_history_length,
        test_load_default_csv,
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
