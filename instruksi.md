# AGENTS.md — PSO TSP Visualization (Jawa Barat)

## 🎯 Project Overview

This project implements a **Particle Swarm Optimization (PSO)** approach to solve the **Traveling Salesman Problem (TSP)** using real-world geographic data (cities in West Java).

The system is designed as an **agentic pipeline** that:

* Loads dataset from CSV
* Processes and filters location data
* Solves TSP using PSO (discrete permutation-based)
* Visualizes results interactively using Streamlit

Target: **Academic demo (lecturer presentation)**

---

## 📂 Dataset Specification

### Source

* External CSV file (user-provided)

### Format

```
id | foreign | name | lat | long
```

### Notes

* `foreign` column is ignored
* Only use:

  * `name`
  * `lat`
  * `long`

### Scope

* Region: **West Java**
* Number of cities: **27**

### Agent Responsibility

* Validate CSV structure
* Drop unused columns
* Ensure no missing lat/long
* Normalize coordinates if needed

---

## ⚙️ Problem Definition

* Objective: Minimize total travel distance
* Input: List of cities (lat, long)
* Output: Optimal visiting order (route)

Distance metric:

* Euclidean distance (or Haversine if implemented)

---

## 🧠 PSO Design (Discrete)

### Representation

* Particle = permutation of city indices

Example:

```
[0, 3, 1, 2, ...]
```

---

### Velocity (Discrete Adaptation)

* Represented as sequence of **swap operations**

---

### Operators (RECOMMENDED SET)

* Swap operator (primary)
* Optional: small mutation for exploration

---

### Update Rules

Adaptation of:

```
v = w*v + c1*(pbest - x) + c2*(gbest - x)
```

Implemented as:

* Generate swap sequences toward:

  * personal best
  * global best

---

### Parameters (Auto-Tuned by Agent)

Agent should dynamically choose:

* number of particles: 10–30
* iterations: 50–150
* inertia (w): 0.4 – 0.9
* c1, c2: 1.0 – 2.0

### Auto-Tuning Strategy

Agent must:

1. Try multiple parameter combinations
2. Compare convergence speed
3. Select best-performing configuration

### Output Explanation

Agent must explain:

* why parameters were chosen
* trade-off (exploration vs exploitation)

---

## 📊 Visualization Requirements

### 1. Route Visualization (MANDATORY)

* Plot cities on 2D map
* Draw path connections
* Highlight start/end

---

### 2. Convergence Graph (MANDATORY)

* X-axis: iteration
* Y-axis: best distance
* Show improvement trend

---

### 3. Iteration Playback (IMPORTANT)

* Slider or Next button
* Show:

  * current iteration route
  * gradual improvement

---

### 4. Optional Enhancements

* Compare initial vs final route
* Show particle diversity

---

## 🖥️ Deployment (Streamlit)

### Required Features

* Upload CSV
* Select number of cities (optional filter)
* Run PSO button
* Interactive visualizations

---

### UI Components

* Sidebar:

  * dataset upload
  * parameter mode (auto/manual)
* Main panel:

  * map visualization
  * convergence chart
  * iteration slider

---

## 🤖 Agent Roles (Multi-Agent Behavior)

### 1. Data Agent

* Load and clean dataset
* Validate structure
* Filter region

---

### 2. Optimization Agent

* Run PSO algorithm
* Handle permutation encoding
* Perform auto-tuning

---

### 3. Visualization Agent

* Generate plots
* Handle animation/slider
* Ensure clarity for demo

---

### 4. Explanation Agent

* Provide reasoning:

  * parameter choices
  * convergence behavior
  * final result quality

---

## 🔄 Pipeline Flow

```
CSV Input
   ↓
Data Cleaning
   ↓
City Selection (27)
   ↓
PSO Initialization
   ↓
Optimization Loop
   ↓
Best Route Found
   ↓
Visualization + Explanation
```

---

## 📦 Expected Outputs

### Primary Outputs

* Best route (ordered list of cities)
* Total distance

### Visual Outputs

* Route map
* Convergence graph
* Iteration playback

### Text Outputs

* Parameter explanation
* Optimization summary

---

## 🚧 Constraints

* Must remain lightweight (demo-ready)
* Must prioritize clarity over complexity
* Avoid over-engineering (no heavy frameworks)

---

## 💡 Notes for Agent

* Prefer simplicity in operators (swap > complex heuristics)
* Visualization clarity > algorithm sophistication
* Ensure deterministic behavior when needed (seed control)
* Always provide explanation for decisions

---

## ✅ Success Criteria

* Runs smoothly in Streamlit
* Produces visually clear route
* Shows convergence behavior
* Provides understandable explanation
* Suitable for academic demo

---
