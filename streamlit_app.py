import os
from datetime import datetime

import pandas as pd
import streamlit as st

from io_utils import (
    CUSTOMERS_CSV, STORES_CSV, PRODUCTS_CSV, TRANSACTIONS_CSV,
    MERGED_CSV,
    REJ_CUSTOMERS_CSV, REJ_STORES_CSV, REJ_PRODUCTS_CSV, REJ_TRANSACTIONS_CSV,
    ensure_dir,
    load_or_empty,
    append_rows,
    append_rejections,
    rebuild_merged
)

from dq_customers import dq_customers
from dq_stores import dq_stores
from dq_products import dq_products
from loyalty_update import update_loyalty_tiers

from dq_transactions import dq_transactions


# =========================
# Page config
# =========================
st.set_page_config(page_title="Retail Data Quality UI", layout="wide")
ensure_dir()

st.title("Retail Data Quality UI")
st.caption("Upload CSVs or add rows manually. Data Quality rules validate and append safe rows; rejected rows are logged.")


# =========================
# Load existing tables
# =========================
customers_existing = load_or_empty(CUSTOMERS_CSV, [
    "customer_id", "gender", "age", "join_date", "loyalty_tier",
    "region", "city", "preferred_channel"
])

stores_existing = load_or_empty(STORES_CSV, [
    "store_id", "store_type", "region", "city", "opening_date"
])

products_existing = load_or_empty(PRODUCTS_CSV, [
    "product_id", "category", "subcategory", "brand",
    "unit_price", "unit_cost", "is_discountable"
])

transactions_existing = load_or_empty(TRANSACTIONS_CSV, [
    "transaction_id", "customer_id", "store_id", "product_id",
    "transaction_date", "channel", "quantity", "discount_pct", "year_month"
])


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.subheader("Current dataset sizes")
    st.write("Customers:", len(customers_existing))
    st.write("Stores:", len(stores_existing))
    st.write("Products:", len(products_existing))
    st.write("Transactions:", len(transactions_existing))

    st.divider()

    if st.button("Rebuild merged_transactions.csv"):
        merged = rebuild_merged(customers_existing, stores_existing, products_existing, transactions_existing)
        st.success(f"Merged rebuilt. Rows: {len(merged)}")


st.divider()


# =========================
# Tabs
# =========================
tab_customers, tab_stores, tab_products, tab_transactions = st.tabs(
    ["Customers", "Stores", "Products", "Transactions"]
)


# ==========================================================
# CUSTOMERS TAB
# ==========================================================
with tab_customers:
    st.subheader("Append Customers")

    st.markdown("### Data Quality Rules (high level)")
    st.markdown("""
- Required fields must not be empty  
- Age must be between 16 and 90  
- customer_id must be unique  
- gender / loyalty_tier / preferred_channel must match allowed values  
    """)

    mode = st.radio("Input method", ["Upload CSV", "Manual entry"], horizontal=True, key="cust_mode")

    if mode == "Upload CSV":
        up = st.file_uploader("Upload customers CSV", type=["csv"], key="cust_upload")

        if up is not None:
            df_new = pd.read_csv(up)
            st.write("Preview:")
            st.dataframe(df_new.head(20), use_container_width=True)

            if st.button("Validate & Append Customers"):
                accepted, rejected = dq_customers(df_new, customers_existing)

                append_rows(CUSTOMERS_CSV, accepted)
                append_rejections(REJ_CUSTOMERS_CSV, rejected)

                st.success(f"Accepted: {len(accepted)} | Rejected: {len(rejected)}")
                if len(rejected):
                    st.dataframe(rejected.head(50), use_container_width=True)

    else:
        with st.form("cust_form"):
            c1, c2, c3 = st.columns(3)

            with c1:
                customer_id = st.text_input("customer_id", value="C00999")
                gender = st.selectbox("gender", ["F", "M", "O"])
                age = st.number_input("age", min_value=16, max_value=90, value=30)

            with c2:
                loyalty_tier = st.selectbox("loyalty_tier", ["Bronze", "Silver", "Gold", "Platinum"])
                preferred_channel = st.selectbox("preferred_channel", ["InStore", "Online", "Mobile"])
                region = st.selectbox("region", ["North", "South", "East", "West", "Central"])

            with c3:
                city = st.text_input("city", value="Midtown")
                join_date = st.date_input("join_date", value=datetime(2025, 1, 1))

            submitted = st.form_submit_button("Validate & Append")

        if submitted:
            df_new = pd.DataFrame([{
                "customer_id": customer_id,
                "gender": gender,
                "age": age,
                "join_date": str(join_date),
                "loyalty_tier": loyalty_tier,
                "region": region,
                "city": city,
                "preferred_channel": preferred_channel,
            }])

            accepted, rejected = dq_customers(df_new, customers_existing)

            append_rows(CUSTOMERS_CSV, accepted)
            append_rejections(REJ_CUSTOMERS_CSV, rejected)

            if len(accepted):
                st.success("Customer accepted and appended.")
            else:
                st.error("Customer rejected.")
                st.dataframe(rejected, use_container_width=True)


# ==========================================================
# STORES TAB
# ==========================================================
with tab_stores:
    st.subheader("Append Stores")

    st.markdown("### Data Quality Rules (high level)")
    st.markdown("""
- Required fields must not be empty  
- store_id must be unique  
- store_type and region must match allowed values  
    """)

    mode = st.radio("Input method", ["Upload CSV", "Manual entry"], horizontal=True, key="store_mode")

    if mode == "Upload CSV":
        up = st.file_uploader("Upload stores CSV", type=["csv"], key="store_upload")

        if up is not None:
            df_new = pd.read_csv(up)
            st.write("Preview:")
            st.dataframe(df_new.head(20), use_container_width=True)

            if st.button("Validate & Append Stores"):
                accepted, rejected = dq_stores(df_new, stores_existing)

                append_rows(STORES_CSV, accepted)
                append_rejections(REJ_STORES_CSV, rejected)

                st.success(f"Accepted: {len(accepted)} | Rejected: {len(rejected)}")
                if len(rejected):
                    st.dataframe(rejected.head(50), use_container_width=True)

    else:
        with st.form("store_form"):
            c1, c2, c3 = st.columns(3)

            with c1:
                store_id = st.text_input("store_id", value="S999")
                store_type = st.selectbox("store_type", ["Mall", "Street", "Outlet", "OnlineHub"])

            with c2:
                region = st.selectbox("region", ["North", "South", "East", "West", "Central"], key="store_region")
                city = st.text_input("city", value="Centrum")

            with c3:
                opening_date = st.date_input("opening_date", value=datetime(2020, 1, 1))

            submitted = st.form_submit_button("Validate & Append")

        if submitted:
            df_new = pd.DataFrame([{
                "store_id": store_id,
                "store_type": store_type,
                "region": region,
                "city": city,
                "opening_date": str(opening_date),
            }])

            accepted, rejected = dq_stores(df_new, stores_existing)

            append_rows(STORES_CSV, accepted)
            append_rejections(REJ_STORES_CSV, rejected)

            if len(accepted):
                st.success("Store accepted and appended.")
            else:
                st.error("Store rejected.")
                st.dataframe(rejected, use_container_width=True)


# ==========================================================
# PRODUCTS TAB
# ==========================================================
with tab_products:
    st.subheader("Append Products")

    st.markdown("### Data Quality Rules (high level)")
    st.markdown("""
- Required fields must not be empty  
- product_id must be unique  
- unit_price must be numeric and valid  
- category and is_discountable must match allowed values  
    """)

    mode = st.radio("Input method", ["Upload CSV", "Manual entry"], horizontal=True, key="prod_mode")

    if mode == "Upload CSV":
        up = st.file_uploader("Upload products CSV", type=["csv"], key="prod_upload")

        if up is not None:
            df_new = pd.read_csv(up)
            st.write("Preview:")
            st.dataframe(df_new.head(20), use_container_width=True)

            if st.button("Validate & Append Products"):
                accepted, rejected = dq_products(df_new, products_existing)

                append_rows(PRODUCTS_CSV, accepted)
                append_rejections(REJ_PRODUCTS_CSV, rejected)

                st.success(f"Accepted: {len(accepted)} | Rejected: {len(rejected)}")
                if len(rejected):
                    st.dataframe(rejected.head(50), use_container_width=True)

    else:
        with st.form("prod_form"):
            c1, c2, c3 = st.columns(3)

            with c1:
                product_id = st.text_input("product_id", value="P9999")
                category = st.selectbox("category", ["Grocery", "Electronics", "Clothing", "Home", "Beauty", "Sports"])
                unit_price = st.number_input("unit_price", min_value=0.5, max_value=5000.0, value=25.0)

            with c2:
                subcategory = st.text_input("subcategory", value="Accessories")
                brand = st.text_input("brand", value="Nova")

            with c3:
                is_discountable = st.selectbox("is_discountable", [0, 1])
                unit_cost = st.number_input("unit_cost", min_value=0.0, max_value=5000.0, value=12.0)

            submitted = st.form_submit_button("Validate & Append")

        if submitted:
            df_new = pd.DataFrame([{
                "product_id": product_id,
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "unit_price": unit_price,
                "unit_cost": unit_cost,
                "is_discountable": is_discountable,
            }])

            accepted, rejected = dq_products(df_new, products_existing)

            append_rows(PRODUCTS_CSV, accepted)
            append_rejections(REJ_PRODUCTS_CSV, rejected)

            if len(accepted):
                st.success("Product accepted and appended.")
            else:
                st.error("Product rejected.")
                st.dataframe(rejected, use_container_width=True)


# ==========================================================
# TRANSACTIONS TAB
# ==========================================================
with tab_transactions:
    st.subheader("Append Transactions")

    st.markdown("### Data Quality Rules (high level)")
    st.markdown("""
- Required fields must not be empty  
- transaction_id must be unique  
- quantity must be in range 1–50  
- discount_pct must be between 0 and 0.80  
- customer_id, store_id, product_id must exist in their tables (FK check)  
- transaction_date must be >= store opening_date  
    """)

    mode = st.radio("Input method", ["Upload CSV", "Manual entry"], horizontal=True, key="tx_mode")

    if mode == "Upload CSV":
        up = st.file_uploader("Upload transactions CSV", type=["csv"], key="tx_upload")

        if up is not None:
            df_new = pd.read_csv(up)
            st.write("Preview:")
            st.dataframe(df_new.head(20), use_container_width=True)

            if st.button("Validate & Append Transactions"):
                accepted, rejected = dq_transactions(
                    df_new,
                    transactions_existing,
                    customers_existing,
                    stores_existing,
                    products_existing,
                )

                append_rows(TRANSACTIONS_CSV, accepted)
                append_rejections(REJ_TRANSACTIONS_CSV, rejected)

                st.success(f"Accepted: {len(accepted)} | Rejected: {len(rejected)}")
                if len(rejected):
                    st.dataframe(rejected.head(50), use_container_width=True)

                # Reload + rebuild merged
                customers_existing = pd.read_csv(CUSTOMERS_CSV)
                stores_existing = pd.read_csv(STORES_CSV)
                products_existing = pd.read_csv(PRODUCTS_CSV)
                transactions_existing = pd.read_csv(TRANSACTIONS_CSV)

                customers_updated = update_loyalty_tiers(customers_existing, transactions_existing, products_existing)
                customers_updated.to_csv(CUSTOMERS_CSV, index=False)

                customers_existing = pd.read_csv(CUSTOMERS_CSV)

                merged = rebuild_merged(customers_existing, stores_existing, products_existing, transactions_existing)

                st.success("merged_transactions.csv updated + loyalty tiers recalculated ")
                st.info(f"Merged rows: {len(merged)}")


    else:
        with st.form("tx_form"):
            c1, c2, c3 = st.columns(3)

            with c1:
                transaction_id = st.text_input("transaction_id", value="T9999999")
                customer_id = st.text_input("customer_id", value="C00001")
                store_id = st.text_input("store_id", value="S001")

            with c2:
                product_id = st.text_input("product_id", value="P0001")
                channel = st.selectbox("channel", ["InStore", "Online", "Mobile"])
                transaction_date = st.date_input("transaction_date", value=datetime(2025, 12, 1))

            with c3:
                quantity = st.number_input("quantity", min_value=1, max_value=50, value=1)
                discount_pct = st.number_input("discount_pct", min_value=0.0, max_value=0.80, value=0.0, step=0.05)

            submitted = st.form_submit_button("Validate & Append")

        if submitted:
            df_new = pd.DataFrame([{
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "store_id": store_id,
                "product_id": product_id,
                "transaction_date": str(transaction_date),
                "channel": channel,
                "quantity": quantity,
                "discount_pct": discount_pct,
            }])

            accepted, rejected = dq_transactions(
                df_new,
                transactions_existing,
                customers_existing,
                stores_existing,
                products_existing,
            )

            append_rows(TRANSACTIONS_CSV, accepted)
            append_rejections(REJ_TRANSACTIONS_CSV, rejected)

            if len(accepted):
                st.success("Transaction accepted and appended.")

                # Reload + rebuild merged
                customers_existing = pd.read_csv(CUSTOMERS_CSV)
                stores_existing = pd.read_csv(STORES_CSV)
                products_existing = pd.read_csv(PRODUCTS_CSV)
                transactions_existing = pd.read_csv(TRANSACTIONS_CSV)

                merged = rebuild_merged(customers_existing, stores_existing, products_existing, transactions_existing)
                st.info(f"merged_transactions.csv updated. Rows: {len(merged)}")

            else:
                st.error("Transaction rejected.")
                st.dataframe(rejected, use_container_width=True)


# =========================
# Merged preview
# =========================
st.divider()

if os.path.exists(MERGED_CSV):
    st.subheader("Merged Transactions Preview")
    merged_now = pd.read_csv(MERGED_CSV)
    st.dataframe(merged_now.tail(30), use_container_width=True)
else:
    st.info("merged_transactions.csv not found yet. Click rebuild in sidebar.")
