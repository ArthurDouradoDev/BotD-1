# BotD-1 | Automação de Relatórios MicroStrategy

O **BotD-1** é um robô de automação inteligente desenvolvido em Python para extrair relatórios diários (D-1) do portal MicroStrategy da TIM, consolidando os dados de 3G, 4G e 5G e automatizando o envio por e-mail.

## 🚀 Status do Projeto

Atualmente, o robô está com as **Fases 1 e 2** concluídas:
- [x] **Fase 1: Autenticação Estratégica**: Login automático via Microsoft com suporte a pausar para aprovação no Authenticator (MFA).
- [x] **Fase 2: Navegação até a Base**: Redirecionamento automático para o servidor QualiTim e acesso à seção "My Subscriptions".
- [ ] **Fase 3: Módulo de Extração**: Coleta dos relatórios 3G/4G/5G (Próximo passo).
- [ ] **Fase 4: Despacho de E-mail**: Envio consolidado via Outlook.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.12+**: Linguagem base.
- **Playwright**: Automação de navegador (Sessão Limpa).
- **CustomTkinter**: Interface gráfica moderna e responsiva.
- **Modular Update System**: Arquitetura de "Hot-Reload" para atualizações ultra-rápidas.
- **PyInstaller**: Geração de executáveis independentes.

---

## 🏗️ Arquitetura de Atualização (Modular)

Para evitar downloads pesados do executável, o BotD-1 utiliza um sistema de carregamento dinâmico:
1. **Core (EXE)**: O executável fixo que contém a interface e o motor básico.
2. **Logic (ZIP)**: Um pacote minúsculo que contém as regras de negócio e automação (`src/`).
3. **Bootstrap**: Ao iniciar, o `main.py` verifica se há um `logic.zip` na pasta `%APPDATA%/BotD1/updates/`. Se o Checksum (SHA-256) for válido, ele carrega a lógica atualizada instantaneamente.

---

## 📦 Manual do Desenvolvedor (Build e Deploy)

### Como rodar em desenvolvimento:
```powershell
python main.py
```

### Como gerar uma nova versão:
O processo é totalmente automatizado via script:

- **Atualização de Rotina (Apenas Lógica):**
  ```powershell
  python build_all.py
  ```
  *Incrementa a `logic_version` e gera o ZIP/EXE na pasta `dist/`.*

- **Lançamento de Grande Versão (App + Lógica):**
  ```powershell
  python build_all.py --major
  ```
  *Incrementa a `app_version` (versão do executável) e a lógica.*

### Como publicar no GitHub:
1. Vá até o repositório no GitHub > **Releases** > **Create new release**.
2. Use uma tag (ex: `v1.0.1`).
3. Faça o upload dos **3 arquivos** gerados na pasta `dist/`:
   - `BotD1.exe`
   - `logic.zip`
   - `version.json`
4. Publique a release. O robô detectará a atualização automaticamente na próxima vez que for aberto.

---

## ⚙️ Configuração (.env)

O robô utiliza variáveis de ambiente para segurança. Crie um arquivo `.env` na raiz ou preencha via interface:
- `MSTR_USER`: Seu e-mail corporativo (T3755000...).
- `MSTR_PASS`: Sua senha.
- `GITHUB_TOKEN`: Token para consulta de atualizações privadas (se necessário).
- `GITHUB_REPO`: `ArthurDouradoDev/BotD-1`.

---

## 🛡️ Resiliência

- **Integridade**: Se um download de atualização falhar ou o arquivo for corrompido, o robô reverte automaticamente para a versão interna estável.
- **Navegação**: Filtros inteligentes por texto e ID garantem que o robô clique no servidor correto mesmo se a posição dos ícones mudar no MicroStrategy.
