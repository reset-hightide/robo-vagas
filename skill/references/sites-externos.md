# Inscrição fora do LinkedIn (Gupy, Workday, Kenoby/Solides, SAP SuccessFactors, sites próprios)

Credenciais: `~/.config/robo-vagas/perfis/<perfil>/credenciais.json`. **O robô não digita senha nem CPF**: preenche o e-mail e para; o usuário digita a senha (ou aceita a sugerida pelo Chrome) e o CPF. Conta nova → **registrar o site** em `credenciais.json` (`{"site": {"email":..., "senha_arquivo":"senha", "criado": "AAAA-MM-DD"}}`).
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
- **Campo de pretensão/salário numérico**: digitar só números ("3000"). "R$ 3.000,00" vira 300000! Conferir na tela Review antes de enviar.
- Workday: "Sign in with LinkedIn" funciona sem senha (pedir OK do usuário uma vez). Cada empresa tem um Workday próprio.
- SuccessFactors: pede datas de início/fim de cada formação (ter no `cv_base.json`), data de nascimento e bairro; a IA do site sugere habilidades — remover as que não estão no CV.
- Nunca preencher campo por "rótulo começa com": "Endereço" casa com "Endereço de e-mail". Usar rótulo exato.
- Nunca mentir num formulário. Se a pergunta pede algo que não está no `perfil.json`/CV → pendente + perguntar ao usuário no relatório.
- Captcha que não passa, SMS no celular, vídeo-entrevista → `inscricao_pendente` com motivo.
- Guardar o link externo em `link_externo`.
- Máx. ~15 min por site; travou → pendente e segue para a próxima vaga.
