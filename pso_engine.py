from __future__ import annotations

import random
import time
from typing import Any

import numpy as np
import pandas as pd

# ── Type aliases ──────────────────────────────────────────────────────────────
Coords = list[tuple[float, float]]
Route  = list[int]

# ── Column name aliases for CSV auto-detection ────────────────────────────────
_NAME_ALIASES = ['Kabupaten_Kota', 'kabupaten_kota', 'name', 'Name', 'kota', 'Kota', 'city', 'wilayah']
_LAT_ALIASES  = ['Latitude', 'latitude', 'lat', 'Lat', 'y', 'Y']
_LONG_ALIASES = ['Longitude', 'longitude', 'long', 'Long', 'lon', 'Lon', 'x', 'X']


# ==========================================
# 1. Data Cleaning & Region Filtering
# ==========================================

def _detect_column(df_cols: list[str], aliases: list[str]) -> str:
    for alias in aliases:
        if alias in df_cols:
            return alias
    raise ValueError(
        f"Kolom tidak ditemukan. Tersedia: {df_cols}. "
        f"Diharapkan salah satu dari: {aliases}"
    )


def load_and_filter_data(csv_path: Any = "kabupaten_kota_jawa_barat.csv") -> pd.DataFrame:
    """
    Loads and standardizes a kabupaten/kota CSV dataset.
    Accepts a file path string or a file-like object (e.g. Streamlit UploadedFile).
    Auto-detects column names for name, latitude, and longitude.
    """
    df = pd.read_csv(csv_path)
    cols = list(df.columns)

    name_col = _detect_column(cols, _NAME_ALIASES)
    lat_col  = _detect_column(cols, _LAT_ALIASES)
    long_col = _detect_column(cols, _LONG_ALIASES)

    df['lat']  = pd.to_numeric(df[lat_col],  errors='coerce')
    df['long'] = pd.to_numeric(df[long_col], errors='coerce')
    df['name'] = df[name_col].astype(str).str.strip()
    df['id']   = df.index

    df = df.dropna(subset=['name', 'lat', 'long'])
    df = df[['id', 'name', 'lat', 'long']].reset_index(drop=True)
    return df


# ==========================================
# 2. Distance Calculators
# ==========================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes distance in km between two coordinates using the Haversine formula."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return float(2 * np.arcsin(np.sqrt(a)) * 6371.0)


def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes simple 2D Euclidean distance."""
    return float(np.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2))


def calculate_route_distance(route: Route, coords: Coords, metric: str = 'haversine') -> float:
    """Calculates total round-trip route distance."""
    n = len(route)
    if n <= 1:
        return 0.0
    dist_fn = haversine_distance if metric == 'haversine' else euclidean_distance
    total = 0.0
    for i in range(n):
        c1 = coords[route[i]]
        c2 = coords[route[(i + 1) % n]]
        total += dist_fn(c1[0], c1[1], c2[0], c2[1])
    return total


# ==========================================
# 3. Greedy Baseline Solver
# ==========================================

class GreedyTSPSolver:
    """Greedy (Nearest Neighbor) TSP solver."""

    def __init__(self, coords: Coords, metric: str = 'haversine') -> None:
        self.coords = coords
        self.metric = metric
        self._dist_fn = haversine_distance if metric == 'haversine' else euclidean_distance

    def solve(self, start_idx: int = 0) -> tuple[Route, float, float]:
        n = len(self.coords)
        if n == 0:
            return [], 0.0, 0.0
        unvisited = set(range(n))
        unvisited.remove(start_idx)
        route = [start_idx]
        current = start_idx
        start_time = time.time()
        while unvisited:
            cx, cy = self.coords[current]
            nearest = min(
                unvisited,
                key=lambda x: self._dist_fn(cx, cy, self.coords[x][0], self.coords[x][1])
            )
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        dist = calculate_route_distance(route, self.coords, self.metric)
        return route, dist, time.time() - start_time


# ==========================================
# 4. Discrete PSO Solver for TSP
# ==========================================

class SwapOperation:
    """A single swap of two indices in a route permutation."""

    __slots__ = ('i', 'j')

    def __init__(self, i: int, j: int) -> None:
        self.i = i
        self.j = j

    def __repr__(self) -> str:
        return f"Swap({self.i}, {self.j})"


def get_swap_sequence(route1: Route, route2: Route) -> list[SwapOperation]:
    """
    Returns the minimal swap sequence that transforms route1 into route2.
    Equivalent to (route2 - route1) in continuous PSO notation.
    """
    temp = list(route1)
    sequence: list[SwapOperation] = []
    for idx in range(len(route2)):
        if temp[idx] != route2[idx]:
            swap_idx = temp.index(route2[idx])
            sequence.append(SwapOperation(idx, swap_idx))
            temp[idx], temp[swap_idx] = temp[swap_idx], temp[idx]
    return sequence


def scale_velocity(swap_sequence: list[SwapOperation], p: float) -> list[SwapOperation]:
    """
    Stochastically retains each swap with probability min(p, 1.0).
    Clamping p to [0, 1] preserves stochasticity even when c1/c2 > 1 —
    without the clamp, p > 1 would always keep every swap, eliminating randomness.
    """
    p = min(max(p, 0.0), 1.0)
    return [s for s in swap_sequence if random.random() < p]


def apply_velocity(route: Route, swap_sequence: list[SwapOperation]) -> Route:
    """Applies a sequence of swap operations to a copy of route."""
    new_route = list(route)
    for s in swap_sequence:
        new_route[s.i], new_route[s.j] = new_route[s.j], new_route[s.i]
    return new_route


class Particle:
    """A single particle in the discrete PSO swarm."""

    def __init__(self, num_cities: int, coords: Coords, metric: str = 'haversine') -> None:
        self.coords = coords
        self.metric = metric
        self.position: Route = list(range(num_cities))
        random.shuffle(self.position)
        self.best_position: Route = list(self.position)
        self.best_distance: float = calculate_route_distance(self.position, coords, metric)
        self.distance: float = self.best_distance
        self.velocity: list[SwapOperation] = []

    def update_position(
        self,
        gbest_position: Route,
        w: float,
        c1: float,
        c2: float,
        mutation_rate: float = 0.0,
        iter_ratio: float = 0.0,
    ) -> None:
        """
        Updates particle position using the discrete PSO velocity equation.

        iter_ratio in [0, 1] drives adaptive mutation decay:
        mutation is high early (exploration) and decays to 10% by the final iteration.

        Velocity is capped at num_cities // 2 to prevent velocity bloat,
        which otherwise causes the position to behave like a random walk.
        """
        cognitive_vel = scale_velocity(
            get_swap_sequence(self.position, self.best_position), c1 * random.random()
        )
        social_vel = scale_velocity(
            get_swap_sequence(self.position, gbest_position), c2 * random.random()
        )
        inertia_vel = scale_velocity(self.velocity, w)

        new_velocity = inertia_vel + cognitive_vel + social_vel

        # Velocity length cap: prevents unbounded growth that leads to random-walk behaviour
        max_vel = max(1, len(self.position) // 2)
        if len(new_velocity) > max_vel:
            new_velocity = random.sample(new_velocity, max_vel)
        self.velocity = new_velocity

        self.position = apply_velocity(self.position, self.velocity)

        # Adaptive mutation: decays from mutation_rate → mutation_rate * 0.1
        adaptive_rate = mutation_rate * (1.0 - iter_ratio * 0.9)
        if random.random() < adaptive_rate:
            i, j = random.sample(range(len(self.position)), 2)
            self.position[i], self.position[j] = self.position[j], self.position[i]

        self.distance = calculate_route_distance(self.position, self.coords, self.metric)
        if self.distance < self.best_distance:
            self.best_position = list(self.position)
            self.best_distance = self.distance


class PSOSolver:
    """
    Discrete PSO for TSP with:
    - Hybrid Greedy + 2-opt seeding (gbest starts at greedy distance)
    - Adaptive mutation rate decay
    - Velocity length cap
    - Periodic 2-opt on top-25% particles every 5 iterations
    - Diversity-based partial restart (prevents premature convergence)
    - Early stopping
    """

    _TWO_OPT_INTERVAL         = 5     # run 2-opt on elite particles every N iterations
    _DIVERSITY_COV_THRESHOLD  = 0.01  # coefficient of variation < 1% triggers restart
    _RESTART_FRACTION         = 0.25  # fraction of worst particles to reinitialize

    def __init__(
        self,
        coords: Coords,
        metric: str = 'haversine',
        num_particles: int = 20,
        max_iter: int = 100,
        w: float = 0.7,
        c1: float = 1.5,
        c2: float = 1.5,
        mutation_rate: float = 0.05,
        seed: int | None = None,
        early_stopping_rounds: int | None = None,
        enable_periodic_two_opt: bool = True,
    ) -> None:
        self.coords = coords
        self.metric = metric
        self.num_particles = num_particles
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.mutation_rate = mutation_rate
        self.early_stopping_rounds = early_stopping_rounds
        self.enable_periodic_two_opt = enable_periodic_two_opt

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.num_cities = len(coords)
        self.particles: list[Particle] = []

        # Seed particle 0 with the Greedy route so gbest starts at greedy distance,
        # producing a clear visual step-down on the convergence chart.
        greedy_solver = GreedyTSPSolver(coords, metric)
        greedy_route, greedy_dist, _ = greedy_solver.solve()

        p0 = Particle(self.num_cities, coords, metric)
        p0.position      = list(greedy_route)
        p0.best_position = list(greedy_route)
        p0.best_distance = greedy_dist
        p0.distance      = greedy_dist
        self.particles.append(p0)

        for _ in range(1, num_particles):
            self.particles.append(Particle(self.num_cities, coords, metric))

        self.gbest_position: Route  = list(greedy_route)
        self.gbest_distance: float  = greedy_dist
        for p in self.particles:
            if p.distance < self.gbest_distance:
                self.gbest_distance = p.distance
                self.gbest_position = list(p.position)

        self.history: list[float]          = []
        self.route_history: list[Route]    = []
        self.diversity_history: list[float] = []

    def _two_opt(self, route: Route) -> tuple[Route, float]:
        """2-opt local search — iteratively reverses sub-segments to eliminate crossing edges."""
        best = list(route)
        best_dist = calculate_route_distance(best, self.coords, self.metric)
        n = len(route)
        improved = True
        while improved:
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 2, n):
                    new = best[:]
                    new[i:j] = reversed(best[i:j])
                    d = calculate_route_distance(new, self.coords, self.metric)
                    if d < best_dist - 0.01:
                        best, best_dist = new, d
                        improved = True
                        break
                if improved:
                    break
        return best, best_dist

    def _partial_restart(self) -> None:
        """
        Reinitializes the worst _RESTART_FRACTION of particles with random routes.
        Called when swarm diversity collapses to restore exploration capacity.
        """
        n_restart = max(1, int(len(self.particles) * self._RESTART_FRACTION))
        worst = sorted(self.particles, key=lambda p: p.distance, reverse=True)[:n_restart]
        for p in worst:
            p.position      = list(range(self.num_cities))
            random.shuffle(p.position)
            p.distance      = calculate_route_distance(p.position, self.coords, self.metric)
            p.best_position = list(p.position)
            p.best_distance = p.distance
            p.velocity      = []

    def solve(self, progress_callback=None) -> tuple[Route, float, float]:
        start_time = time.time()

        self.history.append(self.gbest_distance)
        self.route_history.append(list(self.gbest_position))
        self.diversity_history.append(float(np.std([p.distance for p in self.particles])))

        no_improvement_count = 0

        for iteration in range(1, self.max_iter + 1):
            prev_best  = self.gbest_distance
            iter_ratio = iteration / self.max_iter

            # Untangle Greedy route with 2-opt on the very first iteration
            if iteration == 1:
                opt_route, opt_dist = self._two_opt(self.gbest_position)
                if opt_dist < self.gbest_distance:
                    self.gbest_distance = opt_dist
                    self.gbest_position = list(opt_route)

            # Main PSO update
            for p in self.particles:
                p.update_position(
                    self.gbest_position, self.w, self.c1, self.c2,
                    self.mutation_rate, iter_ratio
                )
                if p.distance < self.gbest_distance:
                    opt_route, opt_dist = self._two_opt(p.position)
                    self.gbest_distance = opt_dist
                    self.gbest_position = list(opt_route)

            # Periodic 2-opt refinement on top-25% particles (disabled during auto-tune)
            if self.enable_periodic_two_opt and iteration % self._TWO_OPT_INTERVAL == 0:
                n_elite = max(1, len(self.particles) // 4)
                elite = sorted(self.particles, key=lambda p: p.distance)[:n_elite]
                for p in elite:
                    opt_route, opt_dist = self._two_opt(p.position)
                    p.position = opt_route
                    p.distance = opt_dist
                    if opt_dist < p.best_distance:
                        p.best_position = opt_route
                        p.best_distance = opt_dist
                    if opt_dist < self.gbest_distance:
                        self.gbest_distance = opt_dist
                        self.gbest_position = list(opt_route)

            # Diversity-based partial restart
            distances  = [p.distance for p in self.particles]
            mean_dist  = float(np.mean(distances))
            if mean_dist > 0 and float(np.std(distances)) / mean_dist < self._DIVERSITY_COV_THRESHOLD:
                self._partial_restart()

            self.history.append(self.gbest_distance)
            self.route_history.append(list(self.gbest_position))
            self.diversity_history.append(float(np.std([p.distance for p in self.particles])))

            if progress_callback:
                progress_callback(iteration, self.max_iter, self.gbest_distance)

            if self.gbest_distance < prev_best - 0.01:
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            if (
                self.early_stopping_rounds is not None
                and no_improvement_count >= self.early_stopping_rounds
            ):
                if progress_callback:
                    progress_callback(iteration, iteration, self.gbest_distance)
                break

        return self.gbest_position, self.gbest_distance, time.time() - start_time


# ==========================================
# 5. Auto-Tuning Module
# ==========================================

def evaluate_parameters(
    coords: Coords,
    metric: str,
    w: float,
    c1: float,
    c2: float,
    num_particles: int,
    trials: int = 3,
    test_iters: int = 30,
) -> float:
    """
    Evaluates a parameter set by averaging the final best distance over multiple trials.
    Lower score is better.
    """
    total = 0.0
    for _ in range(trials):
        solver = PSOSolver(
            coords=coords, metric=metric, num_particles=num_particles,
            max_iter=test_iters, w=w, c1=c1, c2=c2, mutation_rate=0.05,
            enable_periodic_two_opt=False,
        )
        solver.solve()
        total += solver.history[-1]
    return total / trials


def auto_tune_pso(coords: Coords, metric: str = 'haversine') -> tuple[dict, list[dict]]:
    """
    Grid search over 4 preset configurations. Returns (best_preset, tuning_log).

    Limitation: this is a fixed-preset grid search, not continuous hyperparameter
    optimization. Suitable for quick demo selection; use Bayesian or random search
    for rigorous tuning.
    """
    presets = [
        {
            "name": "Balanced",
            "w": 0.7, "c1": 1.5, "c2": 1.5, "num_particles": 20,
            "description": "Balances exploration and exploitation — good general-purpose choice.",
        },
        {
            "name": "Exploration-Heavy",
            "w": 0.9, "c1": 2.0, "c2": 1.0, "num_particles": 30,
            "description": "High inertia, strong personal memory. Best for avoiding local minima on larger maps.",
        },
        {
            "name": "Exploitation-Heavy",
            "w": 0.4, "c1": 1.0, "c2": 2.0, "num_particles": 15,
            "description": "Low inertia, strong social pull. Converges fast toward current global best.",
        },
        {
            "name": "Lightweight",
            "w": 0.6, "c1": 1.2, "c2": 1.2, "num_particles": 10,
            "description": "Minimal particle count for fast demo runs.",
        },
    ]

    best_preset: dict = {}
    best_score = float('inf')
    tuning_log: list[dict] = []

    for preset in presets:
        score = evaluate_parameters(
            coords=coords, metric=metric,
            w=preset["w"], c1=preset["c1"], c2=preset["c2"],
            num_particles=preset["num_particles"],
        )
        entry = {**preset, "score": score}
        tuning_log.append(entry)
        if score < best_score:
            best_score = score
            best_preset = entry

    return best_preset, tuning_log
