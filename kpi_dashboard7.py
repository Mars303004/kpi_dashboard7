import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="KPI Dashboard")

# ========== LOAD DATA ==========
file_path = "Dashboard 7.csv"
if not os.path.exists(file_path):
    st.error(f"File {file_path} tidak ditemukan.")
    st.stop()

try:
    df = pd.read_csv(file_path)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

# Pastikan kolom penting ada
required_cols = ['Perspective', 'KPI', 'Kode KPI', 'Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb', 'Achv Feb']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan di data.")
        st.stop()

# ========== Fungsi untuk menentukan status warna berdasarkan Achv Feb ==========
def get_status_color(achv):
    try:
        achv = float(achv)
        if achv > 99:
            return 'Hijau'
        elif 70 <= achv <= 99:
            return 'Kuning'
        elif achv < 70:
            return 'Merah'
        else:
            return 'Hitam'
    except:
        return 'Hitam'  # Untuk N/A atau data tidak valid

df['Status'] = df['Achv Feb'].apply(get_status_color)

# ========== Hitung jumlah KPI per status global ==========
status_order = ['Merah', 'Kuning', 'Hijau', 'Hitam']
status_colors = {'Merah':'#d62728', 'Kuning':'#ffbb33', 'Hijau':'#2ca02c', 'Hitam':'#000000'}

global_status_counts = df['Status'].value_counts().reindex(status_order, fill_value=0)

# ========== Hitung jumlah KPI per status per perspective ==========
perspective_status_counts = df.groupby(['Perspective', 'Status']).size().unstack(fill_value=0).reindex(columns=status_order, fill_value=0)

# ========== Chart Traffic Light Global ==========
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

# ========== Chart Traffic Light Per Perspective ==========
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

# ========== Sidebar Multi-select Perspective ==========
st.sidebar.header("Filter Perspective")
perspectives = df['Perspective'].dropna().unique().tolist()
selected_perspectives = st.sidebar.multiselect("Pilih Perspective (bisa lebih dari satu):", options=perspectives, default=perspectives)

if not selected_perspectives:
    st.warning("Silakan pilih minimal satu perspective.")
    st.stop()

# ========== Filter data berdasarkan perspective terpilih ==========
filtered_df = df[df['Perspective'].isin(selected_perspectives)].reset_index(drop=True)

# ========== Tampilkan Chart di bagian atas halaman ==========
st.title("📊 Dashboard KPI dengan Traffic Light Status")
st.plotly_chart(fig_global, use_container_width=True)
st.plotly_chart(fig_persp, use_container_width=True)

# ========== Tampilkan Tabel KPI ==========
st.markdown(f"### Daftar KPI untuk Perspective: {', '.join(selected_perspectives)}")

# Fungsi untuk styling baris tabel berdasarkan status
def highlight_row(row):
    color = ''
    if row['Status'] == 'Hijau':
        color = 'background-color: #d4edda'  # hijau muda
    elif row['Status'] == 'Kuning':
        color = 'background-color: #fff3cd'  # kuning muda
    elif row['Status'] == 'Merah':
        color = 'background-color: #f8d7da'  # merah muda
    else:
        color = ''  # default
    return [color]*len(row)

display_cols = ['Kode KPI', 'KPI', 'Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb', 'Achv Feb', 'Status']
table_df = filtered_df[display_cols]

# Buat container untuk tabel dan tombol show chart per baris
st.write("Klik tombol 'Show Chart' di sebelah kanan untuk melihat detail KPI.")

# Tampilkan tabel dan tombol "Show Chart" per baris
for idx, row in table_df.iterrows():
    cols = st.columns([8, 1])  # Lebar kolom: tabel 8, tombol 1
    with cols[0]:
        st.write(f"**{row['Kode KPI']} - {row['KPI']}**  \n"
                 f"Target Tahunan: {row['Target Tahunan']}  \n"
                 f"Actual Jan: {row['Actual Jan']}  \n"
                 f"Target Feb: {row['Target Feb']}  \n"
                 f"Actual Feb: {row['Actual Feb']}  \n"
                 f"Achv Feb: {row['Achv Feb']}%  \n"
                 f"Status: {row['Status']}")
    with cols[1]:
        if st.button(f"Show Chart {idx}", key=f"btn_{idx}"):
            # Tampilkan chart detail KPI
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Target Jan', 'Actual Jan', 'Target Feb', 'Actual Feb'],
                y=[row['Target Tahunan'], row['Actual Jan'], row['Target Feb'], row['Actual Feb']],
                marker_color=['#636EFA', '#EF553B', '#636EFA', '#EF553B']
            ))
            fig.update_layout(
                title=f"Detail KPI: {row['Kode KPI']} - {row['KPI']}",
                yaxis_title="Nilai",
                xaxis_title="Bulan",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
