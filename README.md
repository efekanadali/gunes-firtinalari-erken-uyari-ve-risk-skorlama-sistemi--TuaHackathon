# Türkiye Uzay Ajansı (TUA) - Erken Uyarı Sistemi & Uzay Havası Dashboard 🚀

![TUA Erken Uyarı Sistemi](tua.png)

## Proje Hakkında
TUA Erken Uyarı Sistemi, Dünya'nın manyetosferini etkileyen gerçek zamanlı Güneş rüzgarları, jeomanyetik fırtınalar ve kütle atımları (CME) gibi ekstrem uzay olaylarını haritalandıran, simüle eden ve **Google Gemini Yapay Zeka** yardımıyla raporlayan interaktif bir uzay hava durumu (Space Weather) konsoludur.

Bu platform, NASA DONKI ve NOAA web servislerini entegre ederek küresel bir durumsal farkındalık (Space Situational Awareness) sunar. Hackathon veya profesyonel demolar için yüksek kaliteli bir Streamlit SaaS arayüzü ile donatılmıştır.

## 🎯 Özellikler

- **Gerçek Zamanlı Telemetri:** NOAA ve NASA CCMC üzerinden Güneş rüzgarı hızı, Kp indeksi, Proton Yoğunluğu, Toplam Manyetik Alan (Bt) ve X-ray radyasyon akısı anlık olarak çekilir.
- **Manyetosfer Simülasyon Motoru:** Sınıfının tek örneği olan fizik simülatörü (`simulation_engine.py`), Akasofu Epsilon enerji girişini hesaplar ve Kopma/Şok Dalgası (Bow Shock) üzerindeki basıncı matematiksel olarak değerlendirip anlık 2B grafiklere döker.
- **Yapay Zeka Raporlama (Gemini 2.5 Flash):** Ham sayısal uzay verilerini bir astrofizikçi gibi okur, fırtına R-Skorlarına göre Olası Risk ve Taktiksel Operasyon Raporları üretir. (Sakin, Aktif, Fırtına, Şiddetli, Ekstrem)
- **3D Aurora Haritalama:** `globe.gl` ve `plotly` gibi entegrasyonlarla anlık güney ve kuzey kutbu Aurora (Kutup Işıkları) ihtimallerini interaktif bir yerküre üzerinde canlandırır.
- **Otomatik Güvenlik & Fallback:** Eğer Gemini API Limitleriniz (429) dolarsa çökme yaşanmaz; akıllı sistem anlık verilerden acil durum senaryo çıktıları basar.

## 🛠️ Kurulum Adımları

**1. Projeyi Klonlayın veya İndirin:**
```bash
git clone https://github.com/KULLANICI_ADINIZ/tua-erken-uyari.git
cd tua-erken-uyari
```

**2. Gereksinimleri Yükleyin:**
Python 3.9 veya daha güncel bir sürüm gereklidir. Gerekli kütüphaneleri kurmak için:
```bash
pip install -r requirements.txt
```

**3. Çevresel Değişkenleri Ayarlayın:**
Ana dizindeki `.env` dosyanıza kendi Google Gemini API anahtarınızı eklemeniz gerekmektedir:
```env
GEMINI_API_KEY=AIzaSy...
```

**4. Sistemi Çalıştırın:**
Terminal üzerinden ana sistemi veya bağımsız modülleri başlatabilirsiniz:
```bash
# Ana Sistem ve Simülatör için:
streamlit run solar_dashboard.py

# Bağımsız Gerçek Zamanlı Aurora Modülü için:
streamlit run uzay_havasi.py
```

## 📂 Dosya Yapısı
* `app.py`: NASA/NOAA veri toplama mekanizması, fırtına tehlike puanı hesaplayıcısı ve AI entegrasyonu.
* `simulation_engine.py`: Güneş rüzgarı dinamiği, O'Brien & McPherron Dst tahmini ve Akasofu bağlanma fonksiyonlarının döndüğü fizik motoru.
* `solar_dashboard.py`: Modern, glassmorphism temalı ana arayüz dosyası. Header, sekme gezinmeleri ve görsel grafiklerin (Canvas, HTML/JS embed) barındığı yer.
* `uzay_havasi.py`: Kutuplardaki aurora faaliyetlerini özel projeksiyon (Plotly) kullanarak anlık raporlayan mini bağımsız uygulama.
* `tua.png`: Arayüzdeki kurumsal logoyu barındırır.
* `.env`: API Key'lerin güvende tutulduğu gizli dosya.

## 📡 Kullanılan API ve Servisler
- [NOAA / SWPC Veri Servisleri](https://www.swpc.noaa.gov/) (Solar Wind, Mag, K-index, Goes X-RAY)
- [NASA DONKI](https://kauai.ccmc.gsfc.nasa.gov/DONKI/) (Coronal Mass Ejection & Flares)
- [Google AI Studio (Gemini Flash)](https://aistudio.google.com/)

---
***Not:** Bu proje Hackathon amaçlı ve tamamen açık kaynak kodlu olarak geliştirilmiştir. Türkiye Uzay Ajansı (TUA) konseptli kurgusal bir veri yönetim ekranı provasıdır.*
