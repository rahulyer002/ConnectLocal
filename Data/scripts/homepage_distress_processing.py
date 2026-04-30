from __future__ import annotations

from pathlib import Path
import re
import json
import pandas as pd
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE = RAW_DIR / "psychological_distress_au.xls"

OUTPUT_CSV = PROCESSED_DIR / "homepage_distress_by_age.csv"
OUTPUT_JSON = PROCESSED_DIR / "homepage_distress_by_age.json"
OUTPUT_HTML = PROCESSED_DIR / "homepage_distress_visual.html"


AGE_PATTERN = re.compile(
    r"^(15[-–]24|25[-–]34|35[-–]44|45[-–]54|55[-–]64|65[-–]74|75[-–]84|85\s*(years\s*)?(and\s*)?over|85\+)$",
    re.IGNORECASE
)


def load_workbook_sheets() -> dict[str, pd.DataFrame]:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Missing file: {RAW_FILE}. Place psychological_distress_au.xls in Data/raw/"
        )

    return pd.read_excel(RAW_FILE, sheet_name=None, header=None)


def normalise_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def find_relevant_sheet(sheets: dict[str, pd.DataFrame]) -> tuple[str, pd.DataFrame]:
    best_sheet_name = None
    best_score = -1

    for sheet_name, df in sheets.items():
        text_blob = " ".join(
            normalise_text(x).lower()
            for x in df.values.flatten()
            if normalise_text(x)
        )

        score = 0

        if "psychological distress" in text_blob:
            score += 5
        if "high or very high" in text_blob:
            score += 5
        if "age" in text_blob:
            score += 2
        if "persons" in text_blob:
            score += 2

        if score > best_score:
            best_score = score
            best_sheet_name = sheet_name

    if best_sheet_name is None:
        raise ValueError("Could not identify a relevant psychological distress sheet.")

    return best_sheet_name, sheets[best_sheet_name]


def find_age_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for i in range(len(df)):
        row_values = [normalise_text(x) for x in df.iloc[i].tolist()]

        for col_idx, value in enumerate(row_values):
            clean_value = value.replace(" years", "").replace("yrs", "").strip()

            if AGE_PATTERN.match(clean_value):
                rows.append((i, col_idx, clean_value))

    if not rows:
        raise ValueError(
            "Could not find age-group rows. Open the spreadsheet and check how age groups are labelled."
        )

    return pd.DataFrame(rows, columns=["row_index", "age_col", "age_group"])


def find_best_value_column(df: pd.DataFrame, age_rows: pd.DataFrame) -> int:
    candidate_cols = []

    for col in range(df.shape[1]):
        values = pd.to_numeric(
            df.iloc[age_rows["row_index"], col],
            errors="coerce"
        )

        valid_count = values.notna().sum()

        if valid_count >= 3:
            median_value = values.dropna().median()

            if 0 <= median_value <= 100:
                candidate_cols.append((col, valid_count, median_value))

    if not candidate_cols:
        raise ValueError("Could not identify the percentage value column.")

    candidate_cols = sorted(candidate_cols, key=lambda x: (-x[1], x[0]))

    return candidate_cols[0][0]


def clean_homepage_distress_data(_: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, sheet_name="Table 7.3_Proportions", header=None)

    age_groups = df.iloc[6, 1:7].tolist()
    distress_values = df.iloc[13, 1:7].tolist()

    output = pd.DataFrame({
        "age_group": age_groups,
        "psychological_distress_percent": distress_values
    })

    output["age_group"] = (
        output["age_group"]
        .astype(str)
        .str.replace(" years and over", "+", regex=False)
        .str.replace("–", "-", regex=False)
        .str.replace("\n", " ", regex=False)
        .str.strip()
    )

    output["psychological_distress_percent"] = (
        pd.to_numeric(output["psychological_distress_percent"], errors="coerce")
        .round(1)
    )

    output["year"] = "2017-18"
    output["source"] = "ABS National Health Survey, Psychological distress - Australia"

    return output


def export_processed_data(df: pd.DataFrame) -> None:
    df.to_csv(OUTPUT_CSV, index=False)

    records = df.to_dict(orient="records")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"\nSaved CSV to: {OUTPUT_CSV}")
    print(f"Saved JSON to: {OUTPUT_JSON}")
    print("\nPreview:")
    print(df)


def create_interactive_visual(df: pd.DataFrame) -> None:
    fig = px.bar(
        df,
        x="age_group",
        y="psychological_distress_percent",
        text="psychological_distress_percent",
        title="You are not alone: psychological distress by age group",
        labels={
            "age_group": "Age group",
            "psychological_distress_percent": "People experiencing high or very high psychological distress (%)"
        },
        hover_data={
            "age_group": True,
            "psychological_distress_percent": ":.1f",
            "year": True,
            "source": True
        }
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_range=[0, max(df["psychological_distress_percent"]) + 10],
        title={
            "text": "You are not alone: psychological distress by age group",
            "x": 0.5
        },
        template="plotly_white"
    )

    fig.write_html(OUTPUT_HTML)

    print(f"Saved interactive visualisation to: {OUTPUT_HTML}")


def main() -> None:
    sheets = load_workbook_sheets()

    sheet_name, raw_df = find_relevant_sheet(sheets)

    print(f"Using sheet: {sheet_name}")
    print(f"Raw sheet shape: {raw_df.shape}")

    cleaned_df = clean_homepage_distress_data(raw_df)

    export_processed_data(cleaned_df)
    create_interactive_visual(cleaned_df)


if __name__ == "__main__":
    main()