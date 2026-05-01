# Data Notes , ConnectLocal (Iteration 1)

## Overview

This document outlines the data processing workflow used to prepare ABS Census 2021 data for the ConnectLocal project.

The goal of this stage is to create a clean, suburb-level dataset (SA2 level) that supports analysis of:
- Age distribution
- Vulnerability (need for assistance)
- Population characteristics relevant to loneliness and accessibility

---

## Data Sources

Primary dataset:
- ABS Census 2021 , General Community Profile (GCP) for SA2 (Victoria)

Files used:
- G01: General population and age distribution
- G04A: Detailed age breakdown (explored, not used in v1)
- G11A: Education (loaded for exploration)
- G16A: Income (loaded for exploration)
- G17A: Household income distribution (loaded for exploration)
- G18: Need for assistance (key vulnerability indicator)

---

## Processing Workflow

The processing script (`abs_processing.py`) follows a modular pipeline:

### 1. Load Data
All required CSV files are loaded using a reusable `load_csv()` function:
- Ensures file existence
- Keeps file paths consistent

---

### 2. Build Base Suburb Table

The base dataset is created from G01:

- `SA2_CODE_2021` -> `suburb_id`
- `Tot_P_P` -> `population_total`

This ensures:
- One row per suburb (SA2)
- A clean primary key for joining additional features

---

### 3. Add Age Features (G01)

We use grouped age bands from G01 instead of detailed G04A data for simplicity and clarity.

Features added:
- `population_65_74`
- `population_75_84`
- `population_85_plus`

These directly align with the project focus on older adults.

---

### 4. Add Vulnerability Feature (G18)

From G18, we include:

- `P_Tot_Need_for_assistance` -> `need_assistance`

This acts as a **proxy for mobility limitations and vulnerability**, which is critical for:
- Accessibility-focused recommendations
- Identifying high-risk communities

---

### 5. Export Processed Dataset

The final dataset is exported to:
The script also prints:
- Preview of the dataset
- Column names
- Output path

---

## Output Dataset (v1)

The processed dataset includes:

- suburb_id
- population_total
- population_65_74
- population_75_84
- population_85_plus
- need_assistance

This forms the **foundation dataset for Iteration 1**.

---

## Key Design Decisions

### Why use G01 instead of G04A?
- G01 already provides grouped age bands (65+)
- Reduces complexity
- Keeps processing cleaner for backend integration

### Why include "need_assistance"?
- Strong proxy for:
  - Physical limitations
  - Mobility challenges
  - Social isolation risk

### Why SA2 level?
- Matches project scope (suburb-level recommendations)
- Compatible with other datasets (pedestrian, toilets, etc.)

---

## Current Limitations

- Suburb names are not yet included (only suburb_id)
- Income, household type, and transport variables are not yet integrated
- No normalization into multiple tables (single wide table used for now)

---

## Next Steps

Planned enhancements:

1. Add suburb names (if available in ABS metadata)
2. Add loneliness-related indicators:
   - Lone person households
   - Low income population
   - No vehicle access
3. Normalize dataset into ERD structure:
   - Suburb table
   - Demographics table
4. Integrate with other datasets:
   - Pedestrian data
   - Public infrastructure
   - Events (future)

---

## Summary

This workflow establishes a clean, reproducible pipeline for transforming raw ABS data into a structured dataset ready for:
- Backend integration
- Analysis
- Feature engineering

The approach prioritises:
- Clarity
- Reproducibility
- Alignment with project goals

---

## Landmark to Suburb Mapping

We mapped landmarks to suburbs using geospatial proximity.

Steps:
1. Processed landmarks dataset (lat/lng extracted from coordinates)
2. Generated suburb centroids using ABS SA2 shapefile
3. Calculated nearest suburb for each landmark using Euclidean distance
4. Assigned:
   - suburb_id
   - suburb_name

Output:
- processed/landmarks.csv

This enables:
- linking landmarks to demographic data
- suburb-level aggregation
- location-based recommendations