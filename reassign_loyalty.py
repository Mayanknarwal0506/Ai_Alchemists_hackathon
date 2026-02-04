import pandas as pd
import os

DATA_DIR = "synthetic_retail"

CUSTOMERS_CSV = os.path.join(DATA_DIR, "customers.csv")
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")
TRANSACTIONS_CSV = os.path.join(DATA_DIR, "transactions.csv")
STORES_CSV = os.path.join(DATA_DIR, "stores.csv")
MERGED_CSV = os.path.join(DATA_DIR, "merged_transactions.csv")


def rebuild_merged(customers, stores, products, transactions):
    transactions = transactions.copy()
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"], errors="coerce")

    df = transactions.merge(
        products[["product_id", "category", "unit_price", "is_discountable"]],
        on="product_id",
        how="left"
    )

    df = df.merge(
        stores[["store_id", "store_type", "region", "city"]],
        on="store_id",
        how="left"
    )

    df = df.merge(
        customers[["customer_id", "gender", "age", "loyalty_tier", "preferred_channel"]],
        on="customer_id",
        how="left"
    )

    final_cols = [
        "product_id", "category", "unit_price", "is_discountable",
        "store_id", "store_type", "region", "city",
        "customer_id", "gender", "age", "loyalty_tier", "preferred_channel",
        "transaction_id", "transaction_date", "channel",
        "quantity", "discount_pct"
    ]

    df = df[final_cols]
    df.to_csv(MERGED_CSV, index=False)
    return df


# =========================
# Load data
# =========================
customers = pd.read_csv(CUSTOMERS_CSV)
products = pd.read_csv(PRODUCTS_CSV)
transactions = pd.read_csv(TRANSACTIONS_CSV)
stores = pd.read_csv(STORES_CSV)

transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"], errors="coerce")

# =========================
# Compute spend per transaction
# =========================
df = transactions.merge(products[["product_id", "unit_price"]], on="product_id", how="left")

df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
df["discount_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce").fillna(0)
df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)

df["spend"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"])

# =========================
# Monthly spend per customer
# =========================
df["year_month"] = df["transaction_date"].dt.to_period("M").astype(str)

monthly = (
    df.groupby(["customer_id", "year_month"])["spend"]
    .sum()
    .reset_index()
    .rename(columns={"spend": "monthly_spend"})
)

# =========================
# Average monthly spend per customer
# =========================
avg_monthly = (
    monthly.groupby("customer_id")["monthly_spend"]
    .mean()
    .reset_index()
    .rename(columns={"monthly_spend": "avg_monthly_spend"})
)

# Merge into customers
customers = customers.merge(avg_monthly, on="customer_id", how="left")
customers["avg_monthly_spend"] = customers["avg_monthly_spend"].fillna(0)

# =========================
# Assign tiers by quartiles (25% each)
# =========================
customers = customers.sort_values("avg_monthly_spend", ascending=False).reset_index(drop=True)

n = len(customers)
q1 = int(n * 0.25)
q2 = int(n * 0.50)
q3 = int(n * 0.75)

def tier_from_rank(i):
    if i < q1:
        return "Platinum"
    elif i < q2:
        return "Gold"
    elif i < q3:
        return "Silver"
    else:
        return "Bronze"

customers["loyalty_tier"] = [tier_from_rank(i) for i in range(n)]

# Drop helper column (optional)
customers.drop(columns=["avg_monthly_spend"], inplace=True)

# =========================
# Save customers + rebuild merged
# =========================
customers.to_csv(CUSTOMERS_CSV, index=False)
print("Updated loyalty_tier based on avg monthly spend.")

merged = rebuild_merged(customers, stores, products, transactions)
print("Rebuilt merged_transactions.csv:", merged.shape)
