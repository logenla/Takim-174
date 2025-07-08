import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# CSV 
df = pd.read_csv("medipolice_mock_veri_riskli.csv")

# Grafik
sns.countplot(data=df, x='risk_sinifi', palette='viridis')
plt.title('Risk Sınıfı Dağılımı')
plt.xlabel('Risk Sınıfı (1= Düşük, 5= Yüksek)')
plt.ylabel('Kullanıcı Sayısı')
plt.show()

#Yaş Dağılımı ve Risk Sınıfı İlişkisi (Boxplot)

plt.figure(figsize=(10,6))
sns.boxplot(data=df, x='risk_sinifi', y='yas', palette='coolwarm')
plt.title('Risk Sınıfına Göre Yaş Dağılımı')
plt.xlabel('Risk Sınıfı')
plt.ylabel('Yaş')
plt.show()

#3. Sigara Kullanımı ve Risk Sınıfı (Yüzdelik Barplot)

plt.figure(figsize=(8,6))
sns.countplot(data=df, x='sigara_kullanimi', hue='risk_sinifi', palette='magma')
plt.title('Sigara Kullanımı ve Risk Sınıfı Dağılımı')
plt.xlabel('Sigara Kullanımı')
plt.ylabel('Kullanıcı Sayısı')
plt.legend(title='Risk Sınıfı')
plt.show()

#Günlük Adım Sayısı ve Risk Sınıfı (Yığılmış Barplot)
plt.figure(figsize=(10,6))
adim_risk = pd.crosstab(df['gunluk_adim_sayisi'], df['risk_sinifi'], normalize='index')
adim_risk.plot(kind='bar', stacked=True, colormap='Spectral')
plt.title('Günlük Adım Sayısı ile Risk Sınıfı Oranları')
plt.xlabel('Günlük Adım Sayısı Kategorisi')
plt.ylabel('Risk Sınıfı Oranı')
plt.legend(title='Risk Sınıfı', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()

#Korelasyon Matrisi (Numerik Değişkenler)
plt.figure(figsize=(10,8))
num_cols = ['yas', 'saglik_algisi', 'saglik_harcamasi_endisesi', 'sigorta_bilgi_duzeyi', 'sigorta_yaptirma_istegi', 'risk_puani', 'risk_sinifi']
sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Sayısal Değişkenler Korelasyon Matrisi')
plt.show()


#Medeni Duruma Göre Risk Sınıfı Dağılımı (Yüzdelik Barplot)
medeni_risk = pd.crosstab(df['medeni_durum'], df['risk_sinifi'], normalize='index')
medeni_risk.plot(kind='bar', stacked=True, colormap='Set2', figsize=(8,6))
plt.title('Medeni Duruma Göre Risk Sınıfı Oranları')
plt.xlabel('Medeni Durum')
plt.ylabel('Oran')
plt.legend(title='Risk Sınıfı', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()
