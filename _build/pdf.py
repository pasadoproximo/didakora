# PDF de cada sesión → pdf/<id>.pdf (diseño A, «tipográfica», elegido por Jorge el 24-11-2026). Lo llama build.py.
# Nombre, minutos, agrupamiento y herramienta de cada paso salen de sesiones.py. El desarrollo, la rúbrica y el dibujo, de sesiones_doc.json.
# Lo imprime Chrome sin ventana (no hace falta Playwright). Sin Chrome se quedan los PDF que hubiera.
import hashlib, html, json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_build"))
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
AUTOR = "Jorge Delgado Aguilera · CC BY-NC-SA 4.0"
FUENTES = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;0,800;1,400;1,500&family=Bricolage+Grotesque:opsz,wght@12..96,400..800&display=swap">'
e = html.escape
CSS = """
@page{size:210mm 297mm;margin:0}
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font:400 12pt/1.4 'Alegreya Sans',sans-serif;color:#061033}
ul,ol{list-style:none}
.pg{position:relative;width:210mm;height:297mm;background:#fff;overflow:hidden;break-after:page}.pg:last-of-type{break-after:auto}
.top{position:absolute;left:20mm;right:20mm;top:15mm;height:7mm;display:flex;justify-content:space-between;align-items:center}
.top img{height:6.6mm;display:block}
.top span{font:600 10.5pt/1 'Bricolage Grotesque',sans-serif;letter-spacing:.09em;text-transform:uppercase}
.pie{position:absolute;left:20mm;right:20mm;bottom:12mm;display:flex;justify-content:space-between;font-size:10.5pt;line-height:1;color:#1B2C6B}
.cu{position:absolute;left:20mm;top:37mm;width:170mm}
h1{font:800 46pt/.98 'Bricolage Grotesque',sans-serif;letter-spacing:-.035em;text-wrap:balance;max-width:168mm}
.pt{font:800 30pt/1 'Bricolage Grotesque',sans-serif;letter-spacing:-.03em;display:flex;justify-content:space-between;align-items:baseline}
.pt small{font:500 12pt/1 'Alegreya Sans',sans-serif;letter-spacing:0;color:#1B2C6B}
.lead{font-size:16pt;line-height:1.34;margin-top:8mm;max-width:156mm;text-wrap:pretty}
.datos{display:grid;grid-template-columns:27mm 45mm 46mm 1fr;column-gap:6mm;margin-top:12mm}
.datos dt{font-size:10.5pt;line-height:1.2;color:#1B2C6B}.datos dd{font:700 13pt/1.25 'Alegreya Sans',sans-serif;margin-top:.8mm}
.sec{display:grid;grid-template-columns:40mm 122mm;column-gap:8mm;border-top:.4mm solid #061033;padding-top:5.5mm;margin-top:11mm}
.p1 .sec{margin-top:12mm}.p1 .sec li+li{margin-top:2.8mm}
.ai .sec{margin-top:13mm;padding-top:6.5mm}.ai .sec p,.ai .sec li{font-size:13.5pt}.ai .sec li+li{margin-top:3.4mm}.ai ul.pt2 li::before{margin-top:2.6mm}.ai ol.nu li::before{font-size:13.5pt}.ai h2{font-size:14pt}
h2{font:700 13pt/1.25 'Bricolage Grotesque',sans-serif;letter-spacing:-.01em}
.sec p,.sec li{font-size:12.5pt;line-height:1.4;text-wrap:pretty}
.sec li+li{margin-top:2.2mm}
ul.pt2 li{display:grid;grid-template-columns:6mm 1fr}ul.pt2 li::before{content:"";width:1.8mm;height:1.8mm;background:#FF8A6B;margin-top:2.25mm}
ol.nu{counter-reset:n}ol.nu li{counter-increment:n;display:grid;grid-template-columns:8mm 1fr}
ol.nu li::before{content:counter(n);font:700 12.5pt/1.4 'Bricolage Grotesque',sans-serif}
.sec .nota{font-weight:700;margin-bottom:3.5mm}
.bar{display:flex;height:4.6mm;gap:.7mm}.bar i{background:#9FB3FF}.bar i.h{background:#FF8A6B}
.tic{position:relative;height:7mm;font:500 10.5pt/1 'Alegreya Sans',sans-serif;color:#1B2C6B}.tic b{position:absolute;top:1.6mm;font-weight:500;white-space:nowrap;transform:translateX(-50%)}.tic b:first-child{transform:none}.tic b:last-child{transform:translateX(-100%)}
.plan{margin-top:3.5mm}.plan li{display:grid;grid-template-columns:7mm 47mm 27mm 1fr 15mm;font-size:12.5pt;line-height:1.3;padding:2.5mm 0;margin:0!important}
.plan li>b:first-child{font-family:'Bricolage Grotesque',sans-serif}.plan li>span:last-child{text-align:right;font-weight:700}
.ley{display:flex;gap:7mm;margin-top:4mm;white-space:nowrap;font-size:10.5pt;color:#1B2C6B}.ley span{display:flex;align-items:center;gap:1.8mm}.ley i{width:3mm;height:3mm;background:#9FB3FF}.ley i.h{background:#FF8A6B}
.act{display:grid;grid-template-columns:40mm 122mm;column-gap:8mm;border-top:.4mm solid #061033;padding-top:7mm;margin-top:13mm}
.pt+.act{margin-top:11mm}
.act .n{font:800 66pt/.74 'Bricolage Grotesque',sans-serif;letter-spacing:-.04em}
.act .m{font:700 15pt/1.2 'Alegreya Sans',sans-serif;margin-top:8mm}
.act .k{font-size:12pt;line-height:1.35;color:#1B2C6B;margin-top:.6mm}
h3{font:800 23pt/1.05 'Bricolage Grotesque',sans-serif;letter-spacing:-.025em;margin-top:-.8mm}
.act ol{margin-top:6mm}.act li{font-size:12.5pt;line-height:1.4;text-wrap:pretty}.act li+li{margin-top:2.4mm}
.di{margin-top:7mm;border-left:1.3mm solid #FF8A6B;padding:.4mm 0 .6mm 5mm}
.di span{display:block;font:600 10.5pt/1 'Bricolage Grotesque',sans-serif;letter-spacing:.09em;text-transform:uppercase}
.di p{font:600 16pt/1.25 'Bricolage Grotesque',sans-serif;letter-spacing:-.015em;margin-top:2.4mm;text-wrap:balance}
.ai .sec{margin-top:9mm!important}.ai .sec li+li{margin-top:2.4mm!important}.dib svg{display:block}
.ru .lead{font-size:13pt;margin-top:4mm;max-width:170mm}
.rt{margin-top:7mm}.rc,.rf{display:grid;grid-template-columns:42mm 1fr 1fr 1fr;column-gap:6mm}
.rc{padding-bottom:2.5mm;border-bottom:.4mm solid #061033}.rc b{font:700 12pt/1.2 'Bricolage Grotesque',sans-serif}
.rf{padding:3.4mm 0;border-bottom:.2mm solid #9FB3FF}.rf h3{font-size:14pt;line-height:1.15;letter-spacing:-.01em;margin:0}.rf div p{font-size:11pt;color:#1B2C6B;margin-top:1mm}.rf>p{font-size:12pt;line-height:1.35;text-wrap:pretty}
.rl{margin-top:8mm}.rl ul{margin-top:3mm}.rl li{display:grid;grid-template-columns:42mm 1fr;column-gap:6mm;font-size:10.5pt;line-height:1.3}.rl li+li{margin-top:1.6mm}.rl>p{font-size:10.5pt;line-height:1.3;color:#1B2C6B;margin-top:3mm}
"""
lis = lambda l: '<ul class="pt2">' + "".join(f"<li>{e(x)}</li>" for x in l) + "</ul>"
ols = lambda l: '<ol class="nu">' + "".join(f"<li>{e(x)}</li>" for x in l) + "</ol>"

CRI = json.load(open(os.path.join(ROOT, "_build", "criterios_boe.json"), encoding="utf-8"))   # texto consolidado del BOE, extraído el 24-11-2026
AREA = {"Área 1. Crecimiento en Armonía": "Armonía", "Área 2. Descubrimiento y Exploración del Entorno": "Entorno", "Área 3. Comunicación y Representación de la Realidad": "Comunicación",
        "Conocimiento del Medio Natural, Social y Cultural": "C. del Medio", "Lengua Castellana y Literatura": "Lengua", "Educación en Valores Cívicos y Éticos": "Valores Cívicos", "Educación Artística": "Ed. Artística", "Tecnología y Digitalización": "Tecnología y Dig."}
RD = {"95": "Real Decreto 95/2022 (Infantil)", "157": "Real Decreto 157/2022 (Primaria)", "217": "Real Decreto 217/2022 (ESO)", "243": "Real Decreto 243/2022 (Bachillerato)"}
def rubrica(q):
    def nom(c): return f'{AREA.get(c[1], c[1])} {c[3]}' if "." in c[3] else f'{AREA.get(c[1], c[1])}, competencia {c[3]}'   # sin número en el BOE: es el único criterio de esa competencia
    cab = "".join(f"<b>{e(n)}</b>" for n in q["niv"])
    filas = "".join(f'<div class="rf"><div><h3>{e(t)}</h3><p>{e(nom(c))}</p></div>' + "".join(f"<p>{e(n)}</p>" for n in ns) + "</div>" for t, c, ns in q["filas"])
    cri = {nom(c): CRI[c[0]][c[1]][c[2]][c[3]] for _, c, _ in q["filas"]}   # si el criterio no existe, el build se para
    li = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in cri.items())
    ley = " y ".join(RD[n] for n in dict.fromkeys(c[0] for _, c, _ in q["filas"]))
    return (f'<p class="pt">Rúbrica</p><p class="lead">{e(q["nota"])}</p><div class="rt"><div class="rc"><b></b>{cab}</div>{filas}</div>'
            f'<div class="rl"><h2>Criterios de evaluación: {e(q["curso"])}</h2><ul>{li}</ul><p>{ley}. Son enseñanzas mínimas: consulta el currículo de tu comunidad. Si cambias el tema o el curso, revisa los criterios.</p></div>')

def documento(x, d, APA, MAT, MET, ETN, nombre, url):
    N = len(x["pasos"]); tot = 3 + (N + 1) // 2 + (1 if d.get('rub') else 0); t = 0; rango = []
    for p in x["pasos"]: rango.append((t, t + p[0])); t += p[0]
    con = lambda p: " y ".join(nombre(h) for h in p[4].split()) or "Sin pantalla"
    def pag(n, cuerpo, cls=""):
        der = f"{AUTOR} · {n} de {tot}" if n in (1, tot) else f"{n} de {tot}"
        return (f'<section class="pg {cls}"><div class="top"><img src="{url}/marca/didakora-logo-a.svg" alt="Didákora"><span>Sesión de aula</span></div><div class="cu">{cuerpo}</div>'
                f'<div class="pie"><span>didakora.es/sesion/{x["id"]}</span><span>{der}</span></div></section>')
    def sec(t, c): return f'<div class="sec"><h2>{t}</h2>{c}</div>'
    def act(i):
        p = x["pasos"][i]; (ins, di) = d["pasos"][i]
        return (f'<div class="act"><div><p class="n">{i + 1}</p><p class="m">{p[0]} minutos</p><p class="k">Del minuto {rango[i][0]} al {rango[i][1]}</p><p class="k">{e(p[1])}</p><p class="k">{e(con(p))}</p></div>'
                f'<div><h3>{e(p[2])}</h3>{ols(ins)}<div class="di"><span>Di a la clase</span><p>«{e(di)}»</p></div></div></div>')
    bar = "".join(f'<i style="flex:{p[0]}"{" class=h" if p[4] else ""}></i>' for p in x["pasos"])
    tic = "".join(f'<b style="left:{100 * m / x["min"]:.2f}%">{m}{" min" if m == x["min"] and x["pasos"][-1][0] / m > .13 else ""}</b>' for m in [0] + [r[1] for r in rango])
    plan = "".join(f'<li><b>{i + 1}</b><b>{e(p[2])}</b><span>{e(p[1])}</span><span>{e(con(p))}</span><span>{p[0]} min</span></li>' for i, p in enumerate(x["pasos"]))
    dat = [("Duración", f'{x["min"]} minutos'), ("Etapa", d.get("etapa") or " · ".join(ETN[k] for k in x["e"])), ("Herramienta", " y ".join(nombre(h) for h in dict.fromkeys(" ".join(p[4] for p in x["pasos"]).split()))),
           ("Dispositivos", {"p": "Tu ordenador y el proyector"}.get(x["d"], APA[x["d"]]))]
    pp = [pag(1, f'<h1>{e(x["t"])}</h1><p class="lead">{e(d["lead"])}</p><dl class="datos">' + "".join(f"<div><dt>{a}</dt><dd>{e(b)}</dd></div>" for a, b in dat) + "</dl>"
              + sec("Qué van a aprender", lis(d["obj"])) + sec("La sesión de un vistazo", f'<div><div class="bar">{bar}</div><div class="tic">{tic}</div><ul class="plan">{plan}</ul><p class="ley"><span><i class="h"></i>Con pantalla</span><span><i></i>Sin pantalla</span></p></div>'), "p1"),
          pag(2, '<p class="pt">Antes de clase</p>' + sec("Qué necesitas", lis(d["mat"])) + sec("Qué preparas", ols(d["prep"])) + f'<div class="sec dib"><h2>{e(d["dib"]["rot"])}</h2><svg viewBox="0 0 122 46" width="122mm" height="46mm" aria-hidden="true">{d["dib"]["svg"]}</svg></div>', "ai")]
    for k in range(0, N, 2):
        ids = list(range(k, min(k + 2, N))); sub = f"Actividad {ids[0] + 1}" if len(ids) == 1 else f"Actividades {ids[0] + 1} y {ids[1] + 1}"
        pp.append(pag(len(pp) + 1, f'<p class="pt">En clase<small>{sub} de {N}</small></p>' + "".join(act(i) for i in ids)))
    if d.get('rub'): pp.append(pag(len(pp) + 1, rubrica(d['rub']), 'ru'))
    pp.append(pag(tot, '<p class="pt">Después de clase</p>' + sec("Qué observar", f'<div><p class="nota">{e(d["bien"])}</p>{lis(d["obs"])}</div>') + sec("Para que llegue a todos", lis(d["div"]))
                  + sec("Si falla el wifi", f'<p>{e(d["wifi"])}</p>') + sec("Para otra clase", f'<p>{e(d["otra"])}</p>'), "ai"))
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(x["t"])} · Didákora</title>{FUENTES}<style>{CSS}</style></head><body>{"".join(pp)}</body></html>'

def imprime(doc, destino):
    exe = next((c for c in CHROME if os.path.exists(c)), None)
    if not exe: return False
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        f = os.path.join(tmp, "s.html"); open(f, "w", encoding="utf-8").write(doc)
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={tmp}\\p", "--allow-file-access-from-files", "--virtual-time-budget=8000", "--no-pdf-header-footer", f"--print-to-pdf={destino}", "file:///" + f.replace("\\", "/")], check=True, capture_output=True, timeout=90)
    return os.path.exists(destino)

def todos(sesiones, APA, MAT, MET, ETN, nombre):
    """pdf/<id>.pdf de cada sesión. Solo vuelve a imprimir las que cambian (pdf/claves.json). Sin Chrome se quedan los que hubiera."""
    DOC = json.load(open(os.path.join(ROOT, "_build", "sesiones_doc.json"), encoding="utf-8"))
    dest = os.path.join(ROOT, "pdf"); os.makedirs(dest, exist_ok=True)
    fc = os.path.join(dest, "claves.json"); claves = json.load(open(fc, encoding="utf-8")) if os.path.exists(fc) else {}
    url = "file:///" + ROOT.replace("\\", "/"); n = 0
    for x in sesiones:
        d = DOC[x["id"]]
        assert len(d["pasos"]) == len(x["pasos"]), f'PDF {x["id"]}: pasos'
        txt = json.dumps({k: v for k, v in d.items() if k != "dib"}, ensure_ascii=False); assert ";" not in txt and ", y " not in txt, f'PDF {x["id"]}: punto y coma o coma antes de «y»'
        k = hashlib.sha1(documento(x, d, APA, MAT, MET, ETN, nombre, "").encode()).hexdigest(); f = os.path.join(dest, x["id"] + ".pdf")
        if claves.get(x["id"]) == k and os.path.exists(f): continue
        if imprime(documento(x, d, APA, MAT, MET, ETN, nombre, url), f): claves[x["id"]] = k; n += 1
    ids = {x["id"] for x in sesiones}
    for f in os.listdir(dest):
        if f.endswith(".pdf") and f[:-4] not in ids: os.remove(os.path.join(dest, f)); claves.pop(f[:-4], None)
    json.dump(claves, open(fc, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return n
