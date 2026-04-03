import os
import importlib.util
import sys

class PluginManager:
    PLUGIN_DIR = os.path.join(os.getcwd(), "KayaVuln", "plugins")

    def __init__(self):
        self.plugins = {} # {plugin_name: plugin_module}

        if not os.path.exists(PluginManager.PLUGIN_DIR):
            os.makedirs(PluginManager.PLUGIN_DIR)

    def load_plugins(self):
        """Plugin dizinindeki tüm Python dosyalarını yükler."""
        self.plugins = {} # Her yüklemede eski pluginleri temizle
        
        for filename in os.listdir(PluginManager.PLUGIN_DIR):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3] # .py uzantısını kaldır
                file_path = os.path.join(PluginManager.PLUGIN_DIR, filename)

                try:
                    spec = importlib.util.spec_from_file_location(plugin_name, file_path)
                    if spec is None:
                        print(f"  Plugin '{plugin_name}' için spec bulunamadı.")
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Her plugin'in 'run' adında bir fonksiyonu olduğunu varsayıyoruz
                    if hasattr(module, 'run') and callable(module.run):
                        self.plugins[plugin_name] = module
                    else:
                        print(f"  Plugin '{plugin_name}' bir 'run' fonksiyonu içermiyor.")
                except Exception as e:
                    print(f"  Plugin '{plugin_name}' yüklenirken hata oluştu: {e}")
        
        return self.plugins

    def execute_plugin(self, plugin_name, *args, **kwargs):
        """Yüklenmiş bir plugini çalıştırır."""
        if plugin_name in self.plugins:
            try:
                result = self.plugins[plugin_name].run(*args, **kwargs)
                return result
            except Exception as e:
                return f"Hata: Plugin '{plugin_name}' çalıştırılırken hata oluştu: {e}"
        else:
            return None