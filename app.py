import requests
import math
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    # Güvenlik ve best-practice açısından API anahtarı .env dosyasından çekiliyor.
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    pass

def safe_get_json(url):
    """
    Belirtilen URL'den JSON verisi çekmeyi dener.
    Eğer bir ağ hatası veya zaman aşımı (timeout) olursa uygulamanın çökmesini engeller 
    ve sessizce None değerini döndürür. Dashboard'un kesintisiz çalışması için çok kritiktir.
    """
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def get_space_weather():
    """
    NOAA (Space Weather Prediction Center) ve NASA DONKI API'lerinden 
    gerçek zamanlı (real-time) uzay hava durumu verilerini çeker ve derler.
    Tüm birimleri tek bir sözlük (dictionary) objesinde toplayarak arayüze sunar.
    """
    try:
        # 1. Kp Index: Jeomanyetik fırtınaların temel göstergesidir (0-9 arası değer alır).
        kp_json = safe_get_json("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json")
        kp = kp_json[-1]['kp_index'] if kp_json else None
        
        kp_history = []
        if kp_json:
            # 1 gün = 1440 dakika. API çok fazla veri döndürüyor, son 1 günlük veriyi alıyoruz
            # Grafiğin dolu ve detaylı görünmesi için her 10 dakikada 1 örnek alıyoruz (Toplam 144 Bar)
            last_24h = kp_json[-1440::10] 
            for item in last_24h:
                if "time_tag" in item and "kp_index" in item:
                    kp_history.append({"Zaman": item["time_tag"][11:16], "Kp İndeksi": float(item["kp_index"])})

        # 2. Solar Wind Plasma (Güneş Rüzgarı Plazması): Parçacık yoğunluğu (density) ve hızını (speed) ölçer.
        plasma_json = safe_get_json("https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json")
        if plasma_json and len(plasma_json) > 1:
            last = plasma_json[-1]
            density = float(last[1]) if last[1] is not None else None
            speed = float(last[2]) if last[2] is not None else None
        else:
            density = speed = None

        # 3. Magnetic Field (Manyetik Alan): Dünyanın manyetik alanına vuran gücü ölçer.
        # Özellikle 'bz' (Z eksenindeki manyetik sapma) fırtına tespiti için hayati önem taşır.
        mag_json = safe_get_json("https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json")
        if mag_json and len(mag_json) > 1:
            last = mag_json[-1]
            try:
                bz = float(last[3]) # Gezegenler arası manyetik alanın dikey bileşeni (-) ise tehlikedir.
                bx = float(last[1])
                by = float(last[2])
                bt = math.sqrt(bx**2 + by**2 + bz**2) # Toplam manyetik akı yoğunluğu hesaplaması
                clock_angle = math.degrees(math.atan2(by, bz))
            except (TypeError, ValueError):
                bz = bt = clock_angle = None
        else:
            bz = bt = clock_angle = None

        # 4. X-ray Flux: Güneş patlamalarının (Solar Flare) şiddetini belirlemekte kullanılır.
        xray_json = safe_get_json("https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json")
        xray = float(xray_json[-1]['flux']) if xray_json else None

        # 5. Proton Flux: Radyasyon fırtınaları tehlikesini ölçer. Yüksek enerjili (>=10 MeV) protonlar baz alınır.
        proton_json = safe_get_json("https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json")
        proton_flux = None
        if proton_json:
            for entry in reversed(proton_json):
                if entry.get('energy') == '>=10 MeV':
                    proton_flux = float(entry['flux'])
                    break

        # 6. CME (Coronal Mass Ejection): NASA DONKI'den uyduları vurabilecek kütle atımlarının hızı çekilir.
        cme_json = safe_get_json("https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/CME")
        cme_speed = None
        cme_history = []
        if cme_json:
            for cme in reversed(cme_json):
                if cme.get("cmeAnalyses") and len(cme["cmeAnalyses"]) > 0:
                    speed_val = cme["cmeAnalyses"][0].get("speed")
                    time_val = cme.get("startTime", "")[:10] # Sadece tarihi YYYY-MM-DD olarak alalım
                    if speed_val is not None:
                        cme_history.insert(0, {"Zaman": time_val, "Hız": float(speed_val)}) # En eski gün başa gelsin

            # Listeyi sadece son 20 olay ile sınırlayalım (Chart'ın taşmaması için)
            cme_history = cme_history[-20:]

            # Güncel hızı almak için yine en güncel (en son) değere bakıyoruz
            for cme in reversed(cme_json):
                if cme.get("cmeAnalyses") and len(cme["cmeAnalyses"]) > 0:
                    speed_val = cme["cmeAnalyses"][0].get("speed")
                    if speed_val is not None:
                        cme_speed = float(speed_val)
                        break

        # 7. Dst Index (Disturbance Storm Time): Ekvatoral manyetik alan değişimini ölçer (Şiddetli fırtınalarda çok düşer).
        dst_json = safe_get_json("https://services.swpc.noaa.gov/products/kyoto-dst.json")
        dst = None
        if dst_json and len(dst_json) > 1:
            last_entry = dst_json[-1]
            try:
                if isinstance(last_entry, dict):
                    dst = float(last_entry.get("dst"))
                else:
                    dst = float(last_entry[1])
            except:
                dst = None

        # 8. Solar Flare (Güneş Patlaması Sınıfı): X-class (Ekstra Şiddetli), M-class (Orta) vb. sınıf tespiti.
        flare_json = safe_get_json("https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/FLR")
        solar_flare = None
        if flare_json:
            solar_flare = flare_json[-1].get("classType")

        return {
            "kp": kp,
            "kp_history": kp_history,
            "dst": dst,
            "speed": speed,
            "density": density,
            "bz": bz,
            "bt": bt,
            "xray": xray,
            "proton_flux": proton_flux,
            "clock_angle": clock_angle,
            "cme_speed": cme_speed,
            "cme_history": cme_history,
            "solar_flare": solar_flare
        }

    except Exception as e:
        print("API Verisi derlenirken hata oluştu:", e)
        return None


def calculate_risk(data):
    """
    Gelen API verilerini analiz edip puanlayarak (skor) mevcut uzay hava durumunun 
    DÜŞÜK, ORTA veya YÜKSEK riskli olduğunu belirten algoritmik bir fonksiyon.
    """
    if not data:
        return "UNKNOWN", 0

    score = 0
    max_score = 15  # Algoritmamızın üretebileceği en yüksek fırtına şiddeti puanı

    # --- ANA PARAMETRELER (Kritik skora etki eden temel uzay olayları) ---
    if data.get("kp") is not None and data["kp"] >= 5:       # Kp 5 ve üzeri = G1 jeomanyetik fırtına
        score += 2
    if data.get("speed") is not None and data["speed"] > 600:# Yüksek hızlı güneş rüzgarı (600 km/s üzeri)
        score += 2
    if data.get("bz") is not None and data["bz"] < 0:        # Güneye (Southward) dönük manyetik alan (Yırtıcı etki yaratır)
        score += 3
    if data.get("xray") is not None and data["xray"] > 1e-5: # Radyasyon parlaması
        score += 1

    # --- EK PARAMETRELER VE NASA ANOMALİLERİ ---
    if data.get("proton_flux") is not None and data["proton_flux"] > 10:
        score += 1
    if data.get("cme_speed") is not None and data["cme_speed"] > 1000:   # 1000km/s hıza sahip sert kütle atımları
        score += 1
    if data.get("dst") is not None and data["dst"] < -100:               # Ciddi ekvatoral manyetik bozulma
        score += 2

    # --- GÜNEŞ PATLAMASI TİPİ (X ve M sınıfları tehlikelidir) ---
    if data.get("solar_flare"):
        flare_class = data["solar_flare"].upper()
        if flare_class.startswith("X"): # X-class en şiddetli olanıdır, sistemi çökertebilir.
            score += 3
        elif flare_class.startswith("M"):
            score += 1

    # Puanı klasifiye et (Dashboard'daki arayüz alert renkleri bu string değere bağlıdır)
    if score >= 8:
        level = "HIGH"
    elif score >= 4:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Yüzdelik Oran (Dashboard arayüzünde gösterilecek % bazlı tehlike oranı)
    percentage = (score / max_score) * 100

    return level, round(percentage, 2)


def generate_ai_insight(speed, density, kp, bz, bt, risk_level):
    """
    Google Gemini API kullanarak anlık uzay hava durumu verilerini 
    bir astrofizikçi gibi değerlendirir.
    """
    try:
        # Hızlı çıkarımlar için en güncel gemini flash sürümü kullanılıyor
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Sen bir uzay hava durumu (Space Weather) meteoroloğusun. Ekranda okuduğun gerçek zamanlı NOAA uydu verileri şunlar:
        - Güneş Rüzgarı Hızı: {speed} km/s
        - Proton Yoğunluğu: {density} p/cm³
        - Toplam Manyetik Alan (Bt): {bt} nT
        - Dikey Manyetik Sapma (Bz): {bz} nT
        - Kp İndeksi: {kp} (Jeomanyetik fırtına ölçeği)

        GÖREV:
        Bu verileri dikkate alarak, şu anki uzay hava durumunu ve Dünya'daki olası etkilerini (Radyo frekansları, uydu navigasyonu, Aurora ihtimali) detaylıca yorumla.
        1. Yorumunu yaparken MUTLAKA yukarıdaki sayılara ve değerlere (örn: "Hızın {speed} km/s olması nedeniyle..." veya "Kp indeksinin {kp} seviyesinde olması gösteriyor ki...") atıfta bulunarak gerekçe sun. Verileri neden topladığını ve bunların ne anlama geldiğini açıkla.
        2. Bilimsel, ciddi ve profesyonel bir dille, durumu özetleyen net bir astrofiziksel analiz oluştur. 
        3. Çok uzun olmasın (en fazla 3 cümle büyüklüğünde, yoğun bilgi içersin). "Merhaba", "Analizim şu şekilde" gibi giriş kelimeleri kullanmadan, doğrudan tespitlerinle başla.
        """
        response = model.generate_content(prompt)
        text = response.text.replace('\n', ' ').strip()
        # Varsa Markdown ** işaretlerini kaldır
        text = text.replace('**', '')
        return text
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota" in error_str or "quota" in error_str.lower():
            return "⚠️ Gemini API Limiti Doldu (429 Quota Exceeded)! Lütfen .env dosyasındaki GEMINI_API_KEY değerini yeni bir anahtarla güncelleyip projeyi tekrar çalıştırın."
        else:
            import traceback
            return f"Model Hatası: {str(e)} - {traceback.format_exc()}"


def generate_simulation_report(risk_score):
    """
    Kullanıcının ürettiği R skoruna göre uzay durumunu, olası etkileri
    ve eylem planını bir tablo matrisinden alarak LLM'e şık bir TUA Raporu yazdırır.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        score = float(risk_score)
        
        # Risk Tablosu Senaryo Matrisi
        if score <= 2.99:
            context = "Seviye: Sakin (Quiet). Etki: Her şey normal. GPS hatası milimetre düzeyinde. Eylem: Standart operasyonlara devam et."
        elif score <= 4.99:
            context = "Seviye: Aktif (Unsettled). Etki: HF (Kısa Dalga) Radyo: Kutup bölgelerinde parazitlenme başlar. Eylem: Radyo operatörlerini uyar. Yedek iletişim kanallarını kontrol et."
        elif score <= 6.99:
            context = "Seviye: Fırtına (Minor/Mod). Etki: Navigasyon: GPS'te birkaç metrelik sapma olur. Güç: Trafo merkezlerinde voltaj dalgalanmaları görülür. Eylem: Güç şebekesi dengeleme sistemlerini aktif et. Hassas GPS gerektiren (drone vb.) işleri durdur."
        elif score <= 8.99:
            context = "Seviye: Şiddetli (Severe). Etki: Uydu: Uyduların yön bulma sistemleri (star-tracker) bozulabilir. Havacılık: Pilotlar kutup rotasından kaçınır. Eylem: Uyduları 'Güvenli Mod'a (Safe Mode) al. Havayolu rotalarını alçak enlemlere kaydır."
        else:
            context = "Seviye: Ekstrem (Extreme). Etki: Güç Şebekesi: Trafolar yanabilir, bölgesel elektrik kesintileri (blackout) olur. İnternet: Denizaltı kabloları zarar görebilir. Eylem: Kritik yükleri (hastaneler vb.) ayır. Şebekede kontrollü kesintiler (load shedding) yap."

        prompt = f"""
        Sen Türkiye Uzay Ajansı (TUA) Erken Uyarı Sistemi yapay zekasısın. 
        Kullanıcı bir manyetosfer simülasyonu çalıştırdı ve sentetik Risk Skoru (R) {risk_score}/10 çıktı.
        Bu skora göre tablo verimiz şöyledir: "{context}"

        TUA Operasyon Merkezi için kısa, askeri netlikte ve profesyonel bir durum raporu (Aksiyon Planı) yaz. 
        Cevabın 3 cümleyi aşmasın. "Merhaba" vb. girişler olmadan doğrudan durumu, beklenen etkiyi ve alınması gereken önlemi net bir komut veya uyarı formatında belirterek yaz.
        """
        response = model.generate_content(prompt)
        text = response.text.replace('\n', ' ').strip()
        text = text.replace('**', '')
        return text
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota" in error_str or "quota" in error_str.lower():
            return "⚠️ Gemini API Limiti Doldu! Rapor oluşturulamadı."
        return f"Rapor Oluşturma Hatası: {str(e)}"


if __name__ == "__main__":
    # Test Modu: Script doğrudan çalıştırılırsa verileri konsola basar.
    data = get_space_weather()

    print("Güncel Uzay Hava Verisi (NOAA/NASA Taraması):")
    if data:
        for k, v in data.items():
            print(f"  {k}: {v}")

    level, pct = calculate_risk(data)
    print(f"\nSistem Tarafindan Hesaplanmış Tahmini Risk Seviyesi: {level} (%{pct})")