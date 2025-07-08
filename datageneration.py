import pandas as pd
import numpy as np
import random

# Sabitler
n = 1000
np.random.seed(42)
random.seed(42)

# Yardımcı listeler
medeni_durumlar = ["Evli", "Bekâr", "Dul"]
gelir_araliklari = ["0–40K", "40K–80K", "80K–120K", "120K+"]
calisma_durumlari = ["Çalışıyor", "Çalışmıyor", "Emekli", "Öğrenci"]
binary = ["Evet", "Hayır"]
adim_kategorileri = ["0–3000", "3000–7000", "7000+"]
motivasyonlar = ["Hastalık Korkusu", "Finansal Güvence", "Çocukları Düşünme", "Zorunlu Gördüğü İçin", "Diğer"]

# Veri üretimi
data = {
    "yas": np.random.randint(18, 80, n),
    "medeni_durum": random.choices(medeni_durumlar, k=n),
    "gelir_seviyesi": random.choices(gelir_araliklari, weights=[0.3, 0.4, 0.2, 0.1], k=n),
    "calisma_durumu": random.choices(calisma_durumlari, weights=[0.5, 0.2, 0.2, 0.1], k=n),
    "sigara_kullanimi": random.choices(binary, weights=[0.3, 0.7], k=n),
    "hastane_yatisi_son1yil": random.choices(binary, weights=[0.2, 0.8], k=n),
    "gunluk_adim_sayisi": random.choices(adim_kategorileri, weights=[0.2, 0.5, 0.3], k=n),
    "kronik_hastalik": random.choices(binary, weights=[0.25, 0.75], k=n),
    "saglik_algisi": np.random.randint(1, 6, n),
    "saglik_harcamasi_endisesi": np.random.randint(1, 6, n),
    "sigorta_bilgi_duzeyi": np.random.randint(1, 6, n),
    "sigorta_yaptirma_istegi": np.random.randint(1, 6, n),
    "gecmiste_sigortasi_var_mi": random.choices(binary, weights=[0.4, 0.6], k=n),
    "ailede_hastalik_oykusu": random.choices(binary, weights=[0.3, 0.7], k=n),
    "sigorta_motivasyonu": random.choices(motivasyonlar, weights=[0.25, 0.3, 0.2, 0.15, 0.1], k=n),
}

df = pd.DataFrame(data)
print(df.head())

# CSV olarak kaydetmek istersen:
df.to_csv("medipolice_mock_veri.csv", index=False)
