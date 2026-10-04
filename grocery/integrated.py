"""
Integration: price_analyzer.py (price intelligence) + recommender.py (co-purchase).

Flow:
  1. price_analyzer loads prices, computes moving averages, z-score anomalies, trends
  2. we turn those results into a price SIGNAL per product
  3. recommender suggests items; the price signal re-ranks them
"""
import numpy as np
import pandas as pd

import price_analyzer as pa                    # <-- your price analyzer module
from recommender import Recommender            # <-- your recommender
from indian_data import make_indian_orders, PRODUCTS

PRICE_CSV = "indian_prices.csv"


# ---------- sample prices for the same product names the recommender uses ----------
def create_prices_csv(path, days=90, seed=3):
    np.random.seed(seed)
    dates = pd.date_range("2026-07-01", periods=days)
    frames = []
    for p in PRODUCTS:
        base = np.random.randint(20, 400)
        trend = np.linspace(0, base * np.random.uniform(-0.05, 0.12), days)
        price = base + trend + np.random.normal(0, base * 0.02, days)
        price[-7:] *= np.random.choice([0.8, 1.0, 1.25])       # recent move
        frames.append(pd.DataFrame({"date": dates, "product": p, "price": price.round(2)}))
    pd.concat(frames, ignore_index=True).to_csv(path, index=False)


# ---------- turn price_analyzer output into one signal per product ----------
def build_signals(df, trends):
    trend_by_product = trends.set_index("product")
    signals = {}
    for p, g in df.groupby("product"):
        recent = g["price"].tail(7).mean()
        usual = g["price"].iloc[-37:-7].mean()
        change = (recent - usual) / usual * 100
        recent_anoms = g.tail(7)
        anomaly_dir = 0
        if recent_anoms["is_anomaly"].any():
            anomaly_dir = 1 if recent_anoms.loc[recent_anoms["is_anomaly"], "z_score"].mean() > 0 else -1
        signals[p] = {"change": change,
                      "anomaly": anomaly_dir,
                      "trend": trend_by_product.loc[p, "trend"]}
    return signals


# ---------- re-rank recommendations using the signals ----------
def smart_recommend(rec, cart, signals, top_n=5):
    results = []
    for item, score in rec.recommend_for_cart(cart, top_n=10):
        s = signals.get(item)
        new_score, notes = score, []
        if s:
            if s["change"] <= -10 or (s["anomaly"] < 0 and s["change"] <= -5):
                new_score *= 1.2
                notes.append(f"DEAL ({s['change']:+.0f}% vs usual)")
            elif s["change"] >= 15 or (s["anomaly"] > 0 and s["change"] >= 5):
                new_score *= 0.7
                notes.append(f"PRICE SPIKE ({s['change']:+.0f}% vs usual)")
            if s["trend"] == "rising":
                new_score *= 0.9
                notes.append("rising trend")
        results.append((item, round(score, 2), round(new_score, 2), "; ".join(notes)))
    results.sort(key=lambda r: r[2], reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    # 1. price intelligence (your price_analyzer functions)
    create_prices_csv(PRICE_CSV)
    df = pa.add_features(pa.load_data(PRICE_CSV))
    trends = pa.trend_summary(df)
    signals = build_signals(df, trends)

    # 2. recommender
    rec = Recommender(make_indian_orders(season="diwali"))

    # 3. combined output
    cart = ["Ghee", "Atta"]
    print(f"Cart: {cart}\n")
    print(f"{'Item':<12}{'plain':>7}{'smart':>7}   notes")
    for item, plain, smart, note in smart_recommend(rec, cart, signals):
        print(f"{item:<12}{plain:>7}{smart:>7}   {note}")
      
