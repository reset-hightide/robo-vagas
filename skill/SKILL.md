---
name: robo-vagas
description: Robô de vagas no LinkedIn para qualquer pessoa. Procura vagas frescas (última hora) na ordem de prioridade do perfil, adapta o CV com as palavras-chave da vaga sem inventar nada, faz a inscrição (LinkedIn e sites externos como Gupy/Workday), segue a empresa, conecta com a recrutadora, escreve uma mensagem personalizada sem cara de IA e só envia depois da aprovação no WhatsApp "Lembrete". Também melhora o SEO do perfil, alimenta uma planilha de controle no OneDrive e manda um relatório no fim. Na primeira vez faz um questionário (uma pergunta por vez) para montar o perfil da pessoa. Use quando pedirem "/robo-vagas", "procurar vagas", "rodar o robô de vagas", "candidatar a vagas", "buscar emprego no LinkedIn".
---

# Robô de vagas

Baseado no método de uma recrutadora com 20+ anos de RH: (1) **perfil configurado para aparecer na busca** (recrutamento passivo), (2) **conexão estratégica** (seguir a empresa e falar com quem contrata), (3) **radar das vagas frescas** (vagas da última hora, inscrição imediata e conexão com quem publicou, transformando a "vaga de anúncio" em "vaga de busca").

Pasta da skill: `~/.claude/skills/robo-vagas` (scripts em `scripts/`, guias em `references/`).
Dados pessoais (NUNCA no GitHub): `~/.config/robo-vagas/perfis/<perfil>/`:
`perfil.json` (dados de formulário), `cv_base.json` (CV fiel; fonte da verdade), `cv_original.pdf`, `preferencias.json`, `mensagem_modelo.md`, `credenciais.json` + `senha` (chmod 600), `vagas.db`, `cvs/` (PDFs adaptados).
Python: `PY=~/.venvs/robo-vagas/bin/python` (openpyxl). Scripts sempre com `-I`.

## Frequência
O atalho do Desktop abre o Claude Code com `/loop 1h /robo-vagas`: uma rodada agora e depois **de hora em hora**, enquanto a janela do terminal ficar aberta. Cada rodada começa processando as aprovações do Lembrete. Para rodar uma vez só: `/robo-vagas`. Para parar: fechar a janela (ou pedir "parar o loop").
Se o perfil ainda não existe, a primeira rodada é o questionário; o loop só deve continuar depois dele.

## 0. Início
1. Ler `references/` que for usar (busca-linkedin, perfil-seo, mensagem-recrutador, sites-externos).
2. Perfis em `~/.config/robo-vagas/perfis/`. Nenhum, ou o usuário disse "nova pessoa" → **Questionário (seção 1)**. Mais de um → perguntar qual (uma pergunta).
3. Carregar a skill `claude-in-chrome` e usar o Chrome do usuário (LinkedIn da pessoa logado). Conferir na página `/in/me/` que o perfil logado é o da pessoa certa; se não for, parar e avisar.
4. `$PY -I scripts/db.py <perfil> inicio`.

## 1. Questionário (só na primeira vez, ou para editar)
Texto puro, **uma pergunta por mensagem**, sem popup. Salvar cada resposta na hora.
1. Nome da pessoa e como ela é chamada (para mensagens). Gênero gramatical da mensagem (formado/formada).
2. Onde está o CV (PDF/DOCX). Ler e montar `cv_base.json` **fiel** (mesma estrutura do exemplo em `templates/cv_base.exemplo.json`). Mostrar divergências (ex.: "cursando" × "formada") e perguntar.
3. Cargos e áreas na ordem de prioridade; níveis (assistente, júnior, pleno...); preferir multinacional?
4. Cidades e modelo (presencial/híbrido/remoto; máx. dias presenciais por cidade).
5. Aceita estágio? Aceita presencial?
6. Candidatura só no LinkedIn (Easy Apply) ou também em sites externos (criar contas)? Se externos: e-mail das contas, se o webmail está aberto no Chrome, contas que já existem (Gupy etc.) e senha padrão para contas novas. Gravar em `credenciais.json`/`senha` com chmod 600. Oferecer o comando `read -rs` para o usuário digitar a senha sem ela aparecer no chat.
7. Dados de formulário: pretensão salarial, nascimento, CPF, CEP/endereço, disponibilidade, autoidentificação (padrão "prefiro não informar") → `perfil.json` (chmod 600).
8. LinkedIn Premium? (InMail) → `linkedin_premium`.
9. Modelo de mensagem: usar o do usuário (arquivo) ou o genérico de `references/mensagem-recrutador.md`.
10. Onde aprovar mensagens e receber relatório (padrão WhatsApp "Lembrete") e pasta do OneDrive (padrão `onedrive:18. Robô de Vagas/<Nome>`).
11. Pode ajustar o perfil do LinkedIn (SEO, sem inventar)? Limite de inscrições por rodada (padrão 10).
Gerar `preferencias.json` (ver `templates/preferencias.exemplo.json`), rodar `scripts/cv.py pdf` no `cv_base.json` e mostrar o PDF para conferir.

## 2. Começo da rodada: pendências da rodada anterior
`$PY -I scripts/db.py <perfil> pend` e então:
1. **WhatsApp "Lembrete"**: ler as respostas do usuário às mensagens "🤖 VAGA #N". Formatos aceitos: `N ok`, `ok N`, `N aprovada`, `N não`, `N ajuste: <pedido>`, ou um texto reescrito citando a mensagem (= usar o texto dele). Atualizar `msg_status` (`aprovada`/`cancelada`/`ajustar`) e `msg_texto`. Ajuste → refazer e reenviar para aprovação.
2. **Aprovadas**: abrir o perfil da recrutadora. Se já é conexão (botão "Mensagem") → enviar a mensagem aprovada, anexar/colar o link do CV se pedido, `msg_status=enviada msg_enviada_em=...`. Se o convite ainda está pendente → deixar. Com Premium → InMail.
3. **Inscrições pendentes** em sites externos: tentar de novo só se o motivo era técnico.
4. **Follow-ups vencidos** (`follow_up_dias` após a mensagem sem resposta): rascunhar follow-up curto e mandar para aprovação igual à mensagem.
5. Ler **mensagens recebidas no LinkedIn** (caixa de entrada) de recrutadoras: resumir no relatório. Não responder sozinho, exceto agradecer o aceite do convite.

## 3. Busca (radar das vagas frescas)
Seguir `references/busca-linkedin.md`. Para cada termo de `termos_busca` × cada local de `locais`, na ordem de `cargos_prioridade`: começar em `f_TPR=r3600` (última hora) e, **só se não achar vagas aproveitáveis**, ampliar passo a passo: 2 h → 3 h → 24 h → 48 h → 72 h → 1 semana, parando quando a cota da rodada encher. Extrair a lista por JS, pular `db.py seen`, abrir e **ler a vaga inteira**. Decidir:
- Descartar (nível, local, presencial, estágio, vaga suspeita) → `db.py add ... --set status=descartada --set motivo=...` (evita reabrir).
- Aprovar → `db.py add` com título, empresa, área, nível, local, modelo, multinacional, plataforma (`linkedin`/`gupy`/`workday`/...), `publicada_ha`.
Ordenar as aprovadas: prioridade 1 (multinacional + área prioritária + mais fresca) primeiro. Parar em `max_inscricoes_por_rodada`.

## 4. Para cada vaga aprovada
1. **CV adaptado** (`cvs/AAAA-MM-DD_<Empresa>_<Vaga>.pdf`):
   - Copiar `cv_base.json` → `cvs/<id>.json` e editar SÓ: `titulo` (o nome da vaga ou o cargo-alvo mais próximo, ex.: "Assistente de Contas a Pagar | Contratos"), `resumo` (reescrito com as palavras-chave da vaga que correspondem a fatos reais), ordem e redação dos bullets (trocar por sinônimos de mercado usados na vaga, ex.: "conferência de documentos fiscais" só se o original já disser algo equivalente), ordem/redação das `competencias`.
   - **Proibido**: inventar empresa, cargo, data, ferramenta (SAP, Power BI...), certificação, nível de idioma, resultado, ou transformar estudo em experiência.
   - Rodar `$PY -I scripts/cv.py check <cv_base.json> cvs/<id>.json`. PROBLEMAS ≠ nenhum → corrigir. Revisar cada PALAVRA NOVA: se não for sinônimo/termo para algo que já está no CV, remover.
   - `$PY -I scripts/cv.py pdf cvs/<id>.json cvs/<arquivo>.pdf` → precisa dar **1 página** (2 no máximo, se o original tiver 2). Olhar o PNG (pdftoppm) na primeira vez de cada rodada.
   - Gravar `cv_arquivo`, `cv_titulo`, `palavras_chave` (as usadas).
2. **Inscrição**:
   - Easy Apply: preencher com `perfil.json`; no upload, usar o PDF adaptado (o Chrome Flatpak só enxerga `~/Downloads`: copiar o PDF para lá antes do `file_upload`). Perguntas de formulário: só a verdade; "anos de experiência com X": contar a partir do CV (experiência profissional real; arredondar para baixo); sem dado → pendente.
   - Site externo: `references/sites-externos.md`.
   - Concluiu → `status=inscrita`; travou → `status=inscricao_pendente motivo=...`.
3. **Seguir a empresa** (página da empresa → "Seguir") → `seguiu_empresa=sim`.
4. **Recrutadora**: bloco "Conheça a equipe de contratação" na vaga (confirmado) ou busca de pessoas da empresa com "recrutadora / talent acquisition / recruiter" (não confirmado). Gravar nome, cargo, link, `recrutador_confirmado`. Nenhuma achada → seguir sem mensagem, anotar.
5. **Convite de conexão** para a recrutadora (sempre, mesmo com Premium; respeitar `max_convites_por_rodada`). Sem nota, ou nota curta se houver cota grátis. `convite_status=enviado` (ou `ja_conexao`).
6. **Mensagem**: escrever com `mensagem_modelo.md` + regras de `references/mensagem-recrutador.md`, usando a descrição da vaga e o `cv_base.json`. Contar palavras (85–125). `msg_status=aguardando_aprovacao`, `msg_texto=...`.
7. **Enviar para aprovação no WhatsApp** (chat de `whatsapp_chat`), uma mensagem por vaga:
   ```
   🤖 VAGA #<id> · <Vaga> · <Empresa>
   Recrutadora: <Nome> (<cargo>) <confirmada na vaga | não confirmada>
   Inscrição: <feita no LinkedIn | feita na Gupy | pendente: motivo>
   Vaga: <link>

   <mensagem>

   ➡️ Responda "<id> ok" para aprovar, "<id> ajuste: ..." ou "<id> não".
   ```
   Técnicas do WhatsApp Web: as mesmas da skill `compras-cotacao` (ler o header do `#main` antes de enviar; esperar a sincronização). Quebras de linha: Shift+Enter, ou colar por `ClipboardEvent('paste')` com texto.
8. **SEO do perfil** (se `ajustar_perfil_linkedin`): seguir `references/perfil-seo.md`, 1–2 ajustes pequenos por vaga, só reescrevendo o que é verdadeiro; gravar antes→depois em `perfil_ajustes`. Na 1ª rodada do perfil: checklist completo, inclusive "Aberto a oportunidades" só para recrutadores.
9. `follow_up_em` = hoje + `follow_up_dias`. `db.py log "<resumo da vaga>"`.

## 5. Fim da rodada
1. Esperar até ~10 min por aprovações no Lembrete (checar a cada 2 min); processar as que chegarem (seção 2.1–2.2). As que não chegarem ficam para a próxima rodada.
2. `$PY -I scripts/planilha.py <perfil>` → atualiza `Candidaturas <Nome>.xlsx` (abas Candidaturas, Follow-ups, Rodadas) e sobe planilha + CVs para o OneDrive.
3. **Relatório no Lembrete** (curto):
   ```
   🤖 Robô de vagas · <Nome> · <data hora>
   Vagas vistas: X · inscrições: Y (LinkedIn A, Gupy B...) · pendentes: Z
   Mensagens aguardando sua aprovação: #.. #..
   Enviadas: #.. · convites aceitos: ..
   Perfil: <ajustes feitos>
   Precisa de você: <testes Gupy, perguntas sem resposta, etc.>
   Planilha: OneDrive › 18. Robô de Vagas › <Nome>
   ```
4. Fechar as abas que o robô abriu.

## Regras
- **Nunca mentir** (CV, formulário, mensagem, perfil). Na dúvida → pendente + perguntar no relatório.
- **Nada sai para recrutadora sem aprovação** explícita no Lembrete.
- Nunca responder testes (lógica, inglês, comportamental, vídeo) pela pessoa.
- Limites anti-bloqueio do LinkedIn: ≤ `max_inscricoes_por_rodada` inscrições e ≤ `max_convites_por_rodada` convites por rodada, ~100 convites/semana; pausas de alguns segundos entre ações; se aparecer aviso de "atividade incomum"/captcha, parar a rodada e avisar.
- Nunca citar IA/robô/Claude em nada que a recrutadora veja.
- Sem alerts/confirm do navegador; fechar modais pelo X.
- Credenciais só dos arquivos locais; nunca colar senha em chat, log, planilha ou relatório.
