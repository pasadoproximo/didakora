# PDF de cada sesión, como documento para llevar al aula: datos de sesiones.py y desarrollo de sesiones_doc.py.
# Lo imprime Chrome sin ventana (no hace falta Playwright).
# Lo llama build.py → pdf/<id>.pdf
import hashlib, html, json, os, re, subprocess, sys, tempfile
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
.hero{position:relative;height:92mm;background:#9FB3FF;overflow:hidden;padding:15mm 20mm 0}
.hero::before{content:"";position:absolute;width:84mm;height:84mm;border-radius:50%;background:#FF8A6B;right:-24mm;top:-36mm}
.hero svg{height:8mm;width:auto;position:relative}
h1{position:absolute;left:20mm;bottom:31mm;width:150mm;font-size:34pt;line-height:1;text-wrap:balance}
.da{position:absolute;left:20mm;bottom:11mm;display:flex;gap:11mm}.da span{display:block;font-size:10pt;color:#1B2C6B}.da b{font-size:12pt}
.m{display:grid;grid-template-columns:1fr 1fr;gap:13mm 18mm;padding:15mm 20mm 0;font-size:12pt;line-height:1.35}
h2{font-size:15pt;line-height:1.1;margin-bottom:3.5mm}
.m li{list-style:none;margin-bottom:2mm}.m .ch li{display:flex;gap:3mm}.m .ch li::before{content:"";flex:none;width:4mm;height:4mm;border:.45mm solid #061033;border-radius:1.1mm;margin-top:.6mm}
.tr{position:absolute;left:0;right:0;bottom:0;background:#FFE1D8;padding:11mm 20mm 10mm;display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:10mm;font-size:11.5pt;line-height:1.35}.tr h2{font-size:13pt;margin-bottom:2mm}
.tr .pie{grid-column:1/4;position:static;margin-top:2mm}.pie{display:flex;justify-content:space-between;font-size:9pt;color:#4d4a5c}
.pasos{position:absolute;left:20mm;right:20mm;top:24mm;bottom:72mm;display:flex;flex-direction:column;justify-content:space-between}
.paso{display:grid;grid-template-columns:38mm 1fr;align-items:start}
.min{font-size:44pt;line-height:.82}.min small{font:400 11pt 'Alegreya Sans';letter-spacing:0;color:#5A6480;margin-left:1.5mm}
.di{font-size:20pt;line-height:1.14;text-wrap:balance}.gr{margin-top:3.5mm;font-size:11.5pt;font-weight:700;color:#1B2C6B}.nota{margin-top:3mm;color:#2A3352;font-size:13pt;line-height:1.38;max-width:118mm}
.her{display:flex;align-items:center;gap:2mm;font-weight:700;font-size:11.5pt;margin-top:2mm;color:#061033}.her img{width:5mm;height:5mm}
.fin{position:absolute;left:0;right:0;bottom:0;height:56mm;background:#FFE1D8;padding:13mm 20mm 0}.fin p{font-size:19pt;line-height:1.15;max-width:150mm;text-wrap:balance}.fin .s{font:400 11pt 'Alegreya Sans';letter-spacing:0;color:#5A6480;margin-bottom:2mm}
"""

def documento(x, d, APA, MAT, MET, ETN, nombre, url):
    li = lambda l, c="": f"<ul{c}>" + "".join(f"<li>{e(t)}</li>" for t in l) + "</ul>"
    logo = open(os.path.join(ROOT, "marca", "didakora-logo-a-cielo.svg"), encoding="utf-8").read()
    pasos = "".join(f'<div class="paso"><div class="min d">{p[0]}<small>min</small><p class="gr" style="font-family:Alegreya Sans;letter-spacing:0;line-height:1.2">{e(p[1])}</p></div><div><p class="di d">{e(di)}</p><p class="nota">{e((p[3] + " " + nota).strip())}</p>'
                    + "".join(f'<p class="her"><img src="{url}/logos/{h}.png" alt="">{e(nombre(h))}</p>' for h in p[4].split()) + "</div></div>" for p, (di, nota) in zip(x["pasos"], d["pasos"]))
    pie = f'<span>didakora.es/sesion/{x["id"]}</span><span>Jorge Delgado Aguilera · CC BY-NC-SA 4.0</span>'
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(x["t"])} · Didákora</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,800&display=swap"><style>{CSS}</style></head><body>
<div class="pg"><div class="hero">{logo}<h1>{e(x["t"])}</h1><div class="da"><p><span>Duración</span><b>{x["min"]} minutos</b></p><p><span>Etapa</span><b>{e(" · ".join(ETN[k] for k in x["e"]))}</b></p><p><span>Dispositivos</span><b>{e(APA[x["d"]])}</b></p></div></div>
<div class="m"><div><h2>Qué van a aprender</h2>{li(d["obj"])}</div><div><h2>Qué necesitas</h2>{li(d["mat"])}</div>
<div><h2>Antes de clase</h2>{li(re.split(r"(?<=[.]) (?=[A-ZÁÉÍÓÚ])", x["prep"]), " class='ch'")}</div><div><h2>Para que llegue a todos</h2>{li(d["div"])}</div></div>
<div class="tr"><div><h2>Ten en cuenta</h2><p>{e(d["ojo"])}</p></div><div><h2>Si falla el wifi</h2><p>{e(x["b"])}</p></div><div><h2>Para otra clase</h2><p>{e(x["otra"])}</p></div><div class="pie">{pie}</div></div></div>
<div class="pg"><div class="pasos">{pasos}</div><div class="fin"><p class="s">Ha salido bien si…</p><p class="d">{e(d["bien"])}</p></div></div>
</body></html>"""

def imprime(doc, destino):
    exe = next((c for c in CHROME if os.path.exists(c)), None)
    if not exe: return False
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        f = os.path.join(tmp, "s.html"); open(f, "w", encoding="utf-8").write(doc)
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={tmp}\\p", "--allow-file-access-from-files", "--virtual-time-budget=8000", "--no-pdf-header-footer", f"--print-to-pdf={destino}", "file:///" + f.replace("\\", "/")], check=True, capture_output=True, timeout=90)
    return os.path.exists(destino)

def todos(sesiones, APA, MAT, MET, ETN, nombre):
    """pdf/<id>.pdf de cada sesión. Solo vuelve a imprimir las que cambian (pdf/claves.json). Sin Chrome se quedan los que hubiera."""
    from sesiones_doc import DOC
    dest = os.path.join(ROOT, "pdf"); os.makedirs(dest, exist_ok=True)
    fc = os.path.join(dest, "claves.json"); claves = json.load(open(fc, encoding="utf-8")) if os.path.exists(fc) else {}
    url = "file:///" + ROOT.replace("\\", "/"); n = 0
    for x in sesiones:
        d = DOC[x["id"]]
        assert len(d["pasos"]) == len(x["pasos"]), f'PDF {x["id"]}: pasos'
        txt = json.dumps(d, ensure_ascii=False); assert ";" not in txt and ", y " not in txt, f'PDF {x["id"]}: punto y coma o coma antes de «y»'
        k = hashlib.sha1(documento(x, d, APA, MAT, MET, ETN, nombre, "").encode()).hexdigest(); f = os.path.join(dest, x["id"] + ".pdf")
        if claves.get(x["id"]) == k and os.path.exists(f): continue
        if imprime(documento(x, d, APA, MAT, MET, ETN, nombre, url), f): claves[x["id"]] = k; n += 1
    ids = {x["id"] for x in sesiones}
    for f in os.listdir(dest):
        if f.endswith(".pdf") and f[:-4] not in ids: os.remove(os.path.join(dest, f)); claves.pop(f[:-4], None)
    json.dump(claves, open(fc, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return n
