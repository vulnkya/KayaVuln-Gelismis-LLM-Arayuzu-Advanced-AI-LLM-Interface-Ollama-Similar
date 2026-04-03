from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QSplitter, QTextEdit, QFileDialog, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal

from core.plugin_manager import PluginManager

class PluginManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.plugin_manager = PluginManager()
        self.init_ui()
        self.load_plugins()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<h2 style='color:#e0e0e0;'>Plugin Yöneticisi</h2>"))
        header_layout.addStretch()
        
        self.add_plugin_button = QPushButton("Plugin Ekle")
        self.add_plugin_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #005f99; }
        """)
        self.add_plugin_button.clicked.connect(self.add_plugin_manually)
        header_layout.addWidget(self.add_plugin_button)

        self.refresh_button = QPushButton("Yenile")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #444444; }
        """)
        self.refresh_button.clicked.connect(self.load_plugins)
        header_layout.addWidget(self.refresh_button)
        main_layout.addLayout(header_layout)

        splitter = QSplitter(Qt.Horizontal)

        self.plugin_list = QListWidget()
        self.plugin_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                border-radius: 8px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #555555;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #444444;
            }
        """)
        self.plugin_list.currentRowChanged.connect(self.display_plugin_details)
        splitter.addWidget(self.plugin_list)

        details_container = QWidget()
        details_layout = QVBoxLayout(details_container)
        
        self.plugin_detail_display = QTextEdit()
        self.plugin_detail_display.setReadOnly(True)
        self.plugin_detail_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        details_layout.addWidget(self.plugin_detail_display)

        actions_layout = QHBoxLayout()
        self.enable_checkbox = QCheckBox("Aktif")
        self.enable_checkbox.setStyleSheet("color: #e0e0e0;")
        # Bağlantı daha sonra yapılacak (plugin durumunu kaydetmek için)
        actions_layout.addWidget(self.enable_checkbox)
        actions_layout.addStretch()

        self.run_plugin_button = QPushButton("Test Çalıştır")
        self.run_plugin_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        self.run_plugin_button.clicked.connect(self.run_selected_plugin_test)
        actions_layout.addWidget(self.run_plugin_button)

        self.delete_plugin_button = QPushButton("Plugin Sil")
        self.delete_plugin_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        self.delete_plugin_button.clicked.connect(self.delete_selected_plugin)
        actions_layout.addWidget(self.delete_plugin_button)
        
        details_layout.addLayout(actions_layout)
        splitter.addWidget(details_container)
        
        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)

    def load_plugins(self):
        """Pluginleri yükler ve listeyi günceller."""
        self.plugin_list.clear()
        self.plugin_detail_display.clear()
        self.plugin_manager.load_plugins() # core/plugin_manager.py'dan
        
        if not self.plugin_manager.plugins:
            self.plugin_list.addItem("Henüz plugin bulunamadı.")
            return

        for plugin_name in self.plugin_manager.plugins.keys():
            self.plugin_list.addItem(plugin_name)

    def display_plugin_details(self, index):
        """Seçilen pluginin detaylarını gösterir."""
        if index < 0:
            self.plugin_detail_display.clear()
            self.enable_checkbox.setChecked(False)
            return

        plugin_name = self.plugin_list.item(index).text()
        plugin_module = self.plugin_manager.plugins.get(plugin_name)

        if plugin_module:
            details_text = f"""
            <h3 style='color:#007acc;'>{plugin_name}</h3>
            <p><b>Durum:</b> Yüklü</p>
            <p><b>Yol:</b> {plugin_module.__file__}</p>
            <p><b>Açıklama:</b> {getattr(plugin_module, '__doc__', 'Açıklama yok.')}</p>
            """
            self.plugin_detail_display.setHtml(details_text)
            # Plugin durumu için bir mekanizma eklenmeli
            self.enable_checkbox.setChecked(True) # Varsayılan olarak aktif gibi göster
        else:
            self.plugin_detail_display.clear()
            self.enable_checkbox.setChecked(False)

    def run_selected_plugin_test(self):
        """Seçilen plugini test amacıyla çalıştırır."""
        current_row = self.plugin_list.currentRow()
        if current_row >= 0:
            plugin_name = self.plugin_list.item(current_row).text()
            # Test için basit bir prompt verebiliriz veya bir diyalog kutusu açabiliriz
            test_query = QMessageBox.getText(self, "Plugin Testi", f"'{plugin_name}' plugini için bir test sorgusu girin:")
            if test_query[1]: # Kullanıcı 'OK'e bastıysa
                result = self.plugin_manager.execute_plugin(plugin_name, query=test_query[0])
                QMessageBox.information(self, "Plugin Test Sonucu", f"Plugin '{plugin_name}' çalıştırıldı. Sonuç:\n{result}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen test etmek için bir plugin seçin.")

    def delete_selected_plugin(self):
        """Seçilen plugini diskten siler."""
        current_row = self.plugin_list.currentRow()
        if current_row >= 0:
            plugin_name = self.plugin_list.item(current_row).text()
            plugin_path = self.plugin_manager.plugins[plugin_name].__file__

            reply = QMessageBox.question(self, 'Plugin Sil', 
                                         f"'{plugin_name}' pluginini silmek istediğinize emin misiniz? Bu işlem geri alınamaz.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    os.remove(plugin_path)
                    # Eğer __pycache__ dosyası varsa onu da sil
                    pycache_dir = os.path.join(os.path.dirname(plugin_path), "__pycache__")
                    compiled_file = os.path.join(pycache_dir, f"{plugin_name}.cpython-{sys.version_info.major}{sys.version_info.minor}.pyc")
                    if os.path.exists(compiled_file):
                        os.remove(compiled_file)

                    QMessageBox.information(self, "Başarılı", f"Plugin '{plugin_name}' başarıyla silindi.")
                    self.load_plugins() # Listeyi güncelle
                except OSError as e:
                    QMessageBox.critical(self, "Hata", f"Plugin silinirken hata oluştu: {e}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir plugin seçin.")

    def add_plugin_manually(self):
        """Kullanıcının dosya sisteminden plugin eklemesine olanak tanır."""
        initial_dir = os.path.join(os.getcwd(), "KayaVuln", "plugins")
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir)

        file_path, _ = QFileDialog.getOpenFileName(self, "Plugin Dosyasını Seç", initial_dir, "Python Pluginleri (*.py);;Tüm Dosyalar (*)")
        if file_path:
            destination_dir = os.path.join(os.getcwd(), "KayaVuln", "plugins")
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(destination_dir, file_name)

            if os.path.exists(destination_path):
                QMessageBox.warning(self, "Uyarı", "Bu plugin zaten mevcut. Lütfen farklı bir isimle ekleyin veya mevcut plugini kullanın.")
                return

            try:
                import shutil
                shutil.copy(file_path, destination_path)
                QMessageBox.information(self, "Başarılı", f"Plugin '{file_name}' başarıyla eklendi.")
                self.load_plugins()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Plugin eklenirken hata oluştu: {e}")