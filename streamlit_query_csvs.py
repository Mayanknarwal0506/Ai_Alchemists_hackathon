import streamlit as st
import pandas as pd
import duckdb
import os

DATA_DIR = "synthetic_retail"

CSV_FILES = {
    "customers": os.path.join(DATA_DIR, "customers.csv"),
    "stores": os.path.join(DATA_DIR, "stores.csv"),
    "products": os.path.join(DATA_DIR, "products.csv"),
    "transactions": os.path.join(DATA_DIR, "transactions.csv"),
    "merged_transactions": os.path.join(DATA_DIR, "merged_transactions.csv"),
}

st.set_page_config(page_title="CSV Viewer + SQL Query", layout="wide")

st.title(" Retail CSV Viewer + SQL Query Tool")
st.write("View tables and run SQL queries across customers, stores, products, transactions, merged_transactions.")

# ---------------------------
# Load CSVs
# ---------------------------
@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

tables = {}
missing = []

for name, path in CSV_FILES.items():
    if os.path.exists(path):
        tables[name] = load_csv(path)
    else:
        missing.append(name)

if missing:
    st.warning(f"Missing files: {', '.join(missing)}")

# ---------------------------
# Sidebar: Select table to view
# ---------------------------
st.sidebar.header("View Table")

table_name = st.sidebar.selectbox("Choose a CSV table", list(tables.keys()))

df = tables[table_name]

st.subheader(f"Viewing: {table_name}.csv")
st.write("Shape:", df.shape)

# Basic filters
with st.expander(" Filter options"):
    cols = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist())
    limit = st.slider("Rows to show", 5, 200, 25)

st.dataframe(df[cols].head(limit), use_container_width=True)

# ---------------------------
# SQL Query Section
# ---------------------------
st.divider()
st.subheader(" SQL Query (DuckDB)")

st.write("You can query across all tables using SQL. Example:")
st.code("""
SELECT customer_id, COUNT(*) AS tx_count
FROM transactions
GROUP BY customer_id
ORDER BY tx_count DESC
LIMIT 10;
""")

default_query = "SELECT * FROM customers LIMIT 10;"

query = st.text_area("Write SQL query here", value=default_query, height=160)

run = st.button("▶ Run Query")

if run:
    try:
        con = duckdb.connect(database=":memory:")

        # Register all loaded tables into duckdb
        for name, d in tables.items():
            con.register(name, d)

        result = con.execute(query).df()

        st.success(f"Query executed successfully. Rows returned: {len(result)}")
        st.dataframe(result, use_container_width=True)

        # Download result
        csv_out = result.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download query result as CSV",
            data=csv_out,
            file_name="query_result.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error("Query failed.")
        st.code(str(e))

# ---------------------------
# Quick Query Buttons
# ---------------------------
st.divider()
st.subheader("⚡ Quick Queries")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Top 10 Customers by Spend"):
        con = duckdb.connect(database=":memory:")
        for name, d in tables.items():
            con.register(name, d)

        q = """
        SELECT
          t.customer_id,
          SUM(t.quantity * p.unit_price * (1 - t.discount_pct)) AS total_spend
        FROM transactions t
        JOIN products p ON t.product_id = p.product_id
        GROUP BY t.customer_id
        ORDER BY total_spend DESC
        LIMIT 10;
        """
        st.dataframe(con.execute(q).df(), use_container_width=True)

with col2:
    if st.button("Transactions per Store"):
        con = duckdb.connect(database=":memory:")
        for name, d in tables.items():
            con.register(name, d)

        q = """
        SELECT store_id, COUNT(*) AS tx_count
        FROM transactions
        GROUP BY store_id
        ORDER BY tx_count DESC;
        """
        st.dataframe(con.execute(q).df(), use_container_width=True)

with col3:
    if st.button("Sales by Category"):
        con = duckdb.connect(database=":memory:")
        for name, d in tables.items():
            con.register(name, d)

        q = """
        SELECT
          p.category,
          SUM(t.quantity * p.unit_price * (1 - t.discount_pct)) AS sales
        FROM transactions t
        JOIN products p ON t.product_id = p.product_id
        GROUP BY p.category
        ORDER BY sales DESC;
        """
        st.dataframe(con.execute(q).df(), use_container_width=True)
