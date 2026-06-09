import pandas as pd
import numpy as np
import random
import time

# ==========================================
# 1. Data Cleaning & Region Filtering
# ==========================================

def load_and_filter_data(csv_path="kabupaten_kota_jawa_barat.csv", region_type="jabar"):
    """
    Loads, cleans, and standardizes the West Java kabupaten/kota dataset.
    """
    df = pd.read_csv(csv_path)
    
    # Map and convert column names from 'Kabupaten_Kota', 'Latitude', 'Longitude'
    df['lat'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['long'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df['name'] = df['Kabupaten_Kota'].str.strip()
    df['id'] = df.index
    
    # Drop rows with missing crucial data
    df = df.dropna(subset=['name', 'lat', 'long'])
    
    # Drop unused columns and reset index
    df = df[['id', 'name', 'lat', 'long']].reset_index(drop=True)
    return df


# ==========================================
# 2. Distance Calculators
# ==========================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Computes distance between two coordinates in kilometers using Haversine formula.
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371.0  # Earth's radius in km
    return c * r

def euclidean_distance(lat1, lon1, lat2, lon2):
    """
    Computes simple 2D Euclidean distance.
    """
    return np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def calculate_route_distance(route, coords, metric='haversine'):
    """
    Calculates total route distance (returning to starting city).
    """
    total = 0.0
    n = len(route)
    if n <= 1:
        return 0.0
    for i in range(n):
        idx1 = route[i]
        idx2 = route[(i + 1) % n]  # Loop back to start
        c1 = coords[idx1]
        c2 = coords[idx2]
        if metric == 'haversine':
            total += haversine_distance(c1[0], c1[1], c2[0], c2[1])
        else:
            total += euclidean_distance(c1[0], c1[1], c2[0], c2[1])
    return total


# ==========================================
# 3. Greedy Baseline Solver
# ==========================================

class GreedyTSPSolver:
    """
    Greedy (Nearest Neighbor) TSP solver.
    """
    def __init__(self, coords, metric='haversine'):
        self.coords = coords  # List of (lat, long)
        self.metric = metric
        
    def solve(self, start_idx=0):
        n = len(self.coords)
        if n == 0:
            return [], 0.0
            
        unvisited = set(range(n))
        unvisited.remove(start_idx)
        route = [start_idx]
        current = start_idx
        
        start_time = time.time()
        while unvisited:
            # Find nearest city
            nearest = min(
                unvisited,
                key=lambda x: haversine_distance(self.coords[current][0], self.coords[current][1], self.coords[x][0], self.coords[x][1])
                if self.metric == 'haversine'
                else euclidean_distance(self.coords[current][0], self.coords[current][1], self.coords[x][0], self.coords[x][1])
            )
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
            
        execution_time = time.time() - start_time
        dist = calculate_route_distance(route, self.coords, self.metric)
        return route, dist, execution_time


# ==========================================
# 4. Discrete PSO Solver for TSP
# ==========================================

class SwapOperation:
    """
    Represents a single swap operation at indices i and j.
    """
    def __init__(self, i, j):
        self.i = i
        self.j = j
        
    def __repr__(self):
        return f"Swap({self.i}, {self.j})"


def get_swap_sequence(route1, route2):
    """
    Generates a list of SwapOperations that transforms route1 into route2.
    Equivalent to (route2 - route1)
    """
    temp_r = list(route1)
    sequence = []
    for idx in range(len(route2)):
        if temp_r[idx] != route2[idx]:
            val_needed = route2[idx]
            swap_idx = temp_r.index(val_needed)
            
            swap = SwapOperation(idx, swap_idx)
            sequence.append(swap)
            
            # Apply swap internally to keep searching
            temp_r[idx], temp_r[swap_idx] = temp_r[swap_idx], temp_r[idx]
    return sequence


def scale_velocity(swap_sequence, p):
    """
    Keeps each swap operation in the sequence with probability p.
    Equivalent to (p * velocity)
    """
    return [swap for swap in swap_sequence if random.random() < p]


def apply_velocity(route, swap_sequence):
    """
    Applies a sequence of swaps to a route.
    Equivalent to (route + velocity)
    """
    new_route = list(route)
    for swap in swap_sequence:
        new_route[swap.i], new_route[swap.j] = new_route[swap.j], new_route[swap.i]
    return new_route


class Particle:
    """
    Represents a particle in the discrete PSO swarm.
    """
    def __init__(self, num_cities, coords, metric='haversine'):
        self.coords = coords
        self.metric = metric
        
        # Position = permutation of city indices
        self.position = list(range(num_cities))
        random.shuffle(self.position)
        
        # Personal best
        self.best_position = list(self.position)
        self.best_distance = calculate_route_distance(self.position, self.coords, self.metric)
        self.distance = self.best_distance
        
        # Velocity = sequence of swap operations
        self.velocity = []
        
    def update_position(self, gbest_position, w, c1, c2, mutation_rate=0.0):
        # Cognitive velocity (c1 * r1 * (pbest - x))
        cognitive_seq = get_swap_sequence(self.position, self.best_position)
        cognitive_vel = scale_velocity(cognitive_seq, c1 * random.random())
        
        # Social velocity (c2 * r2 * (gbest - x))
        social_seq = get_swap_sequence(self.position, gbest_position)
        social_vel = scale_velocity(social_seq, c2 * random.random())
        
        # Inertia velocity (w * v)
        inertia_vel = scale_velocity(self.velocity, w)
        
        # Combined velocity
        self.velocity = inertia_vel + cognitive_vel + social_vel
        
        # Apply swaps
        self.position = apply_velocity(self.position, self.velocity)
        
        # Optional: Mutation for exploration
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(self.position)), 2)
            self.position[i], self.position[j] = self.position[j], self.position[i]
            
        # Re-evaluate
        self.distance = calculate_route_distance(self.position, self.coords, self.metric)
        
        # Update personal best
        if self.distance < self.best_distance:
            self.best_position = list(self.position)
            self.best_distance = self.distance


class PSOSolver:
    """
    PSO TSP Optimization loop with Hybrid (Greedy + 2-opt) Seeding,
    Memetic Local Search, and Early Stopping.
    """
    def __init__(self, coords, metric='haversine', num_particles=20, max_iter=100,
                 w=0.7, c1=1.5, c2=1.5, mutation_rate=0.05, seed=None,
                 early_stopping_rounds=None):
        self.coords = coords
        self.metric = metric
        self.num_particles = num_particles
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.mutation_rate = mutation_rate
        self.early_stopping_rounds = early_stopping_rounds
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.num_cities = len(coords)
        
        # 1. Initialize empty particle list
        self.particles = []
        
        # 2. Get Greedy Baseline Route
        greedy_solver = GreedyTSPSolver(self.coords, self.metric)
        greedy_route, greedy_dist, _ = greedy_solver.solve()
        
        # 3. Seed Particle 0: Exact Greedy Route
        p0 = Particle(self.num_cities, self.coords, self.metric)
        p0.position = list(greedy_route)
        p0.best_position = list(greedy_route)
        p0.best_distance = greedy_dist
        p0.distance = greedy_dist
        self.particles.append(p0)
        
        # 4. Initialize remaining particles with random routes
        # (This ensures that at iteration 0, the global best starts EXACTLY at Greedy,
        # showing a clear visual improvement when 2-opt/PSO starts optimizing).
        for _ in range(1, self.num_particles):
            self.particles.append(Particle(self.num_cities, self.coords, self.metric))
            
        # Global best starts exactly at Greedy
        self.gbest_position = list(greedy_route)
        self.gbest_distance = greedy_dist
        
        # Double check if any random particle is somehow better
        for p in self.particles:
            if p.distance < self.gbest_distance:
                self.gbest_distance = p.distance
                self.gbest_position = list(p.position)
                
        # To track optimization history
        self.history = []  # List of best distances
        self.route_history = []  # List of best routes at each iteration
        self.diversity_history = []  # List of standard deviation of particle fitness values
        
    def _two_opt(self, route):
        """
        2-opt local search to eliminate crossing lines and refine a route.
        """
        best_route = list(route)
        best_dist = calculate_route_distance(best_route, self.coords, self.metric)
        improved = True
        n = len(route)
        while improved:
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    if j - i == 1:
                        continue
                    new_route = best_route[:]
                    new_route[i:j] = reversed(best_route[i:j])
                    new_dist = calculate_route_distance(new_route, self.coords, self.metric)
                    if new_dist < best_dist - 0.01:
                        best_route = new_route
                        best_dist = new_dist
                        improved = True
                        break # Restart search
                if improved:
                    break
        return best_route, best_dist

    def solve(self, progress_callback=None):
        start_time = time.time()
        
        # Save iteration 0 state
        self.history.append(self.gbest_distance)
        self.route_history.append(list(self.gbest_position))
        self.diversity_history.append(float(np.std([p.distance for p in self.particles])))
        
        no_improvement_count = 0
        
        for iteration in range(1, self.max_iter + 1):
            prev_best = self.gbest_distance
            
            # In iteration 1, we apply 2-opt to the global best (which is the Greedy route)
            # to untangle it. This shows the step-down convergence on the plot.
            if iteration == 1:
                opt_route, opt_dist = self._two_opt(self.gbest_position)
                if opt_dist < self.gbest_distance:
                    self.gbest_distance = opt_dist
                    self.gbest_position = list(opt_route)
                    
            for p in self.particles:
                p.update_position(self.gbest_position, self.w, self.c1, self.c2, self.mutation_rate)
                
                # Update global best
                if p.distance < self.gbest_distance:
                    opt_route, opt_dist = self._two_opt(p.position)
                    self.gbest_distance = opt_dist
                    self.gbest_position = list(opt_route)
                    
            self.history.append(self.gbest_distance)
            self.route_history.append(list(self.gbest_position))
            self.diversity_history.append(float(np.std([p.distance for p in self.particles])))
            
            if progress_callback:
                progress_callback(iteration, self.max_iter, self.gbest_distance)
                
            # Early stopping check
            if self.gbest_distance < prev_best - 0.01:
                no_improvement_count = 0
            else:
                no_improvement_count += 1
                
            if self.early_stopping_rounds is not None and no_improvement_count >= self.early_stopping_rounds:
                # Signal end to progress callback with final values
                if progress_callback:
                    progress_callback(iteration, iteration, self.gbest_distance)
                break
                
        execution_time = time.time() - start_time
        return self.gbest_position, self.gbest_distance, execution_time


# ==========================================
# 5. Auto-Tuning Module
# ==========================================

def evaluate_parameters(coords, metric, w, c1, c2, num_particles, trials=3, test_iters=30):
    """
    Evaluates a set of parameters by running short PSO sessions.
    Score = Average final best distance found across trials.
    (Lower score is better; ranks configurations based solely on final shortest path)
    """
    total_score = 0.0
    for _ in range(trials):
        solver = PSOSolver(
            coords=coords,
            metric=metric,
            num_particles=num_particles,
            max_iter=test_iters,
            w=w,
            c1=c1,
            c2=c2,
            mutation_rate=0.05
        )
        solver.solve()
        
        # Only use final best distance
        final_dist = solver.history[-1]
        total_score += final_dist
        
    return total_score / trials


def auto_tune_pso(coords, metric='haversine'):
    """
    Runs grid search over 4 key preset parameter configurations:
    1. Balanced (Medium inertia, medium coefficients)
    2. Exploration-Heavy (High inertia, high cognitive)
    3. Exploitation-Heavy (Low inertia, high social)
    4. Lightweight (Low particle count, fast execution)
    """
    presets = [
        {
            "name": "Balanced",
            "w": 0.7, "c1": 1.5, "c2": 1.5, "num_particles": 20,
            "description": "Balances exploration (swap random/pbest) and exploitation (gbest swaps)."
        },
        {
            "name": "Exploration-Heavy",
            "w": 0.9, "c1": 2.0, "c2": 1.0, "num_particles": 30,
            "description": "High inertia weight and personal confidence. Good for large maps to avoid local minima."
        },
        {
            "name": "Exploitation-Heavy",
            "w": 0.4, "c1": 1.0, "c2": 2.0, "num_particles": 15,
            "description": "Low inertia weight, high global attraction. Quickly converges towards global best route."
        },
        {
            "name": "Lightweight",
            "w": 0.6, "c1": 1.2, "c2": 1.2, "num_particles": 10,
            "description": "Few particles, faster iterations. Suitable for quick demonstrations."
        }
    ]
    
    best_preset = None
    best_score = float('inf')
    
    tuning_log = []
    
    for preset in presets:
        score = evaluate_parameters(
            coords=coords,
            metric=metric,
            w=preset["w"],
            c1=preset["c1"],
            c2=preset["c2"],
            num_particles=preset["num_particles"]
        )
        preset_info = preset.copy()
        preset_info["score"] = score
        tuning_log.append(preset_info)
        
        if score < best_score:
            best_score = score
            best_preset = preset_info
            
    return best_preset, tuning_log
