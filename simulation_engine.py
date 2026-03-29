import numpy as np
import math

class SolarStormRiskAlgorithm:
    def __init__(self):
        # Fiziksel Sabitler
        self.RE = 6371.0  # Dünya yarıçapı (km)
        self.RS = 695700.0  # Güneş yarıçapı (km)
        self.AU = 149597870.7  # 1 Astronomik Birim (km)
        self.MU_0 = 4 * np.pi * 1e-7  # Boşluğun manyetik geçirgenliği
        self.gamma_default = 0.2e-7  # Standart sürüklenme katsayısı (km^-1) [1, 2]

    def calculate_coupling_functions(self, v_sw, bt, clock_angle):
        """
        Newell ve Akasofu Epsilon enerji transferi hesaplamaları.
        """
        theta_rad = np.radians(clock_angle)
        
        # 1. Akasofu Epsilon (epsilon) hesaplaması güncellemesi (Gelişmiş Oransal Katsayı)
        efficiency = np.sin(theta_rad / 2)**4
        raw_energy = v_sw * (bt**2) * efficiency
        scaling_factor = 0.0005 
        energy_gw = raw_energy * scaling_factor
        
        # Karşılama ekranında sonucun 'eps/1e9' olarak ele alınması nedeniyle
        # Hesapladığımız GW değerini Watt cinsine çevirerek döndürüyoruz.
        epsilon = energy_gw * 1e9
        
        # 2. Newell Bağlaşım Fonksiyonu (dPhi/dt) [5, 6]
        # v_sw^(4/3) * bt^(2/3) * sin(theta/2)^(8/3)
        newell = (v_sw**(4/3)) * (bt**(2/3)) * (np.sin(abs(theta_rad) / 2)**(8/3))
        
        return epsilon, newell

    def predict_dst_change(self, dst_now, v_sw, bz, density):
        """
        O'Brien & McPherron Dst Tahmin Modeli [7]
        """
        # Dinamik Basınç (nPa)
        p_dyn = 2e-6 * density * (v_sw**2)
        
        # Basınç düzeltmeli Dst* [8, 9]
        dst_star = dst_now - 7.26 * np.sqrt(p_dyn) + 11
        
        # vBs (Solar rüzgar sürücüsü)
        v_bs = v_sw * abs(bz) if bz < 0 else 0
        v_bs_mv_m = v_bs * 1e-3  # mV/m cinsine çevrim
        
        # Enjeksiyon (Q) ve Sönüm (tau) [7]
        Q = -4.4 * (v_bs_mv_m - 0.5) if v_bs_mv_m > 0.5 else 0
        tau = 2.4 * np.exp(9.74 / (4.69 + v_bs_mv_m))
        
        # dDst/dt denklemi
        dDst_dt = Q - (dst_star / tau)
        return dDst_dt, p_dyn

    def cme_arrival_toa(self, v_cme, w_bg, r_start=20):
        """
        Drag-Based Model (DBM) ile CME Varış Zamanı (ToA) Tahmini [1, 10]
        """
        r_start_km = r_start * self.RS
        r_target_km = self.AU
        gamma = self.gamma_default
        
        v0 = v_cme
        w = w_bg
        s = 1 if v0 > w else -1
        
        # Mesafe-Zaman denkleminin sayısal çözümü (Analitik basitleştirme)
        # R(t) = (s/gamma) * ln(1 + s*gamma*(v0-w)*t) + w*t + R0
        # Bu fonksiyon t için kök bulma gerektirir. Basit bir yaklaşım:
        t_seconds = 0
        dt = 600  # 10 dakikalık adımlar
        r_current = r_start_km
        
        while r_current < r_target_km and t_seconds < 500000: # Max 5-6 gün
            v_t = (v0 - w) / (1 + s * gamma * (v0 - w) * t_seconds) + w
            r_current += v_t * dt
            t_seconds += dt
            
        return t_seconds / 3600, v_t # Saat ve varış hızı (km/s)

    def calculate_global_risk_score(self, kp, dst, proton_flux, xray_flux, newell):
        """
        Ağırlıklı Non-Lineer Risk Skoru (R)
        """
        # 1. Normalizasyon (0-1 arası)
        n_kp = kp / 9.0
        n_dst = min(abs(dst) / 400.0, 1.0)
        n_proton = min(np.log10(proton_flux + 1) / 5.0, 1.0)
        n_xray = min((np.log10(xray_flux) + 8) / 5.0, 1.0) # -8 (A) to -3 (X)
        n_newell = min(newell / 10000.0, 1.0)
        
        # 2. Ağırlıklar 
        weights = {'kp': 0.25, 'dst': 0.20, 'proton': 0.20, 'xray': 0.15, 'newell': 0.20}
        
        raw_score = (n_kp * weights['kp'] + n_dst * weights['dst'] + 
                     n_proton * weights['proton'] + n_xray * weights['xray'] + 
                     n_newell * weights['newell'])
        
        # 3. Sigmoid Aktivasyonu (Keskinlik ve Eşikleme)
        k = 12  # Diklik katsayısı
        alpha = 0.45 # Eşik kaydırma
        risk_index = 10 / (1 + np.exp(-k * (raw_score - alpha)))
        
        return round(risk_index, 2)
