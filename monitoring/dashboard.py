#!/usr/bin/env python3
"""
Streamlit Dashboard for API Monitoring
Displays real-time API usage statistics and metrics
"""
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

# Page configuration
st.set_page_config(
    page_title="Book API Monitoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
@st.cache_resource
def get_engine():
    return create_engine(settings.DATABASE_URL)

engine = get_engine()

# Title
st.title("📊 Book Recommendation API - Monitoring Dashboard")
st.markdown("Real-time API usage statistics and performance metrics")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Fetch data
@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_api_logs():
    query = """
    SELECT * FROM api_logs
    ORDER BY timestamp DESC
    LIMIT 1000
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=30)
def load_books_stats():
    query = """
    SELECT
        COUNT(*) as total_books,
        AVG(price) as avg_price,
        COUNT(DISTINCT category) as total_categories
    FROM books
    """
    return pd.read_sql(query, engine)

try:
    logs_df = load_api_logs()
    books_stats = load_books_stats()

    # Sidebar - Time filter
    st.sidebar.header("⏱️ Time Filter")
    time_options = {
        "Last Hour": 1,
        "Last 6 Hours": 6,
        "Last 24 Hours": 24,
        "Last 7 Days": 168,
        "All Time": None
    }
    selected_time = st.sidebar.selectbox("Select time range", list(time_options.keys()))

    if time_options[selected_time]:
        cutoff_time = datetime.utcnow() - timedelta(hours=time_options[selected_time])
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        filtered_logs = logs_df[logs_df['timestamp'] >= cutoff_time]
    else:
        filtered_logs = logs_df

    # === KPIs ===
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📈 Total Requests",
            value=f"{len(filtered_logs):,}",
            delta=f"+{len(filtered_logs[filtered_logs['timestamp'] >= datetime.utcnow() - timedelta(hours=1)])} last hour"
        )

    with col2:
        if len(filtered_logs) > 0:
            avg_response = filtered_logs['response_time'].mean()
            st.metric(
                label="⚡ Avg Response Time",
                value=f"{avg_response:.2f} ms",
                delta=f"P95: {filtered_logs['response_time'].quantile(0.95):.2f}ms"
            )
        else:
            st.metric(label="⚡ Avg Response Time", value="N/A")

    with col3:
        if len(filtered_logs) > 0:
            error_rate = (filtered_logs['status_code'] >= 400).sum() / len(filtered_logs) * 100
            st.metric(
                label="⚠️ Error Rate",
                value=f"{error_rate:.1f}%",
                delta=f"{(filtered_logs['status_code'] >= 400).sum()} errors"
            )
        else:
            st.metric(label="⚠️ Error Rate", value="0%")

    with col4:
        st.metric(
            label="📚 Total Books",
            value=f"{books_stats['total_books'].iloc[0]:,}",
            delta=f"{books_stats['total_categories'].iloc[0]} categories"
        )

    st.divider()

    # === Charts Row 1 ===
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Requests Over Time")
        if len(filtered_logs) > 0:
            logs_hourly = filtered_logs.copy()
            logs_hourly['hour'] = pd.to_datetime(logs_hourly['timestamp']).dt.floor('H')
            requests_per_hour = logs_hourly.groupby('hour').size().reset_index(name='count')

            fig = px.line(
                requests_per_hour,
                x='hour',
                y='count',
                title='API Requests per Hour',
                labels={'hour': 'Time', 'count': 'Number of Requests'}
            )
            fig.update_traces(line_color='#1f77b4', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected time range")

    with col2:
        st.subheader("🎯 Top Endpoints")
        if len(filtered_logs) > 0:
            endpoint_counts = filtered_logs['endpoint'].value_counts().head(10)

            fig = px.bar(
                x=endpoint_counts.values,
                y=endpoint_counts.index,
                orientation='h',
                title='Most Popular Endpoints',
                labels={'x': 'Request Count', 'y': 'Endpoint'}
            )
            fig.update_traces(marker_color='#2ca02c')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

    # === Charts Row 2 ===
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚡ Response Time Distribution")
        if len(filtered_logs) > 0:
            fig = px.histogram(
                filtered_logs,
                x='response_time',
                nbins=50,
                title='Response Time Distribution',
                labels={'response_time': 'Response Time (ms)', 'count': 'Frequency'}
            )
            fig.update_traces(marker_color='#ff7f0e')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

    with col2:
        st.subheader("📊 HTTP Status Codes")
        if len(filtered_logs) > 0:
            status_counts = filtered_logs['status_code'].value_counts()

            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title='HTTP Status Code Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

    # === Recent Requests Table ===
    st.subheader("📋 Recent API Requests")
    if len(filtered_logs) > 0:
        display_cols = ['timestamp', 'method', 'endpoint', 'status_code', 'response_time']
        recent_logs = filtered_logs[display_cols].head(20).copy()
        recent_logs['response_time'] = recent_logs['response_time'].round(2).astype(str) + ' ms'

        # Color code status codes
        def color_status(val):
            if val >= 500:
                return 'background-color: #ffcccc'
            elif val >= 400:
                return 'background-color: #ffffcc'
            elif val >= 200:
                return 'background-color: #ccffcc'
            return ''

        styled_df = recent_logs.style.applymap(color_status, subset=['status_code'])
        st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.info("No requests logged yet")

    # === Footer ===
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>📊 Dashboard auto-refreshes every 30 seconds | 🚀 Powered by Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-refresh every 30 seconds
    import time
    time.sleep(30)
    st.rerun()

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.exception(e)
