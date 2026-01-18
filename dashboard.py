
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import glob
import os

# Set Page Config - Professional Title
st.set_page_config(
    page_title="UIDAI Strategic Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Mode & Professional Fonts)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111;
        border-right: 1px solid #333;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #E0E0E0;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2D2D2D;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    
    /* Remove default Streamlit menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------
@st.cache_data
def load_data():
    if not os.path.exists("assets/tables/afi_scores.csv"):
       st.error("Data Error: 'assets/tables/afi_scores.csv' not found.")
       st.stop()
       
    afi_df = pd.read_csv("assets/tables/afi_scores.csv")
    
    # LOAD STATE MAPPING - Fix for missing 'state' column
    try:
        if 'state' not in afi_df.columns:
            enrol_files = glob.glob('data/raw/api_data_aadhar_enrolment/*.csv')
            if not enrol_files:
                enrol_files = glob.glob('../data/raw/api_data_aadhar_enrolment/*.csv')
                
            if enrol_files:
                map_dfs = []
                for f in enrol_files[:5]: 
                    tmp = pd.read_csv(f, usecols=['state', 'district'])
                    map_dfs.append(tmp.drop_duplicates())
                
                if map_dfs:
                    state_map_df = pd.concat(map_dfs).drop_duplicates(subset=['district'])
                    afi_df = afi_df.merge(state_map_df, on='district', how='left')
                    afi_df['state'] = afi_df['state'].fillna('Unknown')
            else:
                afi_df['state'] = 'Unknown'
    except Exception as e:
        afi_df['state'] = 'Unknown'
        
    return afi_df

afi_df = load_data()

# Helper to display HTML plots
def html_plot(filename, height=600):
    try:
        path = f"assets/plots/{filename}"
        if not os.path.exists(path):
             st.warning(f"Plot file not found: {filename}")
             return
             
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        st.components.v1.html(html, height=height, scrolling=True)
    except Exception as e:
        st.error(f"Error loading plot {filename}: {e}")

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("Strategic Analysis")
page = st.sidebar.radio("Navigate", [
    "Executive Summary", 
    "Friction Landscape", 
    "Demand Forecasting", 
    "Anomaly & Fraud Detection"
])

# ---------------------------------------------------------
# PAGE: EXECUTIVE SUMMARY
# ---------------------------------------------------------
if page == "Executive Summary":
    st.title("Strategic Intelligence Executive Dashboard")
    
    st.markdown('<div class="section-header">National Enrollment Trends</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Demographic Pyramid", "Enrollment Trend Analysis"])
    with tab1:
        html_plot("age_pyramid.html", height=600)
    with tab2:
        html_plot("trend_analysis.html", height=600)

# ---------------------------------------------------------
# PAGE: FRICTION LANDSCAPE
# ---------------------------------------------------------
elif page == "Friction Landscape":
    st.title("Aadhaar Friction Index (AFI)")
    
    st.markdown('<div class="section-header">Strategic Matrix & Rankings</div>', unsafe_allow_html=True)
    
    # Interactive Plotly Matrix
    if 'total_enrol' not in afi_df.columns:
        size_col = None
    else:
        size_col = 'total_enrol'
        
    fig = px.scatter(
        afi_df,
        x='avg_daily_vol',
        y='AFI',
        color='Child_Exclusion_Score',
        size=size_col,
        hover_name='district',
        hover_data=['AFI', 'Bio_Score', 'Overload_Score'],
        log_x=True,
        title='Strategic Matrix: Volume vs Friction',
        labels={'avg_daily_vol': 'Daily Volume (Log Scale)', 'AFI': 'Friction Score', 'Child_Exclusion_Score': 'Child Excl.'},
        color_continuous_scale='Turbo',
        height=650
    )
    # Add Quadrants
    avg_vol = afi_df['avg_daily_vol'].median()
    avg_friction = afi_df['AFI'].mean()
    fig.add_vline(x=avg_vol, line_width=1, line_dash="dash", line_color="grey")
    fig.add_hline(y=avg_friction, line_width=1, line_dash="dash", line_color="grey")
    fig.add_annotation(x=np.log10(avg_vol*10), y=95, text="CRITICAL ZONE", showarrow=False, font=dict(color="red"))
    
    col_main, col_detail = st.columns([2, 1])
    with col_main:
        st.plotly_chart(fig, use_container_width=True)
    with col_detail:
        st.subheader("Top Critical Districts")
        cols_to_show = ['district', 'AFI']
        if 'state' in afi_df.columns:
            cols_to_show.insert(1, 'state')
            
        st.dataframe(
            afi_df[cols_to_show].sort_values('AFI', ascending=False).head(15),
            height=600
        )

    st.markdown('<div class="section-header">Detailed Friction Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Top 20 Districts", "Service Deserts (Bubble)", "State Demographics", "Weekend Service Gap"])
    
    with tab1:
        html_plot("top_20_districts_bar.html", height=600)
    with tab2:
        html_plot("state_density_bubble.html", height=600)
    with tab3:
        html_plot("state_demographics_treemap.html", height=600)
    with tab4:
        html_plot("weekend_gap_pie.html", height=600)

# ---------------------------------------------------------
# PAGE: DEMAND FORECASTING
# ---------------------------------------------------------
elif page == "Demand Forecasting":
    st.title("Predictive Demand Modeling")
    
    st.markdown('<div class="section-header">6-Month Demand Projections</div>', unsafe_allow_html=True)
    # Using the regenerated Forecast with 95% CI
    html_plot("prophet_forecast.html", height=600)
    
    st.markdown('<div class="section-header">Model Diagnostics & Breakdowns</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "State Growth", 
        "Seasonality",
        "Predicted vs Actual",
        "Baseline Forecast (LR)",
        "Forecast Data Table",
        "Challenger Model",
        "Components", 
        "Error Dist.", 
        "Residuals", 
        "Rolling RMSE"
    ])
    
    with tab1:
        html_plot("future_projection_bar.html", height=600)
    with tab2:
        # Added Seasonality Heatmap
        html_plot("seasonality_heatmap.html", height=700)
    with tab3:
        # Added Predicted vs Actual Scatter
        html_plot("forecast_scatter.html", height=600)
    with tab4:
        # Baseline Linear Regression Forecast
        html_plot("forecast_interactive.html", height=600)
    with tab5:
        # Forecast Data Table
        html_plot("forecast_data_table.html", height=600)
    with tab6:
        # Added Challenger Forecast View
        html_plot("prophet_forecast_challenger.html", height=600)
    with tab7:
        html_plot("prophet_components.html", height=800)
    with tab8:
        html_plot("forecast_error_distribution.html", height=600)
    with tab9:
        html_plot("forecast_residuals.html", height=600)
    with tab10:
        html_plot("rolling_rmse.html", height=600)

# ---------------------------------------------------------
# PAGE: ANOMALY DETECTION
# ---------------------------------------------------------
elif page == "Anomaly & Fraud Detection":
    st.title("Ghost District Detection")
    
    st.markdown('<div class="section-header">Anomaly Identification</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        html_plot("ghost_districts_scatter.html", height=600)
    with col2:
        st.subheader("Top Anomalous Districts")
        html_plot("top_anomalies_bar.html", height=600)

    st.markdown('<div class="section-header">Fraud Pattern Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "3D Anomaly View",
        "Anomalies vs Time", 
        "Day of Week Analysis", 
        "XGBoost Feature Imp.",
        "Score Distribution",
        "Raw Anomaly Scatter"
    ])
    
    with tab1:
        st.info("Interactive 3D Visualization of Anomaly Clusters")
        html_plot("3d_anomaly_view.html", height=700)
    with tab2:
        html_plot("anomaly_magnitude_time.html", height=600)
    with tab3:
        html_plot("day_of_week_analysis.html", height=600)
    with tab4:
        html_plot("xgboost_feature_importance.html", height=600)
    with tab5:
        html_plot("anomaly_score_distribution.html", height=600)
    with tab6:
        html_plot("anomaly_scatter.html", height=600)
