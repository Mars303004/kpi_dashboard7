import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Load data
df = pd.read_excel("Coba excel.xlsx", sheet_name="Dulu")

# Traffic light logic
def get_status(row):
    if row["%Achv"].lower() == "n/a":
        return "Hitam"
    elif float(row["%Achv"]) < 70:
        return "Merah"
    elif 70 <= float(row["%Achv"]) <= 100:
        return "Kuning"
    else:
        return "Hijau"

df["Status"] = df.apply(get_status, axis=1)

# === Ringkasan Total KPI Status ===
st.markdown("### Total KPI Status (Global)")
status_order = ["Merah", "Kuning", "Hijau", "Hitam"]
color_map = {"Hijau": "green", "Kuning": "yellow", "Merah": "red", "Hitam": "black"}

status_counts = df["Status"].value_counts().reindex(status_order, fill_value=0)

fig_global = go.Figure(data=[
    go.Bar(
        x=status_counts.index,
        y=status_counts.values,
        text=status_counts.values,
        textposition='auto',
        marker_color=[color_map[status] for status in status_counts.index]
    )
])
fig_global.update_layout(yaxis_title="Jumlah KPI")
st.plotly_chart(fig_global, use_container_width=True)

# === KPI Status per Perspective ===
st.markdown("### KPI Status per Perspective")
perspective_counts = df.groupby(["Perspective", "Status"]).size().unstack(fill_value=0).reindex(columns=status_order).fillna(0)

fig_perspective = go.Figure()
for status in status_order:
    fig_perspective.add_trace(go.Bar(
        x=perspective_counts.index,
        y=perspective_counts[status],
        name=status,
        marker_color=color_map[status],
        text=perspective_counts[status],
        textposition='auto'
    ))

fig_perspective.update_layout(
    barmode='stack',
    yaxis_title="Jumlah KPI",
    xaxis_title="Perspective"
)
st.plotly_chart(fig_perspective, use_container_width=True)

# === Filter Perspective (2x2 tombol besar) ===
st.markdown("### Filter Perspective (klik salah satu):")
perspectives = df["Perspective"].unique()
perspective_selection = None

col1, col2 = st.columns(2)
with col1:
    for p in perspectives[:2]:
        if st.button(p, key=f"btn_{p}", help=f"Filter by {p}", use_container_width=True):
            perspective_selection = p
with col2:
    for p in perspectives[2:]:
        if st.button(p, key=f"btn_{p}_2", help=f"Filter by {p}", use_container_width=True):
            perspective_selection = p

if perspective_selection:
    st.markdown(f"### Daftar KPI untuk Perspective: {perspective_selection}")
    df_filtered = df[df["Perspective"] == perspective_selection]
    st.dataframe(df_filtered)

    st.markdown("### Pilih KPI untuk lihat detail chart:")
    kpi_options = df_filtered[["Kode KPI", "KPI"]].drop_duplicates()
    for _, row in kpi_options.iterrows():
        if st.button(f"Show Chart {row['Kode KPI']}"):
            st.markdown(f"**Detail KPI: {row['Kode KPI']} - {row['KPI']}**")
            kpi_data = df_filtered[df_filtered["Kode KPI"] == row["Kode KPI"]]

            categories = ["Actual Jan", "Target Feb", "Actual Feb"]
            actual_values = [kpi_data[c].values[0] for c in categories]
            target_line = float(kpi_data["Target Tahunan"].values[0])
            months = categories

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=actual_values, mode='lines+markers', name='Kinerja Bulanan', line=dict(color="#0f098e")))
            fig.add_trace(go.Scatter(x=months, y=[target_line]*len(months), mode='lines', name='Target Tahunan', line=dict(color='green', dash='dash')))

            fig.update_layout(yaxis_title="Nilai", xaxis_title="Kategori")
            st.plotly_chart(fig, use_container_width=True)
