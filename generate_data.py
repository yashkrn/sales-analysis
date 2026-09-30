# generate_data.py
# I did not have real shop data, so I made a sample sales dataset
# of a general store in Bihar. Some values are missing on purpose and
# some rows are duplicated, so that I can practice data cleaning.

import numpy as np
import pandas as pd

np.random.seed(42)

n_rows = 10000

# product -> (category, base price)
products = {
    "Atta 5kg":        ("Grocery", 230),
    "Rice 5kg":        ("Grocery", 320),
    "Sugar 1kg":       ("Grocery", 45),
    "Mustard Oil 1L":  ("Grocery", 155),
    "Tea 500g":        ("Grocery", 240),
    "Biscuits":        ("Snacks", 20),
    "Namkeen":         ("Snacks", 30),
    "Soap":            ("Personal Care", 38),
    "Shampoo":         ("Personal Care", 110),
    "Toothpaste":      ("Personal Care", 85),
    "Notebook":        ("Stationery", 50),
    "Pen Pack":        ("Stationery", 60),
}

cities = ["Muzaffarpur", "Patna", "Darbhanga", "Gaya", "Bhagalpur", "Hajipur"]
city_weights = [0.30, 0.25, 0.15, 0.12, 0.10, 0.08]

payments = ["Cash", "UPI", "Card"]
payment_weights = [0.45, 0.45, 0.10]

# random dates from 1 Jan 2024 to 31 Dec 2025
all_dates = pd.date_range("2024-01-01", "2025-12-31")

# more sales in festival months (Oct, Nov) and wedding season (Dec, Feb)
month_weight = {1: 1.0, 2: 1.2, 3: 1.0, 4: 0.9, 5: 0.9, 6: 0.8,
                7: 0.8, 8: 0.9, 9: 1.0, 10: 1.6, 11: 1.7, 12: 1.3}
date_weights = np.array([month_weight[d.month] for d in all_dates])
date_weights = date_weights / date_weights.sum()

dates = np.random.choice(all_dates, size=n_rows, p=date_weights)
product_names = np.random.choice(list(products.keys()), size=n_rows)

df = pd.DataFrame({
    "order_id": ["ORD" + str(i).zfill(5) for i in range(1, n_rows + 1)],
    "order_date": pd.to_datetime(dates).strftime("%Y-%m-%d"),
    "city": np.random.choice(cities, size=n_rows, p=city_weights),
    "product": product_names,
    "quantity": np.random.randint(1, 8, size=n_rows),
    "payment_mode": np.random.choice(payments, size=n_rows, p=payment_weights),
})

df["category"] = df["product"].map(lambda p: products[p][0])
# price changes a little bit (+/- 5 %) from order to order
df["unit_price"] = df["product"].map(lambda p: products[p][1])
df["unit_price"] = (df["unit_price"] * np.random.uniform(0.95, 1.05, n_rows)).round(0)

df = df[["order_id", "order_date", "city", "category", "product",
         "quantity", "unit_price", "payment_mode"]]

# ---- make the data a bit messy ----
# 1) missing payment_mode and city
df.loc[df.sample(frac=0.02, random_state=1).index, "payment_mode"] = np.nan
df.loc[df.sample(frac=0.01, random_state=2).index, "city"] = np.nan

# 2) city names typed in different ways
messy = df.sample(frac=0.03, random_state=3).index
df.loc[messy, "city"] = df.loc[messy, "city"].str.lower()
messy2 = df.sample(frac=0.02, random_state=4).index
df.loc[messy2, "city"] = " " + df.loc[messy2, "city"].astype(str) + " "

# 3) duplicate rows (same entry saved twice)
dupes = df.sample(n=250, random_state=5)
df = pd.concat([df, dupes]).sample(frac=1, random_state=6).reset_index(drop=True)

df.to_csv("data/sales_data.csv", index=False)
print("Saved data/sales_data.csv with", len(df), "rows")
