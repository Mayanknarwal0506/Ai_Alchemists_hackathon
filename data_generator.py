import numpy as np
import pandas as pd
import os, math, random

np.random.seed(42)
random.seed(42)

# =========================
# Parameters
# =========================
N_CUSTOMERS = 250
N_TRANSACTIONS = 50000
N_PRODUCTS = 250
N_STORES = 50

start_date = pd.Timestamp("2025-08-01")
end_date = pd.Timestamp("2025-12-31")  # 5 months

out_dir = "synthetic_retail"
os.makedirs(out_dir, exist_ok=True)

# =========================
# 1) CUSTOMERS TABLE
# =========================
customer_ids = [f"C{str(i).zfill(5)}" for i in range(1, N_CUSTOMERS + 1)]

regions = ["North", "South", "East", "West", "Central"]
cities_by_region = {
    "North": ["Northville", "Winterton", "Frostford"],
    "South": ["Southport", "Sunvale", "Baytown"],
    "East": ["Easton", "Rivermouth", "Lakeview"],
    "West": ["Westhaven", "Hillcrest", "Oakridge"],
    "Central": ["Centrum", "Midtown", "Grandview"],
}

loyalty_tiers = ["Bronze", "Silver", "Gold", "Platinum"]
tier_probs = [0.45, 0.30, 0.18, 0.07]

gender = ["F", "M", "O"]
gender_probs = [0.49, 0.49, 0.02]

ages = np.clip(np.random.normal(35, 12, N_CUSTOMERS).round().astype(int), 18, 75)
join_dates = start_date - pd.to_timedelta(np.random.randint(30, 730, N_CUSTOMERS), unit="D")

cust_regions = np.random.choice(regions, size=N_CUSTOMERS, p=[0.22, 0.20, 0.20, 0.18, 0.20])
cust_cities = [np.random.choice(cities_by_region[r]) for r in cust_regions]
cust_tiers = np.random.choice(loyalty_tiers, size=N_CUSTOMERS, p=tier_probs)
cust_gender = np.random.choice(gender, size=N_CUSTOMERS, p=gender_probs)

channels = ["InStore", "Online", "Mobile"]
channel_probs_by_tier = {
    "Bronze": [0.62, 0.25, 0.13],
    "Silver": [0.58, 0.28, 0.14],
    "Gold": [0.52, 0.32, 0.16],
    "Platinum": [0.45, 0.38, 0.17],
}
pref_channel = [np.random.choice(channels, p=channel_probs_by_tier[t]) for t in cust_tiers]

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "gender": cust_gender,
    "age": ages,
    "join_date": join_dates,
    "loyalty_tier": cust_tiers,
    "region": cust_regions,
    "city": cust_cities,
    "preferred_channel": pref_channel,
})

tier_freq_mult = {"Bronze": 0.85, "Silver": 1.00, "Gold": 1.15, "Platinum": 1.30}

# =========================
# 2) STORES TABLE
# =========================
store_ids = [f"S{str(i).zfill(3)}" for i in range(1, N_STORES + 1)]

store_types = ["Mall", "Street", "Outlet", "OnlineHub"]
store_type_probs = [0.38, 0.32, 0.20, 0.10]

store_regions = np.random.choice(regions, size=N_STORES, p=[0.22, 0.20, 0.20, 0.18, 0.20])
store_cities = [np.random.choice(cities_by_region[r]) for r in store_regions]
opening_dates = start_date - pd.to_timedelta(np.random.randint(180, 3650, N_STORES), unit="D")

stores = pd.DataFrame({
    "store_id": store_ids,
    "store_type": np.random.choice(store_types, size=N_STORES, p=store_type_probs),
    "region": store_regions,
    "city": store_cities,
    "opening_date": opening_dates,
})

# =========================
# 3) PRODUCTS TABLE
# =========================
product_ids = [f"P{str(i).zfill(4)}" for i in range(1, N_PRODUCTS + 1)]

categories = ["Grocery", "Electronics", "Clothing", "Home", "Beauty", "Sports"]
subcats = {
    "Grocery": ["Snacks", "Beverages", "Pantry", "Fresh"],
    "Electronics": ["Accessories", "Audio", "Computing", "Mobile"],
    "Clothing": ["Men", "Women", "Kids", "Footwear"],
    "Home": ["Kitchen", "Decor", "Cleaning", "Furniture"],
    "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrance"],
    "Sports": ["Fitness", "Outdoor", "TeamSports", "Shoes"],
}
brands = ["Aster", "Nova", "Pine", "Orchid", "Kite", "Nimbus", "Zenith", "Atlas"]

cat_price = {
    "Grocery": (1.5, 15),
    "Beauty": (5, 60),
    "Clothing": (8, 120),
    "Home": (4, 250),
    "Sports": (10, 180),
    "Electronics": (15, 900),
}

prod_cat = np.random.choice(categories, size=N_PRODUCTS,
                           p=[0.30, 0.12, 0.20, 0.16, 0.12, 0.10])
prod_subcat = [np.random.choice(subcats[c]) for c in prod_cat]
prod_brand = np.random.choice(brands, size=N_PRODUCTS)

prices, costs, discountable = [], [], []
for c in prod_cat:
    low, high = cat_price[c]
    base = np.exp(np.random.normal(np.log((low + high) / 2), 0.55))
    unit_price = float(np.clip(base, low, high))
    cost = unit_price * np.random.uniform(0.45, 0.75)

    prices.append(round(unit_price, 2))
    costs.append(round(cost, 2))
    discountable.append(np.random.choice([0, 1], p=[0.25, 0.75]))

products = pd.DataFrame({
    "product_id": product_ids,
    "category": prod_cat,
    "subcategory": prod_subcat,
    "brand": prod_brand,
    "unit_price": prices,
    "unit_cost": costs,
    "is_discountable": discountable,
})

# =========================
# 4) TRANSACTIONS TABLE (NO unit_price, NO total_amount)
# =========================
date_range = pd.date_range(start_date, end_date, freq="D")

dow = date_range.dayofweek.values
is_weekend = (dow >= 5).astype(int)
month_day = date_range.day.values
month_end = (month_day >= 25).astype(int)

daily_intensity = 1.0 + 0.15 * is_weekend + 0.10 * month_end
daily_intensity = daily_intensity / daily_intensity.mean()
date_probs = daily_intensity / daily_intensity.sum()

cust_propensity = pd.Series(
    np.random.lognormal(mean=0.0, sigma=0.35, size=N_CUSTOMERS),
    index=customers["customer_id"]
)

cust_tier = customers.set_index("customer_id")["loyalty_tier"]
cust_region = customers.set_index("customer_id")["region"]
cust_pref_channel = customers.set_index("customer_id")["preferred_channel"]

store_type_map = stores.set_index("store_id")["store_type"]
stores_by_region = {r: stores.loc[stores["region"] == r, "store_id"].tolist() for r in regions}
all_store_ids = stores["store_id"].tolist()

prod_df = products.set_index("product_id")
prod_discountable = prod_df["is_discountable"].to_dict()

fav_cats = {}
for cid in customer_ids:
    t = cust_tier[cid]
    base_probs = np.array([0.30, 0.12, 0.20, 0.16, 0.12, 0.10])
    if t in ["Gold", "Platinum"]:
        base_probs = base_probs + np.array([-0.03, 0.02, 0.00, 0.02, -0.01, 0.00])
    base_probs = base_probs / base_probs.sum()
    fav_cats[cid] = np.random.choice(categories, size=2, replace=False, p=base_probs).tolist()

products_by_cat = {c: products.loc[products["category"] == c, "product_id"].tolist()
                   for c in categories}

freq_weights = np.array([cust_propensity[cid] * tier_freq_mult[cust_tier[cid]]
                         for cid in customer_ids])
freq_weights = freq_weights / freq_weights.sum()

tx_customer = np.random.choice(customer_ids, size=N_TRANSACTIONS, p=freq_weights)
tx_dates = np.random.choice(date_range, size=N_TRANSACTIONS, p=date_probs)
tx_ids = [f"T{str(i).zfill(7)}" for i in range(1, N_TRANSACTIONS + 1)]

tx_store, tx_channel, tx_product = [], [], []
tx_qty, tx_discount_pct = [], []

for cid, dt in zip(tx_customer, tx_dates):

    r = cust_region[cid]
    if np.random.rand() < 0.85 and len(stores_by_region[r]) > 0:
        sid = np.random.choice(stores_by_region[r])
    else:
        sid = np.random.choice(all_store_ids)

    pref = cust_pref_channel[cid]
    if store_type_map[sid] == "OnlineHub":
        channel = np.random.choice(["Online", "Mobile"], p=[0.65, 0.35])
    else:
        base = {"InStore": 0.62, "Online": 0.25, "Mobile": 0.13}
        base[pref] += 0.18
        p = np.array([base["InStore"], base["Online"], base["Mobile"]])
        p = p / p.sum()
        channel = np.random.choice(["InStore", "Online", "Mobile"], p=p)

    if np.random.rand() < 0.70:
        cat = np.random.choice(fav_cats[cid])
    else:
        cat = np.random.choice(categories)

    pid = np.random.choice(products_by_cat[cat])

    if cat == "Grocery":
        qty = np.random.choice([1, 2, 3, 4, 5], p=[0.45, 0.25, 0.15, 0.10, 0.05])
    else:
        qty = np.random.choice([1, 2, 3], p=[0.75, 0.20, 0.05])

    disc = 0.0
    if prod_discountable[pid] == 1:
        prob_disc = 0.18
        if store_type_map[sid] == "Outlet":
            prob_disc += 0.18
        if channel in ["Online", "Mobile"]:
            prob_disc += 0.06
        if np.random.rand() < prob_disc:
            disc = np.random.choice([0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
                                    p=[0.25, 0.28, 0.18, 0.15, 0.09, 0.05])

    tx_store.append(sid)
    tx_channel.append(channel)
    tx_product.append(pid)
    tx_qty.append(qty)
    tx_discount_pct.append(round(disc, 2))

transactions = pd.DataFrame({
    "transaction_id": tx_ids,
    "customer_id": tx_customer,
    "store_id": tx_store,
    "product_id": tx_product,
    "transaction_date": pd.to_datetime(tx_dates),
    "channel": tx_channel,
    "quantity": tx_qty,
    "discount_pct": tx_discount_pct,
})

transactions["year_month"] = transactions["transaction_date"].dt.to_period("M").astype(str)
transactions = transactions.sort_values("transaction_date").reset_index(drop=True)

# =========================
# Save CSVs
# =========================
customers.to_csv(os.path.join(out_dir, "customers.csv"), index=False)
stores.to_csv(os.path.join(out_dir, "stores.csv"), index=False)
products.to_csv(os.path.join(out_dir, "products.csv"), index=False)
transactions.to_csv(os.path.join(out_dir, "transactions.csv"), index=False)

print("Saved datasets to:", out_dir)
print(customers.shape, stores.shape, products.shape, transactions.shape)
