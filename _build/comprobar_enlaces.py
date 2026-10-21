# Comprueba los enlaces de tools.js: la web de cada herramienta (url) y la fuente de su edad mínima (edadUrl).
# Solo lee: no cambia nada. Lo usan el Auditor y el Coordinador editorial del sistema de agentes.
#   ok              responde 2xx (aunque redirija dentro del mismo dominio)
#   redirige        responde, pero acaba en otro dominio: revisar si la herramienta ha cambiado de web o de nombre
#   roto            404, 410, el dominio no existe o acaba en una página de error (…/404, ?404, not-found)
#   no verificable  403, 429, 5xx o sin respuesta: muchas webs bloquean a los robots; abrirla a mano antes de concluir nada
# Uso: python _build/comprobar_enlaces.py [--json salida.json] [--solo id1,id2 (o id1 id2)]
import json, os, re, subprocess, sys, socket, urllib.request, urllib.error
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERROR = re.compile(r"(^|[/?&=_.-])(404|not-?found|page-?not-?found|error)([/?&=_.-]|$)", re.I)
LOGIN = {"accounts.google.com", "login.microsoftonline.com", "login.live.com"}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

TOOLS = json.loads(subprocess.check_output(["node", "-e",
    "const s=require('fs').readFileSync(process.argv[1],'utf8');process.stdout.write(JSON.stringify(new Function(s+';return TOOLS')()))",
    os.path.join(ROOT, "tools.js")]).decode("utf-8"))

def dominio(u):
    h = urlparse(u).hostname or ""
    return h[4:] if h.startswith("www.") else h

def comprobar(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            final = r.geturl()
            if ERROR.search(urlparse(final).path + "?" + urlparse(final).query):  # responde 200, pero es una página de error
                return "roto", r.status, final
            if dominio(final) in LOGIN:  # pide iniciar sesión: la web existe
                return "ok", r.status, "pide iniciar sesión"
            if dominio(final) != dominio(u) and not dominio(final).endswith("." + dominio(u)):
                return "redirige", r.status, final
            return "ok", r.status, final
    except urllib.error.HTTPError as e:
        return ("roto" if e.code in (404, 410) else "no verificable"), e.code, ""
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.gaierror):
            return "roto", 0, "el dominio no existe"
        return "no verificable", 0, str(e.reason)[:80]
    except Exception as e:
        return "no verificable", 0, str(e)[:80]

def main():
    a = sys.argv[1:]
    solo = None
    if "--solo" in a:  # ids separados por comas o por espacios
        i, vals = a.index("--solo") + 1, []
        while i < len(a) and not a[i].startswith("--"): vals += a[i].split(","); i += 1
        solo = {v for v in vals if v}
        faltan = solo - {t["id"] for t in TOOLS}
        if faltan: print("Ids que no están en tools.js:", ", ".join(sorted(faltan)))
    enlaces = [(t["id"], campo, t[campo]) for t in TOOLS if not solo or t["id"] in solo
               for campo in ("url", "edadUrl") if t.get(campo)]
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda e: comprobar(e[2]), enlaces))
    filas = [dict(id=i, campo=c, url=u, estado=r[0], codigo=r[1], destino=r[2]) for (i, c, u), r in zip(enlaces, res)]
    cuenta = {}
    for f in filas:
        cuenta[f["estado"]] = cuenta.get(f["estado"], 0) + 1
    print(f"Enlaces comprobados: {len(filas)} · " + " · ".join(f"{k}: {v}" for k, v in sorted(cuenta.items())))
    for f in filas:
        if f["estado"] != "ok":
            print(f'- {f["estado"]:<15} {f["id"]} ({f["campo"]}) {f["url"]} · {f["codigo"] or ""} {f["destino"]}'.rstrip())
    if "--json" in a:
        with open(a[a.index("--json") + 1], "w", encoding="utf-8") as fh:
            json.dump(dict(resumen=cuenta, enlaces=filas), fh, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
