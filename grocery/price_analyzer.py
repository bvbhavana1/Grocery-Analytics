"""
Grocery Price Trend and Anomaly Analyzer.

Reads daily product prices from a CSV, then:
  1. computes a 7-day moving average
  2. finds the overall price trend per product
  3. flags unusual price spikes/drops (anomalies)
  4. saves charts and a summary
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")            # lets it run without a display window
import matplotlib.pyplot as plt

CSV_FILE = "prices.csv"


# ---------------------------------------------------------------
# 1. CREATE SAMPLE DATA (skipped if you already have prices.csv)
#    To use real data, make a CSV with columns: date, product, price
# ---------------------------------------------------------------
def create_sample_csv(path):
    np.random.seed(7)
    dates = pd.date_range("2026-01-01", periods=180)
    base_prices = {"Tomato": 40, "Onion": 30, "Milk": 56,
                   "Rice (5kg)": 320, "Eggs (12)": 84}
    frames = []
    for product, base in base_prices.items():
        trend = np.linspace(0, base * np.random.uniform(-0.1, 0.2), len(dates))
        noise = np.random.normal(0, base * 0.02, len(dates))
        price = base + trend + noise
        # inject 3 random spikes/drops so there is something to detect
        for i in np.random.choice(len(dates), 3, replace=False):
            price[i] *= np.random.choice([0.7, 1.4])
        frames.append(pd.DataFrame({"date": dates, "product": product,
                                    "price": price.round(2)}))
    pd.concat(frames, ignore_index=True).to_csv(path, index=False)


# ---------------------------------------------------------------
# 2. LOAD AND CLEAN
# ---------------------------------------------------------------
def load_data(path):
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.dropna(subset=["price"])
    df = df.sort_values(["product", "date"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------
# 3. MOVING AVERAGE + ANOMALY DETECTION
# ---------------------------------------------------------------
def add_features(df, window=7, z_threshold=3.0):
    grouped = df.groupby("product")["price"]

    # 7-day moving average smooths out daily noise
    df["moving_avg"] = grouped.transform(lambda s: s.rolling(window, min_periods=1).mean())

    # Compare each day to the PREVIOUS 14 days (shift(1) so a spike
    # doesn't hide itself by being part of its own average)
    prev_mean = grouped.transform(lambda s: s.rolling(14).mean().shift(1))
    prev_std = grouped.transform(lambda s: s.rolling(14).std().shift(1))

    # z-score: how many standard deviations away from normal is today's price?
    df["z_score"] = (df["price"] - prev_mean) / prev_std
    df["is_anomaly"] = df["z_score"].abs() > z_threshold
    return df


# ---------------------------------------------------------------
# 4. TREND PER PRODUCT
# ---------------------------------------------------------------
def trend_summary(df):
    rows = []
    for product, g in df.groupby("product"):
        days = np.arange(len(g))
        slope = np.polyfit(days, g["price"], 1)[0]     # price change per day
        start = g["price"].head(14).mean()
        end = g["price"].tail(14).mean()
        pct = (end - start) / start * 100
        direction = "rising" if pct > 2 else "falling" if pct < -2 else "stable"
        rows.append({"product": product,
                     "start_avg": round(start, 2),
                     "end_avg": round(end, 2),
                     "change_%": round(pct, 1),
                     "slope_per_day": round(slope, 3),
                     "trend": direction})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------
# 5. CHARTS
# ---------------------------------------------------------------
def plot_products(df, out_dir="charts"):
    os.makedirs(out_dir, exist_ok=True)
    for product, g in df.groupby("product"):
        plt.figure(figsize=(10, 4))
        plt.plot(g["date"], g["price"], label="Daily price", alpha=0.6)
        plt.plot(g["date"], g["moving_avg"], label="7-day average", linewidth=2)
        bad = g[g["is_anomaly"]]
        plt.scatter(bad["date"], bad["price"], color="red", zorder=5, label="Anomaly")
        plt.title(f"{product} - price over time")
        plt.xlabel("Date")
        plt.ylabel("Price (Rs.)")
        plt.legend()
        plt.tight_layout()
        safe = product.replace(" ", "_").replace("(", "").replace(")", "")
        plt.savefig(os.path.join(out_dir, f"{safe}.png"), dpi=120)
        plt.close()


# ---------------------------------------------------------------
# 6. RUN EVERYTHING
# ---------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(CSV_FILE):
        create_sample_csv(CSV_FILE)
        print(f"Created sample data: {CSV_FILE}")

    df = load_data(CSV_FILE)
    df = add_features(df)

    print("\n=== PRICE TRENDS ===")
    print(trend_summary(df).to_string(index=False))

    anomalies = df[df["is_anomaly"]][["date", "product", "price", "z_score"]]
    print(f"\n=== ANOMALIES DETECTED: {len(anomalies)} ===")
    print(anomalies.round({"price": 2, "z_score": 2}).to_string(index=False))
    anomalies.to_csv("anomalies.csv", index=False)

    plot_products(df)
    print("\nCharts saved in the 'charts' folder. Anomalies saved to anomalies.csv")
