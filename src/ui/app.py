import os
import threading
import customtkinter as ctk
from PIL import Image
from src.utils.helpers import resource_path
from src.utils.config import is_configured, save_credentials
from src.utils.updater import check_for_updates, download_update, apply_update
from src.automation.flows import executar_fase1
from .dialogs import LoginConfigDialog, UpdateDialog

VERSION = "1.0.0"

class AutomaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("BotD-1 | Automação de Relatórios")
        
        ctk.set_appearance_mode("dark")
        self.after(0, lambda: self.wm_state('zoomed'))
        
        icone_path = resource_path(os.path.join("src", "assets", "d-1bot.ico"))
        if os.path.exists(icone_path):
            self.iconbitmap(icone_path)
            
        threading.Thread(target=self.verificar_atualizacao, daemon=True).start()

        self.setup_ui()
        self.verificar_configuracao_inicial()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Logo
        logo_path = resource_path(os.path.join("src", "assets", "d-1bot.png"))
        if os.path.exists(logo_path):
            try:
                pil_image = Image.open(logo_path)
                logo_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(120, 120))
                self.lbl_logo = ctk.CTkLabel(self, image=logo_img, text="")
                self.lbl_logo.grid(row=1, column=0, pady=(0, 20))
            except Exception as e:
                print(f"Erro ao carregar o logotipo: {e}")

        # Título
        self.lbl_title = ctk.CTkLabel(self, text="Painel de Automação MSTR", font=("Inter", 32, "bold"))
        self.lbl_title.grid(row=2, column=0, pady=(0, 10))
            
        # Status Rápido
        self.lbl_status = ctk.CTkLabel(self, text="Pronto para iniciar.", font=("Inter", 20), text_color="#A9A9A9")
        self.lbl_status.grid(row=3, column=0, pady=(0, 40))
        
        # Botão
        self.btn_start = ctk.CTkButton(self, text="Iniciar Automação (Fases 1 e 2)", command=self.iniciar_fase1, 
                                       font=("Inter", 18, "bold"), width=300, height=50, corner_radius=8)
        self.btn_start.grid(row=4, column=0, sticky="n", pady=(0, 40))
        
        # Log Container
        self.log_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.log_wrapper.grid(row=5, column=0, sticky="ew")
        self.log_wrapper.grid_columnconfigure(0, weight=1)
        self.log_wrapper.grid_columnconfigure(1, weight=4) 
        self.log_wrapper.grid_columnconfigure(2, weight=1)
        
        self.log_container = ctk.CTkFrame(self.log_wrapper, fg_color="#222222", corner_radius=10)
        self.log_container.grid(row=0, column=1, sticky="ew")
        self.log_container.grid_columnconfigure(0, weight=1)
        
        self.log_header = ctk.CTkFrame(self.log_container, fg_color="transparent")
        self.log_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        self.log_header.grid_columnconfigure(0, weight=1)
        
        self.lbl_log_title = ctk.CTkLabel(self.log_header, text="Log de Status", font=("Inter", 18, "bold"), text_color="#E0E0E0")
        self.lbl_log_title.grid(row=0, column=0, sticky="w")
        
        self.btn_copy_log = ctk.CTkButton(self.log_header, text="Copiar log", width=120, height=35,
                                          command=self.copiar_log, font=("Inter", 14), corner_radius=6)
        self.btn_copy_log.grid(row=0, column=1, sticky="e")
        
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
        
        texto_original = self.btn_copy_log.cget("text")
        self.btn_copy_log.configure(text="Copiado! ✓")
        self.after(2000, lambda: self.btn_copy_log.configure(text=texto_original))

    def iniciar_fase1(self):
        self.btn_start.configure(state="disabled")
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")
        
        self.atualizar_status("Iniciando Automação...")
        
        threading.Thread(
            target=executar_fase1, 
            args=(
                lambda msg, err=False: self.after(0, self.atualizar_status, msg, err),
                lambda: self.after(0, lambda: self.btn_start.configure(state="normal"))
            ), 
            daemon=True
        ).start()

    def verificar_configuracao_inicial(self):
        if not is_configured():
            self.after(500, lambda: LoginConfigDialog(self, self.callback_salvar_credentials))

    def callback_salvar_credentials(self, user, senha):
        save_credentials(user, senha)
        self.atualizar_status("Configurações salvas com sucesso!")

    def verificar_atualizacao(self):
        update_info = check_for_updates(VERSION)
        if update_info:
            self.after(0, lambda: UpdateDialog(self, update_info["version"], 
                                             lambda: self.realizar_update(update_info["url"])))

    def realizar_update(self, url):
        self.atualizar_status("Baixando atualização... Por favor, aguarde.")
        
        def run_update():
            new_exe = download_update(url, self.atualizar_status)
            if new_exe:
                self.after(0, self.atualizar_status, "Download concluído. Reiniciando...")
                if apply_update(new_exe):
                    self.quit()

        threading.Thread(target=run_update, daemon=True).start()
