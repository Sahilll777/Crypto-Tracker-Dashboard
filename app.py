import streamlit as st
import pandas as pd
import plotly.express as px
from utils.coingecko_api import get_market_data, get_price_chart
from datetime import datetime
import time

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="Real-Time Crypto Tracker",
    layout="wide",
    
)

# ----------------------------
# Custom CSS Styling
# ----------------------------
st.markdown("""
    <style>
    /* Main title styling */
    .main-title {
        font-size: 42px !important;
        color: #00C853;
        text-align: center;
        font-weight: 800;
    }
    /* Subtitle */
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #B0BEC5;
        margin-bottom: 25px;
    }
    /* Section headers */
    .section-header {
        color: #00BFA5;
        font-size: 26px;
        font-weight: 700;
        margin-top: 25px;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1C1C1E;
    }
    /* Table customization */
    .stDataFrame {
        border-radius: 12px;
    }
    /* Card containers */
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.2);
    }
    .metric-label {
        font-size: 18px;
        color: #9E9E9E;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #00E676;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Dashboard Header
# ----------------------------
st.markdown("<h1 class='main-title'> Real-Time Cryptocurrency Tracker Dashboard</h1>", unsafe_allow_html=True) 
st.markdown("<p class='subtitle'>Monitor live crypto prices, performance, and trends in real-time — powered by CoinGecko API.</p>", unsafe_allow_html=True)

# ----------------------------
# Sidebar Settings
# ----------------------------
st.sidebar.header(" Settings") 

vs_currency = st.sidebar.selectbox("Select Currency", ["usd", "inr", "eur"], index=0)
refresh_rate = st.sidebar.slider("Auto Refresh (seconds)", 10, 120, 60)
num_coins = st.sidebar.slider("Number of Top Coins", 5, 20, 10)
selected_days = st.sidebar.selectbox("Chart Duration", ["1", "7", "30", "90"], index=0)
alert_threshold = st.sidebar.slider("Alert if 24h Change (%) >", 5, 20, 10)

st.sidebar.info(" Data Source: CoinGecko (Updated live)") 

# ----------------------------
# Fetch Data
# ----------------------------
with st.spinner("Fetching latest crypto market data..."):
    try:
        market_data = get_market_data(vs_currency=vs_currency, per_page=num_coins)
        df = pd.DataFrame(market_data)[
            ["id", "symbol", "name", "current_price", "price_change_percentage_24h", "market_cap", "total_volume"]
        ]
    except Exception as e:
        st.error(f" Error fetching data: {e}") 
        st.stop()

# ----------------------------
# KPI Summary Cards
# ----------------------------
st.markdown("<div class='section-header'> Market Summary</div>", unsafe_allow_html=True) 
avg_change = df["price_change_percentage_24h"].mean()
top_coin = df.iloc[0]["name"]
top_price = df.iloc[0]["current_price"]

col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='metric-card'><div class='metric-label'>Average 24h Change</div><div class='metric-value'>{avg_change:.2f}%</div></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><div class='metric-label'>Top Coin</div><div class='metric-value'>{top_coin}</div></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><div class='metric-label'>Price of {top_coin}</div><div class='metric-value'>{top_price:.2f} {vs_currency.upper()}</div></div>", unsafe_allow_html=True)

# ----------------------------
# Market Overview Table
# ----------------------------
st.markdown("<div class='section-header'> Market Overview</div>", unsafe_allow_html=True) 

df_display = df.rename(columns={
    "id": "Coin ID",
    "symbol": "Symbol",
    "name": "Name",
    "current_price": f"Current Price ({vs_currency.upper()})",
    "price_change_percentage_24h": "24h Change (%)",
    "market_cap": "Market Cap",
    "total_volume": "24h Volume"
})

st.dataframe(df_display.style.format({
    f"Current Price ({vs_currency.upper()})": "{:.2f}",
    "24h Change (%)": "{:.2f}",
    "Market Cap": "{:,.0f}",
    "24h Volume": "{:,.0f}"
}).background_gradient(subset=["24h Change (%)"], cmap="RdYlGn"))

# ----------------------------
# Gainers / Losers Visualization
# ----------------------------
st.markdown("<div class='section-header'> Top Gainers &  Top Losers (24h)</div>", unsafe_allow_html=True) 

col1, col2 = st.columns(2)

with col1:
    gainers = df.nlargest(5, "price_change_percentage_24h")[["name", "price_change_percentage_24h"]]
    fig_g = px.bar(gainers, x="name", y="price_change_percentage_24h", text_auto=".2f",
                   color="price_change_percentage_24h", color_continuous_scale="Greens")
    fig_g.update_layout(title=" Top 5 Gainers (24h)", title_x=0.3, xaxis_title="Coin", yaxis_title="% Change") 
    st.plotly_chart(fig_g, use_container_width=True)

with col2:
    losers = df.nsmallest(5, "price_change_percentage_24h")[["name", "price_change_percentage_24h"]]
    fig_l = px.bar(losers, x="name", y="price_change_percentage_24h", text_auto=".2f",
                   color="price_change_percentage_24h", color_continuous_scale="Reds")
    fig_l.update_layout(title=" Top 5 Losers (24h)", title_x=0.3, xaxis_title="Coin", yaxis_title="% Change") 
    st.plotly_chart(fig_l, use_container_width=True)

# ----------------------------
# Individual Coin Trend
# ----------------------------
st.markdown("<div class='section-header'>Individual Coin Price Trend</div>", unsafe_allow_html=True) 

coin_choice = st.selectbox("Select a Coin", df["id"].tolist(), index=0)
chart_data = get_price_chart(coin_choice, vs_currency, days=int(selected_days))

fig = px.line(
    chart_data, x="timestamp", y="price",
    title=f"{coin_choice.capitalize()} Price Over Last {selected_days} Days",
    labels={"timestamp": "Time", "price": f"Price ({vs_currency.upper()})"},
    template="plotly_dark"
)
fig.update_traces(line=dict(width=3, color="#00E5FF"))
fig.update_layout(title_x=0.3, hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Alerts Section
# ----------------------------
alerts = df[df["price_change_percentage_24h"] > alert_threshold]
if not alerts.empty:
    st.markdown("<div class='section-header'> Price Surge Alerts</div>", unsafe_allow_html=True) 
    st.warning("Some coins exceeded the alert threshold:")
    st.dataframe(alerts[["name", "price_change_percentage_24h"]])

# ----------------------------
# Auto-Refresh
# ----------------------------
st.sidebar.markdown("---")
st.sidebar.write(f" Dashboard auto-refreshes every **{refresh_rate} seconds**") 

progress = st.sidebar.progress(0)
for i in range(refresh_rate):
    time.sleep(1)
    progress.progress((i + 1) / refresh_rate)
st.rerun()
