import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json

# -------------------------------
# Load Model & Files
# -------------------------------
model = joblib.load("xgboost_spend_model.pkl")
scaler = joblib.load("feature_scaler.pkl")

with open("feature_columns.json") as f:
    feature_cols = json.load(f)

df = pd.read_csv("short_term_spend_model_data.csv")

num_cols = ["daily_spend","total_qty","avg_price","transactions","avg_discount","age"]

# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="Customer Spend Predictor", layout="centered")

st.title("Short-Term Customer Spend Prediction")
st.write("Predict how much a customer will spend in the next 30 days")

cust_id = st.selectbox("Select Customer ID", df["customer_id"].unique())

cust = df[df["customer_id"] == cust_id].sort_values("transaction_date").iloc[-1]

st.subheader("Customer Profile")
st.write(f"Region: {cust['region']}")
st.write(f"City: {cust['city']}")
st.write(f"Gender: {cust['gender']}")
st.write(f"Age: {cust['age']}")
st.write(f"Store Type: {cust['store_type']}")

st.subheader("Enter Today’s Shopping Details")

daily_spend = st.number_input("Daily Spend", value=float(cust["daily_spend"]))
total_qty = st.number_input("Total Quantity", value=float(cust["total_qty"]))
avg_price = st.number_input("Average Price", value=float(cust["avg_price"]))
transactions = st.number_input("Transactions", value=int(cust["transactions"]))
avg_discount = st.number_input("Average Discount", value=float(cust["avg_discount"]))

# -------------------------------
# Prediction
# -------------------------------
if st.button("Predict Next 30-Day Spend"):

    # Build raw input
    input_df = pd.DataFrame([{
        "daily_spend": daily_spend,
        "total_qty": total_qty,
        "avg_price": avg_price,
        "transactions": transactions,
        "avg_discount": avg_discount,
        "age": cust["age"],
        "region": cust["region"],
        "city": cust["city"],
        "gender": cust["gender"],
        "store_type": cust["store_type"]
    }])

    #  One-hot encode categoricals
    input_df = pd.get_dummies(input_df)

    # Align with training columns
    input_df = input_df.reindex(columns=feature_cols, fill_value=0)

    # Scale numeric columns
    num_cols = ["daily_spend","total_qty","avg_price","transactions","avg_discount"]

    input_df[num_cols] = scaler.transform(input_df[num_cols])

    #  Predict
    pred = model.predict(input_df)[0]

    st.success(f"Predicted Next 30-Day Spend: ₹ {pred:,.2f}")

