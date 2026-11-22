# Perfil privado da pessoa (repositório separado)

O robô é genérico. Os dados de cada pessoa ficam num **repositório git privado** dela, clonado em:

```
~/.config/robo-vagas/perfis/<perfil>/
```

## O que vai no repositório privado
| Arquivo | Conteúdo |
|---|---|
| `perfil.json` | dados de formulário e todas as respostas já dadas (CPF, endereços por região, CNH, salário atual/pretensão, compliance...) |
| `preferencias.json` | cargos, áreas, cidades, exclusões, limites, canal de aprovação, pasta da planilha |
| `cv_base.json` + `cv_original.pdf` | CV fiel (fonte da verdade) |
| `mensagem_modelo.md` | modelo de mensagem da pessoa |
| `credenciais.json` | **só** em quais sites há conta e com qual e-mail/login (sem senhas) |
| `vagas.db` | histórico de vagas, inscrições, contatos e mensagens |
| `cvs/` | CVs adaptados (JSON + PDF) por vaga |

## O que NUNCA vai (está no `.gitignore`)
`senha`, `senhas_locais.json`, `envio/`, `*.xlsx` gerado, `__pycache__/`.
Senhas ficam só no gerenciador de senhas do navegador (ou digitadas pela pessoa na hora).

## Instalar num computador novo
```bash
git clone https://github.com/<usuario>/robo-vagas.git ~/projects/robo-vagas && bash ~/projects/robo-vagas/install.sh
git clone https://github.com/<usuario>/robo-vagas-<pessoa>.git ~/.config/robo-vagas/perfis/<pessoa>
```

## Salvar o progresso
Ao fim de cada rodada, se o perfil for um repositório git: `git add -A && git commit -m "rodada <data>" && git push` (pedir OK da pessoa na primeira vez).
