import pandas as pd


def dq_stores(df_new: pd.DataFrame, stores_existing: pd.DataFrame):
    df = df_new.copy()

    required = ["store_id", "store_type", "region", "city", "opening_date"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    reasons = []

    # Rule 1: required not null
    missing_required = df[required].isna().any(axis=1)
    reasons.append((missing_required, "Missing required field(s)"))

    # Rule 2: store_id uniqueness
    df["store_id"] = df["store_id"].astype(str)
    existing_ids = set(stores_existing["store_id"].astype(str)) if len(stores_existing) else set()

    dup_existing = df["store_id"].isin(existing_ids)
    dup_within = df["store_id"].duplicated(keep="first")
    reasons.append((dup_existing | dup_within, "store_id not unique"))

    # Rule: opening_date must not be in the future
    df["opening_date"] = pd.to_datetime(df["opening_date"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    bad_open_date = df["opening_date"].isna() | (df["opening_date"] > today)
    reasons.append((bad_open_date, "opening_date is invalid or in the future"))


    # Rule 3: conformance
    valid_type = {"Mall", "Street", "Outlet", "OnlineHub"}
    valid_region = {"North", "South", "East", "West", "Central"}

    bad_type = ~df["store_type"].astype(str).isin(valid_type)
    bad_region = ~df["region"].astype(str).isin(valid_region)

    reasons.append((bad_type, "Invalid store_type"))
    reasons.append((bad_region, "Invalid region"))

    reject_mask = pd.Series(False, index=df.index)
    reason_text = pd.Series("", index=df.index, dtype="object")

    for mask, msg in reasons:
        reject_mask = reject_mask | mask
        reason_text = reason_text.where(~mask, reason_text + msg + "; ")

    accepted = df.loc[~reject_mask].copy()
    rejected = df.loc[reject_mask].copy()
    rejected["rejection_reason"] = reason_text.loc[reject_mask].str.strip()

    accepted["opening_date"] = pd.to_datetime(accepted["opening_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    return accepted, rejected
