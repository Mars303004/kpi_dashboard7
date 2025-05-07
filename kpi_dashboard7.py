import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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

# Urutan status (Merah paling atas, Hitam paling bawah)
status_order = ['Merah', 'Kuning', 'Hijau', 'Hitam']

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
st.markdown("<h3 style='color:#b42020;'>Filter Perspective (klik salah satu):</h3>", unsafe_allow_html=True)

# CSS styling tombol besar
st.markdown("""
<style>
button.persp-btn {
    width: 100%;
    height: 80px;
    font-size: 1.5rem;
    color: white;
    background-color: #0f098e;
    border-radius: 12px;
    border: 2px solid #b42020;
    margin-bottom: 12px;
    cursor: pointer;
}
button.persp-btn:hover {
    background-color: #b42020;
}
</style>
""", unsafe_allow_html=True)

cols = st.columns(2)

if 'selected_persp' not in st.session_state:
    st.session_state.selected_persp = perspectives[0]

def select_persp(p):
    st.session_state.selected_persp = p

for i, p in enumerate(perspectives):
    col = cols[i % 2]
    is_selected = (st.session_state.selected_persp == p)
    btn_label = f"✔ {p}" if is_selected else p
    if col.button(btn_label, key=p, on_click=select_persp, args=(p,), kwargs=None):
        pass

selected_perspective = st.session_state.selected_persp

# ========== FILTER DATA BERDASARKAN PERSPECTIVE ==========
filtered_df = df[df['Perspective'] == selected_perspective]

# ========== FORMAT ANGKA DI TABEL ==========
# Batasi angka desimal pada kolom numerik
def format_numeric_columns(df_in):
    df_out = df_in.copy()
    for col in ['Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb']:
        if col in df_out.columns:
            df_out[col] = pd.to_numeric(df_out[col], errors='coerce').round(2)
    return df_out

table_df = format_numeric_columns(filtered_df[[
    'Kode KPI', 'KPI', 'Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb', 'Measurement Type', 'Status'
]]).copy()

# ========== TABEL KPI DENGAN CONDITIONAL FORMATTING ==========
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

st.markdown(f"<h3 style='color:#b42020;'>Daftar KPI untuk Perspective: {selected_perspective}</h3>", unsafe_allow_html=True)
st.dataframe(table_df.style.apply(style_row, axis=1), use_container_width=True)

# ========== SHOW CHART PER KPI ==========
st.markdown("<h3 style='color:#b42020;'>Pilih KPI untuk lihat detail chart:</h3>", unsafe_allow_html=True)

selected_kpi_code = None
cols_per_row = 4

for i in range(0, len(table_df), cols_per_row):
    cols_buttons = st.columns(cols_per_row)
    for j, row in enumerate(table_df.iloc[i:i+cols_per_row].itertuples()):
        if cols_buttons[j].button(f"Show Chart {row.Kode_KPI}", key=f"btn_{row.Kode_KPI}"):
            selected_kpi_code = row.Kode_KPI

if selected_kpi_code:
    kpi_row = filtered_df[filtered_df['Kode KPI'] == selected_kpi_code].iloc[0]
    actual_feb = kpi_row['Actual Feb']
    if pd.isna(actual_feb) or str(actual_feb).strip().upper() == 'NA':
        st.info("Belum ada data yang tersedia untuk KPI ini.")
    else:
        fig_detail = go.Figure()

        # Siapkan data bulan
        x_data = ['Jan', 'Feb']
        y_data = [kpi_row['Actual Jan'], kpi_row['Actual Feb']]

        # Garis target tahunan
        target_tahunan = kpi_row['Target Tahunan']
        target_line = go.Scatter(
            x=x_data,
            y=[target_tahunan] * len(x_data),
            mode='lines',
            name='Target Tahunan',
            line=dict(color='green', dash='dash')
        )

        # Garis aktual bulanan
        actual_line = go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name='Kinerja Bulanan',
            line=dict(color='#0f098e')
        )

        fig_detail.add_traces([target_line, actual_line])
        fig_detail.update_layout(
            xaxis_title='Bulan',
            yaxis_title='Nilai',
            xaxis=dict(showticklabels=True),
            height=400,
            plot_bgcolor='white'
        )
        st.plotly_chart(fig_detail, use_container_width=True)
