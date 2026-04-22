import os
import sys
import json
import hashlib

def get_checksum(file_path):
    if not os.path.exists(file_path):
        return None
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def bootstrap():
    """Tenta carregar a lógica atualizada do ZIP antes de iniciar o app"""
    updates_dir = os.path.join(os.getenv("APPDATA"), "BotD1", "updates")
    zip_path = os.path.join(updates_dir, "logic.zip")
    version_path = os.path.join(updates_dir, "version.json")
    
    if os.path.exists(zip_path) and os.path.exists(version_path):
        try:
            with open(version_path, "r") as f:
                version_data = json.load(f)
            
            expected_checksum = version_data.get("logic_checksum", "")
            actual_checksum = get_checksum(zip_path)
            
            if expected_checksum and actual_checksum == expected_checksum:
                # O ZIP é válido, adiciona ao caminho de busca do Python
                # Inserir no índice 0 garante prioridade sobre o que está embutido no EXE
                sys.path.insert(0, zip_path)
                return f"Logic {version_data.get('logic_version', 'dev')}"
            else:
                # Corrompido ou Checksum não bate
                os.remove(zip_path) # Remove para tentar baixar de novo na próxima
                print("Aviso: logic.zip corrompido ou inválido. Usando versão interna.")
        except Exception as e:
            print(f"Erro ao carregar atualização: {e}")
            
    return "Interna"

# Iniciar Bootstrap
logic_origin = bootstrap()

from src.utils.config import load_config
from src.ui.app import AutomaApp

def main():
    # Inicializa as configurações (.env)
    load_config()
    
    # Inicia a interface gráfica
    app = AutomaApp()
    # Podemos passar a origem da lógica para exibir na UI se desejado
    app.title(f"BotD-1 | Automação [{logic_origin}]")
    app.mainloop()

if __name__ == "__main__":
    main()
