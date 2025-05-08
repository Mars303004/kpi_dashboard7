# pip install streamlit plotly pandas

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ===== CONFIG =====
st.set_page_config(layout="wide", page_title="KPI Dashboard")

# ===== LOAD DATA =====
file_path = "Dashboard 7.csv"
df = pd.read_csv(file_path)

required_cols = ['Perspective', 'Kode KPI', 'KPI', 'Target Tahunan', 'Measurement Type',
                 'Target Jan', 'Actual Jan', 'Achv Jan', 'Target Feb', 'Actual Feb', 'Achv Feb']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan di data.")
        st.stop()

df['Achv Feb Num'] = pd.to_numeric(df['Achv Feb'].str.replace('%', '').str.replace(',', '.'), errors='coerce')

def get_status(achv):
    if pd.isna(achv):
        return 'Hitam'
    elif achv < 70:
        return 'Merah'
    elif 70 <= achv <= 99:
        return 'Kuning'
    else:
        return 'Hijau'

df['Status'] = df['Achv Feb Num'].apply(get_status)

# ===== COLORS =====
COLOR_RED = "#b42020"
COLOR_YELLOW = "#ffe600"
COLOR_GREEN = "#1bb934"
COLOR_BLACK = "#222222"
COLOR_BLUE = "#0f098e"
COLOR_WHITE = "#ffffff"

status_color_map = {
    "Merah": COLOR_RED,
    "Kuning": COLOR_YELLOW,
    "Hijau": COLOR_GREEN,
    "Hitam": COLOR_BLACK
}
status_order = ['Merah', 'Kuning', 'Hijau', 'Hitam']

# ===== COUNT PER STATUS =====
def get_status_counts(data):
    return {status: (data['Status'] == status).sum() for status in status_order}

global_counts = get_status_counts(df)

fig_global = go.Figure()
for status in status_order:
    fig_global.add_trace(go.Bar(
        x=[status],
        y=[global_counts[status]],
        name=status,
        marker_color=status_color_map[status],
        text=[global_counts[status]],
        textposition='auto'
    ))
fig_global.update_layout(
    title="Total KPI Status (Global)",
    barmode='stack',
    plot_bgcolor=COLOR_WHITE,
    paper_bgcolor=COLOR_WHITE,
    font=dict(color=COLOR_BLUE, size=16),
    height=350
)

# ===== PER PERSPECTIVE =====
perspectives = df['Perspective'].dropna().unique().tolist()
perspective_counts = {p: get_status_counts(df[df['Perspective'] == p]) for p in perspectives}

fig_persp = go.Figure()
for status in status_order:
    fig_persp.add_trace(go.Bar(
        x=perspectives,
        y=[perspective_counts[p][status] for p in perspectives],
        name=status,
        marker_color=status_color_map[status],
        text=[perspective_counts[p][status] for p in perspectives],
        textposition='auto'
    ))
fig_persp.update_layout(
    title="KPI Status per Perspective",
    barmode='stack',
    plot_bgcolor=COLOR_WHITE,
    paper_bgcolor=COLOR_WHITE,
    font=dict(color=COLOR_BLUE, size=16),
    height=400
)

# ===== DISPLAY CHARTS =====
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_global, use_container_width=True)
with col2:
    st.plotly_chart(fig_persp, use_container_width=True)

# ===== FILTER PER STATUS =====
st.subheader("Filter Berdasarkan Warna Status:")
selected_status = st.selectbox("Pilih status warna:", status_order)

filtered_by_status = df[df['Status'] == selected_status]
st.dataframe(filtered_by_status[['Kode KPI', 'KPI', 'Status']])

# ===== FILTER PERSPECTIVE =====
st.subheader("Filter Berdasarkan Perspective:")
selected_perspective = st.selectbox("Pilih Perspective:", perspectives)
filtered_df = df[df['Perspective'] == selected_perspective]

# ===== TREND INSIGHT & TABEL =====
def generate_trend_insight(row):
    actual_cols = [col for col in df.columns if col.startswith("Actual")]
    actuals = pd.to_numeric(row[actual_cols].replace('NA', None), errors='coerce').tolist()
    recent_values = [v for v in actuals if pd.notna(v)][-3:]
    if len(recent_values) >= 2:
        if all(x > y for x, y in zip(recent_values[1:], recent_values[:-1])):
            return "📈 Naik 2 bulan"
        elif all(x < y for x, y in zip(recent_values[1:], recent_values[:-1])):
            return "📉 Turun 2 bulan"
        elif recent_values[-1] > row['Target Tahunan']:
            return "✅ Di atas target"
    return ""

filtered_df['Trend Insight'] = filtered_df.apply(generate_trend_insight, axis=1)

def style_row(row):
    color = status_color_map.get(row['Status'], "")
    font_color = 'black' if row['Status'] == 'Kuning' else 'white'
    return [f'background-color: {color}; color: {font_color};'] * len(row)

display_cols = ['Kode KPI', 'KPI', 'Target Tahunan', 'Actual Jan', 'Actual Feb', 'Measurement Type', 'Status', 'Trend Insight']
st.dataframe(filtered_df[display_cols].style.apply(style_row, axis=1), use_container_width=True)
