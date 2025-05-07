import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="Dashboard KPI dengan Traffic Light Status")

# ========== LOAD DATA ==========
file_path = "Dashboard 7.csv"
df = pd.read_csv(file_path)

# Pastikan kolom penting ada
required_cols = ['Perspective', 'Kode KPI', 'KPI', 'Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb', 'Achv Feb', 'Measurement Type']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan di data.")
        st.stop()

# Konversi Achv Feb ke numeric, non-konvertible jadi NaN
df['Achv Feb'] = pd.to_numeric(df['Achv Feb'], errors='coerce')

# Fungsi status warna
def get_status_color(achv):
    if pd.isna(achv):
        return 'Hitam'
    elif achv < 70:
        return 'Merah'
    elif 70 <= achv < 100:
        return 'Kuning'
    elif achv >= 100:
        return 'Hijau'
    else:
        return 'Hitam'

df['Status'] = df['Achv Feb'].apply(get_status_color)

# Warna untuk status
status_colors = {
    'Merah': 'red',
    'Kuning': 'yellow',
    'Hijau': 'green',
    'Hitam': 'black'
}

# ================== LAYOUT ATAS: CHART TRAFFIC LIGHT GLOBAL & PER PERSPECTIVE ==================
st.markdown("<h1 style='color:#b42020;'>Dashboard KPI dengan Traffic Light Status</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Total KPI Status (Global)")
    status_order = ['Merah', 'Kuning', 'Hijau', 'Hitam']
    global_counts = df['Status'].value_counts().reindex(status_order, fill_value=0)
    fig_global = go.Figure()
    fig_global.add_trace(go.Bar(
        x=status_order,
        y=global_counts.values,
        marker_color=[status_colors[s] for s in status_order],
        text=global_counts.values,
        textposition='auto'
    ))
    fig_global.update_layout(yaxis_title='Jumlah KPI', xaxis_title='Status', plot_bgcolor='white', height=350)
    st.plotly_chart(fig_global, use_container_width=True)

with col2:
    st.markdown("### KPI Status per Perspective")
    # Hitung jumlah per perspective dan status
    perspective_status = df.groupby(['Perspective', 'Status']).size().unstack(fill_value=0)
    # Pastikan semua status ada kolomnya
    for s in status_order:
        if s not in perspective_status.columns:
            perspective_status[s] = 0
    perspective_status = perspective_status[status_order]  # urutkan kolom
    fig_persp = go.Figure()
    bottom = [0]*len(perspective_status)
    for s in status_order:
        fig_persp.add_trace(go.Bar(
            x=perspective_status.index,
            y=perspective_status[s],
            name=s,
            marker_color=status_colors[s],
            text=perspective_status[s],
            textposition='auto',
            offsetgroup=0,
            base=bottom
        ))
        bottom = [bottom[i] + perspective_status[s].iloc[i] for i in range(len(bottom))]
    fig_persp.update_layout(barmode='stack', yaxis_title='Jumlah KPI', xaxis_title='Perspective', plot_bgcolor='white', height=350)
    st.plotly_chart(fig_persp, use_container_width=True)

# ================== FILTER PERSPECTIVE (2x2 tombol besar) ==================
st.markdown("<h3 style='color:#b42020;'>Filter Perspective (klik salah satu):</h3>", unsafe_allow_html=True)

perspectives = df['Perspective'].dropna().unique().tolist()
perspectives.sort()

# Buat tombol 2x2 dengan warna latar #0f098e dan font putih
selected_perspective = None
cols = st.columns(2)
for i, p in enumerate(perspectives):
    col = cols[i % 2]
    is_selected = False
    if 'selected_perspective' in st.session_state:
        is_selected = (st.session_state.selected_perspective == p)
    else:
        # default pilih perspektif pertama
        if i == 0:
            is_selected = True
            st.session_state.selected_perspective = p

    button_style = f"""
        background-color: {'#0f098e' if not is_selected else '#b42020'};
        color: white;
        font-size: 1.5rem;
        width: 100%;
        height: 60px;
        border-radius: 10px;
        border: none;
        margin-bottom: 10px;
        cursor: pointer;
    """

    if col.button(p, key=f"btn_{p}", help=f"Pilih perspektif {p}"):
        st.session_state.selected_perspective = p

selected_perspective = st.session_state.selected_perspective

# ================== FILTER DATA BERDASARKAN PERSPECTIVE ==================
filtered_df = df[df['Perspective'] == selected_perspective].reset_index(drop=True)

# ================== TABEL KPI DENGAN CONDITIONAL FORMATTING ==================
st.markdown(f"<h3 style='color:#b42020;'>Daftar KPI untuk Perspective: {selected_perspective}</h3>", unsafe_allow_html=True)
st.markdown("Klik tombol 'Show Chart' di sebelah kanan untuk melihat detail KPI.")

# Buat tabel HTML dengan conditional formatting baris merah jika status Merah
def generate_table_html(data):
    header_color = "#0f098e"
    header_font_color = "white"
    row_red_bg = "#f8d7da"
    row_red_font = "#842029"
    row_default_bg = "white"
    row_default_font = "black"

    html = """
    <style>
    table {
        border-collapse: collapse;
        width: 100%;
        font-family: Arial, sans-serif;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: """ + header_color + """;
        color: """ + header_font_color + """;
        font-size: 1.1rem;
    }
    </style>
    <table>
        <thead>
            <tr>
                <th>Kode KPI</th>
                <th>KPI</th>
                <th style="text-align:right;">Target Tahunan</th>
                <th style="text-align:right;">Actual Jan</th>
                <th style="text-align:right;">Target Feb</th>
                <th style="text-align:right;">Actual Feb</th>
                <th>Measurement Type</th>
                <th>Aksi</th>
            </tr>
        </thead>
        <tbody>
    """

    for i, row in data.iterrows():
        bg_color = row_red_bg if row['Status'] == 'Merah' else row_default_bg
        font_color = row_red_font if row['Status'] == 'Merah' else row_default_font
        html += f"""
        <tr style="background-color:{bg_color};color:{font_color};">
            <td>{row['Kode KPI']}</td>
            <td>{row['KPI']}</td>
            <td style="text-align:right;">{row['Target Tahunan']}</td>
            <td style="text-align:right;">{row['Actual Jan'] if pd.notna(row['Actual Jan']) else ''}</td>
            <td style="text-align:right;">{row['Target Feb']}</td>
            <td style="text-align:right;">{row['Actual Feb'] if pd.notna(row['Actual Feb']) else ''}</td>
            <td>{row['Measurement Type']}</td>
            <td><button id="show_chart_{i}" style="background:#0f098e;color:white;border:none;padding:6px 12px;border-radius:6px;cursor:pointer;">Show Chart</button></td>
        </tr>
        """

    html += "</tbody></table>"
    return html

# Render tabel dengan HTML
table_html = generate_table_html(filtered_df)
st.markdown(table_html, unsafe_allow_html=True)

# ================== INTERAKSI SHOW CHART ==================
# Karena tombol HTML tidak bisa langsung diproses Streamlit,
# kita buat tombol Streamlit di samping tabel untuk setiap baris

st.markdown("<br>")
st.markdown("### Pilih KPI untuk lihat detail chart:")

cols = st.columns([8,1])
with cols[0]:
    for i, row in filtered_df.iterrows():
        st.write(f"**{row['Kode KPI']} - {row['KPI']}**")
with cols[1]:
    selected_chart_idx = None
    for i in range(len(filtered_df)):
        if st.button("Show Chart", key=f"show_chart_{i}"):
            selected_chart_idx = i

if selected_chart_idx is not None:
    kpi = filtered_df.loc[selected_chart_idx]
    st.markdown(f"### Detail Chart KPI: {kpi['Kode KPI']} - {kpi['KPI']}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=['Target Tahunan', 'Actual Jan', 'Target Feb', 'Actual Feb'],
        y=[kpi['Target Tahunan'], kpi['Actual Jan'], kpi['Target Feb'], kpi['Actual Feb']],
        mode='lines+markers',
        line=dict(color='#0f098e', width=3),
        marker=dict(size=10)
    ))
    fig.update_layout(
        yaxis_title='Nilai',
        xaxis_title='Kategori',
        plot_bgcolor='white',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
