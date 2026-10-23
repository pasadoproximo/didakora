# Genera Didákora (antes «Caja de herramientas digitales» del portfolio) en varias páginas:
#   /                      portada: buscador, categorías, añadidas recientemente y actualidad
#   /todas/                listado completo con buscador y filtros (JS)
#   /destacadas/           las diez más versátiles (ya sin enlace en el menú ni en la portada)
#   /nuevas/               las últimas añadidas (RECIENTES en tools.js)
#   /categorias/           índice de categorías y /categorias/<slug>/ con sus apartados
#   /<id>/                 una ficha por herramienta
#   /actualidad/           el blog de noticias de educación digital y /actualidad/<slug>/ cada post (_build/actualidad/)
# Todas las rutas cuelgan de BASE ("/didakora" en GitHub Pages; "" si algún día va en dominio propio:
#   DK_BASE= python _build/build.py). Datos: tools.js. Logos de la marca: _build/marca.py → marca/.
# Uso: python _build/build.py
#      python _build/build.py --vista <post.json> <carpeta>   → solo la vista previa de un post (no toca la web)
import json, os, re, subprocess, html, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = ROOT
B = os.environ.get("DK_BASE", "/didakora").rstrip("/")  # base de todas las rutas
SITE = "https://pasadoproximo.github.io"
V = "65"  # versión de didakora.css / didakora.js

d = json.loads(subprocess.check_output(["node", "-e",
    "const s=require('fs').readFileSync(process.argv[1],'utf8');const d=new Function(s+';return {SECTIONS,TOOLS,CHANGES,RECIENTES:typeof RECIENTES==`undefined`?[]:RECIENTES}')();process.stdout.write(JSON.stringify(d))",
    os.path.join(H, "tools.js")]).decode("utf-8"))
SECTIONS, TOOLS, CHANGES, RECIENTES = d["SECTIONS"], d["TOOLS"], d["CHANGES"], d["RECIENTES"]
LOGOS = {f[:-4] for f in os.listdir(os.path.join(H, "logos")) if f.endswith(".png")}
esc = lambda s: html.escape(str(s), quote=True)
# posts de Actualidad (los prepara el ciclo del blog, /boletin): uno por archivo, del más antiguo al más reciente
PDIR = os.path.join(ROOT, "_build", "actualidad")
POSTS = sorted((json.load(open(os.path.join(PDIR, f), encoding="utf-8")) for f in os.listdir(PDIR) if f.endswith(".json")),
               key=lambda p: (p["fecha"], p.get("numero", 0))) if os.path.isdir(PDIR) else []

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
 ("colaborar-y-organizar", "Colaborar y organizar", "Murales, mapas mentales, pizarras y herramientas para organizar recursos.", "colaborar"),
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
# etapas: Didákora es de Secundaria; Infantil y Primaria cuando el repositorio de 2024 las recogía también ahí
REPO_P = {"chatterpix","stopmotion","suno","canva","genially","padlet","vocaroo","bookcreator","codeorg","blockly","classdojo",
          "nearpod","badge","educaplay","exelearning","kahoot","plickers","edpuzzle","loom","scratch","phet","gizmos","geogebra","classroomscreen","fastboard"}
REPO_I = {"chatterpix","codeorg","educaplay","kahoot","plickers"}
def etapas(t):
    if t["s"] != "aula": return ["I", "P", "S"]  # herramientas del docente y recursos: para el profesorado de cualquier etapa
    i = t["id"]; return [e for e, ok in (("I", i in REPO_I), ("P", i in REPO_P), ("S", True)) if ok]
ETN = {"I": "Infantil", "P": "Primaria", "S": "Secundaria y Bachillerato"}
for t in TOOLS:
    t["cs"], t["sub"] = place(t); t["et"] = etapas(t)
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
def card_dest(t, txt=None):
    """tarjeta compacta de las destacadas y las nuevas: texto corto, categoría a la izquierda y solo la flecha"""
    nm, alias = split_name(t["n"]); c = CAT[t["cs"]]
    return (f'<article class="tc td"><div class="tc-h"><span class="lg">{logo(t)}</span><h3><a class="tc-a" href="{B}/{t["id"]}/">{esc(nm)}</a>'
            f'{f"<small>{esc(alias)}</small>" if alias else ""}</h3></div><p>{esc(txt or DEST_TXT[t["id"]])}</p>'
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
    x = re.sub(r"<title>.*?</title>", "", x).replace(' role="img" aria-label="didákora"',' aria-hidden="true" focusable="false"')
    return x.replace("<svg ", f'<svg class="{cls}" ', 1)
LOGO = _svg_inline("didakora-logo-a.svg", "lockup")
# la caja del logo del menú va en su propio grupo para poder animarla al pulsar
_i = LOGO.index(">", LOGO.index("<g ")) + 1; _j = LOGO.index("</g>", _i)
LOGO = LOGO[:_i] + '<g class="caja">' + LOGO[_i:_j] + "</g>" + LOGO[_j:]
def topbar(cur=""):
    nav = [("todas", "Todas", "/todas/"), ("categorias", "Categorías", "/categorias/"), ("nuevas", "Nuevas", "/nuevas/")]  # «Destacadas» fuera del menú (Jorge, 22-10-2026)
    if POSTS: nav.append(("actualidad", "Actualidad", "/actualidad/"))  # solo cuando ya hay algún post
    nav.append(("sobre", "Sobre mí", "/sobre-mi/"))
    links = "".join(f'<a href="{B}{h}"' + (' class="cta"' if k == "sobre" else "") + (' aria-current="page"' if k == cur else "") + f'>{t}</a>' for k, t, h in nav)
    return f'''<header class="top">
 <div class="bar">
  <a class="brand" href="{B}/" aria-label="didákora · inicio">{LOGO}</a>
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
CONTACTO = [
 ("mail", "Correo", "jorgedelagui@gmail.com", "mailto:jorgedelagui@gmail.com"),
 ("in", "LinkedIn", "jorgedelgadoaguilera", "https://www.linkedin.com/in/jorgedelgadoaguilera"),
 ("ig", "Instagram", "@pasadoproximo · divulgación histórica", "https://www.instagram.com/pasadoproximo/"),
]
# iconos de contacto dibujados en el mismo cuadro (de 3 a 21) para que se vean del mismo tamaño
CICO = {"mail": '<rect x="3" y="4" width="18" height="16" rx="3.5"/><path d="m4 7 8 6.5 8-6.5"/>',
        "in": '<rect x="3" y="3" width="18" height="18" rx="4.5"/><path d="M8 10.5V16.5M8 7.6v.1M11.8 16.5v-6M11.8 13.2c0-1.7 1.1-2.8 2.5-2.8s2.3 1 2.3 2.8v3.3"/>',
        "ig": '<rect x="3" y="3" width="18" height="18" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><path d="M17.3 6.7v.1"/>'}
def foot(scripts=""):
    """bloque final de todas las páginas: invitación a proponer herramientas, centrada, con los contactos debajo"""
    cont = "".join(f'<a href="{u}"' + ("" if u.startswith("mailto:") else ' rel="noopener" target="_blank"') +
                   f' aria-label="{t}" title="{t}"><svg viewBox="0 0 24 24" aria-hidden="true">{CICO[k]}</svg></a>' for k, t, d, u in CONTACTO)
    return f'''
<aside class="fin" id="contacto" aria-labelledby="h-inv">
 <h2 id="h-inv">¿Echas en falta una herramienta?</h2><p>Propónmela y la reviso con los mismos criterios.</p>
 <nav class="fin-c" aria-label="Contacto">{cont}</nav>
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
    return (f'<a class="cc" href="{B}/categorias/{c[0]}/"><b>{esc(c[1])}</b><span class="cc-d">{esc(CORTO[c[0]])}</span>'
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
    body = f'''
<main>
 <section class="hero" aria-labelledby="ph1">
  <div class="hero-t">
   <span class="lab">Herramientas digitales para docentes</span>
   <h1 id="ph1">La herramienta que <span>necesitas</span> para tu clase</h1>
   <p class="hero-d">Descubre apps, plataformas y recursos para planificar clases, evaluar, crear actividades, gamificar y atender la diversidad. Todos revisados uno a uno, con una ficha que explica qué son, para qué sirven y qué necesitan.</p>
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
  <p class="more"><a class="btn solid" href="{B}/categorias/">Ver categorías {ICO["arrow"]}</a></p>
 </section>

{seccion_nuevas()}
{seccion_actualidad()}
</main>'''
    write("index.html", head("didákora · Herramientas digitales para docentes",
        f"{len(TOOLS)} herramientas digitales para docentes, revisadas en octubre de 2026, con una ficha que explica qué es cada una, para qué sirve y qué necesita.", "/") + body + foot())

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
    write("todas/index.html", head("Todas las herramientas · didákora", "Todas las herramientas de didákora, con buscador y filtros por categoría y etapa.", "/todas/", "todas")
          + body + foot(f'\n<script src="{B}/tools.js?v={V}"></script>\n<script src="{B}/didakora-datos.js?v={V}"></script>\n<script>cajaListado()</script>'))

# ---------------------------------------------------------------- sobre mí
def sobremi():
    body = f'''
<main class="pg">
 <section class="me">
  <img src="{B}/img/jorge.jpg" alt="Jorge Delgado Aguilera en un aula, con una estantería de libros y un mapamundi al fondo" width="720" height="734">
  <div>
   <div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Sobre mí", "")])}<h1>Sobre mí</h1></div>
   <p>Soy Jorge Delgado Aguilera, profesor de Geografía e Historia y diseñador de materiales educativos digitales. didákora es la actualización del repositorio digital que creé en 2024 para el Colegio Cerrado de Calderón, que el centro presentó en el IX Congreso Internacional de Creatividad Educativa (Braining, Valencia, 2025).</p>
   <p>Cada herramienta se comprueba a mano: que funcione hoy, para qué tarea de clase sirve, si se puede empezar gratis, si pide cuenta y, cuando sus condiciones lo indican, qué edad mínima exige. Si una cierra o cambia de nombre, lo anoto y propongo una alternativa.</p>
   <p class="more"><a class="btn solid" href="{SITE}/" rel="noopener" target="_blank">Visita mi portfolio {ICO["ext"]}</a><a class="btn line" href="{SITE}/proyectos/repositorio-digital/" rel="noopener" target="_blank">Cómo hice didákora {ICO["ext"]}</a></p>
  </div>
 </section>
</main>'''
    write("sobre-mi/index.html", head("Sobre mí · didákora", "Quién hace didákora: Jorge Delgado Aguilera, profesor de Geografía e Historia y diseñador de materiales educativos digitales.", "/sobre-mi/", "sobre") + body + foot())

# ---------------------------------------------------------------- destacadas
def destacadas():
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Herramientas destacadas", "")])}<h1>Herramientas destacadas</h1></div><p>Las {len(DESTACADAS)} más versátiles para empezar a usar en clase.</p></div>
 <div class="tcg c4">{"".join(card_dest(BYID[i]) for i in DESTACADAS)}</div>
 <p class="more"><a class="btn solid" href="{B}/todas/">Ver todas las herramientas {ICO["arrow"]}</a></p>
</main>'''
    write("destacadas/index.html", head("Herramientas destacadas · didákora", f"Las {len(DESTACADAS)} herramientas más versátiles de didákora para empezar a usar en clase.", "/destacadas/", "destacadas") + body + foot())

# ---------------------------------------------------------------- nuevas (las últimas añadidas)
def nuevas_lista(): return [(BYID[x["id"]], x["txt"]) for x in RECIENTES if x["id"] in BYID]
def seccion_nuevas():
    ns = nuevas_lista()
    if not ns: return ""
    return f'''
 <section class="sec" aria-labelledby="h-nuevas">
  {secth("", "Añadidas recientemente", "Las últimas herramientas que han entrado en el catálogo.", "h-nuevas")}
  <div class="tcg c4">{"".join(card_dest(t, x) for t, x in ns[:4])}</div>
  <p class="more"><a class="btn solid" href="{B}/nuevas/">Ver nuevas {ICO["arrow"]}</a></p>
 </section>
'''
def nuevas():
    ns = nuevas_lista()
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Herramientas nuevas", "")])}<h1>Herramientas nuevas</h1></div><p>Las últimas {len(ns)} que han entrado en el catálogo, de la más reciente a la más antigua.</p></div>
 <div class="tcg c4">{"".join(card_dest(t, x) for t, x in ns)}</div>
 <p class="more"><a class="btn solid" href="{B}/todas/">Ver todas las herramientas {ICO["arrow"]}</a></p>
</main>'''
    write("nuevas/index.html", head("Herramientas nuevas · didákora", f"Las últimas herramientas digitales para docentes añadidas a didákora.", "/nuevas/", "nuevas") + body + foot())

# ---------------------------------------------------------------- categorías
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower().translate(str.maketrans("áéíóúñü", "aeiounu"))).strip("-")
def categorias():
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Categorías", "")])}<h1>Categorías</h1></div><p>Diez categorías según para qué sirve cada herramienta.</p></div>
 <div class="ccg">{"".join(catcard(c) for c in CATS)}</div>
</main>'''
    write("categorias/index.html", head("Categorías · didákora", "Las diez categorías de didákora, según para qué sirve cada herramienta.", "/categorias/", "categorias") + body + foot())
    for c in CATS:
        ts = [t for t in TOOLS if t["cs"] == c[0]]
        subs = []
        for t in ts:
            if t["sub"] not in subs: subs.append(t["sub"])
        nav = "".join(f'<a href="#{slug(s)}">{esc(s)} <span>{sum(1 for t in ts if t["sub"] == s)}</span></a>' for s in subs) if len(subs) > 1 else ""
        blocks = "".join(f'<section class="sub" aria-labelledby="{slug(s)}"><h2 id="{slug(s)}">{esc(s)} <span>{sum(1 for t in ts if t["sub"] == s)}</span></h2><div class="tcg">{"".join(card(t, False) for t in ts if t["sub"] == s)}</div></section>' for s in subs)
        others = "".join(f'<a href="{B}/categorias/{o[0]}/">{esc(o[1])}</a>' for o in CATS if o[0] != c[0])
        body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Categorías", f"{B}/categorias/"), (c[1], "")])}<h1>{esc(c[1])}</h1></div><p>{esc(c[2])} {len(ts)} herramientas.</p></div>
 {f'<nav class="subnav" aria-label="Apartados">{nav}</nav>' if nav else ""}
 {blocks}
 <section class="sec others" aria-labelledby="h-otras"><h2 id="h-otras">Otras categorías</h2><div class="oc">{others}</div></section>
</main>'''
        write(f"categorias/{c[0]}/index.html", head(f"{c[1]} · didákora", f"{c[2]} {len(ts)} herramientas revisadas en octubre de 2026.", f"/categorias/{c[0]}/", "categorias") + body + foot())

# ---------------------------------------------------------------- fichas
from fichas import F   # «Qué es», usos y (para docente y recursos) dispositivos y cuenta
faltan = [t["id"] for t in TOOLS if t["id"] not in F]
assert not faltan, f"Faltan fichas en _build/fichas.py: {faltan}"
OWN = re.compile(r"^no necesita|código|codigo|del docente|del centro|enlace del docente|integrado|extensión|solo para guardar|clase del docente", re.I)
def uses_ai(t):
    a = (t.get("a") or "").lower(); a = a.translate(str.maketrans("áéíóú", "aeiou"))
    # Code.org solo habla de la IA en sus cursos: el alumnado no conversa con una IA
    return t["s"] == "aula" and t["id"] != "codeorg" and re.search(r"(^|[^a-z])ia([^a-z]|$)", a) is not None
REV = "2026-10"  # revisión general del catálogo (cabecera de tools.js)
MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()
def revisada(rev):
    a, m = rev.split("-"); return f"{MESES[int(m) - 1].capitalize()} de {a}"
def ficha(t):
    nm, alias = split_name(t["n"]); c = CAT[t["cs"]]; aula = t["s"] == "aula"; f = F[t["id"]]
    disp = t["disp"] if aula else f["disp"]; cta = t["cta"] if aula else f["cta"]
    # debajo de la cuenta, en pequeño: edad mínima (solo con fuente oficial) y avisos de privacidad
    notas = []
    if t.get("edad"): notas.append(f'Edad mínima: {esc(t["edadTxt"])} · <a href="{esc(t["edadUrl"])}" rel="noopener" target="_blank">condiciones</a>')
    elif aula and not OWN.search(t["cta"]) and not t.get("intef"): notas.append("Consulta la edad mínima en sus condiciones antes de crear cuentas.")
    if uses_ai(t): notas.append("Trabaja con IA: no introduzcas datos personales.")
    # aviso de la guía de protección de datos del INTEF: punto rojo y explicación corta (intef: "rojo" o "ver")
    if t.get("intef"): notas.insert(0, '<span class="intef"><i aria-hidden="true"></i><b>En rojo en la guía del INTEF</b>: no la recomienda para el alumnado'
                                    + ('; puede ver lo que crea el docente sin registrarse' if t["intef"] == "ver" else '') + '.</span>')
    if t.get("datos") and not re.match(r"(con|trabaja con|usa) la cuenta del centro", t["datos"], re.I): notas.append(esc(t["datos"]) + ".")
    et = " · ".join(ETN[e] for e in t["et"])
    rows = [("Categoría", f'<a class="tag" href="{B}/categorias/{c[0]}/">{icon(c[3])}{esc(c[1])}</a>'),
            ("Etapa", et + (f'<small>Recomendada: {esc(t["c"])}</small>' if aula and t["c"] != "Toda la etapa" else "")),
            ("Dispositivos", esc(disp)),
            # con aviso del INTEF, la cuenta va en pequeño como las notas, y el aviso justo debajo
            ("Cuenta", (f"<small>{esc(cta)}.</small>" if t.get("intef") else esc(cta)) + "".join(f"<small>{n}</small>" for n in notas)),
            # última revisión de la ficha: `rev` («AAAA-MM») en tools.js; sin él, la revisión general del catálogo
            ("Revisada", revisada(t.get("rev", REV)))]
    dl = "".join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in rows)
    usos = "".join(f'<li>{ICO["check"]}<span>{esc(u)}</span></li>' for u in f["usos"])
    # alternativas en rueda: las siguientes del mismo apartado (y luego de la categoría), así toda herramienta
    # aparece como alternativa en alguna ficha y no salen siempre las mismas tres
    def ring(group):
        i = group.index(t); return [group[(i + k) % len(group)] for k in range(1, len(group))]
    same = ring([o for o in TOOLS if o["sub"] == t["sub"] and o["cs"] == t["cs"]])
    alts = (same + [o for o in ring([o for o in TOOLS if o["cs"] == t["cs"]]) if o not in same])[:3]
    body = f'''
<main class="pg">
 <section class="fh">
  {crumbs([("Inicio", f"{B}/"), (c[1], f"{B}/categorias/{c[0]}/"), (nm, "")])}
  <span class="lg xl">{logo(t, 44)}</span>
  <h1>{esc(nm)}{f" <small>{esc(alias)}</small>" if alias else ""}</h1>
 </section>
 <div class="fg">
  <section class="fb fq"><h2>Qué es {esc(nm)}</h2><p>{esc(f["q"])}</p></section>
  <aside class="fb fa"><h2>Ficha rápida</h2><dl>{dl}</dl></aside>
  <section class="fb fu" aria-label="Para qué lo puedes usar"><ul>{usos}</ul></section>
 </div>
 <p class="go"><a class="btn solid" href="{esc(t["url"])}" rel="noopener" target="_blank">Ir a {esc(nm)} {ICO["ext"]}</a></p>
 <section class="sec alt" aria-labelledby="h-alt"><h2 id="h-alt">Herramientas alternativas</h2><div class="tcg">{"".join(card(o) for o in alts)}</div>
  <p class="more"><a class="btn solid" href="{B}/categorias/{c[0]}/">Ver todo {esc(c[1])} {ICO["arrow"]}</a></p></section>
</main>'''
    write(f'{t["id"]}/index.html', head(f"{nm} · didákora", f["q"].split(". ")[0].rstrip(".") + ".", f'/{t["id"]}/') + body + foot())


# ---------------------------------------------------------------- actualidad (blog)
# Cada post es un JSON (_build/actualidad/<slug>.json) que deja el Maquetador cuando Jorge aprueba el diseño:
#   slug, titulo, fecha (AAAA-MM-DD), entradilla, etiqueta (tema, opcional), portada {src, alt, credito, url_credito} | null
#   (21:9, cabecera del post), miniatura {src} (16:9, tarjetas; las dos salen de _build/miniatura.py),
#   bloques: las secciones del artículo, en orden [{tipo: texto | destacado | lista | pasos | oficial | video | imagen | cita, …}],
#   fuentes: [{nombre, url}]
# Se lee de corrido, como un artículo de blog: las secciones no van en tarjetas sueltas. Las imágenes van junto a la
# página (actualidad/<slug>/img/…) y se citan en relativo («img/portada.jpg»).
# En los textos solo vale **negrita**, [texto](https://…) y párrafos separados por una línea en blanco.
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
TONOS = ("cielo", "coral", "hielo")
def fecha_larga(f):
    a, m, d = (int(x) for x in f[:10].split("-")); return f"{d} de {MESES[m - 1]} de {a}"
def bt_inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", lambda m: f'<a href="{m.group(2)}" rel="noopener" target="_blank">{m.group(1)}</a>', s)
def bt_parrafos(s): return "".join(f"<p>{bt_inline(p.strip())}</p>" for p in re.split(r"\n\s*\n", str(s or "")) if p.strip())
def bt_plano(s): return re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", str(s or "")).replace("**", "")
def post_slug(p): return p.get("slug") or slug(p["titulo"])
def bt_fuente(f): return f'<p class="pa-fu">Fuente: <a href="{esc(f["url"])}" rel="noopener" target="_blank">{esc(f["nombre"])}</a></p>' if f else ""
def bt_enlace(e): return f'<p class="pa-go"><a class="btn solid" href="{esc(e["url"])}" rel="noopener" target="_blank">{esc(e["texto"])} {ICO["ext"]}</a></p>' if e else ""
def bt_img(i, cls="pa-img"):
    if not i or not i.get("src"): return ""
    cred = esc(i.get("credito", ""))
    if cred and i.get("url_credito"): cred = f'<a href="{esc(i["url_credito"])}" rel="noopener" target="_blank">{cred}</a>'
    pie = " · ".join(x for x in (esc(i.get("pie", "")), cred) if x)
    return f'<figure class="{cls}"><img src="{esc(i["src"])}" alt="{esc(i.get("alt", ""))}" loading="lazy">{f"<figcaption>{pie}</figcaption>" if pie else ""}</figure>'
def bt_cab(b, kicker=""):
    k = kicker or (esc(b["etiqueta"]) if b.get("etiqueta") else "")
    return (f'<span class="pa-k">{k}</span>' if k else "") + (f'<h2>{esc(b["titulo"])}</h2>' if b.get("titulo") else "")
def bt_item(it, con_logo=True):
    # el logo sustituye al número solo si todos los elementos de la lista son herramientas del catálogo;
    # si se mezclan, todos llevan su número (el enlace a la ficha se mantiene)
    t = BYID.get(it.get("ficha") or "")
    lg = f'<span class="lg">{logo(t)}</span>' if t and con_logo else '<span class="pa-n" aria-hidden="true"></span>'
    nombre = esc(it["titulo"])
    if it.get("url"): nombre = f'<a href="{esc(it["url"])}" rel="noopener" target="_blank">{nombre}</a>'
    fl = f' <a class="pa-ficha" href="{B}/{t["id"]}/">Ver su ficha en didákora {ICO["arrow"]}</a>' if t else ""
    return f'<li>{lg}<div><h3>{nombre}</h3>{bt_parrafos(it.get("texto"))}{f"<p>{fl.strip()}</p>" if fl else ""}</div></li>'
def seccion_post(b):
    k = b["tipo"]; caja = f' pa-caja t-{b["tono"]}' if b.get("tono") in TONOS else ""
    if k == "texto": return f'<section class="pa-s{caja}">{bt_cab(b)}{bt_parrafos(b.get("texto"))}{bt_fuente(b.get("fuente"))}</section>'
    if k == "destacado":
        return (f'<section class="pa-s pa-dest{caja}">{bt_cab(b)}{bt_parrafos(b.get("texto"))}{bt_img(b.get("img"))}'
                f'{bt_enlace(b.get("enlace"))}{bt_fuente(b.get("fuente"))}</section>')
    if k == "oficial":
        k2 = esc(b.get("ambito", "Oficial")) + (f' · {esc(fecha_larga(b["fecha"]))}' if b.get("fecha") else "")
        return f'<section class="pa-s pa-of{caja}">{bt_cab(b, k2)}{bt_parrafos(b.get("texto"))}{bt_enlace(b.get("enlace"))}{bt_fuente(b.get("fuente"))}</section>'
    if k == "lista":
        its = b.get("items", []); cl = bool(its) and all(BYID.get(i.get("ficha") or "") for i in its)
        return (f'<section class="pa-s{caja}">{bt_cab(b)}{bt_parrafos(b.get("intro"))}<ol class="pa-lista">{"".join(bt_item(i, cl) for i in its)}</ol>'
                f'{bt_fuente(b.get("fuente"))}</section>')
    if k == "pasos":
        ej = f'<div class="pa-ej"><span class="lab">Ejemplo</span><p>{bt_inline(b["ejemplo"])}</p></div>' if b.get("ejemplo") else ""
        return (f'<section class="pa-s{caja}">{bt_cab(b)}{bt_parrafos(b.get("intro"))}<ol class="pa-pasos">'
                + "".join(f'<li><h3>{esc(p["titulo"])}</h3>{bt_parrafos(p.get("texto"))}</li>' for p in b.get("pasos", []))
                + f'</ol>{ej}{bt_fuente(b.get("fuente"))}</section>')
    if k == "video":  # sin reproductor incrustado: un enlace al vídeo (así didákora no carga cookies de terceros)
        meta = " · ".join(esc(x) for x in (b.get("canal"), b.get("duracion")) if x)
        return (f'<section class="pa-s">{bt_cab({"etiqueta": b.get("etiqueta")})}<a class="pa-v" href="{esc(b["url"])}" rel="noopener" target="_blank"><span class="pa-play">{ICO["play"]}</span>'
                f'<span><b>{esc(b["titulo"])}</b>{f"<small>{meta}</small>" if meta else ""}</span></a>{bt_parrafos(b.get("texto"))}</section>')
    if k == "imagen": return bt_img(b.get("img"), "pa-img ancha")
    if k == "cita":
        au = esc(b.get("autor", ""))
        if au and b.get("url"): au = f'<a href="{esc(b["url"])}" rel="noopener" target="_blank">{au}</a>'
        return f'<blockquote class="pa-cita"><p>{bt_inline(b["texto"])}</p>{f"<footer>{au}</footer>" if au else ""}</blockquote>'
    raise SystemExit(f"Actualidad: tipo de sección desconocido «{k}»")
def post_card(p, img_base=None):
    s = post_slug(p); base = img_base if img_base is not None else f"{B}/actualidad/{s}/"
    pt = p.get("miniatura") or p.get("portada") or {}  # la miniatura (16:9) hecha con _build/miniatura.py; si no, la portada
    img = f'<img src="{esc(base + pt["src"])}" alt="" loading="lazy">' if pt.get("src") else '<span class="pc-ph" aria-hidden="true"></span>'
    # en la miniatura: el tema arriba a la izquierda y la fecha, en pequeño, abajo a la derecha
    tema = f'<span class="pc-tema">{esc(p["etiqueta"])}</span>' if p.get("etiqueta") else ""
    return (f'<article class="tc pc"><div class="pc-img">{img}{tema}'
            f'<time class="pc-fecha" datetime="{esc(p["fecha"])}">{esc(fecha_larga(p["fecha"]))}</time></div>'
            f'<h3><a class="tc-a" href="{B}/actualidad/{s}/">{esc(p["titulo"])}</a></h3><p>{esc(bt_plano(p["entradilla"]))}</p></article>')
def portada_post(p):
    """cabecera del post: la portada (21:9) en pantallas anchas y la miniatura (16:9) en el móvil, para que no se corte el titular"""
    h = bt_img(p.get("portada"), "pa-img portada")
    mini = (p.get("miniatura") or {}).get("src")
    if h and mini: h = h.replace("<img ", f'<picture><source media="(max-width:640px)" srcset="{esc(mini)}"><img ', 1).replace('loading="lazy">', 'loading="lazy"></picture>', 1)
    return h
def pagina_post(p, path):
    s = post_slug(p)
    fu = "".join(f'<li><a href="{esc(f["url"])}" rel="noopener" target="_blank">{esc(f["nombre"])}</a></li>' for f in p.get("fuentes", []))
    otros = [x for x in reversed(POSTS) if post_slug(x) != s][:3]
    body = f'''
<main class="pg post">
 <div class="pa-volver">{crumbs([("Inicio", f"{B}/"), ("Actualidad", f"{B}/actualidad/"), (p["titulo"], "")])}</div>
 <header class="pa-h">
  <h1>{esc(p["titulo"])}</h1>
  <span class="lab">{f"{esc(p['etiqueta'])} · " if p.get("etiqueta") else ""}<time datetime="{esc(p["fecha"])}">{esc(fecha_larga(p["fecha"]))}</time></span>
  <p class="pa-lead">{bt_inline(p["entradilla"])}</p></header>
 {portada_post(p)}
 <article class="pa">{"".join(seccion_post(x) for x in p["bloques"])}
  {f'<footer class="pa-fuentes"><h2>Fuentes</h2><ul>{fu}</ul></footer>' if fu else ""}</article>
 {f'<section class="sec" aria-labelledby="h-mas">{secth("", "Más actualidad", "", "h-mas")}<div class="pcg">{"".join(post_card(x) for x in otros)}</div></section>' if otros else ""}
 <p class="more"><a class="btn solid" href="{B}/actualidad/">Toda la actualidad {ICO["arrow"]}</a><a class="btn line" href="{B}/todas/">Ver las herramientas {ICO["arrow"]}</a></p>
</main>'''
    # el texto de los posts va en Literata (letra de lectura en pantalla); los títulos, en la de la marca
    lectura = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap">\n'
    return head(f'{p["titulo"]} · didákora', bt_plano(p["entradilla"])[:155], path, "actualidad").replace("</head>", lectura + "</head>", 1) + body + foot()
def seccion_actualidad():
    if not POSTS: return ""
    return f'''
 <section class="sec" aria-labelledby="h-act">
  {secth("", "Actualidad", "Noticias de educación digital, con lo que te sirve para clase.", "h-act")}
  <div class="pcg">{"".join(post_card(p) for p in list(reversed(POSTS))[:3])}</div>
  <p class="more"><a class="btn solid" href="{B}/actualidad/">Ver toda la actualidad {ICO["arrow"]}</a></p>
 </section>
'''
def actualidad():
    if not POSTS: return
    for p in POSTS: write(f"actualidad/{post_slug(p)}/index.html", pagina_post(p, f"/actualidad/{post_slug(p)}/"))
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Actualidad", "")])}<h1>Actualidad</h1></div><p>Noticias de educación digital: herramientas, inteligencia artificial, lo que publican el Ministerio y la Junta de Andalucía e ideas para aprovecharlo en clase.</p></div>
 <div class="pcg">{"".join(post_card(p) for p in reversed(POSTS))}</div>
</main>'''
    write("actualidad/index.html", head("Actualidad · didákora", "Noticias de educación digital para docentes: herramientas, IA, recomendaciones oficiales e ideas para clase.", "/actualidad/", "actualidad") + body + foot())
def vista(ruta_json, carpeta):
    """vista previa de un post sin publicarlo: escribe <carpeta>/index.html (dentro del repo, por ejemplo en agentes/)"""
    p = json.load(open(ruta_json, encoding="utf-8"))
    rel = os.path.relpath(os.path.abspath(carpeta), H).replace(os.sep, "/")
    write(f"{rel}/index.html", pagina_post(p, f"/{rel}/").replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1))
    print("vista previa:", f"{rel}/index.html")

# ---------------------------------------------------------------- datos para el listado
def extras():
    """página de error 404 (GitHub Pages la sirve sola) y mapa del sitio (robots.txt solo cuenta en la raíz del dominio)"""
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Página no encontrada", "")])}<h1>Esta página no existe</h1></div><p>Puede que el enlace esté mal escrito o que la herramienta haya cambiado de dirección. Búscala desde aquí.</p></div>
 <form class="ls" action="{B}/todas/" method="get" role="search"><div class="hs-r"><div class="hs-q">{ICO["search"]}<label class="sr" for="eq">Busca una herramienta</label><input id="eq" name="q" type="text" placeholder="Busca por nombre o por lo que necesitas hacer…" autocomplete="off" enterkeyhint="search"></div></div></form>
 <p class="more"><a class="btn solid" href="{B}/">Ir al inicio {ICO["arrow"]}</a><a class="btn line" href="{B}/todas/">Ver todas las herramientas {ICO["arrow"]}</a></p>
</main>'''
    write("404.html", head("Página no encontrada · didákora", "Esta página no existe en didákora.", "/404.html") + body + foot())
    urls = ["/", "/todas/", "/destacadas/", "/nuevas/", "/categorias/", "/sobre-mi/"] + [f"/categorias/{c[0]}/" for c in CATS] + [f'/{t["id"]}/' for t in TOOLS]
    if POSTS: urls += ["/actualidad/"] + [f"/actualidad/{post_slug(p)}/" for p in POSTS]
    NL = "\n"
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>' + NL + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + NL
          + "".join(f"<url><loc>{SITE}{B}{u}</loc></url>{NL}" for u in urls) + "</urlset>" + NL)

def datos():
    from fichas import F
    # también van los textos de la ficha («Qué es» y usos) para que el buscador los encuentre
    m = {t["id"]: [t["cs"], t["et"], 1 if t["id"] in LOGOS else 0, t["sub"], " ".join(F[t["id"]]["usos"]) + " " + F[t["id"]]["q"]] for t in TOOLS}
    cats = {c[0]: [c[1], IC[c[3]]] for c in CATS}
    write("didakora-datos.js", "// Generado por _build/build.py: categoría, etapas, logo, apartado y textos de la ficha de cada herramienta\nconst CAJA=" + json.dumps({"cats": cats, "t": m}, ensure_ascii=False) + ";\n")

if __name__ == "__main__":
    if "--vista" in sys.argv:
        i = sys.argv.index("--vista"); vista(sys.argv[i + 1], sys.argv[i + 2]); sys.exit()
    shutil.copyfile(os.path.join(ROOT, "_build", "didakora.css"), os.path.join(H, "didakora.css"))
    shutil.copyfile(os.path.join(ROOT, "_build", "didakora.js"), os.path.join(H, "didakora.js"))
    datos(); portada(); todas(); destacadas(); nuevas(); categorias(); sobremi(); extras(); actualidad()
    for t in TOOLS: ficha(t)
    print("didakora:", len(TOOLS), "fichas,", len(CATS), "categorías")
