from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
OUTPUT_CSV = OUTPUTS_DIR / "rank_order.csv"
OUTPUT_PNG = OUTPUTS_DIR / "rank_order.png"
MIN_N = 5
TOP_N = 20

IGNORE_COL_KEYWORDS = {
    "timestamp",
    "time stamp",
    "email",
    "e-mail",
    "name",
    "id",
    "netid",
    "uid",
    "comment",
    "feedback",
    "suggestion",
    "free text",
    "response id",
}

LIKERT_MAP = {
    "strongly disagree": 1,
    "disagree": 2,
    "somewhat disagree": 2,
    "neutral": 3,
    "neither agree nor disagree": 3,
    "somewhat agree": 4,
    "agree": 4,
    "strongly agree": 5,
    "very dissatisfied": 1,
    "dissatisfied": 2,
    "neither satisfied nor dissatisfied": 3,
    "satisfied": 4,
    "very satisfied": 5,
    "poor": 1,
    "fair": 2,
    "good": 3,
    "very good": 4,
    "excellent": 5,
    "least preferred": 1,
    "most preferred": 5,
}


@dataclass
class Dataset:
    path: Path
    frame: pd.DataFrame
    sheet_name: str | None = None


def find_dataset(data_dir: Path) -> Path:
    xlsx_files = sorted(data_dir.glob("*.xlsx"))
    if xlsx_files:
        return xlsx_files[0]

    csv_files = sorted(data_dir.glob("*.csv"))
    if csv_files:
        return csv_files[0]

    raise FileNotFoundError(f"No dataset found in {data_dir}. Expected .xlsx or .csv")


def choose_sheet(path: Path) -> str:
    xls = pd.ExcelFile(path)
    scores: list[tuple[int, str]] = []

    for sheet in xls.sheet_names:
        sheet_lower = sheet.lower()
        score = 0
        if any(k in sheet_lower for k in ["response", "survey", "exit", "data", "results"]):
            score += 5
        if any(k in sheet_lower for k in ["summary", "pivot", "chart"]):
            score -= 3

        preview = pd.read_excel(path, sheet_name=sheet, nrows=50)
        score += min(preview.shape[1], 20)
        score += min(preview.shape[0] // 5, 10)

        scores.append((score, sheet))

    scores.sort(key=lambda x: (-x[0], x[1]))
    return scores[0][1]


def load_dataset(path: Path) -> Dataset:
    if path.suffix.lower() == ".xlsx":
        sheet = choose_sheet(path)
        frame = pd.read_excel(path, sheet_name=sheet)
        return Dataset(path=path, frame=frame, sheet_name=sheet)

    frame = pd.read_csv(path)
    return Dataset(path=path, frame=frame)


def should_ignore_column(name: str) -> bool:
    lowered = name.lower().strip()
    return any(keyword in lowered for keyword in IGNORE_COL_KEYWORDS)


def normalize_text_series(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .replace({"nan": pd.NA, "none": pd.NA, "": pd.NA})
    )


def convert_series_to_numeric(series: pd.Series) -> pd.Series:
    # Try direct numeric conversion first.
    numeric = pd.to_numeric(series, errors="coerce")
    valid_ratio = numeric.notna().mean()
    if valid_ratio >= 0.5:
        return numeric

    text = normalize_text_series(series)
    mapped = text.map(LIKERT_MAP)
    mapped_ratio = mapped.notna().mean()

    # Fallback: attempt extracting leading integer (e.g., "5 - Strongly Agree")
    if mapped_ratio < 0.3:
        extracted = pd.to_numeric(text.str.extract(r"^\s*([0-9]+(?:\.[0-9]+)?)")[0], errors="coerce")
        extracted_ratio = extracted.notna().mean()
        if extracted_ratio > mapped_ratio:
            mapped = extracted

    return mapped


def is_reasonable_rating(col_numeric: pd.Series) -> bool:
    non_null = col_numeric.dropna()
    if non_null.empty:
        return False

    n_unique = non_null.nunique(dropna=True)
    if n_unique < 2:
        return False

    # Survey ratings commonly fall in a bounded range.
    if non_null.min() < 0 or non_null.max() > 10:
        return False

    return True


def build_ranking(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []

    for col in df.columns:
        if should_ignore_column(col):
            continue

        numeric = convert_series_to_numeric(df[col])
        if not is_reasonable_rating(numeric):
            continue

        n = int(numeric.notna().sum())
        if n < MIN_N:
            continue

        rows.append(
            {
                "item": str(col),
                "mean_score": float(numeric.mean()),
                "n": n,
            }
        )

    ranking = pd.DataFrame(rows)
    if ranking.empty:
        raise ValueError("No rating/preference columns were detected after cleaning and filtering.")

    ranking = ranking.sort_values(
        by=["mean_score", "n", "item"],
        ascending=[False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    ranking["rank"] = ranking.index + 1
    ranking = ranking[["item", "mean_score", "n", "rank"]]
    return ranking


def plot_ranking(ranking: pd.DataFrame, output_path: Path, top_n: int = TOP_N) -> None:
    plot_df = ranking.head(top_n).sort_values(
        by=["mean_score", "n", "item"],
        ascending=[True, True, False],
        kind="mergesort",
    )

    plt.figure(figsize=(12, max(6, len(plot_df) * 0.35)))
    plt.barh(plot_df["item"], plot_df["mean_score"], color="#2E86AB")
    plt.xlabel("Mean student rating / preference score")
    plt.ylabel("Program / Course / Survey item")
    plt.title(f"Rank Order of MAcc One-Year Exit Survey Items (Top {len(plot_df)})")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    dataset_path = find_dataset(DATA_DIR)
    dataset = load_dataset(dataset_path)

    ranking = build_ranking(dataset.frame)

    ranking.to_csv(OUTPUT_CSV, index=False)
    plot_ranking(ranking, OUTPUT_PNG)

    print(f"Dataset used: {dataset.path.name}")
    if dataset.sheet_name:
        print(f"Sheet used: {dataset.sheet_name}")
    print(f"Rows ranked: {len(ranking)}")
    print(f"Saved CSV: {OUTPUT_CSV}")
    print(f"Saved plot: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
