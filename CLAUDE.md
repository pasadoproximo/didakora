# Didákora · herramientas digitales para docentes

Web estática de Jorge Delgado Aguilera (antes «Caja de herramientas digitales» del portfolio pasadoproximo.github.io).
Se publicará con GitHub Pages en el repo `didakora` → https://pasadoproximo.github.io/didakora/ (hay `.nojekyll`).

## Estructura

- `_build/build.py` → genera todas las páginas (portada, `todas/`, `destacadas/` (sin enlace en el menú ni en la portada desde el 22-10-2026), `categorias/`, una ficha por herramienta,
  `sobre-mi/` y 404). **Las páginas son generadas: no editarlas a mano.** Las rutas cuelgan de `B` (`/didakora`);
  para un dominio propio: `DK_BASE= python _build/build.py`.
- `tools.js` → los datos de las herramientas (`SECTIONS`, `TOOLS`, `RECIENTES`, `CHANGES`). `logos/` → logos de cada herramienta.
  `RECIENTES` = las últimas añadidas, de la más reciente a la más antigua (máximo 12, cada una con texto corto): salen en
  «Añadidas recientemente» de la portada (las 4 primeras, bajo las categorías) y en `/nuevas/` («Nuevas» en el menú).
- `_build/didakora.css` y `_build/didakora.js` → se copian a la raíz al generar. Si cambian, subir `V` en `build.py`.
- `didakora-datos.js` → generado (categoría, etapas, logo y apartado de cada herramienta para el listado).
- Buscador: `dkMotor` en `didakora.js` puntúa por nombre, descripción, categoría, apartado, materia, etapa e ideas;
  entiende plurales, sinónimos (`SYN`), frases (`PHRASES`), principio de palabra y una errata; ordena por relevancia y, si
  nada tiene todas las palabras, enseña las parecidas. **Tras tocar datos o buscador: `node _build/probar_buscador.js`**
  (busca cada herramienta por nombre, palabras, principio, nombre anterior y con errata, más búsquedas habituales de clase;
  las de `RECIENTES` también por sus búsquedas típicas `q`, que deben sacarlas entre las 5 primeras).
- `_build/fichas.py` → contenido de cada ficha: «Qué es» (`q`), usos generales (`usos`) y, para docente y recursos,
  dispositivos (`disp`) y cuenta (`cta`). Si se añade una herramienta a `tools.js`, hay que añadir su ficha aquí
  (el build se para si falta). Ficha: cabecera (volver, logo, nombre, botón «Ir a…»), «Qué es» y «Ficha rápida»
  (categoría, etapa, dispositivos, cuenta + edad mínima y avisos en pequeño) del mismo tamaño, usos debajo y alternativas.
  Sin referencias al año en que se añadió cada herramienta.
  Lo que **no se ve** en la ficha: `coste` (solo lo usa el buscador) y un `datos` que empieza por «Con la cuenta del centro»,
  «Usa la cuenta del centro» o «Trabaja con la cuenta del centro» (`build.py`, en `ficha()`). El aviso «Trabaja con IA: no
  introduzcas datos personales» solo sale en las del alumnado (Aula) cuya descripción habla de IA (`uses_ai`); las del
  docente no lo llevan salvo que lo diga su `datos`. Lo que está en rojo en la guía de protección de datos del INTEF va en
  `intef` (`"rojo"`, o `"ver"` si el alumnado puede ver lo del docente sin registrarse), no en `datos`: sale con un punto rojo
  bajo la cuenta (que entonces va en pequeño, como las notas) y sustituye a «Consulta la edad mínima…».
  Si cambia esa lógica de `build.py`, actualiza estas líneas.
  La Ficha rápida acaba con «Revisada» (mes y año): `rev:"AAAA-MM"` en la herramienta o, si no lo tiene, `REV` en `build.py`
  (la revisión general). El Administrador pone `rev` al dar de alta o cambiar una herramienta; comprobar el enlace no cuenta.
  Lo que puede cambiar (un nombre nuevo, un cierre, un precio) va con su fuente bajo «Qué es»: `fu=dict(t, url, fecha)` en
  `fichas.py` → «t (anuncio oficial, comprobado el DD/MM/AAAA). Si cambia, lo anoto aquí.» (`fuente_q()` en `build.py`; `enlace`
  cambia el texto del enlace). Solo con enlace oficial abierto; lo que dice `fu` no se repite en `q`. El Rastreador vuelve a abrir
  cada `fu.url` en cada ciclo. Primera: NotebookLM (23-10-2026).
- Portada: bajo el párrafo del hero, la autoría (`autoria()` en `build.py`, brief del portfolio v3): foto, «Revisado a mano por
  Jorge Delgado Aguilera» (enlaza al portfolio), el número de herramientas y el mes de la última revisión, calculados solos.
  Solo es verdad si Jorge ve cada cambio: los agentes proponen y él aprueba y publica.
- Alternativas de cada ficha «en rueda» dentro del apartado: todas las herramientas salen como alternativa en alguna ficha.
- `_build/marca.py` → genera los logos de `marca/` con el nombre en trazos (necesita `fonttools` y `uharfbuzz`;
  fuente en `_build/fuentes/`, licencia OFL). Las PNG de `marca/` (og, icono, redes, avatar) se sacaron con el navegador.
- **Actualidad** (`/actualidad/` y `/actualidad/<slug>/`): el blog de noticias de educación digital. Cada post es
  `_build/actualidad/<slug>.json` (secciones `texto`, `destacado`, `lista`, `pasos`, `oficial`, `video`, `imagen` y `cita`;
  ver la sección «actualidad» de `build.py`) con sus imágenes en `actualidad/<slug>/img/`. Se lee de corrido como un
  artículo (no en tarjetas). Mientras no hay ningún post, la web no cambia; con el primero aparecen «Actualidad» en el menú
  (en el móvil, con poco ancho, quedan Todas, Actualidad y Sobre mí) y los últimos posts en la portada. Los vídeos van como enlace, sin reproductor.
  Diseño fijado por Jorge el 22-10-2026: post con volver arriba a la izquierda, título, tema y fecha, entradilla, portada
  21:9 a todo el ancho (16:9 en el móvil), texto en Literata en una columna centrada de 820 px y botones a la derecha;
  tarjetas con la miniatura (tema y fecha dentro), título de dos líneas y descripción de cuatro. Las imágenes salen de
  `_build/miniatura.py` (foto con licencia y duotono navy y cielo, forma coral, aro blanco y gancho corto; o ilustración).
  Vista previa sin publicar: `python _build/build.py --vista <post.json> <carpeta>`.
- `_build/capturas.py` también captura cualquier página con `nombre=ruta` (p. ej. `boletin-1=boletin/1`).
- `propuestas/` → maquetas de paleta y logo, solo en local (no se sube: está en `.gitignore`).

## Flujo

1. `python _build/build.py` (`python` ya es Python 3.12 en este equipo; úsalo así, sin la ruta completa).
2. Probar en local sirviendo la carpeta padre (`El pasado próximo`) para que exista `/didakora/`:
   `python -m http.server 8020` → http://127.0.0.1:8020/didakora/ . Revisar escritorio y móvil (390 px).
3. Commit con autor `Jorge Delgado Aguilera <jorgedelagui@gmail.com>` y mensaje en español.

## Sistema de agentes

Dos ciclos independientes, con ocho agentes (`.claude/agents/`). Catálogo: Rastreador, Coordinador editorial,
Administrador web y Auditor. Actualidad (el blog): Cronista, Redactor y Maquetador. El Optimizador revisa a los ocho. Se lanzan solo a mano:

- `/ciclo` → Rastreador → Coordinador → **pausa para que Jorge apruebe** → Administrador (commit local por tarea) → Auditor.
  `/ciclo prueba` recorre el flujo con datos ficticios sin tocar el catálogo.
- `/boletin` → Actualidad, aparte del catálogo, en tres trabajos que pueden ir a la vez. **Buscar** (la campanilla del
  monasterio): el Cronista trae noticias de educación digital (herramientas, IA, legislación, Ministerio, INTEF y Junta de
  Andalucía; fuentes en `agentes/boletin/fuentes.md`) y **Jorge guarda las que le interesan** (`agentes/boletin/pendientes.json`).
  **Encargar** (desde el Libro): Jorge elige una o varias guardadas y se crea un post (varias = un único post con todas).
  **Cada post** sigue su camino: Redactor → **Jorge aprueba o reescribe el texto** → Maquetador (tres miniaturas) → **Jorge
  elige una** → Maquetador (el post con ella) → **visto bueno** → publicación con commit local, por turnos. Hasta 2 posts a la
  vez; las guardadas salen de la lista cuando su post se publica. Cada post tiene su estado en `agentes/boletin/numeros/<id>/`.
  Al cerrar cada post, el Auditor (modo boletín) compara el texto de Lucas con el de Jorge
  (`python _build/comparar_texto.py agentes/boletin/numeros/<id>`) junto con sus decisiones; después pone al día
  `agentes/boletin/estilo-jorge.md`, la guía de su forma de escribir que leen Redactor, Cronista y Maquetador.
- `/optimizar` → solo el Optimizador; propone mejoras a los agentes de los dos ciclos y nunca las aplica.
- `/aprendizaje <corrección>` → registra una corrección de Jorge para los próximos ciclos.
- `/monasterio` → abre el monasterio (`agentes/monasterio/`, privado): juego en pixel art (LPC) donde Jorge habla con los
  monjes-agentes, lee los informes y decide las propuestas. Su servidor (`servidor.py`, solo 127.0.0.1) guarda las
  decisiones en `agentes/tareas.json`; si `/ciclo` está esperando en Claude Code, sigue solo. La **campana** del claustro
  (y Fray Ambrosio) lanzan `claude -p "/ciclo monasterio"` u `"/optimizar monasterio"` sin interfaz, con permisos cerrados
  (`agentes/monasterio/permisos-campana.json`, sin push); el ciclo se para en la decisión y el servidor lo reanuda al sellar.
  Al sur del claustro, el **Scriptorium de la Gaceta** (Fray Tomás, Fray Lucas y Fray Isidoro): su **campanilla** lanza la
  búsqueda (`claude -p "/boletin monasterio buscar"`); los posts se encargan en la pestaña «Gaceta» del Libro y el servidor
  lanza `claude -p "/boletin monasterio post <id>"` para cada uno (hasta 2 a la vez; publicar, por turnos). Las consultas se
  deciden hablando con los monjes o en la Gaceta. El catálogo (campana y Fray Ambrosio) sigue con una sesión a la vez.
- `python _build/comprobar_enlaces.py` → comprueba las URL de `tools.js` (solo lee).

Registros privados en `agentes/` (en `.gitignore`: solo en este equipo): `fuentes.md`, `estado.json`, `tareas.json`,
`aprendizajes.md`, `ciclos/<fecha>/` y `mejoras/`. `git push` está bloqueado para Claude en `.claude/settings.json`,
con una sola excepción que autorizó Jorge el 22-10-2026: `git -C "C:/Users/USER/Desktop/El pasado próximo/didakora" push origin
rediseno-2026-10:main` (GitHub Pages publica desde `main`), que Claude hace cuando Jorge se lo pide. Los agentes del
monasterio siguen sin poder publicar. Sin tareas programadas, servicios externos ni dependencias nuevas.

## Identidad

- Paleta «cielo y coral», de la familia del portfolio: cielo `#9FB3FF` (cabecera, con texto navy), coral `#FF8A6B`
  (subrayado del titular, círculo de la cabecera, iconos y etiquetas; suave `#FFE1D8`), navy `#061033` (texto y botones),
  `#1B2C6B`, hielo `#DDE4F6`, fondo `#F2F4F9`.
- Logo: caja abierta (solapas cielo y coral, caja navy). Logotipo «B2» en la web (el cuerpo de la caja mide lo que la «d»);
  apilado para redes. Nombre siempre en minúsculas: «didákora», en Bricolage Grotesque 800.
- Tipografías: Bricolage Grotesque (títulos) y Alegreya Sans (texto).

## Normas de contenido

- No inventar métricas, capturas ni testimonios. Edad mínima solo con fuente oficial.
- Nunca coma antes de «y».
- Nunca publicar en redes en nombre de Jorge: dejarlo preparado.
