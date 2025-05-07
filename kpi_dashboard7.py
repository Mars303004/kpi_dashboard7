import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="KPI Dashboard")

# ========== LOAD DATA ==========
file_path = "Dashboard 7.csv"
df = pd.read_csv(file_path)

# ========== DATA PREPARATION ==========
# Pastikan kolom penting ada
required_cols = ['Perspective', 'Kode KPI', 'KPI', 'Target Tahunan', 'Measurement Type',
                 'Target Jan', 'Actual Jan', 'Achv Jan', 'Target Feb', 'Actual Feb', 'Achv Feb']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan di data.")
        st.stop()

# Konversi Achv Feb ke numerik, N/A jadi NaN
df['Achv Feb Num'] = pd.to_numeric(df['Achv Feb'].str.replace('%','').str.replace(',','.'), errors='coerce')

def get_status(achv):
    if pd.isna(achv):
        return 'Hitam'
    elif achv > 99:
        return 'Hijau'
    elif 70 <= achv <= 99:
        return 'Kuning'
    elif achv < 70:
        return 'Merah'
    return 'Hitam'

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

# ========== CHART TRAFFIC LIGHT GLOBAL ==========
def get_status_counts(data):
    return {
        "Merah": (data['Status'] == "Merah").sum(),
        "Kuning": (data['Status'] == "Kuning").sum(),
        "Hijau": (data['Status'] == "Hijau").sum(),
        "Hitam": (data['Status'] == "Hitam").sum()
    }

global_counts = get_status_counts(df)

fig_global = go.Figure(data=[
    go.Bar(
        x=list(global_counts.keys()),
        y=list(global_counts.values()),
        marker_color=[COLOR_RED, COLOR_YELLOW, COLOR_GREEN, COLOR_BLACK],
        text=list(global_counts.values()),
        textposition='auto'
    )
])
fig_global.update_layout(
    title="Total KPI Status (Global)",
    plot_bgcolor=COLOR_WHITE,
    paper_bgcolor=COLOR_WHITE,
    font=dict(color=COLOR_BLUE, size=16),
    margin=dict(l=20, r=20, t=40, b=20)
)

# ========== CHART TRAFFIC LIGHT PER PERSPECTIVE ==========
perspectives = df['Perspective'].dropna().unique().tolist()
perspective_counts = {p: get_status_counts(df[df['Perspective'] == p]) for p in perspectives}

fig_persp = go.Figure()
for status, color in status_color_map.items():
    fig_persp.add_trace(go.Bar(
        x=perspectives,
        y=[perspective_counts[p][status] for p in perspectives],
        name=status,
        marker_color=color
    ))
fig_persp.update_layout(
    barmode='stack',
    title="KPI Status per Perspective",
    plot_bgcolor=COLOR_WHITE,
    paper_bgcolor=COLOR_WHITE,
    font=dict(color=COLOR_BLUE, size=16),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# ========== LAYOUT ATAS: CHART SAMPINGAN ==========
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_global, use_container_width=True)
with col2:
    st.plotly_chart(fig_persp, use_container_width=True)

# ========== FILTER PERSPECTIVE (SINGLE SELECT, TOMBOL BESAR 2x2) ==========
st.markdown(f"<h2 style='color:{COLOR_RED};margin-top:0.5em;'>Filter Perspective</h2>", unsafe_allow_html=True)
persp_options = perspectives
selected_persp = st.radio(
    "Pilih Perspective (klik salah satu):",
    options=persp_options,
    index=0,
    format_func=lambda x: x,
    horizontal=False,
    key="persp_radio"
)

# Custom tombol besar 2x2
st.markdown(
    """
    <style>
    div[role="radiogroup"] > label {
        display: inline-block;
        width: 180px;
        height: 80px;
        margin: 10px 20px 10px 0;
        background: #0f098e;
        color: #fff !important;
        font-size: 1.5em;
        font-weight: bold;
        border-radius: 16px;
        text-align: center;
        line-height: 80px;
        cursor: pointer;
        border: 3px solid #b42020;
        transition: 0.2s;
    }
    div[role="radiogroup"] > label[data-selected="true"] {
        background: #b42020 !important;
        color: #fff !important;
        border: 3px solid #0f098e;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ========== FILTER DATA KPI ==========
filtered_df = df[df['Perspective'] == selected_persp].reset_index(drop=True)

# ========== TABEL KPI (HTML) ==========
st.markdown(f"<h2 style='color:{COLOR_RED};margin-top:1em;'>Daftar KPI untuk Perspective: {selected_persp}</h2>", unsafe_allow_html=True)
st.write("Klik tombol 'Show Chart' di sebelah kanan untuk melihat detail KPI.")

def row_html(row, idx):
    status = row['Status']
    bg = status_color_map.get(status, COLOR_WHITE)
    font = COLOR_WHITE if status == "Merah" else COLOR_BLUE
    return f"""
    <tr style="background-color:{bg};color:{font};font-size:1.1em;">
        <td style="padding:8px;">{row['Kode KPI']}</td>
        <td style="padding:8px;">{row['KPI']}</td>
        <td style="padding:8px;text-align:right;">{row['Target Tahunan']}</td>
        <td style="padding:8px;text-align:right;">{row['Actual Jan']}</td>
        <td style="padding:8px;text-align:right;">{row['Target Feb']}</td>
        <td style="padding:8px;text-align:right;">{row['Actual Feb']}</td>
        <td style="padding:8px;">{row['Measurement Type']}</td>
        <td style="padding:8px;text-align:center;">
            <form action="" method="post">
                <button name="show_chart" value="{idx}" style="background:{COLOR_BLUE};color:#fff;font-size:1em;padding:8px 18px;border:none;border-radius:8px;cursor:pointer;">Show Chart</button>
            </form>
        </td>
    </tr>
    """

table_html = f"""
<table style="width:100%;border-collapse:collapse;margin-top:1em;">
    <thead>
        <tr style="background-color:{COLOR_BLUE};color:#fff;font-size:1.2em;">
            <th style="padding:8px;">Kode KPI</th>
            <th style="padding:8px;">KPI</th>
            <th style="padding:8px;">Target Tahunan</th>
            <th style="padding:8px;">Actual Jan</th>
            <th style="padding:8px;">Target Feb</th>
            <th style="padding:8px;">Actual Feb</th>
            <th style="padding:8px;">Measurement Type</th>
            <th style="padding:8px;">Aksi</th>
        </tr>
    </thead>
    <tbody>
"""
for idx, row in filtered_df.iterrows():
    table_html += row_html(row, idx)
table_html += "</tbody></table>"

st.markdown(table_html, unsafe_allow_html=True)

# ========== SHOW CHART (LINE CHART) ==========
# Tangkap tombol Show Chart
show_chart_idx = st.session_state.get("show_chart_idx", None)
for idx in range(len(filtered_df)):
    if st.form_submit_button(f"Show Chart {idx}"):
        st.session_state["show_chart_idx"] = idx
        show_chart_idx = idx

if show_chart_idx is not None and show_chart_idx < len(filtered_df):
    kpi = filtered_df.iloc[show_chart_idx]
    st.markdown(f"<h3 style='color:{COLOR_BLUE};margin-top:1em;'>Detail KPI: {kpi['Kode KPI']} - {kpi['KPI']}</h3>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=['Target Jan', 'Actual Jan', 'Target Feb', 'Actual Feb'],
        y=[
            float(kpi['Target Jan']) if pd.notna(kpi['Target Jan']) else None,
            float(kpi['Actual Jan']) if pd.notna(kpi['Actual Jan']) else None,
            float(kpi['Target Feb']) if pd.notna(kpi['Target Feb']) else None,
            float(kpi['Actual Feb']) if pd.notna(kpi['Actual Feb']) else None
        ],
        mode='lines+markers',
        line=dict(color=COLOR_BLUE, width=4),
        marker=dict(size=12, color=COLOR_RED)
    ))
    fig.update_layout(
        yaxis_title='Nilai',
        xaxis_title='Bulan',
        plot_bgcolor=COLOR_WHITE,
        paper_bgcolor=COLOR_WHITE,
        font=dict(color=COLOR_BLUE, size=16),
        height=500,
        width=800
    )
    st.plotly_chart(fig, use_container_width=False)
