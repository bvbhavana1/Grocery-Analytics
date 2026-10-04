"""
Smart Grocery Assistant = recommender + price signals.
Recommends items bought together, then boosts items that are on a deal
and demotes items whose price just spiked.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from indian_data import make_indian_orders, PRODUCTS
from recommender import Recommender


# 1. Simulated daily prices for each product (last 7 days may move up/down)
def make_prices(days=60, seed=3):
    np.random.seed(seed)
    dates = pd.date_range("2026-08-01", periods=days)
    rows = []
    for p in PRODUCTS:
        base = np.random.randint(20, 400)
        price = base + np.random.normal(0, base * 0.02, days)
        price[-7:] *= np.random.choice([0.8, 1.0, 1.25])
        rows.append(pd.DataFrame({"date": dates, "product": p, "price": price}))
    return pd.concat(rows, ignore_index=True)


# 2. % change: average of last 7 days vs the 30 days before that
def price_signals(df):
    signals = {}
    for p, g in df.groupby("product"):
        recent = g["price"].tail(7).mean()
        usual = g["price"].iloc[-37:-7].mean()
        signals[p] = (recent - usual) / usual * 100
    return signals


# 3. Recommend, then adjust scores using price signals
def smart_recommend(rec, cart, signals, top_n=5):
    results = []
    for item, score in rec.recommend_for_cart(cart, top_n=10):
        change = signals.get(item, 0)
        new_score, note = score, ""
        if change <= -10:                       # price dropped 10%+ -> boost
            new_score = score * 1.2
            note = f"DEAL: {abs(change):.0f}% cheaper than usual"
        elif change >= 15:                      # price jumped 15%+ -> demote
            new_score = score * 0.7
            note = f"PRICE SPIKE: +{change:.0f}%"
        results.append({"item": item, "plain_score": score,
                        "smart_score": new_score, "note": note, "change": change})
    results.sort(key=lambda r: r["smart_score"], reverse=True)
    return results[:top_n]


# 4. Chart: plain vs price-aware scores
def plot_results(results, cart, path="smart_recommendations.png"):
    results = results[::-1]
    names = [r["item"] for r in results]
    y = np.arange(len(names))
    plt.figure(figsize=(10, 5.5))
    plt.barh(y + 0.2, [r["plain_score"] for r in results], height=0.4,
             label="Co-purchase score only", color="#9aa5b1")
    plt.barh(y - 0.2, [r["smart_score"] for r in results], height=0.4,
             label="After price adjustment", color="#2a7de1")
    for i, r in enumerate(results):
        if r["note"]:
            plt.text(max(r["plain_score"], r["smart_score"]) + 0.05, i, r["note"],
                     va="center", fontsize=8)
    plt.yticks(y, names)
    plt.xlabel("Recommendation score")
    plt.title(f"Smart recommendations for cart: {', '.join(cart)}")
    plt.legend()
    plt.xlim(0, max(max(r["plain_score"], r["smart_score"]) for r in results) * 1.5)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


if __name__ == "__main__":
    rec = Recommender(make_indian_orders(season="diwali"))
    signals = price_signals(make_prices())
    cart = ["Ghee", "Atta"]

    results = smart_recommend(rec, cart, signals)
    print(f"Cart: {cart}\n")
    for r in results:
        print(f"{r['item']:<16} plain {r['plain_score']:.2f} -> smart {r['smart_score']:.2f}   {r['note']}")

    plot_results(results, cart)
    print("\nChart saved: smart_recommendations.png")
