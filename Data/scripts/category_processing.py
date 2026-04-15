from __future__ import annotations

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_landmarks() -> pd.DataFrame:
    path = PROCESSED_DIR / "landmarks.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing landmarks file: {path}. Run landmarks_processing.py first."
        )
    return pd.read_csv(path)


def load_open_space() -> pd.DataFrame:
    path = PROCESSED_DIR / "open_space.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing open_space file: {path}. Run open_space_processing.py first."
        )
    return pd.read_csv(path)


def is_senior_friendly(name: str) -> bool:
    text = str(name).lower()

    keywords = [
        "park",
        "garden",
        "reserve",
        "recreation",
        "leisure",
        "green space",
        "urban space",
        "open space",
        "community",
        "club",
        "square",
    ]

    return any(keyword in text for keyword in keywords)


def build_category_table(
    landmarks: pd.DataFrame,
    open_space: pd.DataFrame
) -> pd.DataFrame:
    parent_names = set()
    child_pairs: set[tuple[str, str]] = set()

    # LANDMARK hierarchy: theme -> sub_theme
    if "theme" in landmarks.columns:
        parent_names.update(
            landmarks["theme"].dropna().astype(str).str.strip().tolist()
        )

    if {"theme", "sub_theme"}.issubset(landmarks.columns):
        landmark_pairs = (
            landmarks[["theme", "sub_theme"]]
            .dropna()
            .astype(str)
            .apply(lambda col: col.str.strip())
        )

        for _, row in landmark_pairs.iterrows():
            if row["theme"] and row["sub_theme"]:
                child_pairs.add((row["theme"], row["sub_theme"]))

    # OPEN_SPACE hierarchy: space_type -> category
    if "space_type" in open_space.columns:
        parent_names.update(
            open_space["space_type"].dropna().astype(str).str.strip().tolist()
        )

    if {"space_type", "category"}.issubset(open_space.columns):
        open_space_pairs = (
            open_space[["space_type", "category"]]
            .dropna()
            .astype(str)
            .apply(lambda col: col.str.strip())
        )

        for _, row in open_space_pairs.iterrows():
            if row["space_type"] and row["category"]:
                child_pairs.add((row["space_type"], row["category"]))

    # Build parent rows first
    parent_names = sorted(name for name in parent_names if name)

    category_rows = []
    category_id = 1
    parent_lookup: dict[str, int] = {}

    for name in parent_names:
        parent_lookup[name] = category_id
        category_rows.append({
            "category_id": category_id,
            "parent_id": None,
            "name": name,
            "senior_tag": is_senior_friendly(name)
        })
        category_id += 1

    # Build child rows
    child_pairs = sorted(
        (parent, child)
        for parent, child in child_pairs
        if parent and child and child != parent
    )

    seen_children = set()

    for parent_name, child_name in child_pairs:
        if child_name in seen_children:
            continue
        if parent_name not in parent_lookup:
            continue

        category_rows.append({
            "category_id": category_id,
            "parent_id": parent_lookup[parent_name],
            "name": child_name,
            "senior_tag": is_senior_friendly(child_name)
        })
        seen_children.add(child_name)
        category_id += 1

    category_df = pd.DataFrame(category_rows)

    return category_df


def export_category(category_df: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / "category.csv"
    category_df.to_csv(output_path, index=False)

    print(f"\nSaved category file to: {output_path}")
    print("\nPreview:")
    print(category_df.head(10))
    print("\nShape:")
    print(category_df.shape)
    print("\nSenior tag summary:")
    print(category_df["senior_tag"].value_counts(dropna=False))
    print(category_df[category_df["parent_id"].notna()].head())


def main() -> None:
    landmarks = load_landmarks()
    open_space = load_open_space()

    category_df = build_category_table(landmarks, open_space)
    export_category(category_df)



if __name__ == "__main__":
    main()