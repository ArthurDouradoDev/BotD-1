import customtkinter as ctk
from src.utils.config import get_config

class LoginConfigDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        
        self.title("Primeiro Acesso - Configuração")
        self.geometry("450x350")
        self.grab_set() # Torna a janela modal
        self.resizable(False, False)
        
        self.after(10, self.lift) 
        
        # UI
        ctk.set_appearance_mode("dark")
        
        self.lbl_title = ctk.CTkLabel(self, text="Configuração de Login", font=("Inter", 22, "bold"))
        self.lbl_title.pack(pady=(30, 20))
        
        self.lbl_desc = ctk.CTkLabel(self, text="Insira suas credenciais da TIM para o MicroStrategy.\nEsses dados ficarão salvos apenas no seu computador.", 
                                    font=("Inter", 12), text_color="#A9A9A9")
        self.lbl_desc.pack(pady=(0, 20))
        
        self.entry_user = ctk.CTkEntry(self, placeholder_text="E-mail (ex: T1234567@timbrasil.com.br)", width=350, height=40)
        self.entry_user.pack(pady=10)
        
        user_atual = get_config("MSTR_USER", "")
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

class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, nova_versao, on_confirm):
        super().__init__(parent)
        self.title("Atualização Disponível")
        self.geometry("400x200")
        self.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(self, text=f"Uma nova versão ({nova_versao}) está disponível!\nDeseja atualizar agora?", 
                           font=("Inter", 14))
        lbl.pack(pady=30)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        btn_sim = ctk.CTkButton(btn_frame, text="Sim, atualizar", width=120, 
                                command=lambda: [self.destroy(), on_confirm()])
        btn_sim.grid(row=0, column=0, padx=10)
        
        btn_nao = ctk.CTkButton(btn_frame, text="Depois", width=120, fg_color="gray",
                                command=self.destroy)
        btn_nao.grid(row=0, column=1, padx=10)
