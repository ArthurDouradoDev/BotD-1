import os
from .engine import ensure_chromium_installed, create_persistent_context
from playwright.sync_api import sync_playwright

def executar_fase1(callback_log, callback_finished):
    """Executa o login e verificação inicial (Fase 1)"""
    try:
        ensure_chromium_installed(callback_log)
        
        user_data_path = os.path.join(os.getenv("APPDATA"), "BotD1", "profile")
        
        with sync_playwright() as p:
            callback_log("Iniciando navegador com perfil persistente...")
            context = create_persistent_context(p, user_data_path)
            
            page = context.pages[0] if context.pages else context.new_page()
            
            callback_log("Acessando URL base...")
            url = "https://microstrategyqualidade.internal.timbrasil.com.br/MicroStrategy/servlet/mstrWeb?continue"
            page.goto(url)
            
            callback_log("Verificando estado da sessão...")
            
            try:
                login_selector = 'input[type="email"]'
                dashboard_selector = 'a.mstrLargeIconViewItemLink'
                
                target = page.wait_for_selector(f"{login_selector}, {dashboard_selector}", timeout=15000)
                
                if page.query_selector(login_selector):
                    callback_log("Sessão não encontrada. Iniciando login (Microsoft)...")
                    email = os.getenv("MSTR_USER", "T3755000@timbrasil.com.br")
                    page.fill(login_selector, email)
                    page.click('input[type="submit"]')
                    
                    senha = os.getenv("MSTR_PASS", "")
                    if senha and senha != "SUA_SENHA_AQUI":
                        senha_input = page.wait_for_selector('input[type="password"]', state='visible', timeout=15000)
                        if senha_input:
                            senha_input.fill(senha)
                            page.click('input[type="submit"]')
                    else:
                        callback_log("Senha não detectada. Preencha manualmente no portal.")
                    
                    callback_log("Aguardando aprovação no Authenticator...")
                else:
                    callback_log("Sessão ativa detectada! Pulando etapa de login.")
            
            except Exception:
                callback_log("Não foi possível determinar o estado da sessão. Tentando prosseguir...")
            
            callback_log("Aguardando ação do usuário...")
            page.wait_for_selector('a.mstrLargeIconViewItemLink', state='visible', timeout=120000)
            
            callback_log("Login Concluído. Acessando Painel MicroStrategy (Fim da Fase 1)")
            
            # TODO: Placeholder para Fase 2 e 3
            # page.wait_for_timeout(5000)
            
            page.wait_for_timeout(30000) # Manter aberto por um tempo para visualização
            context.close()
            callback_finished()

    except Exception as e:
        callback_log(f"Erro na Fase 1: {type(e).__name__} - {str(e)}", True)
        callback_finished()
