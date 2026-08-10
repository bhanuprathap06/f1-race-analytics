# DATA LEAKAGE PREVENTION POLICY
## Formula 1 ML Prediction Systems

**Version:** 1.0  
**Date:** 2026-08-10  
**Purpose:** Ensure no future information leaks into predictive models

---

## EXECUTIVE SUMMARY

**Data leakage is the #1 error in predictive modeling.**

This system prevents it by enforcing a strict **temporal cutoff policy**: 
- Features may ONLY include information available BEFORE the target race
- Target variables are ONLY known AFTER the race occurs
- Dataset includes TWO versions for each prediction task

---

## THE TEMPORAL CUTOFF PRINCIPLE

### Definition
For any target race on date `T`:

**ALLOWED FEATURES:** Data from races before `T` (and qualifying info if using qualifying model)  
**FORBIDDEN FEATURES:** Any data from race `T` or after

### Example: 2024 Monaco GP (2024-05-26)

#### ALLOWED Features
- 2024 seasons opener (Australia, 2024-03-24): results, positions, points ✓
- All 2023 races ✓
- All historical races ✓
- Monaco qualifying (2024-05-25) if model variant uses it ✓
- Monaco practice (2024-05-24) if available ✓

#### FORBIDDEN Features
- 2024 Monaco race results ✗ (known after race)
- 2024 Monaco final positions ✗
- 2024 Monaco fastest lap ✗
- 2024 post-race standings ✗
- Bahrain 2024 results if predicting Australia 2024 ✗
- ANY race info after target race ✗

---

## IMPLEMENTATION: TWO DATASET VERSIONS

### Version A: PRE-QUALIFYING PREDICTION
**Use Case:** Predict winner/podium before qualifying happens

**Cutoff:** Start of qualifying day (minus ~24 hours)

**Available Data:**
- Grid position: NO (not known yet)
- Qualifying lap time: NO (not known yet)
- Weather forecast for race: YES (if available)
- Prior races: YES (all history before qualifying)
- Driver performance: YES (prior season)
- Constructor performance: YES (prior season)
- Circuit history: YES
- Practice sessions: MAYBE (depends on data source)

**Filename:** `01a_race_prediction_dataset_PRE_QUALIFYING.csv`

**Columns Removed:**
- `qualifying_position`
- `qualifying_lap_time`
- `qualifying_lap_time_ms`
- `grid_position` (this is based on qualifying)

**Use:** Training models that predict purely from prior form, not knowing qualifying result

---

### Version B: POST-QUALIFYING PREDICTION
**Use Case:** Predict podium/position after qualifying, before race

**Cutoff:** After qualifying, before race start

**Available Data:**
- All data from Version A: YES
- Grid position: YES (from qualifying)
- Qualifying lap time: YES
- Qualifying gap to pole: YES
- Car setup confirmed: NO (not publicly known mid-race)
- Race weather forecast: YES (if updated)
- Race strategy: NO (not finalized)

**Filename:** `01b_race_prediction_dataset_POST_QUALIFYING.csv`

**Columns Added:**
- `qualifying_position`
- `qualifying_lap_time`
- `qualifying_lap_time_ms`
- `grid_position`
- `qualifying_gap_to_pole_ms`
- `qualifying_percentile`

**Use:** Training models that use qualifying result to predict race outcome

---

## DETAILED FEATURE-BY-FEATURE LEAKAGE MATRIX

### Features That Are ALWAYS SAFE (No Temporal Issues)

| Feature | Why Safe | Example |
|---------|----------|---------|
| `career_wins_before_race` | Calculated from prior races only | Sydney 2024 predictions: use wins through Adelaide 2024 |
| `career_podiums_before_race` | Calculated from prior races only | Same |
| `career_points_before_race` | Calculated from prior races only | Same |
| `previous_3_race_avg_position` | Uses races n-3, n-2, n-1 only | Sydney race: use Melbourne, Shanghai, Bahrain |
| `previous_5_race_avg_position` | Uses races n-5 to n-1 only | Same principle |
| `driver_circuit_wins_before_race` | Uses only prior visits to circuit | Monaco 2024: use Monaco 2023 and earlier |
| `driver_circuit_podiums_before_race` | Uses only prior visits to circuit | Same |
| `previous_race_position` | Strictly race n-1 | Sydney 2024: use Melbourne 2024 result |
| `constructor_wins_before_race` | Calculated from prior races only | Same as driver |

---

### Features That REQUIRE Careful Cutoff (Version A vs B)

| Feature | Pre-Qualifying OK? | Post-Qualifying OK? | Why | Mitigation |
|---------|-------------------|-------------------|-----|-----------|
| `grid_position` | NO | YES | Based on qualifying result | Removed from Version A |
| `qualifying_position` | NO | YES | Literal qualifying result | Removed from Version A |
| `qualifying_lap_time_ms` | NO | YES | From qualifying session | Removed from Version A |
| `qualifying_gap_to_pole` | NO | YES | Computed from qualifying | Removed from Version A |

---

### Features That Are NEVER SAFE (ALWAYS FORBIDDEN)

| Feature | Why Forbidden | If Used | Risk |
|---------|--------------|---------|------|
| `final_position` | TARGET variable | Training features | Direct leakage |
| `points_scored` | Assigned after race | Training features | Direct leakage |
| `dnf` | Known after race | Training features | Direct leakage |
| `fastest_lap` | Recorded during race | Training features | During-race leakage |
| `fastest_lap_time_ms` | Recorded during race | Training features | During-race leakage |
| `laps_completed` | Known after race | Training features | Direct leakage |
| `race_time_ms` | Known after race | Training features | Direct leakage |
| `race_finish_status` | Known after race | Training features | Direct leakage |
| `post_race_driver_standing` | Assigned after race | Training features | Direct leakage |
| `post_race_constructor_standing` | Assigned after race | Training features | Direct leakage |

---

## SPECIAL CASES & EDGE CASES

### Case 1: Multi-Round Predictions
**Scenario:** Predict winner for rounds 1-5 together (season opening)

**Issue:** Round 2 features can't include Round 1 results

**Solution:** 
- For Round 1: Use only prior-season data
- For Round 2: Use Round 1 results ✓
- For Round 3: Use Rounds 1-2 results ✓
- Each race uses data from races before it only

**Implementation:** 
- Add `races_completed_in_season` column
- Filter training data by this column during model training

### Case 2: Qualifying Lineup Changes
**Scenario:** A driver gets grid penalty after qualifying

**Issue:** Grid position differs from qualifying position

**Solution:**
- Store both: `qualifying_position` and `grid_position`
- Version A: use neither
- Version B: use `grid_position` (actual starting position)
- Include `penalty_applied` flag if available

### Case 3: Sprint Race Results
**Scenario:** Predict Sunday main race using Saturday sprint result

**Issue:** Sprint occurs day before main race; is it leakage?

**Solution:**
- **Debate:** Is Saturday sprint info available before Sunday prediction?
- **Decision:** Treat sprint as a separate race event
- Create `02b_race_prediction_dataset_POST_SPRINT.csv` for races after sprints
- For races without sprints, sprint columns are NULL
- Clearly label sprint data as "Saturday race result"

### Case 4: Friday Practice Data
**Scenario:** Use Friday FP1/FP2 lap times to predict Sunday

**Issue:** Friday data is before race; is it allowable?

**Solution:**
- Friday data is technically before race ✓
- However, it's NOT part of official F1 records in F1DB
- Available only via OpenF1 (2023+)
- Create separate column: `Friday_practice_available` (bool)
- For pre-2023: NULL (not in data)
- Document assumption: "Friday practice is not race-determining data"

### Case 5: Historical Races (1950-2022)
**Scenario:** Building training set for entire history

**Issue:** Can't predict 1950 without prior data

**Solution:**
- First race (1950 British GP): mark as `prediction_possible=0`
- First N races (before 10 races completed): mark as `insufficient_history=1`
- Filter training data: only use rows where sufficient history exists
- Document: "Models trained on races 11 onward (sufficient prior races)"

---

## AUTOMATED LEAKAGE DETECTION

### Checks Run on Every Dataset Build

```python
def check_data_leakage(dataset, target_column='final_position'):
    """
    Automated checks for data leakage
    """
    issues = []
    
    # Check 1: No race results in feature set
    forbidden_cols = ['final_position', 'winner', 'podium', 'dnf', 
                      'points_scored', 'fastest_lap_time_ms', 'laps_completed']
    for col in forbidden_cols:
        if col in dataset.columns and col != target_column:
            issues.append(f"LEAKAGE: {col} found in features (should be target only)")
    
    # Check 2: No post-race standings
    if 'post_race_standing_position' in dataset.columns:
        issues.append("LEAKAGE: post-race standing in features")
    
    # Check 3: Temporal ordering for prior race features
    for race_idx, row in dataset.iterrows():
        race_id = row['race_id']
        race_date = row['race_date']
        
        if 'previous_race_position' in dataset.columns:
            prev_race_id = row['previous_race_id']
            prev_race_date = row['previous_race_date']
            
            if prev_race_date >= race_date:
                issues.append(f"LEAKAGE: Race {race_id} uses race {prev_race_id} which is not prior")
    
    return issues
```

### Checks Performed
1. ✓ No forbidden columns present
2. ✓ Temporal ordering of prior races
3. ✓ No future standings included
4. ✓ No during-race metrics included
5. ✓ Qualifying data only in POST_QUALIFYING version
6. ✓ Career stats correctly calculated (through race n-1 only)

---

## VALIDATION CHECKLIST

### Before Using Dataset for Model Training

- [ ] Dataset version clearly labeled (PRE/POST/BOTH)
- [ ] All forbidden columns verified removed
- [ ] Temporal ordering spot-checked (random 10 rows)
- [ ] Earliest races marked as `insufficient_history=1`
- [ ] Data leakage script run: zero issues reported
- [ ] Data dictionary reviewed for this specific use case
- [ ] Target variable clearly identified
- [ ] Features all have `_before_race` or `_prior` suffix where relevant
- [ ] No columns from races after target race included
- [ ] Qualifying data only in POST_QUALIFYING version

---

## EXAMPLE: CORRECT FEATURE SET FOR PODIUM PREDICTION

### Target Race: 2024 Monaco GP (2024-05-26)

### Correct Features (POST-QUALIFYING Version)

```
season = 2024
round = 6
race_id = [Monaco 2024 ID]
race_date = 2024-05-26
race_name = "Monaco Grand Prix"
circuit_id = [Monaco ID]
circuit_name = "Circuit de Monaco"
country = "Monaco"

driver_id = [driver]
driver_name = [driver name]
constructor_id = [constructor]
constructor_name = [constructor name]

# Qualifying (ALLOWED because before race)
qualifying_position = 5 (from qualifying on 2024-05-25)
qualifying_lap_time_ms = 72340 (from qualifying)
grid_position = 5 (actual grid position after penalties if any)

# Career stats BEFORE this race (calculated through 2024 Bahrain)
career_wins_before_race = 7
career_podiums_before_race = 23
career_points_before_race = 145
races_completed_before_race = 45

# Recent performance (races 1-5 of 2024)
previous_race_position = 3 (2024 Bahrain result)
previous_race_points = 15 (2024 Bahrain points)
previous_3_race_avg_position = 3.67 (avg of Bahrain, Shanghai, Melbourne)
previous_5_race_avg_position = 4.4 (avg of Shanghai, Bahrain, Saudi Arabia, Australia, 2023 Abu Dhabi)
previous_5_race_avg_points = 10.5

# Circuit-specific history (through all prior Monaco races)
driver_circuit_races_before_race = 15 (races at Monaco before 2024)
driver_circuit_avg_finish_before_race = 4.2 (average position at Monaco)
driver_circuit_avg_lap_time_before_race = 74230 (average fastest lap)
driver_circuit_podiums_before_race = 7
driver_circuit_wins_before_race = 2

# Constructor stats BEFORE this race
constructor_wins_before_race = 23
constructor_podiums_before_race = 67
constructor_points_before_race = 287
constructor_previous_5_race_avg_position = 3.1

# TARGET VARIABLE (after race) - NOT IN TRAINING FEATURES
podium = 1 (if finished top 3) — ONLY KNOWN AFTER RACE
final_position = 2 — ONLY KNOWN AFTER RACE
dnf = 0 — ONLY KNOWN AFTER RACE
```

### INCORRECT Features (DON'T USE THESE)

```
race_fastest_lap_time_ms = 74100 ✗ (known after race)
laps_completed = 78 ✗ (known after race)
final_position = 2 ✗ (this is the target!)
points_scored = 18 ✗ (known after race)
post_race_standing_position = 3 ✗ (known after race)
race_finish_status = "Finished" ✗ (known after race)
fastest_lap_rank = 1 ✗ (known after race)
```

---

## VERSION CONTROL & DATASET FILENAMES

### Naming Convention
```
01_race_prediction_dataset_PRE_QUALIFYING.csv
01_race_prediction_dataset_POST_QUALIFYING.csv
01_race_prediction_dataset_BOTH.csv  (merged for reference, splits handled in code)
```

### Metadata Columns (In All Versions)
```
dataset_version = "PRE_QUALIFYING" | "POST_QUALIFYING"
leakage_check_status = "PASSED" | "FAILED"
leakage_check_date = "2026-08-10"
insufficient_history_flag = 1 (if <5 prior races) | 0
max_race_used_for_features = race_id (the most recent race whose data is included)
```

---

## REPORTING & DOCUMENTATION

Every dataset release must include:

1. **Leakage Report:** `LEAKAGE_CHECK_REPORT.txt`
   - Lists all checks performed
   - Reports pass/fail for each check
   - Any warnings or edge cases flagged

2. **Feature Timeline:** `FEATURE_AVAILABILITY_TIMELINE.csv`
   - For each feature, when it becomes available
   - Example: "qualifying_lap_time available from race 2024-Bahrain onward"

3. **Dataset Audit:** `DATASET_AUDIT.log`
   - Hash of dataset files
   - Row/column counts
   - Missing data percentages
   - Date generated

---

## SUMMARY

**The rule is simple:** 
> **Use only information that existed BEFORE the race you're predicting.**

**Two dataset versions:**
- **Version A (PRE-QUALIFYING):** No qualifying info
- **Version B (POST-QUALIFYING):** Includes qualifying info

**Use the version appropriate for your prediction task.**

**Run leakage checks automatically before model training.**

**Violations detected = do not use dataset.**

---

**End of Data Leakage Policy**
