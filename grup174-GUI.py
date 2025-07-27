import sys
import subprocess
import os
import signal
import time
import threading

try:
    from win10toast import ToastNotifier
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "win10toast"])
    from win10toast import ToastNotifier

try:
    toaster = ToastNotifier()
    toaster.show_toast("MediPoliçe", "Eklentiler indiriliyor, lütfen bekleyiniz...", duration=5, threaded=True)
except Exception:
    pass

REQUIRED = [
    "PySide6", "matplotlib", "pandas", "numpy"
]
missing = []
for pkg in REQUIRED:
    try:
        __import__(pkg if pkg != "PySide6" else "PySide6.QtWidgets")
    except ImportError:
        missing.append(pkg)
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    os.execl(sys.executable, sys.executable, *sys.argv)

import pandas as pd
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QTableWidget, QTableWidgetItem, QComboBox, QSlider, QSizePolicy,
    QFrame, QPushButton, QGraphicsBlurEffect
)
from PySide6.QtCore import Qt, QTimer, QRect, QEvent, QTime, QDateTime, QPropertyAnimation, QEasingCurve, QPoint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import datetime

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

class DynamicIsland(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #23272f;
                border-radius: 18px;
                border: 2px solid #444;
            }
        """)

class ThemedTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #23272f;
                color: #fff;
                border-radius: 18px;
                border: 2px solid #444;
                gridline-color: #444;
                font-size: 13px;
                selection-background-color: #444;
                selection-color: #fff;
            }
            QHeaderView::section {
                background-color: #23272f;
                color: #fff;
                border-radius: 12px;
                font-weight: bold;
                padding: 6px;
            }
            QTableWidget::item {
                border-radius: 10px;
                background: #2c313c;
                padding: 4px;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #23272f;
                border-radius: 8px;
                width: 12px;
                margin: 2px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #888;
                border-radius: 8px;
                min-height: 20px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                border: none;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
            }
            QWidget#centralwidget {
                background: #23272f;
                border-radius: 32px;
            }
        """)
        self.setWindowTitle("🩺 MediPoliçe Risk Analizi Paneli")
        self.setMinimumSize(1600, 900)
        self.df = pd.read_csv("medipolice_mock_veri.csv")
        self.df["risk_puani"] = self.df.apply(hesapla_risk_puani, axis=1)
        self.df["risk_sinifi"] = self.df["risk_puani"].apply(siniflandir)
        self.filtered = self.df.copy()
        self.animating = False
        self.slider_timer = QTimer()
        self.slider_timer.setInterval(20)
        self.slider_timer.timeout.connect(self.animate_graphs)
        self.target_filtered = None
        self.animation_step = 0
        self.init_ui()

    def init_ui(self):
        self.fig1, self.ax1 = plt.subplots(figsize=(4, 3))
        self.canvas1 = FigureCanvas(self.fig1)
        self.fig2, self.ax2 = plt.subplots(figsize=(4, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        self.fig3, self.ax3 = plt.subplots(figsize=(4, 3))
        self.canvas3 = FigureCanvas(self.fig3)
        self.fig4, self.ax4 = plt.subplots(figsize=(4, 3))
        self.canvas4 = FigureCanvas(self.fig4)
        self.fig5, self.ax5 = plt.subplots(figsize=(4, 3))
        self.canvas5 = FigureCanvas(self.fig5)
        self.fig6, self.ax6 = plt.subplots(figsize=(4, 3))
        self.canvas6 = FigureCanvas(self.fig6)
                             # GUI designed by BiberliSut 
        main_widget = QWidget()
        main_widget.setObjectName("centralwidget")
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(16)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)
        title_widget = QWidget()
        title_widget.setStyleSheet("""
            background: #23272f;
            border-radius: 18px;
            padding: 0 18px;
        """)
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("MediPoliçe Paneli")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; background: transparent;")
        title_layout.addWidget(title)
        top_row.addWidget(title_widget, alignment=Qt.AlignLeft)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        btn_row.setContentsMargins(0, 0, 0, 0)
        self.min_btn = QPushButton("_")
        self.min_btn.setFixedSize(32, 32)
        self.min_btn.setStyleSheet("background:#23272f; color:#fff; border-radius:16px; font-size:18px;")
        self.min_btn.clicked.connect(self.showMinimized)
        btn_row.addWidget(self.min_btn)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setStyleSheet("background:#23272f; color:#fff; border-radius:16px; font-size:18px;")
        self.close_btn.clicked.connect(self.confirm_exit)
        btn_row.addWidget(self.close_btn)
        top_row.addLayout(btn_row)

        legend_widget = QWidget()
        legend_layout = QHBoxLayout(legend_widget)
        legend_layout.setContentsMargins(12, 0, 12, 0)
        legend_layout.setSpacing(8)
        legend_widget.setStyleSheet("""
            background: #23272f;
            border-radius: 12px;
            border: 2px solid #444;
        """)
        legend_layout.addWidget(QLabel('<b>Sigara/Adım Risk Sınıfı:</b>'))
        reds = [plt.cm.Reds(i) for i in np.linspace(0.3, 0.9, 5)]
        greens = [plt.cm.Greens(i) for i in np.linspace(0.3, 0.9, 5)]
        for i in range(5):
            color = f'rgb({int(reds[i][0]*255)},{int(reds[i][1]*255)},{int(reds[i][2]*255)})'
            box = QLabel(str(i+1))
            box.setStyleSheet(f"""
                background: {color};
                color: #23272f;
                border-radius: 6px;
                min-width: 18px; max-width: 18px;
                min-height: 18px; max-height: 18px;
                font-weight: bold;
                font-size: 12px;
                text-align: center;
                padding: 0px 2px;
            """)
            legend_layout.addWidget(box)
        legend_layout.addSpacing(12)
        for i in range(5):
            color = f'rgb({int(greens[i][0]*255)},{int(greens[i][1]*255)},{int(greens[i][2]*255)})'
            box = QLabel(str(i+1))
            box.setStyleSheet(f"""
                background: {color};
                color: #23272f;
                border-radius: 6px;
                min-width: 18px; max-width: 18px;
                min-height: 18px; max-height: 18px;
                font-weight: bold;
                font-size: 12px;
                text-align: center;
                padding: 0px 2px;
            """)
            legend_layout.addWidget(box)
        top_row.addWidget(legend_widget, alignment=Qt.AlignRight)

        datetime_widget = QWidget()
        datetime_widget.setStyleSheet("""
            background: #23272f;
            border-radius: 18px;
            padding: 0 18px;
        """)
        datetime_layout = QHBoxLayout(datetime_widget)
        datetime_layout.setContentsMargins(0, 0, 0, 0)
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("font-size: 16px; color: #fff; font-weight: bold; background: transparent;")
        datetime_layout.addWidget(self.datetime_label)
        top_row.addWidget(datetime_widget, alignment=Qt.AlignRight)
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        main_layout.addLayout(top_row)

        filter_island = DynamicIsland()
        filter_layout = QHBoxLayout(filter_island)
        filter_layout.setContentsMargins(16, 8, 16, 8)
        filter_layout.setSpacing(12)

        self.gelir_combo = QComboBox()
        self.gelir_combo.addItem("💰 Gelir Seviyesi: Tümü")
        for g in self.df["gelir_seviyesi"].unique():
            self.gelir_combo.addItem(f"💰 {g}")
        self.gelir_combo.currentIndexChanged.connect(self.apply_filters)
        self.gelir_combo.setMinimumWidth(160)
        self.gelir_combo.setStyleSheet("background: #23272f; color: #fff; border-radius: 12px; padding: 6px;")
        filter_layout.addWidget(self.gelir_combo)

        self.risk_combo = QComboBox()
        self.risk_combo.addItem("⚠️ Risk Sınıfı: Tümü")
        for r in sorted(self.df["risk_sinifi"].unique()):
            self.risk_combo.addItem(f"⚠️ {r}")
        self.risk_combo.currentIndexChanged.connect(self.apply_filters)
        self.risk_combo.setMinimumWidth(120)
        self.risk_combo.setStyleSheet("background: #23272f; color: #fff; border-radius: 12px; padding: 6px;")
        filter_layout.addWidget(self.risk_combo)

        self.reset_btn = QPushButton("Sıfırla")
        self.reset_btn.setStyleSheet("background:#444; color:#fff; border-radius:12px; padding:6px 18px;")
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)
        filter_layout.addStretch(1)
        main_layout.addWidget(filter_island)

        content_grid = QHBoxLayout()
        content_grid.setSpacing(24)
        main_layout.addLayout(content_grid)

        sol_kolon = QVBoxLayout()
        sol_kolon.setSpacing(12)

        yas_island = DynamicIsland()
        yas_layout = QHBoxLayout(yas_island)
        yas_layout.setContentsMargins(16, 8, 16, 8)
        yas_layout.setSpacing(8)

        yas_label = QLabel("Yaş Max:")
        yas_label.setStyleSheet("""
            background: #23272f;
            color: #fff;
            font-weight: bold;
            border-radius: 12px;
            padding: 6px 16px;
            border: 2px solid #444;
""")
        yas_layout.addWidget(yas_label)

        self.yas_slider = QSlider(Qt.Horizontal)
        self.yas_slider.setMinimum(int(self.df["yas"].min()))
        self.yas_slider.setMaximum(int(self.df["yas"].max()))
        self.yas_slider.setValue(int(self.df["yas"].max()))
        self.yas_slider.valueChanged.connect(self.on_slider_change)
        self.yas_slider.sliderReleased.connect(self.on_slider_released)
        self.yas_slider.setStyleSheet("""
            QSlider { background: #23272f; border-radius: 12px; height: 24px; }
            QSlider::groove:horizontal { border-radius: 12px; height: 12px; background: #444; }
            QSlider::handle:horizontal { background: #7ad7f0; border: 2px solid #fff; width: 24px; margin: -8px 0; border-radius: 12px; }
""")
        yas_layout.addWidget(self.yas_slider)
        sol_kolon.addWidget(yas_island)

        table_island = DynamicIsland()
        table_island.setMinimumSize(600, 480)
        table_layout = QVBoxLayout(table_island)
        table_layout.setContentsMargins(16, 8, 16, 8)
        table_label = QLabel("Filtrelenmiş Müşteri Tablosu")
        table_label.setStyleSheet("""
            color: #fff;
            font-weight: bold;
            font-size: 15px;
            background: #23272f;
            border-radius: 12px;
            padding: 8px 0 8px 12px;
        """)
        table_layout.addWidget(table_label)
        self.table = ThemedTable()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.horizontalScrollBar().setStyleSheet("""
    QScrollBar:horizontal {
        background: #23272f;
        border-radius: 10px;
        height: 16px;
        margin: 2px 20px 2px 20px;
    }
    QScrollBar::handle:horizontal {
        background: #7ad7f0;
        border-radius: 8px;
        min-width: 40px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: none;
        border: none;
    }
""")
        table_layout.addWidget(self.table)
        sol_kolon.addWidget(table_island)

        content_grid.addLayout(sol_kolon, 2)

        grafik_grid = QGridLayout()
        grafik_grid.setSpacing(16)

        grafikler = [
            ("Sigorta Yaptırma Motivasyonu", self.canvas1),
            ("Yaş Risk Puanı İlişkisi", self.canvas6),
            ("Yaş Dağılımı", self.canvas3),
            ("Gelir Seviyesi Dağılımı", self.canvas4),
            ("Sigara Kullanımı ve Risk Sınıfı", self.canvas2),
            ("Günlük Adım ve Risk Sınıfı", self.canvas5),
        ]
        for idx, (label, canvas) in enumerate(grafikler):
            g_island = QWidget()
            g_island.setStyleSheet("""
                background: #fff;
                border-radius: 18px;
                border: 2px solid #e0e0e0;
            """)
            g_layout = QVBoxLayout(g_island)
            g_layout.setContentsMargins(12, 12, 12, 12)
            g_layout.setSpacing(8)
            g_layout.addWidget(canvas)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #23272f; font-size: 13px; font-weight: bold; background: transparent; border: none;")
            lbl.setAlignment(Qt.AlignCenter)
            g_layout.addWidget(lbl)
            grafik_grid.addWidget(g_island, idx // 2, idx % 2)

        sag_widget = QWidget()
        sag_widget.setLayout(grafik_grid)
        content_grid.addWidget(sag_widget, 3)

        self.setCentralWidget(main_widget)
        self.apply_filters()

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.datetime_label.setText(now.toString("dd.MM.yyyy HH:mm:ss"))

    def confirm_exit(self):
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(0)
        self.centralWidget().setGraphicsEffect(self.blur_effect)
        self.blur_anim = QPropertyAnimation(self.blur_effect, b"blurRadius")
        self.blur_anim.setStartValue(0)
        self.blur_anim.setEndValue(12)
        self.blur_anim.setDuration(350)
        self.blur_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.blur_anim.start()

        self.exit_dialog = QWidget(self)
        self.exit_dialog.setStyleSheet("""
            background: #23272f;
            border-radius: 24px;
""")
        self.exit_dialog.setGeometry(self.width()//2-200, self.height()//2-80, 400, 160)
        vbox = QVBoxLayout(self.exit_dialog)
        vbox.setAlignment(Qt.AlignCenter)
        label = QLabel("Gerçekten çıkmak istiyor musunuz?")
        label.setStyleSheet("color:#fff; font-size:18px; font-weight:bold;")
        vbox.addWidget(label, alignment=Qt.AlignCenter)
        btns = QHBoxLayout()
        evet = QPushButton("Evet")
        evet.setStyleSheet("""
            background:#444; color:#fff; border-radius:12px; font-weight:bold; padding:8px 24px;
            border:none;
        """)
        evet.clicked.connect(self.animated_close)
        btns.addWidget(evet)
        hayir = QPushButton("Hayır")
        hayir.setStyleSheet("""
            background:#23272f; color:#fff; border-radius:12px; font-weight:bold; padding:8px 24px;
            border:1px solid #444;
        """)
        hayir.clicked.connect(self.cancel_exit)
        btns.addWidget(hayir)
        vbox.addLayout(btns)
        self.exit_dialog.show()
                           # E.R.D.E.M tarafından geliştirildi
    def animated_close(self):
        self.close_anim = QPropertyAnimation(self, b"windowOpacity")
        self.close_anim.setDuration(350)
        self.close_anim.setStartValue(1)
        self.close_anim.setEndValue(0)
        self.close_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.close_anim.finished.connect(self.force_kill_app)
        self.close_anim.start()

    def force_kill_app(self):
        def kill():
            time.sleep(2)
            os._exit(0)
        threading.Thread(target=kill, daemon=True).start()

    def cancel_exit(self):
        if hasattr(self, "blur_effect"):
            self.blur_anim2 = QPropertyAnimation(self.blur_effect, b"blurRadius")
            self.blur_anim2.setStartValue(self.blur_effect.blurRadius())
            self.blur_anim2.setEndValue(0)
            self.blur_anim2.setDuration(350)
            self.blur_anim2.setEasingCurve(QEasingCurve.OutCubic)
            self.blur_anim2.finished.connect(lambda: self.centralWidget().setGraphicsEffect(None))
            self.blur_anim2.start()
        self.exit_dialog.close()

    def showMinimized(self):
        self.min_anim = QPropertyAnimation(self, b"windowOpacity")
        self.min_anim.setDuration(250)
        self.min_anim.setStartValue(1)
        self.min_anim.setEndValue(0)
        self.min_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.min_anim.finished.connect(super().showMinimized)
        self.min_anim.finished.connect(lambda: self.setWindowOpacity(1))
        self.min_anim.start()

    def closeEvent(self, event):
        if hasattr(self, "exit_dialog") and self.exit_dialog.isVisible():
            event.ignore()
        else:
            event.accept()

    def apply_filters(self):
        yas_max = self.yas_slider.value()
        gelir = self.gelir_combo.currentText()
        risk = self.risk_combo.currentText()

        filtered = self.df[self.df["yas"] <= yas_max]
        if not ("Tümü" in gelir):
            gelir_deger = gelir.replace("💰", "").strip()
            filtered = filtered[filtered["gelir_seviyesi"] == gelir_deger]
        if not ("Tümü" in risk):
            risk_deger = ''.join(filter(str.isdigit, risk))
            if risk_deger:
                filtered = filtered[filtered["risk_sinifi"] == int(risk_deger)]
        self.filtered = filtered

        self.table.setRowCount(len(filtered))
        self.table.setColumnCount(len(filtered.columns))
        self.table.setHorizontalHeaderLabels(filtered.columns)
        for row_idx, (_, row) in enumerate(filtered.iterrows()):
            for col_idx, val in enumerate(row):
                if self.table.horizontalHeaderItem(col_idx).text() == "risk_sinifi":
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))
                else:
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))

        self.ax1.clear()
        motivasyon = filtered["sigorta_motivasyonu"].value_counts()
        bars1 = motivasyon.plot(kind="bar", color=["#7ad7f0", "#ffe066", "#ffb3b3", "#baffc9", "#d291bc"], ax=self.ax1)
        self.ax1.set_ylabel("Kişi Sayısı")
        self.ax1.set_xlabel("Motivasyon")
        self.ax1.set_title("")
        self.ax1.grid(True, axis='y', linestyle='--', alpha=0.5)
        self.ax1.yaxis.set_major_locator(plt.MaxNLocator(6))
        for p in self.ax1.patches:
            self.ax1.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2, p.get_height()),
                              ha='center', va='bottom', fontsize=9, color='#23272f', fontweight='bold')
        self.fig1.tight_layout()
        self.canvas1.draw()

        self.ax2.clear()
        crosstab2 = pd.crosstab(filtered["sigara_kullanimi"], filtered["risk_sinifi"])
        renkler2 = [plt.cm.Reds(i) for i in np.linspace(0.3, 0.9, crosstab2.shape[1])]
        bars2 = crosstab2.plot(kind="bar", stacked=False, ax=self.ax2, color=renkler2)
        self.ax2.set_ylabel("Kişi Sayısı")
        self.ax2.set_xlabel("Sigara Kullanımı")
        self.ax2.set_title("")
        self.ax2.grid(True, axis='y', linestyle='--', alpha=0.5)
        self.ax2.yaxis.set_major_locator(plt.MaxNLocator(6))
        self.ax2.get_legend().remove() if self.ax2.get_legend() else None
        self.fig2.tight_layout()
        self.canvas2.draw()

        self.ax3.clear()
        filtered["yas"].plot(kind="hist", bins=20, color="#7ad7f0", edgecolor="black", ax=self.ax3)
        self.ax3.set_xlabel("Yaş")
        self.ax3.set_ylabel("Kişi Sayısı")
        self.ax3.set_title("")
        self.ax3.grid(True, axis='y', linestyle='--', alpha=0.5)
        self.ax3.yaxis.set_major_locator(plt.MaxNLocator(6))
        self.fig3.tight_layout()
        self.canvas3.draw()

        self.ax4.clear()
        gelir = filtered["gelir_seviyesi"].value_counts()
        renkler4 = [plt.cm.viridis(i) for i in np.linspace(0.3, 0.9, gelir.shape[0])]
        bars4 = gelir.plot(kind="bar", color=renkler4, ax=self.ax4)
        self.ax4.set_ylabel("Kişi Sayısı")
        self.ax4.set_xlabel("Gelir Seviyesi")
        self.ax4.set_title("")
        self.ax4.grid(True, axis='y', linestyle='--', alpha=0.5)
        self.ax4.yaxis.set_major_locator(plt.MaxNLocator(6))
        for p in self.ax4.patches:
            self.ax4.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2, p.get_height()),
                              ha='center', va='bottom', fontsize=9, color='#23272f', fontweight='bold')
        self.fig4.tight_layout()
        self.canvas4.draw()

        self.ax5.clear()
        crosstab5 = pd.crosstab(filtered["gunluk_adim_sayisi"], filtered["risk_sinifi"])
        renkler5 = [plt.cm.Greens(i) for i in np.linspace(0.3, 0.9, crosstab5.shape[1])]
        bars5 = crosstab5.plot(kind="bar", stacked=False, ax=self.ax5, color=renkler5)
        self.ax5.set_ylabel("Kişi Sayısı")
        self.ax5.set_xlabel("Günlük Adım")
        self.ax5.set_title("")
        self.ax5.get_legend().remove() if self.ax5.get_legend() else None
        self.fig5.tight_layout()
        self.canvas5.draw()

        self.ax6.clear()
        self.ax6.scatter(filtered["yas"], filtered["risk_puani"], c=filtered["risk_sinifi"], cmap="Blues", edgecolor="black")
        self.ax6.set_xlabel("Yaş")
        self.ax6.set_ylabel("Risk Puanı")
        self.ax6.set_title("")
        self.fig6.tight_layout()
        self.canvas6.draw()

    def reset_filters(self):
        self.gelir_combo.setCurrentIndex(0)
        self.risk_combo.setCurrentIndex(0)
        self.yas_slider.setValue(int(self.df["yas"].max()))

    def set_colored_cell(self, table, row, col, color):
        w = QFrame()
        w.setStyleSheet(f"""
            background: {color};
            border-radius: 10px;
            min-width: 24px; min-height: 24px;
            max-width: 24px; max-height: 24px;
        """)
        table.setCellWidget(row, col, w)

    def on_slider_change(self):
        if not self.animating:
            self.animating = True
            self.animation_step = 0
            self.slider_timer.start()

    def on_slider_released(self):
        self.target_filtered = self.df[self.df["yas"] <= self.yas_slider.value()]
        self.animation_step = 0
        self.slider_timer.start()

    def animate_graphs(self):
        if self.animation_step < 5:
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
                for bar in ax.containers if hasattr(ax, "containers") else []:
                    for patch in bar:
                        patch.set_alpha(1 - self.animation_step * 0.2)
                for coll in ax.collections:
                    coll.set_alpha(1 - self.animation_step * 0.2)
            for canvas in [self.canvas1, self.canvas2, self.canvas3, self.canvas4, self.canvas5, self.canvas6]:
                canvas.draw()
            self.animation_step += 1
        elif self.animation_step == 5:
            self.filtered = self.target_filtered if self.target_filtered is not None else self.filtered
            self.apply_filters()
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
                for bar in ax.containers if hasattr(ax, "containers") else []:
                    for patch in bar:
                        patch.set_alpha(0)
                for coll in ax.collections:
                    coll.set_alpha(0)
            for canvas in [self.canvas1, self.canvas2, self.canvas3, self.canvas4, self.canvas5, self.canvas6]:
                canvas.draw()
            self.animation_step += 1
        elif self.animation_step < 11:
            alpha = (self.animation_step - 5) * 0.2
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
                for bar in ax.containers if hasattr(ax, "containers") else []:
                    for patch in bar:
                        patch.set_alpha(alpha)
                for coll in ax.collections:
                    coll.set_alpha(alpha)
            for canvas in [self.canvas1, self.canvas2, self.canvas3, self.canvas4, self.canvas5, self.canvas6]:
                canvas.draw()
            self.animation_step += 1
        else:
            self.slider_timer.stop()
            self.animating = False
            self.target_filtered = None
#created by erdem erçetin
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "marquee_bar"):
            self.marquee_bar.setGeometry(0, self.height()-38, self.width(), 38)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QWidget { background-color: #181a20; color: #fff; }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())