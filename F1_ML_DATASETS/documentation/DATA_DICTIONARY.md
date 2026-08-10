# DATA DICTIONARY
## Formula 1 ML Dataset System

**Generated:** 2026-08-10  
**Version:** 1.0  
**Scope:** All variables across 9 ML-ready datasets

---

## TABLE OF CONTENTS
1. Core Dimensions (drivers, constructors, circuits, races)
2. Race Results
3. Qualifying
4. Lap Times
5. Pit Stops
6. Championship Standings
7. Derived Features
8. Target Variables

---

## 1. CORE DIMENSIONS

### drivers
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| driver_id | INT | No | Unique driver identifier | 1-900 | F1DB | 1950 |
| driver_ref | STR | Yes | Driver reference code | - | F1DB | 1950 |
| number | INT | Yes | Driver racing number | 1-99 | F1DB | 1950 |
| code | STR | Yes | 3-letter driver code (HAM, VER) | 3 chars | F1DB | 1980 |
| forename | STR | No | First name | - | F1DB | 1950 |
| surname | STR | No | Last name | - | F1DB | 1950 |
| dob | DATE | Yes | Date of birth (YYYY-MM-DD) | - | F1DB | 1950 |
| nationality | STR | Yes | Driver nationality | - | F1DB | 1950 |

### constructors
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| constructor_id | INT | No | Unique constructor identifier | 1-300 | F1DB | 1950 |
| constructor_ref | STR | Yes | Constructor reference code | - | F1DB | 1950 |
| name | STR | No | Constructor name | - | F1DB | 1950 |
| nationality | STR | Yes | Constructor nationality | - | F1DB | 1950 |

### circuits
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| circuit_id | INT | No | Unique circuit identifier | 1-80 | F1DB | 1950 |
| circuit_ref | STR | Yes | Circuit reference code | - | F1DB | 1950 |
| name | STR | No | Circuit name | - | F1DB | 1950 |
| location | STR | Yes | Location description | - | F1DB | 1950 |
| country | STR | Yes | Country (ISO 3166-1) | 2 chars | F1DB | 1950 |
| lat | FLOAT | Yes | Latitude (decimal degrees) | -90 to 90 | F1DB | 1960 |
| lng | FLOAT | Yes | Longitude (decimal degrees) | -180 to 180 | F1DB | 1960 |
| alt | INT | Yes | Altitude (meters) | - | F1DB | 1960 |

### races
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| race_id | INT | No | Unique race identifier | - | F1DB | 1950 |
| year | INT | No | Season year (YYYY) | 1950-2026 | F1DB | 1950 |
| round | INT | No | Round in season | 1-24 | F1DB | 1950 |
| circuit_id | INT | No | Circuit where race held | - | F1DB | 1950 |
| name | STR | No | Race name (Grand Prix) | - | F1DB | 1950 |
| date | DATE | No | Race date (YYYY-MM-DD) | - | F1DB | 1950 |
| time | TIME | Yes | Race start time (HH:MM:SS UTC) | - | F1DB | 1950 |
| url | STR | Yes | Wikipedia URL | - | F1DB | 1950 |

---

## 2. RACE RESULTS

### results
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| result_id | INT | No | Unique result ID | - | F1DB | 1950 |
| race_id | INT | No | Foreign key to races | - | F1DB | 1950 |
| driver_id | INT | No | Foreign key to drivers | - | F1DB | 1950 |
| constructor_id | INT | No | Foreign key to constructors | - | F1DB | 1950 |
| number | INT | Yes | Car number | 1-99 | F1DB | 1950 |
| grid | INT | Yes | Starting grid position | 0-50 | F1DB | 1950 |
| position | INT\|STR | Yes | Final position or status (R, D, E, F, W, N) | 1+ or code | F1DB | 1950 |
| positionText | STR | Yes | Position text ("+1 Lap", "DNF") | - | F1DB | 1950 |
| points | FLOAT | No | Championship points awarded | 0-25 | F1DB | 1950 |
| laps | INT | No | Laps completed | 0+ | F1DB | 1950 |
| time | STR | Yes | Finishing time (HH:MM:SS.mmm or gap) | - | F1DB | 1950 |
| milliseconds | INT | Yes | Finishing time in milliseconds | - | F1DB | 1957 |
| fastestLap | INT | Yes | Fastest lap rank (1=best) | 1+ | F1DB | 1950 |
| rank | INT | Yes | Fastest lap rank (alternative field) | 1+ | F1DB | 1950 |
| fastestLapTime | STR | Yes | Fastest lap time (MM:SS.mmm) | - | F1DB | 1950 |
| fastestLapTimeInMillis | INT | Yes | Fastest lap time in milliseconds | - | F1DB | 2004 |
| statusId | INT | No | Finishing status ID (see status table) | 1-150 | F1DB | 1950 |

### status (Race finish codes)
| Code | Meaning |
|------|---------|
| +1 Lap | Completed but one lap behind |
| Accident | DNF - Accident |
| Brake failure | DNF - Technical failure |
| Engine | DNF - Engine failure |
| Gearbox | DNF - Gearbox failure |
| Hydraulics | DNF - Hydraulic failure |
| Mechanical | DNF - Mechanical failure |
| Tyre | DNF - Tyre failure |
| Weather | DNF - Weather-related (accident/spin) |
| Finished | Completed race (may include DNF) |
| DNF | Generic Did Not Finish |

---

## 3. QUALIFYING

### qualifying
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| qualify_id | INT | No | Unique qualifying result ID | - | F1DB | 1950 |
| race_id | INT | No | Foreign key to races | - | F1DB | 1950 |
| driver_id | INT | No | Foreign key to drivers | - | F1DB | 1950 |
| constructor_id | INT | No | Foreign key to constructors | - | F1DB | 1950 |
| number | INT | Yes | Car number | 1-99 | F1DB | 1950 |
| position | INT | Yes | Qualifying position (1=pole) | 1-30 | F1DB | 1950 |
| q1 | STR | Yes | Q1 time (MM:SS.mmm) or NULL if eliminated | - | F1DB | 2003 |
| q2 | STR | Yes | Q2 time (MM:SS.mmm) or NULL if eliminated | - | F1DB | 2003 |
| q3 | STR | Yes | Q3 time (MM:SS.mmm) or NULL if eliminated | - | F1DB | 2003 |

**Note:** Pre-2003 qualifying had different formats (single run, multiple run without sessions). See DATA_PROVENANCE.md for format changes.

---

## 4. LAP TIMES

### lap_times
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| race_id | INT | No | Foreign key to races | - | F1DB | 1996 |
| driver_id | INT | No | Foreign key to drivers | - | F1DB | 1996 |
| lap | INT | No | Lap number in race | 1+ | F1DB | 1996 |
| position | INT | Yes | Driver position on this lap | 1-30 | F1DB | 1996 |
| time | STR | Yes | Lap time (MM:SS.mmm) | - | F1DB | 1996 |
| milliseconds | INT | Yes | Lap time in milliseconds | - | F1DB | 1996 |

**Critical Note:** Lap times only available from 1996 onwards. Cannot use lap-time analysis for 1950-1995. Do not interpolate.

---

## 5. PIT STOPS

### pit_stops
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| race_id | INT | No | Foreign key to races | - | F1DB | 1994 |
| driver_id | INT | No | Foreign key to drivers | - | F1DB | 1994 |
| stop | INT | No | Pit stop sequence (1st, 2nd, etc) | 1+ | F1DB | 1994 |
| lap | INT | No | Lap on which stop occurred | 1+ | F1DB | 1994 |
| time | STR | No | Time of pit stop (HH:MM:SS) | - | F1DB | 1994 |
| duration | STR | Yes | Pit stop duration (MM:SS.mmm) | - | F1DB | 2003 |
| milliseconds | INT | Yes | Pit stop duration in milliseconds | - | F1DB | 2003 |

**Note:** Pit stop duration only reliably available from 2003 onwards.

---

## 6. CHAMPIONSHIP STANDINGS

### driver_standings
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| driverStandingsId | INT | No | Unique ID | - | F1DB | 1950 |
| raceId | INT | No | Foreign key to races | - | F1DB | 1950 |
| driverId | INT | No | Foreign key to drivers | - | F1DB | 1950 |
| points | FLOAT | No | Cumulative championship points | 0+ | F1DB | 1950 |
| position | INT | Yes | Championship position (1=leader) | 1+ | F1DB | 1950 |
| positionText | STR | Yes | Position with ties noted | - | F1DB | 1950 |
| wins | INT | No | Wins accumulated to date | 0+ | F1DB | 1950 |

### constructor_standings
| Column | Type | Nullable | Description | Range | Source | Available From |
|--------|------|----------|-------------|-------|--------|-----------------|
| constructorStandingsId | INT | No | Unique ID | - | F1DB | 1950 |
| raceId | INT | No | Foreign key to races | - | F1DB | 1950 |
| constructorId | INT | No | Foreign key to constructors | - | F1DB | 1950 |
| points | FLOAT | No | Cumulative championship points | 0+ | F1DB | 1950 |
| position | INT | Yes | Championship position (1=leader) | 1+ | F1DB | 1950 |
| positionText | STR | Yes | Position with ties noted | - | F1DB | 1950 |
| wins | INT | No | Constructor wins to date | 0+ | F1DB | 1950 |

**Note:** Scoring system changed multiple times (8-6-4-3-2-1 → 10-8-6 → current). Historical points follow original scoring rules; do not normalize.

---

## 7. DERIVED FEATURES

### Calculated in 01_race_prediction_dataset.csv

#### Historical Driver Features (Pre-Race)
| Feature | Type | Description | Calculation |
|---------|------|-------------|-------------|
| career_wins_before_race | INT | Driver wins before this race | COUNT(position=1) for all prior races |
| career_podiums_before_race | INT | Driver podiums before this race | COUNT(position≤3) for all prior races |
| career_points_before_race | FLOAT | Career points accumulated | SUM(points) from championship standings |
| races_completed_before_race | INT | Races this driver started | COUNT(*) prior races |
| previous_race_position | INT | Finish position in race n-1 | From prior race results |
| previous_race_points | FLOAT | Points from race n-1 | From prior race results |
| previous_3_race_avg_position | FLOAT | Average finish position last 3 races | MEAN(position) for races n-3, n-2, n-1 |
| previous_5_race_avg_position | FLOAT | Average finish position last 5 races | MEAN(position) for races n-5 to n-1 |
| previous_5_race_avg_points | FLOAT | Average points last 5 races | MEAN(points) for last 5 races |
| previous_5_race_avg_lap_time | FLOAT | Average fastest lap last 5 races | MEAN(fastest_lap_time_ms) for last 5 races |
| driver_dnf_rate_before_race | FLOAT | Proportion of DNF 0.0-1.0 | COUNT(DNF) / COUNT(total) |

#### Historical Constructor Features (Pre-Race)
| Feature | Type | Description | Calculation |
|---------|------|-------------|-------------|
| constructor_wins_before_race | INT | Constructor wins before this race | COUNT(position=1) for constructor |
| constructor_podiums_before_race | INT | Constructor podiums before this race | COUNT(position≤3) for constructor |
| constructor_points_before_race | FLOAT | Constructor points accumulated | SUM(points) from standings |
| constructor_previous_5_race_avg_position | FLOAT | Constructor avg finish last 5 races | MEAN(position) for last 5 races |
| constructor_previous_5_race_avg_points | FLOAT | Constructor avg points last 5 races | MEAN(points) for last 5 races |
| constructor_dnf_rate_before_race | FLOAT | Proportion of DNF 0.0-1.0 | COUNT(DNF) / COUNT(total) |

#### Circuit-Specific Historical Features (Pre-Race)
| Feature | Type | Description | Calculation |
|---------|------|-------------|-------------|
| driver_circuit_races_before_race | INT | Times driver raced at this circuit | COUNT(*) at this circuit only |
| driver_circuit_avg_finish_before_race | FLOAT | Average finish position at circuit | MEAN(position) at this circuit |
| driver_circuit_avg_lap_time_before_race | FLOAT | Avg fastest lap time at circuit (ms) | MEAN(fastest_lap_time_ms) at circuit |
| driver_circuit_podiums_before_race | INT | Podiums at this circuit | COUNT(position≤3) at circuit |
| driver_circuit_wins_before_race | INT | Wins at this circuit | COUNT(position=1) at circuit |

### Calculated in 04_driver_performance_dataset.csv

#### Performance Scores (Scale 0.0-10.0)
| Score | Components | Formula | Range |
|-------|------------|---------|-------|
| race_performance_score | Wins, podiums, points | NORMALIZE(wins×10 + podiums×5 + points/max_points×10) | 0.0-10.0 |
| lap_performance_score | Fastest lap rate, avg lap speed | NORMALIZE(fastest_lap_count/races + avg_speed/max_speed) | 0.0-10.0 |
| qualifying_score | Pole rate, avg qualifying position | NORMALIZE(pole_rate + 1/avg_qual_pos) | 0.0-10.0 |
| consistency_score | Low std dev in positions/lap times | NORMALIZE(1 - (position_std / 20) - (lap_time_std / max_std)) | 0.0-10.0 |
| championship_score | Points as % of max possible | (championship_points / (races × max_points_per_race)) × 10 | 0.0-10.0 |
| reliability_score | Inverse of DNF rate | (1 - dnf_rate) × 10 | 0.0-10.0 |
| overall_driver_index | Weighted combination | See DRIVER_RATING_METHODOLOGY.md | 0.0-10.0 |

---

## 8. TARGET VARIABLES (FOR PREDICTION)

### 01_race_prediction_dataset.csv
| Target | Type | Description | Values |
|--------|------|-------------|--------|
| final_position | INT | Driver's finishing position | 1+ or NULL if DNF |
| winner | INT | Binary: did driver win? | 0 or 1 |
| podium | INT | Binary: top-3 finish? | 0 or 1 |
| dnf | INT | Binary: did-not-finish? | 0 or 1 |
| points_scored | FLOAT | Championship points awarded | 0+ |

### 02_lap_performance_dataset.csv
| Target | Type | Description | Values |
|--------|------|-------------|--------|
| lap_time_ms | INT | Time for this lap (milliseconds) | 0+ |
| lap_time_zscore | FLOAT | Normalized to circuit median | -3.0 to +3.0 (typically) |
| lap_position | INT | Driver's position on this lap | 1-20 |
| lap_consistency | FLOAT | How consistent vs own avg (0.0-1.0) | 0.0-1.0 |

---

## MISSING DATA CODES

| Code | Meaning | Action |
|------|---------|--------|
| NULL / NaN | Data not recorded or not applicable | Leave empty; treat as missing |
| NOT_APPLICABLE | Feature doesn't apply (e.g., pit stop for non-stop race) | Leave empty; document context |
| NOT_RECORDED | Data never recorded in this era | Leave empty; document era |
| UNKNOWN | Data should exist but unavailable | Leave empty; flag in quality report |

---

## NORMALIZATION & STANDARDIZATION

### Qualifying Time Standardization
All qualifying times converted to **milliseconds (integer)**:
- Q1, Q2, Q3 times (modern era): direct millisecond value
- Pre-2003 qualifying: convert MM:SS.mmm → milliseconds
- Pre-1960: NULL (not recorded)

### Lap Time Standardization
All lap times stored as **milliseconds (integer)**:
- Post-1996: direct from milliseconds
- Pre-1996: NULL (not available)

### Pit Stop Duration Standardization
All pit stop durations stored as **milliseconds (integer)**:
- Post-2003: direct from milliseconds
- 1994-2002: NULL for duration (stop occurred but timing not recorded)

### Position Standardization
All positions stored as **integers**:
- 1 = First place (winner)
- 2 = Second place
- NULL or "DNF" flag = Did not finish
- No negative positions

### Points Standardization
Championship points stored as **float** (to handle partial points):
- Current system: 0, 1, 2, 4, 6, 8, 10, 12, 15, 18, 20, 25
- Historical systems: document in scoring_era column
- Do NOT normalize across eras; preserve historical values

---

## CATEGORICAL VARIABLES

### Status Codes (Finishing Status)
Standard F1 finish status codes (see status table above). Values like:
- "Finished" = Completed race
- "Accident" = DNF via accident
- "Engine" = DNF via engine
- "Brake failure" = DNF via brakes
- "+1 Lap" = Completed but one lap down

### Era Classification
| Era | Years | Key Changes |
|-----|-------|------------|
| EARLY | 1950-1959 | No lap times, limited data |
| CLASSIC | 1960-1971 | Qualifying introduced, single run |
| MODERN_EARLY | 1972-1989 | Improved timing, points changes |
| MODERN | 1990-2002 | Electronic timing, refueling |
| HYBRID_EARLY | 2003-2008 | Refueling ban, current Q format |
| HYBRID | 2009-2020 | DRS, hybrid units (2014+) |
| TURBO_HYBRID | 2021-2026 | Sprint races, cost caps, new tech |

---

**End of Data Dictionary**

For detailed variable definitions, see individual dataset sections.
For historical coverage gaps, see DATA_PROVENANCE.md
For derivation methods, see FEATURE_ENGINEERING.md
