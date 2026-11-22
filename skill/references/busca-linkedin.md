# Busca de vagas no LinkedIn: o "radar das vagas frescas"

Método aprendido com uma recrutadora (20+ anos de RH): candidatar-se **cedo** e **transformar a vaga de anúncio em vaga de busca**, conectando-se com quem publicou.

## URL de busca
```
https://www.linkedin.com/jobs/search/?keywords=<TERMO>&location=<LOCAL>&f_TPR=r3600&f_WT=<MODELO>&f_E=<NIVEL>&sortBy=DD
```
| Parâmetro | Valores |
|---|---|
| `f_TPR` | `r3600` = última hora · `r86400` = 24 h · `r604800` = 7 dias. Truque: o filtro da tela só oferece 24 h; trocar 86400 por 3600 na URL mostra só a última hora. |
| `f_WT` | `1` presencial · `2` remoto · `3` híbrido (vários: `2%2C3`) |
| `f_E` | `1` estágio · `2` assistente/júnior (entry) · `3` pleno-júnior (associate) · `4` sênior |
| `f_AL=true` | só "Candidatura simplificada" (Easy Apply) |
| `sortBy=DD` | mais recentes primeiro |
| `location` | texto ("São Paulo, Brasil", "Sorocaba, São Paulo, Brasil", "Brasil" para remoto) |

## Ordem de varredura em cada rodada (o robô roda de hora em hora)
Começar pela janela mais curta e **ir ampliando só se não encontrar vagas aproveitáveis** (novas, não vistas, dentro do perfil) até preencher a cota da rodada:

| Passo | `f_TPR` | Janela |
|---|---|---|
| 1 | `r3600` | última hora |
| 2 | `r7200` | 2 h |
| 3 | `r10800` | 3 h |
| 4 | `r86400` | 24 h |
| 5 | `r172800` | 48 h |
| 6 | `r259200` | 72 h |
| 7 | `r604800` | 1 semana (só vagas com menos de ~100 candidatos) |

- Em cada passo, varrer todos os termos × locais na ordem de prioridade antes de ampliar.
- Parar de ampliar assim que a cota (`max_inscricoes_por_dia`) estiver cheia.
- Na rodada seguinte, recomeçar do passo 1 (as vagas antigas já vistas ficam na base e são puladas).
- Anotar em `publicada_ha` e no log em que passo a vaga foi achada (ex.: "janela 3 h").

Remoto: `location=Brasil&f_WT=2`. Locais com limite de dias presenciais (ex.: híbrido no máx. 2x/semana) → ler a descrição; se não disser, aceitar e anotar "dias presenciais não informados".

## ⚠️ O filtro de modelo NÃO é confiável
A listagem pública (`jobs-guest/.../seeMoreJobPostings`) aceita `f_TPR` (janela) mas **ignora `f_WT`** (presencial/híbrido/remoto) em boa parte dos resultados (teste 22/11/2026: 7 de 10 "híbridas" eram presenciais). Sempre **abrir a vaga logada** e ler o selo abaixo do título ("Presencial" / "Híbrido" / "Remoto") antes de recomendar; conferir também no site da empresa (ex.: Pandapé mostra "Presential"). Presencial só entra se o usuário abrir exceção (ex.: indicação).

## Ler o card e a vaga
- Extrair por JS da lista: título, empresa, local, "há X minutos", nº de candidatos, selo "Candidatura simplificada", link `/jobs/view/<id>/`.
- Abrir a vaga e ler a descrição inteira ("ver mais"). Guardar: requisitos, atividades, palavras-chave, modelo de trabalho, dias presenciais, nível.
- Bloco **"Conheça a equipe de contratação" / "Meet the hiring team"** no topo da vaga: aí aparece quem publicou. É a recrutadora **confirmada** (`recrutador_confirmado=sim`).
- Se não houver: buscar na página da empresa → Pessoas → "talent acquisition", "recrutadora", "recruiter", "RH" (nesse caso `recrutador_confirmado=nao`: a mensagem NÃO pode dizer que ela conduz o processo).

## Multinacional?
Sinais: página da empresa com "10.001+ funcionários", sede ou presença em vários países, nome global conhecido, vaga pedindo inglês/espanhol, "global", "LATAM", "headquarters". Marcar `multinacional=sim/nao/provavel`. Multinacional sobe na prioridade, mas não é obrigatório.

## Filtros que descartam a vaga
- Tudo que estiver em `excluir` do `preferencias.json` (ex.: escritórios de advocacia: nome com "Advogados"/"Advocacia"/"Sociedade de Advogados" ou setor "Serviços jurídicos" na página da empresa).
- Requisito marcado como **obrigatório** que o CV não comprova (sistema específico, certificação, registro profissional) → descartar e substituir por outra vaga, de preferência em multinacional. "Desejável/diferencial" não descarta.
- Nível acima do perfil (pleno/sênior/coordenador/especialista com 5+ anos) → descartar.
- Local fora da lista ou presencial fora do permitido → descartar.
- Estágio, quando o perfil já é formado (a não ser que as preferências permitam).
- Empresa de "consultoria de RH" sem cliente informado, vagas genéricas de banco de talentos, pirâmide/vendas porta a porta → descartar.
- Mesma vaga já na base (`db.py seen`) → pular.

## Depois de se candidatar (vaga de anúncio → vaga de busca)
1. **Seguir a página da empresa.** A recrutadora usa o filtro "Engajamento com a marca", que só mostra quem segue a empresa.
2. **Convite de conexão** para quem publicou a vaga (ou recrutadora da empresa), logo após a inscrição.
3. Mensagem personalizada (aprovada pelo usuário) assim que o convite for aceito, ou direto se já for conexão.
