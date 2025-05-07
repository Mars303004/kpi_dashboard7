# File: kpi_dashboard.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_extras.grid import grid
import os

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="KPI Dashboard")

# ========== CUSTOM STYLING ==========
st.markdown("""
    <style>
        .highlight-box {
            background-color: rgba(255, 0, 0, 0.05);
            border-left: 5px solid red;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
        }
        .spark-box {
            margin-bottom: 1rem;
        }
        .block-title {
            font-weight: bold;
            font-size: 18px;
            color: #0f098e;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📈 KPI Dashboard")

# ========== LOAD DATA ==========
file_path = "Dashboard 7.csv"
if not os.path.exists(file_path):
    st.error(f"File `{file_path}` tidak ditemukan.")
    st.stop()

try:
    df = pd.read_csv(file_path)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

# ========== UI FILTER ==========
perspectives = df["Perspective"].dropna().unique().tolist()
selected_perspective = st.selectbox("🎯 Pilih Perspective", perspectives)

# ========== FILTER DATA ==========
filtered_df = df[df['Perspective'] == selected_perspective]

# ========== KPI SUMMARY ==========
st.markdown("### 📊 Ringkasan KPI")

summary_grid = grid(2, [1, 1], gap="1rem")
with summary_grid.container():
    st.markdown("**✅ Top 5 Best KPI**")
    best = df.sort_values("%Achv", ascending=False).head(5)
    st.dataframe(best[["KPI", "%Achv"]], use_container_width=True, hide_index=True)

with summary_grid.container():
    st.markdown("**❌ Top 5 Worst KPI**")
    worst = df.sort_values("%Achv", ascending=True).head(5)
    st.dataframe(worst[["KPI", "%Achv"]], use_container_width=True, hide_index=True)

# ========== KPI DETAIL ==========
st.markdown(f"### 📋 Daftar KPI - Perspective: {selected_perspective}")

kpi_grid = grid(len(filtered_df), [3, 1], gap="0.5rem")

for i, row in filtered_df.iterrows():
    with kpi_grid.container():
        st.markdown(f"""
            <div class="highlight-box">
                <div class="block-title">{row['KPI']}</div>
                🎯 Target bulan ini: <strong>{row['Target Feb']}</strong><br>
                📈 Aktual bulan ini: <strong>{row['Actual Feb']}</strong><br>
                📉 Aktual bulan lalu: <strong>{row['Actual Jan']}</strong>
            </div>
        """, unsafe_allow_html=True)

    with kpi_grid.container():
        sparkline = go.Figure()
        sparkline.add_trace(go.Scatter(
            x=["Jan", "Feb"],
            y=[row['Actual Jan'], row['Actual Feb']],
            mode="lines+markers",
            line=dict(color="#b42020"),
            marker=dict(size=6),
            showlegend=False
        ))
        sparkline.update_layout(
            height=100,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, visible=False),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(sparkline, use_container_width=True)
