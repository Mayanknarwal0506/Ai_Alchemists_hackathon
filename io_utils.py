import os
import pandas as pd
from datetime import datetime

DATA_DIR = "synthetic_retail"

CUSTOMERS_CSV = os.path.join(DATA_DIR, "customers.csv")
STORES_CSV = os.path.join(DATA_DIR, "stores.csv")
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")
TRANSACTIONS_CSV = os.path.join(DATA_DIR, "transactions.csv")
MERGED_CSV = os.path.join(DATA_DIR, "merged_transactions.csv")

REJ_CUSTOMERS_CSV = os.path.join(DATA_DIR, "rejected_customers.csv")
REJ_STORES_CSV = os.path.join(DATA_DIR, "rejected_stores.csv")
REJ_PRODUCTS_CSV = os.path.join(DATA_DIR, "rejected_products.csv")
REJ_TRANSACTIONS_CSV = os.path.join(DATA_DIR, "rejected_transactions.csv")


def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_or_empty(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=columns)


def append_rows(path, df_new: pd.DataFrame):
    if df_new is None or len(df_new) == 0:
        return

    if os.path.exists(path):
        df_old = pd.read_csv(path)
        df_out = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_out = df_new.copy()

    df_out.to_csv(path, index=False)


def append_rejections(path, df_rej: pd.DataFrame):
    if df_rej is None or len(df_rej) == 0:
        return

    df_rej = df_rej.copy()
    df_rej["rejected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if os.path.exists(path):
        old = pd.read_csv(path)
        out = pd.concat([old, df_rej], ignore_index=True)
    else:
        out = df_rej

    out.to_csv(path, index=False)


def rebuild_merged(customers, stores, products, transactions):
    # Ensure datetime
    transactions = transactions.copy()
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"], errors="coerce")

    # Join products
    df = transactions.merge(
        products[["product_id", "category", "unit_price", "is_discountable"]],
        on="product_id",
        how="left"
    )

    # Join stores
    df = df.merge(
        stores[["store_id", "store_type", "region", "city"]],
        on="store_id",
        how="left",
        suffixes=("", "_store")
    )

    # Join customers
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
