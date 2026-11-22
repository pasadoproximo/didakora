# Imagen para compartir (1200 × 630) de cada ficha: og/<id>.png. Es la que sale al pegar el enlace de una ficha en
# WhatsApp, LinkedIn o X: el nombre de la herramienta, su logo y su categoría con la marca de Didákora
# (fondo cielo, círculo coral y aro blanco, como marca/og.png, de donde se recorta el logotipo).
# La llama build.py (necesita Pillow; sin Pillow el build sigue y deja las imágenes que ya hubiera).
# Solo vuelve a pintar una imagen si cambia su nombre, su categoría o su logo (og/claves.json guarda con qué se hizo).
#   python _build/og.py            → pinta las que falten o hayan cambiado (lo mismo que hace el build)
#   python _build/og.py --todas    → las pinta todas otra vez (si se cambia este diseño)
import hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTE = os.path.join(ROOT, "_build", "fuentes", "BricolageGrotesque.ttf")
CIELO, CORAL, NAVY, NAVY3, BLANCO = (159, 179, 255), (255, 138, 107), (6, 16, 51), (27, 44, 107), (255, 255, 255)
W, HH, MX = 1200, 630, 80   # ancho, alto y margen izquierdo
DISENO = "1"                # súbelo si cambia el dibujo: obliga a pintarlas todas


def _fuente(px, peso):
    from PIL import ImageFont
    f = ImageFont.truetype(FUENTE, px)
    f.set_variation_by_axes([min(96, max(12, px)), peso, 100])  # tamaño óptico, peso y ancho
    return f


def _lineas(d, texto, fuente, ancho):
    out, cur = [], ""
    for w in texto.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fuente) <= ancho or not cur: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def pinta(nombre, categoria, logo, destino):
    from PIL import Image, ImageDraw
    S = 2  # se dibuja al doble y se reduce: bordes suaves
    im = Image.new("RGB", (W * S, HH * S), CIELO); d = ImageDraw.Draw(im)
    d.ellipse([900 * S, -330 * S, 1500 * S, 270 * S], fill=CORAL)                              # círculo coral
    d.ellipse([636 * S, 466 * S, 940 * S, 770 * S], outline=(214, 222, 255), width=32 * S)     # aro
    im = im.resize((W, HH), Image.LANCZOS); d = ImageDraw.Draw(im)
    # logotipo de Didákora, recortado de marca/og.png (mismo fondo cielo)
    marca = Image.open(os.path.join(ROOT, "marca", "og.png")).convert("RGB").crop((78, 196, 636, 302))
    marca = marca.resize((round(marca.width * .5), round(marca.height * .5)), Image.LANCZOS)
    im.paste(marca, (MX - 1, 64))
    # nombre: lo más grande que quepa en dos líneas
    ancho = 800
    for px in (112, 100, 90, 80, 70, 62, 54):
        f = _fuente(px, 800); ls = _lineas(d, nombre, f, ancho)
        if len(ls) <= 2 and all(d.textlength(l, font=f) <= ancho for l in ls): break
    alto = round(px * 1.04)
    y = 318 - (alto * len(ls)) // 2
    # logo de la herramienta en una ficha blanca, a la izquierda del nombre
    x = MX
    if logo and os.path.exists(logo):
        lado = 132; yy = 318 - lado // 2 - 6
        d.rounded_rectangle([MX, yy, MX + lado, yy + lado], radius=30, fill=BLANCO)
        lg = Image.open(logo).convert("RGBA"); lg = lg.resize((88, 88), Image.LANCZOS)
        im.paste(lg, (MX + 22, yy + 22), lg)
        x = MX + lado + 36
        ls = _lineas(d, nombre, f, ancho - lado - 36)
        while (len(ls) > 2 or any(d.textlength(l, font=f) > ancho - lado - 36 for l in ls)) and px > 46:
            px -= 6; f = _fuente(px, 800); ls = _lineas(d, nombre, f, ancho - lado - 36)
        alto = round(px * 1.04); y = 318 - (alto * len(ls)) // 2
    for i, l in enumerate(ls): d.text((x, y + i * alto - px * .12), l, font=f, fill=NAVY)
    # debajo: para qué es la página y la categoría, sobre una raya coral
    d.rounded_rectangle([MX, 452, MX + 72, 460], radius=4, fill=CORAL)
    d.text((MX, 478), "Qué es y para qué sirve en clase", font=_fuente(38, 500), fill=NAVY)
    d.text((MX, 532), categoria.upper(), font=_fuente(22, 700), fill=NAVY3)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    im.save(destino, optimize=True)


def genera(fichas, todas=False):
    """fichas: [(id, nombre, categoría)]. Devuelve cuántas ha pintado, o None si no hay Pillow."""
    try: import PIL  # noqa: F401
    except ImportError: return None
    carpeta = os.path.join(ROOT, "og"); rc = os.path.join(carpeta, "claves.json")
    claves = json.load(open(rc, encoding="utf-8")) if os.path.exists(rc) else {}
    n = 0
    for fid, nombre, cat in fichas:
        logo = os.path.join(ROOT, "logos", fid + ".png")
        k = hashlib.sha1((DISENO + nombre + cat).encode("utf-8") + (open(logo, "rb").read() if os.path.exists(logo) else b"")).hexdigest()[:12]
        destino = os.path.join(carpeta, fid + ".png")
        if todas or claves.get(fid) != k or not os.path.exists(destino):
            pinta(nombre, cat, logo, destino); claves[fid] = k; n += 1
    vivas = {f[0] for f in fichas}
    for f in os.listdir(carpeta) if os.path.isdir(carpeta) else []:   # las de herramientas retiradas
        if f.endswith(".png") and f[:-4] not in vivas: os.remove(os.path.join(carpeta, f))
    claves = {k: v for k, v in sorted(claves.items()) if k in vivas}
    if fichas:
        open(rc, "w", encoding="utf-8", newline="\n").write(json.dumps(claves, indent=0, ensure_ascii=False) + "\n")
    return n


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build as b
    r = genera([(t["id"], b.split_name(t["n"])[0], b.CAT[t["cs"]][1]) for t in b.TOOLS], todas="--todas" in sys.argv)
    print("og: falta Pillow (pip install pillow)" if r is None else f"og: {r} imágenes pintadas")
