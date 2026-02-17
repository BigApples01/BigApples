from __future__ import annotations

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def find_dataset(data_dir: Path) -> Path:
    xlsx_files = sorted(data_dir.glob("*.xlsx"))
    if xlsx_files:
        return xlsx_files[0]
    csv_files = sorted(data_dir.glob("*.csv"))
    if csv_files:
        return csv_files[0]
    raise FileNotFoundError(f"No .xlsx or .csv files found in {data_dir}")


def main() -> None:
    dataset_path = find_dataset(DATA_DIR)
    print(f"Dataset filename used: {dataset_path.name}")

    if dataset_path.suffix.lower() == ".xlsx":
        xls = pd.ExcelFile(dataset_path)
        print("Sheet names:", list(xls.sheet_names))
        df = pd.read_excel(dataset_path, sheet_name=xls.sheet_names[0])
    else:
        print("Sheet names: n/a (csv)")
        df = pd.read_csv(dataset_path)

    print("Column names:")
    for col in df.columns:
        print(f"- {col}")

    print("\nFirst 5 rows:")
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
