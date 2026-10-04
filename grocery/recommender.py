"""
Frequently Bought Together - a simple grocery recommendation engine.

Idea: if many customers buy item A and item B in the same order,
then when someone adds A to their cart, suggest B.
"""
import random
from collections import Counter
from itertools import combinations

# ---------------------------------------------------------------
# 1. SAMPLE DATA (replace make_orders() with real data if you have it)
# ---------------------------------------------------------------
PRODUCTS = [
    "Bread", "Butter", "Milk", "Eggs", "Pasta", "Pasta Sauce", "Cheese",
    "Tea", "Sugar", "Biscuits", "Chips", "Cola", "Rice", "Dal", "Oil",
    "Tomato", "Onion", "Potato", "Curd", "Coffee",
]

# Groups of items people tend to buy together
BUNDLES = [
    ("Bread", "Butter", "Milk"),
    ("Pasta", "Pasta Sauce", "Cheese"),
    ("Tea", "Sugar", "Biscuits"),
    ("Chips", "Cola"),
    ("Rice", "Dal", "Oil"),
    ("Eggs", "Bread"),
]


def make_orders(n_orders=3000, seed=42):
    """Create fake orders. Each order is a list of item names."""
    random.seed(seed)
    orders = []
    for _ in range(n_orders):
        basket = set()
        # pick 1-2 bundles, each item in a bundle is included 80% of the time
        for bundle in random.sample(BUNDLES, k=random.randint(1, 2)):
            for item in bundle:
                if random.random() < 0.8:
                    basket.add(item)
        # add 0-3 random items (noise)
        basket.update(random.sample(PRODUCTS, k=random.randint(0, 3)))
        if basket:
            orders.append(sorted(basket))
    return orders


# ---------------------------------------------------------------
# 2. COUNT HOW OFTEN ITEMS AND PAIRS APPEAR
# ---------------------------------------------------------------
class Recommender:
    def __init__(self, orders, min_pair_count=20):
        self.n_orders = len(orders)
        self.min_pair_count = min_pair_count
        self.item_count = Counter()   # how many orders contain each item
        self.pair_count = Counter()   # how many orders contain each pair

        for order in orders:
            items = sorted(set(order))
            self.item_count.update(items)
            for a, b in combinations(items, 2):
                self.pair_count[(a, b)] += 1

    # -----------------------------------------------------------
    # 3. SCORE A PAIR
    # -----------------------------------------------------------
    def _score(self, item, other):
        """Return (pair_count, confidence, lift) for item -> other."""
        key = tuple(sorted((item, other)))
        pair = self.pair_count.get(key, 0)
        # confidence: of the orders containing `item`, what share also had `other`?
        confidence = pair / self.item_count[item]
        # lift: how much more likely is `other` given `item`, vs. in general?
        # lift > 1 means a real association, not just "other is popular"
        popularity = self.item_count[other] / self.n_orders
        lift = confidence / popularity
        return pair, confidence, lift

    # -----------------------------------------------------------
    # 4. RECOMMEND FOR ONE ITEM
    # -----------------------------------------------------------
    def recommend(self, item, top_n=3):
        if item not in self.item_count:
            return []
        results = []
        for other in self.item_count:
            if other == item:
                continue
            pair, conf, lift = self._score(item, other)
            if pair >= self.min_pair_count:   # ignore rare, unreliable pairs
                results.append((other, pair, conf, lift))
        results.sort(key=lambda r: r[3], reverse=True)   # best lift first
        return results[:top_n]

    # -----------------------------------------------------------
    # 5. RECOMMEND FOR A WHOLE CART
    # -----------------------------------------------------------
    def recommend_for_cart(self, cart, top_n=3):
        scores = Counter()
        for item in cart:
            for other, _, _, lift in self.recommend(item, top_n=10):
                if other not in cart:         # don't suggest what's already in cart
                    scores[other] += lift
        return scores.most_common(top_n)


# ---------------------------------------------------------------
# 6. DEMO
# ---------------------------------------------------------------
if __name__ == "__main__":
    orders = make_orders()
    rec = Recommender(orders)
    print(f"Loaded {rec.n_orders} orders, {len(rec.item_count)} products\n")

    for item in ["Bread", "Pasta", "Tea", "Rice"]:
        print(f"Customers who bought {item} also bought:")
        for other, pair, conf, lift in rec.recommend(item):
            print(f"   {other:<12} bought together {pair:>4} times | "
                  f"confidence {conf:.0%} | lift {lift:.1f}")
        print()

    cart = ["Bread", "Pasta"]
    print(f"Cart = {cart}")
    print("Suggested:", [name for name, _ in rec.recommend_for_cart(cart)])

    # Interactive mode
    print("\nType an item name to get suggestions (or 'quit').")
    while True:
        item = input("Item: ").strip().title()
        if item.lower() == "quit":
            break
        recs = rec.recommend(item)
        if not recs:
            print("  No suggestions (unknown item or not enough data).")
        for other, pair, conf, lift in recs:
            print(f"  -> {other} (confidence {conf:.0%}, lift {lift:.1f})")
