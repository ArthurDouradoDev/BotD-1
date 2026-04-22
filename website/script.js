// Configurações do Repositório
// Sugestão: Preencha com o nome do seu repositório privado
const REPO = "USUARIO/NOME-DO-REPO"; 

async function updateDownloadLink() {
    const downloadBtn = document.getElementById('download-btn');
    const versionTag = document.getElementById('version-tag');
    const repoLink = document.getElementById('repo-link');

    // Link padrão do GitHub que sempre redireciona para o download da última versão
    // Nota: Para repositórios privados, você precisará estar logado no GitHub no navegador.
    const latestDownloadUrl = `https://github.com/${REPO}/releases/latest/download/BotD1.exe`;
    
    downloadBtn.href = latestDownloadUrl;
    repoLink.href = `https://github.com/${REPO}`;

    try {
        // Tentamos buscar a versão para exibir no Badge (isso pode falhar se não houver token/sessão)
        const response = await fetch(`https://api.github.com/repos/${REPO}/releases/latest`);
        if (response.ok) {
            const data = await response.json();
            versionTag.innerText = data.tag_name;
        } else {
            versionTag.innerText = "v1.0.0"; // Fallback
        }
    } catch (e) {
        versionTag.innerText = "v1.0.0";
    }
}

document.addEventListener('DOMContentLoaded', updateDownloadLink);
