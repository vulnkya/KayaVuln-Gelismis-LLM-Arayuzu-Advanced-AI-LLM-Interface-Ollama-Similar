# core/model_downloader.py
import os
from huggingface_hub import hf_hub_download
# from huggingface_hub.utils import HfHubDownloadError # Bu satırı sildik veya yorumladık
from core.model_loader import ModelLoader, BaseModel

class ModelDownloader:
    @staticmethod
    def download_model(repo_id: str, filename: str, subfolder: str = None):
        local_dir = ModelLoader.MODEL_DIR
        os.makedirs(local_dir, exist_ok=True)

        print(f"'{repo_id}' deposundan '{filename}' modeli indiriliyor...")
        try:
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                subfolder=subfolder,
                cache_dir=local_dir,
                local_dir=local_dir,
                local_dir_use_symlinks=False
            )
            print(f"Model başarıyla indirildi: {local_path}")
            
            model_name = filename.replace(".gguf", "")
            size = os.path.getsize(local_path)
            new_model = BaseModel(
                name=model_name,
                path=local_path,
                size_bytes=size,
                format_type="GGUF",
                description=f"Hugging Face'den indirildi: {repo_id}"
            )
            
            existing_models = ModelLoader.load_models_info()
            found = False
            for i, model in enumerate(existing_models):
                if model.path == new_model.path:
                    existing_models[i] = new_model
                    found = True
                    break
            if not found:
                existing_models.append(new_model)
            
            ModelLoader.save_models_info(existing_models)
            print("İndirilen model, model listesine eklendi/güncellendi.")
            return local_path

        except Exception as e: # Sadece genel Exception yakalayın
            print(f"Model indirilirken bir hata oluştu: {e}")
            return None