import os
import sys
import requests
import tempfile
import shutil
import subprocess
from .config import get_config

def check_for_updates(current_version):
    """Verifica se há uma nova versão no GitHub Releases"""
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
            
            if tag_name > current_version:
                download_url = ""
                for asset in data.get("assets", []):
                    if asset.get("name", "").endswith(".exe"):
                        download_url = asset.get("browser_download_url")
                        break
                
                if download_url:
                    return {"version": tag_name, "url": download_url}
    except Exception as e:
        print(f"Erro ao verificar atualização: {e}")
    return None

def download_update(url, callback_status):
    """Baixa o novo executável"""
    try:
        token = get_config("GITHUB_TOKEN")
        headers = {"Authorization": f"token {token}"}
        
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            ext = ".exe"
            temp_dir = tempfile.gettempdir()
            new_exe_path = os.path.join(temp_dir, f"BotD1_new{ext}")
            
            with open(new_exe_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            return new_exe_path
        else:
            callback_status("Erro no download da atualização.", True)
    except Exception as e:
        callback_status(f"Erro ao baixar: {e}", True)
    return None

def apply_update(new_exe_path):
    """Aplica o update e reinicia o app"""
    current_exe = sys.executable
    if not current_exe.endswith(".exe"):
        return False

    batch_path = os.path.join(tempfile.gettempdir(), "update_bot.bat")
    
    batch_content = f"""@echo off
timeout /t 2 /nobreak > nul
del "{current_exe}"
move /y "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
    with open(batch_path, "w") as f_bat:
        f_bat.write(batch_content)
    
    subprocess.Popen([batch_path], shell=True)
    return True
