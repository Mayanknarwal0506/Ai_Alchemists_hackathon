import pandas as pd


def dq_products(df_new: pd.DataFrame, products_existing: pd.DataFrame):
    df = df_new.copy()

    required = ["product_id", "category", "unit_price", "is_discountable"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    reasons = []

    # Rule 1: required not null
    missing_required = df[required].isna().any(axis=1)
    reasons.append((missing_required, "Missing required field(s)"))

    # Rule 2: unit_price numeric and positive
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    bad_price = df["unit_price"].isna() | (df["unit_price"] <= 0) | (df["unit_price"] > 5000)
    reasons.append((bad_price, "Invalid unit_price"))

    # Rule 3: product_id uniqueness
    df["product_id"] = df["product_id"].astype(str)
    existing_ids = set(products_existing["product_id"].astype(str)) if len(products_existing) else set()

    dup_existing = df["product_id"].isin(existing_ids)
    dup_within = df["product_id"].duplicated(keep="first")
    reasons.append((dup_existing | dup_within, "product_id not unique"))

    # Rule 4: conformance
    valid_category = {"Grocery", "Electronics", "Clothing", "Home", "Beauty", "Sports"}
    bad_category = ~df["category"].astype(str).isin(valid_category)
    reasons.append((bad_category, "Invalid category"))

    df["is_discountable"] = pd.to_numeric(df["is_discountable"], errors="coerce")
    bad_disc = df["is_discountable"].isna() | ~df["is_discountable"].isin([0, 1])
    reasons.append((bad_disc, "Invalid is_discountable (must be 0/1)"))

    reject_mask = pd.Series(False, index=df.index)
    reason_text = pd.Series("", index=df.index, dtype="object")

    for mask, msg in reasons:
        reject_mask = reject_mask | mask
        reason_text = reason_text.where(~mask, reason_text + msg + "; ")

    accepted = df.loc[~reject_mask].copy()
    rejected = df.loc[reject_mask].copy()
    rejected["rejection_reason"] = reason_text.loc[reject_mask].str.strip()

    # Optional fill columns if missing
    for c in ["subcategory", "brand", "unit_cost"]:
        if c not in accepted.columns:
            accepted[c] = None

    return accepted, rejected
