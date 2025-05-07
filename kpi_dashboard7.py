import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="Dashboard KPI")

# ========== LOAD DATA ==========
file_path = "Dashboard 7.csv"
df = pd.read_csv(file_path)

# ========== PREPROCESSING ==========
# Konversi Achv Feb ke numeric, biarkan error jadi NaN (untuk N/A)
df['Achv Feb Numeric'] = pd.to_numeric(df['Achv Feb'], errors='coerce')

# Fungsi status warna sesuai Achv Feb Numeric, NaN = Hitam
def get_status_color(achv):
    if pd.isna(achv):
        return 'Hitam'
    elif achv < 70:
        return 'Merah'
    elif 70 <= achv <= 99:
        return 'Kuning'
    elif achv > 99:
        return 'Hijau'
    else:
        return 'Hitam'

df['Status'] = df['Achv Feb Numeric'].apply(get_status_color)

# Urutan status dan warna
status_order = ['Merah', 'Kuning', 'Hijau', 'Hitam']
status_colors = {'Merah':'#d62728', 'Kuning':'#ffbb33', 'Hijau':'#2ca02c', 'Hitam':'#000000'}

# Hitung jumlah KPI per status global
global_status_counts = df['Status'].value_counts().reindex(status_order, fill_value=0)

# Hitung jumlah KPI per status per perspective
perspective_status_counts = df.groupby(['Perspective', 'Status']).size().unstack(fill_value=0).reindex(columns=status_order, fill_value=0)

# ========== CHART TRAFFIC LIGHT GLOBAL ==========
fig_global = go.Figure()
for status in status_order:
    fig_global.add_trace(go.Bar(
        x=[status],
        y=[global_status_counts[status]],
        name=status,
        marker_color=status_colors[status],
        text=[global_status_counts[status]],
        textposition='auto'
    ))
fig_global.update_layout(
    title="Total KPI Status (Global)",
    yaxis_title="Jumlah KPI",
    xaxis_title="Status",
    showlegend=False,
    plot_bgcolor='white',
    height=300
)

# ========== CHART TRAFFIC LIGHT PER PERSPECTIVE ==========
fig_persp = go.Figure()
for status in status_order:
    fig_persp.add_trace(go.Bar(
        x=perspective_status_counts.index,
        y=perspective_status_counts[status],
        name=status,
        marker_color=status_colors[status],
        text=perspective_status_counts[status],
        textposition='auto'
    ))
fig_persp.update_layout(
    barmode='stack',
    title="KPI Status per Perspective",
    yaxis_title="Jumlah KPI",
    xaxis_title="Perspective",
    plot_bgcolor='white',
    height=400
)

# ========== FILTER PERSPECTIVE (TOMBOL 2x2) ==========
st.markdown("<h1 style='color:#b42020;'>Dashboard KPI Kamu</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_global, use_container_width=True)
with col2:
    st.plotly_chart(fig_persp, use_container_width=True)

st.markdown("<h3 style='color:#b42020;'>Filter Perspective (klik salah satu):</h3>", unsafe_allow_html=True)

perspectives = df['Perspective'].dropna().unique().tolist()
selected_perspective = None

# Buat tombol besar 2x2
btn_cols = st.columns(2)
for i, p in enumerate(perspectives):
    col = btn_cols[i % 2]
    if col.button(p, key=f"btn_{p}", help=f"Pilih perspective {p}", 
                  args=None, 
                  kwargs=None):
        selected_perspective = p

# Jika belum pilih, default pilih yang pertama
if selected_perspective is None and len(perspectives) > 0:
    selected_perspective = perspectives[0]

# Filter data sesuai perspective terpilih
filtered_df = df[df['Perspective'] == selected_perspective]

# ========== TABEL KPI ==========
st.markdown(f"<h3 style='color:#b42020;'>Daftar KPI untuk Perspective: {selected_perspective}</h3>", unsafe_allow_html=True)

# Styling baris merah
def style_row(row):
    color = ''
    if row['Status'] == 'Merah':
        color = 'background-color: #f8d7da;'  # merah muda
    return [color]*len(row)

display_cols = ['Kode KPI', 'KPI', 'Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb', 'Measurement Type', 'Status']
table_df = filtered_df[display_cols].copy()

# Tampilkan tabel dengan style
st.dataframe(table_df.style.apply(style_row, axis=1), use_container_width=True)

# ========== SHOW CHART PER KPI ==========
st.markdown("<h3 style='color:#b42020;'>Pilih KPI untuk lihat detail chart:</h3>", unsafe_allow_html=True)

selected_kpi = st.selectbox("Pilih KPI:", options=table_df['Kode KPI'] + " - " + table_df['KPI'])

if selected_kpi:
    kode = selected_kpi.split(" - ")[0]
    kpi_row = filtered_df[filtered_df['Kode KPI'] == kode].iloc[0]

    fig_detail = go.Figure()
    fig_detail.add_trace(go.Scatter(
        x=['Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb'],
        y=[kpi_row['Target Tahunan'], kpi_row['Actual Jan'], kpi_row['Target Feb'], kpi_row['Actual Feb']],
        mode='lines+markers',
        line=dict(color='#0f098e', width=3)
    ))
    fig_detail.update_layout(
        title=f"Detail KPI: {kpi_row['Kode KPI']} - {kpi_row['KPI']}",
        yaxis_title="Nilai",
        xaxis_title="Kategori",
        height=400,
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_detail, use_container_width=True)
