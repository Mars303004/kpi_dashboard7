import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import base64
import io

# ========== PAGE CONFIG ==========
st.set_page_config(layout="wide", page_title="KPI Dashboard")

# ========== SAMPLE DATA ==========
np.random.seed(42)
data = {
    'KPI Name': ['Revenue Growth', 'Customer Satisfaction', 'Efficiency Ratio', 'Market Share', 'Employee Engagement', 'Cost Reduction', 'Quality Index', 'Customer Retention'],
    'Perspective': ['Financial', 'Customer', 'Internal Process', 'Financial', 'Learning & Growth', 'Financial', 'Internal Process', 'Customer'],
    'Trend Data': [
        np.random.randint(70, 120, size=12),
        np.random.randint(60, 110, size=12),
        np.random.randint(80, 130, size=12),
        np.random.randint(75, 125, size=12),
        np.random.randint(65, 115, size=12),
        np.random.randint(70, 120, size=12),
        np.random.randint(85, 135, size=12),
        np.random.randint(60, 110, size=12)
    ],
    'Achv Feb': [105, 88, 115, 98, 90, 110, 120, 85]
}
df = pd.DataFrame(data)

# ========== FUNCTION TO GENERATE SPARKLINE IMAGE (BASE64) ==========
def generate_sparkline(trend_data, color='#0f098e'):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(2, 0.5))
    ax.plot(trend_data, color=color, linewidth=2)
    ax.axis('off')
    fig.patch.set_alpha(0)
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"<img src='data:image/png;base64,{image_base64}'/>"

df['Sparkline'] = df['Trend Data'].apply(lambda x: generate_sparkline(x, color='#0f098e'))

# ========== CUSTOM CSS STYLING ==========
st.markdown("""
    <style>
    .kpi-card {
        background-color: #0f098e;
        color: white;
        padding: 15px;
        border-radius: 10px;
        width: 250px;
        display: inline-block;
        margin: 10px 10px 10px 0;
        vertical-align: top;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        cursor: pointer;
        user-select: none;
        transition: transform 0.1s ease-in-out;
    }
    .kpi-card:hover {
        transform: scale(1.05);
    }
    .kpi-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: #b42020;
        margin-bottom: 5px;
    }
    .sparkline {
        margin-top: 5px;
    }
    .container {
        white-space: nowrap;
        overflow-x: auto;
        padding-bottom: 10px;
    }
    .btn-perspective {
        background-color: #0f098e;
        color: white;
        border: none;
        padding: 15px 20px;
        margin: 10px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        transition: background-color 0.3s ease;
    }
    .btn-perspective:hover {
        background-color: #b42020;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Dashboard KPI")

# ========== BUTTONS PERSPECTIVE 2x2 ==========
perspectives = ['Financial', 'Customer', 'Internal Process', 'Learning & Growth']

st.markdown("### Pilih Perspective KPI:")

cols = st.columns(2)
for i, perspective in enumerate(perspectives):
    with cols[i % 2]:
        if st.button(perspective, key=f"btn_{perspective}"):
            st.session_state['selected_perspective'] = perspective

# Default selected perspective jika belum ada
if 'selected_perspective' not in st.session_state:
    st.session_state['selected_perspective'] = perspectives[0]

selected_perspective = st.session_state['selected_perspective']

st.markdown(f"### KPI untuk Perspective: **{selected_perspective}**")

# Filter KPI berdasarkan perspective yang dipilih
df_filtered = df[df['Perspective'] == selected_perspective]

# Tampilkan KPI cards dengan sparkline
st.markdown('<div class="container">', unsafe_allow_html=True)
for idx, row in df_filtered.iterrows():
    card_html = f"""
    <div class="kpi-card" id="card-{idx}">
        <div class="kpi-title">{row['KPI Name']}</div>
        <div class="kpi-value">{row['Achv Feb']}</div>
        <div class="sparkline">{row['Sparkline']}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ========== DETAIL TREND PLOT ==========
if len(df_filtered) > 0:
    selected_kpi = df_filtered.iloc[0]  # default pilih KPI pertama di list

    # Jika user klik kartu, kamu bisa tambahkan interaksi lebih lanjut (misal pakai st.button atau st.radio)
    # Untuk contoh ini, kita tampilkan detail trend KPI pertama saja

    st.subheader(f"Detail Trend untuk {selected_kpi['KPI Name']}")

    trend = selected_kpi['Trend Data']
    x = list(range(1, len(trend) + 1))

    fig = go.Figure(go.Scatter(
        x=x,
        y=trend,
        mode='lines+markers+text',
        text=trend,
        textposition='top center',
        line
