import os
import sys
import zipfile
import hashlib
import json
import subprocess
import shutil
import argparse

def get_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def build():
    parser = argparse.ArgumentParser(description="Build Modular BotD-1")
    parser.add_argument("--major", action="store_true", help="Atualiza a versão do App (EXE) além da lógica")
    args = parser.parse_args()

    print("--- Iniciando Build Modular BotD-1 ---")
    
    # 1. Carregar versão atual
    with open("version.json", "r") as f:
        version_data = json.load(f)
    
    print(f"Versão atual: App={version_data['app_version']}, Logic={version_data['logic_version']}")
    
    # 2. Incrementar versão
    if args.major:
        # Incrementa App Version (1.0.0 -> 1.0.1)
        app_parts = version_data['app_version'].split('.')
        app_parts[-1] = str(int(app_parts[-1]) + 1)
        version_data['app_version'] = ".".join(app_parts)
        print(f"Nova versão do App: {version_data['app_version']}")

    # Sempre incrementa a versão da lógica
    v_parts = version_data['logic_version'].split('.')
    v_parts[-1] = str(int(v_parts[-1]) + 1)
    version_data['logic_version'] = ".".join(v_parts)
    print(f"Nova versão da lógica: {version_data['logic_version']}")
    
    # 3. Criar o logic.zip
    zip_name = "logic.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
        
    print("Compactando pasta src...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("src"):
            for file in files:
                if "__pycache__" not in root:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path)
        # Inclui o version.json dentro do zip também para consistência
        zipf.writestr("version.json", json.dumps(version_data, indent=4))

    # 4. Calcular Checksum
    checksum = get_checksum(zip_name)
    version_data['logic_checksum'] = checksum
    
    # 5. Salvar version.json atualizado
    with open("version.json", "w") as f:
        json.dump(version_data, f, indent=4)
        
    print(f"Zip criado com sucesso. Checksum: {checksum}")
    
    # 6. Mover para dist para facilitar o download/upload
    if not os.path.exists("dist"):
        os.makedirs("dist")
    shutil.copy(zip_name, os.path.join("dist", zip_name))
    shutil.copy("version.json", os.path.join("dist", "version.json"))
    
    # 7. Gerar o Executável (.exe)
    print("\n--- Iniciando geração do executável (.exe) ---")
    try:
        # Roda o PyInstaller usando o arquivo .spec
        # --noconfirm sobrescreve arquivos antigos na pasta dist
        subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "Bot D-1.spec"], check=True)
        print("Executável gerado com sucesso!")
    except subprocess.CalledProcessError:
        print("\n[ERRO] Falha ao rodar PyInstaller. O EXE não foi atualizado.")
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro inesperado: {e}")

    print("\n--- Processo Total Concluído! ---")
    print(f"App Version: {version_data['app_version']} | Logic Version: {version_data['logic_version']}")
    print("Tudo o que você precisa está na pasta './dist/':")
    print("  - BotD1.exe    (O programa principal)")
    print("  - logic.zip    (A lógica para atualizações rápidas)")
    print("  - version.json (O controle de versões e assinaturas)")

if __name__ == "__main__":
    build()
