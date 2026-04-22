import os
from dotenv import load_dotenv, set_key

def load_config():
    """Carrega as configurações do arquivo .env"""
    load_dotenv()

def get_config(key, default=None):
    """Retorna um valor de configuração"""
    return os.getenv(key, default)

def save_credentials(user, senha, env_path=".env"):
    """Salva as credenciais no .env e atualiza em memória"""
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write("")
    
    set_key(env_path, "MSTR_USER", user)
    set_key(env_path, "MSTR_PASS", senha)
    
    os.environ["MSTR_USER"] = user
    os.environ["MSTR_PASS"] = senha

def is_configured():
    """Verifica se as credenciais básicas estão configuradas"""
    user = os.getenv("MSTR_USER")
    senha = os.getenv("MSTR_PASS")
    return bool(user and senha and senha != "SUA_SENHA_AQUI")
