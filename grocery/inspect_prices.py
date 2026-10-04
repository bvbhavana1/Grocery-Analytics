import glob
import pandas as pd

# change these words if your file names are different
for path in sorted(glob.glob("*.csv")):
    if any(w in path.lower() for w in ["food", "price", "retail", "weekly", "monthly"]):
        try:
            df = pd.read_csv(path, nrows=5)
            n_rows = sum(1 for _ in open(path, encoding="utf-8", errors="ignore")) - 1
            print("=" * 70)
            print(path, "| rows:", n_rows)
            print("Columns:", list(df.columns))
            print(df.head(5).to_string())
        except Exception as e:
            print(path, "-> could not read:", e)
