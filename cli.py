# cli.py
import typer
from rich.console import Console
from rich.table import Table
import os

from core.model_loader import ModelLoader
from core.model_downloader import ModelDownloader

app = typer.Typer(help="NovaAI CLI - LLM Yönetimi ve İndirme")
console = Console()

@app.command(name="list-models", help="Yerel olarak bulunan LLM modellerini listeler.")
def list_models():
    models = ModelLoader.scan_models()
    if not models:
        console.print("[yellow]Henüz yerel model bulunamadı.[/yellow]")
        return

    table = Table(title="Yerel NovaAI Modelleri")
    table.add_column("Ad", style="cyan", no_wrap=True)
    table.add_column("Format", style="magenta")
    table.add_column("Boyut (GB)", justify="right", style="green")
    table.add_column("Yol", style="white")

    for model in models:
        table.add_row(
            model.name,
            model.format_type,
            f"{model.size_bytes / (1024*1024*1024):.2f}",
            model.path
        )
    console.print(table)

@app.command(name="download-model", help="Hugging Face Hub'dan bir LLM modeli indirir.")
def download_model(
    repo_id: str = typer.Argument(..., help="Hugging Face model deposu ID'si (örn. TheBloke/Llama-2-7B-Chat-GGUF)"),
    filename: str = typer.Argument(..., help="Depodaki .gguf dosyasının adı (örn. llama-2-7b-chat.Q4_K_M.gguf)"),
    subfolder: str = typer.Option(None, "--subfolder", "-s", help="Dosyanın depodaki alt klasörü (isteğe bağlı)")
):
    console.print(f"[blue]İndirme başlatılıyor...[/blue]")
    local_path = ModelDownloader.download_model(repo_id, filename, subfolder)
    if local_path:
        console.print(f"[green]'{filename}' modeli başarıyla indirildi: {local_path}[/green]")
    else:
        console.print(f"[red]'{filename}' modelinin indirilmesi başarısız oldu.[/red]")

@app.command(name="delete-model", help="Yerel bir LLM modelini siler.")
def delete_model(
    model_name: str = typer.Argument(..., help="Silinecek modelin tam adı (örn. tinyllama-1.1b-chat-v1.0.Q2_K)")
):
    models = ModelLoader.load_models_info()
    model_to_delete = None
    for model in models:
        if model.name == model_name:
            model_to_delete = model
            break
    
    if not model_to_delete:
        console.print(f"[red]'{model_name}' adında bir model bulunamadı.[/red]")
        return

    try:
        os.remove(model_to_delete.path)
        # Config dosyasından da çıkarın
        models = [m for m in models if m.name != model_name]
        ModelLoader.save_models_info(models)
        console.print(f"[green]Model '{model_name}' başarıyla silindi.[/green]")
    except OSError as e:
        console.print(f"[red]Model '{model_name}' silinirken hata oluştu: {e}[/red]")

# Daha fazla CLI komutu eklenebilir (örn. pluginleri listele, plugin çalıştır)

if __name__ == "__main__":
    app()