import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_extras.grid import grid
import base64

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="KPI Dashboard")

# ========== CUSTOM STYLING ==========
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
        }
        .main {
            color: #0f098e;
            font-family: Arial, sans-serif;
        }
        .highlight-red {
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 5px solid red;
            padding: 10px;
            border-radius: 8px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px red; }
            100% { box-shadow: 0 0 20px red; }
        }
        .block-box {
            background-color: #f9f9f9;
            padding: 1rem;
            border-radius: 10px;
            border-left: 5px solid #0f098e;
            margin-bottom: 1rem;
        }
        .button-box {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .button-box div {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #0f098e;
            color: white;
            font-size: 18px;
            padding: 1rem;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
        }
        .button-box div:hover {
            background-color: #b42020;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📈 KPI Dashboard")

# ========== UI FILTER ==========
# Dropdown as button-like grid
perspective_options = ["FIN", "CM", "IP", "LG"]
st.markdown("### 🎯 Pilih Perspective:")
col1, col2 = st.columns([1, 1])

with col1:
    selected_perspective = st.selectbox("Pilih Perspective", perspective_options, index=2)

# ========== LOAD DATA ==========
excel_file = "Dashboard 7.csv"  # Pastikan path file yang benar
df = pd.read_excel(excel_file, sheet_name="Dashboard 7")  # Perbaiki nama sheet

# Mapping warna
status_mapping = {
    "Merah": "🔴 Merah",
    "Kuning": "🟡 Kuning",
    "Hijau": "🟢 Hijau",
    "Hitam": "⚫ Hitam"
}

# ========== FILTER DATA ==========
filtered_df = df[df['Perspective'] == selected_perspective]

# ========== KPI SUMMARY ==========
st.subheader("📊 KPI Summary")

with st.container():
    g = grid(2, [1, 1], gap="1rem")
    
    with g.container():
        st.markdown("### ❌ Top 5 Worst KPI")
        worst = df.sort_values("%Achv", ascending=True).head(5)
        st.dataframe(worst[["KPI", "%Achv"]], use_container_width=True)

    with g.container():
        st.markdown("### ✅ Top 5 Best KPI")
        best = df.sort_values("%Achv", ascending=False).head(5)
        st.dataframe(best[["KPI", "%Achv"]], use_container_width=True)

# ========== KPI DETAILS ==========
st.subheader(f"📋 Daftar KPI untuk Perspective {selected_perspective}")

for i, row in filtered_df.iterrows():
    with st.container():
        g = grid(2, [3, 1], gap="0.5rem")

        with g.container():
            st.markdown(f"""
                <div class="highlight-red">
                    <strong>{row['KPI']}</strong><br>
                    🎯 Target bulan ini: {row['Target Feb']}<br>
                    📈 Aktual bulan ini: {row['Actual Feb']}<br>
                    📉 Aktual bulan lalu: {row['Actual Jan']}
                </div>
            """, unsafe_allow_html=True)

        with g.container():
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
