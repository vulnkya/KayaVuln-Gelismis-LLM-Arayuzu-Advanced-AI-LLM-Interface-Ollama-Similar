# ui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QStackedWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from ui.chat_widget import ChatWidget
from ui.model_manager_widget import ModelManagerWidget
from ui.plugin_manager_widget import PluginManagerWidget
from ui.settings_widget import SettingsWidget # Yeni eklendi
from ui.settings_widget import SettingsManager # Tema ayarını okumak için

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KayaVuln - Gelişmiş LLM Arayüzü")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("assets/novaai_icon.png")) # İkon dosyası eklenmeli

        self.init_ui()
        self.load_initial_theme() # Tema ayarını buradan yükle

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b; /* Koyu gri */
                border: none;
                padding: 10px;
                font-size: 16px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 5px;
                color: #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #555555; /* Seçili öğe arka planı */
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #444444; /* Fare üzerine gelindiğinde */
            }
        """)

        self.sidebar.addItem("Chat")
        self.sidebar.addItem("Models")
        self.sidebar.addItem("Plugins")
        self.sidebar.addItem("Settings") # Ayarlar sayfası
        main_layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        self.chat_widget = ChatWidget()
        self.model_manager_widget = ModelManagerWidget()
        self.plugin_manager_widget = PluginManagerWidget()
        self.settings_widget = SettingsWidget() # Yeni eklendi

        self.content_stack.addWidget(self.chat_widget)          # Index 0
        self.content_stack.addWidget(self.model_manager_widget) # Index 1
        self.content_stack.addWidget(self.plugin_manager_widget)# Index 2
        self.content_stack.addWidget(self.settings_widget)      # Index 3

        self.sidebar.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0) # Başlangıçta sohbet sayfasını göster

        self.model_manager_widget.model_selected_signal.connect(self.chat_widget.set_current_model)
        self.model_manager_widget.refresh_models()

    def load_initial_theme(self):
        settings = SettingsManager.load_settings()
        if settings.get("enable_dark_mode", True):
            self.apply_dark_theme()
        # Açık tema için farklı bir stil de eklenebilir

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e; /* Koyu arka plan */
                color: #e0e0e0;
            }
            QScrollBar:vertical {
                border: none;
                background: #333333;
                width: 8px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
             QLabel, QCheckBox { color: #e0e0e0; } /* Genel olarak QLabel ve QCheckBox metin rengini ayarla */
        """)