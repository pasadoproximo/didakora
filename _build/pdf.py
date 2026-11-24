# PDF de cada sesión, como documento para llevar al aula: datos de sesiones.py y desarrollo de sesiones_doc.py.
# Lo imprime Chrome sin ventana (no hace falta Playwright).
#   python _build/pdf.py <id> <destino.pdf>
import html, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_build"))
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
e = html.escape

CSS = """
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font:400 13pt/1.4 'Alegreya Sans',sans-serif;color:#061033}
h1,h2,.d{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.025em}
.pg{position:relative;width:210mm;height:297mm;overflow:hidden;break-after:page}.pg:last-child{break-after:auto}
.hero{position:relative;height:150mm;background:#9FB3FF;overflow:hidden;padding:20mm 20mm 0}
.hero::before{content:"";position:absolute;width:118mm;height:118mm;border-radius:50%;background:#FF8A6B;right:-34mm;top:-44mm}
.fin::after{content:"";position:absolute;width:40mm;height:40mm;border-radius:50%;border:6mm solid rgba(255,138,107,.45);right:16mm;bottom:-26mm}
.hero svg{height:8.5mm;width:auto;position:relative}
h1{position:absolute;left:20mm;bottom:19mm;width:130mm;font-size:45pt;line-height:.98}
.m{display:grid;grid-template-columns:1fr 1fr;gap:20mm;padding:24mm 20mm 0}
h2{font-size:17pt;line-height:1.1;margin-bottom:7mm}
.m li{list-style:none;display:flex;gap:4mm;margin-bottom:4.5mm;line-height:1.3}.m li::before{content:"";flex:none;width:4.6mm;height:4.6mm;border:.5mm solid #061033;border-radius:1.3mm;margin-top:.4mm}
.dato{margin-bottom:5mm}.dato b{display:block;font-size:13pt}.dato span{color:#5A6480;font-size:11pt}
.pie{position:absolute;left:20mm;right:20mm;bottom:12mm;display:flex;justify-content:space-between;font-size:9pt;color:#5A6480}
.pasos{position:absolute;left:20mm;right:20mm;top:24mm;bottom:72mm;display:flex;flex-direction:column;justify-content:space-between}
.paso{display:grid;grid-template-columns:38mm 1fr;align-items:start}
.min{font-size:44pt;line-height:.82}.min small{font:400 11pt 'Alegreya Sans';letter-spacing:0;color:#5A6480;margin-left:1.5mm}
.di{font-size:20pt;line-height:1.14;text-wrap:balance}.gr{margin-top:3.5mm;font-size:11.5pt;font-weight:700;color:#1B2C6B}.nota{margin-top:3mm;color:#2A3352;font-size:13pt;line-height:1.38;max-width:118mm}
.her{display:flex;align-items:center;gap:2mm;font-weight:700;font-size:11.5pt;margin-top:2mm;color:#061033}.her img{width:5mm;height:5mm}
.fin{position:absolute;left:0;right:0;bottom:0;height:56mm;background:#FFE1D8;padding:13mm 20mm 0}.fin p{font-size:19pt;line-height:1.15;max-width:150mm;text-wrap:balance}.fin .s{font:400 11pt 'Alegreya Sans';letter-spacing:0;color:#5A6480;margin-bottom:2mm}
"""

def documento(x, d, APA, MAT, MET, ETN, nombre, url):
    logo = open(os.path.join(ROOT, "marca", "didakora-logo-a-cielo.svg"), encoding="utf-8").read()
    pasos = "".join(f'<div class="paso"><div class="min d">{p[0]}<small>min</small><p class="gr" style="font-family:Alegreya Sans;letter-spacing:0;line-height:1.2">{e(p[1])}</p></div><div><p class="di d">{e(di)}</p><p class="nota">{e(nota)}</p>'
                    + "".join(f'<p class="her"><img src="{url}/logos/{h}.png" alt="">{e(nombre(h))}</p>' for h in p[4].split()) + "</div></div>" for p, (di, nota) in zip(x["pasos"], d["pasos"]))
    pie = f'<span>didakora.es/sesion/{x["id"]}</span><span>Jorge Delgado Aguilera · CC BY-NC-SA 4.0</span>'
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(x["t"])} · Didákora</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,800&display=swap"><style>{CSS}</style></head><body>
<div class="pg"><div class="hero">{logo}<h1>{e(x["t"])}</h1></div>
<div class="m"><div><h2>Antes de clase</h2><ul>{"".join(f"<li>{e(t)}</li>" for t in d["antes"])}</ul></div>
<div><p class="dato"><span>Duración</span><b>{x["min"]} minutos</b></p><p class="dato"><span>Para</span><b>{e(" · ".join(ETN[k] for k in x["e"]))}</b></p><p class="dato"><span>Dispositivos</span><b>{e(APA[x["d"]])}</b></p><p class="dato"><span>Si falla el wifi</span><b>{e(x["b"])}</b></p></div></div>
<div class="pie">{pie}</div></div>
<div class="pg"><div class="pasos">{pasos}</div><div class="fin"><p class="s">Ha salido bien si…</p><p class="d">{e(d["bien"])}</p></div></div>
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
