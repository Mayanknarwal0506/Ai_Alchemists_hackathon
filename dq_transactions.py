import pandas as pd


def dq_transactions(
    df_new: pd.DataFrame,
    transactions_existing: pd.DataFrame,
    customers_existing: pd.DataFrame,
    stores_existing: pd.DataFrame,
    products_existing: pd.DataFrame,
):
    df = df_new.copy()

    required = ["transaction_id", "customer_id", "store_id", "product_id",
                "transaction_date", "channel", "quantity", "discount_pct"]

    for c in required:
        if c not in df.columns:
            df[c] = None

    reasons = []

    # Rule 1: required not null
    missing_required = df[required].isna().any(axis=1)
    reasons.append((missing_required, "Missing required field(s)"))

    # Normalize types
    df["transaction_id"] = df["transaction_id"].astype(str)
    df["customer_id"] = df["customer_id"].astype(str)
    df["store_id"] = df["store_id"].astype(str)
    df["product_id"] = df["product_id"].astype(str)

    # Rule 2: transaction_id uniqueness
    existing_tx = set(transactions_existing["transaction_id"].astype(str)) if len(transactions_existing) else set()
    dup_existing = df["transaction_id"].isin(existing_tx)
    dup_within = df["transaction_id"].duplicated(keep="first")
    reasons.append((dup_existing | dup_within, "transaction_id not unique"))

    # Rule 3: quantity range
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    bad_qty = df["quantity"].isna() | (df["quantity"] < 1) | (df["quantity"] > 50)
    reasons.append((bad_qty, "Invalid quantity (1–50)"))

    # Rule 4: discount range
    df["discount_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce")
    bad_disc = df["discount_pct"].isna() | (df["discount_pct"] < 0) | (df["discount_pct"] > 0.80)
    reasons.append((bad_disc, "Invalid discount_pct (0–0.80)"))

    # Rule 5: channel conformance
    valid_channel = {"InStore", "Online", "Mobile"}
    bad_channel = ~df["channel"].astype(str).isin(valid_channel)
    reasons.append((bad_channel, "Invalid channel"))

    # Rule 6: FK checks
    cust_ids = set(customers_existing["customer_id"].astype(str)) if len(customers_existing) else set()
    store_ids = set(stores_existing["store_id"].astype(str)) if len(stores_existing) else set()
    prod_ids = set(products_existing["product_id"].astype(str)) if len(products_existing) else set()

    bad_cust = ~df["customer_id"].isin(cust_ids)
    bad_store = ~df["store_id"].isin(store_ids)
    bad_prod = ~df["product_id"].isin(prod_ids)

    reasons.append((bad_cust, "customer_id does not exist"))
    reasons.append((bad_store, "store_id does not exist"))
    reasons.append((bad_prod, "product_id does not exist"))

    # Rule 7: store opening date logic
    # Reject if transaction_date < opening_date
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    stores_tmp = stores_existing.copy()
    stores_tmp["opening_date"] = pd.to_datetime(stores_tmp["opening_date"], errors="coerce")

    tmp = df.merge(stores_tmp[["store_id", "opening_date"]], on="store_id", how="left")
    bad_store_date = tmp["opening_date"].isna() | (tmp["transaction_date"] < tmp["opening_date"])
    reasons.append((bad_store_date, "transaction_date is before store opening_date"))

    # Build rejection reason text
    reject_mask = pd.Series(False, index=df.index)
    reason_text = pd.Series("", index=df.index, dtype="object")

    for mask, msg in reasons:
        reject_mask = reject_mask | mask
        reason_text = reason_text.where(~mask, reason_text + msg + "; ")

    accepted = df.loc[~reject_mask].copy()
    rejected = df.loc[reject_mask].copy()
    rejected["rejection_reason"] = reason_text.loc[reject_mask].str.strip()

    # Add year_month to accepted
    accepted["transaction_date"] = pd.to_datetime(accepted["transaction_date"], errors="coerce")
    accepted["year_month"] = accepted["transaction_date"].dt.to_period("M").astype(str)

    # Standardize date format
    accepted["transaction_date"] = accepted["transaction_date"].dt.strftime("%Y-%m-%d")

    return accepted, rejected
