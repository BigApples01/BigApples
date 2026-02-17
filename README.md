# BigApples

This repository answers the question: **"Rank order the programs or courses based on student ratings or preferences for the one-year MAcc exit survey dataset."**

## Repository structure
- `data/` – input dataset file(s), expected as `.xlsx` (preferred) or `.csv`
- `src/` – analysis scripts (`preview.py`, `rank_order.py`)
- `outputs/` – generated ranking outputs (`rank_order.csv`, `rank_order.png`)
- `.github/workflows/` – GitHub Actions workflow for reproducible cloud execution

## Run locally
```bash
pip install -r requirements.txt
python src/preview.py
python src/rank_order.py
```

## Output location
Generated files are written to:
- `outputs/rank_order.csv`
- `outputs/rank_order.png`

## GitHub Actions
The workflow at `.github/workflows/run_analysis.yml` runs automatically on pushes to `main` and can also be run manually using **workflow_dispatch**.
