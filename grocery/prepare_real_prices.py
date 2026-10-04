"""
Turn the Kaggle 'Weekly_Food_Retail_Prices.csv' into a small, clean file
(date, product, price) that price_analyzer.py can read.

For each chosen commodity we:
  1. keep only its most-reported variety (so we don't mix different varieties)
  2. average the price across all centres for each week (a national average)
"""
import re
import pandas as pd

SOURCE = "Weekly_Food_Retail_Prices.csv"
OUTPUT = "real_prices.csv"
START_YEAR = 2015          # keep data from this year onward (dataset ends around 2021)

# words to look for in the Commodity column (case-insensitive, matched at word start)
KEYWORDS = ["tomato", "onion", "potato", "rice", "sugar", "wheat", "milk",
            "tea", "arhar", "gur", "jaggery", "atta", "oil"]
pattern = re.compile(r"\b(" + "|".join(KEYWORDS) + ")", re.IGNORECASE)

kept = []
all_commodities = {}

# the file has ~5 million rows, so read it in chunks
for chunk in pd.read_csv(SOURCE, usecols=["Commodity", "Variety", "Date", "Retail Price"],
                         chunksize=500_000):
    chunk = chunk.dropna(subset=["Retail Price"])
    for name, n in chunk["Commodity"].value_counts().items():
        all_commodities[name] = all_commodities.get(name, 0) + n
    mask = chunk["Commodity"].astype(str).apply(lambda s: bool(pattern.search(s)))
    kept.append(chunk[mask])

df = pd.concat(kept, ignore_index=True)
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["Date"])
df = df[df["Date"].dt.year >= START_YEAR]

print("Commodities available in the file (with price counts):")
for name, n in sorted(all_commodities.items(), key=lambda x: -x[1]):
    print(f"   {name:<30}{n:>10}")

print("\nCommodities selected by KEYWORDS:", sorted(df["Commodity"].unique()))

# keep the most-reported variety of each commodity
best = (df.groupby(["Commodity", "Variety"]).size().reset_index(name="n")
          .sort_values("n", ascending=False).drop_duplicates("Commodity"))
df = df.merge(best[["Commodity", "Variety"]], on=["Commodity", "Variety"])

# national average per commodity per week
out = (df.groupby(["Commodity", "Date"])["Retail Price"].mean().round(2)
         .reset_index().rename(columns={"Commodity": "product", "Date": "date",
                                        "Retail Price": "price"}))
out = out[["date", "product", "price"]].sort_values(["product", "date"])
out.to_csv(OUTPUT, index=False)

print(f"\nSaved {OUTPUT}: {len(out)} rows")
print(out.groupby("product").agg(first=("date", "min"), last=("date", "max"), weeks=("price", "size")))
print("\nVarieties used:")
print(best.to_string(index=False))
