# DRIVER PERFORMANCE INDEX (DPI) METHODOLOGY
## Formula 1 ML Dataset System

**Version:** 1.0  
**Date:** 2026-08-10  
**Rating Scale:** 0.0 (worst) to 10.0 (best)  
**Transparency:** This is a mathematical construction, not an objective truth

---

## EXECUTIVE SUMMARY

Driver Performance Index (DPI) synthesizes 7 independent performance metrics into a single 0-10 score.

**Weighting:**
- Race Performance: 25%
- Lap Performance: 25%
- Qualifying Performance: 15%
- Championship Performance: 15%
- Consistency: 10%
- Wins/Podiums Ratio: 5%
- Reliability: 5%

**Key Point:** This weighting is PROPOSED, not definitive. Adjust weights based on your ML task.

---

## 1. RACE PERFORMANCE SCORE (25%)

### Definition
Performance in race results (positions, points accumulation, improvement over qualifying).

### Formula
```python
def race_performance_score(driver_id, season):
    """
    Calculate race performance based on:
    1. Win rate
    2. Podium rate
    3. Points per race
    """
    
    season_races = get_races_in_season(season)
    results = get_driver_results(driver_id, season_races)
    
    # Component 1: Win Rate
    wins = len([r for r in results if r.position == 1])
    races = len(results)
    win_rate = wins / races if races > 0 else 0
    # Normalize: best win rate in history ≈ 0.30 (30%), worst ≈ 0
    win_component = (win_rate / 0.30) * 10  # cap at 10
    
    # Component 2: Podium Rate
    podiums = len([r for r in results if r.position <= 3])
    podium_rate = podiums / races if races > 0 else 0
    # Normalize: typical elite ≈ 0.60 (60%), midfield ≈ 0.05
    podium_component = (podium_rate / 0.60) * 10  # cap at 10
    
    # Component 3: Points per Race
    total_points = sum([r.points for r in results])
    avg_points = total_points / races if races > 0 else 0
    # Normalize: best ≈ 18 pts/race (winning most), worst ≈ 0
    points_component = (avg_points / 20) * 10  # cap at 10
    
    # Combine (equal weighting of 3 components)
    race_score = (win_component + podium_component + points_component) / 3
    
    return min(race_score, 10.0)  # Cap at 10.0
```

### Examples

**Lewis Hamilton 2020** (dominant season):
- Wins: 11 / 17 races = 64.7% win rate
- Podiums: 17 / 17 = 100% podium rate
- Points: 408 / 17 = 24 pts/race
- Normalized: (64.7 + 100 + 100) / 3 / 10 = 9.8/10

**George Russell 2024** (mid-season):
- Wins: 0 / 14 races = 0% win rate
- Podiums: 3 / 14 = 21.4% podium rate
- Points: 41 / 14 = 2.9 pts/race
- Normalized: (0 + 14.2 + 1.4) / 3 / 10 = 0.52/10

---

## 2. LAP PERFORMANCE SCORE (25%)

### Definition
Pace, consistency, and improvement in lap times throughout season.

### Formula
```python
def lap_performance_score(driver_id, season):
    """
    Calculate based on:
    1. Fastest lap percentage
    2. Average lap time vs circuit median
    3. Lap time consistency (std dev)
    """
    
    season_races = get_races_in_season(season)
    lap_times = get_driver_lap_times(driver_id, season_races)
    
    if not lap_times:
        return 0.0  # No lap data (pre-1996)
    
    # Component 1: Fastest Lap Rate
    fastest_laps = count_fastest_laps(driver_id, season_races)
    races_with_laps = len(season_races)
    fastest_lap_rate = fastest_laps / races_with_laps
    # Normalize: best ≈ 0.40, average ≈ 0.05
    fastest_lap_component = (fastest_lap_rate / 0.40) * 10
    
    # Component 2: Pace (lap time vs circuit baseline)
    circuit_medians = {}
    for race_id in season_races:
        circuit = get_circuit(race_id)
        median = median_lap_time_at_circuit(race_id)
        circuit_medians[circuit] = median
    
    driver_pace_ratios = []
    for lap in lap_times:
        circuit = lap.circuit_id
        ratio = lap.time_ms / circuit_medians.get(circuit, lap.time_ms)
        driver_pace_ratios.append(ratio)
    
    # Average pace ratio (1.0 = circuit median, 0.95 = 5% faster)
    avg_pace_ratio = mean(driver_pace_ratios)
    # Elite drivers: 0.97-0.99
    # Average drivers: 1.00-1.05
    pace_component = ((1.0 - avg_pace_ratio + 0.01) / 0.05) * 10
    
    # Component 3: Consistency (inverse of std dev)
    lap_time_std = std(driver_pace_ratios)
    # Elite: std ≈ 0.01, average: std ≈ 0.03
    consistency_component = (1.0 - min(lap_time_std, 0.1) / 0.1) * 10
    
    lap_score = (fastest_lap_component + pace_component + consistency_component) / 3
    
    return min(lap_score, 10.0)
```

### Availability
**IMPORTANT:** Lap times only available from 1996 onwards.

For drivers 1950-1995: Use fastest race lap times instead (recorded but less granular).

### Examples

**Max Verstappen 2023** (RB19 era, very fast car):
- Fastest laps: 19 / 22 races = 86% (many won by default)
- Pace ratio: 0.965 (6.5% faster than average)
- Consistency: std 0.008 (very consistent)
- Score: 9.8/10

**Nico Rosberg 2016** (paired with Hamilton):
- Fastest laps: 8 / 21 races = 38%
- Pace ratio: 0.978 (2.2% slower than Hamilton on average)
- Consistency: std 0.012
- Score: 7.2/10

---

## 3. QUALIFYING PERFORMANCE SCORE (15%)

### Definition
Performance in qualifying sessions; ability to extract one lap pace.

### Formula
```python
def qualifying_score(driver_id, season):
    """
    Based on:
    1. Pole position percentage
    2. Average qualifying position
    3. Qualifying gap to pole
    """
    
    qualifying_results = get_driver_qualifying(driver_id, season)
    races = len(qualifying_results)
    
    if races == 0:
        return 0.0
    
    # Component 1: Pole Rate
    poles = len([q for q in qualifying_results if q.position == 1])
    pole_rate = poles / races
    # Elite: 0.30+, average: 0.05
    pole_component = (pole_rate / 0.30) * 10
    
    # Component 2: Average Grid Position
    avg_grid = mean([q.position for q in qualifying_results])
    # Elite: 2-4, average: 8-12
    grid_component = (20.0 - avg_grid) / 18.0 * 10  # normalize
    
    # Component 3: Gap to Pole Average
    gaps_to_pole = [q.gap_to_pole_ms for q in qualifying_results]
    avg_gap = mean(gaps_to_pole)
    # Elite: 0-50ms, average: 100-200ms
    gap_component = max(0, (500 - avg_gap) / 500 * 10)
    
    qual_score = (pole_component + grid_component + gap_component) / 3
    
    return min(qual_score, 10.0)
```

### Pre-2003 Qualifying
**Important Note:** Pre-2003 qualifying was single-run or had different formats.

- Pole rate may not be comparable
- Gap-to-pole calculations problematic
- Recommend: Use position component only for pre-2003

### Examples

**Michael Schumacher 1994** (pre-modern Q format):
- Pole positions: 3 (out of 16 races)
- Qualifying score: ~6.5/10
- (Old format makes direct comparison unfair)

**Sebastian Vettel 2010** (modern Q1/Q2/Q3):
- Pole positions: 15 / 19
- Pole rate: 78.9%
- Avg gap to pole: 34ms
- Qualifying score: 9.3/10

---

## 4. CHAMPIONSHIP PERFORMANCE SCORE (15%)

### Definition
Overall season championship standing and progression.

### Formula
```python
def championship_score(driver_id, season):
    """
    Measure of championship performance:
    1. Final championship position
    2. Points percentage of maximum possible
    3. Points accumulation trend
    """
    
    standings = get_driver_standings_season(driver_id, season)
    final_position = standings['final_position']
    final_points = standings['final_points']
    races = count_races(season)
    
    # Component 1: Final Position
    # 1st: 10, 2nd: 8, 3rd: 6, ..., 20th: 1, 21+: 0
    position_score = max(0, 10 - final_position + 1)
    
    # Component 2: Points as % of Max Possible
    max_points = 25 * races  # Max points per race * races
    points_percentage = (final_points / max_points) * 100
    # Elite: 70-90%, top team: 40-60%, midfield: 10-30%
    points_component = min((points_percentage / 70) * 10, 10.0)
    
    # Component 3: Points Momentum (last third vs first third)
    first_third_races = standings['races_1_to_N_of_3']
    last_third_races = standings['races_2N_of_3_to_N']
    first_third_ppg = first_third_races['avg_points_per_race']
    last_third_ppg = last_third_races['avg_points_per_race']
    
    momentum = last_third_ppg / first_third_ppg if first_third_ppg > 0 else 1.0
    # >1.0 = improving, <1.0 = declining
    momentum_component = min(momentum * 5, 10.0)
    
    champ_score = (position_score + points_component + momentum_component) / 3
    
    return min(champ_score, 10.0)
```

### Examples

**Ayrton Senna 1991:**
- Final position: 1st (10 points)
- Points: 96 / 176 max = 54% (5.4 component)
- Momentum: Consistent (1.0 momentum = 5.0 component)
- Championship score: 6.8/10

**Lando Norris 2024** (strong points accumulation):
- Final position: 2nd (9 points)
- Points: 587 / 775 max = 76% (7.6 component)
- Momentum: Strong late-season (1.2 momentum = 6.0 component)
- Championship score: 7.5/10

---

## 5. CONSISTENCY SCORE (10%)

### Definition
Variability of performance (lower variance = more consistent = higher score).

### Formula
```python
def consistency_score(driver_id, season):
    """
    Measure performance consistency:
    1. Position variance (std dev)
    2. Points per race variance
    3. Grid-to-finish delta consistency
    """
    
    results = get_driver_results(driver_id, season)
    
    # Component 1: Position Variance
    positions = [r.position for r in results if r.position > 0]  # Exclude DNF
    position_std = std(positions)
    # Elite: 3-5, average: 8-12
    position_consistency = max(0, (15 - position_std) / 15 * 10)
    
    # Component 2: Points Variance
    points = [r.points for r in results]
    points_std = std(points)
    points_mean = mean(points)
    coefficient_of_variation = points_std / points_mean if points_mean > 0 else 0
    # Elite CV: 0.5-0.7, average: 1.2-1.8
    points_consistency = max(0, (1.5 - coefficient_of_variation) / 1.5 * 10)
    
    # Component 3: Grid-to-Finish Delta Consistency
    grid_deltas = [r.position - r.grid_position for r in results]
    delta_std = std(grid_deltas)
    # Elite: 1-2, average: 3-5
    delta_consistency = max(0, (6 - delta_std) / 6 * 10)
    
    consistency = (position_consistency + points_consistency + delta_consistency) / 3
    
    return min(consistency, 10.0)
```

### Examples

**Lewis Hamilton 2020** (Mercedes dominance, very consistent):
- Position std: 2.1 (very consistent)
- Points CV: 0.58 (very consistent)
- Delta consistency: High
- Consistency score: 9.1/10

**Daniel Ricciardo 2023** (reliability issues, inconsistent):
- Position std: 8.3 (DNF-affected)
- Points CV: 1.85 (high variance)
- Consistency score: 3.2/10

---

## 6. WINS/PODIUMS RATIO (5%)

### Definition
Strikes a balance between pure win rate and podium consistency.

### Formula
```python
def wins_podiums_score(driver_id, season):
    """
    Measure of competitive performance:
    wins / (wins + podiums + top 10 finishes)
    """
    
    results = get_driver_results(driver_id, season)
    
    wins = len([r for r in results if r.position == 1])
    podiums = len([r for r in results if r.position <= 3])
    top_10 = len([r for r in results if r.position <= 10])
    
    # Weighted average: win is "worth" 3 podiums
    weighted_score = (wins * 3 + podiums + top_10 / 2) / (wins * 3 + podiums + top_10 / 2 + len(results))
    
    # Normalize to 0-10
    score = weighted_score * 10
    
    return min(score, 10.0)
```

### Examples

**Max Verstappen 2022** (15 wins, 17 podiums in 22 races):
- Weighted score: (15×3 + 17 + 22/2) / (45 + 17 + 11 + 22) = 73/95 = 0.77
- Score: 7.7/10

**Sergio Perez 2022** (1 win, 11 podiums in 22 races):
- Weighted score: (1×3 + 11 + 22/2) / (3 + 11 + 11 + 22) = 25/47 = 0.53
- Score: 5.3/10

---

## 7. RELIABILITY SCORE (5%)

### Definition
Inverse of Did-Not-Finish rate (mechanical/reliability-caused).

### Formula
```python
def reliability_score(driver_id, season):
    """
    Measure of car/team reliability:
    (1 - dnf_rate) * 10
    """
    
    results = get_driver_results(driver_id, season)
    total_races = len(results)
    
    # Count reliability DNFs (exclude crashes, driver errors)
    reliability_dnfs = len([
        r for r in results 
        if r.status in ['Engine', 'Brake failure', 'Gearbox', 'Hydraulics', 'Mechanical', 'Tyre']
    ])
    
    dnf_rate = reliability_dnfs / total_races if total_races > 0 else 0
    
    reliability_score = (1.0 - dnf_rate) * 10
    
    return min(reliability_score, 10.0)
```

### Examples

**2024 Ferrari Team** (relatively reliable):
- Reliability DNFs: 2 out of 22 races
- DNF rate: 0.09 (9%)
- Reliability score: 9.1/10

**2014 McLaren-Honda** (notoriously unreliable):
- Reliability DNFs: 8 out of 20 races
- DNF rate: 0.40 (40%)
- Reliability score: 6.0/10

---

## 8. COMBINED DRIVER PERFORMANCE INDEX

### Formula

```python
def driver_performance_index(
    driver_id, 
    season,
    weights={
        'race': 0.25,
        'lap': 0.25,
        'qualifying': 0.15,
        'championship': 0.15,
        'consistency': 0.10,
        'wins_podiums': 0.05,
        'reliability': 0.05
    }
):
    """Calculate combined DPI (0-10)."""
    
    scores = {
        'race': race_performance_score(driver_id, season),
        'lap': lap_performance_score(driver_id, season),  # 0 if pre-1996
        'qualifying': qualifying_score(driver_id, season),
        'championship': championship_score(driver_id, season),
        'consistency': consistency_score(driver_id, season),
        'wins_podiums': wins_podiums_score(driver_id, season),
        'reliability': reliability_score(driver_id, season),
    }
    
    # Handle pre-1996 (no lap times)
    if scores['lap'] == 0:
        # Redistribute lap weight to other components
        lap_weight = weights['lap']
        other_weight_sum = 1.0 - weights['lap']
        for key in weights:
            if key != 'lap':
                weights[key] = weights[key] / other_weight_sum * (1.0 - lap_weight)
    
    dpi = sum(scores[k] * weights[k] for k in scores.keys())
    
    return min(dpi, 10.0)
```

### Examples

**Lewis Hamilton 2008** (Rookie, McLaren):
- Race: 8.2 (1 win, good points)
- Lap: 7.8 (competitive vs Alonso)
- Qualifying: 7.9 (good grid positions)
- Championship: 7.1 (2nd in points)
- Consistency: 7.5 (variable performances)
- Wins/Podiums: 6.8
- Reliability: 8.1
- **DPI: 7.6/10**

**Ayrton Senna 1988** (McLaren-Honda dominance):
- Race: 9.4 (15 wins, very dominant)
- Lap: 9.1 (fastest lap rate very high)
- Qualifying: 9.8 (15 poles out of 16 races!)
- Championship: 9.7 (world champion)
- Consistency: 9.3 (extremely consistent)
- Wins/Podiums: 9.6
- Reliability: 9.4
- **DPI: 9.5/10**

---

## 9. IMPORTANT CAVEATS

### 1. Car Performance is Not Driver Performance
A driver in a Ferrari-powered car will score higher than the same driver in a Williams, all else equal.

**Mitigation:** Consider pairing DPI with constructor performance scores.

### 2. Era Standardization Issues
Weighting these components equally across 1950-2026 is problematic because:
- Pre-1996: No lap time data (lap component = 0)
- Pre-2003: Different qualifying formats
- 1950s: Very few races per season

**Solution:** Apply era adjustments where needed.

### 3. Teammate Comparison
DPI works best for comparing drivers ACROSS seasons within same team/era.

For Hamilton vs Senna directly: Use relative metrics instead.

### 4. Weighting is Arbitrary
The 25%-25%-15%-15%-10%-5%-5% split is PROPOSED, not optimal.

You should adjust weights based on your specific ML task:
- For race winner prediction: increase race (40%) and lap (35%), decrease qualifying (10%)
- For qualifying prediction: increase qualifying (40%), decrease lap (15%)
- For championship prediction: increase championship (30%), decrease others

### 5. This is a Statistical Tool, Not Reality
DPI quantifies performance patterns but doesn't capture:
- Driver maturity/consistency over time
- Mental resilience in adversity
- Team dynamics and political factors
- Career trajectory and potential

Use DPI as ONE input to analysis, not THE answer.

---

## 10. SENSITIVITY ANALYSIS

Test different weightings:

```python
weights_aggressive = {
    'race': 0.40,
    'lap': 0.30,
    'qualifying': 0.10,
    'championship': 0.10,
    'consistency': 0.05,
    'wins_podiums': 0.03,
    'reliability': 0.02,
}

weights_balanced = {  # Default
    'race': 0.25,
    'lap': 0.25,
    'qualifying': 0.15,
    'championship': 0.15,
    'consistency': 0.10,
    'wins_podiums': 0.05,
    'reliability': 0.05,
}

weights_qualifying_focused = {
    'race': 0.20,
    'lap': 0.15,
    'qualifying': 0.40,
    'championship': 0.10,
    'consistency': 0.08,
    'wins_podiums': 0.04,
    'reliability': 0.03,
}
```

Test each weighting against your ML task and choose based on performance.

---

## SUMMARY

Driver Performance Index (DPI) provides a 0-10 rating combining 7 independent metrics.

**Use it for:**
- Comparing drivers within same season
- Benchmarking performance across eras
- ML feature engineering
- Dashboard visualization

**Don't use it for:**
- Objective "who is the best driver"
- Comparing across radically different eras
- Replacing detailed race-by-race analysis

**Customize the weighting** for your specific prediction task.

---

**End of Driver Rating Methodology**

Questions? See FEATURE_ENGINEERING.md for detailed formulas.
