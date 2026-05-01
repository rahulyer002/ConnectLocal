# Table Plan - ConnectLocal (Iteration 1)

## Table: suburb_profile

### Description
A suburb-level dataset (SA2) containing population and vulnerability indicators derived from ABS Census 2021 data.

Each row represents one suburb.

---

## Columns

| Column Name            | Description                                      | Source File | Source Column                  |
|----------------------|--------------------------------------------------|------------|-------------------------------|
| suburb_id            | Unique suburb identifier (SA2 code)              | G01        | SA2_CODE_2021                 |
| population_total     | Total population                                 | G01        | Tot_P_P                       |
| population_65_74     | Population aged 65 - 74                            | G01        | Age_65_74_yr_P                |
| population_75_84     | Population aged 75 - 84                            | G01        | Age_75_84_yr_P                |
| population_85_plus   | Population aged 85+                              | G01        | Age_85ov_P                    |
| need_assistance      | Total people needing assistance                  | G18        | P_Tot_Need_for_assistance     |

---

## Primary Key

- `suburb_id`

---

## Notes

- All data is aggregated at SA2 level
- Age variables are grouped to match project focus on elderly population
- Need for assistance is used as a proxy for vulnerability and mobility limitations

---

## Relationships (Future ERD)

Planned structure:

### suburb
- suburb_id (PK)
- suburb_name (to be added)

### demographics
- suburb_id (FK)
- population_total
- population_65_74
- population_75_84
- population_85_plus
- need_assistance

---

## Planned Additions

Future columns may include:

| Feature                     | Source File |
|----------------------------|------------|
| Lone person households     | Gxx        |
| Median income              | G16A       |
| Low income population      | G17A       |
| No vehicle households      | TBD        |

---

## File Output
Data/processed/suburb_profile.csv

---

## Summary

This table serves as the core dataset for Iteration 1, supporting:
- Suburb-level analysis
- Backend integration
- Feature expansion in later iterations

---

### LANDMARK (Processed)

| Column | Description |
|-------|------------|
| landmark_id | Unique ID |
| name | Landmark name |
| theme | Category |
| sub_theme | Sub-category |
| lat | Latitude |
| lng | Longitude |
| suburb_id | FK -> SUBURB |
| suburb_name | Human-readable suburb |

Derived via:
- landmarks.csv (City dataset)
- suburb_reference.csv (ABS shapefile)