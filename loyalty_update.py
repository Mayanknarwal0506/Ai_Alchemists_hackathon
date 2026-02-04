import pandas as pd


def update_loyalty_tiers(customers: pd.DataFrame,
                         transactions: pd.DataFrame,
                         products: pd.DataFrame) -> pd.DataFrame:
    """
    Rule:
    - Monthly spend per customer = sum(quantity * unit_price * (1-discount))
    - Avg monthly spend per customer = mean(monthly spend)
    - Sort customers by avg monthly spend desc
    - Top 25% Platinum, next 25% Gold, next 25% Silver, last 25% Bronze
    """

    customers = customers.copy()
    transactions = transactions.copy()
    products = products.copy()

    customers["customer_id"] = customers["customer_id"].astype(str)
    transactions["customer_id"] = transactions["customer_id"].astype(str)
    transactions["product_id"] = transactions["product_id"].astype(str)
    products["product_id"] = products["product_id"].astype(str)

    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"], errors="coerce")

    # Merge unit_price into transactions
    tx = transactions.merge(products[["product_id", "unit_price"]], on="product_id", how="left")

    tx["quantity"] = pd.to_numeric(tx["quantity"], errors="coerce").fillna(0)
    tx["discount_pct"] = pd.to_numeric(tx["discount_pct"], errors="coerce").fillna(0)
    tx["unit_price"] = pd.to_numeric(tx["unit_price"], errors="coerce").fillna(0)

    # Spend
    tx["spend"] = tx["quantity"] * tx["unit_price"] * (1 - tx["discount_pct"])

    # Month bucket
    tx["year_month"] = tx["transaction_date"].dt.to_period("M").astype(str)

    # Monthly spend
    monthly = (
        tx.groupby(["customer_id", "year_month"])["spend"]
        .sum()
        .reset_index()
        .rename(columns={"spend": "monthly_spend"})
    )

    # Avg monthly spend
    avg_monthly = (
        monthly.groupby("customer_id")["monthly_spend"]
        .mean()
        .reset_index()
        .rename(columns={"monthly_spend": "avg_monthly_spend"})
    )

    customers = customers.merge(avg_monthly, on="customer_id", how="left")
    customers["avg_monthly_spend"] = customers["avg_monthly_spend"].fillna(0)

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

    customers.drop(columns=["avg_monthly_spend"], inplace=True)

    return customers
