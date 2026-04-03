from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QColor, QFont
from PyQt5.QtCore import Qt, QEvent # QEvent'ı import edin

from core.llm_inference import LLMInferenceWorker
from core.model_loader import ModelLoader, BaseModel # BaseModel'i de import ettiğinizden emin olun

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_model = None
        self.llm_inference_worker = None
        self.llm_thread = None 

        self.init_ui()
        self.load_available_models()

    def init_ui(self):
        layout = QVBoxLayout(self)

        model_selector_layout = QHBoxLayout()
        model_selector_layout.addWidget(QLabel("Model Seç:"))
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self.on_model_selected_from_combo)
        model_selector_layout.addWidget(self.model_combo)
        model_selector_layout.addStretch() 

        self.load_model_button = QPushButton("Modeli Yükle")
        self.load_model_button.clicked.connect(self.load_selected_model)
        model_selector_layout.addWidget(self.load_model_button)

        layout.addLayout(model_selector_layout)

        # Sohbet Geçmişi Alanı
        self.chat_history_display = QTextEdit()
        self.chat_history_display.setReadOnly(True)
        self.chat_history_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 10px;
                font-family: Arial;
                font-size: 14px;
            }
        """)
        self.chat_history_display.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.chat_history_display)

        input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Mesajınızı buraya yazın...")
        self.message_input.setFixedHeight(50) # Tek satırlık gibi görünmesi için
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: #333333;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        self.message_input.setFont(QFont("Segoe UI", 10))
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Gönder")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc; /* Mavi gönder butonu */
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
        """)
        self.send_button.setFixedWidth(100)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    
    def load_available_models(self):
        """ModelLoader'dan mevcut modelleri çekip ComboBox'a doldurur."""
        self.model_combo.clear()
        models = ModelLoader.load_models_info() # 
        if not models:
            self.model_combo.addItem("Henüz Model Yok")
            self.model_combo.setEnabled(False)
            self.load_model_button.setEnabled(False)
            return

        self.model_combo.setEnabled(True)
        self.load_model_button.setEnabled(True)
        for model in models:
            self.model_combo.addItem(f"{model.name} ({model.format_type})", model)
        
        # İlk modeli otomatik seç
        if self.model_combo.count() > 0:
            self.on_model_selected_from_combo(0)

    def set_current_model(self, model_info):
        """Model Manager'dan bir model seçildiğinde çağrılır."""
        idx = self.model_combo.findData(model_info)
        if idx != -1:
            self.model_combo.setCurrentIndex(idx)
        else:
            # Model yeni indirilmiş olabilir, combo'yu yenile
            self.load_available_models()
            idx = self.model_combo.findData(model_info)
            if idx != -1:
                self.model_combo.setCurrentIndex(idx)

        self.current_model = model_info
        self.chat_history_display.append(f"<p style='color:#007acc;'><b>KayaVuln:</b> '{model_info.name}' modeli sohbet için seçildi. Henüz yüklenmedi.</p>")

    def on_model_selected_from_combo(self, index):
        """ComboBox'tan bir model seçildiğinde current_model'ı ayarlar."""
        model_data = self.model_combo.itemData(index)
        if isinstance(model_data, BaseModel): # Sadece BaseModel kullanın
            self.current_model = model_data
            self.chat_history_display.append(f"<p style='color:#007acc;'><b>KayaVuln:</b> '{model_data.name}' modeli hazırda bekliyor.</p>")
        else:
            self.current_model = None

    def load_selected_model(self):
        """Seçilen modeli LLM çıkarım worker'ına yükler."""
        if not self.current_model:
            self.chat_history_display.append("<p style='color:red;'>Lütfen önce bir model seçin!</p>")
            return

        if self.llm_inference_worker and self.llm_thread and self.llm_thread.isRunning():
            self.chat_history_display.append("<p style='color:orange;'>Zaten bir model yüklü ve çalışıyor.</p>")
            return

        self.chat_history_display.append(f"<p style='color:#007acc;'><b>KayaVuln:</b> '{self.current_model.name}' modeli yükleniyor... Bu biraz zaman alabilir.</p>")
        self.send_button.setEnabled(False)
        self.load_model_button.setEnabled(False)

        # Ayrı bir thread'de modeli yükle
        self.llm_thread = QThread()
        # LLMInferenceWorker'ın __init__ metodunu thread içinde çalıştırmak için
        # modeli yükleme işlemini ayrı bir metoda taşıdık.
        self.llm_inference_worker = LLMInferenceWorker(model_path=self.current_model.path)
        self.llm_inference_worker.moveToThread(self.llm_thread)

        self.llm_thread.started.connect(self.llm_inference_worker.load_model_in_thread)
        self.llm_inference_worker.model_loaded_signal.connect(self.on_model_loaded)
        self.llm_inference_worker.error_signal.connect(self.on_error)
        self.llm_inference_worker.response_signal.connect(self.display_response)

        self.llm_thread.start()

    def on_model_loaded(self, success):
        """Model yüklendiğinde veya yüklenemediğinde çağrılır."""
        self.send_button.setEnabled(True)
        self.load_model_button.setEnabled(True)
        if success:
            self.chat_history_display.append(f"<p style='color:green;'><b>KayaVuln:</b> Model '{self.current_model.name}' başarıyla yüklendi!</p>")
        else:
            self.chat_history_display.append(f"<p style='color:red;'><b>KayaVuln:</b> Model '{self.current_model.name}' yüklenirken bir hata oluştu.</p>")
            if self.llm_thread.isRunning():
                self.llm_thread.quit()
                self.llm_thread.wait()
            self.llm_inference_worker = None # Worker'ı sıfırla

    def on_error(self, error_message):
        """Worker'dan gelen hataları görüntüler."""
        self.chat_history_display.append(f"<p style='color:red;'><b>HATA:</b> {error_message}</p>")
        self.send_button.setEnabled(True)
        self.load_model_button.setEnabled(True)
        if self.llm_thread and self.llm_thread.isRunning():
            self.llm_thread.quit()
            self.llm_thread.wait()
        self.llm_inference_worker = None


    def send_message(self):
        if not self.llm_inference_worker or not self.llm_inference_worker.is_model_loaded():
            self.chat_history_display.append("<p style='color:red;'>Lütfen önce bir model yükleyin!</p>")
            return

        user_message = self.message_input.toPlainText().strip()
        if not user_message:
            return

        self.chat_history_display.append(f"<p style='color:#00aaff;'><b>Siz:</b> {user_message}</p>")
        self.message_input.clear()
        self.send_button.setEnabled(False)

        # LLM çıkarımını ayrı bir thread'de başlat
        self.llm_inference_worker.generate_response(user_message)


    def display_response(self, response_text):
        self.chat_history_display.append(f"<p style='color:#aaff00;'><b>KayaVuln:</b> {response_text}</p>")
        self.send_button.setEnabled(True)