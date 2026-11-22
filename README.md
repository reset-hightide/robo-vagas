# Robô de vagas

Uma skill do [Claude Code](https://claude.com/claude-code) que procura vagas no LinkedIn e faz a parte chata da candidatura, **sem inventar nada no currículo**.

Serve para qualquer pessoa: na primeira vez ele faz um questionário (uma pergunta por vez) e monta o perfil.

## O que ele faz em cada rodada

1. **Radar das vagas frescas.** Procura vagas publicadas **na última hora** (truque da URL do LinkedIn: `f_TPR=r86400` vira `f_TPR=r3600`), na ordem de prioridade que você definir: cargos, áreas, níveis, multinacionais, cidades, híbrido/remoto.
2. **Lê a vaga inteira** e descarta o que não serve (nível, local, presencial demais...).
3. **Adapta o CV** com as palavras-chave que os filtros automáticos (ATS) procuram nessa vaga. Só reescreve o que **já existe** no CV: muda o título, o resumo, a ordem e os termos. Um verificador (`cv.py check`) aponta qualquer palavra nova para revisão.
4. **Faz a inscrição** pela Candidatura simplificada ou em sites externos (Gupy, Workday...). Testes de lógica, inglês, comportamentais e vídeo **nunca** são respondidos pelo robô: ficam pendentes para a pessoa.
5. **Segue a empresa.** As recrutadoras filtram por "engajamento com a marca".
6. **Acha quem publicou a vaga** e manda um convite de conexão.
7. **Escreve uma mensagem personalizada** (85–125 palavras, sem cara de IA) e manda no WhatsApp **"Lembrete"** para você aprovar. Nada é enviado à recrutadora sem o seu "ok".
8. **Melhora o SEO do perfil** do LinkedIn aos poucos (título, sobre, competências, "aberto a oportunidades" só para recrutadores), sempre com informação verdadeira.
9. **Atualiza uma planilha** no OneDrive (vaga, empresa, links, recrutadora, status, follow-up) e guarda cada versão do CV.
10. **Manda um relatório** no WhatsApp no fim.

O método vem de dicas públicas de uma recrutadora com mais de 20 anos de RH: perfil configurado para aparecer na busca, conexão com quem contrata e vagas frescas.

## Instalação (Linux / Steam Deck)

Requisitos: Claude Code com a extensão **Claude in Chrome**, Google Chrome com o LinkedIn da pessoa logado, WhatsApp Web aberto (chat "Lembrete"), `rclone` com um remoto `onedrive:` (opcional) e `poppler-utils` (`pdfinfo`, `pdftoppm`).

```bash
git clone https://github.com/reset-hightide/robo-vagas.git ~/projects/robo-vagas
cd ~/projects/robo-vagas && ./install.sh
```

Isso cria o atalho **Robô de vagas** no Desktop. Dois cliques e ele começa. No Claude Code, também dá para digitar `/robo-vagas`.

## Onde ficam os dados

Tudo o que é pessoal fica **só no seu computador**, em `~/.config/robo-vagas/perfis/<pessoa>/` (pasta com permissão 700): CV, CPF, senhas, base de vagas. Nada disso vai para o GitHub.

| Arquivo | Para quê |
|---|---|
| `cv_base.json` | CV fiel, a fonte da verdade |
| `perfil.json` | dados de formulário (pretensão, CEP...) |
| `preferencias.json` | cargos, cidades, limites, Premium, pasta do OneDrive |
| `mensagem_modelo.md` | seu modelo de mensagem |
| `credenciais.json`, `senha` | contas da Gupy, Workday etc. (chmod 600) |
| `vagas.db` | controle de tudo (SQLite) |
| `cvs/` | um PDF por vaga |

## Limites e cuidados

- Por rodada: até 10 inscrições e 15 convites (dá para mudar). O LinkedIn bloqueia contas com atividade em massa.
- Sem LinkedIn Premium, a mensagem completa só vai depois que a recrutadora aceita o convite. Com Premium, vai por InMail.
- Automação no LinkedIn vai contra os termos de uso da plataforma. Use com moderação e por sua conta e risco.

## Licença

MIT
