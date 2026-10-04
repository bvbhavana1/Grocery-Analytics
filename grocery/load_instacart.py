import pandas as pd

def load_instacart(folder=".", n_orders=100_000, seed=42):
    products = pd.read_csv(f"{folder}/products.csv", usecols=["product_id", "product_name"])
    op = pd.read_csv(f"{folder}/order_products__prior.csv",
                     usecols=["order_id", "product_id"],
                     dtype={"order_id": "int32", "product_id": "int32"})
    orders = pd.read_csv(f"{folder}/orders.csv",
                         usecols=["order_id", "order_hour_of_day"],
                         dtype={"order_id": "int32", "order_hour_of_day": "int8"})

    # random sample of orders
    keep = op["order_id"].drop_duplicates().sample(n_orders, random_state=seed)
    op = op[op["order_id"].isin(keep)].merge(products, on="product_id")

    # one list of product names per order
    baskets = op.groupby("order_id")["product_name"].apply(list).reset_index()
    baskets = baskets.merge(orders, on="order_id")
    return baskets
