# Grocery Analytics: Recommendation Engine and Price Analysis

A Python project with two parts that can also be combined:

1. **A market-basket recommendation engine** ("customers who bought X also bought Y") built on co-purchase counts, confidence and lift, and analyzed on **100,000 real grocery orders** from the Instacart dataset.
2. **A price analyzer** (moving averages, trend fitting, z-score anomaly detection) run on **real Government of India weekly retail price data** for 10 staple foods (2015 to early 2021).

A third piece prototypes **combining the two**: re-ranking recommendations using price signals (discounts and spikes). That prototype runs on **simulated data only**. See [Data sources](#data-sources) for exactly what is real and what is simulated.

> **Honesty note:** the methods are standard techniques (market-basket analysis, rolling statistics). The project is a learning and analysis exercise, not a production system, and the recommender has not been formally evaluated (see [Limitations](#limitations)).

---

## Table of contents
- [Data sources](#data-sources)
- [Project structure](#project-structure)
- [Setup](#setup)
- [How to run](#how-to-run)
- [How it works](#how-it-works)
- [Results](#results)
- [Limitations](#limitations)
- [Future work](#future-work)
- [Author](#author)

---

## Data sources

| Component | Data | Real or simulated |
|---|---|---|
| Recommender analysis on real orders | [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset) (Kaggle): anonymized US grocery orders, about 3 million. The code samples **100,000 orders** at random. | **Real** |
| Price analysis on real prices | [Retail Prices Of Commodities In India](https://www.kaggle.com/) (Kaggle): weekly and monthly retail prices of food and non-food commodities in India, 2001 to 2021, sourced from the Government of India's Wholesale and Retail Price Information System. This project uses `Weekly_Food_Retail_Prices.csv`. | **Real** |
| Recommender demo (`recommender.py`) | Fake baskets generated in code, with planted product bundles | Simulated |
| Sample price analyzer (`price_analyzer.py` default run) | 180 days of generated prices with injected spikes | Simulated |
| Indian orders and Diwali bundles (`indian_data.py`) | Generated orders with Indian grocery bundles and an optional festival season | Simulated |
| Price-aware assistant (`smart_assistant.py`, `integrated.py`) | Simulated Indian orders plus simulated prices | Simulated |

The real datasets are **not included in this repository** because of their size (the Instacart order file alone is about 560 MB). See [Setup](#setup) for how to download them.

---

## Project structure

```
grocery-analytics/
├── recommender.py            # Core recommender: co-purchase counts, confidence, lift
├── load_instacart.py         # Loads and samples the real Instacart orders
├── run_real.py               # Runs the recommender on real orders (+ time-of-day slices)
├── make_plots.py             # Charts from the real Instacart analysis
│
├── price_analyzer.py         # Moving average, trend and z-score anomaly detection
├── prepare_real_prices.py    # Converts the Kaggle weekly price file to date,product,price
├── analyze_real_prices.py    # Runs the price analyzer on the real prices
├── inspect_prices.py         # Helper: prints columns and first rows of CSV files
│
├── indian_data.py            # Simulated Indian grocery orders (normal and Diwali)
├── smart_assistant.py        # Simulated demo: recommendations re-ranked by price signals
├── integrated.py             # Same idea, wired to price_analyzer.py and recommender.py
│
├── images/                   # Chart screenshots used in this README
├── requirements.txt
└── README.md
```

---

## Setup

**Requirements:** Python 3.9 or newer.

```bash
# 1. Clone the repository
git clone https://github.com/bvbhavana1/grocery-analytics.git
cd grocery-analytics

# 2. Install dependencies
pip install -r requirements.txt
```

`requirements.txt`:
```
pandas
numpy
matplotlib
```

### Download the real datasets (only needed for the real-data parts)

1. **Instacart:** download the dataset from Kaggle, unzip it, and place `orders.csv`, `order_products__prior.csv` and `products.csv` in the project folder.
2. **Indian retail prices:** download "Retail Prices Of Commodities In India" from Kaggle, unzip it, and place `Weekly_Food_Retail_Prices.csv` in the project folder.

> Do not double-click these CSV files on Windows (they open in Excel and hang on the large ones). Python reads them directly. They are excluded from git by `.gitignore`.

---

## How to run

### A. Recommender on simulated data (no downloads needed)
```bash
python recommender.py
```
Prints recommendations for sample items, a cart-level suggestion, and then an interactive prompt (type an item name, or `quit`).

### B. Recommender on real Instacart orders
```bash
python run_real.py        # prints top products and recommendations, plus time-of-day slices
python make_plots.py      # saves four charts to charts_real/
```
Loading takes one to two minutes because `order_products__prior.csv` is large.

### C. Price analyzer on simulated prices (no downloads needed)
```bash
python price_analyzer.py
```
Creates `prices.csv`, prints trends and anomalies, and saves one chart per product to `charts/`.

### D. Price analyzer on real Government of India prices
```bash
python prepare_real_prices.py     # builds real_prices.csv (takes a minute or two)
python analyze_real_prices.py     # trends, anomalies, charts in charts_real_prices/
```

### E. Price-aware recommendations (simulated prototype)
```bash
python smart_assistant.py         # prints re-ranked recommendations, saves a chart
python integrated.py              # same idea, using price_analyzer.py and recommender.py
```

---

## How it works

### 1. Recommendation engine (`recommender.py`)

For every order, the code counts how often each item appears and how often each **pair** of items appears together (using `itertools.combinations`). Two scores are then computed for "item A leads to item B":

- **Confidence** = (orders containing both A and B) / (orders containing A). It answers: of the customers who bought A, what share also bought B?
- **Lift** = confidence / (share of all orders containing B). A lift of 1 means no relationship; above 1 means B is more likely in baskets with A than in a random basket. Lift corrects for B simply being popular.

Recommendations are ranked by lift. A **minimum pair count** filter (for example 50 co-occurrences on the real data) ignores rare pairs whose lift would be unreliable. `recommend_for_cart()` adds up scores across all items in a cart and excludes items already in it.

### 2. Real-data analysis (`load_instacart.py`, `run_real.py`, `make_plots.py`)

Samples 100,000 real orders, builds one list of product names per order, and runs the recommender. The order hour is used to count orders per time slot and to chart demand by hour.

### 3. Price analyzer (`price_analyzer.py`)

Input is a CSV with columns `date, product, price`. For each product:

- **Moving average:** a 7-observation rolling mean that smooths short-term noise.
- **Anomaly detection:** each price is compared with the mean and standard deviation of the **previous 14 observations** (shifted by one so a spike does not hide itself). The z-score is `(price - previous mean) / previous std`; values beyond ±3 are flagged.
- **Trend:** the first-14 and last-14 observation averages give a percentage change, and a linear fit (`numpy.polyfit`) gives the slope per observation. Labels: rising (> +2%), falling (< -2%), stable.
- **Charts:** price, moving average, and anomalies marked in red, one per product.

### 4. Real price preparation (`prepare_real_prices.py`)

The Kaggle weekly file has about 5 million rows (state, centre, commodity, variety, date, price) with many empty prices. The script reads it in chunks, selects staple commodities by keyword, keeps the **most-reported variety** of each (so different varieties are not mixed), keeps data from 2015 onward, and averages across centres to one national price per commodity per week.

### 5. Price-aware recommendations (`smart_assistant.py`, `integrated.py`)

Prototype only. The price analysis produces a **signal per product** (recent change versus the previous 30 observations, anomaly direction, long-term trend). The recommender's scores are then adjusted:

| Signal | Adjustment |
|---|---|
| Price dropped 10% or more | score x 1.2 (labelled DEAL) |
| Price rose 15% or more | score x 0.7 (labelled PRICE SPIKE) |
| Long-term rising trend (`integrated.py`) | score x 0.9 |

These thresholds and multipliers are **design choices, not tuned values**.

---

## Results

### Real Instacart orders (100,000-order sample)

**Orders by time of day**

| Time slot | Orders |
|---|---|
| Afternoon (12:00 to 16:59) | 42,204 |
| Morning (05:00 to 11:59) | 33,478 |
| Evening (17:00 to 21:59) | 21,331 |
| Night (22:00 to 04:59) | 2,987 |

About 76% of sampled orders were placed in the morning or afternoon.

**Most-ordered products:** Banana (14,469 orders), Bag of Organic Bananas (12,050), Organic Strawberries (8,292), Organic Baby Spinach (7,455), Organic Hass Avocado (6,681). Fresh produce dominates.

**Example associations** (minimum pair count 50)

| If the cart has | Top suggestion | Bought together | Confidence | Lift |
|---|---|---|---|---|
| Organic Whole Milk | Whole Milk Plain Yogurt | 120 orders | 2.8% | 6.1 |
| Banana | Golden Delicious Apple | 76 orders | 0.5% | 3.2 |

The associations are sensible (milk with yogurt, banana with other fruit). Confidence is low even for the strongest pairs: real baskets are hard to predict, and most customers who buy milk do not buy any one specific yogurt.

![Orders by hour](images/1_orders_by_hour.png)
![Recommendations for Organic Whole Milk](images/3_recommendations_Organic_Whole_Milk.png)

### Real Government of India retail prices (weekly national averages, Jan 2015 to Mar 2021)

Change is the average of the first 14 weeks versus the last 14 weeks, in nominal prices (not adjusted for inflation).

| Commodity | Early 2015 avg | Early 2021 avg | Change |
|---|---|---|---|
| Onion | 25.94 | 44.77 | +72.6% |
| Potato | 17.42 | 26.80 | +53.8% |
| Tomato | 21.26 | 27.76 | +30.6% |
| Wheat | 23.77 | 29.52 | +24.2% |
| Arhar (toor dal) | 84.48 | 104.82 | +24.1% |
| Milk | 42.03 | 51.96 | +23.6% |
| Atta | 26.84 | 30.77 | +14.6% |
| Gur (jaggery) | 44.37 | 50.70 | +14.3% |
| Rice | 29.24 | 33.15 | +13.4% |
| Tea | 108.36 | 108.22 | -0.1% |

(Prices in rupees per unit, mostly per kg; milk is per litre.)

**Observations**
- Onion and potato rose the most; rice, atta, gur and tea moved the least.
- Vegetables were the most volatile, with repeated sharp surges (onion in 2015, 2019 and 2020; tomato in mid-2017 and mid-2020). Staples like rice and atta moved gradually.
- Arhar spiked in late 2015, fell by 2018, then climbed again, so a simple "rising" label from start versus end hides its shape.
- The detector flagged 161 anomalies, but most are runs of consecutive weeks from a single surge, and a few extreme single-week values (for example tea and potato) are probably reporting artifacts. The anomaly count should not be read as 161 separate events.

![Onion price chart](images/Onion.png)

### Price-aware prototype (simulated data)

Example output for a cart of Ghee and Atta in the simulated Diwali season:

```
Item          plain  smart   notes
Paneer         5.12   5.12
Besan          1.99   2.39   DEAL (-21% vs usual)
```

Besan moves up because its simulated price dropped. This demonstrates the mechanism only; it says nothing about real customers or prices.

---

## Limitations

- **The recommender is not evaluated.** No hit rate, precision or recall has been measured, so there is no evidence yet that lift ranking beats confidence ranking or a plain "most popular" baseline.
- **Lift favours niche items.** The top suggestions can be rare products; the minimum pair count only partly offsets this.
- **Simulated components** (demo orders, sample prices, Indian orders, Diwali bundles, price-aware assistant) show that the code works, not real-world behaviour. The price-aware re-ranking is untested for whether it improves anything.
- **Real prices and real orders are not joined.** The Instacart data has no prices, and there is no real Indian order data, so the price-aware assistant cannot run on real data.
- **Time-of-day recommendation differences were too noisy to report.** Slices (especially night, about 3,000 orders) are small.
- **Price data caveats:** values are nominal; weekly figures are averages over whichever centres reported that week, so changes in reporting coverage can create artificial jumps; one variety per commodity is used (for example Tea is a single brand); the dataset ends around early 2021.
- **Instacart is US data** (product names such as "Bag of Organic Bananas"), so patterns may not transfer to Indian shoppers.

---

## Future work

- Add an **evaluation**: hold out one item per test order and measure hit@k for lift, confidence and a popularity baseline.
- Use the **median** across centres and skip weeks with few reporting centres to make weekly prices more robust.
- Count consecutive anomaly flags as **single episodes** and rank commodities by volatility.
- Connect real prices to the recommender for products present in both datasets.
- Add a simple Streamlit interface (cart input, suggestions, price chart).

---

## Data credits

- Instacart Online Grocery Shopping Dataset, via Kaggle.
- Retail Prices Of Commodities In India, via Kaggle; underlying source: Wholesale and Retail Price Information System, Directorate of Economics and Statistics, Government of India.

Please check each dataset's page for its license terms before reusing the data.

---

## Author

**Bhavana B V**: ECE undergraduate, RV Institute of Technology and Management, Bengaluru
[LinkedIn](https://linkedin.com/in/bhavanabv) | [GitHub](https://github.com/bvbhavana1) | bvbhavana52@gmail.com
