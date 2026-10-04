"""Simulated Indian grocery orders, with an optional Diwali season."""
import random

PRODUCTS = ["Atta", "Ghee", "Rice", "Toor Dal", "Oil", "Dosa Batter", "Coconut Chutney",
            "Sambar Powder", "Idli Rice", "Tea", "Sugar", "Biscuits", "Milk", "Curd",
            "Onion", "Tomato", "Paneer", "Besan", "Dry Fruits", "Jaggery", "Diya",
            "Rangoli Colours"]

NORMAL_BUNDLES = [
    ("Dosa Batter", "Coconut Chutney", "Sambar Powder"),
    ("Atta", "Ghee", "Paneer"),
    ("Rice", "Toor Dal", "Oil"),
    ("Tea", "Sugar", "Biscuits"),
    ("Milk", "Curd"),
]

# extra bundles that show up during Diwali
FESTIVAL_BUNDLES = [
    ("Besan", "Ghee", "Sugar", "Dry Fruits"),
    ("Diya", "Rangoli Colours", "Oil"),
    ("Jaggery", "Dry Fruits"),
]


def make_indian_orders(n=3000, season="normal", seed=1):
    random.seed(seed)
    bundles = NORMAL_BUNDLES + (FESTIVAL_BUNDLES * 2 if season == "diwali" else [])
    orders = []
    for _ in range(n):
        basket = set()
        for b in random.sample(bundles, k=random.randint(1, 2)):
            for item in b:
                if random.random() < 0.8:
                    basket.add(item)
        basket.update(random.sample(PRODUCTS, k=random.randint(0, 3)))
        if basket:
            orders.append(sorted(basket))
    return orders
