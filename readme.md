# Synthetic Data Generation

An end-to-end data engineering ecosystem designed to generate high-fidelity synthetic retail data, enforce rigorous Data Quality (DQ) standards, and provide actionable insights via an interactive dashboard.

## Key Features

* **Data Generation:** Custom engine (`data_generator.py`) to create relational retail entities (Customers, Products, Stores, Transactions).
* **DQ Framework:** Dedicated validation suite for each data silo to ensure referential integrity and schema compliance.
* **Loyalty Logic:** Specialized scripts for updating and reassigning customer loyalty tiers based on transactional behavior.
* **Interactive Analytics:** A Streamlit-powered frontend for real-time querying and data visualization.

---

## Repository Roadmap

| Category | Files |
| :--- | :--- |
| **Data Core** | `customers.csv`, `products.csv`, `transactions.csv`, `final_dataset.csv` |
| **Quality Suite** | `dq_customers.py`, `dq_products.py`, `dq_stores.py`, `dq_transactions.py` |
| **Processing** | `dataset.py`, `loyalty_update.py`, `reassign_loyalty.py`, `io_utils.py` |
| **Web UI** | `streamlit_app.py`, `schema_ui.py`, `streamlit_query_csvs.py` |


---
# Short-Term Customer Spend Prediction  
An end-to-end Machine Learning and Analytics System

An intelligent data science and machine learning pipeline designed to analyze customer transaction data, train a predictive model, and deliver real-time spend predictions through an interactive Streamlit dashboard.

---

##  Key Features

- Data analytics using Exploratory Data Analysis (EDA)  
- Data preprocessing and feature engineering  
- Machine learning using XGBoost regression  
- Model deployment using Streamlit  
- Real-time next 30-day spend prediction  

---

## System Architecture

Raw Data → Preprocessing → Feature Engineering → Model Training → Model Saving → Streamlit App → Prediction

---

##  Repository Roadmap

| Category | Files |
|--------|-------|
| Data Core | `final_dataset.csv`, `short_term_spend_model_data.csv` |
| Analytics | `EDA.ipynb` |
| Preprocessing | `Data Preparation.ipynb` |
| Modeling | `Models.ipynb` |
| Saved Artifacts | `xgboost_spend_model.pkl`, `feature_scaler.pkl`, `feature_columns.json` |
| Web App | `app.py` |
| Environment | `requirements.txt` |

---

##  Data Engineering

The dataset includes customer purchase behavior such as:
- Daily spend  
- Quantity  
- Average price  
- Transactions  
- Discounts  
- Demographics (age, gender, region, city, store type)

### Processing steps
- Data cleaning  
- One-hot encoding of categorical features  
- Feature scaling using StandardScaler  
- Feature alignment using feature_columns.json  

---

##  Machine Learning Model

The models are trained and evaluated in `Models.ipynb`.

We implemented and compared multiple machine learning and deep learning models:

- **Linear Regression**  
- **Random Forest Regressor**  
- **XGBoost Regressor**  
- **Recurrent Neural Network (RNN)**  
- **Long Short-Term Memory (LSTM)**  
- **Gated Recurrent Unit (GRU)**  

These models were used to learn customer spending patterns from historical transaction data.

Why these models?

- **Linear Regression** – Baseline model to understand linear relationships  
- **Random Forest** – Handles non-linearity and feature interactions  
- **XGBoost** – High performance on structured tabular data  
- **RNN** – Learns sequential patterns in customer transactions  
- **LSTM** – Captures long-term dependencies in spending behavior  
- **GRU** – Efficient alternative to LSTM for time-series modeling  

The best-performing model was selected and saved as:

The model is trained using **GRU** in `Models.ipynb`.

Why GRU?
- Works well with structured data  
- High accuracy  
- Prevents overfitting  
- Handles complex relationships
  
## Streamlit Application

File: `app.py`

The web app allows users to:
- Select customer ID  
- View profile  
- Enter today’s shopping details  
- Predict next 30-day spend  

Pipeline:
1. User inputs data  
2. One-hot encoding  
3. Feature alignment  
4. Scaling  
5. Prediction using XGBoost  


## Team
**Team Name:**  
###  AI Alchemists  
A team dedicated to transforming data into intelligent, impactful solutions using Machine Learning and AI.
---

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py

http://localhost:8501
---




