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