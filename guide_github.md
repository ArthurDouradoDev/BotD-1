# Guia de Configuração: GitHub, Releases e Auto-Update

Este documento explica como configurar seu repositório privado para que o sistema de download e o auto-update do Bot D-1 funcionem corretamente.

## 1. Criando o Repositório e o Token (PAT)

Como o repositório é **Privado**, o bot precisa de uma "chave" para checar por atualizações.

1.  Crie seu repositório no GitHub (ex: `seu-usuario/BotD-1`).
2.  Vá em **Settings** (do seu perfil, não do repo) > **Developer Settings** > **Personal Access Tokens** > **Tokens (classic)**.
3.  Clique em **Generate new token (classic)**.
4.  Dê um nome (ex: `Update-BotD1`) e selecione a permissão `repo` (Full control of private repositories).
5.  **Copie o token gerado** e cole no seu arquivo `.env` na chave `GITHUB_TOKEN`.

## 2. Configurando o Repositório no .env

No seu arquivo `.env`, preencha as informações:
```env
GITHUB_TOKEN=ghp_SeuTokenGeradoAqui...
GITHUB_REPO=seu-usuario/BotD1
```

## 3. Como usar o GitHub Releases

O bot só vai atualizar se ele encontrar uma "Release" com uma versão maior que a atual (`1.0.0`).

1.  No seu repositório no GitHub, clique em **Releases** (na barra lateral direita).
2.  Clique em **Create a new release**.
3.  Em **Choose a tag**, digite `v1.1.0` (por exemplo) e clique em *Create new tag*.
4.  No título, coloque `Versão 1.1.0`.
5.  **IMPORTANTE:** Na área de "Attach binaries", arraste o seu arquivo `BotD1.exe` (gerado pelo PyInstaller).
6.  Clique em **Publish release**.

**O que acontece agora?**
Quando o usuário abrir a versão `1.0.0` do bot, ele vai detectar que a `1.1.0` existe no GitHub, perguntar se quer atualizar, baixar o novo `.exe` e se auto-substituir.

## 4. GitHub Pages (Site de Download)

Para o site (`/website`) funcionar:
1.  Vá em **Settings** do repositório > **Pages**.
2.  Em **Build and deployment** > **Branch**, selecione `main` e a pasta `/ (root)` ou crie uma branch separada se preferir.
3.  Se você mantiver o site na pasta `website`, a URL será algo como `https://seu-usuario.github.io/BotD-1/website/`.

> [!NOTE]
> Para baixar o arquivo pelo site em um repositório privado, o usuário precisa estar logado na mesma conta do GitHub no navegador, ou você precisará tornar o repositório público.

## 5. Gerando o Executável

Sempre que fizer mudanças, gere o executável usando:
```bash
pyinstaller "Bot D-1.spec"
```
O arquivo final estará na pasta `dist/BotD1.exe`. É este arquivo que você deve subir no GitHub Releases.
