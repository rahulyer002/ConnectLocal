-- migrations/001_add_open_space_shade_columns.sql
-- Run once against your RDS instance before running the new ETL.
-- IF NOT EXISTS makes this safe to re-run.

ALTER TABLE open_space
  ADD COLUMN IF NOT EXISTS shade_score_100   double precision,
  ADD COLUMN IF NOT EXISTS nearby_tree_count integer;
