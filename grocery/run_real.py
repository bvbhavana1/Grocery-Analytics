from load_instacart import load_instacart
from recommender import Recommender

baskets = load_instacart()
rec = Recommender(baskets["product_name"].tolist(), min_pair_count=50)

print(rec.item_count.most_common(20))   # real product names you can test with

for item in ["Organic Whole Milk", "Banana"]:
    print(item, "->", rec.recommend(item))


# ---------- Time-of-day recommendations ----------
def slot(h):
    return "morning" if 5 <= h < 12 else "afternoon" if h < 17 else "evening" if h < 22 else "night"


baskets["slot"] = baskets["order_hour_of_day"].apply(slot)
print("\nOrders per time slot:")
print(baskets["slot"].value_counts())

recs = {s: Recommender(g["product_name"].tolist(), min_pair_count=15)
        for s, g in baskets.groupby("slot")}

for item in ["Banana", "Organic Whole Milk"]:
    print(f"\n=== {item} ===")
    for s in ["morning", "afternoon", "evening", "night"]:
        top = [name for name, *_ in recs[s].recommend(item)]
        print(f"{s:<10}", top)
