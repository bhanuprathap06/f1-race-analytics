# FEATURE ENGINEERING GUIDE
## Formula 1 ML Dataset System

**Version:** 1.0  
**Date:** 2026-08-10  
**Audience:** Data scientists building ML models on F1 datasets

---

## TABLE OF CONTENTS
1. Overview
2. Raw Features → Engineered Features
3. Historical Features (Pre-Race)
4. Circuit-Specific Features
5. Temporal Features
6. Normalization & Standardization
7. Interaction Features
8. Target Engineering
9. Feature Selection Recommendations

---

## 1. OVERVIEW

### Feature Engineering Philosophy

This system follows these principles:

1. **Transparent:** Every engineered feature has a clear, documented formula
2. **Interpretable:** Features should be understandable (not deep embeddings)
3. **Non-leaking:** Features only use data available before prediction time
4. **Normalized:** Comparable across different eras and circuits
5. **Temporal:** Respects time ordering (prior races only)

### Types of Features

| Type | Count | Examples |
|------|-------|----------|
| Raw (Direct from F1DB) | 40+ | position, points, lap_time, grid_position |
| Derived (Calculated once) | 15+ | career_wins, average_lap_time |
| Temporal (Time-windowed) | 20+ | previous_5_race_avg_position |
| Circuit-specific | 10+ | driver_circuit_avg_finish |
| Interaction | 5+ | (to be engineered per model) |

---

## 2. RAW FEATURES → ENGINEERED FEATURES

### Historical Driver Performance Features

#### Feature: `career_wins_before_race`
**Raw Source:** `results.csv` (position = 1)

**Calculation:**
```sql
SELECT COUNT(*)
FROM results r
JOIN races rc ON r.race_id = rc.race_id
WHERE r.driver_id = {driver_id}
  AND rc.date < {target_race_date}
  AND r.position = 1
```

**Type:** Integer (0+)  
**Interpretation:** Total wins by driver before this race  
**Example:** Driver entering Monaco 2024 with 8 career wins

**Use in Models:**
- Raw: Use directly
- Normalized (0-1): `career_wins / max_wins_any_driver` (max ≈ 103 for Hamilton)
- Binned: `1: 0-5 wins`, `2: 6-10`, `3: 11-20`, `4: 21+`

---

#### Feature: `previous_5_race_avg_position`
**Raw Source:** `results.csv` (position)

**Calculation:**
```python
def calculate_prev_5_race_avg(driver_id, race_date):
    prior_races = (
        races
        .filter(races.date < race_date)
        .sort_values('date', ascending=False)
        .head(5)
    )
    results = results_df[results_df['driver_id'] == driver_id]
    finishes = results[results['race_id'].isin(prior_races['race_id'])]['position']
    
    # Handle DNF: either exclude or count as high position
    clean_positions = [int(p) for p in finishes if isinstance(p, int)]
    
    if len(clean_positions) < 5:
        return None  # Insufficient history
    
    return mean(clean_positions)
```

**Type:** Float (1-20)  
**Interpretation:** Average finishing position in last 5 races (before this race)  
**Example:** Driver with positions [2, 5, 1, 4, 3] → average 3.0  
**Handling DNF:** 
- Option A: Exclude from calculation (only completed races)
- Option B: Count as position 20 (or higher)
- **Chosen:** Option A (only completed races), with separate DNF_rate feature

**Use in Models:**
- Raw: Use directly (lower = better)
- Inverse (higher = better): `1 / avg_position`
- Normalized: `(20 - avg_position) / 19` (0-1, higher = better)

---

#### Feature: `driver_dnf_rate_before_race`
**Raw Source:** `results.csv` (statusId)

**Calculation:**
```python
def calculate_dnf_rate(driver_id, target_date):
    career_races = results_df[results_df['driver_id'] == driver_id]
    prior_races = career_races[career_races['race_date'] < target_date]
    
    dnf_count = prior_races['statusId'].isin([3, 4, 5, 11, 12, ...]).sum()
    total_races = len(prior_races)
    
    if total_races == 0:
        return None
    
    return dnf_count / total_races
```

**Type:** Float (0.0-1.0)  
**Status Codes (DNF):** 3=Accident, 4=Engine, 5=Gearbox, etc. (see status table)  
**Example:** Driver with 5 DNF in 50 races → 0.10 (10% DNF rate)  
**Interpretation:** Reliability metric (lower = more reliable)

**Use in Models:**
- Raw: Use directly (0.0 = perfect reliability, 1.0 = every race DNF)
- Inverse: `1 - dnf_rate`
- Risk score: `dnf_rate * 10` (0-10 scale)

---

### Historical Constructor Performance Features

#### Feature: `constructor_wins_before_race`
**Raw Source:** `results.csv` (constructor_id, position = 1)

**Calculation:**
```python
def calculate_constructor_wins(constructor_id, target_date):
    races_before = races[races['date'] < target_date]['race_id']
    constructor_wins = results_df[
        (results_df['constructor_id'] == constructor_id) &
        (results_df['race_id'].isin(races_before)) &
        (results_df['position'] == 1)
    ]
    return len(constructor_wins)
```

**Type:** Integer (0+)  
**Interpretation:** Total constructor wins before this race  
**Example:** Mercedes entering 2024 season with 245 constructor wins

**Use in Models:**
- Raw: Use directly
- Normalized: Constructor_wins / max_wins
- Strength indicator

---

#### Feature: `constructor_previous_5_race_avg_position`
**Raw Source:** `results.csv` (constructor_id, position)

**Calculation:**
```python
def constructor_avg_position_5races(constructor_id, target_date):
    prior_races = races[races['date'] < target_date].sort_values('date', ascending=False).head(5)
    
    constructor_results = results_df[
        (results_df['constructor_id'] == constructor_id) &
        (results_df['race_id'].isin(prior_races['race_id']))
    ]
    
    positions = [float(p) for p in constructor_results['position'] if isinstance(p, (int, float))]
    
    if len(positions) < 10:  # Both drivers in last 5 races
        return None
    
    return mean(positions)
```

**Type:** Float  
**Note:** Constructor results include BOTH drivers; average both  
**Example:** Mercedes last 5 races: [1.5, 2.0, 1.5, 3.0, 2.0] → average 2.0

---

### Circuit-Specific Historical Features

#### Feature: `driver_circuit_avg_finish_before_race`
**Raw Source:** `results.csv` + `races.csv` (circuit_id)

**Calculation:**
```python
def driver_circuit_avg_finish(driver_id, circuit_id, target_date):
    target_circuit_races = races[
        (races['circuit_id'] == circuit_id) &
        (races['date'] < target_date)
    ]['race_id']
    
    results_at_circuit = results_df[
        (results_df['driver_id'] == driver_id) &
        (results_df['race_id'].isin(target_circuit_races))
    ]
    
    positions = [int(p) for p in results_at_circuit['position'] if isinstance(p, int)]
    
    if len(positions) == 0:
        return None  # Driver never raced at this circuit
    
    return mean(positions)
```

**Type:** Float  
**Interpretation:** Driver's average finishing position at THIS SPECIFIC CIRCUIT  
**Example:** Lewis Hamilton at Monaco:
- Races: 1997-2024 (multiple times)
- Finishes: [2, 1, 1, 2, 1, 1, DNF, 2, 1, DNF, 3, 2, 1, 1, 1, 3]
- Avg: ~1.4 (very strong at Monaco)

**Handling:**
- If driver never raced at circuit: NULL (not 0)
- If only 1 prior race at circuit: use that result (not enough for average)
- Only count completed races (exclude DNF from average)

**Use in Models:**
- Raw: Direct indicator of circuit affinity
- Normalized: `(20 - avg_position) / 19`

---

#### Feature: `driver_circuit_lap_time_ms`
**Raw Source:** `lap_times.csv` (driver_id, lap_time_ms) + `races.csv` (circuit_id)

**Calculation:**
```python
def driver_circuit_avg_lap_time(driver_id, circuit_id, target_date):
    # Only available from 1996 onward
    target_circuit_races = races[
        (races['circuit_id'] == circuit_id) &
        (races['date'] < target_date) &
        (races['date'] >= datetime(1996, 1, 1))  # Data starts 1996
    ]['race_id']
    
    lap_times = lap_times_df[
        (lap_times_df['driver_id'] == driver_id) &
        (lap_times_df['race_id'].isin(target_circuit_races))
    ]['milliseconds']
    
    if len(lap_times) < 20:  # Need reasonable sample
        return None
    
    return mean(lap_times)
```

**Type:** Integer (milliseconds)  
**Interpretation:** Average fastest lap time at this circuit (driver-specific)  
**Availability:** 1996 onwards only  
**Example:** Senna never recorded (died 1994); Schumacher Monaco avg ≈74,200ms

**Normalization (Circuit-Specific):**
```python
def normalize_lap_time(driver_lap_time_ms, circuit_id, year):
    circuit_median = (
        lap_times_df[
            (lap_times_df['race_id'].isin(races at circuit before year))
        ]['milliseconds'].median()
    )
    
    relative_time = driver_lap_time_ms / circuit_median
    # 1.0 = median pace
    # 0.95 = 5% faster than median (strong)
    # 1.05 = 5% slower than median (weak)
    
    return relative_time
```

---

### Temporal Features

#### Feature: `races_completed_before_race`
**Raw Source:** `results.csv` (driver_id)

**Calculation:**
```python
def races_completed(driver_id, target_date):
    prior_races = results_df[
        (results_df['driver_id'] == driver_id) &
        (results_df['race_date'] < target_date)
    ]
    return len(prior_races)
```

**Type:** Integer (0+)  
**Interpretation:** Career races for this driver (experience proxy)  
**Example:**
- Driver starting F1 career: 0
- Mid-career driver: 150-200
- Vettel 2024: 385+

**Use in Models:**
- Raw: Experience indicator
- Log scale: `log10(races + 1)` (diminishing returns on experience)
- Binned: `1: Rookie`, `2: 1-5 years`, `3: 5-10 years`, `4: 10+ years`

---

#### Feature: `seasons_in_f1`
**Raw Source:** `races.csv` (year) + `results.csv` (driver_id)

**Calculation:**
```python
def seasons_in_f1(driver_id, target_date):
    seasons = results_df[results_df['driver_id'] == driver_id]['year'].unique()
    return len(seasons)
```

**Type:** Integer  
**Example:** A driver who raced 2018-2020, 2022-2024 → 6 seasons

---

#### Feature: `years_since_career_start`
**Raw Source:** `drivers.csv` (dob) + `results.csv`

**Calculation:**
```python
def years_since_start(driver_id, target_race_date):
    first_race = results_df[results_df['driver_id'] == driver_id]['race_date'].min()
    years = (target_race_date - first_race).days / 365.25
    return years
```

**Type:** Float  
**Interpretation:** Years of F1 experience (continuous)  
**Example:** Hamilton started 2007 → by 2024, ~17 years

---

### Qualifying Features

#### Feature: `qualifying_gap_to_pole_ms`
**Raw Source:** `qualifying.csv`

**Calculation:**
```python
def qual_gap_to_pole(race_id):
    q_session = qualifying_df[qualifying_df['race_id'] == race_id]
    
    # Get pole position time (best Q3 time)
    pole_time = q_session['q3'].min()  # in milliseconds
    
    gaps = {}
    for idx, row in q_session.iterrows():
        driver_id = row['driver_id']
        best_time = min([t for t in [row['q1'], row['q2'], row['q3']] if t is not None])
        gap = best_time - pole_time
        gaps[driver_id] = gap
    
    return gaps
```

**Type:** Integer (milliseconds)  
**Interpretation:** How many ms off pole position (lower = better grid)  
**Example:** Driver with gap of 250ms = 0.25 seconds off pole

**Use in Models:**
- Raw: Directly indicates qualifying performance
- Normalized: `gap_to_pole / max_gap` (0-1, where 0=pole)
- Log scale: For very large gaps

---

#### Feature: `qualifying_percentile`
**Raw Source:** `qualifying.csv` (position)

**Calculation:**
```python
def qual_percentile(qualifying_position, race_id):
    grid = qualifying_df[qualifying_df['race_id'] == race_id]['position'].max()
    # Assuming grid of ~20 cars typical
    percentile = (grid - qualifying_position) / (grid - 1)
    # Pole = 1.0, last place = 0.0
    return percentile
```

**Type:** Float (0.0-1.0)  
**Interpretation:** Qualifying position as percentile (1.0=pole, 0.0=last)

---

## 3. HISTORICAL FEATURES SUMMARY TABLE

| Feature | Type | Calculation | Typical Range | Pre-Qual OK? | Missing Era |
|---------|------|-----------|---|---|---|
| career_wins | INT | COUNT(position=1) | 0-103 | ✓ | None |
| career_podiums | INT | COUNT(position≤3) | 0-182 | ✓ | None |
| career_points | FLOAT | SUM(points) | 0-4500 | ✓ | None |
| prev_5_avg_pos | FLOAT | MEAN(position) | 1-20 | ✓ | None |
| dnf_rate | FLOAT | COUNT(DNF)/total | 0.0-1.0 | ✓ | None |
| races_completed | INT | COUNT(*) | 0-400 | ✓ | None |
| circuit_avg_finish | FLOAT | MEAN(position) at circuit | 1-20 | ✓ | None |
| circuit_avg_laptime | INT | MEAN(laptime_ms) at circuit | 70000+ | ✗ | <1996 |
| driver_circuit_wins | INT | COUNT(pos=1) at circuit | 0-10 | ✓ | None |
| qualifying_gap_ms | INT | Best qual time - pole | 0-2000 | ✗ | Post-qual only |

---

## 4. NORMALIZATION & STANDARDIZATION

### Lap Time Normalization (Circuit-Specific)

**Problem:** Raw lap times not comparable across circuits (Monza ≈ 70,000ms, Monaco ≈ 75,000ms)

**Solution 1: Z-score within Circuit**
```python
def normalize_laptime_zscore(lap_time_ms, circuit_id, year):
    circuit_laps = lap_times_df[
        lap_times_df['circuit_id'] == circuit_id &
        lap_times_df['year'] == year
    ]['milliseconds']
    
    mean = circuit_laps.mean()
    std = circuit_laps.std()
    
    zscore = (lap_time_ms - mean) / std
    return zscore
    # Typical range: -3.0 to +3.0
    # 0 = circuit median
    # -1.0 = one std dev faster than median
```

**Solution 2: Relative to Circuit Median**
```python
def normalize_laptime_relative(lap_time_ms, circuit_id, year):
    circuit_median = lap_times_df[
        lap_times_df['circuit_id'] == circuit_id &
        lap_times_df['year'] == year
    ]['milliseconds'].median()
    
    relative = lap_time_ms / circuit_median
    return relative
    # Typical range: 0.95 to 1.10
    # 1.0 = circuit median pace
    # 0.97 = 3% faster than median
```

**Recommendation:** Use Solution 2 (relative) for interpretability

---

### Championship Points Normalization

**Problem:** Points systems changed over time (8-6-4-3-2-1 → 10-8-6 → current)

**Solution:** Create era-aware normalization
```python
def normalize_points_to_current(points, scoring_era):
    # Era-specific max points per race:
    max_points_by_era = {
        'pre_1991': 6,      # 8-6-4-3-2-1
        '1991_2002': 10,    # 10-8-6-4-2-1
        '2003_2009': 10,    # 10-8-6-5-4-3-2-1
        '2010_present': 25  # 25-18-15-12-10-8-6-4-2-1
    }
    
    max_points = max_points_by_era[scoring_era]
    normalized = points / max_points * 25  # Scale to 25
    return normalized
```

**Alternative:** Keep historical points raw, don't normalize across eras

---

### Grid Position Normalization

**Problem:** Grid size increased over time (8 cars in 1950 → 20 cars today)

**Solution:** Position percentile
```python
def grid_position_percentile(grid_position, year):
    # Typical grid sizes by era:
    grid_size_by_era = {
        1950: 8,
        1960: 14,
        1990: 18,
        2010: 20,
        2024: 20
    }
    
    grid_size = grid_size_by_era.get(year, 20)
    percentile = (grid_size - grid_position) / (grid_size - 1)
    # 1.0 = pole position
    # 0.0 = last position on grid
    
    return percentile
```

---

## 5. INTERACTION FEATURES

### Features to Engineer (Model-Specific)

These are NOT pre-computed; engineer during model training per your specific needs:

#### Interaction: Driver × Circuit Affinity
```python
# Does this driver historically perform well at this circuit?
driver_circuit_affinity = driver_circuit_avg_finish / circuit_avg_finish_all_drivers

# Example: Hamilton at Silverstone (avg 2.1) vs circuit average (5.0)
# affinity = 2.1 / 5.0 = 0.42 (strong affinity, performs better than average)
```

#### Interaction: Constructor Power × Driver Skill
```python
# Does driver's recent performance match constructor performance?
performance_alignment = abs(driver_5race_avg - constructor_5race_avg)

# Low value = driver and constructor in sync
# High value = misalignment (interesting edge case)
```

#### Interaction: Grid Position × Constructor Pace
```python
# Can constructor overcome a poor grid position?
pace_advantage = (constructor_avg_speed - circuit_avg_speed) / 1000

# Multiply by grid deficit to estimate catch-up potential
expected_position_gain = pace_advantage * grid_deficit_positions
```

---

## 6. TARGET ENGINEERING

### Binary Classification: Podium (0/1)

**Simple Definition:**
```python
target_podium = 1 if final_position <= 3 else 0
```

**Class Imbalance:** ~20% podium in dataset (class imbalance)  
**Handling:** Use stratified split, class weights, or SMOTE during training

---

### Multi-Class: Final Position Prediction

**Regression (continuous position):**
```python
# Predict as continuous, round to integer
target_position = final_position  # 1.0, 2.0, 3.0, etc.
```

**Classification (position bins):**
```python
# Bin positions into categories:
if final_position <= 3:
    position_class = 'PODIUM'
elif final_position <= 10:
    position_class = 'POINTS'
elif final_position <= 20:
    position_class = 'MIDFIELD'
else:
    position_class = 'BACKMARKER'
```

---

### Ranking Problem (Not Standard Regression)

**Consider:** Final position is ordinal, not interval

```python
# Ranking loss (better than MSE for position prediction)
# Learning-to-rank approaches may be better than standard regression
```

---

## 7. FEATURE SELECTION RECOMMENDATIONS

### Top 20 Features for Winner Prediction

**Ranked by expected importance:**

1. `qualifying_position` (grid position = very strong predictor)
2. `previous_5_race_avg_position` (recent form)
3. `constructor_wins_before_race` (team strength)
4. `driver_circuit_avg_finish_before_race` (circuit affinity)
5. `career_wins_before_race` (experience/skill)
6. `previous_5_race_avg_points` (recent points)
7. `constructor_points_before_race` (team championship standing)
8. `driver_circuit_wins_before_race` (circuit expertise)
9. `previous_race_position` (momentum)
10. `driver_dnf_rate_before_race` (reliability)
11. `career_podiums_before_race` (career consistency)
12. `previous_race_points` (last race points)
13. `qualifying_gap_to_pole_ms` (qualifying gap)
14. `constructor_dnf_rate_before_race` (team reliability)
15. `driver_circuit_podiums_before_race` (circuit success rate)
16. `previous_3_race_avg_position` (recent 3-race trend)
17. `races_completed_before_race` (experience)
18. `constructor_previous_5_race_avg_position` (team form)
19. `driver_circuit_races_before_race` (circuit experience count)
20. `career_points_before_race` (career points total)

---

## 8. MODEL RECOMMENDATIONS

### For Winner/Podium Prediction
- **Algorithm:** XGBoost, LightGBM (handle non-linearity)
- **Key Features:** Grid position, qualifying gap, recent form
- **Class Imbalance:** Use sample_weight or scale_pos_weight

### For Final Position Prediction (Regression)
- **Algorithm:** Gradient Boosting, Neural Networks
- **Consider:** Ranking loss instead of MSE
- **Output:** Continuous prediction, then rank

### For Lap Time Prediction
- **Algorithm:** Linear Regression (surprisingly effective), RegressionTrees
- **Normalization:** Use circuit-specific z-scores
- **Data:** Only 1996+ available

---

## 9. FEATURE VALIDATION CHECKLIST

Before using engineered features:

- [ ] Feature calculation formula documented
- [ ] Examples calculated by hand and verified
- [ ] No data leakage (calculated from pre-race data only)
- [ ] Temporal ordering correct (no future races used)
- [ ] Missing data handled consistently (NULL vs 0)
- [ ] Normalization (if applied) documented
- [ ] Feature range verified (no impossible values)
- [ ] Nulls counted and reason documented
- [ ] Feature correlated with target (spot check)
- [ ] Ready for model training

---

**End of Feature Engineering Guide**

Questions about specific features? Check DATA_DICTIONARY.md and DATA_PROVENANCE.md.
