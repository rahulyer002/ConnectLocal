-- Migration 002 — suburb_inference table
-- Precomputed elderly-friendliness inference per suburb. Populated by ETL.
-- Re-run is idempotent: load_suburb_inference() truncates before insert.

CREATE TABLE IF NOT EXISTS suburb_inference (
    suburb_id                BIGINT       PRIMARY KEY,

    score_rest               REAL,
    score_relief             REAL,
    score_amenities          REAL,
    score_shade              REAL,
    score_transit            REAL,
    score_social             REAL,

    outing_score             REAL,
    persona                  VARCHAR(64),
    data_completeness_pct    REAL,

    strengths                JSONB,
    gaps                     JSONB,
    peer_suburbs             JSONB,

    benches_per_100_elderly      REAL,
    toilets_per_100_elderly      REAL,
    wc_places_per_100_elderly    REAL,

    elderly_total            INTEGER,
    elderly_pct              REAL,
    welcoming_spaces         INTEGER,
    wc_place_count           INTEGER,
    wc_social_count          INTEGER,
    wc_essentials_count      INTEGER,
    wc_healthcare_count      INTEGER,
    bench_count              INTEGER,
    toilet_count             INTEGER,
    tree_count               INTEGER,
    stop_count               INTEGER,
    wc_stop_count            INTEGER,
    stop_modes               INTEGER,
    green_space_count        INTEGER,
    avg_tree_shade           REAL,
    dist_to_cbd_km           REAL,

    generated_at             TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_suburb_inference_outing_score
    ON suburb_inference (outing_score DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_suburb_inference_persona
    ON suburb_inference (persona);
