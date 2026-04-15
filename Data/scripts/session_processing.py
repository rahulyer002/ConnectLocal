from __future__ import annotations

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_event_table() -> pd.DataFrame:
    path = PROCESSED_DIR / "event.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing event file: {path}\n"
            "Export the teammate's processed event table to Data/processed/event.csv first."
        )

    return pd.read_csv(path)


def validate_event_columns(events: pd.DataFrame) -> None:
    required = ["event_id", "datetime_start", "datetime_end"]
    missing = [col for col in required if col not in events.columns]

    if missing:
        raise KeyError(
            f"Missing required event columns: {missing}\n"
            f"Available columns are: {events.columns.tolist()}"
        )


def build_session_table(events: pd.DataFrame) -> pd.DataFrame:
    validate_event_columns(events)

    session_df = events[["event_id", "datetime_start", "datetime_end"]].copy()

    if "timezone" in events.columns:
        session_df["timezone"] = events["timezone"]
    else:
        session_df["timezone"] = "Australia/Melbourne"

    # Clean up
    session_df["event_id"] = session_df["event_id"].astype(str)
    session_df["datetime_start"] = pd.to_datetime(
        session_df["datetime_start"], errors="coerce"
    )
    session_df["datetime_end"] = pd.to_datetime(
        session_df["datetime_end"], errors="coerce"
    )

    session_df = session_df.dropna(subset=["datetime_start", "datetime_end"]).copy()

    # Iteration 1 assumption:
    # one session row per event row
    session_df = session_df.reset_index(drop=True)
    session_df["session_id"] = range(1, len(session_df) + 1)

    session_df = session_df[[
        "session_id",
        "event_id",
        "datetime_start",
        "datetime_end",
        "timezone"
    ]]

    return session_df


def export_sessions(session_df: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / "session.csv"
    session_df.to_csv(output_path, index=False)

    print(f"\nSaved session file to: {output_path}")
    print("\nPreview:")
    print(session_df.head(10))
    print("\nShape:")
    print(session_df.shape)
    print("\nTimezone breakdown:")
    print(session_df["timezone"].value_counts(dropna=False))


def main() -> None:
    events = load_event_table()

    print("Event input columns:")
    print(events.columns.tolist())

    session_df = build_session_table(events)
    export_sessions(session_df)


if __name__ == "__main__":
    main()