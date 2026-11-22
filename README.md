# Robô de vagas

Uma skill do [Claude Code](https://claude.com/claude-code) que procura vagas no LinkedIn e faz a parte chata da candidatura, **sem inventar nada no currículo**.

Serve para qualquer pessoa, e **quem usa é a própria pessoa candidata, conversando com o robô no Claude Code**: ele faz o trabalho no Chrome e, quando precisa de algo (aprovar uma mensagem, digitar o CPF ou a senha num site, responder uma pergunta de formulário), pergunta na tela, uma coisa por vez. Cada resposta fica guardada para os próximos formulários.

## O que ele faz em cada rodada

0. **Lê o e-mail da pessoa** atrás de retornos das empresas e faz **follow-ups educados** no LinkedIn (5 e 12 dias úteis) antes de procurar vagas novas.

1. **Radar das vagas frescas.** Roda de hora em hora procurando vagas publicadas **na última hora** (truque da URL do LinkedIn: `f_TPR=r86400` vira `f_TPR=r3600`). Se não achar nada, amplia aos poucos: 2 h, 3 h, 24 h, 48 h, 72 h, 1 semana. Segue a ordem de prioridade que você definir: cargos, áreas, níveis, multinacionais, cidades, híbrido/remoto.
2. **Lê a vaga inteira** e descarta o que não serve (nível, local, presencial demais...).
3. **Adapta o CV** com as palavras-chave que os filtros automáticos (ATS) procuram nessa vaga. Só reescreve o que **já existe** no CV: muda o título, o resumo, a ordem e os termos. Um verificador (`cv.py check`) aponta qualquer palavra nova para revisão.
4. **Faz a inscrição** pela Candidatura simplificada ou em sites externos (Gupy, Workday...). Testes de lógica, inglês, comportamentais e vídeo **nunca** são respondidos pelo robô: ficam pendentes para a pessoa.
5. **Segue a empresa.** As recrutadoras filtram por "engajamento com a marca".
6. **Conecta com o RH** (de preferência quem publicou a vaga) **e com o gestor da área**.
7. **Escreve mensagens personalizadas** (85–125 palavras, sem cara de IA) para o RH e para o gestor e mostra para a pessoa aprovar. Nada é enviado sem o "sim" dela.
8. **Melhora o SEO do perfil** do LinkedIn aos poucos (título, sobre, competências, "aberto a oportunidades" só para recrutadores), sempre com informação verdadeira.
9. **Atualiza uma planilha** no OneDrive (vaga, empresa, links, recrutadora, status, follow-up) e guarda cada versão do CV.
10. **Manda um relatório** no WhatsApp no fim.

O método vem de dicas públicas de uma recrutadora com mais de 20 anos de RH: perfil configurado para aparecer na busca, conexão com quem contrata e vagas frescas.

## Instalação (Linux / Steam Deck)

Requisitos: Claude Code com a extensão **Claude in Chrome**, Google Chrome com o LinkedIn da pessoa logado, WhatsApp Web aberto (chat "Lembrete"), `rclone` com um remoto `onedrive:` (opcional) e `poppler-utils` (`pdfinfo`, `pdftoppm`).

```bash
git clone https://github.com/reset-hightide/robo-vagas.git ~/projects/robo-vagas
cd ~/projects/robo-vagas && bash install.sh
```

Isso cria o atalho **Robô de vagas** no Desktop. Dois cliques e ele roda uma vez na hora e depois **de hora em hora**, enquanto a janela ficar aberta. Para uma rodada só: `robo-vagas uma-vez` no terminal, ou `/robo-vagas` dentro do Claude Code.

## Dados pessoais: repositório privado

O perfil de cada pessoa fica num **repositório privado separado** (veja `skill/references/perfil-privado.md`), clonado em `~/.config/robo-vagas/perfis/<pessoa>/`. Senhas nunca vão para nenhum repositório.

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

- Por dia: até 10 inscrições (as 10 melhores vagas) e 10 convites, com pausas entre as ações, para o LinkedIn não tratar a conta como automação. Dá para mudar.
- Sem LinkedIn Premium, a mensagem completa só vai depois que a recrutadora aceita o convite. Com Premium, vai por InMail.
- Automação no LinkedIn vai contra os termos de uso da plataforma. Use com moderação e por sua conta e risco.

## Licença

MIT
