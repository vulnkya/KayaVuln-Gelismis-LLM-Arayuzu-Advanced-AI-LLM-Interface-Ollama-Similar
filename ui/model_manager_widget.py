import os # Bu satırı ekleyin

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QSplitter, QTextEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

from core.model_loader import ModelLoader, BaseModel # BaseModel'i de import ettiğinizden emin olun

# ... (kodun geri kalanı)

class ModelManagerWidget(QWidget):
    model_selected_signal = pyqtSignal(object) # Seçilen modelin BaseModel objesini gönderir

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_models()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Üst kısım: Başlık ve Yenile/Ekle Butonları
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<h2 style='color:#e0e0e0;'>Model Yöneticisi</h2>"))
        header_layout.addStretch()
        
        self.add_model_button = QPushButton("Model Ekle")
        self.add_model_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #005f99; }
        """)
        self.add_model_button.clicked.connect(self.add_model_manually)
        header_layout.addWidget(self.add_model_button)

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
        self.refresh_button.clicked.connect(self.refresh_models)
        header_layout.addWidget(self.refresh_button)
        main_layout.addLayout(header_layout)

        # Orta kısım: Modeller Listesi ve Detaylar için Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Modeller Listesi
        self.model_list = QListWidget()
        self.model_list.setStyleSheet("""
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
        self.model_list.currentRowChanged.connect(self.display_model_details)
        splitter.addWidget(self.model_list)

        # Model Detayları ve Aksiyonlar
        details_container = QWidget()
        details_layout = QVBoxLayout(details_container)
        
        self.model_detail_display = QTextEdit()
        self.model_detail_display.setReadOnly(True)
        self.model_detail_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        details_layout.addWidget(self.model_detail_display)

        actions_layout = QHBoxLayout()
        self.select_for_chat_button = QPushButton("Sohbette Kullan")
        self.select_for_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745; /* Yeşil */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        self.select_for_chat_button.clicked.connect(self.select_model_for_chat)
        actions_layout.addWidget(self.select_for_chat_button)

        self.delete_model_button = QPushButton("Modeli Sil")
        self.delete_model_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545; /* Kırmızı */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        self.delete_model_button.clicked.connect(self.delete_selected_model)
        actions_layout.addWidget(self.delete_model_button)
        
        details_layout.addLayout(actions_layout)
        splitter.addWidget(details_container)
        
        splitter.setSizes([300, 700]) # Oranları ayarla
        main_layout.addWidget(splitter)

    def refresh_models(self):
        """Modelleri yeniden tarar ve listeyi günceller."""
        self.model_list.clear()
        self.model_detail_display.clear()
        self.models = ModelLoader.scan_models() # core/model_loader.py'dan
        ModelLoader.save_models_info(self.models) # Güncel listeyi kaydet

        if not self.models:
            self.model_list.addItem("Henüz yerel model bulunamadı.")
            return

        for model in self.models:
            self.model_list.addItem(f"{model.name} ({model.format_type})")

    def display_model_details(self, index):
        """Seçilen modelin detaylarını gösterir."""
        if index < 0 or index >= len(self.models):
            self.model_detail_display.clear()
            return
        
        model = self.models[index]
        details_text = f"""
        <h3 style='color:#007acc;'>{model.name}</h3>
        <p><b>Yol:</b> {model.path}</p>
        <p><b>Boyut:</b> {model.size_bytes / (1024*1024*1024):.2f} GB</p>
        <p><b>Format:</b> {model.format_type}</p>
        <p><b>Durum:</b> {model.status}</p>
        <p><b>Açıklama:</b> {model.description}</p>
        """
        self.model_detail_display.setHtml(details_text)

    def select_model_for_chat(self):
        """Seçilen modeli ChatWidget'a göndermek için sinyal yayar."""
        current_row = self.model_list.currentRow()
        if current_row >= 0 and current_row < len(self.models):
            selected_model = self.models[current_row]
            self.model_selected_signal.emit(selected_model)
            QMessageBox.information(self, "Model Seçildi", f"'{selected_model.name}' sohbet için seçildi.")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir model seçin.")

    def delete_selected_model(self):
        """Seçilen modeli diskten siler."""
        current_row = self.model_list.currentRow()
        if current_row >= 0 and current_row < len(self.models):
            model_to_delete = self.models[current_row]
            reply = QMessageBox.question(self, 'Modeli Sil', 
                                         f"'{model_to_delete.name}' modelini silmek istediğinize emin misiniz? Bu işlem geri alınamaz.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    os.remove(model_to_delete.path)
                    QMessageBox.information(self, "Başarılı", f"Model '{model_to_delete.name}' başarıyla silindi.")
                    self.refresh_models() # Listeyi güncelle
                except OSError as e:
                    QMessageBox.critical(self, "Hata", f"Model silinirken hata oluştu: {e}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir model seçin.")

    def add_model_manually(self):
        """Kullanıcının dosya sisteminden model eklemesine olanak tanır."""
        # Mevcut model dizinini varsayılan olarak ayarlayın
        initial_dir = os.path.join(os.getcwd(), "KayaVuln", "models")
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir)

        file_path, _ = QFileDialog.getOpenFileName(self, "Model Dosyasını Seç", initial_dir, "GGUF Modelleri (*.gguf);;Tüm Dosyalar (*)")
        if file_path:
            # Seçilen dosyayı modeller dizinine kopyala veya taşı
            destination_dir = os.path.join(os.getcwd(), "KayaVuln", "models")
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(destination_dir, file_name)

            if os.path.exists(destination_path):
                QMessageBox.warning(self, "Uyarı", "Bu model zaten mevcut. Lütfen farklı bir isimle ekleyin veya mevcut modeli kullanın.")
                return

            try:
                # Modeli kopyala (taşımak yerine kopyalamak daha güvenli olabilir)
                import shutil
                shutil.copy(file_path, destination_path)
                QMessageBox.information(self, "Başarılı", f"Model '{file_name}' başarıyla eklendi.")
                self.refresh_models()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Model eklenirken hata oluştu: {e}")