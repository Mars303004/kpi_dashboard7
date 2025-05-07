import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit.components.v1 import html

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="KPI Dashboard")

# ========== LOAD DATA ==========
file_path = "Dashboard 7.csv"
df = pd.read_csv(file_path)

# ========== DATA PREPARATION ==========
required_cols = ['Perspective', 'Kode KPI', 'KPI', 'Target Tahunan', 'Measurement Type',
                 'Target Jan', 'Actual Jan', 'Achv Jan', 'Target Feb', 'Actual Feb', 'Achv Feb']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan di data.")
        st.stop()

df['Achv Feb Num'] = pd.to_numeric(df['Achv Feb'].str.replace('%','').str.replace(',','.'), errors='coerce')

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

# ========== WARNA ==========
COLOR_RED = "#b42020"
COLOR_BLUE = "#0f098e"
COLOR_WHITE = "#ffffff"
COLOR_GREEN = "#1bb934"
COLOR_YELLOW = "#ffe600"
COLOR_BLACK = "#222222"

status_color_map = {
    "Merah": COLOR_RED,
    "Kuning": COLOR_YELLOW,
    "Hijau": COLOR_GREEN,
    "Hitam": COLOR_BLACK
}

status_order = ['Hitam', 'Hijau', 'Kuning', 'Merah']

# ========== CHART TRAFFIC LIGHT GLOBAL ==========
def get_status_counts(data):
    return {
        "Merah": (data['Status'] == "Merah").sum(),
        "Kuning": (data['Status'] == "Kuning").sum(),
        "Hijau": (data['Status'] == "Hijau").sum(),
        "Hitam": (data['Status'] == "Hitam").sum()
    }

global_counts = get_status_counts(df)

fig_global = go.Figure()
for status in reversed(status_order):
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
    yaxis_title="Jumlah KPI",
    xaxis_title="Status",
    barmode='stack',
    plot_bgcolor=COLOR_WHITE,
    paper_bgcolor=COLOR_WHITE,
    font=dict(color=COLOR_BLUE, size=16),
    margin=dict(l=20, r=20, t=40, b=20),
    height=350
)

# ========== CHART TRAFFIC LIGHT PER PERSPECTIVE ==========
perspectives = df['Perspective'].dropna().unique().tolist()
perspective_counts = {p: get_status_counts(df[df['Perspective'] == p]) for p in perspectives}

fig_persp = go.Figure()
for status in reversed(status_order):
    fig_persp.add_trace(go.Bar(
        x=perspectives,
        y=[perspective_counts[p][status] for p in perspectives],
        name=status,
        marker_color=status_color_map[status],
        text=[perspective_counts[p][status] for p in perspectives],
        textposition='auto'
    ))
fig_persp.update_layout(
    barmode='stack',
    title="KPI Status per Perspective",
    yaxis_title="Jumlah KPI",
    xaxis_title="Perspective",
    plot_bgcolor=COLOR_WHITE,
    paper_bgcolor=COLOR_WHITE,
    font=dict(color=COLOR_BLUE, size=16),
    margin=dict(l=20, r=20, t=40, b=20),
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# ========== DISPLAY CHARTS ==========
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_global, use_container_width=True)
with col2:
    st.plotly_chart(fig_persp, use_container_width=True)

# ========== FILTER PERSPECTIVE (TOMBOL 2x2) ==========
html_buttons = """
<style>
.container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
}
.button-persp {
    width: 48%;
    height: 80px;
    margin-bottom: 15px;
    font-size: 24px;
    font-weight: bold;
    color: white;
    border: none;
    border-radius: 20px;
    background-color: #0f098e;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
    cursor: pointer;
    transition: transform 0.1s ease;
}
.button-persp:hover {
    transform: scale(1.02);
}
</style>
<div class="container">
"""

for p in perspectives:
    html_buttons += f"""
    <form action="" method="post">
        <button class="button-persp" name="selected_persp" type="submit" value="{p}">{p}</button>
    </form>
    """

html_buttons += "</div>"

selected = st.experimental_get_query_params().get("selected_persp", [None])[0]
if selected:
    st.session_state.selected_persp = selected
elif 'selected_persp' not in st.session_state:
    st.session_state.selected_persp = perspectives[0]

html(html_buttons, height=220)
selected_perspective = st.session_state.selected_persp

# ========== FILTER DATA BERDASARKAN PERSPECTIVE ==========
filtered_df = df[df['Perspective'] == selected_perspective]

# ========== TABEL KPI DENGAN CONDITIONAL FORMATTING ==========
st.markdown(f"<h3 style='color:#b42020;'>Daftar KPI untuk Perspective: {selected_perspective}</h3>", unsafe_allow_html=True)

def style_row(row):
    if row['Status'] == 'Merah':
        return ['background-color: #b42020; color: white;'] * len(row)
    elif row['Status'] == 'Kuning':
        return ['background-color: #ffe600; color: black;'] * len(row)
    elif row['Status'] == 'Hijau':
        return ['background-color: #1bb934; color: white;'] * len(row)
    elif row['Status'] == 'Hitam':
        return ['background-color: #222222; color: white;'] * len(row)
    else:
        return [''] * len(row)

display_cols = ['Kode KPI', 'KPI', 'Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb', 'Measurement Type', 'Status']
table_df = filtered_df[display_cols].copy()

st.dataframe(table_df.style.apply(style_row, axis=1), use_container_width=True)

# ========== SHOW CHART PER KPI ==========
st.markdown("<h3 style='color:#b42020;'>Pilih KPI untuk lihat detail chart:</h3>", unsafe_allow_html=True)

selected_kpi_code = None
cols_per_row = 4

for i in range(0, len(table_df), cols_per_row):
    cols_buttons = st.columns(cols_per_row)
    for j, row in enumerate(table_df.iloc[i:i+cols_per_row].itertuples()):
        if cols_buttons[j].button(f"Show Chart {row._1}", key=f"btn_{row._1}"):
            selected_kpi_code = row._1

if selected_kpi_code:
    kpi_data = filtered_df[filtered_df['Kode KPI'] == selected_kpi_code].iloc[0]
    actual_cols = [col for col in df.columns if col.startswith("Actual ")]
    months = [col.replace("Actual ", "") for col in actual_cols]
    actual_values = [kpi_data[col] for col in actual_cols]

    target_value = kpi_data["Target Tahunan"]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=months,
        y=[target_value] * len(months),
        mode='lines',
        name='Target Tahunan',
        line=dict(color='green', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=months,
        y=actual_values,
        mode='lines+markers',
        name='Kinerja Bulanan',
        line=dict(color='#0f098e')
    ))

    fig.update_layout(
        xaxis_title='Bulan',
        yaxis_title='Nilai',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
