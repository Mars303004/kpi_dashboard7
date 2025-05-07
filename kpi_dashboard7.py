import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Warna
COLOR_BLUE = '#0f098e'
COLOR_WHITE = '#ffffff'
COLOR_RED = '#b42020'
COLOR_YELLOW = '#f5e960'
COLOR_GREEN = '#00c853'
COLOR_BLACK = '#2e2e2e'

color_dict = {
    "Merah": COLOR_RED,
    "Kuning": COLOR_YELLOW,
    "Hijau": COLOR_GREEN,
    "Hitam": COLOR_BLACK
}

# Load data
df = pd.read_excel("Coba excel.xlsx", sheet_name="Dulu")

# Tambahkan kolom Status
def calculate_status(row):
    if str(row['%Achv']).lower() == 'n/a':
        return 'Hitam'
    elif float(row['%Achv']) < 70:
        return 'Merah'
    elif float(row['%Achv']) <= 100:
        return 'Kuning'
    else:
        return 'Hijau'

df['Status'] = df.apply(calculate_status, axis=1)

# CHART TRAFFIC LIGHT GLOBAL
st.markdown("### Total KPI Status (Global)")
status_counts = df['Status'].value_counts()
fig_status = go.Figure()

for status in ['Merah', 'Kuning', 'Hijau', 'Hitam']:
    count = status_counts.get(status, 0)
    fig_status.add_trace(go.Bar(
        x=[status],
        y=[count],
        name=status,
        marker_color=color_dict[status],
        text=[count],
        textposition='auto'
    ))

fig_status.update_layout(
    yaxis_title='Jumlah KPI',
    xaxis_title='Status',
    showlegend=False
)
st.plotly_chart(fig_status, use_container_width=True)

# CHART TRAFFIC LIGHT PER PERSPECTIVE
st.markdown("### KPI Status per Perspective")
grouped = df.groupby(['Perspective', 'Status']).size().unstack(fill_value=0)
perspectives = grouped.index.tolist()
fig_perspective = go.Figure()

for status in ['Merah', 'Kuning', 'Hijau', 'Hitam']:
    values = grouped.get(status, [0]*len(perspectives))
    fig_perspective.add_trace(go.Bar(
        x=perspectives,
        y=values,
        name=status,
        marker_color=color_dict[status],
        text=values,
        textposition='auto'
    ))

fig_perspective.update_layout(
    barmode='stack',
    yaxis_title='Jumlah KPI',
    xaxis_title='Perspective'
)
st.plotly_chart(fig_perspective, use_container_width=True)

# FILTER PERSPECTIVE 2x2 BESAR
st.markdown("### Filter KPI berdasarkan Perspective")
unique_perspectives = df['Perspective'].unique().tolist()
selected_perspective = None

col1, col2 = st.columns(2)
with col1:
    for i in range(0, len(unique_perspectives), 2):
        if i < len(unique_perspectives):
            p = unique_perspectives[i]
            if st.button(p, key=p, help=f"Pilih {p}"):
                selected_perspective = p

with col2:
    for i in range(1, len(unique_perspectives), 2):
        if i < len(unique_perspectives):
            p = unique_perspectives[i]
            if st.button(p, key=p, help=f"Pilih {p}"):
                selected_perspective = p

# TAMPILKAN DAFTAR KPI BERDASARKAN PERSPECTIVE
if selected_perspective:
    st.markdown(f"### Daftar KPI: {selected_perspective}")
    filtered_df = df[df['Perspective'] == selected_perspective]
    st.dataframe(filtered_df[['Kode KPI', 'KPI', '%Achv', 'Status']])

    st.markdown("### Pilih KPI untuk melihat detail:")
    selected_kpi_code = st.selectbox(
        "Pilih Kode KPI",
        filtered_df['Kode KPI'].unique()
    )

    if selected_kpi_code:
        kpi_row = filtered_df[filtered_df['Kode KPI'] == selected_kpi_code].iloc[0]
        actual_feb = kpi_row['Actual Feb']
        if pd.isna(actual_feb) or str(actual_feb).strip().upper() == 'NA':
            st.info("Belum ada data yang tersedia untuk KPI ini.")
        else:
            fig_detail = go.Figure()

            # Garis Target Tahunan penuh dari ujung ke ujung
            fig_detail.add_trace(go.Scatter(
                x=[0, 1],
                y=[kpi_row['Target Tahunan']] * 2,
                mode='lines',
                name='Target Tahunan',
                line=dict(color=COLOR_GREEN, dash='dash')
            ))

            # Garis Kinerja Bulanan
            fig_detail.add_trace(go.Scatter(
                x=[0, 0.5, 1],
                y=[kpi_row['Actual Jan'], kpi_row['Target Feb'], kpi_row['Actual Feb']],
                mode='lines+markers',
                name='Kinerja Bulanan',
                line=dict(color=COLOR_BLUE, width=3)
            ))

            fig_detail.update_layout(
                title=f"Detail KPI: {kpi_row['Kode KPI']} - {kpi_row['KPI']}",
                yaxis_title="Nilai",
                xaxis=dict(
                    tickvals=[],  # Hapus label Jan/Feb
                    showgrid=False
                ),
                height=400,
                plot_bgcolor=COLOR_WHITE,
                paper_bgcolor=COLOR_WHITE,
                font=dict(color=COLOR_BLUE)
            )
            st.plotly_chart(fig_detail, use_container_width=True)
