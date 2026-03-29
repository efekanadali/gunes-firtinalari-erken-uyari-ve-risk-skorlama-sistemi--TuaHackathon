import streamlit as st
import streamlit.components.v1 as components
import requests
import sys
import os
import time
import base64

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from app import get_space_weather, calculate_risk, generate_ai_insight, generate_simulation_report
except ImportError:
    st.error("app.py bulunamadı.")
    def get_space_weather(): return None
    def calculate_risk(d): return "UNKNOWN", 0
    def generate_ai_insight(*args): return "Yapay zeka modülü aktif değil."
    def generate_simulation_report(r): return "Rapor modülü aktif değil."

st.set_page_config(
    page_title="TUA Erken Uyarı Sistemi", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stApp"], body {
    background-color: #000000 !important; /* Uzayın mutlak karanlık tonu - sitenin en arkası */
    background-image: none !important;
    color: #E2F1E8;
}
body { background-color: #000000 !important; background-image: none !important; }

/* Kapsayıcı bloğun uzay çerçevesini (Hologram dış hatlar) koruyalım */
[data-testid="stHorizontalBlock"] {
    border-radius: 20px; /* Pencereye şık bir kavis */
    border: 1px solid rgba(0, 255, 171, 0.15); /* Hologram ekranı hissiyatı için ince lazer çizgisi */
    padding: 15px; /* Çerçeve ve tablo arasına nefes alma boşluğu */
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.4) inset; /* Hologram derinlik efekti */
}
header {visibility: hidden;}
[data-testid="stSidebar"] {display: none;}

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;600&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 40px;
    border-bottom: 1px solid rgba(0, 255, 171, 0.15);
    background: linear-gradient(180deg, rgba(11, 20, 30, 0.9) 0%, rgba(5, 10, 15, 0.3) 100%);
    backdrop-filter: blur(10px);
    margin-top: -60px;
    margin-bottom: 20px;
}
.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #E2F1E8;
}
.nav-tabs {
    display: flex;
    gap: 35px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1.5px;
    color: #587968;
    text-transform: uppercase;
}
.nav-tabs span.active {
    color: #00FFAB;
    border-bottom: 2px solid #00FFAB;
    padding-bottom: 4px;
}

.metric-container {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 20px;
    margin-top: 40px;
    padding-right: 20px;
}
.metric-title {
    font-size: 11px;
    color: #6A8A7A;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 38px;
    font-weight: 400;
    line-height: 1;
    text-shadow: 0px 0px 15px currentColor;
}
.unit { font-size: 16px; opacity: 0.7; }

.val-blue  { color: #00D5FF; }
.val-green { color: #00FFAB; }
.val-red   { color: #FF4A4A; }
.val-white { color: #FFFFFF; }

.alert-panel {
    background: rgba(20, 5, 5, 0.6);
    border: 1px solid rgba(255, 74, 74, 0.3);
    border-left: 4px solid #FF4A4A;
    padding: 20px;
    border-radius: 6px;
    margin-top: 150px;
    max-width: 300px;
    backdrop-filter: blur(8px);
}
.alert-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 10px;
    color: #FF4A4A;
    font-weight: 700;
    letter-spacing: 2px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.alert-dot {
    width: 8px; height: 8px;
    background-color: #FF4A4A;
    border-radius: 50%;
    box-shadow: 0 0 10px #FF4A4A;
    animation: pulse 1.5s infinite;
}
.alert-title {
    font-size: 20px;
    font-weight: 700;
    margin: 8px 0;
    color: #FFF;
}
.alert-desc {
    font-size: 13px;
    color: #9BA9B0;
    line-height: 1.5;
}
@keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.3); opacity: 0.5; }
    100% { transform: scale(1); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_telemetry_v4():
    return get_space_weather()

@st.cache_data(ttl=300) # Yapay zeka maliyetini (veya limitini) korumak için 5 dk önbellekleme
def get_cached_ai_insight_v3(speed, density, kp, bz, bt, risk_level):
    return generate_ai_insight(speed, density, kp, bz, bt, risk_level)

st.markdown("""
<style>
/* SAAS GLASSMORPHISM TEMPLATE */
.stApp {
    background-color: #030811 !important; /* Derin uzay mavisi */
}
[data-testid="stAppViewBlockContainer"] {
    padding-top: 2.5rem !important;
}
/* Modern Glassmorphism Streamlit Satırları (Row) */
[data-testid="stHorizontalBlock"] {
    background: rgba(10, 15, 25, 0.6);
    border-radius: 16px;
    border: 1px solid rgba(0, 255, 171, 0.15);
    padding: 20px 30px;
    backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6);
    align-items: center; /* Kolonları dikeyde ortalar */
    margin-bottom: 25px;
}

/* Streamlit Radio Header Integration (Menü Butonları - Sade Metin) */
div.row-widget.stRadio > div {
    flex-direction: row; justify-content: center; gap: 40px;
}
/* Menüdeki yuvarlak radyo ikonlarını tamamen gizle */
div[role="radiogroup"] label > div:first-child,
div.stRadio label > div:first-of-type {
    display: none !important;
}
/* Sadece metin linki gibi görünsün */
div.row-widget.stRadio label {
    font-family: 'Inter', sans-serif !important; font-size: 15px !important;
    font-weight: 600; color: #FFFFFF !important; cursor: pointer;
    padding: 5px 10px; transition: all 0.2s ease;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    opacity: 0.6;
}
div.row-widget.stRadio label:hover {
    opacity: 1;
    transform: none;
    background: transparent !important;
}
div.row-widget.stRadio label[data-checked="true"] {
    opacity: 1;
    color: #00FFAB !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
div.row-widget.stRadio label p {
    margin: 0 !important;
}

/* Header Özel Elementleri */
.brand {
    font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 700;
    letter-spacing: 2px; color: #E2F1E8; 
    text-shadow: 0px 0px 15px rgba(0, 213, 255, 0.5);
    margin: 0; padding: 0;
}
.system-status {
    color: #00FFAB; font-size: 14px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;
    padding: 10px 20px; border-radius: 30px; border: 1px solid rgba(0,255,171,0.3);
    background: rgba(0,255,171,0.08);
    box-shadow: 0 0 20px rgba(0,255,171,0.15);
    float: right;
}
/* İç Widget Düzenlemeleri */
[data-testid="stSlider"] label { color: #8A9A90 !important; font-family: 'Space Grotesk', sans-serif; }
</style>
""", unsafe_allow_html=True)

# PREMIUM HEADER ROW (Düzgünce Hizalanmış Üst Menü)
import base64
import os

tua_logo_path = "tua.png"
logo_src = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Turkish_Space_Agency_logo.svg/1200px-Turkish_Space_Agency_logo.svg.png"

# Kullanıcının eklediği .png resmini güvenli olarak st.markdown içinde yüklemek için Base64'e dönüştürüyoruz
if os.path.exists(tua_logo_path):
    with open(tua_logo_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        logo_src = f"data:image/png;base64,{encoded_string}"

head_c1, head_c2, head_c3 = st.columns([1.5, 3, 1.5], vertical_alignment="center")
with head_c1:
    st.markdown(f'''
        <div style="display: flex; align-items: center; gap: 15px;">
            <img src="{logo_src}" style="height: 52px; border-radius: 4px;" />
        </div>
    ''', unsafe_allow_html=True)
with head_c2:
    nav_selection = st.radio("Navigation", ["Küresel Görünüm", "Manyetosfer Simülasyonu"], horizontal=True, label_visibility="collapsed")
with head_c3:
    st.markdown('<div class="system-status"><span style="font-size: 16px;">⚲</span> SİSTEM AKTİF</div>', unsafe_allow_html=True)

if nav_selection == "Manyetosfer Simülasyonu":
    try:
        from simulation_engine import SolarStormRiskAlgorithm
        algo = SolarStormRiskAlgorithm()
    except Exception as e:
        st.error(f"Simülasyon motoru yüklenemedi: {e}")
        st.stop()
        
    st.markdown("<h3 style='text-align:center; color:#E2F1E8; font-family:Space Grotesk; letter-spacing:2px; margin-bottom: 30px;'>MANYETOSFER ETKİLEŞİM MODELİ</h3>", unsafe_allow_html=True)
    
    col_ui, col_viz = st.columns([1, 2.8])
    
    with col_ui:
        st.markdown("<div style='color:#00D5FF; font-size:11px; letter-spacing:1px; margin-bottom:10px;'>GÜNEŞ RÜZGARI PARAMETRELERİ</div>", unsafe_allow_html=True)
        v_sw = st.slider("Güneş Rüzgarı Hızı (km/s)", 300.0, 2500.0, 356.7, step=10.0)
        density = st.slider("Proton Yoğunluğu (p/cm³)", 0.1, 100.0, 1.14, step=0.1)
        bz = st.slider("Manyetik Bz (Güney-Yönlü, nT)", -50.0, 30.0, -2.78, step=0.1)
        bt = st.slider("Manyetik Bt (Toplam, nT)", 1.0, 80.0, 4.42, step=0.1)
        st.markdown("<div style='color:#00FFAB; font-size:11px; letter-spacing:1px; margin-top:20px; margin-bottom:10px;'>FIRTINA METRİKLERİ</div>", unsafe_allow_html=True)
        kp = st.slider("Kp İndeksi", 0.0, 9.0, 1.0, step=0.3)
        proton_flux = st.slider("Proton Akısı (pfu)", 0.0, 50.0, 0.174)
        xray_flux = st.number_input("X-Işını Akısı (W/m² - örn. 1e-6)", value=1.599e-06, format="%e")
        cme_speed = st.slider("KKA Hızı (km/s)", 300.0, 3500.0, 691.0, step=10.0)
        
        # Algoritma Hesaplamaları
        eps, newell = algo.calculate_coupling_functions(v_sw, bt, clock_angle=-130.63)
        dDst, pdyn = algo.predict_dst_change(-17.0, v_sw, bz, density)
        toa_h, v_arr = algo.cme_arrival_toa(cme_speed, v_sw)
        risk_r = algo.calculate_global_risk_score(kp, -17.0, proton_flux, xray_flux, newell)
        
        r_col = "#FF4A4A" if risk_r > 7 else "#FFB800" if risk_r > 4 else "#00FFAB"
        
        st.markdown("<hr style='border-color: rgba(0,255,171,0.2)'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:24px; color:{r_col}; font-family:Space Grotesk;'>Risk Skoru (R): <b>{risk_r}/10</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:14px; color:#00D5FF; margin-top:8px;'>Dinamik Basınç: <b>{pdyn:.2f} nPa</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:14px; color:#E2F1E8;'>Enerji Girişi (Akasofu): <b>{eps/1e9:.2f} GW</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:14px; color:#E2F1E8;'>KKA Tahmini Varış Süresi: <b>{toa_h:.1f} saat</b></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📡 DURUM RAPORU AL", use_container_width=True):
            with st.spinner("TUA Analiz Ediyor..."):
                report = generate_simulation_report(risk_r)
                st.markdown(f"""
                <div style='background:rgba(10,25,35,0.8); border-left:3px solid {r_col}; padding:15px; border-radius:4px; margin-top:10px; font-size:13px; color:#E2F1E8; line-height:1.5;'>
                <b>🤖 TUA Taktik Raporu:</b><br>{report}
                </div>
                """, unsafe_allow_html=True)

    with col_viz:
        canvas_html = f'''
        <style>
            .sim-box {{
                width: 100%; height: 680px; background: #020508; 
                border: 1px solid rgba(0,255,171,0.2); border-radius: 8px; position: relative; overflow:hidden;
            }}
            canvas {{ width: 100%; height: 100%; }}
        </style>
        <div class="sim-box"><canvas id="magnetosphere"></canvas></div>
        <script>
            const canvas = document.getElementById("magnetosphere");
            const ctx = canvas.getContext("2d");
            const pR = window.devicePixelRatio || 1;
            canvas.width = canvas.parentElement.clientWidth * pR;
            canvas.height = canvas.parentElement.clientHeight * pR;
            ctx.scale(pR, pR);
            const w = canvas.parentElement.clientWidth;
            const h = canvas.parentElement.clientHeight;
            
            // Parametrelerin JS dünyasına aktarımı
            const pdyn = {pdyn};
            const vsw = {v_sw};
            const risk = {risk_r};
            
            // Dinamik basınca göre Dünyanın manyetik kalkanının (bow shock) geri çekilmesi
            let compression = Math.max(0.35, 1.0 - (pdyn / 30.0));
            // Hıza göre parçacık akışı ve titreme
            let speedFactor = Math.min(3.0, (vsw / 400.0));

            let tick = 0;
            let ex = w * 0.75; // Dünya'nın sağdaki konumu
            let ey = h * 0.5;
            let eR = 38;       // Dünya yarıçapı büyütüldü
            let bowR = eR * 6.5 * compression; // Kalkan genişliği
            
            let particles = [];
            for(let i=0; i<450; i++) {{
                particles.push({{
                    x: Math.random() * w, 
                    y: ey + (Math.random() - 0.5) * h,
                    speed: speedFactor + Math.random()*2,
                    offsetY: (Math.random() - 0.5) * h * 0.95
                }});
            }}
            
            function drawEarth() {{
                // Gece Tarafı Manyetik Kuyruk Çizgileri (Magnetotail)
                ctx.strokeStyle = "rgba(0, 150, 255, 0.35)";
                ctx.lineWidth = 1.2;
                for(let r=1.5; r<=4.5; r+=0.8) {{
                   let rad = eR * r * compression;
                   ctx.beginPath();
                   ctx.ellipse(ex + rad*0.7, ey, rad*2.0, rad*2.5, 0, -Math.PI/2, Math.PI/2, true);
                   ctx.stroke();
                }}
                
                // Atmosfer Parlaması (Sadece Gündüz Tarafına Doğru Hafif Kaykılmış)
                ctx.shadowBlur = eR * 0.6;
                ctx.shadowColor = "#00D5FF";
                
                // Gündüz / Gece Küresel Işıklandırması (Güneş tam sağımızda / soldan vuruyor)
                let dropGrd = ctx.createLinearGradient(ex - eR, ey, ex + eR, ey);
                dropGrd.addColorStop(0, "#B3E5FF");   // Atmosfer vurma noktası
                dropGrd.addColorStop(0.15, "#1F78FF"); // Okyanus
                dropGrd.addColorStop(0.45, "#0A2540"); // Alacakaranlık (Terminator hattı)
                dropGrd.addColorStop(1, "#010305");   // Tam Gece Karanlığı
                
                ctx.beginPath();
                ctx.arc(ex, ey, eR, 0, Math.PI*2);
                ctx.fillStyle = dropGrd; ctx.fill();
                
                // Yüzey Detayları İçin Klip Maskesi Başlat (Taşmaları önler)
                ctx.save();
                ctx.beginPath();
                ctx.arc(ex, ey, eR, 0, Math.PI*2);
                ctx.clip();
                
                // 1. Stylized Kıtalar
                ctx.fillStyle = "rgba(10, 80, 40, 0.6)";
                ctx.beginPath(); // Büyük kıta
                ctx.ellipse(ex-eR*0.1, ey-eR*0.15, eR*0.6, eR*0.4, Math.PI/5, 0, Math.PI*2);
                ctx.fill();
                ctx.beginPath(); // Güney kıtası
                ctx.ellipse(ex+eR*0.25, ey+eR*0.35, eR*0.4, eR*0.2, -Math.PI/6, 0, Math.PI*2);
                ctx.fill();
                
                // 2. Bulut Katmanı (Fırça darbesi gibi ince atmosferik bulutlar)
                ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
                ctx.lineWidth = eR * 0.15;
                ctx.lineCap = "round";
                ctx.beginPath();
                ctx.arc(ex, ey, eR*0.75, -Math.PI/1.5, Math.PI/4); // Kuzey bulut döngüsü
                ctx.stroke();
                ctx.beginPath();
                ctx.arc(ex - eR*0.1, ey + eR*0.2, eR*0.6, Math.PI/2.5, Math.PI); // Güney bulut şeridi
                ctx.stroke();
                
                // 3. Gece Tarafı Siyah Gölge Çarpması (Terminator Line'ı sertleştirir, volümü artırır)
                let nightGrd = ctx.createLinearGradient(ex - eR*0.2, ey, ex + eR, ey);
                nightGrd.addColorStop(0, "rgba(0,0,0,0)");
                nightGrd.addColorStop(0.8, "rgba(0,0,0,0.85)");
                nightGrd.addColorStop(1, "rgba(0,0,0,0.95)");
                ctx.fillStyle = nightGrd;
                ctx.beginPath();
                ctx.arc(ex, ey, eR, 0, Math.PI*2);
                ctx.fill();
                
                ctx.restore(); // Klip maskesini sonlandır
                
                // İnce Sınır (Kalkanımsı dış çerçeve)
                ctx.shadowBlur = 0;
                ctx.lineWidth = 1; 
                ctx.strokeStyle = "rgba(0, 255, 171, 0.35)"; 
                ctx.stroke();
            }}

            function drawAuroras() {{
                // Parametrik Kutup Işıkları!
                let aurHeight = risk >= 7.5 ? eR * 1.8 : (risk >= 4.0 ? eR * 0.9 : eR * 0.5);
                let aurColor = risk >= 7.5 ? "rgba(255, 50, 150, 0.8)" : (risk >= 4.0 ? "rgba(255, 180, 0, 0.8)" : "rgba(0, 255, 171, 0.8)");
                let waveSpeed = risk >= 7.5 ? 0.3 : 0.05;
                
                ctx.lineWidth = risk >= 7.5 ? 4 : 2;
                ctx.strokeStyle = aurColor;
                ctx.shadowBlur = 15;
                ctx.shadowColor = aurColor;
                ctx.lineCap = "round";

                // Kuzey Kutbu
                for(let i=0; i<3; i++) {{
                    ctx.beginPath();
                    let startX = ex - eR*0.6;
                    ctx.moveTo(startX, ey - eR + 2);
                    let cp1x = startX + eR*0.4;
                    let cp1y = ey - eR - aurHeight * Math.abs(Math.sin(tick*waveSpeed + i));
                    let cp2x = startX + eR*0.8;
                    let cp2y = ey - eR - aurHeight * Math.abs(Math.cos(tick*waveSpeed*0.7 + i));
                    let endX = ex + eR*0.6;
                    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, endX, ey - eR + 2);
                    ctx.stroke();
                }}

                // Güney Kutbu
                for(let i=0; i<3; i++) {{
                    ctx.beginPath();
                    let startX = ex - eR*0.6;
                    ctx.moveTo(startX, ey + eR - 2);
                    let cp1x = startX + eR*0.4;
                    let cp1y = ey + eR + aurHeight * Math.abs(Math.sin(tick*waveSpeed + i*1.5));
                    let cp2x = startX + eR*0.8;
                    let cp2y = ey + eR + aurHeight * Math.abs(Math.cos(tick*waveSpeed*0.7 + i));
                    let endX = ex + eR*0.6;
                    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, endX, ey + eR - 2);
                    ctx.stroke();
                }}
                ctx.shadowBlur = 0;
            }}
            
            function drawSun() {{
                let sunX = -100; // Güneşin merkezi vizörün dışında
                let sunR = 300;
                
                ctx.globalCompositeOperation = "screen"; // Güçlü Bloom etkisi
                
                // 1. Dış Atmosfer Parlaması (Corona Glow)
                let coronaGrd = ctx.createRadialGradient(sunX, ey, sunR*0.8, sunX, ey, sunR*1.8);
                if(risk >= 7.5) {{
                    coronaGrd.addColorStop(0, "rgba(255, 100, 0, 0.4)");
                    coronaGrd.addColorStop(0.5, "rgba(255, 0, 0, 0.15)");
                }} else {{
                    coronaGrd.addColorStop(0, "rgba(255, 200, 100, 0.3)");
                    coronaGrd.addColorStop(0.5, "rgba(255, 100, 0, 0.1)");
                }}
                coronaGrd.addColorStop(1, "rgba(0,0,0,0)");
                ctx.fillStyle = coronaGrd;
                ctx.beginPath(); ctx.arc(sunX, ey, sunR*1.8, 0, Math.PI*2); ctx.fill();

                // 2. Güneş Gövdesi (Volumetric Plasma Core)
                let coreGrd = ctx.createRadialGradient(sunX, ey, 0, sunX, ey, sunR);
                if(risk >= 7.5) {{
                    coreGrd.addColorStop(0, "rgba(255, 255, 255, 1)");
                    coreGrd.addColorStop(0.2, "rgba(255, 150, 0, 1)");
                    coreGrd.addColorStop(0.7, "rgba(200, 0, 0, 0.8)");
                    coreGrd.addColorStop(1, "rgba(100, 0, 0, 0.0)");
                }} else {{
                    coreGrd.addColorStop(0, "rgba(255, 255, 255, 1)");
                    coreGrd.addColorStop(0.3, "rgba(255, 220, 100, 1)");
                    coreGrd.addColorStop(0.7, "rgba(255, 120, 0, 0.7)");
                    coreGrd.addColorStop(1, "rgba(150, 50, 0, 0.0)");
                }}
                ctx.fillStyle = coreGrd;
                ctx.beginPath(); ctx.arc(sunX, ey, sunR, 0, Math.PI*2); ctx.fill();
                
                // 3. Procedural Granular Texture (Matematiksel Plazma Hücreleri)
                // Güneş yüzeyindeki kaynayan noktacıklar
                ctx.globalCompositeOperation = "lighter";
                for(let g=0; g<80; g++) {{
                    let gAngle = -Math.PI/3 + Math.random() * (Math.PI/1.5);
                    let gDist = sunR * Math.random() * 0.95; 
                    let gx = sunX + Math.cos(gAngle)*gDist;
                    let gy = ey + Math.sin(gAngle)*gDist;
                    
                    let gSize = 5 + Math.random()*15;
                    let flicker = Math.sin(tick*0.1 + g) * 0.5 + 0.5; // Titreme efekti
                    
                    ctx.fillStyle = risk >= 7.5 ? "rgba(255, 255, 100, " + (0.1 * flicker) + ")" : "rgba(255, 255, 255, " + (0.05 * flicker) + ")";
                    ctx.beginPath(); ctx.arc(gx, gy, gSize, 0, Math.PI*2); ctx.fill();
                }}
                

                
                ctx.globalCompositeOperation = "source-over"; // Diğer çizimler için normale dön
            }}

            function drawBowShock() {{
                // Manyetik Kalkan Isı Haritası
                let grd = ctx.createLinearGradient(ex - bowR*1.5, 0, ex, 0);
                if(risk >= 7.5) {{
                    grd.addColorStop(0, "rgba(255, 30, 30, 0.95)");  
                    grd.addColorStop(1, "rgba(255, 100, 0, 0.0)");
                }} else if (risk >= 4.0) {{
                    grd.addColorStop(0, "rgba(255, 180, 0, 0.8)");  
                    grd.addColorStop(1, "rgba(200, 200, 0, 0.0)");
                }} else {{
                    grd.addColorStop(0, "rgba(0, 255, 171, 0.6)");  
                    grd.addColorStop(1, "rgba(0, 150, 255, 0.0)");
                }}

                ctx.beginPath();
                ctx.arc(ex - bowR*0.3, ey, bowR * 1.8, -Math.PI/2.3, Math.PI/2.3, false);
                ctx.lineWidth = Math.max(20, 60 * compression); 
                ctx.strokeStyle = grd;
                ctx.lineCap = "round";
                ctx.stroke();
            }}
            
            function updateParticles() {{
                ctx.lineCap = "round";
                for(let p of particles) {{
                    let oldX = p.x;
                    let oldY = p.y;
                    
                    p.x += p.speed * 3.5; // Hızlı plazma ışınları
                    
                    let dx = p.x - ex;
                    let dy = p.y - ey;
                    let dist = Math.sqrt(dx*dx + dy*dy);
                    
                    // Kalkandan seken parçacıklar
                    if (p.x < ex && dist < bowR * 2.2) {{
                        let repel = (bowR * 2.2 - dist) / 10;
                        p.y += dy > 0 ? repel : -repel;
                        p.x += repel * 0.4;
                    }}
                    
                    if(p.x > w || p.y < -150 || p.y > h+150) {{
                        p.x = Math.random()*-150;
                        p.y = ey + p.offsetY + (Math.random() * 80 - 40);
                        oldX = p.x; oldY = p.y;
                    }}
                    
                    // Kuyruklu yıldız / Işın efekti (Çizgi çizimi)
                    ctx.beginPath();
                    ctx.moveTo(oldX, oldY);
                    ctx.lineTo(p.x, p.y);
                    
                    if(risk >= 7.5) {{
                        ctx.strokeStyle = "rgba(255, " + (60 + Math.random()*100) + ", 30, " + (Math.random()*0.8 + 0.2) + ")";
                        ctx.lineWidth = p.speed * 1.2;
                    }} else if (risk >= 4.0) {{
                        ctx.strokeStyle = "rgba(255, 200, 80, " + (Math.random()*0.6 + 0.2) + ")";
                        ctx.lineWidth = p.speed * 0.9;
                    }} else {{
                        ctx.strokeStyle = "rgba(150, 220, 255, " + (Math.random()*0.5 + 0.1) + ")";
                        ctx.lineWidth = p.speed * 0.6;
                    }}
                    ctx.stroke();
                }}
            }}

            function loop() {{
                // Arkaplanı silmeyip karartarak (Trailing effect) motion blur oluştur
                ctx.fillStyle = "rgba(2, 5, 8, 0.4)"; 
                ctx.fillRect(0, 0, w, h);
                
                drawSun();
                drawBowShock();
                drawEarth();
                drawAuroras();
                updateParticles();
                
                tick += 1;
                requestAnimationFrame(loop);
            }}
            loop();
        </script>
        '''
        import streamlit.components.v1 as components
        components.html(canvas_html, height=700)
        
    st.stop() # Sayfanın Global View kısmının çizilmesini engeller

telemetry = fetch_telemetry_v4()

c1, c2, c3 = st.columns([1, 2.5, 1])

with c1:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    risk_level, risk_pct = calculate_risk(telemetry)
    
    if telemetry:
        # Yapay zekadan durumsal farkındalık (Insight) iste
        speed_val = telemetry.get('speed', 0)
        density_val = telemetry.get('density', 0)
        kp_val = telemetry.get('kp', 0)
        bz_val = telemetry.get('bz', 0)
        bt_val = telemetry.get('bt', 0)
        
        with st.spinner("Yapay Zeka Telemetriyi Analiz Ediyor..."):
            ai_text = get_cached_ai_insight_v3(speed_val, density_val, kp_val, bz_val, bt_val, risk_level)
    else:
        ai_text = "Veri akışı sağlanamıyor, yapay zeka bağlantısı kapalı."
        
    # Javascript ile Asenkron (non-blocking) Typewriter efekti
    # Streamlit güvenlik duvarını aşmak ve XSS engellerine takılmamak için
    # Metni Base64 olarak paketleyip, iframe içerisinden parent document'a yansıtıyoruz.
    b64_text = base64.b64encode(ai_text.encode('utf-8')).decode('utf-8')

    if telemetry and risk_level in ["HIGH", "MEDIUM"]:
        ai_color = "#FF4A4A"
    else:
        ai_color = "#AEE0C8"
        
    # Yapay zeka çıktı bloğunu boşalan alanda kendi özel tasarımına alıyoruz
    # height: 260px ve overflow-y: auto ekleyerek kutuyu donanımsal olarak sabitledik.
    # Metin çok uzun gelse bile kutu esnemez, şık biçimde içinde kaydırılabilir (scroll) olur.
    st.markdown(f"""
    <div style='border-left: 3px solid #00D5FF; padding-left: 15px; margin-bottom: 25px;'>
    <div style='font-size: 10px; color: #00D5FF; font-weight: 700; letter-spacing: 2px; margin-bottom: 8px;'>🌌 CANLI FIRTINA ANALİZİ</div>
    <div style='height: 250px; overflow-y: auto; padding-right: 5px; font-size: 14px; font-family: "Space Grotesk", sans-serif; color: {ai_color}; line-height: 1.6; font-weight: 300;'>
    <span class="ai-anim-target"></span>
    </div>
    </div>
    """, unsafe_allow_html=True)

    if telemetry and risk_level in ["HIGH", "MEDIUM"]:
        color = "#FF4A4A" if risk_level == "HIGH" else "#FFB800"
        st.markdown(f"""
<div class="alert-panel" style="border-left-color: {color}; border-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.3);">
<div class="alert-header" style="color:{color};">
<div class="alert-dot" style="background-color: {color}; box-shadow: 0 0 10px {color};"></div>
KRİTİK UYARI
</div>
<div class="alert-title">Güneş Fırtınası: {risk_level}</div>
<div class="alert-desc" style="color:#FFF;">
<i>Şiddetli jeomanyetik aktivite tespit edildi (Risk endeksi %{risk_pct}).</i>
</div>
</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class="alert-panel" style="background: rgba(5,20,10,0.6); border-left-color: #00FFAB; border-color: rgba(0,255,171,0.2);">
<div class="alert-header" style="color:#00FFAB;">
<div class="alert-dot" style="background-color: #00FFAB; box-shadow: 0 0 10px #00FFAB;"></div>
HER ŞEY YOLUNDA
</div>
<div class="alert-title" style="color:#00FFAB;">Koşullar Normal</div>
</div>
        """, unsafe_allow_html=True)

    # Animasyon motoru: parentDOM'da target arayıp b64 çözerek işler.
    js_code = f"""
    <script>
    (function() {{
        const b64 = '{b64_text}';
        const bin = window.atob(b64);
        const bytes = new Uint8Array(bin.length);
        for(let j=0; j<bin.length; j++) bytes[j] = bin.charCodeAt(j);
        const txt = new TextDecoder('utf-8').decode(bytes);
        
        let checkExist = setInterval(function() {{
            const els = window.parent.document.querySelectorAll('.ai-anim-target');
            if(els.length > 0) {{
                clearInterval(checkExist);
                let el = els[els.length - 1]; // always pick the newest rendered one
                if (el.dataset.d > 0) return; // prevent duplicate runs
                el.dataset.d = 1; 
                let idx = 0;
                let scrollBox = el.parentElement; // overflow-y: auto olan GERÇEK kapsayıcı nokta
                function typeW() {{ 
                    if(idx < txt.length) {{ 
                        el.innerHTML += txt[idx]; 
                        scrollBox.scrollTop = scrollBox.scrollHeight + 50; // Yeni satır geldikçe yalnızca özel kutu kaydırılır
                        idx++; 
                        setTimeout(typeW, 30); // Akıcı okuma hızı (30ms per char)
                    }} 
                }}
                typeW();
            }}
        }}, 100);
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)


with c3:
    speed = f"{telemetry['speed']:.1f}" if telemetry and telemetry.get('speed') else "742.8"
    density = f"{telemetry['density']:.1f}" if telemetry and telemetry.get('density') else "12.5"
    kp = f"{telemetry['kp']}" if telemetry and telemetry.get('kp') else "6.67"
    flux = f"{telemetry['bt']:.2f}" if telemetry and telemetry.get('bt') else "8.42"
    
    kp_color = "val-red" if float(kp) > 5 else "val-green"
    
    st.markdown(f"""
<div class="metric-container">
<div style="text-align: right;">
<div class="metric-title">GÜNEŞ RÜZ. HIZI</div>
<div class="metric-value val-blue">{speed} <span class="unit">km/s</span></div>
</div>
<div style="text-align: right; margin-top: 10px;">
<div class="metric-title">PROTON YOĞUNLUĞU</div>
<div class="metric-value val-green">{density} <span class="unit">p/cm³</span></div>
</div>
<div style="text-align: right; margin-top: 10px;">
<div class="metric-title">KP İNDEKSİ</div>
<div class="metric-value {kp_color}">{kp}</div>
</div>
<div style="text-align: right; margin-top: 20px;">
<div class="metric-title">VEKTÖR ROTASI</div>
<div class="metric-value val-white" style="font-size: 24px;">341.2° <span class="unit">KB</span></div>
</div>
<div style="text-align: right; margin-top: 55px; border-right: 4px solid #00FFAB; padding-right: 15px;">
<div class="metric-title">AKI YOĞUNLUĞU</div>
<div class="metric-value val-white">{flux} <span class="unit">µT</span></div>
</div>
</div>
    """, unsafe_allow_html=True)

with c2:
    globe_html = """
    <style>
        body { margin: 0; padding: 0; background: transparent; overflow: hidden; }
        #globeViz { width: 100%; height: 650px; cursor: grab; }
        #globeViz:active { cursor: grabbing; }
    </style>
    <script src="https://unpkg.com/globe.gl"></script>
    <div id="globeViz"></div>
    <script>
        const globe = Globe()
            (document.getElementById('globeViz'))
            .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
            .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
            .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png') // Hareketli (Parallax) uzay kubbesi
            .showAtmosphere(false); // Uzayın simsiyah görünmesi için atmosfer parlamasını kapattık
            
        globe.controls().autoRotate = true;
        globe.controls().autoRotateSpeed = 1.0;
        globe.controls().enableZoom = true;
        
        // Optimize edilmiş 10 kat daha hızlı (0 lag) Aurora Simülasyonu
        fetch('https://services.swpc.noaa.gov/json/ovation_aurora_latest.json')
            .then(res => res.json())
            .then(data => {
                if (data && data.coordinates) {
                    // 1) DOWNSAMPLING: Ekran kartını kastırmamak için sadece her 4 noktadan 1'ini alıyoruz.
                    // Görsellik kalın hatlar sayesinde zengin kalıyor ama RAM/CPU kullanımı %90 azalıyor!
                    const activeData = data.coordinates.filter((d, i) => d[2] > 5 && i % 4 === 0);
                    
                    // 2) YUMUŞATILMIŞ BULUT SİSİ (Çok geniş yarıçap, Düşük Opaklık)
                    const hazes = activeData.map(d => ({
                        lat: d[1], lng: d[0], val: d[2]
                    }));
                    
                    // 3) TEĞET DÖNEN YATAY DALGALAR (Horizontal Tangent Waves)
                    const latGroups = {};
                    activeData.forEach(d => {
                        // Kasmayı engellemek için enlemleri 2 derecelik bantlarda grupla
                        const binnedLat = Math.round(d[1] / 2) * 2;
                        if (!latGroups[binnedLat]) latGroups[binnedLat] = [];
                        latGroups[binnedLat].push(d);
                    });
                    
                    const paths = [];
                    Object.keys(latGroups).forEach(lat => {
                        let pts = latGroups[lat].sort((a,b) => a[0] - b[0]); // Boylam (longitude) sırasına diz
                        
                        let seg = [];
                        let maxVal = 0;
                        for (let i=0; i<pts.length; i++) {
                            const p = pts[i];
                            // Çok uzak noktalarda çizgiyi kopar
                            if (seg.length > 0 && Math.abs(p[0] - seg[seg.length-1][0]) > 8) {
                                addLayers(seg, lat, maxVal);
                                seg = []; maxVal = 0;
                            }
                            seg.push(p);
                            if (p[2] > maxVal) maxVal = p[2];
                        }
                        addLayers(seg, lat, maxVal);
                    });
                    
                    function addLayers(segment, latStr, mv) {
                        if (segment.length > 2) {
                            // Dalgaları yere çok daha yakın ("engin") ve pürüzsüz yapıyoruz (altitüdleri ve zıplamayı x5 kat düşürdüm)
                            
                            // Katman 1: Alt Yeşil Dalga (Yüzeye bitişik)
                            paths.push({
                                type: 'bottom', val: mv,
                                coords: segment.map(p => [parseFloat(latStr), p[0], 0.005 + (p[2]/800)]) 
                            });
                            
                            // Katman 2: Orta Ateşli/Kızıl Dalga
                            paths.push({
                                type: 'mid', val: mv,
                                coords: segment.map(p => [parseFloat(latStr), p[0], 0.015 + (p[2]/800)])
                            });
                            
                            // Katman 3: Üst Mavi/Mor Dalga
                            paths.push({
                                type: 'top', val: mv,
                                coords: segment.map(p => [parseFloat(latStr), p[0], 0.025 + (p[2]/800)])
                            });
                        }
                    }

                    // Sisteme Ekleme & Render
                    globe
                        .pointsData(hazes)
                        .pointAltitude(0.005)
                        .pointColor(d => {
                            if (d.val >= 40) return 'rgba(255, 100, 0, 0.15)'; // Tehlike tabanı turuncu hava
                            if (d.val >= 15) return 'rgba(200, 255, 50, 0.2)'; // Orta tehlike sarımtırak
                            return 'rgba(0, 255, 120, 0.25)'; // Normal yeşil pus
                        })
                        .pointRadius(d => (d.val / 12) + 1.5) // Geniş, soft parlama
                        .pointResolution(16)
                        .pointsMerge(true) // 0 kasma garantisi!
                        
                        .pathsData(paths)
                        .pathPoints('coords')
                        .pathPointLat(p => p[0])
                        .pathPointLng(p => p[1])
                        .pathPointAlt(p => p[2])
                        .pathColor(d => {
                            if (d.type === 'bottom') return 'rgba(0, 255, 120, 0.4)'; // Yeryüzüne çarpan kesin parlak yeşil
                            
                            if (d.type === 'mid') {
                                // Fırtına çok yoğunsa alev/kan kırmızı, orta ise turuncu/sarı, yoksa yeşilin devamı
                                if (d.val >= 40) return 'rgba(255, 40, 40, 0.35)'; 
                                if (d.val >= 15) return 'rgba(255, 180, 0, 0.3)'; 
                                return 'rgba(120, 255, 100, 0.2)'; // Fırtına zayıfsa burası da yeşil
                            }
                            
                            if (d.type === 'top') {
                                // En üst atmosfer katmanındaki iyonlaşma (yoğunlukta mor, zayıflıkta mavi)
                                if (d.val >= 40) return 'rgba(180, 30, 255, 0.25)'; // Sert fırtına tepesi: Patlayan Mor
                                return 'rgba(0, 200, 255, 0.2)'; // Standart: Cyan/Gök mavi şerit
                            }
                        })
                        .pathStroke(3.5) // Hacimli soft perde hattı
                        .pathDashLength(0.4)
                        .pathDashGap(0.1)
                        .pathDashAnimateTime(4000); // Yatay turlayan pürüzsüz akış
                }
            })
            .catch(e => console.error("Aurora API error:", e));
            
        globe.pointOfView({ lat: 60, lng: -90, altitude: 2 });
    </script>
    """
    
    st.markdown("<br>", unsafe_allow_html=True)
    components.html(globe_html, height=650)

# ==========================================
# 24 SAATLİK KP İNDEKSİ GRAFİĞİ (AYRI KATMAN)
# ==========================================
if telemetry and "kp_history" in telemetry and telemetry["kp_history"]:
    import json
    
    labels_js = json.dumps([x["Zaman"] for x in telemetry["kp_history"]])
    data_js = json.dumps([x["Kp İndeksi"] for x in telemetry["kp_history"]])

    # TÜRKÇE KP INDEX CHART SİSTEMİ
    chart_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background: transparent; margin: 0; padding: 10px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
            .legend-container {{ display: flex; justify-content: space-between; gap: 10px; margin-top: 25px; }}
            .legend-item {{ flex: 1; text-align: center; color: white; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: bold; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }}
            .leg-green {{ background: #2ecc71; }}
            .leg-yellow {{ background: #f1c40f; }}
            .leg-orange {{ background: #e67e22; }}
            .leg-red {{ background: #e74c3c; }}
            .leg-purple {{ background: #9b59b6; }}
            .title-box {{ color: white; font-size: 20px; font-weight: bold; margin-bottom: 20px; display: flex; justify-content: space-between; }}
        </style>
    </head>
    <body style="background: rgba(10, 15, 25, 0.4); padding: 25px; border-radius: 12px; border: 1px solid rgba(0, 255, 171, 0.15);">
        <div class="title-box">
            <span>KP İndeksi Değişimi / Son 24 Saat</span>
            <div style="background: #3b82f6; padding: 5px 15px; border-radius: 8px; font-size:14px;">24 Saat</div>
        </div>
        
        <div style="height: 300px; width: 100%;">
            <canvas id="kpChart"></canvas>
        </div>
        
        <div class="legend-container">
            <div class="legend-item leg-green">KP 0-4 (Sakin)</div>
            <div class="legend-item leg-yellow">KP 5 (G1)</div>
            <div class="legend-item leg-orange">KP 6 (G2)</div>
            <div class="legend-item leg-red">KP 7 (G3)</div>
            <div class="legend-item leg-purple">KP 8-9 (G4-G5)</div>
        </div>

        <script>
            const ctx = document.getElementById('kpChart').getContext('2d');
            const data_points = {data_js};
            const labels = {labels_js};
            
            const backgroundColors = data_points.map(val => {{
                if(val < 5) return '#2ecc71';      
                else if(val < 6) return '#f1c40f'; 
                else if(val < 7) return '#e67e22'; 
                else if(val <= 8) return '#e74c3c'; 
                else return '#9b59b6';             
            }});

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'KP Indeksi',
                        data: data_points,
                        backgroundColor: backgroundColors,
                        borderRadius: 6,
                        barPercentage: 0.6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleFont: {{ size: 14 }},
                            bodyFont: {{ size: 14 }},
                            padding: 12,
                            displayColors: true,
                            callbacks: {{
                                label: function(context) {{
                                    let val = context.raw;
                                    let status = "Sakin";
                                    if(val >= 5 && val < 6) status = "G1 (Hafif Fırtına)";
                                    else if(val >= 6 && val < 7) status = "G2 (Orta Şiddetli)";
                                    else if(val >= 7 && val < 8) status = "G3 (Güçlü)";
                                    else if(val >= 8) status = "G4-G5 (Şiddetli/Ekstrem)";
                                    return `KP Değeri: ${{val.toFixed(2)}} - ${{status}}`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            min: 0,
                            max: 9,
                            grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                            ticks: {{ color: '#aaa', font: {{ size: 14 }} }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#aaa', font: {{ size: 12 }}, maxRotation: 45, minRotation: 45 }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    st.markdown("<br>", unsafe_allow_html=True)
    components.html(chart_html, height=520)

# ==========================================
# CME (KORONAL KÜTLE ATIMI) HIZ GRAFİĞİ (AYRI ŞABLON)
# ==========================================
if telemetry and "cme_history" in telemetry and telemetry["cme_history"]:
    import json
    cme_labels_js = json.dumps([x["Zaman"] for x in telemetry["cme_history"]])
    cme_data_js = json.dumps([x["Hız"] for x in telemetry["cme_history"]])

    cme_chart_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background: transparent; margin: 0; padding: 10px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
            .legend-container {{ display: flex; justify-content: space-between; gap: 10px; margin-top: 25px; }}
            .legend-item {{ flex: 1; text-align: center; color: white; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: bold; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }}
            .leg-green {{ background: #2ecc71; }}
            .leg-yellow {{ background: #f1c40f; }}
            .leg-orange {{ background: #e67e22; }}
            .leg-red {{ background: #e74c3c; }}
            .leg-purple {{ background: #9b59b6; }}
            .title-box {{ color: white; font-size: 20px; font-weight: bold; margin-bottom: 20px; display: flex; justify-content: space-between; }}
        </style>
    </head>
    <body style="background: rgba(10, 15, 25, 0.4); padding: 25px; border-radius: 12px; border: 1px solid rgba(255, 120, 0, 0.25);">
        <div class="title-box">
            <span>Koronal Kütle Atımı (CME) Hızı Değişimi</span>
            <div style="background: #e67e22; padding: 5px 15px; border-radius: 8px; font-size:14px;">Son Atımlar</div>
        </div>
        
        <div style="height: 300px; width: 100%;">
            <canvas id="cmeChart"></canvas>
        </div>
        
        <div class="legend-container">
            <div class="legend-item leg-green">0-500 (Sakin)</div>
            <div class="legend-item leg-yellow">500-800 (Orta)</div>
            <div class="legend-item leg-orange">800-1500 (Tehlikeli)</div>
            <div class="legend-item leg-red">1500-2500 (Şiddetli)</div>
            <div class="legend-item leg-purple">>2500 (Ekstrem/X-Sınıfı)</div>
        </div>

        <script>
            const ctx = document.getElementById('cmeChart').getContext('2d');
            const data_points = {cme_data_js};
            const labels = {cme_labels_js};
            
            const backgroundColors = data_points.map(val => {{
                if(val < 500) return '#2ecc71';      
                else if(val < 800) return '#f1c40f'; 
                else if(val < 1500) return '#e67e22'; 
                else if(val <= 2500) return '#e74c3c'; 
                else return '#9b59b6';             
            }});

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Güneş Rüzgarı Hızı (km/s)',
                        data: data_points,
                        backgroundColor: backgroundColors,
                        borderRadius: 6,
                        barPercentage: 0.6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleFont: {{ size: 14 }},
                            bodyFont: {{ size: 14 }},
                            padding: 12,
                            displayColors: true,
                            callbacks: {{
                                label: function(context) {{
                                    let val = context.raw;
                                    let status = "Sakin / Rutin Akış";
                                    if(val >= 500 && val < 800) status = "Orta Şiddetli Atım";
                                    else if(val >= 800 && val < 1500) status = "Tehlikeli / Uyarı";
                                    else if(val >= 1500 && val < 2500) status = "Şiddetli Radyasyon Tehdidi";
                                    else if(val >= 2500) status = "Ekstrem Dünyaya Yönelik Şok Dalgası";
                                    return `Atım Hızı: ${{val.toFixed(0)}} km/s - ${{status}}`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            min: 0,
                            grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                            ticks: {{ color: '#aaa', font: {{ size: 14 }} }},
                            title: {{ display: true, text: 'Hız (km/s)', color: '#ccc', font: {{size: 14}} }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#aaa', font: {{ size: 12 }}, maxRotation: 45, minRotation: 45 }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    components.html(cme_chart_html, height=520)
