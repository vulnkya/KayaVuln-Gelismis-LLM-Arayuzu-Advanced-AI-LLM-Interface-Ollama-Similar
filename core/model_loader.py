import os
import json

class BaseModel:
    def __init__(self, name, path, size_bytes, format_type="GGUF", description="", status="Available"): # 'status' parametresini buraya ekleyin
        self.name = name
        self.path = path
        self.size_bytes = size_bytes
        self.format_type = format_type
        self.description = description
        self.status = status # Şimdi burada da kullanabiliriz
        
    def to_dict(self):
        return {
            "name": self.name,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "format_type": self.format_type,
            "description": self.description,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            path=data["path"],
            size_bytes=data["size_bytes"],
            format_type=data.get("format_type", "Unknown"),
            description=data.get("description", ""),
            status=data.get("status", "Available")
        )

class ModelLoader:
    MODEL_DIR = os.path.join(os.getcwd(), "KayaVuln", "models")
    CONFIG_PATH = os.path.join(os.getcwd(), "KayaVuln", "config", "models.json")

    @staticmethod
    def scan_models():
        """
        Belirtilen dizini tarar ve bulunan modelleri bir BaseModel nesneleri listesi olarak döndürür.
        Şu an için sadece .gguf dosyalarını algılar.
        """
        if not os.path.exists(ModelLoader.MODEL_DIR):
            os.makedirs(ModelLoader.MODEL_DIR)
            return []

        found_models = []
        for filename in os.listdir(ModelLoader.MODEL_DIR):
            if filename.endswith(".gguf"):
                file_path = os.path.join(ModelLoader.MODEL_DIR, filename)
                try:
                    model_name = filename.replace(".gguf", "")
                    size = os.path.getsize(file_path)
                    model = BaseModel(
                        name=model_name,
                        path=file_path,
                        size_bytes=size,
                        format_type="GGUF",
                        description=f"Local GGUF model: {model_name}"
                    )
                    found_models.append(model)
                except Exception as e:
                    print(f"Model '{filename}' yüklenirken hata oluştu: {e}")
        return found_models

    @staticmethod
    def save_models_info(models):
        """Modellerin bilgilerini JSON dosyasına kaydeder."""
        os.makedirs(os.path.dirname(ModelLoader.CONFIG_PATH), exist_ok=True)
        with open(ModelLoader.CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump([model.to_dict() for model in models], f, indent=4)

    @staticmethod
    def load_models_info():
        """JSON dosyasından modellerin bilgilerini yükler."""
        if not os.path.exists(ModelLoader.CONFIG_PATH):
            return []
        with open(ModelLoader.CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [BaseModel.from_dict(item) for item in data]