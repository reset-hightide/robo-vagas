#!/usr/bin/env python3
"""Gera a planilha de controle (.xlsx) a partir do vagas.db e envia ao OneDrive (rclone).

Uso: planilha.py PERFIL [--sem-upload]
Lê destino em preferencias.json: "onedrive_pasta" (ex.: "onedrive:18. Robô de Vagas/Fulana").
Abas: Candidaturas (uma linha por vaga), Follow-ups (o que fazer e quando), Rodadas (log).
CVs adaptados (pasta cvs/) também sobem para <onedrive_pasta>/CVs.
"""
import json, os, sqlite3, subprocess, sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

BASE = os.path.expanduser("~/.config/robo-vagas/perfis")
CAB = [
    ("ID", "id", 5), ("Data", "criado", 16), ("Situação", "_situacao", 60), ("Status", "status", 14), ("Empresa", "empresa", 24),
    ("Multinacional", "multinacional", 12), ("Vaga", "titulo", 34), ("Área", "area", 16), ("Nível", "nivel", 10),
    ("Local", "local", 18), ("Modelo", "modelo", 10), ("Plataforma", "plataforma", 12), ("Link da vaga", "link", 30),
    ("Link externo", "link_externo", 30), ("CV usado", "cv_arquivo", 30), ("Título do CV", "cv_titulo", 30),
    ("Palavras-chave", "palavras_chave", 40), ("Seguiu empresa", "seguiu_empresa", 10),
    ("Recrutador(a)", "recrutador_nome", 22), ("Cargo recrutador", "recrutador_cargo", 22),
    ("Link recrutador", "recrutador_link", 30), ("Convite", "convite_status", 12), ("Mensagem", "msg_status", 14),
    ("Msg enviada em", "msg_enviada_em", 16), ("Gestor/área", "gestor_nome", 22), ("Cargo gestor", "gestor_cargo", 26), ("Link gestor", "gestor_link", 30), ("Convite gestor", "gestor_convite", 12), ("Msg gestor", "gestor_msg_status", 14),
    ("Ajustes no perfil", "perfil_ajustes", 40),
    ("Follow-up em", "follow_up_em", 12), ("Obs.", "obs", 40), ("Texto da mensagem (RH)", "msg_texto", 60), ("Texto da mensagem (gestor)", "gestor_msg_texto", 60),
]


def situacao(r):
    """Frase em português com o pé da vaga (o que já foi feito e o que falta)."""
    s, m, c = r["status"] or "", r["msg_status"] or "", r["convite_status"] or ""
    if s == "descartada":
        return "Descartada: " + (r["motivo"] or "")
    if s == "encontrada":
        return "Selecionada, candidatura ainda não feita"
    if s == "inscricao_pendente":
        return "Candidatura pendente: " + (r["motivo"] or "falta ação no site da empresa")
    partes = ["Candidatura feita" if s == "inscrita" else s.capitalize()]
    if r["seguiu_empresa"] == "sim":
        partes.append("empresa seguida")
    if m == "aguardando_aprovacao":
        partes.append("mensagem aguardando sua aprovação no WhatsApp")
    elif m == "ajustar":
        partes.append("mensagem em ajuste")
    elif m == "aprovada" and c == "enviado":
        partes.append("mensagem aprovada, aguardando a recrutadora aceitar a conexão no LinkedIn para enviar")
    elif m == "aprovada":
        partes.append("mensagem aprovada, pronta para enviar")
    elif m == "enviada":
        partes.append(f"mensagem enviada em {r['msg_enviada_em'] or ''}; aguardando resposta")
    elif c == "enviado":
        partes.append("convite de conexão enviado")
    g = r["gestor_msg_status"] or ""
    if g == "aguardando_aprovacao":
        partes.append("mensagem ao gestor aguardando aprovação")
    elif g == "aprovada":
        partes.append("mensagem ao gestor aprovada, aguardando aceite")
    elif g == "enviada":
        partes.append("mensagem ao gestor enviada")
    if not r["recrutador_nome"] and s == "inscrita":
        partes.append("recrutadora ainda não encontrada")
    return " · ".join(partes)


def link_view(v):
    if v and v.startswith("linkedin:"):
        return "https://www.linkedin.com/jobs/view/" + v.split(":", 1)[1] + "/"
    return v


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    perfil = sys.argv[1]
    d = os.path.join(BASE, perfil)
    pref = json.load(open(os.path.join(d, "preferencias.json"), encoding="utf-8"))
    c = sqlite3.connect(os.path.join(d, "vagas.db")); c.row_factory = sqlite3.Row
    nome = pref.get("nome_curto", perfil)
    wb = Workbook()
    ws = wb.active; ws.title = "Candidaturas"
    ws.append([h for h, _, _ in CAB])
    for r in c.execute("select * from vagas order by id"):
        row = []
        for _, k, _ in CAB:
            v = situacao(r) if k == "_situacao" else (r[k] if k in r.keys() else "")
            if k in ("link",):
                v = link_view(v)
            row.append(v or "")
        ws.append(row)
    for i, (_, _, w) in enumerate(CAB, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="1F3864")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=False)
            if isinstance(cell.value, str) and cell.value.startswith("http"):
                cell.hyperlink = cell.value; cell.font = Font(color="0563C1", underline="single")
    ws.freeze_panes = "F2"
    if ws.max_row > 1:
        t = Table(displayName="Candidaturas", ref=f"A1:{get_column_letter(len(CAB))}{ws.max_row}")
        t.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showRowStripes=True)
        ws.add_table(t)

    f = wb.create_sheet("Follow-ups")
    f.append(["ID", "Empresa", "Vaga", "Recrutador(a)", "Link recrutador", "Status", "Mensagem", "Follow-up em", "Próxima ação"])
    for r in c.execute("select * from vagas where status in ('inscrita','inscricao_pendente','entrevista') order by follow_up_em"):
        if r["status"] == "inscricao_pendente":
            acao = "Concluir inscrição no site externo"
        elif r["msg_status"] in ("aguardando_aprovacao", "ajustar"):
            acao = "Aprovar/ajustar mensagem no Lembrete"
        elif r["msg_status"] == "aprovada":
            acao = "Aguardando aceite do convite para enviar mensagem"
        elif r["msg_status"] == "enviada":
            acao = "Follow-up com a recrutadora se não houver resposta"
        else:
            acao = "Acompanhar"
        f.append([r["id"], r["empresa"], r["titulo"], r["recrutador_nome"], r["recrutador_link"], r["status"],
                  r["msg_status"], r["follow_up_em"], acao])
    for i, w in enumerate([5, 24, 34, 22, 30, 14, 16, 12, 44], 1):
        f.column_dimensions[get_column_letter(i)].width = w
    for cell in f[1]:
        cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="2E5496")

    g = wb.create_sheet("Rodadas")
    g.append(["Quando", "Evento"])
    for e in c.execute("select quando,texto from eventos order by id"):
        g.append([e["quando"], "— início da rodada —" if e["texto"] == "INICIO_RODADA" else e["texto"]])
    g.column_dimensions["A"].width = 17; g.column_dimensions["B"].width = 110

    out = os.path.join(d, f"Candidaturas {nome}.xlsx")
    wb.save(out); print("OK", out)
    if "--sem-upload" not in sys.argv and pref.get("onedrive_pasta"):
        dest = pref["onedrive_pasta"]
        subprocess.run(["rclone", "copyto", out, f"{dest}/Candidaturas {nome}.xlsx"], check=True)
        if os.path.isdir(os.path.join(d, "cvs")):
            subprocess.run(["rclone", "copy", os.path.join(d, "cvs"), f"{dest}/CVs", "--include", "*.pdf"], check=True)
        print("ENVIADO", dest)


if __name__ == "__main__":
    main()
