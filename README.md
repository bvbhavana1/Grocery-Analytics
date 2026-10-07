# Grocery Analytics: Recommendation Engine and Price Analysis

A Python project with two parts that can also be combined:

1. **A market-basket recommendation engine** ("customers who bought X also bought Y") built on co-purchase counts, confidence and lift, and analyzed on **100,000 real grocery orders** from the Instacart dataset.
2. **A price analyzer** (moving averages, trend fitting, z-score anomaly detection) run on **real Government of India weekly retail price data** for 10 staple foods (2015 to early 2021).

A third piece prototypes **combining the two**: re-ranking recommendations using price signals (discounts and spikes). That prototype runs on **simulated data only**. See [Data sources](#data-sources) for exactly what is real and what is simulated.

> **Honesty note:** the methods are standard techniques (market-basket analysis, rolling statistics). This is a learning and analysis project, not a production system, and the recommender has not been formally evaluated (see [Limitations](#limitations)).

---

## Table of contents
- [Data sources](#data-sources)
- [Project structure](#project-structure)
- [Setup](#setup)
- [How to run](#how-to-run)
- [How it works](#how-it-works)
- [Results](#results)
  - [Part 1: Real grocery orders (Instacart)](#part-1-real-grocery-orders-instacart)
  - [Part 2: Real Government of India retail prices](#part-2-real-government-of-india-retail-prices)
  - [Part 3: Simulated demo charts](#part-3-simulated-demo-charts-code-demonstration-only)
  - [Part 4: Price-aware prototype](#part-4-price-aware-prototype-simulated-data)
- [Limitations](#limitations)
- [Future work](#future-work)
- [Data credits](#data-credits)
- [Author](#author)

---

## Data sources

| Component | Data | Real or simulated |
|---|---|---|
| Recommender analysis on real orders | [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset) (Kaggle): anonymized US grocery orders, about 3 million. The code samples **100,000 orders** at random. | **Real** |
| Price analysis on real prices | "Retail Prices Of Commodities In India" (Kaggle): weekly and monthly retail prices of food and non-food commodities in India, 2001 to 2021, sourced from the Government of India's price monitoring system. This project uses `Weekly_Food_Retail_Prices.csv`. | **Real** |
| Recommender demo (`recommender.py`) | Fake baskets generated in code, with planted product bundles | Simulated |
| Sample price analyzer run (`price_analyzer.py` default) | 180 days of generated prices with injected spikes | Simulated |
| Indian orders and Diwali bundles (`indian_data.py`) | Generated orders with Indian grocery bundles and an optional festival season | Simulated |
| Price-aware assistant (`smart_assistant.py`, `integrated.py`) | Simulated Indian orders plus simulated prices | Simulated |

The real datasets are **not included in this repository** because of their size (the Instacart order file alone is about 560 MB). See [Setup](#setup) for how to download them.

---

## Project structure

```
Grocery-Analytics/
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
├── images/
│   ├── real_orders/          # Charts from the real Instacart analysis
│   ├── real_prices/          # Charts from the real Government of India price data
│   └── simulated_prices/     # Charts from the simulated price demo
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Setup

**Requirements:** Python 3.9 or newer.

```bash
# 1. Clone the repository
git clone https://github.com/bvbhavana1/Grocery-Analytics.git
cd Grocery-Analytics

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

Samples 100,000 real orders, builds one list of product names per order, and runs the recommender. The order hour is used to count orders per time slot (morning 05:00 to 11:59, afternoon 12:00 to 16:59, evening 17:00 to 21:59, night 22:00 to 04:59) and to chart demand by hour. The large file is read with memory-efficient integer types (`int32`, `int8`).

### 3. Price analyzer (`price_analyzer.py`)

Input is a CSV with columns `date, product, price`. For each product:

- **Moving average:** a 7-observation rolling mean that smooths short-term noise.
- **Anomaly detection:** each price is compared with the mean and standard deviation of the **previous 14 observations** (shifted by one so a spike does not hide itself). The z-score is `(price - previous mean) / previous std`; values beyond ±3 are flagged.
- **Trend:** the first-14 and last-14 observation averages give a percentage change, and a linear fit (`numpy.polyfit`) gives the slope per observation. Labels: rising (> +2%), falling (< -2%), stable.
- **Charts:** price, moving average, and anomalies marked in red, one per product.

> **Reading the chart labels:** the plotting code is shared between the simulated and real runs, so every chart's legend says "Daily price" and "7-day average". For the **simulated** charts that is correct. For the **real** price charts each point is a **weekly** national average and the moving average spans **7 weeks**.

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

### Part 1: Real grocery orders (Instacart)

All results in this part come from a random sample of **100,000 real orders**.

**Orders by time slot**

| Time slot | Orders |
|---|---|
| Afternoon (12:00 to 16:59) | 42,204 |
| Morning (05:00 to 11:59) | 33,478 |
| Evening (17:00 to 21:59) | 21,331 |
| Night (22:00 to 04:59) | 2,987 |

About 76% of sampled orders were placed in the morning or afternoon.

#### 1.1 When do customers order?

<!-- IMAGE: images/real_orders/1_orders_by_hour.png  (from your charts_real folder) -->
![image alt]()(images/real_orders/1_orders_by_hour.png)

Order volume is very low overnight (hours 0 to 5), climbs sharply from 7:00, and stays high between roughly 10:00 and 16:00 (about 7,800 to 8,400 orders per hour in the sample), then tapers through the evening.

#### 1.2 Most-ordered products

<!-- IMAGE: images/real_orders/2_top_products.png  (from your charts_real folder) -->
![image alt]()![Top 15 most-ordered products](images/real_orders/2_top_products.png)

Demand is concentrated in a few items. Banana appears in about 14,500 of the 100,000 orders and Bag of Organic Bananas in about 12,000. Fresh produce (bananas, strawberries, spinach, avocados) dominates the top 15, with Organic Whole Milk the only dairy item.

#### 1.3 Product associations: "customers who buy X also buy..."

Recommendations are ranked by **lift** with a minimum of 50 co-occurrences. The text on each bar shows how many orders contained both items, which indicates how much evidence is behind the bar.

<!-- IMAGE: images/real_orders/3_recommendations_Organic_Whole_Milk.png  (from your charts_real folder) -->
![image alt]()
![Recommendations for Organic Whole Milk](images/real_orders/3_recommendations_Organic_Whole_Milk.png)

For **Organic Whole Milk**, the strongest associations are yogurts (top lift about 6, from 120 orders containing both), followed by eggs, bread and cheese. Organic Whole String Cheese has the most co-occurrences (276 orders, lift about 3.6), so it is the best-supported suggestion even though its lift is lower than the yogurts'.

<!-- IMAGE: images/real_orders/3_recommendations_Banana.png  (from your charts_real folder) -->
![image alt]()
![Recommendations for Banana](images/real_orders/3_recommendations_Banana.png)

For **Banana**, the suggestions are other fruit (apples, pears, blueberries), plus yogurt, avocado and baby carrots, with lifts of roughly 2.7 to 3.2. Associations are weaker than for milk, because bananas are bought by many different kinds of customers.

| If the cart has | Top suggestion | Bought together | Confidence | Lift |
|---|---|---|---|---|
| Organic Whole Milk | Whole Milk Plain Yogurt | 120 orders | 2.8% | 6.1 |
| Banana | Golden Delicious Apple | 76 orders | 0.5% | 3.2 |

Confidence is low even for the strongest pairs: real baskets are hard to predict, and most customers who buy milk do not buy any one specific yogurt.

#### 1.4 Does time of day change what people buy?

<!-- IMAGE: images/real_orders/4_share_by_time_slot.png  (from your charts_real folder) -->
![image alt]()
![Share of orders containing top products by time slot](images/real_orders/4_share_by_time_slot.png)

The share of orders containing each of the top five products is **broadly similar across the four time slots** (for example, Banana appears in roughly 14 to 15% of orders in every slot), so time of day has little visible effect on these staple items. Night shows somewhat higher shares for several products, but the night slot has only about 3,000 orders, so those differences are treated as noise. Recommendations built separately for each time slot were also too unstable to report as a finding.

---

### Part 2: Real Government of India retail prices

Weekly **national average** retail prices for 10 staple commodities, January 2015 to March 2021, prepared from the Kaggle weekly file as described above. Each point on the charts below is one week; the orange line is a 7-week moving average; red dots are weeks where the price was more than 3 standard deviations from the previous 14 weeks.

**Price change, first 14 weeks (early 2015) versus last 14 weeks (early 2021), nominal prices (not adjusted for inflation):**

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

(Rupees per unit, mostly per kg; milk is per litre.)

**Overall observations**
- Onion and potato rose the most; rice, atta, gur and tea moved the least.
- **Vegetables are the most volatile.** Onion and tomato show repeated sharp surges, while staples such as rice, atta, wheat and milk move gradually.
- The detector flagged 161 anomalies, but most are **runs of consecutive weeks within a single surge**, and a few extreme single-week values (potato in 2017, tea in 2015) are probably reporting artifacts rather than real events. The anomaly count should not be read as 161 separate events.

#### 2.1 Highly volatile: vegetables

<!-- IMAGE: images/real_prices/Onion.png  (from your charts_real_prices folder) -->
![image alt]()
![Onion price over time](images/real_prices/Onion.png)

**Onion:** repeated sharp surges, with peaks in late 2015 (about 58), late 2017 (about 55), the end of 2019 (above 100) and late 2020 (about 67), each followed by a fall back toward 15 to 25. The red dots mostly sit on the rising edge of each surge.

<!-- IMAGE: images/real_prices/Tomato.png  (from your charts_real_prices folder) -->
![image alt]()
![Tomato price over time](images/real_prices/Tomato.png)

**Tomato:** a recurring seasonal pattern of surges and collapses every year, with the biggest peak in mid-2017 (about 72) and another large one in mid-2020 (about 56).

<!-- IMAGE: images/real_prices/Potato.png  (from your charts_real_prices folder) -->
![image alt]()
![Potato price over time](images/real_prices/Potato.png)

**Potato:** slower multi-month swings, a rise through 2020 to about 47 by December, then a sharp fall. The isolated one-week spike in 2017 reverts immediately and is likely a data or reporting artifact (not verified).

#### 2.2 Steady upward trends: staples and dairy

<!-- IMAGE: images/real_prices/Milk.png  (from your charts_real_prices folder) -->
![image alt]()
![Milk price over time](images/real_prices/Milk.png)

**Milk:** a steady climb from about 41 to about 52 over six years, with very little volatility. The flagged points are small deviations along the trend.

<!-- IMAGE: images/real_prices/Atta.png  (from your charts_real_prices folder) -->
![image alt]()
![Atta price over time](images/real_prices/Atta.png)

**Atta:** a gradual rise from about 26 to about 32, with a plateau in 2017 to 2018 and a peak in 2020 before easing slightly.

<!-- IMAGE: images/real_prices/Rice.png  (from your charts_real_prices folder) -->
![image alt]()
![Rice price over time](images/real_prices/Rice.png)

**Rice:** one of the most stable commodities, drifting from about 29 to about 33.5, with noise early on and a faster rise in 2020.

<!-- IMAGE: images/real_prices/Wheat.png  (from your charts_real_prices folder) -->
![image alt]()
![Wheat price over time](images/real_prices/Wheat.png)

**Wheat:** a mostly steady rise from about 23 to about 30, with a flat period in 2018 and a quicker climb through 2019 and 2020. The 2015 spike is a single week.

#### 2.3 Other patterns

<!-- IMAGE: images/real_prices/Arhar.png  (from your charts_real_prices folder) -->
![image alt]()
![Arhar price over time](images/real_prices/Arhar.png)

**Arhar (toor dal):** a boom and bust. Prices spiked to about 170 in late 2015, fell back to about 70 by 2018, then climbed again to about 105 to 110 by 2020 to 2021. A start-versus-end comparison (+24%) hides this shape.

<!-- IMAGE: images/real_prices/Gur.png  (from your charts_real_prices folder) -->
![image alt]()
![Gur price over time](images/real_prices/Gur.png)

**Gur (jaggery):** moderate swings around 45 to 55, with a pronounced spike to about 60 in mid-2016 and another rise in 2020.

<!-- IMAGE: images/real_prices/Tea.png  (from your charts_real_prices folder) -->
![image alt]()
![Tea price over time](images/real_prices/Tea.png)

**Tea:** noisy in 2015, then flat around 95 to 105 from 2017, rising again to about 110 by 2021. The 2015 spike to about 159 lasts only a couple of weeks and may be a reporting artifact. The series is for a single brand (Brooke Bond Red Label), so it reflects that brand's reported price.

---

### Part 3: Simulated demo charts (code demonstration only)

These charts come from the default run of `price_analyzer.py`, which **generates 180 days of artificial prices** with random noise, a gentle trend and **spikes injected by the code itself**. They show that the anomaly detector works (the red dots land on the injected spikes), but they say nothing about real prices.

<!-- IMAGES: images/simulated_prices/  (from your charts folder: Eggs_12, Milk, Onion, Rice_5kg, Tomato) -->

| | |
|---|---|
![image alt]()| ![Eggs (simulated)](images/simulated_prices/Eggs_12.png) | ![Milk (simulated)](images/simulated_prices/Milk.png) |
![image alt]()| ![Onion (simulated)](images/simulated_prices/Onion.png) | ![Rice 5kg (simulated)](images/simulated_prices/Rice_5kg.png) |
![image alt]()| ![Tomato (simulated)](images/simulated_prices/Tomato.png) | |

---

### Part 4: Price-aware prototype (simulated data)

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
- **Time-of-day differences were too small or noisy to report.** Slices (especially night, about 3,000 orders) are small.
- **Price data caveats:** values are nominal; weekly figures are averages over whichever centres reported that week, so changes in reporting coverage can create artificial jumps; one variety per commodity is used (for example Tea is a single brand); the dataset ends around early 2021. Four cooking oils matched the keyword search but did not appear in the final file.
- **Anomaly detection is simple.** A sustained climb keeps triggering flags, so flagged points should be read as episodes, not independent events.
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
- Retail Prices Of Commodities In India, via Kaggle; underlying source: the Government of India's retail price monitoring system.

Please check each dataset's page for its license terms before reusing the data.

---

## Author

**Bhavana B V**: ECE undergraduate, RV Institute of Technology and Management, Bengaluru
[LinkedIn](https://linkedin.com/in/bhavanabv) | [GitHub](https://github.com/bvbhavana1) | bvbhavana52@gmail.com
