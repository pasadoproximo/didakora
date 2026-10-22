# Capturas de fichas a 390 px de ancho con Edge sin ventana (perfil propio: no choca con otro navegador abierto).
# Las usa el Auditor para revisar el móvil y el monasterio para enseñar a Jorge el antes y el después de cada cambio.
#   python _build/capturas.py <carpeta> id1,id2[,portada]            → <id>-despues.png de la web local (127.0.0.1:8020)
#   python _build/capturas.py <carpeta> id1,id2 --antes              → <id>-antes.png de la web publicada (GitHub Pages)
# Una herramienta nueva no tiene «antes»: la publicada da 404 y no se guarda captura.
# Otras páginas: nombre=ruta (p. ej. boletin-1=boletin/1 o vista=agentes/boletin/numeros/2026-10-22/vista) → <nombre>-despues.png
import os, subprocess, sys, tempfile, urllib.request, urllib.error

EDGE = next((p for p in [os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                         os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")] if os.path.exists(p)), None)
LOCAL, PUBLICADA = "http://127.0.0.1:8020/didakora/", "https://pasadoproximo.github.io/didakora/"

def existe(url):
    try: urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20); return True
    except urllib.error.HTTPError: return False
    except Exception: return True  # sin red no se decide aquí: que lo intente Edge

def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) < 2: sys.exit(__doc__ or "uso: python _build/capturas.py <carpeta> id1,id2 [--antes]")
    if not EDGE: sys.exit("No encuentro Edge")
    antes = "--antes" in sys.argv
    carpeta, ids = a[0], [i for i in ",".join(a[1:]).replace(" ", ",").split(",") if i]
    os.makedirs(carpeta, exist_ok=True)
    perfil = tempfile.mkdtemp(prefix="dk-capturas-")
    for i in ids:
        i, ruta = i.split("=", 1) if "=" in i else (i, i)
        url = (PUBLICADA if antes else LOCAL) + ("" if ruta == "portada" else ruta.strip("/") + "/")
        salida = os.path.abspath(os.path.join(carpeta, f"{i}-{'antes' if antes else 'despues'}.png"))
        if antes and not existe(url): print(i, "sin antes (no está publicada)"); continue
        # Edge sin ventana no baja de ~500 px de ancho: la ficha va dentro de un marco de 390 px (así aplica el CSS de móvil)
        marco = os.path.join(perfil, "marco.html")
        with open(marco, "w", encoding="utf-8") as f:
            f.write(f'<!doctype html><body style="margin:0;background:#fff"><iframe src="{url}" style="border:0;width:390px;height:1600px;display:block"></iframe>')
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--virtual-time-budget=6000",
                        f"--user-data-dir={perfil}", "--window-size=640,1600", f"--screenshot={salida}", "file:///" + marco.replace("\\", "/")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90, check=False)
        if os.path.exists(salida):
            try:
                from PIL import Image
                Image.open(salida).crop((0, 0, 390, 1600)).save(salida)
            except ImportError: pass
        print(i, "ok" if os.path.exists(salida) else "sin captura")

if __name__ == "__main__":
    main()
