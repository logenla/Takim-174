import pandas as pd

# Örnek veri yükle
df = pd.read_csv("medipolice_mock_veri.csv")

def hesapla_risk_puani(row):
    puan = 0
    if row['yas'] > 60:
        puan += 15
    if row['sigara_kullanimi'] == 'Evet':
        puan += 10
    if row['kronik_hastalik'] == 'Evet':
        puan += 15
    if row['ailede_hastalik_oykusu'] == 'Evet':
        puan += 5
    if row['hastane_yatisi_son1yil'] == 'Evet':
        puan += 10
    if row['gunluk_adim_sayisi'] == '0–3000':
        puan += 10
    if row['saglik_algisi'] < 3:
        puan += 5
    if row['saglik_harcamasi_endisesi'] > 3:
        puan += 5
    return puan

df['risk_puani'] = df.apply(hesapla_risk_puani, axis=1)

def siniflandir(puan):
    if puan < 15:
        return 1
    elif puan < 30:
        return 2
    elif puan < 45:
        return 3
    elif puan < 60:
        return 4
    else:
        return 5

df['risk_sinifi'] = df['risk_puani'].apply(siniflandir)

print(df[['risk_puani', 'risk_sinifi']].head())
