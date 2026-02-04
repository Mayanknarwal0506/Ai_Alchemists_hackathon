import pandas as pd
import streamlit as st
from graphviz import Digraph


# =========================
# Hardcoded schema rules
# =========================

SCHEMA = {
    "customers.csv": {
        "pk": ["customer_id"],
        "columns": {
            "customer_id": "string",
            "gender": "string",
            "age": "int",
            "join_date": "date",
            "loyalty_tier": "string",
            "region": "string",
            "city": "string",
            "preferred_channel": "string",
        }
    },
    "stores.csv": {
        "pk": ["store_id"],
        "columns": {
            "store_id": "string",
            "store_type": "string",
            "region": "string",
            "city": "string",
            "opening_date": "date",
        }
    },
    "products.csv": {
        "pk": ["product_id"],
        "columns": {
            "product_id": "string",
            "category": "string",
            "subcategory": "string",
            "brand": "string",
            "unit_price": "float",
            "unit_cost": "float",
            "is_discountable": "int",
        }
    },
    "transactions.csv": {
        "pk": ["transaction_id"],
        "fk": {
            "customer_id": ("customers.csv", "customer_id"),
            "store_id": ("stores.csv", "store_id"),
            "product_id": ("products.csv", "product_id"),
        },
        "columns": {
            "transaction_id": "string",
            "customer_id": "string",
            "store_id": "string",
            "product_id": "string",
            "transaction_date": "date",
            "channel": "string",
            "quantity": "int",
            "discount_pct": "float",
            "year_month": "string",
        }
    }
}


# =========================
# Schema Table Builder
# =========================

def schema_table(table_name: str):
    meta = SCHEMA[table_name]

    rows = []
    for col, dtype in meta["columns"].items():
        is_pk = col in meta.get("pk", [])
        is_fk = col in meta.get("fk", {})

        fk_ref = ""
        if is_fk:
            ref_table, ref_col = meta["fk"][col]
            fk_ref = f"{ref_table}.{ref_col}"

        rows.append({
            "column": col,
            "datatype": dtype,
            "PK": "YES" if is_pk else "",
            "FK": "YES" if is_fk else "",
            "references": fk_ref
        })

    return pd.DataFrame(rows)


# =========================
# ER Diagram Builder
# =========================

def build_er_diagram():
    dot = Digraph("Retail_ER", format="png")
    dot.attr(rankdir="LR", fontsize="12")

    # Nodes (tables)
    for table_name, meta in SCHEMA.items():
        pk_cols = meta.get("pk", [])
        cols = meta["columns"]

        label_lines = [f"<b>{table_name}</b>"]

        for c, t in cols.items():
            if c in pk_cols:
                label_lines.append(f"<b>PK</b> {c}: {t}")
            elif c in meta.get("fk", {}):
                label_lines.append(f"<b>FK</b> {c}: {t}")
            else:
                label_lines.append(f"{c}: {t}")

        label_html = "<br/>".join(label_lines)

        dot.node(
            table_name,
            label=f"<{label_html}>",
            shape="box",
            style="rounded"
        )

    # Edges (relationships)
    tx_fk = SCHEMA["transactions.csv"]["fk"]
    for fk_col, (ref_table, ref_col) in tx_fk.items():
        dot.edge("transactions.csv", ref_table, label=f"{fk_col} → {ref_col}")

    return dot


# =========================
# Streamlit UI
# =========================

def render_schema_page():
    st.subheader(" Dataset Schema (All 4 CSVs)")
    st.caption("Shows columns, datatypes, Primary Keys, Foreign Keys, and relationships.")

    st.divider()

    # ER Diagra
    st.markdown("## Relationship Graph (ER Diagram)")
    er = build_er_diagram()
    st.graphviz_chart(er)

    st.divider()

    # Schema tables
    st.markdown("## Table Schemas")

    for table in SCHEMA.keys():
        st.markdown(f"### {table}")
        df = schema_table(table)
        st.dataframe(df, use_container_width=True)
        st.divider()
