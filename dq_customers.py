import pandas as pd


def dq_customers(df_new: pd.DataFrame, customers_existing: pd.DataFrame):
    df = df_new.copy()

    required = ["customer_id", "gender", "age", "join_date",
                "loyalty_tier", "region", "city", "preferred_channel"]

    # Ensure columns exist
    for c in required:
        if c not in df.columns:
            df[c] = None

    reasons = []

    # Rule 1: required not null
    missing_required = df[required].isna().any(axis=1)
    reasons.append((missing_required, "Missing required field(s)"))

    # Rule 2: age valid
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    bad_age = df["age"].isna() | (df["age"] < 16) | (df["age"] > 90)
    reasons.append((bad_age, "Age out of range (16–90)"))

    # Rule 2b: join_date must not be in the future
    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    bad_join_date = df["join_date"].isna() | (df["join_date"] > today)
    reasons.append((bad_join_date, "join_date is invalid or in the future"))


    # Rule 3: uniqueness
    existing_ids = set(customers_existing["customer_id"].astype(str)) if len(customers_existing) else set()
    df["customer_id"] = df["customer_id"].astype(str)

    duplicate_existing = df["customer_id"].isin(existing_ids)
    duplicate_within = df["customer_id"].duplicated(keep="first")
    reasons.append((duplicate_existing | duplicate_within, "customer_id not unique"))

    # Rule 4: conformance
    valid_gender = {"F", "M", "O"}
    valid_tier = {"Bronze", "Silver", "Gold", "Platinum"}
    valid_channel = {"InStore", "Online", "Mobile"}
    valid_region = {"North", "South", "East", "West", "Central"}

    bad_gender = ~df["gender"].astype(str).isin(valid_gender)
    bad_tier = ~df["loyalty_tier"].astype(str).isin(valid_tier)
    bad_channel = ~df["preferred_channel"].astype(str).isin(valid_channel)
    bad_region = ~df["region"].astype(str).isin(valid_region)

    reasons.append((bad_gender, "Invalid gender"))
    reasons.append((bad_tier, "Invalid loyalty_tier"))
    reasons.append((bad_channel, "Invalid preferred_channel"))
    reasons.append((bad_region, "Invalid region"))

    # Build rejection reason text
    reject_mask = pd.Series(False, index=df.index)
    reason_text = pd.Series("", index=df.index, dtype="object")

    for mask, msg in reasons:
        reject_mask = reject_mask | mask
        reason_text = reason_text.where(~mask, reason_text + msg + "; ")

    accepted = df.loc[~reject_mask].copy()
    rejected = df.loc[reject_mask].copy()
    rejected["rejection_reason"] = reason_text.loc[reject_mask].str.strip()

    # Cleanup: standardize join_date
    accepted["join_date"] = pd.to_datetime(accepted["join_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    return accepted, rejected
