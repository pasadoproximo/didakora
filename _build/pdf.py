# PDF de cada sesión, como documento para llevar al aula: datos de sesiones.py y desarrollo de sesiones_doc.py.
# Lo imprime Chrome sin ventana (no hace falta Playwright).
#   python _build/pdf.py <id> <destino.pdf>
import html, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_build"))
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
e = html.escape

CSS = """
@page{size:A4;margin:14mm 17mm 17mm;@bottom-left{content:"didakora.es";font:700 8.5pt 'Alegreya Sans';color:#5A6480}@bottom-center{content:"Jorge Delgado Aguilera · CC BY-NC-SA 4.0";font:400 8.5pt 'Alegreya Sans';color:#5A6480}@bottom-right{content:counter(page) " / " counter(pages);font:700 8.5pt 'Alegreya Sans';color:#5A6480}}
*{box-sizing:border-box;margin:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font:400 10.3pt/1.38 'Alegreya Sans',sans-serif;color:#2A3352}
h1,h2,h3,.n{font-family:'Bricolage Grotesque',sans-serif;color:#061033}
.c{display:flex;justify-content:space-between;align-items:center;padding-bottom:4mm;border-bottom:1.6pt solid #061033}
.c svg,.c img{height:7mm;width:auto}.c span{font-weight:700;font-size:9pt;color:#5A6480}
h1{font-weight:800;font-size:25pt;line-height:1.04;letter-spacing:-.025em;margin-top:6mm;max-width:150mm}
.r{font-size:13pt;line-height:1.35;margin-top:2mm;color:#1B2C6B}
.f{display:grid;grid-template-columns:auto auto auto 1fr;margin:5mm 0 1mm;border-top:.6pt solid #C9D0E2;border-bottom:.6pt solid #C9D0E2}
.f div{padding:2.6mm 6mm 2.6mm 0}.f div+div{padding-left:6mm;border-left:.6pt solid #C9D0E2}.f dt{font-size:8.5pt;color:#5A6480}.f dd{font-weight:700;color:#061033}
section{display:grid;grid-template-columns:32mm 1fr;gap:6mm;padding-top:4mm;margin-top:4mm;border-top:.6pt solid #C9D0E2;break-inside:avoid}
section.l{display:block;break-inside:auto}
h2{font-weight:800;font-size:12pt;line-height:1.15;letter-spacing:-.01em}
ul,ol{padding-left:4.5mm}li{padding-left:1mm;margin-bottom:.9mm}li::marker{color:#E0603F;font-weight:700}
.dos{columns:2;column-gap:8mm}
table{border-collapse:collapse;width:100%;margin-top:3mm}th{text-align:left;font-weight:700;font-size:9pt;color:#1B2C6B;padding:0 4mm 1.6mm 0;border-bottom:1.2pt solid #061033}
td{vertical-align:top;padding:3mm 4mm 3mm 0;border-bottom:.6pt solid #C9D0E2}tr{break-inside:avoid}thead{display:table-header-group}
td:last-child,th:last-child{padding-right:0}
.n{font-weight:800;font-size:17pt;line-height:1;white-space:nowrap}.n small{display:block;font:400 8.5pt 'Alegreya Sans';color:#5A6480;margin-top:1mm}
.p h3{font-weight:800;font-size:11.5pt;line-height:1.15}.p td>p+p{margin-top:1mm}
.g{font-size:9pt;color:#5A6480;margin-top:.8mm}.h{display:flex;align-items:center;gap:1.6mm;font-weight:700;font-size:9.5pt;color:#061033;margin-top:1.8mm}.h img{width:4.4mm;height:4.4mm;border-radius:1mm}
tr.k td{padding-top:0}tr.q td{border-bottom:0;padding-bottom:1.8mm}.k i{display:block;font-style:normal;background:#FFE1D8;border-radius:1.6mm;padding:1.6mm 3mm;font-size:9.6pt;color:#061033}
.o b{color:#061033}.o p+p{margin-top:1.4mm}
section.l+section{border-top:0;margin-top:2mm}table{table-layout:fixed}tbody:last-child tr:last-child td{border-bottom:.6pt solid #C9D0E2}.o p:first-of-type{margin-top:3mm}
"""

def documento(x, d, APA, MAT, MET, ETN, nombre, url):
    li = lambda l, c="": f'<ul{c}>' + "".join(f"<li>{e(t)}</li>" for t in l) + "</ul>"
    logo = open(os.path.join(ROOT, "marca", "didakora-logo-a.svg"), encoding="utf-8").read()
    t = 0; filas = ""
    for (m, g, tit, _, hs), (tu, ellos, con) in zip(x["pasos"], d["pasos"]):
        her = "".join(f'<p class="h"><img src="{url}/logos/{h}.png" alt="">{e(nombre(h))}</p>' for h in hs.split())
        filas += (f'<tbody class="p" style="break-inside:avoid"><tr class="{"q" if con else ""}"><td class="n">{m}′<small>{t} a {t + m}</small></td><td><h3>{e(tit)}</h3><p class="g">{e(g)}</p>{her}</td><td>{e(tu)}</td><td>{e(ellos)}</td></tr>'
                  + (f'<tr class="k"><td></td><td colspan="3"><i>{e(con)}</i></td></tr>' if con else "") + "</tbody>"); t += m
    ev = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in d["evi"])
    mat = " · ".join(MAT[s] for s in x["s"] if s != "*") or "Cualquier materia"
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(x["t"])} · Didákora</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&display=swap"><style>{CSS}</style></head><body>
<div class="c">{logo}<span>Sesión de aula</span></div>
<h1>{e(x["t"])}</h1><p class="r">{e(x["r"])}</p>
<dl class="f"><div><dt>Duración</dt><dd>{x["min"]} minutos</dd></div><div><dt>Etapa</dt><dd>{e(" · ".join(ETN[k] for k in x["e"]))}</dd></div><div><dt>Materia</dt><dd>{e(mat)}</dd></div><div><dt>Dispositivos</dt><dd>{e(APA[x["d"]])}</dd></div></dl>
<section style="border:0;margin-top:0"><h2>Qué van a aprender</h2>{li(d["obj"])}</section>
<section><h2>Qué necesitas</h2>{li(d["mat"], ' class="dos"')}</section>
<section><h2>Antes de la clase</h2>{li(d["antes"]).replace("<ul>", "<ol>").replace("</ul>", "</ol>")}</section>
<section class="l"><h2>Desarrollo</h2><table><colgroup><col style="width:16mm"><col style="width:37mm"><col><col></colgroup><thead><tr><th>Tiempo</th><th>Momento</th><th>Qué haces tú</th><th>Qué hace el alumnado</th></tr></thead>{filas}</table></section>
<section><h2>Preguntas para guiar</h2>{li(d["preg"])}</section>
<section class="l" style="break-inside:avoid"><h2>Cómo saber si ha funcionado</h2><table><colgroup><col style="width:30mm"><col><col></colgroup><thead><tr><th>Qué miras</th><th>Lo ha conseguido si…</th><th>Si le cuesta</th></tr></thead>{ev}</table></section>
<section><h2>Para que llegue a todos</h2>{li(d["div"])}</section>
<section><h2>Ten en cuenta</h2><div class="o">{li(d["ojo"])}<p><b>Si falla el wifi.</b> {e(x["b"])}</p><p><b>Para otra clase.</b> {e(x["otra"])}</p></div></section>
</body></html>"""

def imprime(doc, destino):
    exe = next((c for c in CHROME if os.path.exists(c)), None)
    if not exe: return False
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        f = os.path.join(tmp, "s.html"); open(f, "w", encoding="utf-8").write(doc)
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={tmp}\\p", "--allow-file-access-from-files", "--virtual-time-budget=8000", "--no-pdf-header-footer", f"--print-to-pdf={destino}", "file:///" + f.replace("\\", "/")], check=True, capture_output=True, timeout=90)
    return os.path.exists(destino)

if __name__ == "__main__":
    from sesiones import SESIONES, METAS, MATERIAS, APARATOS
    from sesiones_doc import DOC
    import re
    T = open(os.path.join(ROOT, "tools.js"), encoding="utf-8").read()
    nombre = lambda h: re.search(r'id:"%s".*?\bn:"([^"]+)"' % h, T, re.S).group(1)
    ETN = {"I": "Infantil", "P": "Primaria", "S": "Secundaria y Bachillerato"}
    x = next(s for s in SESIONES if s["id"] == sys.argv[1]); d = DOC[x["id"]]
    assert len(d["pasos"]) == len(x["pasos"])
    print(imprime(documento(x, d, dict(APARATOS), dict(MATERIAS), dict(METAS), ETN, nombre, "file:///" + ROOT.replace("\\", "/")), os.path.abspath(sys.argv[2])))
