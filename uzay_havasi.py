import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Real Aurora Map", layout="wide")

# NOAA OVATION API
AURORA_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"

@st.cache_data(ttl=300)
def get_aurora_data():
    try:
        r = requests.get(AURORA_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"NOAA veri hatası: {e}")
        return None

st.title("🌌 Gerçek Zamanlı Aurora Haritası")
st.markdown("---")

# 🔥 BUTON (Kuzey / Güney seçimi)
hemisphere = st.radio(
    "Yarımküre Seç",
    ["Kuzey", "Güney"],
    horizontal=True
)

data = get_aurora_data()

if data and "coordinates" in data:
    
    coords = data["coordinates"]

    lats = []
    lons = []
    intensity = []

    for c in coords:
        lon, lat, value = c

        # 🔥 SEÇİME GÖRE FİLTRE
        if hemisphere == "Kuzey" and lat >= 50:
            lats.append(lat)
            lons.append(lon)
            intensity.append(value)

        elif hemisphere == "Güney" and lat <= -50:
            lats.append(lat)
            lons.append(lon)
            intensity.append(value)

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=dict(
            size=4,
            color=intensity,
            colorscale="Turbo",
            opacity=0.8,
            colorbar=dict(title="Aurora Yoğunluğu")
        )
    ))

    fig.update_layout(
        geo=dict(
            projection_type="azimuthal equal area",  # 🎯 polar görünüm
            showland=True,
            landcolor="rgb(30,30,30)",
            showocean=True,
            oceancolor="rgb(10,10,25)",
            lataxis_range=[50, 90] if hemisphere == "Kuzey" else [-90, -50],
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    # Zaman bilgisi
    if "Forecast Time" in data:
        st.info(f"🕒 Veri Zamanı: {data['Forecast Time']}")

else:
    st.error("Aurora verisi alınamadı.")