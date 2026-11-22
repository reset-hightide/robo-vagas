#!/usr/bin/env python3
"""Base de controle do robô de vagas (SQLite em ~/.config/robo-vagas/perfis/<perfil>/vagas.db).

Uso:
  db.py PERFIL add  --link URL --titulo T --empresa E [--set campo=valor ...]   -> imprime ID (ou EXISTE <id>)
  db.py PERFIL set  ID campo=valor [campo=valor ...]
  db.py PERFIL get  ID
  db.py PERFIL list [--status S]
  db.py PERFIL seen URL            -> "sim <id>" / "nao"  (evita repetir vaga)
  db.py PERFIL pend                -> mensagens aguardando aprovação, convites aguardando aceite, follow-ups vencidos
  db.py PERFIL log "texto"         -> registra evento da rodada
  db.py PERFIL rodada              -> resumo da rodada atual (desde a última 'inicio')
  db.py PERFIL inicio              -> marca início de rodada
  db.py PERFIL hoje                -> inscrições e convites feitos hoje (limite diário)
Ao inscrever: set status=inscrita inscrita_em="AAAA-MM-DD HH:MM"; ao convidar: convite_em=...
Campos: ver COLS.
"""
import datetime as dt, json, os, sqlite3, sys

BASE = os.path.expanduser("~/.config/robo-vagas/perfis")
COLS = [
    "criado", "atualizado", "plataforma", "titulo", "empresa", "multinacional", "area", "nivel",
    "local", "modelo", "link", "link_externo", "publicada_ha", "status", "motivo", "inscrita_em",
    "cv_arquivo", "cv_titulo", "palavras_chave",
    "seguiu_empresa", "recrutador_nome", "recrutador_link", "recrutador_cargo", "recrutador_confirmado",
    "convite_status", "convite_em", "msg_texto", "msg_status", "msg_enviada_em",
    "gestor_nome", "gestor_cargo", "gestor_link", "gestor_convite", "gestor_msg_texto", "gestor_msg_status",
    "perfil_ajustes", "follow_up_em", "obs",
]
# status: encontrada | descartada | inscrita | inscricao_pendente (site externo travou) | entrevista | recusada | contratada
# msg_status: rascunho | aguardando_aprovacao | aprovada | enviada | ajustar | cancelada
# convite_status: nao_enviado | enviado | aceito | ja_conexao


def conn(perfil):
    d = os.path.join(BASE, perfil)
    if not os.path.isdir(d):
        sys.exit(f"perfil '{perfil}' não existe em {BASE}")
    c = sqlite3.connect(os.path.join(d, "vagas.db"))
    c.row_factory = sqlite3.Row
    c.execute("create table if not exists vagas (id integer primary key, " + ", ".join(f"{k} text" for k in COLS) + ")")
    have = {r[1] for r in c.execute("pragma table_info(vagas)")}
    for k in COLS:
        if k not in have:
            c.execute(f"alter table vagas add column {k} text")
    c.execute("create table if not exists eventos (id integer primary key, quando text, texto text)")
    return c


def agora():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def norm_link(u):
    u = (u or "").split("?")[0].rstrip("/")
    if "/jobs/view/" in u:  # linkedin: só o id
        u = "linkedin:" + u.split("/jobs/view/")[1].split("/")[0]
    return u


def kv(pares):
    out = {}
    for p in pares:
        k, _, v = p.partition("=")
        if k not in COLS:
            sys.exit(f"campo desconhecido: {k}")
        out[k] = v
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    perfil, cmd, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    c = conn(perfil)
    if cmd == "add":
        d = {}
        i = 0
        sets = []
        while i < len(args):
            if args[i] == "--set":
                sets.append(args[i + 1]); i += 2
            else:
                d[args[i].lstrip("-")] = args[i + 1]; i += 2
        d.update(kv(sets))
        d["link"] = norm_link(d.get("link"))
        r = c.execute("select id from vagas where link=?", (d["link"],)).fetchone()
        if r:
            print("EXISTE", r["id"]); return
        d.setdefault("status", "encontrada")
        d["criado"] = d["atualizado"] = agora()
        ks = list(d)
        cur = c.execute(f"insert into vagas ({','.join(ks)}) values ({','.join('?' * len(ks))})", [d[k] for k in ks])
        c.commit(); print(cur.lastrowid)
    elif cmd == "set":
        d = kv(args[1:]); d["atualizado"] = agora()
        c.execute(f"update vagas set {', '.join(k + '=?' for k in d)} where id=?", [*d.values(), args[0]])
        c.commit(); print("OK")
    elif cmd == "get":
        r = c.execute("select * from vagas where id=?", (args[0],)).fetchone()
        print(json.dumps(dict(r) if r else None, ensure_ascii=False, indent=1))
    elif cmd == "list":
        q, p = "select id,status,empresa,titulo,msg_status,convite_status,follow_up_em from vagas", []
        if args[:1] == ["--status"]:
            q += " where status=?"; p = [args[1]]
        for r in c.execute(q + " order by id", p):
            print(" | ".join(str(x or "") for x in r))
    elif cmd == "seen":
        r = c.execute("select id from vagas where link=?", (norm_link(args[0]),)).fetchone()
        print(f"sim {r['id']}" if r else "nao")
    elif cmd == "pend":
        hoje = dt.date.today().isoformat()
        print("== Mensagens aguardando aprovação no Lembrete:")
        for r in c.execute("select id,empresa,titulo,recrutador_nome from vagas where msg_status='aguardando_aprovacao'"):
            print(f"  #{r['id']} {r['empresa']} — {r['titulo']} — {r['recrutador_nome']}")
        print("== Aprovadas, aguardando a recrutadora aceitar o convite (conferir e enviar):")
        for r in c.execute("select id,empresa,recrutador_nome,recrutador_link from vagas where msg_status='aprovada'"):
            print(f"  #{r['id']} {r['empresa']} — {r['recrutador_nome']} {r['recrutador_link']}")
        print("== Pedidos de ajuste:")
        for r in c.execute("select id,empresa,obs from vagas where msg_status='ajustar'"):
            print(f"  #{r['id']} {r['empresa']} — {r['obs']}")
        print("== Inscrições pendentes (site externo):")
        for r in c.execute("select id,empresa,link_externo,motivo from vagas where status='inscricao_pendente'"):
            print(f"  #{r['id']} {r['empresa']} — {r['link_externo']} — {r['motivo']}")
        print("== Follow-ups vencidos:")
        for r in c.execute("select id,empresa,titulo,follow_up_em from vagas where follow_up_em<>'' and follow_up_em<=? and status='inscrita'", (hoje,)):
            print(f"  #{r['id']} {r['empresa']} — {r['titulo']} (desde {r['follow_up_em']})")
    elif cmd == "hoje":
        h = dt.date.today().isoformat()
        i = c.execute("select count(*) from vagas where inscrita_em like ?", (h + "%",)).fetchone()[0]
        v = c.execute("select count(*) from vagas where convite_em like ?", (h + "%",)).fetchone()[0]
        print(f"inscricoes_hoje={i} convites_hoje={v}")
    elif cmd == "inicio":
        c.execute("insert into eventos (quando,texto) values (?,?)", (agora(), "INICIO_RODADA")); c.commit(); print("OK")
    elif cmd == "log":
        c.execute("insert into eventos (quando,texto) values (?,?)", (agora(), " ".join(args))); c.commit(); print("OK")
    elif cmd == "rodada":
        r = c.execute("select max(quando) q from eventos where texto='INICIO_RODADA'").fetchone()
        desde = r["q"] or "0000"
        for e in c.execute("select quando,texto from eventos where quando>=? and texto<>'INICIO_RODADA' order by id", (desde,)):
            print(e["quando"], e["texto"])
        print("== Vagas mexidas nesta rodada:")
        for v in c.execute("select id,status,empresa,titulo,msg_status from vagas where atualizado>=? order by id", (desde,)):
            print(" | ".join(str(x or "") for x in v))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
