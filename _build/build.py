# Genera Didakora (antes «Caja de herramientas digitales» del portfolio) en varias páginas:
#   /                      portada: buscador, categorías, destacadas, quién la hace
#   /todas/                listado completo con buscador y filtros (JS)
#   /destacadas/           las diez más versátiles
#   /categorias/           índice de categorías y /categorias/<slug>/ con sus apartados
#   /<id>/                 una ficha por herramienta
#   /alternativas/         qué ha cerrado o cambiado y qué usar ahora
# Todas las rutas cuelgan de BASE ("/didakora" en GitHub Pages; "" si algún día va en dominio propio:
#   DK_BASE= python _build/build.py). Datos: tools.js. Logos de la marca: _build/marca.py → marca/.
# Uso: python _build/build.py
import json, os, re, subprocess, html, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = ROOT
B = os.environ.get("DK_BASE", "/didakora").rstrip("/")  # base de todas las rutas
SITE = "https://pasadoproximo.github.io"
V = "30"  # versión de didakora.css / didakora.js

d = json.loads(subprocess.check_output(["node", "-e",
    "const s=require('fs').readFileSync(process.argv[1],'utf8');const d=new Function(s+';return {SECTIONS,TOOLS,CHANGES}')();process.stdout.write(JSON.stringify(d))",
    os.path.join(H, "tools.js")]).decode("utf-8"))
SECTIONS, TOOLS, CHANGES = d["SECTIONS"], d["TOOLS"], d["CHANGES"]
LOGOS = {f[:-4] for f in os.listdir(os.path.join(H, "logos")) if f.endswith(".png")}
esc = lambda s: html.escape(str(s), quote=True)

# ---------------------------------------------------------------- categorías (10, por uso)
IC = {
 "participar": '<path d="M9 9a3 3 0 1 1 4.2 2.7c-.8.4-1.2 1-1.2 1.8V14"/><circle cx="12" cy="17.5" r=".6"/><circle cx="12" cy="12" r="9"/>',
 "crear": '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
 "colaborar": '<circle cx="8" cy="9" r="3"/><circle cx="16" cy="9" r="3"/><path d="M3 19c.8-3 2.8-4.5 5-4.5s4.2 1.5 5 4.5M11 19c.8-3 2.8-4.5 5-4.5s4.2 1.5 5 4.5"/>',
 "materias": '<path d="M4 5.5C6 4.5 9 4.5 12 6c3-1.5 6-1.5 8-.5V19c-2-1-5-1-8 .5-3-1.5-6-1.5-8-.5z"/><path d="M12 6v13.5"/>',
 "programar": '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M13.5 5l-3 14"/>',
 "ia": '<path d="M12 3v3M12 18v3M3 12h3M18 12h3"/><rect x="7" y="7" width="10" height="10" rx="2.5"/><path d="M10 12h4M12 10v4"/>',
 "evaluar": '<path d="M9 4h6v3H9z"/><path d="M8 5.5H6.5A1.5 1.5 0 0 0 5 7v12.5A1.5 1.5 0 0 0 6.5 21h11a1.5 1.5 0 0 0 1.5-1.5V7a1.5 1.5 0 0 0-1.5-1.5H16"/><path d="m9 14 2 2 4-4"/>',
 "gestion": '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 9.5h16M9 3v4M15 3v4"/>',
 "aulas": '<rect x="3" y="4.5" width="18" height="12" rx="2"/><path d="M8 20h8M12 16.5V20"/>',
 "recursos": '<rect x="4" y="4" width="16" height="16" rx="2.5"/><circle cx="9.5" cy="9.5" r="1.8"/><path d="m20 15-4.5-4.5L6 20"/>',
}
CATS = [
 ("participar-y-repasar", "Participar y repasar", "Cuestionarios, juegos y concursos para participar en clase y repasar.", "participar"),
 ("crear-y-presentar", "Crear y presentar", "Presentaciones, vídeo, audio, cómic y publicaciones del alumnado y del docente.", "crear"),
 ("colaborar-y-organizar", "Colaborar y organizar ideas", "Murales, mapas mentales, pizarras y herramientas para organizar recursos.", "colaborar"),
 ("explorar-por-materias", "Explorar por materias", "Herramientas propias de Geografía e Historia, Ciencias, Música y Arte o lectura.", "materias"),
 ("programacion-y-diseno-3d", "Programación y diseño 3D", "Pensamiento computacional, programación por bloques y diseño en 3D.", "programar"),
 ("inteligencia-artificial", "Inteligencia artificial", "Asistentes y herramientas de IA para preparar clase y para el alumnado.", "ia"),
 ("evaluacion-y-seguimiento", "Evaluación y seguimiento", "Formularios, rúbricas, itinerarios e insignias.", "evaluar"),
 ("gestion-del-aula", "Gestión del aula y familias", "Rutinas de clase, cuaderno del docente y comunicación con las familias.", "gestion"),
 ("aulas-virtuales", "Aulas virtuales", "Plataformas para organizar el curso, las tareas y las entregas.", "aulas"),
 ("bancos-de-recursos", "Bancos de recursos e imágenes", "Situaciones de aprendizaje, formación, imágenes y recursos abiertos.", "recursos"),
]
CAT = {c[0]: c for c in CATS}
# texto corto de las tarjetas de categoría (la página de cada categoría usa el largo)
CORTO = {"participar-y-repasar": "Cuestionarios y juegos", "crear-y-presentar": "Presentaciones, vídeo y audio",
         "colaborar-y-organizar": "Murales, mapas y pizarras", "explorar-por-materias": "Herramientas de cada materia",
         "programacion-y-diseno-3d": "Bloques y diseño 3D", "inteligencia-artificial": "Asistentes para el aula",
         "evaluacion-y-seguimiento": "Formularios y rúbricas", "gestion-del-aula": "Rutinas, cuaderno y familias",
         "aulas-virtuales": "Classroom, Teams y Moodle", "bancos-de-recursos": "Recursos e imágenes libres"}
PROG = {"scratch","snap","blockly","codeorg","appinventor","thunkable","cospaces","coppelia","snatchbot","tinkercad"}
LECT = {"immersive","readwrite"}
SUITES = {"classroom","teams","moodle"}
def place(t):
    s, c, i = t["s"], t["cat"], t["id"]
    if i in PROG: return ("programacion-y-diseno-3d", "Programación y diseño 3D")
    if i in LECT: return ("explorar-por-materias", "Lectura y accesibilidad")
    if i in SUITES: return ("aulas-virtuales", "Aulas virtuales")
    return {("aula","part"):("participar-y-repasar","Cuestionarios y juegos"), ("aula","geohis"):("explorar-por-materias","Geografía e Historia"),
            ("aula","crear"):("crear-y-presentar","Lo crea el alumnado"), ("aula","equipo"):("colaborar-y-organizar","Trabajar en equipo"),
            ("aula","cienc"):("explorar-por-materias","Ciencias y Matemáticas"), ("aula","arte"):("explorar-por-materias","Música y Arte"),
            ("aula","ia"):("inteligencia-artificial","IA para el alumnado"), ("docente","ia"):("inteligencia-artificial","IA para preparar clase"),
            ("docente","crear"):("crear-y-presentar","Materiales del docente"), ("docente","gestion"):("gestion-del-aula","Gestión del aula"),
            ("docente","eval"):("evaluacion-y-seguimiento","Evaluar y motivar"), ("docente","org"):("colaborar-y-organizar","Organizar recursos"),
            ("recursos","sa"):("bancos-de-recursos","Situaciones de aprendizaje"), ("recursos","form"):("bancos-de-recursos","Formación e inspiración"),
            ("recursos","img"):("bancos-de-recursos","Imágenes y multimedia")}[(s, c)]
# etapas: Didakora es de Secundaria; Infantil y Primaria cuando el repositorio de 2024 las recogía también ahí
REPO_P = {"chatterpix","stopmotion","suno","canva","genially","padlet","stormboard","vocaroo","bookcreator","codeorg","blockly","classdojo",
          "nearpod","badge","educaplay","exelearning","kahoot","plickers","edpuzzle","loom","scratch","phet","gizmos","geogebra","classroomscreen","fastboard"}
REPO_I = {"chatterpix","codeorg","educaplay","kahoot","plickers"}
def etapas(i): return [e for e, ok in (("I", i in REPO_I), ("P", i in REPO_P), ("S", True)) if ok]
ETN = {"I": "Infantil", "P": "Primaria", "S": "Secundaria y Bachillerato"}
for t in TOOLS:
    t["cs"], t["sub"] = place(t); t["et"] = etapas(t["id"])
BYID = {t["id"]: t for t in TOOLS}
NUEVAS = [t for t in TOOLS if t["st"] == "nueva"]
# destacadas de la portada: cuatro, elegidas por versátiles (NotebookLM primero)
DESTACADAS = ["notebooklm", "kahoot", "canva", "padlet", "genially", "edpuzzle", "mentimeter", "gforms", "classroomscreen", "classroom"]
# texto corto de cada destacada
DEST_TXT = {"notebooklm": "Responde solo con tus documentos y cita la fuente.",
            "kahoot": "Concursos de preguntas en directo.",
            "canva": "Infografías, pósteres y vídeos con plantillas.",
            "padlet": "Un muro compartido para ideas y enlaces.",
            "genially": "Presentaciones y juegos interactivos.",
            "edpuzzle": "Vídeos con preguntas que el alumnado responde.",
            "mentimeter": "Votaciones y nubes de palabras en directo.",
            "gforms": "Cuestionarios que se corrigen solos.",
            "classroomscreen": "Temporizador, semáforo y ruido en la pizarra.",
            "classroom": "Tareas, materiales y notas de la clase."}

# ---------------------------------------------------------------- piezas comunes
ICO = {"ext": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>',
       "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
       "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.4-4.4"/></svg>',
       "home": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 11 12 4l8 7v9h-5v-6h-6v6H4z"/></svg>',
       "check": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.5 2.5L16 9.5"/></svg>',
       "warn": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/></svg>',
       "share": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.4M8.2 13.2l7.6 4.4"/></svg>',
       "play": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m10 9 5 3-5 3z"/></svg>'}
def icon(k): return f'<svg viewBox="0 0 24 24" aria-hidden="true">{IC[k]}</svg>'
def logo(t, size=26): return (f'<img src="{B}/logos/{t["id"]}.png?v=3" alt="" width="{size}" height="{size}" loading="lazy">' if t["id"] in LOGOS
                              else f'<b aria-hidden="true">{esc(t["n"][0])}</b>')
def split_name(n):
    m = re.match(r"^(.+?)\s*\((.+)\)$", n); return (m.group(1), m.group(2)) if m else (n, "")
def lead(t): return t.get("a") if t["s"] == "aula" else t.get("p") if t["s"] == "docente" else t.get("d")
def card_dest(t):
    """tarjeta compacta de las destacadas: texto corto, categoría a la izquierda y solo la flecha"""
    nm, alias = split_name(t["n"]); c = CAT[t["cs"]]
    return (f'<article class="tc td"><div class="tc-h"><span class="lg">{logo(t)}</span><h3><a class="tc-a" href="{B}/{t["id"]}/">{esc(nm)}</a>'
            f'{f"<small>{esc(alias)}</small>" if alias else ""}</h3></div><p>{esc(DEST_TXT[t["id"]])}</p>'
            f'<div class="tc-f"><a class="tag" href="{B}/categorias/{c[0]}/">{icon(c[3])}{esc(c[1])}</a>'
            f'<a class="td-x" href="{esc(t["url"])}" rel="noopener" target="_blank">{ICO["ext"]}<span class="sr">Abrir {esc(nm)} (se abre en otra pestaña)</span></a></div></article>')

def card(t, cat=True):
    """tarjeta de herramienta: logo y nombre, frase de uso, categoría a la izquierda y flecha (abre la herramienta).
    En la página de una categoría no hace falta repetirla: cat=False."""
    nm, alias = split_name(t["n"]); c = CAT[t["cs"]]
    go = f'<a class="td-x" href="{esc(t["url"])}" rel="noopener" target="_blank">{ICO["ext"]}<span class="sr">Abrir {esc(nm)} (se abre en otra pestaña)</span></a>'
    head = (f'<div class="tc-h"><span class="lg">{logo(t)}</span><h3><a class="tc-a" href="{B}/{t["id"]}/">{esc(nm)}</a>'
            f'{f"<small>{esc(alias)}</small>" if alias else ""}</h3>{"" if cat else go}</div><p>{esc(lead(t))}</p>')
    if not cat:  # sin categoría: la flecha sube junto al nombre y la tarjeta no lleva pie
        return f'<article class="tc td nc">{head}</article>'
    return (f'<article class="tc td">{head}'
            f'<div class="tc-f"><a class="tag" href="{B}/categorias/{c[0]}/">{icon(c[3])}{esc(c[1])}</a>{go}</div></article>')

def _svg_inline(name, cls):
    """mete en la página un SVG de marca/ (sin el <title>, que ya da el aria-label del enlace)"""
    x = open(os.path.join(ROOT, "marca", name), encoding="utf-8").read().strip()
    x = re.sub(r"<title>.*?</title>", "", x).replace(' role="img" aria-label="Didakora"', ' aria-hidden="true" focusable="false"')
    return x.replace("<svg ", f'<svg class="{cls}" ', 1)
LOGO = _svg_inline("didakora-logo-a.svg", "lockup")
def topbar(cur=""):
    nav = [("todas", "Todas", "/todas/"), ("categorias", "Categorías", "/categorias/"), ("destacadas", "Destacadas", "/destacadas/"), ("sobre", "Sobre mí", "/sobre-mi/")]
    links = "".join(f'<a href="{B}{h}"' + (' aria-current="page"' if k == cur else "") + f'>{t}</a>' for k, t, h in nav)
    return f'''<header class="top">
 <div class="bar">
  <a class="brand" href="{B}/" aria-label="Didakora · inicio">{LOGO}</a>
  <nav aria-label="Principal">{links}</nav>
 </div>
</header>'''
def head(title, desc, path, cur=""):
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}{B}/marca/og.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}{B}{path}">
<link rel="icon" href="{B}/marca/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{B}/marca/icono-180.png">
<meta name="theme-color" content="#9FB3FF">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+SC:wght@700&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&display=swap">
<link rel="stylesheet" href="{B}/didakora.css?v={V}">
</head>
<body>
<div class="wrap">
{topbar(cur)}
'''
def foot(scripts=""):
    return f'''
<aside class="fin" aria-labelledby="h-inv">
 <div><h2 id="h-inv">¿Echas en falta una herramienta?</h2><p>Propónmela y la reviso con los mismos criterios.</p></div>
 <a class="btn solid" href="{B}/sobre-mi/#contacto">Proponer una herramienta {ICO["arrow"]}</a>
</aside>
<footer class="ft">
 <p>Jorge Delgado Aguilera</p>
 <a class="ft-cc" rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es" target="_blank" title="Textos con licencia Creative Commons BY-NC-SA 4.0">CC BY-NC-SA 4.0</a>
</footer>
</div>
<script>window.DK_BASE="{B}"</script>
<script src="{B}/didakora.js?v={V}"></script>{scripts}
</body>
</html>
'''
def write(rel, content):
    p = os.path.join(H, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(content)
def crumbs(items):
    """botón de volver que va junto al título de cada página interior (sin ruta)"""
    up = [h for _, h in items if h][-1]  # página de la que cuelga: destino del botón si no hay historial
    back = f'<a class="back" href="{up}" data-back><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg><span class="sr">Atrás</span></a>'
    return back
def secth(lab, title, desc="", hid=""):
    return f'<div class="sh">{f'<span class="lab">{esc(lab)}</span>' if lab else ""}<h2{f" id={chr(34)}{hid}{chr(34)}" if hid else ""}>{esc(title)}</h2>{f"<p>{esc(desc)}</p>" if desc else ""}</div>'
def catcard(c):
    return (f'<a class="cc" href="{B}/categorias/{c[0]}/"><span class="cc-i">{icon(c[3])}</span><b>{esc(c[1])}</b><span class="cc-d">{esc(CORTO[c[0]])}</span>'
            f'<span class="cc-x" aria-hidden="true">{ICO["ext"]}</span></a>')

def etapas_html(fid, cls=""):
    """desplegable de etapa a medida (el nativo sale cuadrado): botón en píldora y lista redondeada; lo maneja didakora.js.
    El valor va en un campo oculto name=nivel, así el formulario de la portada lo manda a /todas/."""
    ops = [("", "Todas las etapas"), ("I", "Infantil"), ("P", "Primaria"), ("S", "Secundaria y Bachillerato")]
    li = "".join(f'<li role="option" id="{fid}-{v or "t"}" data-v="{v}" aria-selected="{"true" if not v else "false"}">{t}</li>' for v, t in ops)
    chev = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
    return (f'<div class="dd{cls}" id="{fid}"><input type="hidden" name="nivel" value="">'
            f'<button type="button" class="dd-b" aria-haspopup="listbox" aria-expanded="false" aria-controls="{fid}-l" aria-labelledby="{fid}-k {fid}-v">'
            f'<span class="sr" id="{fid}-k">Etapa:</span><span class="dd-v" id="{fid}-v">Todas las etapas</span>{chev}</button>'
            f'<ul class="dd-l" id="{fid}-l" role="listbox" aria-label="Etapa" tabindex="-1" hidden>{li}</ul></div>')

# ---------------------------------------------------------------- portada
def portada():
    dest = "".join(card_dest(BYID[i]) for i in DESTACADAS[:4])
    body = f'''
<main>
 <section class="hero" aria-labelledby="ph1">
  <div class="hero-t">
   <span class="lab">Herramientas digitales para docentes</span>
   <h1 id="ph1">La herramienta que <span>necesitas</span> para tu clase</h1>
   <p class="hero-d">Descubre apps, plataformas y recursos para planificar clases, evaluar, crear actividades, gamificar y atender la diversidad. Todos revisados uno a uno y explicados con un ejemplo de uso.</p>
  </div>
  <form class="hs" action="{B}/todas/" method="get" role="search">
   <div class="hs-r"><div class="hs-q">{ICO["search"]}<label class="sr" for="hq">Busca una herramienta</label><input id="hq" name="q" type="text" placeholder="Busca por nombre o por lo que necesitas hacer…" autocomplete="off" enterkeyhint="search"></div>
   {etapas_html("nv")}
   <button type="submit">Buscar {ICO["arrow"]}</button></div>
  </form>
 </section>


 <section class="sec" aria-labelledby="h-cats">
  {secth("", "Categorías principales", "Navega por lo que necesitas.", "h-cats")}
  <div class="ccg c4">{"".join(catcard(c) for c in CATS[:4])}</div>
  <p class="more"><a class="btn solid" href="{B}/categorias/">Ver las {len(CATS)} categorías {ICO["arrow"]}</a></p>
 </section>

 <section class="sec" aria-labelledby="h-dest">
  {secth("", "Herramientas destacadas", "Las más versátiles para empezar a usar en clase.", "h-dest")}
  <div class="tcg c4">{dest}</div>
  <p class="more"><a class="btn solid" href="{B}/destacadas/">Ver las {len(DESTACADAS)} destacadas {ICO["arrow"]}</a></p>
 </section>


</main>'''
    write("index.html", head("Didakora · Herramientas digitales para docentes",
        f"{len(TOOLS)} herramientas digitales para docentes, revisadas en octubre de 2026, con ejemplo de uso, etapa recomendada y lo que necesita cada una.", "/") + body + foot())

# ---------------------------------------------------------------- listado completo (lo pinta didakora.js)
def todas():
    chips = '<button type="button" data-cat="" aria-pressed="true">Todas</button>' + "".join(f'<button type="button" data-cat="{c[0]}" aria-pressed="false">{esc(c[1])}</button>' for c in CATS)
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Todas las herramientas", "")])}<h1>Todas las herramientas</h1></div><p>Busca por nombre o por lo que necesitas hacer y filtra por categoría o por etapa.</p></div>
 <form class="ls" role="search" onsubmit="return false">
  <div class="hs-r"><div class="hs-q">{ICO["search"]}<label class="sr" for="lq">Busca una herramienta</label><input id="lq" type="text" placeholder="Busca por nombre o por lo que necesitas hacer…" autocomplete="off" enterkeyhint="search"></div>
  {etapas_html("lnv", " l")}</div>
 </form>
 <div class="chips" id="lcats" role="group" aria-label="Categoría">{chips}</div>
 <p class="count" id="lcount" aria-live="polite"></p>
 <div class="tcg" id="lgrid"></div>
 <noscript><div class="tcg">{"".join(card(t) for t in TOOLS)}</div></noscript>
</main>'''
    write("todas/index.html", head("Todas las herramientas · Didakora", "Todas las herramientas de Didakora, con buscador y filtros por categoría y etapa.", "/todas/", "todas")
          + body + foot(f'\n<script src="{B}/tools.js?v={V}"></script>\n<script src="{B}/didakora-datos.js?v={V}"></script>\n<script>cajaListado()</script>'))

# ---------------------------------------------------------------- sobre mí y contacto
CONTACTO = [
 ("mail", "Correo", "jorgedelagui@gmail.com", "mailto:jorgedelagui@gmail.com"),
 ("in", "LinkedIn", "jorgedelgadoaguilera", "https://www.linkedin.com/in/jorgedelgadoaguilera"),
 ("ig", "Instagram", "@pasadoproximo · divulgación histórica", "https://www.instagram.com/pasadoproximo/"),
]
CICO = {"mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/>',
        "in": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10.5V16M8 7.8v.1M12 16v-5.5M12 13c0-1.6 1-2.6 2.3-2.6S16.5 11.3 16.5 13v3"/>',
        "ig": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17 7v.1"/>'}
def sobremi():
    cont = "".join(f'<li><a href="{u}"{"" if u.startswith("mailto:") else " rel=" + chr(34) + "noopener" + chr(34) + " target=" + chr(34) + "_blank" + chr(34)}>'
                   f'<span class="ci"><svg viewBox="0 0 24 24" aria-hidden="true">{CICO[k]}</svg></span><span><b>{t}</b><small>{esc(d)}</small></span>'
                   f'<span class="cc-x" aria-hidden="true">{ICO["ext"]}</span></a></li>' for k, t, d, u in CONTACTO)
    body = f'''
<main class="pg">
 <section class="me">
  <img src="{B}/img/jorge.jpg" alt="Jorge Delgado Aguilera en un aula, con una estantería de libros y un mapamundi al fondo" width="720" height="734">
  <div>
   <div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Sobre mí", "")])}<h1>Sobre mí</h1></div>
   <p>Soy Jorge Delgado Aguilera, profesor de Geografía e Historia y diseñador de materiales educativos digitales. Didakora es la actualización del repositorio digital que creé en 2024 para el Colegio Cerrado de Calderón, que el centro presentó en el IX Congreso Internacional de Creatividad Educativa (Braining, Valencia, 2025).</p>
   <p>Cada herramienta se comprueba a mano: que funcione hoy, para qué tarea de clase sirve, si se puede empezar gratis, si pide cuenta y qué edad mínima exige. Si una cierra o cambia de nombre, lo anoto y propongo una alternativa.</p>
   <p class="more"><a class="btn solid" href="{SITE}/" rel="noopener" target="_blank">Visita mi portfolio {ICO["ext"]}</a><a class="btn line" href="{SITE}/proyectos/repositorio-digital/" rel="noopener" target="_blank">Cómo hice Didakora {ICO["ext"]}</a></p>
  </div>
 </section>
 <section class="sec contact" id="contacto" aria-labelledby="h-contacto">
  {secth("", "Contacta conmigo", "Para proponer una herramienta, avisar de un enlace que ya no funciona o hablar de un proyecto.", "h-contacto")}
  <ul class="cl">{cont}</ul>
 </section>
</main>'''
    write("sobre-mi/index.html", head("Sobre mí · Didakora", "Quién hace Didakora y cómo contactar con él: Jorge Delgado Aguilera, profesor de Geografía e Historia y diseñador de materiales educativos digitales.", "/sobre-mi/", "sobre") + body + foot())

# ---------------------------------------------------------------- destacadas
def destacadas():
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Herramientas destacadas", "")])}<h1>Herramientas destacadas</h1></div><p>Las {len(DESTACADAS)} más versátiles para empezar a usar en clase.</p></div>
 <div class="tcg c4">{"".join(card_dest(BYID[i]) for i in DESTACADAS)}</div>
 <p class="more"><a class="btn solid" href="{B}/todas/">Ver todas las herramientas {ICO["arrow"]}</a></p>
</main>'''
    write("destacadas/index.html", head("Herramientas destacadas · Didakora", f"Las {len(DESTACADAS)} herramientas más versátiles de Didakora para empezar a usar en clase.", "/destacadas/", "destacadas") + body + foot())

# ---------------------------------------------------------------- categorías
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower().translate(str.maketrans("áéíóúñü", "aeiounu"))).strip("-")
def categorias():
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Categorías", "")])}<h1>Categorías</h1></div><p>Diez categorías según para qué sirve cada herramienta.</p></div>
 <div class="ccg">{"".join(catcard(c) for c in CATS)}</div>
</main>'''
    write("categorias/index.html", head("Categorías · Didakora", "Las diez categorías de Didakora, según para qué sirve cada herramienta.", "/categorias/", "categorias") + body + foot())
    for c in CATS:
        ts = [t for t in TOOLS if t["cs"] == c[0]]
        subs = []
        for t in ts:
            if t["sub"] not in subs: subs.append(t["sub"])
        nav = "".join(f'<a href="#{slug(s)}">{esc(s)} <span>{sum(1 for t in ts if t["sub"] == s)}</span></a>' for s in subs) if len(subs) > 1 else ""
        blocks = "".join(f'<section class="sub" aria-labelledby="{slug(s)}"><h2 id="{slug(s)}">{esc(s)} <span>{sum(1 for t in ts if t["sub"] == s)}</span></h2><div class="tcg">{"".join(card(t, False) for t in ts if t["sub"] == s)}</div></section>' for s in subs)
        others = "".join(f'<a href="{B}/categorias/{o[0]}/">{icon(o[3])}{esc(o[1])}</a>' for o in CATS if o[0] != c[0])
        body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Categorías", f"{B}/categorias/"), (c[1], "")])}<h1>{esc(c[1])}</h1></div><p>{esc(c[2])} {len(ts)} herramientas.</p></div>
 {f'<nav class="subnav" aria-label="Apartados">{nav}</nav>' if nav else ""}
 {blocks}
 <section class="sec others" aria-labelledby="h-otras"><h2 id="h-otras">Otras categorías</h2><div class="oc">{others}</div></section>
</main>'''
        write(f"categorias/{c[0]}/index.html", head(f"{c[1]} · Didakora", f"{c[2]} {len(ts)} herramientas revisadas en octubre de 2026.", f"/categorias/{c[0]}/", "categorias") + body + foot())

# ---------------------------------------------------------------- fichas
OWN = re.compile(r"^no necesita|código|codigo|del docente|del centro|enlace del docente|integrado|extensión|solo para guardar|clase del docente", re.I)
def uses_ai(t):
    a = (t.get("a") or "").lower(); a = a.translate(str.maketrans("áéíóú", "aeiou"))
    return t["s"] == "aula" and re.search(r"(^|[^a-z])ia([^a-z]|$)", a) is not None
def yt(t): return "https://www.youtube.com/results?search_query=" + re.sub(r"\s+", "+", re.sub(r"\s*\(.*\)", "", t["n"]) + " tutorial español")
def ficha(t):
    nm, alias = split_name(t["n"]); c = CAT[t["cs"]]; aula = t["s"] == "aula"; rec = t["s"] == "recursos"
    tags = f'<a class="tag" href="{B}/categorias/{c[0]}/">{icon(c[3])}{esc(c[1])}</a>' + "".join(f'<span class="tag et">{ETN[e]}</span>' for e in t["et"]) + ('<span class="tag new">Nueva en 2026</span>' if t["st"] == "nueva" else "")
    rows = []
    if aula: rows += [("Para", "El alumnado, en clase"), ("Nivel", t["c"]), ("Dispositivos", t["disp"]), ("Cuenta del alumnado", t["cta"])]
    elif not rec: rows += [("Para", "El docente"), ("Coste", t["coste"]), ("Datos del alumnado", t["datos"])]
    else: rows += [("Tipo", "Recurso en abierto")]
    if t.get("edad"): rows.append(("Edad mínima", f'{esc(t["edadTxt"])} · <a href="{esc(t["edadUrl"])}" rel="noopener" target="_blank">condiciones</a>'))
    dl = "".join(f'<div><dt>{k}</dt><dd>{v if k == "Edad mínima" else esc(v)}</dd></div>' for k, v in rows)
    warn = []
    if aula and not t.get("edad") and not OWN.search(t["cta"]): warn.append("Consulta la edad mínima en las condiciones de la herramienta antes de que el alumnado cree una cuenta.")
    if uses_ai(t): warn.append("El alumnado trabaja con una IA: usa la cuenta del centro, comprueba la edad mínima en sus condiciones y no introduzcas datos personales.")
    if t.get("nota"): warn.append(t["nota"])
    ideas = t.get("i") or []
    sec_ideas = (f'<section class="fb"><h2>{"Ideas para clase" if aula else "Ideas de uso"}</h2><ul class="ok">{"".join(f"<li>{ICO[chr(99)+chr(104)+chr(101)+chr(99)+chr(107)]}{esc(x)}</li>" for x in ideas)}</ul></section>' if ideas else "")
    sec_warn = (f'<section class="fb warnb"><h2>Antes de usarla</h2>{"".join(f"<p>{ICO[chr(119)+chr(97)+chr(114)+chr(110)]}<span>{esc(w)}</span></p>" for w in warn)}</section>' if warn else "")
    # alternativas en rueda: las siguientes del mismo apartado (y luego de la categoría), así toda herramienta
    # aparece como alternativa en alguna ficha y no salen siempre las mismas tres
    def ring(group):
        i = group.index(t); return [group[(i + k) % len(group)] for k in range(1, len(group))]
    same = ring([o for o in TOOLS if o["sub"] == t["sub"] and o["cs"] == t["cs"]])
    alts = (same + [o for o in ring([o for o in TOOLS if o["cs"] == t["cs"]]) if o not in same])[:3]
    que = ("Qué hace el alumnado" if aula else "Para qué te sirve" if not rec else "Qué encontrarás")
    body = f'''
<main class="pg">
 <section class="fh">
  <span class="lg xl">{logo(t, 44)}</span>
  <div class="fh-t"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), (c[1], f"{B}/categorias/{c[0]}/"), (nm, "")])}<h1>{esc(nm)}{f" <small>{esc(alias)}</small>" if alias else ""}</h1></div><p>{esc(lead(t))}</p><div class="tags">{tags}</div></div>
  <div class="fh-b"><a class="btn solid" href="{esc(t["url"])}" rel="noopener" target="_blank">Abrir {esc(nm)} {ICO["ext"]}</a><button type="button" class="btn line" data-share>{ICO["share"]}Compartir</button></div>
 </section>
 <div class="fg">
  <div class="fm">
   <section class="fb"><h2>Qué es {esc(nm)} y cómo se usa en clase</h2><p><b>{que}:</b> {esc(lead(t))}</p>{f'<p class="ex"><b>Ejemplo:</b> {esc(ideas[0])}</p>' if ideas else ""}</section>
   {sec_ideas}
   {sec_warn}
  </div>
  <aside class="fa">
   <section class="fb"><h2>Ficha rápida</h2><dl>{dl}</dl>{"" if rec else f'<a class="tut" href="{yt(t)}" rel="noopener" target="_blank">{ICO["play"]}Buscar videotutoriales <span class="sr">(se abre en otra pestaña)</span></a>'}</section>
  </aside>
 </div>
 <section class="sec alt" aria-labelledby="h-alt"><h2 id="h-alt">Herramientas alternativas</h2><div class="tcg">{"".join(card(o) for o in alts)}</div>
  <p class="more"><a class="btn line" href="{B}/categorias/{c[0]}/">Ver todo {esc(c[1])} {ICO["arrow"]}</a></p></section>
</main>'''
    write(f'{t["id"]}/index.html', head(f"{nm} · Didakora", f"{lead(t)} Ficha revisada en octubre de 2026.", f'/{t["id"]}/') + body + foot())

# ---------------------------------------------------------------- alternativas (qué ha cambiado)
def alternativas():
    rowsh = []
    for ch in CHANGES[:-1]:
        ren = re.search(r"cambi[oó] su nombre", ch["what"], re.I)
        rowsh.append(f'<div class="chr"><div><span class="tg {"nom" if ren else "cie"}">{"Cambio de nombre" if ren else "Ha cerrado"}</span><h2>{esc(ch["n"])}</h2><p>{esc(ch["what"])}</p></div>'
                     f'<span class="ar" aria-hidden="true">{ICO["arrow"]}</span><div class="now"><span class="lab">{"Dónde está ahora" if ren else "Qué usar ahora"}</span><p>{esc(ch["alt"])}</p></div></div>')
    last = CHANGES[-1]
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Qué ha cambiado", "")])}<h1>Qué ha cambiado y qué usar ahora</h1></div><p>Herramientas del repositorio de 2024 que han cerrado o cambiado de nombre, con la alternativa que se puede usar hoy.</p></div>
 <div class="chl">{"".join(rowsh)}</div>
 <section class="sec chn"><span class="lab">Novedad</span><h2>{esc(last["n"])}</h2><p>{esc(last["what"])}</p><p><b>Qué hacer:</b> {esc(last["alt"])}</p></section>
</main>'''
    write("alternativas/index.html", head("Qué ha cambiado · Didakora", "Herramientas que han cerrado o cambiado de nombre desde 2024 y qué usar ahora.", "/alternativas/", "alternativas") + body + foot())

# ---------------------------------------------------------------- datos para el listado
def datos():
    m = {t["id"]: [t["cs"], t["et"], 1 if t["id"] in LOGOS else 0, t["sub"]] for t in TOOLS}
    cats = {c[0]: [c[1], IC[c[3]]] for c in CATS}
    write("didakora-datos.js", "// Generado por _build/build.py: categoría, etapas, logo y apartado de cada herramienta\nconst CAJA=" + json.dumps({"cats": cats, "t": m}, ensure_ascii=False) + ";\n")

if __name__ == "__main__":
    shutil.copyfile(os.path.join(ROOT, "_build", "didakora.css"), os.path.join(H, "didakora.css"))
    shutil.copyfile(os.path.join(ROOT, "_build", "didakora.js"), os.path.join(H, "didakora.js"))
    datos(); portada(); todas(); destacadas(); categorias(); alternativas(); sobremi()
    for t in TOOLS: ficha(t)
    print("didakora:", len(TOOLS), "fichas,", len(CATS), "categorías")
