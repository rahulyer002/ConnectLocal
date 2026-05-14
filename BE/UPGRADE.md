# ConnectLocal Backend v4.0.0 — Upgrade & Testing Guide

This release adds **Epic 6 (Suburb Explorer)** plus three previously orphan/unused datasets:

- **OSM accessibility** — 10K benches, 1.8K accessible toilets, 7.8K wheelchair-accessible places
- **Trees** — 82K rows with `shade_score` (was loaded but never exposed)
- **GTFS routes** — 799 rows with route colours (was loaded but never exposed)
- **Open-space shade** — merged into `open_space` as two new columns
- **Open-Meteo** — free no-key weather for every suburb centroid

No new pip dependencies. No new environment variables.

---

## What changed at a glance

### New files
```
app/models/osm_bench.py
app/models/osm_accessible_toilet.py
app/models/osm_wheelchair_place.py
app/services/open_meteo.py
app/services/suburb_service.py
app/services/accessibility_service.py
app/routers/accessibility.py
app/routers/trees.py
app/routers/routes.py
migrations/001_add_open_space_shade_columns.sql
```

### Modified files
```
app/models/__init__.py          + 3 imports
app/models/open_space.py        + 2 columns (shade_score_100, nearby_tree_count)
app/etl/load_data.py            + helpers + 4 loaders + updated main()
app/routers/suburbs.py          rewritten (preserves /profile, /search, /psychological-distress; adds /map, /compare, /{id}/snapshot + 9 drill-downs)
main.py                         + 3 router registrations, version 4.0.0
```

---

## Step 1 — Drop in the files

Copy the entire `BE/` folder into your repo. All paths match your existing structure.

If you prefer to patch your branch instead of overwriting, the modified files are listed above — review and merge manually.

---

## Step 2 — Add the OSM data

The ETL expects the OSM CSVs at this exact path (sibling of `BE/`):

```
Data/processed/osm_accessibility/osm_benches_clean.csv
Data/processed/osm_accessibility/osm_accessible_toilets_clean.csv
Data/processed/osm_accessibility/osm_wheelchair_accessible_places_clean.csv
Data/processed/open_space_shade.csv
```

These are the files from the `processed.zip` archive you uploaded earlier (already in `processed/osm_accessibility/`).

---

## Step 3 — Run the SQL migration

Apply the migration once against your RDS instance. `IF NOT EXISTS` makes it idempotent.

```bash
psql "$DATABASE_URL_SYNC" -f migrations/001_add_open_space_shade_columns.sql
```

Or paste the SQL straight into a Postgres client connected to `connectlocal-db.c5e06u42kqno.ap-southeast-4.rds.amazonaws.com`.

Verify:
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'open_space' AND column_name IN ('shade_score_100', 'nearby_tree_count');
-- should return 2 rows
```

---

## Step 4 — Run the ETL

```bash
cd BE
python -m app.etl.load_data
```

The new loaders run after the existing ones. Expected log:

```
Loading OSM benches...
  Filtered to Victoria bbox: 10,317 → 10,150
  Loaded 10,150 benches
Loading OSM accessible toilets...
  Filtered to Victoria bbox: 1,815 → 1,790
  Loaded 1,790 accessible toilets
Loading OSM wheelchair-accessible places...
  Filtered to Victoria bbox: 7,828 → 7,700
  Loaded 7,700 wheelchair-accessible places
Merging open space shade data...
  Merged shade data into 60 open_space rows (of 60)
```

The `Base.metadata.create_all()` at the start automatically creates the three new OSM tables — no DDL needed beyond the migration in Step 3.

---

## Step 5 — Start the server

```bash
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` — you should see new tagged sections:

- **Suburbs (Epic 6)** — adds `/map`, `/compare`, `/{id}/snapshot` + drill-downs
- **Accessibility (OSM)** — `/api/accessibility/benches`, `/toilets`, `/places`
- **Trees** — `/api/trees/nearby`, `/shade`
- **Transport Routes** — `/api/routes/search`, `/by-stop/{stop_id}`

The root `/` and `/health` endpoints now report version `4.0.0`.

---

## Step 6 — Test each endpoint

You can copy these into your browser, Postman, or `curl`. They all use `suburb_id=206041117` (Kew) and `lat=-37.8071, lon=145.0282` as a working example — substitute with any suburb you like.

### 6.1 Map paint (Layer 1) — feeds the hex map

```bash
curl http://localhost:8000/api/suburbs/map | jq '.total, .with_live_data, .suburbs[0]'
```

Expected: total ~525, with_live_data ~20-30 (sensor coverage is CBD-focused).

### 6.2 Snapshot (Layer 2) — the one-tap, every-signal endpoint

```bash
curl http://localhost:8000/api/suburbs/206041117/snapshot | jq
```

You should get nested blocks: `crowd`, `weather`, `events`, `accessibility`, `transport`, `green_spaces`, `landmarks`, `trees`, `demographics`, `actions`. Try a CBD suburb (Melbourne `206041122`) for non-null crowd data.

### 6.3 Drill-downs (Layer 3) — each works standalone

```bash
curl http://localhost:8000/api/suburbs/206041117/pedestrian     # crowd + trend
curl http://localhost:8000/api/suburbs/206041117/weather        # Open-Meteo
curl http://localhost:8000/api/suburbs/206041117/events?rows=5  # Eventfinda
curl http://localhost:8000/api/suburbs/206041117/accessibility  # OSM
curl http://localhost:8000/api/suburbs/206041117/transport      # stops + routes
curl http://localhost:8000/api/suburbs/206041117/green-spaces   # parks + shade
curl http://localhost:8000/api/suburbs/206041117/landmarks
curl http://localhost:8000/api/suburbs/206041117/trees
curl http://localhost:8000/api/suburbs/206041117/best-times?top_n=5
```

### 6.4 Compare — cross-suburb

```bash
curl "http://localhost:8000/api/suburbs/compare?suburb_ids=206041117,206041122"
```

### 6.5 Standalone OSM accessibility — point-based

```bash
# Benches near a coordinate (Kew centroid)
curl "http://localhost:8000/api/accessibility/benches?lat=-37.8071&lon=145.0282&radius_km=0.5"

# Accessible toilets — toggle confirmed_wheelchair_only=true for high-confidence only
curl "http://localhost:8000/api/accessibility/toilets?lat=-37.8071&lon=145.0282&radius_km=1.0&confirmed_wheelchair_only=true"

# Wheelchair-accessible cafes
curl "http://localhost:8000/api/accessibility/places?lat=-37.8071&lon=145.0282&category=social&radius_km=2"

# All category/amenity filter options for FE dropdowns
curl http://localhost:8000/api/accessibility/places/categories
```

### 6.6 Trees & shade

```bash
curl "http://localhost:8000/api/trees/nearby?lat=-37.8071&lon=145.0282&radius_km=0.2"
curl "http://localhost:8000/api/trees/shade?lat=-37.8071&lon=145.0282&radius_m=50"
```

### 6.7 GTFS routes

```bash
curl "http://localhost:8000/api/routes/search?mode=tram&limit=10"
curl "http://localhost:8000/api/routes/search?q=109"
# replace <stop_id> with one from your gtfs_stop table
curl "http://localhost:8000/api/routes/by-stop/<stop_id>"
```

---

## Frontend endpoint mapping

| Frontend page | Endpoint |
|---|---|
| Suburb Explorer hex map (paint) | `GET /api/suburbs/map` |
| Suburb Explorer right panel | `GET /api/suburbs/{id}/snapshot` |
| DiscoverPage | `GET /api/suburbs/{id}/events` |
| BestTimeNowPage | `GET /api/suburbs/{id}/pedestrian` |
| BestTimeWeekPage | `GET /api/suburbs/{id}/best-times` |
| JourneySupportPage | `/api/accessibility/toilets`, `/benches`, `/api/suburbs/{id}/transport` |
| WelcomingSpacesPage | `/api/suburbs/{id}/landmarks` + `/api/suburbs/{id}/accessibility` |
| HomePage stats | `GET /api/suburbs/{id}/snapshot` (read the `demographics` slice) |
| Cross-suburb comparison (new) | `GET /api/suburbs/compare?suburb_ids=a,b,c` |

---

## Snapshot response shape (reference)

```jsonc
{
  "suburb_id": 206041117, "suburb_name": "Kew",
  "centroid": { "lat": -37.8071, "lng": 145.0282 },
  "generated_at": "2026-05-14T10:23:00",
  "crowd": {
    "available": true, "people_per_hour": 198,
    "crowd_level": "Very Quiet",  // Very Quiet | Quiet | Moderate | Busy
    "trend": "Getting busier",    // Getting busier | Getting quieter | Steady
    "sensors_count": 2, "hour": 10, "day": "Thursday"
  },
  "weather": {
    "available": true, "temperature_c": 14.5, "humidity_pct": 65,
    "wind_speed_kmh": 8, "sky": "Partly cloudy",
    "summary": "Mild and partly cloudy — comfortable for a short outing",
    "is_safe_for_elderly": true, "warnings": [],
    "source": "open-meteo"
  },
  "events":        { "total": 3, "items": [/*Eventfinda items*/] },
  "accessibility": { "benches": 47, "accessible_toilets": 3,
                     "wheelchair_places": 89, "places_by_category": {...},
                     "sample_places": [...], "sample_toilets": [...] },
  "transport":     { "total_stops": 28, "by_mode": {"bus":18,"tram":8,"train":2},
                     "wheelchair_accessible_stops": 12, "routes_count": 14,
                     "routes": [/*with color_hex*/] },
  "green_spaces":  { "total": 4, "with_toilet": 2,
                     "avg_shade_score": 38.2, "spaces": [...] },
  "landmarks":     { "total": 12, "items": [...] },
  "trees":         { "total": 1247, "top_species": [...],
                     "avg_shade_score": 0.0012, "in_parks": 800, "in_streets": 447 },
  "demographics":  { "population_total": 25148, "elderly_total": 4612,
                     "elderly_pct": 18.3, "need_assistance": 612 },
  "actions": {
    "find_events_url":  "/discover?suburb_id=206041117",
    "plan_journey_url": "/journey?to_lat=...&to_lng=...&to_name=Kew",
    "best_times_url":   "/best-time/week?suburb_id=206041117"
  }
}
```

---

## Troubleshooting

**"relation osm_bench does not exist"** → the ETL didn't run, or `Base.metadata.create_all()` failed silently. Re-run `python -m app.etl.load_data`. The three OSM tables are created automatically.

**`shade_score_100` is always null** → migration didn't apply or `load_open_space_shade()` didn't run. Verify the column exists with the SQL in Step 3, then re-run the ETL.

**Map shows null for every suburb** → `pedestrian_pattern.suburb_id` is null for most rows, or the current hour has no sample. The endpoint correctly returns `has_live_data: false` in that case — this is expected for suburbs without CoM sensor coverage.

**Open-Meteo timeouts** → it's a free public API and very occasionally slow. The snapshot endpoint sets a 10s timeout and falls back to `available: false` — the rest of the snapshot will still return. No retries; restart the request.

**Compare endpoint shadowed** → `/compare` is declared BEFORE `/{suburb_id}/...` on purpose. FastAPI matches in declaration order. If you reorder the file, `/compare` will be parsed as `suburb_id=compare` and return 404.

---

## What was NOT included

- **GTFS transfers** — data quality issue (all rows are degenerate type-4 self-transfers with no `min_transfer_time`). Skip for now.
- **ABS SA2 GeoJSON polygons** — not in `processed/`. The hex tile UI doesn't need real polygons; if you later want a true choropleth map, process the SA2 shapefile and add a `geometry_geojson` column to `suburb`.
- **Redis caching** — every `/snapshot` runs ~7 DB queries + 2 async calls. At single-digit RPS that's fine; cache with a 60s TTL if traffic grows.
- **PostGIS** — all distance math is in Python. Fine at this scale (~30k records). Switch to PostGIS + GiST indexes if you want city-wide heatmaps in real time.
