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
            
            callback_log("Aguardando carregamento do portal (MFA/Redirecionamento)...")
            page.wait_for_selector('a.mstrLargeIconViewItemLink', state='visible', timeout=120000)
            
            callback_log("Login Concluído. Iniciando Fase 2...")
            
            # --- Início da Fase 2 ---
            executar_fase2(page, callback_log)
            # --- Fim da Fase 2 ---
            
            callback_log("Processo concluído com sucesso!")
            page.wait_for_timeout(5000) 
            context.close()
            callback_finished()

    except Exception as e:
        callback_log(f"Erro na automação: {type(e).__name__} - {str(e)}", True)
        callback_finished()

def executar_fase2(page, callback_log):
    """Navegação até My Subscriptions (Fase 2)"""
    try:
        callback_log("Acessando Painel MicroStrategy...")
        
        # Filtra pelo servidor "QualiTim" usando o seletor e o texto para maior segurança
        server_selector = 'a.mstrLargeIconViewItemLink'
        page.wait_for_selector(server_selector, state="visible", timeout=30000)
        
        # Tenta encontrar especificamente o que contém "Project=QualiTim" no href ou texto
        servers = page.query_selector_all(server_selector)
        target_server = None
        for s in servers:
            href = s.get_attribute("href") or ""
            if "Project=QualiTim" in href:
                target_server = s
                break
        
        if not target_server:
            callback_log("Servidor 'QualiTim' não identificado pelo link. Tentando clique genérico no primeiro servidor...", True)
            target_server = page.query_selector(server_selector)

        if target_server:
            target_server.click()
        else:
            raise Exception("Nenhum servidor encontrado na tela de seleção.")

        callback_log("Entrando em My Subscriptions...")
        
        subscriptions_selector = 'div.mstr-dskt-nm'
        
        def wait_for_subscriptions(p, retry=True):
            try:
                p.wait_for_selector(f"{subscriptions_selector} >> text='My Subscriptions'", state="visible", timeout=30000)
                return True
            except Exception:
                if retry:
                    callback_log("Elemento 'My Subscriptions' não apareceu. Recarregando página...")
                    p.reload()
                    return wait_for_subscriptions(p, retry=False)
                return False

        if not wait_for_subscriptions(page):
            callback_log("Aguardando validação manual: O seletor 'My Subscriptions' não foi encontrado automaticamente.")
            # Aguarda indefinidamente (ou por longo tempo) até o usuário resolver ou o elemento aparecer
            page.wait_for_selector(f"{subscriptions_selector} >> text='My Subscriptions'", state="visible", timeout=300000)

        # Clica no elemento
        page.click(f"{subscriptions_selector} >> text='My Subscriptions'")
        callback_log("Navegação da Fase 2 concluída: Chegamos às Subscriptions.")

    except Exception as e:
        callback_log(f"Falha na Fase 2: {str(e)}", True)
        raise e
