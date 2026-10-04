"""Run the price analyzer on the REAL government price data."""
import price_analyzer as pa

df = pa.add_features(pa.load_data("real_prices.csv"))

print("=== PRICE TRENDS (real data) ===")
print(pa.trend_summary(df).to_string(index=False))

anomalies = df[df["is_anomaly"]][["date", "product", "price", "z_score"]]
print(f"\n=== ANOMALIES DETECTED: {len(anomalies)} ===")
print(anomalies.round({"price": 2, "z_score": 2}).to_string(index=False))
anomalies.to_csv("real_anomalies.csv", index=False)

pa.plot_products(df, out_dir="charts_real_prices")
print("\nCharts saved in the 'charts_real_prices' folder")
