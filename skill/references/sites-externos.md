# Inscrição fora do LinkedIn (Gupy, Workday, Kenoby/Solides, SAP SuccessFactors, sites próprios)

Credenciais: `~/.config/robo-vagas/perfis/<perfil>/credenciais.json`. Conta existente → usar. Conta nova → e-mail padrão + senha de `senha`, e **registrar o site** em `credenciais.json` (`{"site": {"email":..., "senha_arquivo":"senha", "criado": "AAAA-MM-DD"}}`).
Códigos de verificação: ler no webmail do e-mail padrão (aba no Chrome). Nunca clicar em links de e-mails que não sejam do próprio site da vaga.

## Gupy (`*.gupy.io`)
- Login único em todas as empresas (conta da candidata). Antes da 1ª inscrição da rodada, conferir o currículo cadastrado na Gupy ("Meu currículo"): formação "Concluído", experiências iguais ao CV-base.
- Etapas comuns: dados pessoais → currículo (anexar o PDF adaptado) → perguntas da empresa → **testes** (lógica, perfil comportamental, inglês, vídeo).
  - Perguntas objetivas (pretensão, disponibilidade, cidade, inglês): responder com `perfil.json`.
  - **Testes de lógica/inglês/comportamental e vídeo: NÃO responder pela candidata.** Parar, marcar `status=inscricao_pendente motivo="teste Gupy"`, e avisar no relatório com o link. Teste é avaliação pessoal.
- "Pré-requisitos eliminatórios" (ex.: "tem CNH?", "mora em X?"): responder só com a verdade; se não souber, deixar pendente.

## Workday (`*.myworkdayjobs.com`)
- Conta é **por empresa**. Senha padrão costuma ser aceita (maiúscula, número, símbolo, 8+).
- "Autofill with resume": usar o PDF adaptado e depois **conferir cada campo** (o parser erra datas e cargos).
- Perguntas de autoidentificação (gênero, raça, PcD, veterano): "prefiro não informar" / "I do not wish to answer", salvo instrução do perfil.

## Regras gerais
- Nunca mentir num formulário. Se a pergunta pede algo que não está no `perfil.json`/CV → pendente + perguntar ao usuário no relatório.
- Captcha que não passa, SMS no celular, vídeo-entrevista → `inscricao_pendente` com motivo.
- Guardar o link externo em `link_externo`.
- Máx. ~15 min por site; travou → pendente e segue para a próxima vaga.
