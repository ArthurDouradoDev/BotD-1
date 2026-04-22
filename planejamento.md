# Planejamento do Projeto: BotD-1

Este documento detalha o planejamento completo para a construção do robô de automação (BotD-1), responsável por extrair relatórios diários (D-1) do portal MicroStrategy da TIM e enviá-los de forma consolidada por e-mail. Este plano baseia-se nas diretrizes de comportamento do fluxo de negócio (`flow.md`) e nas premissas técnicas de extração (`guide.md`).

## 1. Objetivo
Automatizar o processo diário de login com pausas manuais necessárias (Authenticator), realizar a navegação e a extração dos três relatórios operacionais consolidados (3G, 4G, 5G) referentes ao dia anterior (D-1) e encaminhá-los via e-mail interno para a caixa de entrada do próprio usuário.

## 2. Escolha da Pilha Tecnológica (Stack)
- **Linguagem:** Python
- **Automação de Navegador:** `Playwright`. Utiliza a funcionalidade de **Contexto Persistente** (`launch_persistent_context`) salvando o perfil do usuário no `%APPDATA%` do Windows. Isso garante a permanência de cookies e sessões, permitindo que o bot reconheça logins anteriores e pule etapas de MFA (Microsoft Authenticator) em execuções subsequentes.
- **Gestão de Tempo e Datas:** Módulo `datetime` para calcular automaticamente o dia de ontem (D-1) baseando-se na data do sistema host e convertendo para o formato exigido na submissão de formulários (`dd/mm/yyyy`).
- **Automação de E-mail:** `win32com.client` (PyWin32). Interage perfeitamente com a sessão local do portal Microsoft Outlook aberta na máquina sem necessidade de portas de SMTP na rede TIM.
- **Configurações e Segurança:** `python-dotenv` para isolar senhas e login corporativo (`T3755000@...`) de forma não fixada (`hard-coded`) no script da automação.
- **Interface Gráfica (UI):** `customtkinter` para criar uma janela baseada em eventos, exibindo o status atual do robô ao usuário (ex: "Realizando Login...", "Baixando 4G..."). Os ícones do aplicativo (`src/assets/d-1bot.ico` e `d-1bot.png`) serão carregados para configurar a logotipia da janela e da barra de tarefas.

## 3. RoadMap e Escopo das Fases de Desenvolvimento

### Fase 1: Inicialização e Verificação de Login Estratégico
- **Feedback UI:** Iniciar a janela do CustomTkinter, definir o ícone (`src/assets/d-1bot.ico`) e exibir status: *Iniciando Automação e Navegador...*. Por padrão, deve iniciar em tela cheia e o design deve ser no modo escuro.
- Iniciar um contexto persistente no navegador.
- **Navegação Inicial:** Acessar a URL base de redirecionamento (`microstrategyqualidade.internal...`).
- **Verificação de Estado:** O Bot verifica se foi redirecionado para a página de login da Microsoft ou se o Painel MicroStrategy já está visível.
- **Autenticação (Se necessário):** Caso não esteja logado, o Bot digita login e senha injetando-os nos campos da Microsoft.
- **Pausa Estratégica (MFA - Se necessário):** Implementar uma *espera explícita rigorosa* pelo carregamento de um seletor da página "QualiTim", aguardando que o usuário aprove no celular o push do Microsoft Authenticator.

### Fase 2: Navegação até a Base (A Central de Inscrições)
- **Feedback UI:** Atualizar status para: *Login Concluído. Acessando Painel MicroStrategy...*.
- Pós loading da aprovação, o painel do servidor estará liberado (`Project=QualiTim`).
- Redirecionar clicando no servidor pertinente. 
- Encontrar o elemento de classe `mstr-dskt-nm` para apertar o botão central de **"My Subscriptions"**, onde ficam salvas as queries.

### Fase 3: Módulo Downloader Profundo (A Coleta)
Deve implementar a leitura dos elementos na ordem prescrita e conter resiliência técnica por `Expected Conditions` das abas.

- **3.1 Extração do 4G:**
  - **Feedback UI:** Atualizar status para: *Baixando relatório 4G...*.
  - Localizar e apertar link-mãe para o relatório (`D-1 OFENSORES 4G`).
  - Aguardar a saída do loading page para a tabela real em cache.
  - Clicar transversalmente em `Report Home` e acionar o Span `tbExport`.
  - O download ocorrerá em nova aba (interceptar buffer).
  - Clicar de volta em `QualiTim` (botão link) para retornar a raiz.
  - Fechar clicando novamente em `My Subscriptions` para a próxima extração.

- **3.2 Extração do 5G:**
  - **Feedback UI:** Atualizar status para: *Baixando relatório 5G...*.
  - Fluxo perfeitamente análogo: Substitui nome da Busca (`D-1 OFENSORES 5G`), aguarda os links, Exporta aba, volta ao `QualiTim` e retorna ao log das `My Subscriptions`.

- **3.3 Extração e Injeção Diária do 3G:**
  - **Feedback UI:** Atualizar status para: *Processando data e baixando relatório 3G...*.
  - Identificar texto da tabela da Huawei (`Otimização por Célula 3G...`).
  - Acessar o campo transversal de configuração de filtro (Sub-aba menu > `Re-prompt`).
  - **Processamento de Injeção de Data (`D-1`):** Usar lógica matemática `(datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")`.
  - Enviar e sobrescrever texto no input referenciado à linha de configuração (`id_mstr111_txt`).
  - O documento relata exigência de clique duplo em "Run Report". Realizar as devidas esperas dos botões `id_mstr155`.
  - Acessar `Report Home`, e finalmente, `Export` (`tbExport`), extraindo a planilha da aba final.

### Fase 4: O "The Bridge" / Despacho Final de Arquivos (A Ponte)
- **Feedback UI:** Atualizar status para: *Arquivos organizados. Disparando E-mail...*.
- Interceptar e verificar as planilhas baixadas. Para evitar poluição do sistema na pasta `C:\Downloads`, configurar nas `Preferences` do Playwright/Selenium para descer os arquivos em um sub-diretório de output isolado na pasta raiz (`Automações\BotD-1\output\`).
- Levantar os três nomes de arquivos anexáveis (com possível uso de `os` ou `glob` para listagem).
- Iniciar Dispatch via Win32:
  - Subject: `AUTOMAÇÃO - Arquivos Brutos D-1`
  - Body: Corpo dinâmico de aviso indicando sucesso da conclusão.
  - Attachments: Planilhas em excel 4G, 5G e 3G em seu formato original.
  - Para: Caixa de Email do operador do robô pre-definida em variáveis.
- Apagar os arquivos descarregados da pasta local de output para preparar a base e encerrar graciosamente os drives.

## 4. Requisitos Extremos de Tratamento (Resiliência Operacional)
1. Como MicroStrategy tende a reescrever IDs internamente conforma os botões clicam, ancoragem por Textos/Path Parcial/Classes CSS é a prioridade descrita no modelo do `guide.md`.
2. Tolerância a Erros: Uma tratativa Try/Catch generalizada. Se o script crachar na tela de extração 5G, enviar um disparo de Outlook alertando: *Error: Falha na extração de 5G... Log: (sys.exc_info)*.
3. Condições prévias: Rede interna VPN ativada e Autenticador carregado.

## 5. Próximos Passos
O próximo passo seria montar a interface via `customtkinter` utilizando a logotipia (`src/assets/d-1bot`), configurar o carregamento das variáveis sensíveis e definir a inicialização assíncrona/thread do Selenium/Playwright rodando por trás da interface gráfica, pronto para o `main.py` disparar o bot.
