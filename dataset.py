import pandas as pd

# =========================
# Load CSVs
# =========================
customers = pd.read_csv("synthetic_retail/customers.csv")
stores = pd.read_csv("synthetic_retail/stores.csv")
products = pd.read_csv("synthetic_retail/products.csv")
transactions = pd.read_csv("synthetic_retail/transactions.csv")

# Convert dates
customers["join_date"] = pd.to_datetime(customers["join_date"])
stores["opening_date"] = pd.to_datetime(stores["opening_date"])
transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])

# =========================
# Merge step-by-step
# =========================

# 1) transactions + products
df = transactions.merge(
    products[["product_id", "category", "unit_price", "is_discountable"]],
    on="product_id",
    how="left"
)

# 2) add stores
df = df.merge(
    stores[["store_id", "store_type", "region", "city"]],
    on="store_id",
    how="left",
    suffixes=("", "_store")
)

# 3) add customers
df = df.merge(
    customers[["customer_id", "gender", "age", "loyalty_tier", "preferred_channel"]],
    on="customer_id",
    how="left"
)

# =========================
# Reorder columns (clean output)
# =========================
final_cols = [
    # Product
    "product_id", "category", "unit_price", "is_discountable",

    # Store
    "store_id", "store_type", "region", "city",

    # Customer
    "customer_id", "gender", "age", "loyalty_tier", "preferred_channel",

    # Transaction
    "transaction_id", "transaction_date", "channel",
    "quantity", "discount_pct"
]

df = df[final_cols]

# =========================
# Save merged dataset
# =========================
df.to_csv("synthetic_retail/merged_transactions.csv", index=False)

print("Merged dataset saved: synthetic_retail/merged_transactions.csv")
print("Shape:", df.shape)
print(df.head())
