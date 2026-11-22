#!/usr/bin/env python3
"""Gera o PDF do currículo a partir de um JSON (mesma estrutura do cv_base.json)
e confere se a versão adaptada não inventou nada.

Uso:
  cv.py pdf  CV.json SAIDA.pdf          # HTML -> PDF pelo Chrome headless
  cv.py check BASE.json ADAPTADO.json   # lista palavras novas (para revisar: não pode inventar)
"""
import html, json, os, re, shutil, subprocess, sys, tempfile, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(AQUI, "..", "templates", "cv.html")


def e(s):
    return html.escape(s or "")


def render(cv):
    exp = []
    for x in cv.get("experiencias", []):
        li = "".join(f"<li>{e(b)}</li>" for b in x.get("bullets", []))
        res = f'<p class="res"><b>Resultado:</b> {e(x["resultado"])}</p>' if x.get("resultado") else ""
        exp.append(f'<div class="exp"><p class="cab"><b>{e(x["cargo"])}</b> — {e(x["empresa"])} '
                   f'<i>{e(x.get("periodo"))}</i></p><ul>{li}</ul>{res}</div>')
    form = "".join(f'<p><b>{e(f["curso"])}</b> — {e(f["instituicao"])}'
                   + (f' <i>({e(f["detalhe"])})</i>' if f.get("detalhe") else "") + "</p>"
                   for f in cv.get("formacao", []))
    comp = "".join(f'<li><b>{e(c["grupo"])}:</b> {e(c["itens"])}</li>' for c in cv.get("competencias", []))
    idi = " &nbsp;·&nbsp; ".join(f'<b>{e(i["idioma"])}</b> — {e(i["nivel"])}' for i in cv.get("idiomas", []))
    extras = ""
    for sec in cv.get("secoes_extras", []):  # ex.: Cursos, Certificações (só se existirem de verdade)
        extras += f'<h2>{e(sec["titulo"])}</h2><ul>' + "".join(f"<li>{e(i)}</li>" for i in sec["itens"]) + "</ul>"
    t = open(TEMPLATE, encoding="utf-8").read()
    return (t.replace("{{NOME}}", e(cv["nome"]))
             .replace("{{CONTATO}}", " &nbsp;·&nbsp; ".join(e(c) for c in cv.get("contato", [])))
             .replace("{{LINKEDIN}}", e(cv.get("linkedin", "")))
             .replace("{{TITULO}}", e(cv.get("titulo", "")).replace("|", "&nbsp;|&nbsp;"))
             .replace("{{RESUMO}}", e(cv.get("resumo", "")))
             .replace("{{EXPERIENCIAS}}", "".join(exp))
             .replace("{{FORMACAO}}", form)
             .replace("{{COMPETENCIAS}}", comp)
             .replace("{{IDIOMAS}}", idi)
             .replace("{{EXTRAS}}", extras))


def chrome_cmd():
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        if shutil.which(c):
            return [c]
    if shutil.which("flatpak"):  # Steam Deck / Chrome Flatpak
        return ["flatpak", "run", "--command=/app/extra/chrome", "com.google.Chrome"]
    sys.exit("Chrome/Chromium não encontrado")


def pdf(cv_json, saida):
    cv = json.load(open(cv_json, encoding="utf-8"))
    # Chrome Flatpak só enxerga ~/Downloads e afins: trabalha lá e move depois
    tmpdir = tempfile.mkdtemp(prefix="robo-vagas-", dir=os.path.expanduser("~/Downloads"))
    h, p = os.path.join(tmpdir, "cv.html"), os.path.join(tmpdir, "cv.pdf")
    open(h, "w", encoding="utf-8").write(render(cv))
    subprocess.run(chrome_cmd() + ["--headless=new", "--no-sandbox", "--disable-gpu",
                                   "--no-pdf-header-footer", f"--print-to-pdf={p}", "file://" + h],
                   check=True, capture_output=True, timeout=120)
    os.makedirs(os.path.dirname(os.path.abspath(saida)), exist_ok=True)
    shutil.move(p, saida)
    shutil.rmtree(tmpdir, ignore_errors=True)
    pags = subprocess.run(["pdfinfo", saida], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", pags)
    print(f"OK {saida} ({m.group(1) if m else '?'} página(s))")


def palavras(obj):
    s = json.dumps(obj, ensure_ascii=False).lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return set(re.findall(r"[a-z]{4,}", s))


def check(base, adapt):
    b, a = json.load(open(base, encoding="utf-8")), json.load(open(adapt, encoding="utf-8"))
    novas = sorted(palavras(a) - palavras(b))
    probs = []
    for k in ("nome", "linkedin"):
        if a.get(k) != b.get(k):
            probs.append(f"campo {k} mudou")
    be = [(x["empresa"], x.get("periodo")) for x in b.get("experiencias", [])]
    ae = [(x["empresa"], x.get("periodo")) for x in a.get("experiencias", [])]
    if sorted(be) != sorted(ae):
        probs.append(f"empresas/períodos diferentes do original: {ae}")
    if [(f["curso"], f["instituicao"]) for f in a.get("formacao", [])] != [(f["curso"], f["instituicao"]) for f in b.get("formacao", [])]:
        probs.append("formação diferente do original")
    if {i["idioma"]: i["nivel"] for i in a.get("idiomas", [])} != {i["idioma"]: i["nivel"] for i in b.get("idiomas", [])}:
        probs.append("idiomas/níveis diferentes do original")
    print("PROBLEMAS: " + ("; ".join(probs) if probs else "nenhum"))
    print(f"PALAVRAS NOVAS ({len(novas)}) — cada uma precisa ser sinônimo/termo da vaga para algo que JÁ está no CV:")
    print(", ".join(novas) if novas else "(nenhuma)")
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "pdf":
        pdf(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "check":
        check(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
