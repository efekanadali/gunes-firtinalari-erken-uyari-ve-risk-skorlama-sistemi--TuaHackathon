<div align="center">

<img src="tua.png" alt="TUA Logo" height="100"/>

# 🌌 Güneş Fırtınaları Erken Uyarı ve Risk Skorlama Sistemi

### *Solar Storm Early Warning & Risk Scoring System*

---

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![NOAA](https://img.shields.io/badge/NOAA-SWPC%20Real--Time-006994?style=for-the-badge)
![NASA](https://img.shields.io/badge/NASA-DONKI%20API-FC3D21?style=for-the-badge&logo=nasa&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)
![TUA Hackathon](https://img.shields.io/badge/TUA%20Hackathon-2026-FFD700?style=for-the-badge)

**Gerçek zamanlı uzay hava durumu izleme, yapay zeka destekli analiz ve bilimsel fizik modelleri ile güçlendirilmiş,**
**ulusal kritik altyapıları güneş fırtınalarına karşı korumaya yönelik kapsamlı bir erken uyarı platformu.**

[🚀 Hızlı Başlangıç](#-kurulum-ve-çalıştırma) · [🔬 Bilimsel Altyapı](#-bilimsel-altyapı-ve-modeller) · [🏗️ Mimari](#%EF%B8%8F-sistem-mimarisi-ve-veri-akışı) · [🛣️ Gelecek Çalışmalar](#%EF%B8%8F-gelecek-çalışmalar-future-work)

</div>

---

## 🎯 Proje Vizyonu

Güneş fırtınaları; elektrik şebekeleri, GPS/navigasyon sistemleri, iletişim altyapısı ve düşük yörünge uyduları üzerinde yıkıcı etkiler bırakabilir. **1989 Quebec Karartması**, 9 saat süren bölgesel elektrik kesintisiyle 2 milyar dolar ekonomik kayba yol açmış; **2003 Holloween Fırtınaları** ise 47 uydunun görev dışı kalmasına neden olmuştur.

Bu proje, Türkiye'nin uzay hava durumu farkındalığını artırmak ve ulusal kritik altyapıları proaktif biçimde korumak amacıyla **TUA (Türkiye Uzay Ajansı) Hackathon 2026** kapsamında geliştirilmiştir. Sistem; NOAA/NASA'nın gerçek zamanlı uydu telemetrisini, kanıtlanmış fizik tabanlı matematiksel modelleri ve Google Gemini yapay zekasını tek bir operasyonel platformda birleştirmektedir.

---

## ✨ Temel Özellikler

| Özellik | Açıklama |
|---|---|
| 🌐 **Canlı 3D Dünya Globu** | `globe.gl` ile render edilen dönen Dünya üzerinde NOAA OVATION aurora verilerinin katmanlı görselleştirilmesi |
| 🧲 **Manyetosfer Simülasyonu** | Canvas API tabanlı, gerçek zamanlı parametrik Bow-Shock, magnetotail ve kutup ışığı animasyonu |
| 🤖 **Gemini AI Analizi** | `gemini-2.5-flash` ile gerçek zamanlı verilere dayalı astrofiziksel durum değerlendirmesi ve TUA taktik raporu üretimi |
| 📡 **8 Kanallı Telemetri** | Kp İndeksi, Dst, Güneş Rüzgarı Plazması, X-ışını, Proton Akısı, CME (NASA DONKI), Manyetik Alan (Bx/By/Bz/Bt) |
| 🔬 **Fizik Tabanlı Risk Motoru** | Akasofu ε, Newell Bağlaşım Fonksiyonu, O'Brien–McPherron Dst tahmin ve DBM CME varış modelleri |
| 📊 **Gerçek Zamanlı Grafikler** | 24 saatlik Kp İndeksi trend barı ve son 20 CME olayı hız geçmişi (Chart.js) |
| 🗺️ **Aurora Haritası** | NOAA OVATION API ile polar projeksiyon üzerinde kuzey/güney yarımküre aurora yoğunluk haritası |
| ⚡ **Anlık Uyarı Sistemi** | Animasyonlu, renkli durum paneli (LOW / MEDIUM / HIGH) ile operatör odaklı kritik uyarılar |

---

## 🔬 Bilimsel Altyapı ve Modeller

Sistem, uzay havası fiziğinde hakemli dergilerde yayımlanmış kanıtlanmış modelleri uygulamaktadır. Tüm hesaplamalar [`simulation_engine.py`](simulation_engine.py) içindeki `SolarStormRiskAlgorithm` sınıfında barındırılmaktadır.

---

### 1. Akasofu Epsilon (ε) — Güneş Rüzgarı–Manyetosfer Enerji Transferi

Güneş rüzgarının Dünya'nın manyetosferi içine aktardığı toplam enerjiyi (GW cinsinden) hesaplar.

```
ε = v_sw × Bt² × sin⁴(θ/2) × k
```

| Sembol | Açıklama | Birim |
|---|---|---|
| `v_sw` | Güneş rüzgarı hızı | km/s |
| `Bt` | Toplam manyetik akı yoğunluğu (√(Bx²+By²+Bz²)) | nT |
| `θ` | IMF saat açısı (`atan2(By, Bz)`) | derece |
| `k` | Ölçeklendirme katsayısı (`0.0005`) | — |

> **Fiziksel Yorum:** Saat açısı tam güneye (`θ = 180°`) yaklaştığında `sin⁴` terimi maksimuma ulaşır; bu durum, IMF'nin güneye yönelmesiyle manyetopoza en büyük enerji geçişinin yaşandığını fiziksel olarak doğrular.

> **Referans:** Akasofu, S.-I. (1981). *Energy coupling between the solar wind and the magnetosphere*. Space Science Reviews, 28(2), 121–190.

---

### 2. Newell Bağlaşım Fonksiyonu (dΦ/dt) — Manyetik Akı Transferi Oranı

Gün tarafı yeniden bağlanma oranını ve kutup ışığı üretim potansiyelini nicel olarak ifade eder.

```
dΦ/dt = v_sw^(4/3) × Bt^(2/3) × sin^(8/3)(|θ|/2)
```

Bu fonksiyon, Kp İndeksi ve aurora aktivitesiyle yüksek korelasyon göstermekte olup ağırlıklı risk skoru hesaplamasında `newell` parametresi olarak kullanılmaktadır.

> **Referans:** Newell, P.T. et al. (2007). *A nearly universal solar wind-magnetosphere coupling function inferred from 10 magnetospheric state variables*. JGR Space Physics, 112(A1). doi:10.1029/2006JA012015

---

### 3. O'Brien & McPherron Dst Tahmin Modeli — Jeomanyetik Fırtına Tahmini

Mevcut Dst değerinden ve güneş rüzgarı parametrelerinden yola çıkarak fırtına şiddetinin nasıl gelişeceğini tahmin eder.

**Adım 1 — Dinamik Basınç ve Basınç Düzeltmeli Dst\***
```
P_dyn = 2×10⁻⁶ × n × v_sw²           [nPa]
Dst*  = Dst - 7.26 × √(P_dyn) + 11
```

**Adım 2 — Enjeksiyon (Q) ve Sönüm (τ) Terimleri**
```
vBs = v_sw × |Bz|   (yalnızca Bz < 0 iken; güneye yönlü bileşen)

Q   = -4.4 × (vBs [mV/m] - 0.5)      [eğer vBs > 0.5 mV/m]
τ   =  2.4 × exp(9.74 / (4.69 + vBs))
```

**Adım 3 — Dst Değişim Hızı**
```
dDst/dt = Q - (Dst* / τ)
```

> **Referans:** O'Brien, T.P. & McPherron, R.L. (2000). *An empirical phase space analysis of ring current dynamics*. JGR Space Physics, 105(A4), 7707–7719. doi:10.1029/1998JA000437

---

### 4. Drag-Based Model (DBM) — CME Varış Zamanı (ToA) Tahmini

Koronal Kütle Atımının (CME) Dünya'ya ulaşma süresini, heliospheric sürükleme kuvvetleri dikkate alınarak hesaplar.

**Hareket Denklemi (sürükleme ivmesi):**
```
dv_CME/dt = -γ × (v_CME - w) × |v_CME - w|
```

**Analitik Hız Profili:**
```
v(t) = (v₀ - w) / [1 + s × γ × (v₀ - w) × t]  +  w
```

**Mesafe-Zaman Sayısal İntegrasyonu (Δt = 600 s adımlarla):**
```
R(t + Δt) = R(t) + v(t) × Δt

Başlangıç : R₀ = 20 R☉  ≈ 13,914,000 km
Hedef     : R  = 1 AU   = 149,597,870 km
```

| Parametre | Değer | Açıklama |
|---|---|---|
| `γ` | 0.2 × 10⁻⁷ km⁻¹ | Standart heliospheric sürükleme katsayısı |
| `w` | `v_sw` (slider) | Arka plan güneş rüzgarı hızı |
| `v₀` | CME hızı (slider) | Başlangıç CME hızı |
| `s` | +1 veya −1 | Yön işareti (v₀ > w → +1) |

> **Referans:** Vršnak, B. et al. (2013). *Propagation of Interplanetary CMEs: The Drag-Based Model*. Solar Physics, 285(1-2), 295–315. doi:10.1007/s11207-012-0035-4

---

### 5. Ağırlıklı Non-Lineer Risk Skoru (R) — Küresel Tehlike Endeksi

Beş fiziksel parametreyi logaritmik normalizasyon ve sigmoid aktivasyon ile birleştirerek **0–10** aralığında bir operasyonel risk endeksi üretir.

**Normalizasyon (her parametre 0–1 aralığına çekilir):**
```
n_Kp     = Kp / 9.0
n_Dst    = min(|Dst| / 400.0, 1.0)
n_proton = min(log10(φ_p + 1) / 5.0, 1.0)
n_Xray   = min((log10(F_X) + 8) / 5.0, 1.0)    # A sınıfı=-8, X sınıfı=-3
n_Newell = min(Φ_Newell / 10000.0, 1.0)
```

**Ağırlıklı Ham Skor:**
```
R_raw = 0.25·n_Kp + 0.20·n_Dst + 0.20·n_proton + 0.15·n_Xray + 0.20·n_Newell
```

**Sigmoid Aktivasyonu (k=12, α=0.45):**
```
R = 10 / (1 + e^(-12 × (R_raw - 0.45)))
```

> **Tasarım Gerekçesi:** Sigmoid fonksiyon, olağan koşullarda skoru düşük tutarken fırtına eşiği aşıldığında keskin bir geçişle yüksek risk değerlerine hızla ulaşmayı sağlar. Bu yaklaşım, gerçek jeomanyetik fırtınaların ani başlangıç (`sudden commencement`) karakteriyle birebir örtüşmektedir.

---

## 🗺️ Veri Kaynakları

| Kaynak | API Endpoint | Veri Türü | Yenileme |
|---|---|---|---|
| NOAA SWPC | `planetary_k_index_1m` | Kp İndeksi | 1 dakika |
| NOAA SWPC | `solar-wind/plasma-1-day` | v_sw, yoğunluk | Sürekli |
| NOAA SWPC | `solar-wind/mag-1-day` | Bx, By, Bz, Bt | Sürekli |
| NOAA SWPC | `goes/primary/xrays-1-day` | X-ışını akısı | Sürekli |
| NOAA SWPC | `goes/primary/integral-protons-1-day` | Proton akısı (≥10 MeV) | Sürekli |
| NOAA SWPC | `ovation_aurora_latest` | Aurora yoğunluk haritası | 5 dakika |
| NOAA SWPC | `kyoto-dst` | Dst İndeksi | Saatlik |
| NASA CCMC DONKI | `get/CME` | Koronal Kütle Atımı hız/zaman | Olay bazlı |
| NASA CCMC DONKI | `get/FLR` | Güneş patlaması sınıfı | Olay bazlı |

---

## 🏗️ Sistem Mimarisi ve Veri Akışı

```
┌─────────────────────────────────────────────────────────────────────┐
│                     NOAA SWPC  /  NASA CCMC DONKI                   │
│              (Gerçek Zamanlı Uzay Hava Durumu Uydu Verileri)        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  HTTP REST API (JSON)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    app.py  ←─── .env (GEMINI_API_KEY)               │
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────┐  ┌─────────────┐   │
│  │ get_space_weather()  │  │ calculate_risk() │  │ Gemini AI   │   │
│  │ 8-Kanal Telemetri    │─▶│ Eşik Tabanlı     │  │ ai_insight  │   │
│  │ Veri Derleme         │  │ Puanlama (0-15)  │  │ sim_report  │   │
│  └──────────────────────┘  └──────────────────┘  └─────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  Python import
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      simulation_engine.py                           │
│             SolarStormRiskAlgorithm (Fizik Modeli Sınıfı)           │
│                                                                     │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │ calculate_coupling_ │  │ predict_dst_     │  │ cme_arrival  │   │
│  │ functions()         │  │ change()         │  │ _toa()       │   │
│  │ Akasofu ε + Newell  │  │ O'Brien-McPherron│  │ DBM Modeli   │   │
│  └─────────────────────┘  └──────────────────┘  └──────────────┘   │
│                    └──────────────┬──────────────┘                  │
│                   calculate_global_risk_score()                     │
│                   Sigmoid Aktivasyonlu R Skoru (0–10)               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  Python import
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   solar_dashboard.py  (Ana UI)                      │
│                                                                     │
│  ┌─────────────────────────┐   ┌──────────────────────────────┐    │
│  │ Küresel Görünüm         │   │ Manyetosfer Simülasyonu       │    │
│  │ globe.gl 3D Dünya Globu │   │ Canvas API + Parametrik Fizik │    │
│  │ NOAA OVATION Aurora     │   │ Bow-Shock, Magnetotail, Kutup │    │
│  │ Overlay (Çok katmanlı)  │   │ Işıkları, Güneş Koronası     │    │
│  └─────────────────────────┘   └──────────────────────────────┘    │
│                                                                     │
│  ┌──────────────────────┐   ┌─────────────────────────────────┐    │
│  │ 24s Kp İndeksi Grafik│   │ CME Hız Geçmişi (Chart.js)      │    │
│  │ (Chart.js - Renk Kodu│   │ Son 20 olay, km/s sınıflandırma │    │
│  └──────────────────────┘   └─────────────────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ AI Analiz Paneli — Base64 + Typewriter Animasyonu (JS)      │   │
│  │ Durum:  LOW (yeşil)  /  MEDIUM (sarı)  /  HIGH (kırmızı)   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
              ↑
┌─────────────────────────────────────────────────────────────────────┐
│  uzay_havasi.py  (Bağımsız Aurora Haritası Sayfası)                 │
│  NOAA OVATION → Plotly Scattergeo → Polar Projeksiyon              │
│  Kuzey / Güney yarımküre filtreli yoğunluk görselleştirmesi        │
└─────────────────────────────────────────────────────────────────────┘
```

### Modül Sorumlulukları

| Dosya | Satır Sayısı | Sorumluluk |
|---|---|---|
| [`app.py`](app.py) | 290 | Veri çekme (8 API kanalı), eşik tabanlı risk puanlama, Google Gemini entegrasyonu |
| [`simulation_engine.py`](simulation_engine.py) | 107 | Fizik tabanlı matematiksel modeller (`SolarStormRiskAlgorithm` sınıfı) |
| [`solar_dashboard.py`](solar_dashboard.py) | 1118 | Streamlit UI: Glassmorphism tasarım, 3D glob, Canvas animasyonu, grafikler, AI paneli |
| [`uzay_havasi.py`](uzay_havasi.py) | 89 | Bağımsız NOAA OVATION aurora haritası sayfası (polar projeksiyon) |

---

## 🚀 Kurulum ve Çalıştırma

### Ön Gereksinimler

- Python **3.10** veya üzeri
- `pip` paket yöneticisi
- Google AI Studio'dan alınmış Gemini API anahtarı → [aistudio.google.com](https://aistudio.google.com)

---

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/efekanadali/gunes-firtinalari-erken-uyari-sistemi.git
cd gunes-firtinalari-erken-uyari-sistemi
```

---

### 2. Sanal Ortam Oluşturun (Önerilen)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

---

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

**`requirements.txt` içeriği:**

```
streamlit>=1.20.0
requests>=2.28.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
numpy>=1.23.0
plotly>=5.14.0
```

---

### 4. Ortam Değişkenlerini Yapılandırın

Proje kök dizininde `.env` dosyası oluşturun:

```ini
# .env
GEMINI_API_KEY=your_gemini_api_key_here
```

> ⚠️ **Güvenlik Notu:** `.env` dosyası `.gitignore` kapsamındadır ve asla versiyon kontrolüne eklenmemelidir. API anahtarını kaynak koda gömmeyin — `python-dotenv` kütüphanesi bu anahtarı güvenli biçimde ortam değişkeni olarak yükler.

---

### 5. Uygulamayı Başlatın

**Ana Dashboard (Tüm özellikler):**
```bash
streamlit run solar_dashboard.py
```

**Bağımsız Aurora Haritası:**
```bash
streamlit run uzay_havasi.py
```

**Veri API Testi (Konsol çıktısı):**
```bash
python app.py
```

Tarayıcınızda otomatik olarak `http://localhost:8501` adresi açılacaktır.

---

## 📱 Uygulama Görünümleri

### Küresel Görünüm (`Küresel Görünüm` sekmesi)
- **Sol panel:** Google Gemini yapay zeka analizi (typewriter animasyonu) + durum uyarı kartı
- **Orta panel:** Dönen 3D Dünya globu + NOAA OVATION aurora overlay (gerçek zamanlı, çok katmanlı)
- **Sağ panel:** Canlı telemetri metrikleri — güneş rüzgarı hızı, Kp, proton yoğunluğu, manyetik akı
- **Alt bölüm:** 24 saatlik Kp İndeksi trend grafiği + CME hız geçmiş grafiği

### Manyetosfer Simülasyonu (`Manyetosfer Simülasyonu` sekmesi)
- Parametreli slider kontrolleri: `v_sw`, `density`, `Bz`, `Bt`, `Kp`, `proton_flux`, `xray_flux`, `CME speed`
- Canvas animasyonu: Güneş koronal plazması, bow-shock kalkan, Dünya, magnetotail, kutup ışıkları
- Anlık model çıktıları: Akasofu ε (GW), dinamik basınç (nPa), CME varış süresi (saat), Risk R/10
- **"📡 DURUM RAPORU AL"** butonu → Gemini AI taktik raporu üretimi

---

## ⚙️ Risk Sınıflandırması ve Operasyonel Eylem Planı

| Risk Seviyesi | R Skoru | Kp Eşdeğeri | Operasyonel Eylem |
|---|---|---|---|
| 🟢 **Sakin** | 0.0 – 2.99 | Kp 0-2 | Standart operasyonlara devam et |
| 🟡 **Aktif** | 3.0 – 4.99 | Kp 3-4 | HF radyo izleme; yedek iletişim hazırlığı |
| 🟠 **Hafif-Orta Fırtına** | 5.0 – 6.99 | Kp 5-6 (G1-G2) | GPS hassas işlemleri durdur; şebeke dengeleme aktif et |
| 🔴 **Şiddetli Fırtına** | 7.0 – 8.99 | Kp 7-8 (G3-G4) | Uyduları güvenli moda al; polar rotaları kapat |
| 🟣 **Ekstrem Fırtına** | 9.0 – 10.0 | Kp 9 (G5) | Kritik yükleri izole et; kontrollü yük kesintisi uygula |

---

## 🛣️ Gelecek Çalışmalar (Future Work)

### Faz 2 — Gelişmiş Tahmin Motoru
- [ ] **LSTM / Transformer tabanlı Kp tahmin modeli** — Son 72 saatlik telemetriyi kullanarak 6-24 saat ileriye yönelik Kp İndeksi tahmini
- [ ] **WSA-ENLIL kozmik rüzgar simülatörü entegrasyonu** — NASA CCMC heliospheric plazma modeliyle CME propagasyon takibi
- [ ] **NOAA GOES-R / DSCOVR çoklu uydu besleme entegrasyonu** — Çoğaltılmış telemetri ile hata toleransı ve veri doğrulama

### Faz 3 — Operasyonel Uyarı Altyapısı
- [ ] **SMS/E-posta otomatik bildirim servisi** — Yapılandırılabilir eşik değerlere dayalı uyarı (Twilio, SendGrid entegrasyonu)
- [ ] **Sektörel etki haritalaması** — Türkiye elektrik şebekesi, havacılık koridorları ve uydu filosunun koordinat tabanlı risk analizi
- [ ] **Tarihsel fırtına veri tabanı** — 1989–günümüz büyük olaylarının analizi ve benzer örüntü tespiti için ML modeli

### Faz 4 — Platform Genişletme
- [ ] **REST API endpointleri** — FastAPI tabanlı servis katmanı; üçüncü taraf sistemlerin risk skorlarını çekebileceği açık API
- [ ] **Mobil push-bildirim uygulaması** — React Native / Flutter ile çapraz platform erken uyarı desteği
- [ ] **Çoklu dil ve bölge desteği** — Türkçe, İngilizce, Arapça arayüz lokalizasyonu (Orta Doğu / Orta Asya kapsam genişlemesi)
- [ ] **TUA Erken Uyarı Ağı entegrasyonu** — Sistemin TUA'nın resmi operasyonel veri altyapısına bağlanması

---

## 📚 Kaynaklar ve Referanslar

1. Vršnak, B. et al. (2013). *Propagation of Interplanetary Coronal Mass Ejections: The Drag-Based Model*. **Solar Physics**, 285(1-2), 295–315. doi:10.1007/s11207-012-0035-4
2. Cargill, P. J. (2004). *On the Aerodynamic Drag Force Acting on Interplanetary Coronal Mass Ejections*. Solar Physics, 221(1), 135–149.
3. Akasofu, S.-I. (1981). *Energy coupling between the solar wind and the magnetosphere*. **Space Science Reviews**, 28(2), 121–190.
4. Perreault, P. & Akasofu, S.-I. (1978). *A study of geomagnetic storms*. Geophysical Journal International, 54(3), 547–573.
5. Newell, P.T. et al. (2007). *A nearly universal solar wind-magnetosphere coupling function inferred from 10 magnetospheric state variables*. **JGR Space Physics**, 112(A1). doi:10.1029/2006JA012015
6. Newell, P.T. et al. (2008). *Diffuse, monoenergetic, and broadband aurora: The global precipitation budget*. JGR Space Physics, 113(A9).
7. O'Brien, T.P. & McPherron, R.L. (2000). *An empirical phase space analysis of ring current dynamics: Solar wind control of injection and decay*. **JGR Space Physics**, 105(A4), 7707–7719. doi:10.1029/1998JA000437
8. Burton, R.K., McPherron, R.L. & Russell, C.T. (1975). *An empirical relationship between interplanetary conditions and Dst*. JGR Space Physics, 80(31), 4204–4214.
9. NASA CCMC DONKI API: https://kauai.ccmc.gsfc.nasa.gov/DONKI
10. NOAA Space Weather Prediction Center: https://www.swpc.noaa.gov

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında yayımlanmıştır.

---

<div align="center">

**🌌 Türkiye'nin Uzay Hava Durumu Koruması — TUA Hackathon 2026**

*"Güneş'in öfkesini öngörmek, Dünya'nın direncini artırmaktır."*

Made with ❤️ for **Türkiye Uzay Ajansı (TUA)**

</div>
