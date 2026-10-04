import os
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# OUTPUT FOLDER
# ============================================================

OUT = "charts_real"


# ============================================================
# TIME SLOT
# ============================================================

def slot(h):
    if 5 <= h < 12:
        return "morning"
    elif h < 17:
        return "afternoon"
    elif h < 22:
        return "evening"
    else:
        return "night"


# ============================================================
# CHART 1
# ORDERS BY HOUR
# ============================================================

def chart_orders_by_hour(baskets):

    print("Creating chart 1: Orders by hour...")

    counts = (
        baskets["order_hour_of_day"]
        .value_counts()
        .sort_index()
    )

    plt.figure(figsize=(10, 4.5))

    plt.bar(
        counts.index,
        counts.values,
        color="#2a7de1"
    )

    plt.title(
        "When do customers order?",
        fontsize=14,
        fontweight="bold"
    )

    plt.xlabel("Hour of day (0-23)")
    plt.ylabel("Number of orders")

    plt.xticks(range(24))

    plt.tight_layout()

    filename = os.path.join(
        OUT,
        "1_orders_by_hour.png"
    )

    plt.savefig(
        filename,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print("Saved:", filename)


# ============================================================
# CHART 2
# TOP PRODUCTS
# ============================================================

def chart_top_products(rec, n=15):

    print("Creating chart 2: Top products...")

    top = rec.item_count.most_common(n)

    if not top:
        print("WARNING: No products found.")
        return

    top = top[::-1]

    names = [x[0] for x in top]
    values = [x[1] for x in top]

    plt.figure(figsize=(10, 6))

    plt.barh(
        names,
        values,
        color="#2aa876"
    )

    plt.title(
        f"Top {n} most-ordered products",
        fontsize=14,
        fontweight="bold"
    )

    plt.xlabel(
        "Number of orders containing the product"
    )

    plt.tight_layout()

    filename = os.path.join(
        OUT,
        "2_top_products.png"
    )

    plt.savefig(
        filename,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print("Saved:", filename)


# ============================================================
# CHART 3
# PRODUCT RECOMMENDATIONS
# ============================================================

def chart_recommendations(rec, item, n=8):

    print(
        f"Creating recommendation chart for: {item}"
    )

    try:
        recommendations = rec.recommend(
            item,
            top_n=n
        )
    except Exception as e:
        print(
            f"WARNING: Could not generate recommendations "
            f"for '{item}': {e}"
        )
        return

    if not recommendations:

        print(
            f"WARNING: No recommendations found for '{item}'."
        )

        return

    recommendations = recommendations[::-1]

    names = [
        r[0]
        for r in recommendations
    ]

    lifts = [
        r[3]
        for r in recommendations
    ]

    # Prevent empty/invalid values
    valid = []

    for name, lift, row in zip(
        names,
        lifts,
        recommendations
    ):

        if lift is not None:

            try:
                lift = float(lift)

                if lift >= 0:
                    valid.append(
                        (name, lift, row)
                    )

            except (ValueError, TypeError):
                pass

    if not valid:

        print(
            f"WARNING: No valid recommendations "
            f"for '{item}'."
        )

        return

    names = [
        x[0]
        for x in valid
    ]

    lifts = [
        x[1]
        for x in valid
    ]

    rows = [
        x[2]
        for x in valid
    ]

    plt.figure(figsize=(10, 5.5))

    bars = plt.barh(
        names,
        lifts,
        color="#e1752a"
    )

    for bar, row in zip(bars, rows):

        bought_together = row[1]

        plt.text(
            bar.get_width() + 0.05,
            bar.get_y()
            + bar.get_height() / 2,
            f"bought together {bought_together}x",
            va="center",
            fontsize=8
        )

    plt.title(
        f'Customers who buy "{item}" also buy...',
        fontsize=14,
        fontweight="bold"
    )

    plt.xlabel(
        "Lift (higher = stronger association)"
    )

    maximum = max(lifts)

    if maximum > 0:
        plt.xlim(
            0,
            maximum * 1.3
        )

    plt.tight_layout()

    safe_item = (
        item
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    filename = os.path.join(
        OUT,
        f"3_recommendations_{safe_item}.png"
    )

    plt.savefig(
        filename,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print("Saved:", filename)


# ============================================================
# CHART 4
# PRODUCT SHARE BY TIME SLOT
# ============================================================

def chart_share_by_slot(
    baskets,
    products
):

    print(
        "Creating chart 4: Product share by time slot..."
    )

    slots = [
        "morning",
        "afternoon",
        "evening",
        "night"
    ]

    data = {}

    for product in products:

        has_product = baskets[
            "product_name"
        ].apply(
            lambda product_list:
            product in product_list
        )

        percentages = []

        for time_slot in slots:

            mask = (
                baskets["slot"]
                == time_slot
            )

            if mask.sum() == 0:

                percentage = 0

            else:

                percentage = (
                    has_product[mask].mean()
                    * 100
                )

            percentages.append(
                percentage
            )

        data[product] = percentages

    if not data:

        print(
            "WARNING: No products available "
            "for time-slot chart."
        )

        return

    df = pd.DataFrame(
        data,
        index=slots
    )

    ax = df.plot(
        kind="bar",
        figsize=(10, 5),
        rot=0
    )

    ax.set_title(
        "Share of orders containing each product, "
        "by time of day",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_ylabel(
        "% of orders in that time slot"
    )

    ax.set_xlabel(
        "Time slot"
    )

    plt.tight_layout()

    filename = os.path.join(
        OUT,
        "4_share_by_time_slot.png"
    )

    plt.savefig(
        filename,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print("Saved:", filename)


# ============================================================
# MAIN CHART GENERATION FUNCTION
# ============================================================

def make_all(
    baskets,
    rec
):

    print()
    print("=" * 60)
    print("STARTING CHART GENERATION")
    print("=" * 60)

    # Create output folder
    os.makedirs(
        OUT,
        exist_ok=True
    )

    print()
    print(
        "Charts will be saved in:"
    )

    print(
        os.path.abspath(OUT)
    )

    # --------------------------------------------------------
    # Check required columns
    # --------------------------------------------------------

    required_columns = [
        "order_hour_of_day",
        "product_name"
    ]

    for column in required_columns:

        if column not in baskets.columns:

            raise ValueError(
                f"Required column '{column}' "
                f"is missing from the dataset."
            )

    # --------------------------------------------------------
    # Add time slot
    # --------------------------------------------------------

    print()
    print("Adding time-of-day slots...")

    baskets["slot"] = (
        baskets[
            "order_hour_of_day"
        ]
        .apply(slot)
    )

    # --------------------------------------------------------
    # Chart 1
    # --------------------------------------------------------

    chart_orders_by_hour(
        baskets
    )

    # --------------------------------------------------------
    # Chart 2
    # --------------------------------------------------------

    chart_top_products(
        rec
    )

    # --------------------------------------------------------
    # Recommendation charts
    # --------------------------------------------------------

    chart_recommendations(
        rec,
        "Organic Whole Milk"
    )

    chart_recommendations(
        rec,
        "Banana"
    )

    # --------------------------------------------------------
    # Chart 4
    # --------------------------------------------------------

    top5 = [
        product
        for product, count
        in rec.item_count.most_common(5)
    ]

    print()
    print("Top 5 products:")

    for product in top5:
        print(
            " -",
            product
        )

    chart_share_by_slot(
        baskets,
        top5
    )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ALL CHARTS GENERATED SUCCESSFULLY")
    print("=" * 60)

    print()
    print(
        "Open this folder:"
    )

    print(
        os.path.abspath(OUT)
    )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("BIGBASKET / GROCERY RECOMMENDATION PROJECT")
    print("=" * 60)

    print()
    print("Loading dataset...")

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    from load_instacart import load_instacart

    baskets = load_instacart()

    print(
        "Dataset loaded successfully."
    )

    print()
    print(
        "Dataset shape:",
        baskets.shape
    )

    print()
    print(
        "Columns:"
    )

    print(
        baskets.columns.tolist()
    )

    # --------------------------------------------------------
    # Create recommender
    # --------------------------------------------------------

    print()
    print(
        "Creating recommendation model..."
    )

    from recommender import Recommender

    rec = Recommender(
        baskets[
            "product_name"
        ].tolist(),
        min_pair_count=50
    )

    print(
        "Recommendation model created."
    )

    # --------------------------------------------------------
    # Generate charts
    # --------------------------------------------------------

    make_all(
        baskets,
        rec
    )

    print()
    print("PROGRAM FINISHED.")
