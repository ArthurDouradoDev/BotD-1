import os
import glob
from datetime import datetime, timedelta
import win32com.client
from .engine import ensure_chromium_installed, launch_browser, create_standard_context
from playwright.sync_api import sync_playwright

def executar_fase1(callback_log, callback_finished):
    """Executa o login e verificação inicial (Fase 1)"""
    try:
        ensure_chromium_installed(callback_log)
        
        with sync_playwright() as p:
            callback_log("Iniciando navegador (Sessão Limpa)...")
            browser = launch_browser(p)
            context = create_standard_context(browser)
            
            page = context.new_page()
            
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

            # --- Início da Fase 3 ---
            executar_fase3(page, callback_log)
            # --- Fim da Fase 3 ---

            # --- Início da Fase 4 ---
            executar_fase4(callback_log)
            # --- Fim da Fase 4 ---
            
            callback_log("Processo concluído com sucesso!")
            page.wait_for_timeout(5000) 
            context.close()
            browser.close()
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

def executar_fase3(page, callback_log):
    """Módulo Downloader Profundo (Fase 3)"""
    try:
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)

        callback_log("Iniciando Fase 3: Extração de Relatórios...")

        # --- 4G ---
        callback_log("Baixando relatório 4G...")
        _baixar_relatorio(page, callback_log, output_dir, "D-1 OFENSORES 4G", "4G")
        _voltar_para_subscriptions(page, callback_log)

        # --- 5G ---
        callback_log("Baixando relatório 5G...")
        _baixar_relatorio(page, callback_log, output_dir, "D-1 OFENSORES 5G", "5G")
        _voltar_para_subscriptions(page, callback_log)

        # --- 3G ---
        callback_log("Processando data e baixando relatório 3G...")
        _baixar_relatorio_3g(page, callback_log, output_dir)

        callback_log("Fase 3 Concluída: Todos os relatórios baixados.")

    except Exception as e:
        callback_log(f"Falha na Fase 3: {str(e)}", True)
        raise e

def _baixar_relatorio(page, callback_log, output_dir, nome_link, prefixo):
    # Clica no link do relatório
    page.click(f"td.mstrLink >> text='{nome_link}'")
    
    # Aguarda redirecionamento para tabela e botão Report Home
    page.wait_for_selector("div:has-text('Report Home')", state="visible", timeout=120000)
    page.click("div:has-text('Report Home')")

    # Espera pelo botão de Export e intercepta o download
    with page.expect_download(timeout=120000) as download_info:
        page.click("span#tbExport")
    
    download = download_info.value
    
    # Adicionar sufixo de data
    data_sufixo = datetime.now().strftime("%Y%m%d")
    nome_arquivo = f"{prefixo}_{data_sufixo}.xlsx"
    caminho_final = os.path.join(output_dir, nome_arquivo)
    
    download.save_as(caminho_final)
    callback_log(f"Download concluído: {nome_arquivo}")

def _baixar_relatorio_3g(page, callback_log, output_dir):
    # Clica no link do 3G
    page.click("td.mstrLink >> text='Otimização por Célula 3G - Diário- D-1 SP - Huawei'")
    
    # Preenchimento de Data (Re-prompt)
    page.wait_for_selector("td.right.menu", state="visible", timeout=120000)
    page.click("td.right.menu")
    page.click("span:has-text('Re-prompt')")

    # Injeta Data D-1
    data_d1 = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    page.wait_for_selector("input#id_mstr111_txt", state="visible", timeout=60000)
    page.fill("input#id_mstr111_txt", data_d1)

    # Duplo clique em Run Report
    page.click("input#id_mstr155")
    page.wait_for_timeout(2000)
    page.click("input#id_mstr155")

    # Botão Report Home e Export
    page.wait_for_selector("div:has-text('Report Home')", state="visible", timeout=120000)
    page.click("div:has-text('Report Home')")

    with page.expect_download(timeout=120000) as download_info:
        page.click("span#tbExport")

    download = download_info.value
    data_sufixo = datetime.now().strftime("%Y%m%d")
    nome_arquivo = f"3G_{data_sufixo}.xlsx"
    caminho_final = os.path.join(output_dir, nome_arquivo)
    
    download.save_as(caminho_final)
    callback_log(f"Download concluído: {nome_arquivo}")

def _voltar_para_subscriptions(page, callback_log):
    # Sai clicando em QualiTim e depois em My Subscriptions novamente
    page.click("a.mstrLink >> text='QualiTim'")
    page.wait_for_selector("div.mstr-dskt-nm >> text='My Subscriptions'", state="visible", timeout=60000)
    page.click("div.mstr-dskt-nm >> text='My Subscriptions'")

def executar_fase4(callback_log):
    """Despacho Final de Arquivos (Fase 4)"""
    try:
        callback_log("Iniciando Fase 4: Preparando Envio de E-mail...")
        output_dir = os.path.join(os.getcwd(), "output")
        arquivos = glob.glob(os.path.join(output_dir, "*.xlsx"))
        
        if not arquivos:
            callback_log("Nenhum arquivo encontrado em output/ para enviar.")
            return

        destinatario = os.getenv("DESTINATARIO_EMAIL", "arthur.camargo.dourado@huawei.com")
        
        callback_log(f"Enviando arquivos para {destinatario} via Outlook...")
        
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0) # 0 = olMailItem
        mail.To = destinatario
        mail.Subject = "AUTOMAÇÃO - Arquivos Brutos D-1"
        mail.Body = "Olá,\n\nSegue em anexo os arquivos consolidados de D-1 (4G, 5G e 3G) extraídos via automação.\n\nAtenciosamente,\nBot D-1"
        
        for arq in arquivos:
            mail.Attachments.Add(arq)
            
        mail.Send()
        callback_log("E-mail disparado com sucesso.")
        
        # Limpar os arquivos
        callback_log("Limpando diretório output...")
        for arq in arquivos:
            os.remove(arq)
        callback_log("Fase 4 Concluída: Arquivos despachados e limpos.")

    except Exception as e:
        callback_log(f"Falha na Fase 4: {str(e)}", True)
        raise e
