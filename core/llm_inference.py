# core/llm_inference.py
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from llama_cpp import Llama
import os
from ui.settings_widget import SettingsManager # Ayarları almak için

class LLMInferenceWorker(QObject):
    model_loaded_signal = pyqtSignal(bool) # True başarılı, False başarısız
    response_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, model_path): # n_gpu_layers ve n_ctx artık buradan alınmayacak
        super().__init__()
        self.model_path = model_path
        self.llm = None
        self._is_model_loaded = False
        self.chat_history = []
        self.settings = SettingsManager.load_settings() # Ayarları yükle

    def load_model_in_thread(self):
        """Modeli ayrı bir thread'de yükler."""
        if not os.path.exists(self.model_path):
            self.error_signal.emit(f"Model dosyası bulunamadı: {self.model_path}")
            self.model_loaded_signal.emit(False)
            return

        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_gpu_layers=self.settings["llm_n_gpu_layers"], # Ayarlardan oku
                n_ctx=self.settings["llm_n_ctx"],               # Ayarlardan oku
                verbose=False, # Konsol çıktısını kapat
            )
            self._is_model_loaded = True
            self.model_loaded_signal.emit(True)
        except Exception as e:
            self.error_signal.emit(f"Model yüklenirken hata oluştu: {e}")
            self.model_loaded_signal.emit(False)
            self.llm = None
            self._is_model_loaded = False

    def is_model_loaded(self):
        return self._is_model_loaded

    def generate_response(self, user_prompt): # Parametreleri buradan kaldırdık
        """
        Kullanıcı prompt'una yanıt üretir.
        """
        if not self._is_model_loaded or not self.llm:
            self.error_signal.emit("Model yüklenmedi veya kullanıma hazır değil.")
            return

        # Ayarlardan güncel LLM parametrelerini al
        current_settings = SettingsManager.load_settings()

        messages = [{"role": "user", "content": user_prompt}]
        
        try:
            output = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=256, # Bu da ayarlanabilir olmalı, şimdilik sabit
                temperature=current_settings["llm_temperature"],
                top_p=current_settings["llm_top_p"],
                top_k=current_settings["llm_top_k"],
                repeat_penalty=current_settings["llm_repetition_penalty"],
            )
            response_content = output['choices'][0]['message']['content']
            
            self.response_signal.emit(response_content)
        except Exception as e:
            self.error_signal.emit(f"Yanıt üretirken hata oluştu: {e}")