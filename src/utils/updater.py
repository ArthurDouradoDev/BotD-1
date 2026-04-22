import os
import sys
import requests
import json
import hashlib
import shutil
from .config import get_config

def get_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_current_logic_version():
    """Lê a versão da lógica do version.json local (pode estar no zip ou no exe)"""
    try:
        # Tenta carregar do version.json na raiz do projeto (no diretório de execução)
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        version_file = os.path.join(base_path, "version.json")
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                return json.load(f).get("logic_version", "1.0.0")
    except:
        pass
    return "1.0.0"

def check_for_updates(current_app_version):
    """Verifica se há uma nova versão de App ou de Lógica no GitHub"""
    try:
        token = get_config("GITHUB_TOKEN")
        repo = get_config("GITHUB_REPO")
        
        if not token or not repo or "SEU_TOKEN" in token:
            return None

        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tag_name = data.get("tag_name", "").replace("v", "")
            
            # 1. Verifica se o APP (EXE) precisa de atualização (grande mudança)
            if tag_name > current_app_version:
                for asset in data.get("assets", []):
                    if asset.get("name", "").endswith(".exe"):
                        return {"type": "app", "version": tag_name, "url": asset.get("browser_download_url")}

            # 2. Verifica se a LÓGICA (ZIP) precisa de atualização (mudança pequena/rápida)
            # Para isso, precisamos baixar o version.json do release para comparar as versões de lógica
            version_url = ""
            logic_url = ""
            for asset in data.get("assets", []):
                if asset.get("name", "") == "version.json":
                    version_url = asset.get("browser_download_url")
                if asset.get("name", "") == "logic.zip":
                    logic_url = asset.get("browser_download_url")
            
            if version_url and logic_url:
                v_res = requests.get(version_url, headers=headers, timeout=10)
                if v_res.status_code == 200:
                    remote_version_data = v_res.json()
                    remote_logic_v = remote_version_data.get("logic_version", "0.0.0")
                    current_logic_v = get_current_logic_version()
                    
                    if remote_logic_v > current_logic_v:
                        return {
                            "type": "logic", 
                            "version": remote_logic_v, 
                            "url": logic_url,
                            "checksum": remote_version_data.get("logic_checksum", ""),
                            "version_data": remote_version_data
                        }
                        
    except Exception as e:
        print(f"Erro ao verificar atualização: {e}")
    return None

def download_update(update_info, callback_status):
    """Realiza o download dependendo do tipo (App ou Logic)"""
    try:
        token = get_config("GITHUB_TOKEN")
        headers = {"Authorization": f"token {token}"}
        
        callback_status(f"Baixando atualização de {update_info['type']} v{update_info['version']}...")
        
        response = requests.get(update_info["url"], headers=headers, stream=True)
        if response.status_code == 200:
            updates_dir = os.path.join(os.getenv("APPDATA"), "BotD1", "updates")
            if not os.path.exists(updates_dir):
                os.makedirs(updates_dir)

            if update_info["type"] == "logic":
                zip_path = os.path.join(updates_dir, "logic.zip")
                with open(zip_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                
                # Validação de Hash
                actual_hash = get_checksum(zip_path)
                if actual_hash == update_info["checksum"]:
                    # Salva o novo version.json para o bootstrap reconhecer
                    with open(os.path.join(updates_dir, "version.json"), "w") as f:
                        json.dump(update_info["version_data"], f, indent=4)
                    callback_status("Atualização de lógica concluída! Reinicie o app para aplicar.")
                    return True
                else:
                    os.remove(zip_path)
                    callback_status("Erro: Checksum da atualização não confere. Download cancelado.", True)
            else:
                # Caso seja atualização de app completo (.exe)
                # Mantemos o comportamento anterior ou similar para o EXE
                pass
                
        else:
            callback_status("Erro no servidor de atualizações.", True)
    except Exception as e:
        callback_status(f"Erro no processo de update: {e}", True)
    return False

def apply_app_update(new_exe_path):
    """Lógica legada para aplicar update de EXE se necessário"""
    # (Mantido como placeholder ou removido se preferir apenas modular)
    pass
