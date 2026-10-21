# Didákora · herramientas digitales para docentes

Web estática de Jorge Delgado Aguilera (antes «Caja de herramientas digitales» del portfolio pasadoproximo.github.io).
Se publicará con GitHub Pages en el repo `didakora` → https://pasadoproximo.github.io/didakora/ (hay `.nojekyll`).

## Estructura

- `_build/build.py` → genera todas las páginas (portada, `todas/`, `destacadas/`, `categorias/`, una ficha por herramienta,
  `sobre-mi/` y 404). **Las páginas son generadas: no editarlas a mano.** Las rutas cuelgan de `B` (`/didakora`);
  para un dominio propio: `DK_BASE= python _build/build.py`.
- `tools.js` → los datos de las herramientas (`SECTIONS`, `TOOLS`, `RECIENTES`, `CHANGES`). `logos/` → logos de cada herramienta.
  `RECIENTES` = las últimas añadidas, de la más reciente a la más antigua (máximo 12, cada una con texto corto): salen en
  «Añadidas recientemente» de la portada (las 4 primeras, bajo las destacadas) y en `/nuevas/` («Nuevas» en el menú).
- `_build/didakora.css` y `_build/didakora.js` → se copian a la raíz al generar. Si cambian, subir `V` en `build.py`.
- `didakora-datos.js` → generado (categoría, etapas, logo y apartado de cada herramienta para el listado).
- Buscador: `dkMotor` en `didakora.js` puntúa por nombre, descripción, categoría, apartado, materia, etapa e ideas;
  entiende plurales, sinónimos (`SYN`), frases (`PHRASES`), principio de palabra y una errata; ordena por relevancia y, si
  nada tiene todas las palabras, enseña las parecidas. **Tras tocar datos o buscador: `node _build/probar_buscador.js`**
  (busca cada herramienta por nombre, palabras, principio, nombre anterior y con errata, más búsquedas habituales de clase).
- `_build/fichas.py` → contenido de cada ficha: «Qué es» (`q`), usos generales (`usos`) y, para docente y recursos,
  dispositivos (`disp`) y cuenta (`cta`). Si se añade una herramienta a `tools.js`, hay que añadir su ficha aquí
  (el build se para si falta). Ficha: cabecera (volver, logo, nombre, botón «Ir a…»), «Qué es» y «Ficha rápida»
  (categoría, etapa, dispositivos, cuenta + edad mínima y avisos en pequeño) del mismo tamaño, usos debajo y alternativas.
  Sin referencias al año en que se añadió cada herramienta.
  Lo que **no se ve** en la ficha: `coste` (solo lo usa el buscador) y un `datos` que empieza por «Con la cuenta del centro»,
  «Usa la cuenta del centro» o «Trabaja con la cuenta del centro» (`build.py`, en `ficha()`). El aviso «Trabaja con IA: no
  introduzcas datos personales» solo sale en las del alumnado (Aula) cuya descripción habla de IA (`uses_ai`); las del
  docente no lo llevan salvo que lo diga su `datos`. Si cambia esa lógica de `build.py`, actualiza estas líneas.
- Alternativas de cada ficha «en rueda» dentro del apartado: todas las herramientas salen como alternativa en alguna ficha.
- `_build/marca.py` → genera los logos de `marca/` con el nombre en trazos (necesita `fonttools` y `uharfbuzz`;
  fuente en `_build/fuentes/`, licencia OFL). Las PNG de `marca/` (og, icono, redes, avatar) se sacaron con el navegador.
- `propuestas/` → maquetas de paleta y logo, solo en local (no se sube: está en `.gitignore`).

## Flujo

1. `python _build/build.py` (`python` ya es Python 3.12 en este equipo; úsalo así, sin la ruta completa).
2. Probar en local sirviendo la carpeta padre (`El pasado próximo`) para que exista `/didakora/`:
   `python -m http.server 8020` → http://127.0.0.1:8020/didakora/ . Revisar escritorio y móvil (390 px).
3. Commit con autor `Jorge Delgado Aguilera <jorgedelagui@gmail.com>` y mensaje en español.

## Sistema de agentes

Mantenimiento manual del catálogo con cinco agentes (`.claude/agents/`): Rastreador, Coordinador editorial,
Administrador web, Auditor y Optimizador. Se lanza solo a mano:

- `/ciclo` → Rastreador → Coordinador → **pausa para que Jorge apruebe** → Administrador (commit local por tarea) → Auditor.
  `/ciclo prueba` recorre el flujo con datos ficticios sin tocar el catálogo.
- `/optimizar` → solo el Optimizador; propone mejoras a los agentes y nunca las aplica.
- `/aprendizaje <corrección>` → registra una corrección de Jorge para los próximos ciclos.
- `/monasterio` → abre el monasterio (`agentes/monasterio/`, privado): juego en pixel art (LPC) donde Jorge habla con los
  monjes-agentes, lee los informes y decide las propuestas. Su servidor (`servidor.py`, solo 127.0.0.1) guarda las
  decisiones en `agentes/tareas.json`; si `/ciclo` está esperando en Claude Code, sigue solo. La **campana** del claustro
  (y Fray Ambrosio) lanzan `claude -p "/ciclo monasterio"` u `"/optimizar monasterio"` sin interfaz, con permisos cerrados
  (`agentes/monasterio/permisos-campana.json`, sin push); el ciclo se para en la decisión y el servidor lo reanuda al sellar.
- `python _build/comprobar_enlaces.py` → comprueba las URL de `tools.js` (solo lee).

Registros privados en `agentes/` (en `.gitignore`: solo en este equipo): `fuentes.md`, `estado.json`, `tareas.json`,
`aprendizajes.md`, `ciclos/<fecha>/` y `mejoras/`. `git push` está bloqueado para Claude en `.claude/settings.json`:
publicar lo hace Jorge con `! git push`. Sin tareas programadas, servicios externos ni dependencias nuevas.

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
