# ui/settings_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit, QPushButton, QCheckBox, QMessageBox, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Ayarların kaydedilmesi ve yüklenmesi için basit bir mekanizma
import json
import os

class SettingsManager:
    CONFIG_FILE = os.path.join(os.getcwd(), "KayaVuln", "config", "settings.json")
    DEFAULT_SETTINGS = {
        "llm_temperature": 0.7,
        "llm_top_p": 0.9,
        "llm_top_k": 40,
        "llm_repetition_penalty": 1.1,
        "llm_n_ctx": 2048,
        "llm_n_gpu_layers": -1,
        "enable_dark_mode": True,
        "plugin_auto_load": True,
        "model_dir_path": os.path.join(os.getcwd(), "KayaVuln", "models") # Modeller dizini
    }

    @staticmethod
    def load_settings():
        if not os.path.exists(SettingsManager.CONFIG_FILE):
            return SettingsManager.DEFAULT_SETTINGS.copy()
        try:
            with open(SettingsManager.CONFIG_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Eksik ayarları varsayılanlarla tamamla
                for key, default_val in SettingsManager.DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = default_val
                return settings
        except Exception as e:
            print(f"Ayarlar yüklenirken hata oluştu, varsayılanlar kullanılıyor: {e}")
            return SettingsManager.DEFAULT_SETTINGS.copy()

    @staticmethod
    def save_settings(settings: dict):
        os.makedirs(os.path.dirname(SettingsManager.CONFIG_FILE), exist_ok=True)
        try:
            with open(SettingsManager.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            print("Ayarlar başarıyla kaydedildi.")
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata oluştu: {e}")

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager.load_settings()
        self.init_ui()
        self.load_settings_to_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("<h2>Uygulama Ayarları</h2>")
        title_label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title_label)

        # LLM Parametreleri Grubu
        llm_group_box = QGroupBox("LLM Parametreleri")
        llm_group_box.setStyleSheet("QGroupBox { font-weight: bold; color: #007acc; border: 1px solid #444444; border-radius: 8px; margin-top: 10px; }"
                                    "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; color: #e0e0e0; }")
        llm_layout = QVBoxLayout(llm_group_box)
        
        self.add_slider_setting(llm_layout, "Sıcaklık (Temperature)", "llm_temperature", 0.0, 2.0, 0.1, 10, True)
        self.add_slider_setting(llm_layout, "Top P", "llm_top_p", 0.0, 1.0, 0.05, 10, True)
        self.add_slider_setting(llm_layout, "Top K", "llm_top_k", 0, 100, 1, 1, False)
        self.add_slider_setting(llm_layout, "Tekrarlama Cezası", "llm_repetition_penalty", 1.0, 2.0, 0.05, 10, True)
        self.add_slider_setting(llm_layout, "Bağlam Penceresi (n_ctx)", "llm_n_ctx", 512, 8192, 512, 1, False)
        self.add_slider_setting(llm_layout, "GPU Katmanları (n_gpu_layers)", "llm_n_gpu_layers", -1, 30, 1, 1, False) # -1 tümü demek
        
        layout.addWidget(llm_group_box)

        # Genel Ayarlar Grubu
        general_group_box = QGroupBox("Genel Ayarlar")
        general_group_box.setStyleSheet("QGroupBox { font-weight: bold; color: #007acc; border: 1px solid #444444; border-radius: 8px; margin-top: 10px; }"
                                        "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; color: #e0e0e0; }")
        general_layout = QVBoxLayout(general_group_box)

        self.enable_dark_mode_checkbox = QCheckBox("Koyu Temayı Etkinleştir")
        self.enable_dark_mode_checkbox.setStyleSheet("color: #e0e0e0;")
        general_layout.addWidget(self.enable_dark_mode_checkbox)
        
        self.plugin_auto_load_checkbox = QCheckBox("Pluginleri Uygulama Başlangıcında Otomatik Yükle")
        self.plugin_auto_load_checkbox.setStyleSheet("color: #e0e0e0;")
        general_layout.addWidget(self.plugin_auto_load_checkbox)

        # Model dizin yolu gösterimi (değiştirilemez ama bilgi verir)
        model_dir_layout = QHBoxLayout()
        model_dir_layout.addWidget(QLabel("Model Dizini:"))
        self.model_dir_path_display = QLineEdit()
        self.model_dir_path_display.setReadOnly(True)
        self.model_dir_path_display.setStyleSheet("background-color: #333333; color: #e0e0e0; border: 1px solid #555555; border-radius: 5px; padding: 5px;")
        model_dir_layout.addWidget(self.model_dir_path_display)
        general_layout.addLayout(model_dir_layout)


        layout.addWidget(general_group_box)
        layout.addStretch()

        # Kaydet Butonu
        save_button = QPushButton("Ayarları Kaydet")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
        """)
        save_button.clicked.connect(self.save_settings_from_ui)
        layout.addWidget(save_button)

    def add_slider_setting(self, parent_layout, label_text, setting_key, min_val, max_val, step, multiplier, is_float):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: #e0e0e0;")
        h_layout.addWidget(label)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(int(min_val * multiplier))
        slider.setMaximum(int(max_val * multiplier))
        slider.setSingleStep(int(step * multiplier))
        slider.setValue(int(self.settings.get(setting_key, min_val) * multiplier))
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #444444;
                height: 8px;
                background: #333333;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                border: 1px solid #005f99;
                width: 18px;
                margin: -5px 0; /* handle'ı groove'un ortasına hizala */
                border-radius: 9px;
            }
        """)
        h_layout.addWidget(slider)

        value_display = QLineEdit()
        value_display.setReadOnly(True)
        value_display.setFixedWidth(50)
        value_display.setStyleSheet("background-color: #333333; color: #e0e0e0; border: 1px solid #555555; border-radius: 5px; padding: 3px;")
        h_layout.addWidget(value_display)

        def update_value_display(value):
            actual_value = value / multiplier
            value_display.setText(f"{actual_value:.2f}" if is_float else str(int(actual_value)))
        
        slider.valueChanged.connect(update_value_display)
        update_value_display(slider.value()) # Başlangıç değerini ayarla

        setattr(self, f"{setting_key}_slider", slider) # Referans için sakla
        setattr(self, f"{setting_key}_display", value_display) # Referans için sakla
        parent_layout.addLayout(h_layout)

    def load_settings_to_ui(self):
        self.settings = SettingsManager.load_settings() # En güncel ayarları yükle
        
        # LLM Parametreleri
        self.llm_temperature_slider.setValue(int(self.settings.get("llm_temperature", 0.7) * 10))
        self.llm_top_p_slider.setValue(int(self.settings.get("llm_top_p", 0.9) * 10))
        self.llm_top_k_slider.setValue(int(self.settings.get("llm_top_k", 40)))
        self.llm_repetition_penalty_slider.setValue(int(self.settings.get("llm_repetition_penalty", 1.1) * 10))
        self.llm_n_ctx_slider.setValue(int(self.settings.get("llm_n_ctx", 2048)))
        self.llm_n_gpu_layers_slider.setValue(int(self.settings.get("llm_n_gpu_layers", -1)))

        # Genel Ayarlar
        self.enable_dark_mode_checkbox.setChecked(self.settings.get("enable_dark_mode", True))
        self.plugin_auto_load_checkbox.setChecked(self.settings.get("plugin_auto_load", True))
        self.model_dir_path_display.setText(self.settings.get("model_dir_path", ""))


    def save_settings_from_ui(self):
        new_settings = self.settings.copy()

        # LLM Parametreleri
        new_settings["llm_temperature"] = self.llm_temperature_slider.value() / 10.0
        new_settings["llm_top_p"] = self.llm_top_p_slider.value() / 10.0
        new_settings["llm_top_k"] = self.llm_top_k_slider.value()
        new_settings["llm_repetition_penalty"] = self.llm_repetition_penalty_slider.value() / 10.0
        new_settings["llm_n_ctx"] = self.llm_n_ctx_slider.value()
        new_settings["llm_n_gpu_layers"] = self.llm_n_gpu_layers_slider.value()

        # Genel Ayarlar
        new_settings["enable_dark_mode"] = self.enable_dark_mode_checkbox.isChecked()
        new_settings["plugin_auto_load"] = self.plugin_auto_load_checkbox.isChecked()
        # model_dir_path değiştirilemediği için UI'dan almıyoruz, varsayılanı kullanırız

        SettingsManager.save_settings(new_settings)
        self.settings = new_settings # Güncel ayarları sakla
        QMessageBox.information(self, "Ayarlar Kaydedildi", "Ayarlar başarıyla kaydedildi. Bazı değişiklikler uygulamanın yeniden başlatılmasını gerektirebilir.")

        # Temanın anında uygulanması için bir sinyal gönderebiliriz, ama şimdilik yeniden başlatma önerelim.
        # Örneğin, Ana Pencereye theme_changed_signal gönderebiliriz.