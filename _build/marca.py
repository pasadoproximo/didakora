# Genera los logos de Didakora en SVG, con el nombre convertido a trazos (no depende de tener la fuente instalada).
#   marca/didakora-simbolo.svg           la caja abierta sola (favicon y avatar)
#   marca/didakora-logo.svg (+ -blanco)  logotipo horizontal «B2» para la web
#   marca/didakora-apilado.svg (+ -blanco, -cielo) logotipo apilado «C» para redes
# B2: el cuerpo de la caja va de la base a lo alto de la «d»; solo las solapas sobresalen por arriba.
# Uso: python _build/marca.py  (necesita fonttools y uharfbuzz)
import os
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "_build", "fuentes", "BricolageGrotesque.ttf")
OUT = os.path.join(ROOT, "marca")
NAVY, SKY, CORAL, WHITE = "#061033", "#9FB3FF", "#FF8A6B", "#FFFFFF"
VAR = {"wght": 800, "opsz": 48, "wdth": 100}
TRACK = -0.035  # el mismo espaciado que en la web (letter-spacing:-.035em)

blob = hb.Blob.from_file_path(FONT)
face = hb.Face(blob)
font = hb.Font(face)
font.set_variations(VAR)
UPM = face.upem

def word(text):
    """trazos del texto con su espaciado; devuelve (path, ancho, alto de la «d»)"""
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    x, parts = 0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(None)
        font.draw_glyph_with_pen(info.codepoint, pen)
        d = pen.getCommands()
        if d: parts.append(f'<path transform="translate({x + pos.x_offset:.1f} 0)" d="{d}"/>')
        x += pos.x_advance + TRACK * UPM
    x -= TRACK * UPM
    ext = font.get_glyph_extents(font.get_nominal_glyph(ord("d")))
    return "".join(parts), x, ext.y_bearing  # y_bearing = altura de la «d» sobre la base

def overshoot(text):
    """lo que bajan las letras redondas (o, a, d) por debajo de la base: hay que dejarles sitio para que no se corten"""
    low = 0
    for ch in set(text):
        e = font.get_glyph_extents(font.get_nominal_glyph(ord(ch)))
        low = min(low, e.y_bearing + e.height)
    return -low

# la caja abierta en su caja exacta: 42 × 30 (x 3–45, y 13–43); cuerpo de y 21 a 43 (22 de alto)
def box(m, s, c):
    return (f'<path d="M3 13h17l4 8H7z" fill="{s}"/><path d="M45 13H28l-4 8h17z" fill="{c}"/>'
            f'<path d="M8 21h32v17a5 5 0 0 1-5 5H13a5 5 0 0 1-5-5z" fill="{m}"/><rect x="19" y="27" width="10" height="4" rx="2" fill="{s}"/>')

def svg(w, h, inner, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{inner}</svg>\n')

def horizontal(text_color, m, s, c, fit="B2"):
    """B2: el cuerpo de la caja (22) mide lo que la «d»; A: la caja entera, con solapas (30), mide lo que la «d»"""
    paths, tw, asc = word("didakora")
    k = asc / (22 if fit == "B2" else 30)
    bw, bh = 42 * k, 30 * k
    gap = bh * (0.2 if fit == "B2" else 0.22)
    W, H = bw + gap + tw, bh
    base = H                          # base de las letras = base de la caja
    inner = (f'<g transform="translate({-3 * k:.2f} {-13 * k:.2f}) scale({k:.4f})">{box(m, s, c)}</g>'
             f'<g fill="{text_color}" transform="translate({bw + gap:.1f} {base:.1f}) scale(1 -1)">{paths}</g>')
    return svg(W, H + overshoot("didakora"), inner, "Didakora")

def apilado(text_color, m, s, c):
    paths, tw, asc = word("didakora")
    bh = UPM * 1.15; k = bh / 30; bw = 42 * k
    gap = UPM * 0.28
    W = max(bw, tw); H = bh + gap + asc
    inner = (f'<g transform="translate({(W - bw) / 2 - 3 * k:.2f} {-13 * k:.2f}) scale({k:.4f})">{box(m, s, c)}</g>'
             f'<g fill="{text_color}" transform="translate({(W - tw) / 2:.1f} {H:.1f}) scale(1 -1)">{paths}</g>')
    return svg(W, H + overshoot("didakora"), inner, "Didakora")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    files = {
        "didakora-simbolo.svg": svg(42, 30, f'<g transform="translate(-3 -13)">{box(NAVY, SKY, CORAL)}</g>', "Didakora"),
        "didakora-simbolo-blanco.svg": svg(42, 30, f'<g transform="translate(-3 -13)">{box(WHITE, SKY, CORAL)}</g>', "Didakora"),
        "didakora-logo.svg": horizontal(NAVY, NAVY, SKY, CORAL),
        "didakora-logo-blanco.svg": horizontal(WHITE, WHITE, SKY, CORAL),
        "didakora-apilado.svg": apilado(NAVY, NAVY, SKY, CORAL),
        "didakora-apilado-blanco.svg": apilado(WHITE, WHITE, SKY, CORAL),
        # sobre fondo azul cielo la solapa cielo se pierde: va en blanco
        "didakora-apilado-cielo.svg": apilado(NAVY, NAVY, WHITE, CORAL),
        "didakora-logo-cielo.svg": horizontal(NAVY, NAVY, WHITE, CORAL),
        # opción A: la caja entera a la altura de la «d» (más compacta, para la barra del menú)
        "didakora-logo-a.svg": horizontal(NAVY, NAVY, SKY, CORAL, "A"),
        "didakora-logo-a-blanco.svg": horizontal(WHITE, WHITE, SKY, CORAL, "A"),
        # icono de pestaña: la caja centrada en un cuadrado
        "favicon.svg": svg(48, 48, f'<g transform="translate(0 4)">{box(NAVY, SKY, CORAL)}</g>', "Didakora"),
    }
    for n, c in files.items():
        open(os.path.join(OUT, n), "w", encoding="utf-8", newline="\n").write(c)
    print("marca:", ", ".join(files))
