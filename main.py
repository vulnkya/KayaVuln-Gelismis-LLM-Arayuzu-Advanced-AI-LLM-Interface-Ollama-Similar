import sys
import typer # Yeni eklendi

# GUI bileşenleri
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

# CLI bileşenleri
from cli import app as cli_app # cli.py dosyasındaki typer uygulamasını import ediyoruz

def start_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Eğer komut satırında 'python main.py' dışında argümanlar varsa CLI'yi çalıştır
    # Veya sadece 'python main.py gui' gibi bir argümanla GUI'yi başlatabiliriz
    if len(sys.argv) > 1 and sys.argv[1] != "gui":
        # Typer CLI, sys.argv'den kendi argümanlarını işleyecektir.
        cli_app()
    else:
        # 'python main.py' veya 'python main.py gui' ile GUI'yi başlat
        # Eğer 'gui' argümanı varsa, onu sys.argv'den kaldır ki typer karışmasın
        if "gui" in sys.argv:
            sys.argv.remove("gui")
        start_gui()