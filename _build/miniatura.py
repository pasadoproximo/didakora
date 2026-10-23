# Miniaturas de Actualidad: la imagen de cada post, con el estilo de Didákora, en dos tamaños:
#   miniatura.jpg (1200 × 675, 16:9) para las tarjetas de la portada y de /actualidad/
#   portada.jpg   (2100 × 900, 21:9) para la cabecera del post
# Con foto: la recorta y le pone siempre el filtro de la marca (duotono navy y cielo), una forma orgánica coral,
# el aro blanco de la cabecera de la web, un titular corto con la palabra clave subrayada en coral y, si se pide, el logo
# de una herramienta del catálogo. Sin foto: una ilustración con formas orgánicas y un dibujo del tema.
# La compone Edge sin ventana a partir de HTML (las mismas tipografías y colores que la web).
#   python _build/miniatura.py <spec.json>
# spec: { "carpeta": "…/vista/img", "foto": "ruta a la foto descargada" | null, "foco": "50% 40%",
#         "texto": "titular de 2 a 5 palabras", "destaca": "palabra",
#         "icono": "ia|robot|movil|ley|calendario|escudo|libro|aula|megafono|lupa|codigo", "logo": "id del catálogo",
#         "fondo": "cielo|coral|hielo|navy", "semilla": 1 }
# En las tarjetas, la web pone encima el tema (arriba a la izquierda) y la fecha (abajo a la derecha): esas esquinas
# quedan libres.
import json, math, os, random, subprocess, sys, tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EDGE = next((p for p in [os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                         os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")] if os.path.exists(p)), None)
C = {"navy": "#061033", "navy3": "#1B2C6B", "cielo": "#9FB3FF", "coral": "#FF8A6B", "coral2": "#FFE1D8", "hielo": "#DDE4F6", "blanco": "#FFFFFF"}
ICONOS = {  # trazos de 24 × 24, en línea, como los iconos de la web
    "ia": '<path d="M12 3l1.8 4.7 4.7 1.8-4.7 1.8L12 16l-1.8-4.7-4.7-1.8 4.7-1.8z"/><path d="M19 14.5l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/>',
    "robot": '<rect x="5" y="8" width="14" height="11" rx="3"/><circle cx="9.5" cy="13" r="1.2"/><circle cx="14.5" cy="13" r="1.2"/><path d="M12 8V5M10 16.5h4M3 12v3M21 12v3"/><circle cx="12" cy="4" r="1"/>',
    "movil": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "ley": '<path d="M12 3v17M7 21h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
    "calendario": '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4M7.5 14h2M14.5 14h2M7.5 17.5h2"/>',
    "escudo": '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="m9 12 2 2 4-4"/>',
    "libro": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/>',
    "aula": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20l4-4 4 4M7 8h6M7 11h9"/>',
    "megafono": '<path d="M4 10v4h3l7 4V6l-7 4z"/><path d="M18 9a4 4 0 0 1 0 6M7 14l1 5h2"/>',
    "lupa": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.4-4.4"/>',
    "codigo": '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M13.5 6l-3 12"/>',
}
TAMANOS = {"miniatura": (1200, 675), "portada": (2100, 900)}

def mancha(cx, cy, r, semilla, puntas=7, rugosidad=.18):
    """forma orgánica (como una mancha de tinta suave) en SVG: un círculo deformado con curvas suaves"""
    rnd = random.Random(semilla); n = puntas
    pts = [(cx + r * (1 + rnd.uniform(-rugosidad, rugosidad)) * math.cos(2 * math.pi * k / n),
            cy + r * (1 + rnd.uniform(-rugosidad, rugosidad)) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    d = f"M{(pts[0][0] + pts[1][0]) / 2:.1f},{(pts[0][1] + pts[1][1]) / 2:.1f}"
    for k in range(1, n + 1):
        p, q = pts[k % n], pts[(k + 1) % n]
        d += f" Q{p[0]:.1f},{p[1]:.1f} {(p[0] + q[0]) / 2:.1f},{(p[1] + q[1]) / 2:.1f}"
    return d + "Z"

def html(spec, W, H):
    s = int(spec.get("semilla", 1)); u = H / 100  # unidad: 1 % del alto
    foto = spec.get("foto"); trat = "duotono" if foto else None  # Jorge: todas las fotos con el filtro de color de la marca
    fondo = C.get(spec.get("fondo", "cielo"), C["cielo"])
    texto = (spec.get("texto") or "").strip(); dest = (spec.get("destaca") or "").strip()
    if texto and dest and dest in texto:
        texto = texto.replace(dest, f'<span class="d">{dest}</span>', 1)
    oscuro = bool(foto) or spec.get("fondo") == "navy"
    tinta = "#fff" if oscuro else C["navy"]
    # formas orgánicas: una mancha coral grande saliendo por la esquina de arriba a la derecha y el aro blanco de la web
    capas = [f'<path d="{mancha(W * .9, H * .02, H * .52, s)}" fill="{C["coral"]}"/>',
             f'<circle cx="{W * .74:.0f}" cy="{H * 1.02:.0f}" r="{H * .3:.0f}" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="{u * 4.2:.0f}"/>']
    if not foto:  # ilustración: más manchas suaves y el dibujo del tema dentro de una mancha blanca
        capas = [f'<path d="{mancha(W * .12, H * 1.05, H * .55, s + 3, 6)}" fill="{C["hielo"] if spec.get("fondo") != "hielo" else C["blanco"]}" opacity=".9"/>'] + capas
        ix, iy, ir = (W * .7, H * .5, H * .3) if texto else (W * .5, H * .52, H * .32)
        capas += [f'<path d="{mancha(ix, iy, ir, s + 7, 8, .12)}" fill="#fff"/>',
                  f'<g transform="translate({ix - ir * .62:.0f},{iy - ir * .62:.0f}) scale({ir * 1.24 / 24:.3f})" fill="none" stroke="{C["navy"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONOS.get(spec.get("icono", "ia"), ICONOS["ia"])}</g>']
    logo = spec.get("logo"); lg = RAIZ / "logos" / f"{logo}.png" if logo else None
    insignia = (f'<div class="logo"><img src="{lg.as_uri()}" alt=""></div>' if lg and lg.exists() else "")
    if foto:
        trat_css = "linear-gradient(90deg,rgba(6,16,51,.45) 0%,rgba(6,16,51,0) 60%)"  # un poco más oscuro bajo el titular
        base = (f'<img class="f{" duo" if trat == "duotono" else ""}" src="{Path(foto).resolve().as_uri()}" style="object-position:{spec.get("foco", "50% 50%")}">'
                + ('<div class="duo1"></div><div class="duo2"></div>' if trat == "duotono" else "") + f'<div class="velo" style="background:{trat_css}"></div>')
    else:
        base = f'<div class="velo" style="background:{fondo}"></div>'
    fuente = (RAIZ / "_build" / "fuentes" / "BricolageGrotesque.ttf").as_uri()
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:B;src:url("{fuente}");font-weight:200 800}}
*{{margin:0;box-sizing:border-box}} html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{fondo}}}
.lienzo{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
.f{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.duo{{filter:grayscale(1) contrast(1.15) brightness(1.05)}}
.duo1{{position:absolute;inset:0;background:{C["navy"]};mix-blend-mode:lighten}}
.duo2{{position:absolute;inset:0;background:{C["cielo"]};mix-blend-mode:multiply}}
.velo{{position:absolute;inset:0}}
svg{{position:absolute;inset:0}}
.t{{position:absolute;left:{u * 7:.0f}px;bottom:{u * 17:.0f}px;max-width:{W * (.6 if not foto and texto else .62):.0f}px;font:800 {u * (13 if W / H < 2 else 15):.0f}px/1.02 B,sans-serif;letter-spacing:-.03em;color:{tinta}}}
.d{{background:linear-gradient(transparent 62%,{C["coral"]} 62%,{C["coral"]} 92%,transparent 92%);padding:0 .06em}}
.logo{{position:absolute;right:{u * 9:.0f}px;top:{u * 12:.0f}px;width:{u * 22:.0f}px;height:{u * 22:.0f}px;border-radius:{u * 6:.0f}px;background:#fff;display:grid;place-items:center;box-shadow:0 {u:.0f}px {u * 4:.0f}px rgba(6,16,51,.25)}}
.logo img{{width:64%;height:64%;object-fit:contain}}
</style></head><body><div class="lienzo">{base}<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(capas)}</svg>
{f'<div class="t">{texto}</div>' if texto else ""}{insignia}</div></body></html>'''

def main():
    if len(sys.argv) < 2: sys.exit("uso: python _build/miniatura.py <spec.json>")
    if not EDGE: sys.exit("No encuentro Edge")
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    carpeta = Path(spec["carpeta"]).resolve(); carpeta.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="dk-miniatura-"))
    for nombre, (W, H) in TAMANOS.items():
        pagina = tmp / f"{nombre}.html"; pagina.write_text(html(spec, W, H), encoding="utf-8")
        png = tmp / f"{nombre}.png"
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--virtual-time-budget=5000",
                        "--allow-file-access-from-files", f"--user-data-dir={tmp / 'perfil'}", f"--window-size={W},{H}", f"--screenshot={png}", pagina.as_uri()],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90, check=False)
        if not png.exists(): sys.exit(f"{nombre}: sin imagen")
        from PIL import Image
        Image.open(png).convert("RGB").crop((0, 0, W, H)).save(carpeta / f"{nombre}.jpg", quality=86, optimize=True, progressive=True)
        print(nombre, carpeta / f"{nombre}.jpg")

if __name__ == "__main__":
    main()
