import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa yapılandırmasını ayarla
st.set_page_config(layout="wide", page_title="MediPoliçe Risk Analizi", page_icon="🩺")

# CSS ile  özelleştirme
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #e6f3ff;
    }
    .stButton>button {
        color: white;
        background-color: #007bff;
        border-radius: 5px;
    }
    .st-b7 {
        background-color: #e6f3ff;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """
    Veri setlerini yükler ve birleştirir.
    """
    try:
        # Veri setlerini yükle
        veri = pd.read_csv('medipolice_mock_veri.csv')
        riskli_veri = pd.read_csv('medipolice_mock_veri_riskli.csv')

        # Risk puanı ve risk sınıfı sütunlarını ana veri setine ekle
        veri['risk_puani'] = riskli_veri['risk_puani']
        veri['risk_sinifi'] = riskli_veri['risk_sinifi']
        return veri
    except FileNotFoundError:
        st.error("Veri dosyaları bulunamadı. Lütfen 'medipolice_mock_veri.csv' ve 'medipolice_mock_veri_riskli.csv' dosyalarının doğru konumda olduğundan emin olun.")
        return None

# Veriyi yükle
data = load_data()

if data is not None:
    # Başlık
    st.title("🩺 MediPoliçe Müşteri Risk Analizi Paneli")
    st.markdown("Bu panel, müşteri verilerini analiz ederek risk gruplarını belirlemenize ve sigorta motivasyonlarını anlamanıza yardımcı olur.")

    # Kenar çubuğu (sidebar)
    st.sidebar.header("Filtreleme Seçenekleri")

    # Yaş filtresi
    min_yas, max_yas = st.sidebar.slider(
        "Yaş Aralığı",
        int(data['yas'].min()),
        int(data['yas'].max()),
        (int(data['yas'].min()), int(data['yas'].max()))
    )

    # Gelir seviyesi filtresi
    gelir_seviyeleri = st.sidebar.multiselect(
        "Gelir Seviyesi",
        options=data['gelir_seviyesi'].unique(),
        default=data['gelir_seviyesi'].unique()
    )

    # Risk sınıfı filtresi
    risk_siniflari = st.sidebar.multiselect(
        "Risk Sınıfı",
        options=data['risk_sinifi'].sort_values().unique(),
        default=data['risk_sinifi'].sort_values().unique()
    )

    # Filtreleri uygula
    filtrelenmis_veri = data[
        (data['yas'] >= min_yas) & (data['yas'] <= max_yas) &
        (data['gelir_seviyesi'].isin(gelir_seviyeleri)) &
        (data['risk_sinifi'].isin(risk_siniflari))
    ]

    # Ana panel
    st.header("Filtrelenmiş Veri Seti")
    st.dataframe(filtrelenmis_veri)

    st.header("Görsel Analizler")

    col1, col2 = st.columns(2)

    with col1:
        # Risk Sınıfı Dağılımı
        st.subheader("Risk Sınıfı Dağılımı")
        risk_sinifi_dagilimi = filtrelenmis_veri['risk_sinifi'].value_counts().sort_index()
        fig_risk = px.pie(
            values=risk_sinifi_dagilimi.values,
            names=risk_sinifi_dagilimi.index,
            title="Müşterilerin Risk Sınıflarına Göre Dağılımı",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig_risk, use_container_width=True)

        # Sigorta Motivasyonu
        st.subheader("Sigorta Yaptırma Motivasyonu")
        motivasyon_dagilimi = filtrelenmis_veri['sigorta_motivasyonu'].value_counts()
        fig_motivasyon = px.bar(
            x=motivasyon_dagilimi.index,
            y=motivasyon_dagilimi.values,
            title="Sigorta Yaptırma Motivasyonları",
            labels={'x': 'Motivasyon', 'y': 'Kişi Sayısı'},
            color_discrete_sequence=['#007bff']
        )
        st.plotly_chart(fig_motivasyon, use_container_width=True)


    with col2:
        # Yaş Dağılımı
        st.subheader("Yaş Dağılımı")
        fig_yas = px.histogram(
            filtrelenmis_veri,
            x="yas",
            nbins=20,
            title="Müşterilerin Yaş Dağılımı",
            color_discrete_sequence=['#007bff']
        )
        st.plotly_chart(fig_yas, use_container_width=True)


        # Gelir Seviyesi Dağılımı
        st.subheader("Gelir Seviyesine Göre Dağılım")
        gelir_dagilimi = filtrelenmis_veri['gelir_seviyesi'].value_counts()
        fig_gelir = px.bar(
            x=gelir_dagilimi.index,
            y=gelir_dagilimi.values,
            title="Müşterilerin Gelir Seviyelerine Göre Dağılımı",
            labels={'x': 'Gelir Seviyesi', 'y': 'Kişi Sayısı'},
            color_discrete_sequence=['#007bff']
        )
        st.plotly_chart(fig_gelir, use_container_width=True)

    st.header("Detaylı Analizler")

    # Yaş ve Risk Puanı İlişkisi
    st.subheader("Yaş ve Risk Puanı İlişkisi")
    fig_yas_risk = px.scatter(
        filtrelenmis_veri,
        x='yas',
        y='risk_puani',
        color='risk_sinifi',
        title='Yaş ve Risk Puanı Arasındaki İlişki',
        labels={'yas': 'Yaş', 'risk_puani': 'Risk Puanı', 'risk_sinifi': 'Risk Sınıfı'},
        color_continuous_scale=px.colors.sequential.Blues
    )
    st.plotly_chart(fig_yas_risk, use_container_width=True)