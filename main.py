import os
import sys
import glob
import subprocess
import threading
import requests
import json
import tempfile
import shutil
from dotenv import load_dotenv, set_key
import customtkinter as ctk
from PIL import Image
from playwright.sync_api import sync_playwright

VERSION = "1.0.0"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Carrega configurações do .env
load_dotenv()

class LoginConfigDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        
        self.title("Primeiro Acesso - Configuração")
        self.geometry("450x350")
        self.grab_set() # Torna a janela modal
        self.resizable(False, False)
        
        # Centralizar na tela
        self.after(10, self.lift) # Garante que fique por cima
        
        # UI
        ctk.set_appearance_mode("dark")
        
        self.lbl_title = ctk.CTkLabel(self, text="Configuração de Login", font=("Inter", 22, "bold"))
        self.lbl_title.pack(pady=(30, 20))
        
        self.lbl_desc = ctk.CTkLabel(self, text="Insira suas credenciais da TIM para o MicroStrategy.\nEsses dados ficarão salvos apenas no seu computador.", 
                                    font=("Inter", 12), text_color="#A9A9A9")
        self.lbl_desc.pack(pady=(0, 20))
        
        self.entry_user = ctk.CTkEntry(self, placeholder_text="E-mail (ex: T3755000@timbrasil.com.br)", width=350, height=40)
        self.entry_user.pack(pady=10)
        # Preencher se já houver algo
        user_atual = os.getenv("MSTR_USER", "")
        if user_atual: self.entry_user.insert(0, user_atual)
        
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=350, height=40)
        self.entry_pass.pack(pady=10)
        
        self.btn_save = ctk.CTkButton(self, text="Salvar e Continuar", command=self.salvar, 
                                      font=("Inter", 16, "bold"), width=350, height=45)
        self.btn_save.pack(pady=30)

    def salvar(self):
        usuario = self.entry_user.get().strip()
        senha = self.entry_pass.get().strip()
        
        if not usuario or not senha:
            return
            
        self.callback(usuario, senha)
        self.destroy()

class AutomaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("BotD-1 | Automação de Relatórios")
        
        # Modo escuro e estado de janela em zoom (Fullscreen no Windows)
        ctk.set_appearance_mode("dark")
        self.after(0, lambda: self.wm_state('zoomed'))
        
        # Define o ícone da janela
        icone_path = resource_path("d-1bot.ico")
        if os.path.exists(icone_path):
            self.iconbitmap(icone_path)
            
        # Inicia verificação de atualização em segundo plano
        threading.Thread(target=self.verificar_atualizacao, daemon=True).start()

        # UI Principal
        # Centralizando as linhas verticalmente
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Logo do Aplicativo
        logo_path = resource_path("d-1bot.png")
        if os.path.exists(logo_path):
            try:
                # Dimensões baseadas na proporção estética
                pil_image = Image.open(logo_path)
                logo_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(120, 120))
                self.lbl_logo = ctk.CTkLabel(self, image=logo_img, text="")
                self.lbl_logo.grid(row=1, column=0, pady=(0, 20))
            except Exception as e:
                print(f"Erro ao carregar o logotipo: {e}")

        # Verificação de Credenciais
        self.verificar_configuracao()
            
        # 2. Título

        self.lbl_title = ctk.CTkLabel(self, text="Painel de Automação MSTR", font=("Inter", 32, "bold"))
        self.lbl_title.grid(row=2, column=0, pady=(0, 10))
            
        # 3. Status Rápido
        self.lbl_status = ctk.CTkLabel(self, text="Pronto para iniciar.", font=("Inter", 20), text_color="#A9A9A9")
        self.lbl_status.grid(row=3, column=0, pady=(0, 40))
        
        # 4. Botão
        self.btn_start = ctk.CTkButton(self, text="Começar Fase 1", command=self.iniciar_fase1, 
                                       font=("Inter", 18, "bold"), width=300, height=50, corner_radius=8)
        self.btn_start.grid(row=4, column=0, sticky="n", pady=(0, 40))
        
        # 5. Container de Logs (limitando a largura máxima com colunas virtuais)
        self.log_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.log_wrapper.grid(row=5, column=0, sticky="ew")
        self.log_wrapper.grid_columnconfigure(0, weight=1)
        self.log_wrapper.grid_columnconfigure(1, weight=4) # Container principal com peso 4
        self.log_wrapper.grid_columnconfigure(2, weight=1)
        
        # Frame Escuro do Log
        self.log_container = ctk.CTkFrame(self.log_wrapper, fg_color="#222222", corner_radius=10)
        self.log_container.grid(row=0, column=1, sticky="ew")
        self.log_container.grid_columnconfigure(0, weight=1)
        
        # 5.1. Header do Log
        self.log_header = ctk.CTkFrame(self.log_container, fg_color="transparent")
        self.log_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        self.log_header.grid_columnconfigure(0, weight=1)
        
        self.lbl_log_title = ctk.CTkLabel(self.log_header, text="Log de Status", font=("Inter", 18, "bold"), text_color="#E0E0E0")
        self.lbl_log_title.grid(row=0, column=0, sticky="w")
        
        self.btn_copy_log = ctk.CTkButton(self.log_header, text="Copiar log", width=120, height=35,
                                          command=self.copiar_log, font=("Inter", 14), corner_radius=6)
        self.btn_copy_log.grid(row=0, column=1, sticky="e")
        
        # 5.2. Textbox do Log
        self.txt_log = ctk.CTkTextbox(self.log_container, height=220, font=("Consolas", 15), 
                                      fg_color="#181818", text_color="#CCCCCC", state="disabled")
        self.txt_log.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
    def atualizar_status(self, texto, error=False):
        if not error:
            self.lbl_status.configure(text=texto, text_color="#A9A9A9")

        self.txt_log.configure(state="normal")
        log_line = f"> {texto}\n"
        self.txt_log.insert("end", log_line)
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")
        
    def copiar_log(self):
        log_text = self.txt_log.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(log_text)
        
        # Animação rústica do botão copiando
        texto_original = self.btn_copy_log.cget("text")
        self.btn_copy_log.configure(text="Copiado! ✓")
        self.after(2000, lambda: self.btn_copy_log.configure(text=texto_original))
        
    def iniciar_fase1(self):
        self.btn_start.configure(state="disabled")
        
        # Limpar textbox
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")
        
        self.atualizar_status("Iniciando Automação e Navegador...")
        threading.Thread(target=self.rodar_playwright, daemon=True).start()
        
    def rodar_playwright(self):
        try:
            browsers_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path

            chromium_found = glob.glob(os.path.join(browsers_path, "chromium-*", "chrome-win64", "chrome.exe"))
            if not chromium_found:
                self.after(0, self.atualizar_status, "Chromium não encontrado. Instalando pela primeira vez (pode demorar)...")
                from playwright._impl._driver import compute_driver_executable
                driver = compute_driver_executable()
                result = subprocess.run([str(driver), "install", "chromium"], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(result.stderr or result.stdout)
                self.after(0, self.atualizar_status, "Chromium instalado com sucesso.")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, args=['--start-maximized'])
                context = browser.new_context(no_viewport=True)
                page = context.new_page()
                
                self.after(0, self.atualizar_status, "Acessando URL base...")
                url = "https://microstrategyqualidade.internal.timbrasil.com.br/MicroStrategy/servlet/mstrWeb?continue"
                page.goto(url)
                
                self.after(0, self.atualizar_status, "Inserindo Credenciais (Microsoft)...")
                email = os.getenv("MSTR_USER", "T3755000@timbrasil.com.br")
                
                try:
                    email_input = page.wait_for_selector('input[type="email"]', state='visible', timeout=10000)
                    if email_input:
                        email_input.fill(email)
                        page.locator('input[type="submit"]').click()
                except Exception as e:
                    print(f"Formulário de email ignorado: {e}")
                
                senha = os.getenv("MSTR_PASS", "")
                if senha and senha != "SUA_SENHA_AQUI":
                    try:
                        senha_input = page.wait_for_selector('input[type="password"]', state='visible', timeout=15000)
                        if senha_input:
                            senha_input.fill(senha)
                            page.locator('input[type="submit"]').click()
                    except:
                        self.after(0, self.atualizar_status, "Campo de senha não localizado. Siga manualmente.")
                else:
                    self.after(0, self.atualizar_status, "Senha não detectada no .env. Preencha manualmente no portal.")
                
                self.after(0, self.atualizar_status, "Aguardando ação do usuário...")
                
                page.wait_for_selector('a.mstrLargeIconViewItemLink', state='visible', timeout=120000)
                
                self.after(0, self.atualizar_status, "Login Concluído. Acessando Painel MicroStrategy (Fim da Fase 1)")
                
                page.wait_for_timeout(30000)
                browser.close()
                self.after(0, lambda: self.btn_start.configure(state="normal"))
                
        except Exception as e:
            # Mostra nome do erro do Playwright pro log ficar verboso como na print
            erro_clean = f"Erro na Fase 1: {type(e).__name__} at url... Call log: {e}" 
            self.after(0, self.atualizar_status, erro_clean, True)
            self.after(0, lambda: self.btn_start.configure(state="normal"))

    def verificar_atualizacao(self):
        """Verifica se há uma nova versão no GitHub Releases"""
        try:
            token = os.getenv("GITHUB_TOKEN")
            repo = os.getenv("GITHUB_REPO") # Formato: usuario/repositorio
            
            if not token or not repo or "SEU_TOKEN" in token:
                return

            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tag_name = data.get("tag_name", "").replace("v", "")
                
                # Comparação simples de versão
                if tag_name > VERSION:
                    download_url = ""
                    # Procura o primeiro asset que seja .exe
                    for asset in data.get("assets", []):
                        if asset.get("name", "").endswith(".exe"):
                            download_url = asset.get("browser_download_url")
                            break
                    
                    if download_url:
                        self.after(0, lambda: self.abrir_dialogo_update(tag_name, download_url))
        except Exception as e:
            print(f"Erro ao verificar atualização: {e}")

    def abrir_dialogo_update(self, nova_versao, url):
        """Mostra um aviso de que há uma atualização disponível"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Atualização Disponível")
        dialog.geometry("400x200")
        dialog.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(dialog, text=f"Uma nova versão ({nova_versao}) está disponível!\nDeseja atualizar agora?", 
                           font=("Inter", 14))
        lbl.pack(pady=30)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        btn_sim = ctk.CTkButton(btn_frame, text="Sim, atualizar", width=120, 
                                command=lambda: [dialog.destroy(), self.realizar_update(url)])
        btn_sim.grid(row=0, column=0, padx=10)
        
        btn_nao = ctk.CTkButton(btn_frame, text="Depois", width=120, fg_color="gray",
                                command=dialog.destroy)
        btn_nao.grid(row=0, column=1, padx=10)

    def realizar_update(self, url):
        """Baixa o novo executável e inicia o processo de substituição"""
        self.atualizar_status("Baixando atualização... Por favor, aguarde.")
        
        def download_thread():
            try:
                token = os.getenv("GITHUB_TOKEN")
                headers = {"Authorization": f"token {token}"}
                
                response = requests.get(url, headers=headers, stream=True)
                if response.status_code == 200:
                    ext = ".exe"
                    temp_dir = tempfile.gettempdir()
                    new_exe_path = os.path.join(temp_dir, f"BotD1_new{ext}")
                    
                    with open(new_exe_path, 'wb') as f:
                        shutil.copyfileobj(response.raw, f)
                    
                    self.after(0, lambda: self.atualizar_status("Download concluído. Reiniciando para aplicar..."))
                    self.aplicar_update(new_exe_path)
                else:
                    self.after(0, lambda: self.atualizar_status("Erro no download da atualização.", True))
            except Exception as e:
                self.after(0, lambda: self.atualizar_status(f"Erro ao atualizar: {e}", True))

        threading.Thread(target=download_thread, daemon=True).start()

    def aplicar_update(self, novo_exe):
        """Cria um arquivo .bat que substitui o executável atual e reinicia o app"""
        current_exe = sys.executable
        if not current_exe.endswith(".exe"):
            # Se estiver rodando como script .py, apenas avisa
            print("Update ignorado: Rodando como script Python.")
            return

        batch_path = os.path.join(tempfile.gettempdir(), "update_bot.bat")
        
        batch_content = f"""@echo off
timeout /t 2 /nobreak > nul
del "{current_exe}"
move /y "{novo_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
        with open(batch_path, "w") as f_bat:
            f_bat.write(batch_content)
        
        subprocess.Popen([batch_path], shell=True)
        self.quit()
        sys.exit()

    def verificar_configuracao(self):
        """Verifica se o .env tem as credenciais, senão abre o diálogo"""
        user = os.getenv("MSTR_USER")
        senha = os.getenv("MSTR_PASS")
        
        if not user or not senha or senha == "SUA_SENHA_AQUI":
            self.after(500, self.abrir_dialogo_login)

    def abrir_dialogo_login(self):
        LoginConfigDialog(self, self.salvar_credenciais)

    def salvar_credenciais(self, user, senha):
        """Salva no arquivo .env e atualiza variáveis de ambiente"""
        env_path = ".env"
        # Cria o arquivo se não existir
        if not os.path.exists(env_path):
            with open(env_path, 'w') as f:
                f.write("")
        
        set_key(env_path, "MSTR_USER", user)
        set_key(env_path, "MSTR_PASS", senha)
        
        # Atualiza em memória
        os.environ["MSTR_USER"] = user
        os.environ["MSTR_PASS"] = senha
        
        self.atualizar_status("Configurações salvas com sucesso!")

if __name__ == "__main__":
    app = AutomaApp()
    app.mainloop()

