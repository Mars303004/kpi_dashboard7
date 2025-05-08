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
        # Use row[1] to reliably get 'Kode KPI'
        if cols_buttons[j].button(f"Show Chart {row[1]}", key=f"btn_{row[1]}"):
            selected_kpi_code = row[1]

if selected_kpi_code:
    kpi_row = filtered_df[filtered_df['Kode KPI'] == selected_kpi_code].iloc[0]
    actual_feb = kpi_row['Actual Feb']
    if pd.isna(actual_feb) or str(actual_feb).strip().upper() == 'NA':
        st.info("Belum ada data yang tersedia untuk KPI ini.")
    else:
        target_tahunan = kpi_row['Target Tahunan']
        x_data = [col for col in df.columns if col.startswith('Actual')]
        y_data = kpi_row[x_data].values.tolist()
        x_clean = [col.replace('Actual ', '') for col in x_data]

        fig_detail = go.Figure()

        # Add Target Feb line if Measurement Type is SUM and Target Feb is valid
        if kpi_row['Measurement Type'] == 'SUM':
            target_feb = kpi_row['Target Feb']
            if pd.notna(target_feb):
                target_feb_line = go.Scatter(
                    x=x_clean,
                    y=[target_feb] * len(x_clean),
                    mode='lines',
                    name='Target Feb',
                    line=dict(color='blue', dash='dash')
                )
                fig_detail.add_trace(target_feb_line)

        # Add Target Tahunan line (annual target)
        target_line = go.Scatter(
            x=x_clean,
            y=[target_tahunan] * len(x_clean),
            mode='lines',
            name='Target Tahunan',
            line=dict(color='green', dash='dash')
        )
        fig_detail.add_trace(target_line)

        # Add actual performance line
        actual_line = go.Scatter(
            x=x_clean,
            y=y_data,
            mode='lines+markers',
            name='Kinerja Bulanan',
            line=dict(color='#0f098e')
        )
        fig_detail.add_trace(actual_line)

        fig_detail.update_layout(
            xaxis_title='Bulan',
            yaxis_title='Nilai',
            height=400
        )

        st.plotly_chart(fig_detail, use_container_width=True)
 

# ========== TAMBAHAN: LIST KPI STATUS HITAM ==========
st.markdown("## 📌 Daftar KPI dengan Status Hitam (Data tidak lengkap)")
df_hitam = df[df['Status'] == 'Hitam'][['Kode KPI', 'KPI']]

if df_hitam.empty:
    st.info("Tidak ada KPI dengan status Hitam.")
else:
    st.dataframe(df_hitam.reset_index(drop=True), use_container_width=True)
