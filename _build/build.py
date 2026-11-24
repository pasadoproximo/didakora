# Genera Didákora (antes «Caja de herramientas digitales» del portfolio) en varias páginas:
#   /                      portada: buscador, categorías, añadidas recientemente y actualidad
#   /todas/                listado completo con buscador y filtros (JS)
#   /destacadas/           las diez más versátiles (ya sin enlace en el menú ni en la portada)
#   /nuevas/               las últimas añadidas (RECIENTES en tools.js)
#   /categorias/           índice de categorías y /categorias/<slug>/ con sus apartados
#   /<id>/                 una ficha por herramienta
#   /actualidad/           el blog de noticias de educación digital y /actualidad/<slug>/ cada post (_build/actualidad/)
# Dominio propio desde el 21-11-2026: https://didakora.es (archivo CNAME en la raíz). Las rutas cuelgan de B
#   ("" en el dominio; DK_BASE=/didakora solo si hubiera que volver a pasadoproximo.github.io/didakora/). Datos: tools.js. Logos de la marca: _build/marca.py → marca/.
# Uso: python _build/build.py
#      python _build/build.py --vista <post.json> <carpeta>   → solo la vista previa de un post (no toca la web)
import json, os, re, subprocess, html, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = ROOT
B = os.environ.get("DK_BASE", "").rstrip("/")  # base de todas las rutas
SITE = "https://pasadoproximo.github.io"  # el portfolio de Jorge
WEB = "https://didakora.es" if not B else SITE + B  # dirección pública de Didákora
# Contador de visitas de Jorge (GoatCounter, sin cookies; el mismo que el portfolio). No cuenta en local.
# Las visitas se apuntan como «didakora.es/ruta» para no mezclarse con las del portfolio, que tienen las mismas rutas («/»).
GOATCOUNTER = '<script>window.goatcounter={path:function(p){return location.host+p}}</script><script data-goatcounter="https://pasadoproximo.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
V = "79"  # versión de didakora.css / didakora.js

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
 ("explorar-por-materias", "Explorar por materias", "Herramientas propias de Geografía e Historia, Ciencias, Idiomas, Música y Arte o lectura.", "materias"),
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
         "colaborar-y-organizar": "Murales, mapas y pizarras", "explorar-por-materias": "Historia, Ciencias, Idiomas, Música…",
         "programacion-y-diseno-3d": "Bloques y diseño 3D", "inteligencia-artificial": "Asistentes para el aula",
         "evaluacion-y-seguimiento": "Formularios y rúbricas", "gestion-del-aula": "Rutinas, cuaderno y familias",
         "aulas-virtuales": "Classroom, Teams y Moodle", "bancos-de-recursos": "Recursos e imágenes libres"}
PROG = {"scratch","scratchjr","snap","blockly","codeorg","appinventor","thunkable","cospaces","coppelia","tinkercad","wokwi"}
LECT = {"immersive","languagetool","readwrite"}
SUITES = {"classroom","teams","moodle"}
def place(t):
    s, c, i = t["s"], t["cat"], t["id"]
    if i in PROG: return ("programacion-y-diseno-3d", "Programación y diseño 3D")
    if i in LECT: return ("explorar-por-materias", "Lectura y accesibilidad")
    if i in SUITES: return ("aulas-virtuales", "Aulas virtuales")
    return {("aula","part"):("participar-y-repasar","Cuestionarios y juegos"), ("aula","geohis"):("explorar-por-materias","Geografía e Historia"),
            ("aula","crear"):("crear-y-presentar","Lo crea el alumnado"), ("aula","equipo"):("colaborar-y-organizar","Trabajar en equipo"),
            ("aula","cienc"):("explorar-por-materias","Ciencias y Matemáticas"), ("aula","arte"):("explorar-por-materias","Música y Arte"), ("aula","idiomas"):("explorar-por-materias","Idiomas"),
            ("aula","ia"):("inteligencia-artificial","IA para el alumnado"), ("docente","ia"):("inteligencia-artificial","IA para preparar clase"),
            ("docente","crear"):("crear-y-presentar","Materiales del docente"), ("docente","gestion"):("gestion-del-aula","Gestión del aula"),
            ("docente","eval"):("evaluacion-y-seguimiento","Evaluar y motivar"), ("docente","org"):("colaborar-y-organizar","Organizar recursos"),
            ("recursos","sa"):("bancos-de-recursos","Situaciones de aprendizaje"), ("recursos","form"):("bancos-de-recursos","Formación e inspiración"),
            ("recursos","img"):("bancos-de-recursos","Imágenes y multimedia")}[(s, c)]
# etapas: Didákora es de Secundaria; Infantil y Primaria cuando el repositorio de 2024 las recogía también ahí
REPO_P = {"chatterpix","stopmotion","suno","canva","genially","padlet","vocaroo","bookcreator","codeorg","blockly","classdojo",
          "nearpod","badge","educaplay","exelearning","kahoot","plickers","edpuzzle","loom","scratch","phet","gizmos","geogebra","classroomscreen","fastboard"}
REPO_I = {"chatterpix","codeorg","educaplay","kahoot","plickers"}
# altas del 23-11-2026 para Infantil (edades de la web oficial de cada una); las de SOLO_IP no son de Secundaria
REPO_I |= {"gcompris","tuxpaint","musiclab","scratchjr"}; REPO_P |= {"gcompris","tuxpaint","musiclab","scratchjr"}
# revisión de etapas del 23-11-2026 (Jorge): sin cuenta del alumnado o dirigidas por el docente, sin edad mínima y sin aviso del INTEF
REPO_I |= {"lekids"}; REPO_P |= {"lekids","forvo","dicta"}   # altas de Idiomas del 23-11-2026 (LearnEnglish Kids: de 5 a 12 años según su web)
REPO_I |= {"wordwall","visitas","artsculture","earth","incredibox","stopmotion","bookcreator","vocaroo","padlet"}
REPO_P |= {"wordwall","visitas","artsculture","earth","incredibox","wayground","ancientearth","vertebrados","kgeography","tinkercad","cospaces","immersive"}
SOLO_IP = {"gcompris","tuxpaint","scratchjr","lekids"}
def etapas(t):
    if t["s"] != "aula": return ["I", "P", "S"]  # herramientas del docente y recursos: para el profesorado de cualquier etapa
    i = t["id"]; return [e for e, ok in (("I", i in REPO_I), ("P", i in REPO_P), ("S", i not in SOLO_IP)) if ok]
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
SES_PUB = os.environ.get("DK_SESION") != "0"   # «Monta tu sesión» en el menú y con bloque en la portada (Jorge, 23-11-2026); DK_SESION=0 la esconde
def topbar(cur=""):
    nav = [("todas", "Todas", "/todas/"), ("categorias", "Categorías", "/categorias/"), ("nuevas", "Nuevas", "/nuevas/")]  # «Destacadas» fuera del menú (Jorge, 22-10-2026)
    if SES_PUB: nav.append(("sesion", "Monta tu sesión", "/sesion/"))
    if POSTS: nav.append(("actualidad", "Actualidad", "/actualidad/"))  # solo cuando ya hay algún post
    nav.append(("sobre", "Sobre mí", "/sobre-mi/"))
    links = "".join(f'<a data-k="{k}" href="{B}{h}"' + (' class="cta"' if k == "sobre" else "") + (' aria-current="page"' if k == cur else "") + f'>{t}</a>'.replace('>Monta tu sesión<', '><span class="nl">Monta tu sesión</span><span class="ns">Sesión</span><') for k, t, h in nav)
    return f'''<header class="top">
 <div class="bar">
  <a class="brand" href="{B}/" aria-label="didákora · inicio">{LOGO}</a>
  <nav aria-label="Principal">{links}</nav>
 </div>
</header>'''
# datos estructurados (JSON-LD, schema.org): no se ven; ayudan a Google y a las IA a entender cada página.
# Todas llevan la web y a Jorge (con su @id) y, según la página, la ficha, la categoría, el post o las preguntas.
PERSONA = {"@type": "Person", "@id": f"{SITE}/#jorge", "name": "Jorge Delgado Aguilera", "url": f"{SITE}/",
           "jobTitle": "Profesor de Geografía e Historia y diseñador de materiales educativos digitales",
           "sameAs": ["https://www.linkedin.com/in/jorgedelgadoaguilera", "https://www.instagram.com/pasadoproximo/"]}
SITIO = {"@type": "WebSite", "@id": f"{WEB}/#web", "name": "Didákora", "url": f"{WEB}/", "inLanguage": "es",
         "description": "Catálogo de herramientas digitales para docentes revisado a mano.", "publisher": {"@id": PERSONA["@id"]}}
def ld_html(nodos):
    if not nodos: return ""
    g = json.dumps({"@context": "https://schema.org", "@graph": [SITIO, PERSONA] + nodos}, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{g}</script>\n'
def titulo_ficha(nm):
    # título para buscadores: lo que buscan los docentes («qué es», «para qué sirve en clase»); sin «!:» en Kahoot!
    return f'{nm}{" " if nm.endswith(("!", "?")) else ": "}{"Q" if nm.endswith(("!", "?")) else "q"}ué es y para qué sirve en clase · Didákora'

def migas(*pasos):
    """Migas de pan para buscadores (BreadcrumbList): pasos = (nombre, ruta); solo van en los datos estructurados, no se ven."""
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": f"{WEB}{r}"} for i, (n, r) in enumerate(pasos)]}
def head(title, desc, path, cur="", ld=None, img=None, img_alt="", tipo="website"):
    # img: imagen al compartir (dirección completa); sin ella, la general de la marca. Las de las fichas: _build/og.py → og/<id>.png
    og_img = img or f"{WEB}/marca/og.png"; og_alt = img_alt or "Didákora: herramientas digitales para docentes, revisadas una a una"
    medidas = '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n' if not img or "/og/" in img else ""
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="google-site-verification" content="Yc7dog5FgiijAysig5OLHqYJhraIem9FlrTZtTM2qGk" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{WEB}{path}">
<meta property="og:site_name" content="Didákora">
<meta property="og:locale" content="es_ES">
<meta property="og:image" content="{esc(og_img)}">
{medidas}<meta property="og:image:alt" content="{esc(og_alt)}">
<meta property="og:type" content="{tipo}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{esc(og_img)}">
<meta name="robots" content="max-image-preview:large">
<link rel="canonical" href="{WEB}{path}">
{f'<link rel="alternate" type="application/rss+xml" title="Actualidad · Didákora" href="{WEB}/rss.xml">' + chr(10) if POSTS else ""}<link rel="icon" href="{B}/marca/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{B}/marca/icono-180.png">
<meta name="theme-color" content="#9FB3FF">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+SC:wght@700&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&display=swap">
<link rel="stylesheet" href="{B}/didakora.css?v={V}">
{GOATCOUNTER}
{ld_html(ld)}</head>
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
EN_PRUEBAS = set() if SES_PUB else {"sesion/index.html"}   # publicadas sin enlace y sin indexar hasta que Jorge las apruebe
def write(rel, content):
    if rel in EN_PRUEBAS: content = content.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
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
def bloque_sesion():
    """portada: entrada a «Monta tu sesión», con una sesión de ejemplo en pequeño"""
    pasos = [("voz", "Activa lo que ya saben", "Sin pantalla"), ("main", "La actividad de la clase", "Con una herramienta del catálogo"), ("", "Comprueba qué se llevan", "Un ticket de salida")]
    li = "".join(f'<li class="ps-p {c}"><span class="ps-n">{k}</span><span class="ps-t"><b>{esc(t)}</b><small>{esc(d)}</small></span></li>' for k, (c, t, d) in enumerate(pasos, 1))
    return f'''<section class="sec ps" aria-labelledby="h-ses">
  <div class="ps-a"><span class="lab">Nuevo</span><h2 id="h-ses">Monta tu sesión</h2>
   <p>Dime qué quieres hacer en clase, con qué etapa y con qué dispositivos. Te propongo los pasos justos, en su orden, con herramientas del catálogo.</p>
   <p class="more"><a class="btn solid" href="{B}/sesion/">Montar una sesión {ICO["arrow"]}</a></p></div>
  <ol class="ps-l" aria-label="Ejemplo de sesión">{li}</ol>
 </section>'''
def portada():
    body = f'''
<main>
 <section class="hero" aria-labelledby="ph1">
  <div class="hero-t">
   <span class="lab">Herramientas digitales para docentes</span>
   <h1 id="ph1">La herramienta que <span>necesitas</span> para tu clase</h1>
   {autoria()}
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
 {bloque_sesion() if SES_PUB else ""}
 {bloque_guias()}

{seccion_nuevas()}
{seccion_actualidad()}
</main>'''
    write("index.html", head("Didákora · Herramientas digitales para docentes",
        f"{len(TOOLS)} herramientas digitales para docentes, revisadas en {mes_revision()}, con una ficha que explica qué es cada una, para qué sirve y qué necesita.", "/", ld=[{**SITIO, "@id": f"{WEB}/#portada", "@type": "WebPage", "isPartOf": {"@id": SITIO["@id"]}, "potentialAction": {"@type": "SearchAction", "target": f"{WEB}/todas/?q={{search_term_string}}", "query-input": "required name=search_term_string"}}]) + body + foot())

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
    write("todas/index.html", head("Todas las herramientas · Didákora", "Todas las herramientas de Didákora, con buscador y filtros por categoría y etapa.", "/todas/", "todas")
          + body + foot(f'\n<script src="{B}/tools.js?v={V}"></script>\n<script src="{B}/didakora-datos.js?v={V}"></script>\n<script>cajaListado()</script>'))

# ---------------------------------------------------------------- sobre mí
def sobremi():
    body = f'''
<main class="pg">
 <section class="me">
  <img src="{B}/img/jorge.jpg" alt="Jorge Delgado Aguilera en un aula, con una estantería de libros y un mapamundi al fondo" width="720" height="734">
  <div>
   <div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Sobre mí", "")])}<h1>Sobre mí</h1></div>
   <p>Soy Jorge Delgado Aguilera, profesor de Geografía e Historia y diseñador de materiales educativos digitales. Didákora es la actualización del repositorio digital que creé en 2024 para el Colegio Cerrado de Calderón, que el centro presentó en el IX Congreso Internacional de Creatividad Educativa (Braining, Valencia, 2025).</p>
   <p>De cada herramienta compruebo para lo que sirve, si pide cuenta, edad mínima de uso y que funcione adecuadamente. Para estar al día me ayudo de un equipo de agentes de IA que vigila si alguna cierra o cambia de nombre y me propone qué actualizar. Compruebo la información que me dan y solo publico un cambio cuando lo he revisado.</p>
   <p class="more"><a class="btn solid" href="{SITE}/" rel="noopener" target="_blank">Visita mi portfolio {ICO["ext"]}</a><a class="btn line" href="{SITE}/proyectos/repositorio-digital/" rel="noopener" target="_blank">Cómo hice Didákora {ICO["ext"]}</a></p>
  </div>
 </section>
</main>'''
    write("sobre-mi/index.html", head("Sobre mí · Didákora", "Quién hace Didákora: Jorge Delgado Aguilera, profesor de Geografía e Historia y diseñador de materiales educativos digitales.", "/sobre-mi/", "sobre", ld=[{"@type": "ProfilePage", "url": f"{WEB}/sobre-mi/", "isPartOf": {"@id": SITIO["@id"]}, "mainEntity": {"@id": PERSONA["@id"]}}]) + body + foot())

# ---------------------------------------------------------------- destacadas
def destacadas():
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Herramientas destacadas", "")])}<h1>Herramientas destacadas</h1></div><p>Las {len(DESTACADAS)} más versátiles para empezar a usar en clase.</p></div>
 <div class="tcg c4">{"".join(card_dest(BYID[i]) for i in DESTACADAS)}</div>
 <p class="more"><a class="btn solid" href="{B}/todas/">Ver todas las herramientas {ICO["arrow"]}</a></p>
</main>'''
    write("destacadas/index.html", head("Herramientas destacadas · Didákora", f"Las {len(DESTACADAS)} herramientas más versátiles de Didákora para empezar a usar en clase.", "/destacadas/", "destacadas") + body + foot())

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
    write("nuevas/index.html", head("Herramientas nuevas · Didákora", f"Las últimas herramientas digitales para docentes añadidas a Didákora.", "/nuevas/", "nuevas") + body + foot())

# ---------------------------------------------------------------- categorías
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower().translate(str.maketrans("áéíóúñü", "aeiounu"))).strip("-")
def categorias():
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Categorías", "")])}<h1>Categorías</h1></div><p>Diez categorías según para qué sirve cada herramienta.</p></div>
 <div class="ccg">{"".join(catcard(c) for c in CATS)}</div>
</main>'''
    write("categorias/index.html", head("Categorías · Didákora", "Las diez categorías de Didákora, según para qué sirve cada herramienta.", "/categorias/", "categorias") + body + foot())
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
        write(f"categorias/{c[0]}/index.html", head(f"{c[1]} · Didákora", f"{c[2]} {len(ts)} herramientas revisadas en {mes_revision()}.", f"/categorias/{c[0]}/", "categorias", ld=[{"@type": "CollectionPage", "name": c[1], "url": f"{WEB}/categorias/{c[0]}/", "isPartOf": {"@id": SITIO["@id"]}, "mainEntity": {"@type": "ItemList", "numberOfItems": len(ts), "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{WEB}/{x['id']}/", "name": split_name(x["n"])[0]} for i, x in enumerate(ts)]}}, migas(("Inicio", "/"), ("Categorías", "/categorias/"), (c[1], f"/categorias/{c[0]}/"))]) + body + foot())

# ---------------------------------------------------------------- compartir (fila de iconos, como en los periódicos)
# Enlaces normales (funcionan sin JavaScript) y un botón que copia el enlace (`data-copia`, en didakora.js).
# Instagram no deja compartir un enlace desde una web: para eso está «Copiar enlace». Iconos de marca: Simple Icons (CC0).
RED = {
 "wa": ("WhatsApp", "https://wa.me/?text={tu}"),
 "tg": ("Telegram", "https://t.me/share/url?url={u}&text={t}"),
 "in": ("LinkedIn", "https://www.linkedin.com/sharing/share-offsite/?url={u}"),
 "x": ("X", "https://x.com/intent/post?url={u}&text={t}"),
 "fb": ("Facebook", "https://www.facebook.com/sharer/sharer.php?u={u}"),
}
RED_PATH = {'wa': 'M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z', 'tg': 'M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z', 'x': 'M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z', 'fb': 'M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z', 'in': 'M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z'}
def compartir(titulo, path, cls=""):
    from urllib.parse import quote
    url = f"{WEB}{path}"; u = quote(url, safe=""); t = quote(titulo, safe=""); tu = quote(f"{titulo} {url}", safe="")
    a = "".join(f'<a href="{esc(h.format(u=u, t=t, tu=tu))}" rel="noopener" target="_blank" aria-label="Compartir en {n}" title="{n}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{RED_PATH[k]}"/></svg></a>' for k, (n, h) in RED.items())
    a += f'<a href="mailto:?subject={t}&amp;body={tu}" aria-label="Enviar por correo" title="Correo"><svg class="ln" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/></svg></a>'
    a += f'<button type="button" data-copia="{esc(url)}" aria-label="Copiar enlace" title="Copiar enlace"><svg class="ln" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg></button>'
    return f'<div class="comp{" " + cls if cls else ""}"><span class="lab">Compartir</span><div class="comp-i">{a}</div><span class="comp-ok" role="status" aria-live="polite"></span></div>'

# ---------------------------------------------------------------- Monta tu sesión y Plan B (22-11-2026, EN PRUEBAS: sin enlace en el menú)
# Las dos salen solo de los datos de las herramientas del alumnado (Aula): sus ideas de actividad (`i`), dispositivos y cuenta.
# No inventan nada: si una combinación no tiene ideas, la página lo dice.
# Momento y objetivo de cada idea: `_build/sesion_ideas.py`, revisadas una a una; las reglas por palabras de aquí solo cubren una idea nueva.
M_INI = re.compile(r"ideas previas|abrir|al empezar|para empezar|motivar|lluvia de ideas|introduc", re.I)
M_FIN = re.compile(r"cerrar|cierre|repas|comprobar|examen|metacogn|evalua|ticket|resum|al final", re.I)
D_EQUIPO = re.compile(r"pareja|equipo|proyectad|del profesor", re.I)     # vale con un dispositivo por pareja o por equipo
D_PROFE = re.compile(r"proyectad|solo el móvil del profesor", re.I)       # vale solo con el del docente
# el alumnado no crea cuenta: entra con un código o un enlace, o la cuenta solo la necesita el docente («Cuenta del docente para crear»).
# «Cuenta Microsoft del centro» o «Cuenta de Google» cuentan como cuenta: sin ella no se puede usar.
SIN_REG = re.compile(r"^no necesita|^código|^entra con el enlace|^solo para guardar|sin correo|código sin cuenta|del docente|^integrado|^extensión", re.I)
MATERIA = {"Geografía e Historia": "gh", "Ciencias y Matemáticas": "cm", "Música y Arte": "ma", "Lectura y accesibilidad": "ll", "Idiomas": "id", "Programación y diseño 3D": "tp"}  # por apartado; el resto vale para cualquier materia
# Objetivo de cada idea («¿Qué quieres hacer?»): primero por palabras y, si no, por la categoría de su herramienta (provisional, como el momento)
O_PAL = [("rep", re.compile(r"repas|vocabulario|estudiar", re.I)), ("eva", re.compile(r"comprobar|evalua|examen|ticket|ideas previas|informe|autocorreg", re.I)),
         ("equ", re.compile(r"equipo|cooperat|colabor|debate|lluvia de ideas|entre todos|compartid", re.I))]
O_CAT = {"crear-y-presentar": "cre", "programacion-y-diseno-3d": "cre", "colaborar-y-organizar": "equ", "explorar-por-materias": "exp", "participar-y-repasar": "rep", "inteligencia-artificial": "exp"}
from sesion_ideas import SES   # el reparto bueno, idea a idea (23-11-2026); lo de arriba solo cubre una idea que aún no esté ahí
SES_M = {"I": "ini", "C": "des", "F": "fin", "X": None}; SES_O = {"E": "exp", "K": "cre", "Q": "equ", "R": "rep", "V": "eva"}
def objetivo(t, idea):
    c = SES.get(t["id"], {}).get(idea)
    return SES_O[c[1]] if c else next((k for k, r in O_PAL if r.search(idea)), O_CAT[t["cs"]])
def momento(idea, t=None):
    """ini, des o fin; None = la idea no sirve para montar una sesión (tarea para casa, función de la herramienta…)"""
    c = SES.get(t["id"], {}).get(idea) if t else None
    return SES_M[c[0]] if c else "ini" if M_INI.search(idea) else "fin" if M_FIN.search(idea) else "des"
def aula(): return [t for t in TOOLS if t["s"] == "aula"]
def sesion():
    """«Monta tu sesión»: un árbol de preguntas (didakora.js, dkSesion) que acaba en una receta de sesión con los pasos que le convienen.
    El árbol y las recetas están en _build/sesion_recetas.py; el reparto de las ideas, en _build/sesion_ideas.py."""
    from sesion_ideas import RAMA, ETAPA, EXTRA
    from sesion_recetas import RAMAS, METAS, RECETAS, FUENTES
    ideas = [{"t": t["id"], "n": split_name(t["n"])[0], "l": t["id"] in LOGOS, "i": i, "m": momento(i, t), "o": objetivo(t, i), "k": RAMA.get(t["id"], {}).get(i, ""),
              "e": "".join(t["et"]), "d": "p" if D_PROFE.search(t["disp"]) else "e" if D_EQUIPO.search(t["disp"]) else "a", "r": 0 if SIN_REG.search(t["cta"]) else 1,
              "s": MATERIA.get(t["sub"], ""), "x": 1 if t.get("intef") else 0, "dt": t["disp"], "ct": t["cta"]} for t in aula() for i in t["i"] if momento(i, t)]
    for x in ideas:   # etapas idea a idea: una idea pensada para Secundaria no sale en Infantil aunque la herramienta sí valga
        e = ETAPA.get(x["t"], {}).get(x["i"])
        if e is not None: x["e"] = "".join(c for c in x["e"] if c in e)
    porid = {t["id"]: t for t in aula()}
    for tid, ex in EXTRA.items():   # ideas solo de «Monta tu sesión» (no salen en la ficha): propuestas para las etapas sin idea propia
        t = porid[tid]; base = next((x for x in ideas if x["t"] == tid), None)
        for d in ex:
            ideas.append({"t": tid, "n": split_name(t["n"])[0], "l": tid in LOGOS, "i": d["i"], "m": SES_M[d["c"][0]], "o": {"E": "exp", "K": "cre", "Q": "equ", "R": "rep", "V": "eva"}[d["c"][1]],
                          "k": d.get("k", ""), "e": "".join(c for c in "".join(t["et"]) if c in d["e"]), "d": d.get("d") or ("p" if D_PROFE.search(t["disp"]) else "e" if D_EQUIPO.search(t["disp"]) else "a"),
                          "r": 0 if SIN_REG.search(t["cta"]) else 1, "s": MATERIA.get(t["sub"], ""), "x": 1 if t.get("intef") else 0, "dt": t["disp"], "ct": t["cta"]})
    ideas = [x for x in ideas if x["e"]]
    sin = [(t["id"], i) for t in aula() for i in t["i"] if i not in SES.get(t["id"], {})]
    if sin: print(f"· sesión: {len(sin)} ideas sin revisar en _build/sesion_ideas.py (repartidas por palabras): {sin[:3]}")
    textos = {x["i"] for x in ideas}
    for k, r in RECETAS.items():   # una idea citada en una receta que ya no exista (o esté marcada «no sirve») se avisa: el paso se quedaría sin ella
        for p in r["pasos"]:
            for i in p.get("ideas", []):
                if i not in textos: print(f"· sesión: la receta «{k}» cita una idea que no está: {i}")
    for o, (preg, ops) in RAMAS.items():   # cada opción del árbol tiene que llevar a alguna idea y a una receta
        for v, lab in ops:
            n = sum(1 for x in ideas if x["o"] == o and (x["s"] == v and x["m"] == "des" if o == "exp" else x["m"] == v if o == "eva" else x["k"] == v and x["m"] != "ini"))
            if not n: print(f"· sesión: la opción «{lab}» de «{preg}» no tiene ninguna idea")
            if f"{o}/{v}" not in RECETAS and o not in RECETAS: print(f"· sesión: falta la receta de «{o}/{v}»")
    fu = "".join(f'<li><a href="{esc(u)}" rel="noopener" target="_blank">{esc(n)}</a>: {esc(d)}.</li>' for n, u, d in FUENTES)
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Monta tu sesión", "")])}<h1>Monta tu sesión</h1></div><p>Contesta unas pocas preguntas y te propongo una clase con herramientas del catálogo: los pasos justos, en su orden.</p></div>
 <section class="ar" id="ar" aria-live="polite"></section>
 <section class="ar-r" id="ar-r" hidden></section>
 <noscript><p class="count">Esta página necesita JavaScript. Mientras tanto, tienes <a href="{B}/todas/">todas las herramientas</a>.</p></noscript>
 <aside class="ar-b" aria-labelledby="h-base"><h2 id="h-base">En qué se basa</h2>
  <p>Las ideas de actividad son las de cada ficha, repartidas una a una. El orden de los pasos sigue estos marcos:</p><ul>{fu}</ul>
  <p>No todos los pasos llevan pantalla: la tecnología va donde aporta algo.</p></aside>
</main>'''
    datos = {"ideas": ideas, "metas": METAS, "ramas": RAMAS, "recetas": RECETAS}
    datos_js = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    write("sesion/index.html", head("Monta tu sesión · Didákora", "Contesta unas preguntas (qué quieres hacer, con qué etapa y con qué dispositivos) y Didákora te propone una clase paso a paso con herramientas digitales.", "/sesion/")
          + body + foot(f'\n<script>window.dkS=dkSesion({datos_js})</script>'))

# ---------------------------------------------------------------- fichas
from fichas import F   # «Qué es», usos y (para docente y recursos) dispositivos y cuenta
faltan = [t["id"] for t in TOOLS if t["id"] not in F]
assert not faltan, f"Faltan fichas en _build/fichas.py: {faltan}"
OWN = re.compile(r"^no necesita|código|codigo|del docente|del centro|enlace del docente|integrado|extensión|solo para guardar|clase del docente", re.I)
def uses_ai(t):
    a = (t.get("a") or "").lower(); a = a.translate(str.maketrans("áéíóú", "aeiou"))
    # Code.org solo habla de la IA en sus cursos: el alumnado no conversa con una IA
    return t["s"] == "aula" and t["id"] != "codeorg" and re.search(r"(^|[^a-z])ia([^a-z]|$)", a) is not None
REV = "2026-10-23"  # revisión general del catálogo («AAAA-MM-DD»): solo para una herramienta sin `rev`
MESES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()
def revisada(rev):
    # «AAAA-MM-DD» → «23 de octubre de 2026» (la ficha); «AAAA-MM» → «Octubre de 2026»
    if len(rev) > 7: return fecha_larga(rev)
    a, m = rev.split("-"); return f"{MESES[int(m) - 1].capitalize()} de {a}"
def mes_revision():
    # mes de la última revisión del catálogo, «noviembre de 2026» (autoría y meta descripciones de portada y categorías)
    return revisada(max([REV] + [t.get("rev", REV) for t in TOOLS])[:7]).lower()
def autoria():
    # bajo el hero de la portada: quién revisa, cuántas herramientas hay y el mes de la última revisión (se calculan solos)
    return (f'<p class="hero-a"><img src="{B}/img/jorge.jpg" alt="" width="32" height="32">'
            f'<span>Revisado a mano por <a href="{SITE}/">Jorge Delgado Aguilera</a> · {len(TOOLS)} herramientas · '
            f'actualizado en {mes_revision()}</span></p>')
def saber_mas(f):
    # «Para saber más»: preguntas que no repiten la Ficha rápida (faq en fichas.py: p, r, url, fuente, fecha AAAA-MM-DD)
    if not f.get("faq"): return ""
    def una(i, x):
        a, m, d = x["fecha"].split("-")
        return (f'<details{" open" if i == 0 else ""}><summary>{esc(x["p"])}</summary><p>{esc(x["r"])}</p>'
                f'<p class="fq-fu">Fuente: <a href="{esc(x["url"])}" rel="noopener" target="_blank">{esc(x["fuente"])}</a>, comprobado el {d}/{m}/{a}.</p></details>')
    return (f'\n <section class="sec faq" aria-labelledby="h-faq">{secth("", "Para saber más", "Lo que suelen preguntar los docentes antes de usarla en clase.", "h-faq")}'
            f'<div class="faq-l">{"".join(una(i, x) for i, x in enumerate(f["faq"]))}</div></section>')
def fuente_q(f):
    # bajo «Qué es», lo que puede cambiar (nombre, cierre, precio) con su enlace oficial y el día en que se comprobó: fu en fichas.py
    fu = f.get("fu")
    if not fu: return ""
    a, m, d = fu["fecha"].split("-")
    return (f'<p class="fq-fu">{esc(fu["t"])} (<a href="{esc(fu["url"])}" rel="noopener" target="_blank">{esc(fu.get("enlace", "anuncio oficial"))}</a>, '
            f'comprobado el {d}/{m}/{a}). Si cambia, lo anoto aquí.</p>')
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
            # última revisión de la ficha: `rev` («AAAA-MM-DD») en tools.js; sin él, la revisión general del catálogo
            ("Revisada", revisada(t.get("rev", REV)))]
    dl = "".join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in rows)
    usos = "".join(f'<li>{ICO["check"]}<span>{esc(u)}</span></li>' for u in f["usos"])
    # alternativas en rueda: las siguientes del mismo apartado (y luego de la categoría), así toda herramienta
    # aparece como alternativa en alguna ficha y no salen siempre las mismas tres
    def ring(group):
        i = group.index(t); return [group[(i + k) % len(group)] for k in range(1, len(group))]
    same = ring([o for o in TOOLS if o["sub"] == t["sub"] and o["cs"] == t["cs"]])
    alts = (same + [o for o in ring([o for o in TOOLS if o["cs"] == t["cs"]]) if o not in same])[:3]
    from guias import ALTERNATIVAS as _ALT   # con página propia de alternativas, se enlaza; si no, al comparador con la primera
    alt_mas = (f'<a class="btn line" href="{B}/alternativas/{t["id"]}/">Cuándo elegir cada una {ICO["arrow"]}</a>' if t["id"] in _ALT
               else f'<a class="btn line" href="{B}/comparar/?c={t["id"]},{alts[0]["id"]}">Comparar {ICO["arrow"]}</a>')
    body = f'''
<main class="pg">
 <section class="fh">
  {crumbs([("Inicio", f"{B}/"), (c[1], f"{B}/categorias/{c[0]}/"), (nm, "")])}
  <span class="lg xl">{logo(t, 44)}</span>
  <h1>{esc(nm)}{f" <small>{esc(alias)}</small>" if alias else ""}</h1>
 </section>
 <div class="fg">
  <section class="fb fq"><h2>Qué es {esc(nm)}</h2><p>{esc(f["q"])}</p>{fuente_q(f)}{compartir(f"{nm}: qué es y para qué sirve en clase", f'/{t["id"]}/', "c")}</section>
  <aside class="fb fa"><h2>Ficha rápida</h2><dl>{dl}</dl></aside>
  <section class="fb fu" aria-label="Para qué lo puedes usar"><ul>{usos}</ul></section>
 </div>
 <p class="go"><a class="btn solid" href="{esc(t["url"])}" rel="noopener" target="_blank">Ir a {esc(nm)} {ICO["ext"]}</a></p>{saber_mas(f)}
 <section class="sec alt" aria-labelledby="h-alt"><h2 id="h-alt">Herramientas alternativas</h2><div class="tcg">{"".join(card(o) for o in alts)}</div>
  <p class="more"><a class="btn solid" href="{B}/categorias/{c[0]}/">Ver todo {esc(c[1])} {ICO["arrow"]}</a>{alt_mas}</p></section>
</main>'''
    pagina = {"@type": "WebPage", "name": f"{nm} · Didákora", "url": f'{WEB}/{t["id"]}/', "inLanguage": "es", "isPartOf": {"@id": SITIO["@id"]},
              "author": {"@id": PERSONA["@id"]}, "dateModified": t.get("rev", REV),
              "about": {"@type": "Thing", "name": nm, "url": t["url"], "sameAs": t["url"],
                        "description": f["q"].split(". ")[0].rstrip(".") + "."}}
    con_og = os.path.exists(os.path.join(H, "og", t["id"] + ".png"))
    if con_og: pagina["primaryImageOfPage"] = {"@type": "ImageObject", "url": f'{WEB}/og/{t["id"]}.png', "width": 1200, "height": 630}
    ld = [pagina, migas(("Inicio", "/"), (c[1], f"/categorias/{c[0]}/"), (nm, f'/{t["id"]}/'))] + ([{"@type": "FAQPage", "url": f'{WEB}/{t["id"]}/#h-faq', "mainEntity": [{"@type": "Question", "name": x["p"], "acceptedAnswer": {"@type": "Answer", "text": x["r"]}} for x in f["faq"]]}] if f.get("faq") else [])
    write(f'{t["id"]}/index.html', head(titulo_ficha(nm), f["q"].split(". ")[0].rstrip(".") + ".", f'/{t["id"]}/', ld=ld,
          img=f'{WEB}/og/{t["id"]}.png' if con_og else None, img_alt=f"{nm}: qué es y para qué sirve en clase. Ficha de Didákora" if con_og else "") + body + foot())


# ---------------------------------------------------------------- comparador, alternativas y colecciones
# Datos en _build/guias.py. Tres páginas que usan lo que ya dice cada ficha (qué hace, dispositivos, cuenta y etapas).
from guias import ALTERNATIVAS, FRECUENTES, COLECCIONES
def campos(t):
    """lo que se compara de una herramienta: nombre, qué hace, para quién, etapas, dispositivos y cuenta"""
    a = t["s"] == "aula"; f = F[t["id"]]
    return dict(id=t["id"], n=split_name(t["n"])[0], q=lead(t) or f["q"].split(". ")[0] + ".",
                p="La usa el alumnado" if a else "La usa el docente" if t["s"] == "docente" else "Recurso para preparar clases",
                e=" · ".join(ETN[e] for e in t["et"]), d=t["disp"] if a else f["disp"], c=t["cta"] if a else f["cta"],
                x=1 if t.get("intef") else 0, l=1 if t["id"] in LOGOS else 0, k=CAT[t["cs"]][1])
def g_tags(c): return f'<span><b>Cuenta:</b> {esc(c["c"][0].lower() + c["c"][1:])}</span><span><b>Dispositivos:</b> {esc(c["d"][0].lower() + c["d"][1:])}</span>' + ('<span class="r">En rojo en la guía del INTEF</span>' if c["x"] else "")
NOM_CORTO = {"canva": "Canva", "classroom": "Classroom", "teams": "Teams", "gforms": "Google Forms", "msforms": "Microsoft Forms", "gtranslate": "Traductor de Google"}
def corto(i): return NOM_CORTO.get(i) or split_name(BYID[i]["n"])[0]
def g_item(t, txt, extra=""):
    c = campos(t)
    return (f'<li class="g-it"><span class="lg">{logo(t, 30)}</span><div class="g-tx"><h3><a href="{B}/{t["id"]}/">{esc(c["n"])}</a></h3>'
            f'<p>{txt}</p><p class="g-tgs">{g_tags(c)}</p></div>{extra}</li>')
def comparar():
    D = [campos(t) for t in TOOLS]
    ms = {a: {b: "Mejor si " + x + "." for b, x in alts} for a, alts in ALTERNATIVAS.items()}
    grupos = "".join(f'<optgroup label="{esc(c[1])}">' + "".join(f'<option value="{t["id"]}">{esc(split_name(t["n"])[0])}</option>' for t in TOOLS if t["cs"] == c[0]) + "</optgroup>" for c in CATS)
    sel = "".join(f'<label class="cp-s"><span>{lab}</span><select data-i="{i}"><option value="">{"Elige una herramienta" if i < 2 else "Añadir otra (opcional)"}</option>{grupos}</select></label>'
                  for i, lab in enumerate(("Primera", "Segunda", "Tercera")))
    frec = "".join(f'<a href="{B}/comparar/?c={a},{b}">{esc(corto(a))} y {esc(corto(b))}</a>' for a, b in FRECUENTES)
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Comparar", "")])}<h1>Comparar herramientas</h1></div><p>Elige dos o tres y mira en qué se diferencian: qué hacen, qué dispositivos piden y qué cuenta necesitan.</p></div>
 <form class="cp-f" id="cp-f" onsubmit="return false">{sel}</form>
 <p class="cp-fr"><b>Las más comparadas</b>{frec}</p>
 <section class="cp" id="cp" aria-live="polite" hidden></section>
 <noscript><p class="cp-v">El comparador necesita JavaScript. Mientras tanto, puedes abrir las fichas desde <a href="{B}/todas/">todas las herramientas</a>.</p></noscript>
</main>
<script>
(function(){{
 var D={json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")},MS={json.dumps(ms, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")},B="{B}";
 var by={{}};D.forEach(function(t){{by[t.id]=t}});
 var sels=[].slice.call(document.querySelectorAll("#cp-f select")),out=document.getElementById("cp");
 function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return {{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]}})}}
 function lg(t,s){{return '<span class="lg">'+(t.l?'<img src="'+B+'/logos/'+t.id+'.png?v=3" alt="" width="'+s+'" height="'+s+'">':'<b>'+esc(t.n.charAt(0))+'</b>')+'</span>'}}
 function leer(){{var m=/[?&]c=([a-z0-9,]+)/.exec(location.search),ids=m?m[1].split(","):[];return ids.filter(function(i,k){{return by[i]&&ids.indexOf(i)===k}}).slice(0,3)}}
 function pinta(ids,empuja){{
  sels.forEach(function(s,i){{s.value=ids[i]||""}});
  if(empuja){{try{{history.replaceState(null,"",ids.length?"?c="+ids.join(","):location.pathname)}}catch(e){{}}}}
  if(ids.length<2){{out.hidden=true;out.innerHTML="";return}}
  var T=ids.map(function(i){{return by[i]}}),n=T.length;
  var filas=[["Qué hace","q",0],["Para quién","p",1],["Etapas","e",1],["Dispositivos","d",1],["Cuenta","c",1],["Categoría","k",1]];
  var h='<div class="cp-g n'+n+'"><div class="cp-r cp-h"><span></span>'+T.map(function(t){{return '<div class="cp-c">'+lg(t,34)+'<a href="'+B+'/'+t.id+'/">'+esc(t.n)+'</a></div>'}}).join("")+'</div>';
  filas.forEach(function(f){{
   var v=T.map(function(t){{return t[f[1]]}}),ig=v.every(function(x){{return x===v[0]}});
   h+='<div class="cp-r'+(f[2]&&!ig?" dif":"")+'"><h3>'+f[0]+(f[2]?'<i>'+(ig?"Igual":"Distinto")+'</i>':"")+'</h3>'+(f[2]&&ig?'<div class="cp-c eq"><p>'+esc(v[0])+'</p></div>':T.map(function(t){{return '<div class="cp-c" data-n="'+esc(t.n)+'">'+lg(t,22)+'<p>'+esc(t[f[1]])+'</p></div>'}}).join(""))+'</div>';
  }});
  if(T.some(function(t){{return t.x}})) h+='<div class="cp-r dif"><h3>Guía del INTEF</h3>'+T.map(function(t){{return '<div class="cp-c" data-n="'+esc(t.n)+'">'+lg(t,22)+'<p>'+(t.x?"<b class=\\"cp-x\\">En rojo:</b> no la recomienda para el alumnado":"Sin aviso")+'</p></div>'}}).join("")+'</div>';
  h+='</div>';
  var fr=[];T.forEach(function(a){{T.forEach(function(b){{if(a!==b&&MS[a.id]&&MS[a.id][b.id])fr.push('<li>'+lg(b,22)+'<span><b>'+esc(b.n)+'.</b> '+esc(MS[a.id][b.id])+'</span></li>')}})}});
  if(fr.length) h+='<div class="cp-v"><h3>Para decidir</h3><ul>'+fr.filter(function(x,i){{return fr.indexOf(x)===i}}).join("")+'</ul></div>';
  out.innerHTML=h;out.hidden=false;
 }}
 sels.forEach(function(s){{s.addEventListener("change",function(){{var ids=[];sels.forEach(function(x){{if(x.value&&ids.indexOf(x.value)<0)ids.push(x.value)}});pinta(ids,true)}})}});
 pinta(leer(),false);
}})();
</script>'''
    write("comparar/index.html", head("Comparar herramientas digitales para clase · Didákora", "Compara dos o tres herramientas lado a lado: qué hacen, qué dispositivos piden, qué cuenta necesita el alumnado y para qué etapas sirven.", "/comparar/") + body + foot())

def alternativas():
    cards = ""
    for i, alts in ALTERNATIVAS.items():
        t = BYID[i]; c = campos(t); nm = c["n"]
        items = "".join(g_item(BYID[a], "<b>Mejor si</b> " + esc(x) + ".", f'<a class="g-cmp" href="{B}/comparar/?c={i},{a}">Comparar</a>') for a, x in alts)
        body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Alternativas", f"{B}/alternativas/"), (nm, "")])}<h1>Alternativas a {esc(nm)}</h1></div><p>Otras herramientas que sirven para lo mismo y cuándo conviene cada una. Aquí nadie paga por aparecer.</p></div>
 <div class="al">
  <aside class="al-o"><p class="al-k">La que ya conoces</p><div class="al-n"><span class="lg">{logo(t, 34)}</span><h2>{esc(nm)}</h2></div><p>{esc(c["q"])}</p>
   <dl><div><dt>Dispositivos</dt><dd>{esc(c["d"])}</dd></div><div><dt>Cuenta</dt><dd>{esc(c["c"])}</dd></div><div><dt>Etapas</dt><dd>{esc(c["e"])}</dd></div></dl>
   <a class="btn line" href="{B}/{i}/">Ver su ficha {ICO["arrow"]}</a></aside>
  <section class="al-l" aria-labelledby="h-al"><h2 id="h-al">{len(alts)} alternativas</h2><ul class="g-l">{items}</ul>
   <p class="more"><a class="btn solid" href="{B}/comparar/?c={i},{alts[0][0]}">Comparar lado a lado {ICO["arrow"]}</a></p></section>
 </div>
</main>'''
        ld = [migas(("Inicio", "/"), ("Alternativas", "/alternativas/"), (nm, f"/alternativas/{i}/")),
              {"@type": "ItemList", "name": f"Alternativas a {nm}", "itemListElement": [{"@type": "ListItem", "position": k + 1, "name": split_name(BYID[a]["n"])[0], "url": f"{WEB}/{a}/"} for k, (a, x) in enumerate(alts)]}]
        nombres = ", ".join(split_name(BYID[a]["n"])[0] for a, x in alts[:-1]) + " y " + split_name(BYID[alts[-1][0]]["n"])[0]
        write(f"alternativas/{i}/index.html", head(f"Alternativas a {nm} para clase · Didákora", f"{nombres}: cuándo conviene cada una en lugar de {nm}, con sus dispositivos y su cuenta.", f"/alternativas/{i}/", ld=ld) + body + foot())
        cards += (f'<a class="al-c" href="{B}/alternativas/{i}/"><span class="lg">{logo(t, 30)}</span><span class="al-ct"><small>Alternativas a</small><b>{esc(nm)}</b></span>'
                  f'<span class="al-cl">{"".join(logo(BYID[a], 20) for a, x in alts[:4])}</span></a>')
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Alternativas", "")])}<h1>Alternativas a…</h1></div><p>Parte de la herramienta que ya conoces y mira cuáles sirven para lo mismo, con el motivo para elegir cada una.</p></div>
 <div class="al-g">{cards}</div>
 <p class="g-n">¿No está la que buscas? Cada ficha termina con sus herramientas alternativas y en <a href="{B}/comparar/">Comparar</a> puedes enfrentar las que quieras.</p>
</main>'''
    write("alternativas/index.html", head("Alternativas a las herramientas más usadas en clase · Didákora", "Alternativas a Kahoot!, Canva, Padlet, Google Forms y otras herramientas conocidas, con el motivo para elegir cada una.", "/alternativas/") + body + foot())

def colecciones():
    cards = ""
    for k, c in enumerate(COLECCIONES, 1):
        ts = [(BYID[i], x) for i, x in c["items"]]
        items = "".join(g_item(t, esc(x)) for t, x in ts)
        body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Colecciones", f"{B}/colecciones/"), (c["t"], "")])}<h1>{esc(c["t"])}</h1></div><p>{esc(c["d"])}</p></div>
 <ul class="g-l co-l">{items}</ul>
 <p class="more"><a class="btn line" href="{B}/colecciones/">Ver todas las colecciones {ICO["arrow"]}</a></p>
</main>'''
        ld = [migas(("Inicio", "/"), ("Colecciones", "/colecciones/"), (c["t"], f'/colecciones/{c["slug"]}/')),
              {"@type": "ItemList", "name": c["t"], "itemListElement": [{"@type": "ListItem", "position": n + 1, "name": split_name(t["n"])[0], "url": f'{WEB}/{t["id"]}/'} for n, (t, x) in enumerate(ts)]}]
        write(f'colecciones/{c["slug"]}/index.html', head(f'{c["t"]}: herramientas para clase · Didákora', f'{c["d"]} {len(ts)} herramientas elegidas y por qué.', f'/colecciones/{c["slug"]}/', ld=ld) + body + foot())
        cards += (f'<a class="co-c" href="{B}/colecciones/{c["slug"]}/"><i>{k:02d}</i><span class="co-t"><b>{esc(c["t"])}</b><small>{esc(c["s"])}</small></span>'
                  f'<span class="co-g">{"".join(logo(t, 22) for t, x in ts[:5])}</span></a>')
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Colecciones", "")])}<h1>Colecciones</h1></div><p>Pocas herramientas, elegidas para una situación concreta del curso.</p></div>
 <div class="co-gr">{cards}</div>
</main>'''
    write("colecciones/index.html", head("Colecciones de herramientas para cada momento del curso · Didákora", "Listas cortas para una situación concreta: aula sin dispositivos, primer día de clase, evaluar sin examen, tutoría con familias o clase de idiomas.", "/colecciones/") + body + foot())
def bloque_guias():
    """portada: entrada a comparar, alternativas y colecciones"""
    c = [("comparar", "Comparar", "Dos o tres herramientas, lado a lado."), ("alternativas", "Alternativas a…", "Parte de la que ya conoces."), ("colecciones", "Colecciones", "Elegidas para cada momento del curso.")]
    return ('<section class="sec g3" aria-label="Más formas de elegir">' + "".join(f'<a href="{B}/{k}/"><b>{t}</b><span>{d}</span>{ICO["arrow"]}</a>' for k, t, d in c) + "</section>")

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
    fl = f' <a class="pa-ficha" href="{B}/{t["id"]}/">Ver su ficha en Didákora {ICO["arrow"]}</a>' if t else ""
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
    if k == "video":  # sin reproductor incrustado: un enlace al vídeo (así Didákora no carga cookies de terceros)
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
 {compartir(bt_plano(p["titulo"]).rstrip("."), path)}
 <article class="pa">{"".join(seccion_post(x) for x in p["bloques"])}
  {f'<footer class="pa-fuentes"><h2>Fuentes</h2><ul>{fu}</ul></footer>' if fu else ""}</article>
 {f'<section class="sec" aria-labelledby="h-mas">{secth("", "Más actualidad", "", "h-mas")}<div class="pcg">{"".join(post_card(x) for x in otros)}</div></section>' if otros else ""}
 <p class="more"><a class="btn solid" href="{B}/actualidad/">Toda la actualidad {ICO["arrow"]}</a><a class="btn line" href="{B}/todas/">Ver las herramientas {ICO["arrow"]}</a></p>
</main>'''
    # el texto de los posts va en Literata (letra de lectura en pantalla); los títulos, en la de la marca
    lectura = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap">\n'
    art = {"@type": "BlogPosting", "headline": bt_plano(p["titulo"]).rstrip("."), "description": bt_plano(p["entradilla"])[:300], "url": f"{WEB}{path}",
           "datePublished": p["fecha"][:10], "inLanguage": "es", "author": {"@id": PERSONA["@id"]}, "publisher": {"@id": PERSONA["@id"]}, "isPartOf": {"@id": SITIO["@id"]}}
    if (p.get("portada") or {}).get("src"): art["image"] = f'{WEB}{path}{p["portada"]["src"]}'
    mini_og = (p.get("miniatura") or {}).get("src")  # al compartir, la miniatura (16:9): la portada (21:9) se recorta en las redes
    return head(f'{p["titulo"]} · Didákora', bt_plano(p["entradilla"])[:155], path, "actualidad", ld=[art, migas(("Inicio", "/"), ("Actualidad", "/actualidad/"), (bt_plano(p["titulo"]).rstrip("."), path))],
                img=f'{WEB}{path}{mini_og}' if mini_og else art.get("image"), img_alt=bt_plano(p["titulo"]).rstrip(".") if art.get("image") else "", tipo="article").replace("</head>", lectura + "</head>", 1) + body + foot()
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
    write("actualidad/index.html", head("Actualidad · Didákora", ACT_DESC, "/actualidad/", "actualidad") + body + foot())
    rss()
ACT_DESC = "Noticias de educación digital para docentes: herramientas, IA, recomendaciones oficiales e ideas para clase."
def rss():
    # feed RSS 2.0 de Actualidad (/rss.xml), del post más reciente al más antiguo; lo enlaza head() en todas las páginas.
    # La hora no consta en los posts: van a las 00:00 GMT de su fecha. Autor en el formato de RSS 2.0, «correo (nombre)».
    from email.utils import format_datetime
    from datetime import datetime, timezone
    rfc = lambda f: format_datetime(datetime(*(int(x) for x in f[:10].split("-")), tzinfo=timezone.utc))
    x = lambda s: html.escape(str(s), quote=False)
    items = "".join(f"""
  <item>
   <title>{x(bt_plano(p["titulo"]))}</title>
   <link>{WEB}/actualidad/{post_slug(p)}/</link>
   <guid isPermaLink="true">{WEB}/actualidad/{post_slug(p)}/</guid>
   <pubDate>{rfc(p["fecha"])}</pubDate>
   <description>{x(bt_plano(p["entradilla"]))}</description>
   <author>jorgedelagui@gmail.com (Jorge Delgado Aguilera)</author>
   <category>{x(p["etiqueta"])}</category>
  </item>""" for p in reversed(POSTS))
    write("rss.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
 <channel>
  <title>Actualidad · Didákora</title>
  <link>{WEB}/actualidad/</link>
  <atom:link href="{WEB}/rss.xml" rel="self" type="application/rss+xml"/>
  <description>{x(ACT_DESC)}</description>
  <language>es-ES</language>
  <lastBuildDate>{rfc(max(p["fecha"] for p in POSTS))}</lastBuildDate>{items}
 </channel>
</rss>
""")
def vista(ruta_json, carpeta):
    """vista previa de un post sin publicarlo: escribe <carpeta>/index.html (dentro del repo, por ejemplo en agentes/)"""
    p = json.load(open(ruta_json, encoding="utf-8"))
    rel = os.path.relpath(os.path.abspath(carpeta), H).replace(os.sep, "/")
    write(f"{rel}/index.html", pagina_post(p, f"/{rel}/").replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1))
    print("vista previa:", f"{rel}/index.html")

# ---------------------------------------------------------------- datos para el listado
GUIAS_URL = ["/comparar/", "/alternativas/", "/colecciones/"] + [f"/alternativas/{i}/" for i in ALTERNATIVAS] + [f'/colecciones/{c["slug"]}/' for c in COLECCIONES]
def extras():
    """página de error 404 (GitHub Pages la sirve sola) y mapa del sitio (robots.txt solo cuenta en la raíz del dominio)"""
    body = f'''
<main class="pg">
 <div class="pg-h"><div class="pg-t">{crumbs([("Inicio", f"{B}/"), ("Página no encontrada", "")])}<h1>Esta página no existe</h1></div><p>Puede que el enlace esté mal escrito o que la herramienta haya cambiado de dirección. Búscala desde aquí.</p></div>
 <form class="ls" action="{B}/todas/" method="get" role="search"><div class="hs-r"><div class="hs-q">{ICO["search"]}<label class="sr" for="eq">Busca una herramienta</label><input id="eq" name="q" type="text" placeholder="Busca por nombre o por lo que necesitas hacer…" autocomplete="off" enterkeyhint="search"></div></div></form>
 <p class="more"><a class="btn solid" href="{B}/">Ir al inicio {ICO["arrow"]}</a><a class="btn line" href="{B}/todas/">Ver todas las herramientas {ICO["arrow"]}</a></p>
</main>'''
    write("404.html", head("Página no encontrada · Didákora", "Esta página no existe en Didákora.", "/404.html") + body + foot())
    # sitemap con la fecha de cada página (lastmod): la revisión de cada ficha (`rev`, o `REV`), la más reciente de cada
    # categoría y la fecha de cada post; las páginas generales llevan la más reciente de todas. «Sobre mí» va sin fecha.
    rev = lambda t: t.get("rev", REV)
    ult_post = max((p["fecha"][:10] for p in POSTS), default="")
    ult = max([rev(t) for t in TOOLS] + [ult_post])
    urls = ([(u, ult) for u in ["/", "/todas/", "/destacadas/", "/nuevas/", "/categorias/"] + (["/sesion/"] if SES_PUB else []) + GUIAS_URL] + [("/sobre-mi/", "")]
            + [(f"/categorias/{c[0]}/", max(rev(t) for t in TOOLS if t["cs"] == c[0])) for c in CATS]
            + [(f'/{t["id"]}/', rev(t)) for t in TOOLS])
    if POSTS: urls += [("/actualidad/", ult_post)] + [(f"/actualidad/{post_slug(p)}/", p["fecha"][:10]) for p in POSTS]
    NL = "\n"
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>' + NL + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + NL
          + "".join(f"<url><loc>{WEB}{u}</loc>{f'<lastmod>{d}</lastmod>' if d else ''}</url>{NL}" for u, d in urls) + "</urlset>" + NL)
    llms()

def llms():
    # llms.txt: índice en texto plano para que las IA entiendan qué es Didákora y encuentren cada ficha (https://llmstxt.org)
    from fichas import F
    rev = lambda t: t.get("rev", REV)
    pri = lambda q: q.split(". ")[0].rstrip(".") + "."
    L = ["# Didákora", "",
         "> Catálogo de herramientas digitales para docentes de Infantil, Primaria, Secundaria y Bachillerato en España. Cada ficha explica qué es la "
         "herramienta, para qué sirve en clase, en qué dispositivos funciona, si pide cuenta y la edad mínima cuando sus "
         "condiciones la indican. La hace Jorge Delgado Aguilera, profesor de Geografía e Historia y diseñador de materiales "
         "educativos digitales. Un equipo de agentes de IA le propone cambios y él los comprueba antes de publicarlos.", "",
         f"Herramientas: {len(TOOLS)}. Última revisión: {revisada(max(rev(t) for t in TOOLS)[:7]).lower()}.", "",
         "## Páginas principales", "",
         f"- [Todas las herramientas]({WEB}/todas/): listado completo con buscador y filtros por categoría y etapa",
         f"- [Sobre mí]({WEB}/sobre-mi/): quién hace Didákora y cómo se revisa",
         f"- [Portfolio de Jorge Delgado Aguilera]({SITE}/)"]
    if SES_PUB: L.insert(len(L) - 2, f"- [Monta tu sesión]({WEB}/sesion/): unas preguntas (qué quieres hacer, etapa y dispositivos) y una propuesta de clase paso a paso con herramientas del catálogo")
    if POSTS: L.append(f"- [Actualidad]({WEB}/actualidad/): noticias de educación digital para docentes")
    for c in CATS:
        L += ["", f"## {c[1]}", "", c[2], ""]
        L += [f'- [{split_name(t["n"])[0]}]({WEB}/{t["id"]}/): {pri(F[t["id"]]["q"])}' for t in TOOLS if t["cs"] == c[0]]
    if POSTS:
        L += ["", "## Actualidad", ""] + [f"- [{bt_plano(p['titulo']).rstrip('.')}]({WEB}/actualidad/{post_slug(p)}/): {bt_plano(p['entradilla'])}"
                                          for p in reversed(POSTS)]
    write("llms.txt", "\n".join(L) + "\n")

def datos():
    from fichas import F
    # también van los textos de la ficha («Qué es» y usos) para que el buscador los encuentre
    m = {t["id"]: [t["cs"], t["et"], 1 if t["id"] in LOGOS else 0, t["sub"], " ".join(F[t["id"]]["usos"]) + " " + F[t["id"]]["q"] + " " + F[t["id"]].get("fu", {}).get("t", "")] for t in TOOLS}
    cats = {c[0]: [c[1], IC[c[3]]] for c in CATS}
    write("didakora-datos.js", "// Generado por _build/build.py: categoría, etapas, logo, apartado y textos de la ficha de cada herramienta\nconst CAJA=" + json.dumps({"cats": cats, "t": m}, ensure_ascii=False) + ";\n")

if __name__ == "__main__":
    if "--vista" in sys.argv:
        i = sys.argv.index("--vista"); vista(sys.argv[i + 1], sys.argv[i + 2]); sys.exit()
    shutil.copyfile(os.path.join(ROOT, "_build", "didakora.css"), os.path.join(H, "didakora.css"))
    shutil.copyfile(os.path.join(ROOT, "_build", "didakora.js"), os.path.join(H, "didakora.js"))
    datos(); portada(); todas(); destacadas(); nuevas(); categorias(); sobremi(); extras(); actualidad(); sesion(); comparar(); alternativas(); colecciones()
    import og   # imagen para compartir de cada ficha (og/<id>.png); sin Pillow se quedan las que hubiera
    n_og = og.genera([(t["id"], split_name(t["n"])[0], CAT[t["cs"]][1]) for t in TOOLS])
    print("· og: falta Pillow, no se han tocado las imágenes para compartir" if n_og is None else f"· og: {n_og} imágenes nuevas o cambiadas")
    for t in TOOLS: ficha(t)
    print("didakora:", len(TOOLS), "fichas,", len(CATS), "categorías")
