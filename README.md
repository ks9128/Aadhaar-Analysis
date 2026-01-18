# Adhar Analysis

This project implements a prescriptive analytics framework for Aadhaar enrollment and update operations. It provides 6-month demand forecasting, anomaly detection for fraud prevention, and friction indexing to measure resident experience.

## Structure

- **notebooks/**: Core analysis logic.
    - `01_friction_index.ipynb`: Generates Aadhaar Friction Index (AFI).
    - `02_anomaly_detect.ipynb`: Identifies ghost districts using Isolation Forest.
    - `03_forecasting.ipynb`: Predicts demand using Prophet and Linear Regression.
    - `04_demographics.ipynb`: Demographic and geospatial analysis.
    - `05_deserts.ipynb`: Geospatial mapping of service deserts and mobile unit allocation.
- **dashboard.py**: Interactive Streamlit application for visualizing results.
- **assets/**: Generated plots and HTML visualizations.
- **data/**: Processed and raw datasets.

## Setup & Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Dashboard:
   ```bash
   streamlit run dashboard.py
   ```

3. Generate Reports:
   Run the notebooks in sequence (01 to 04) to regenerate analysis assets.
