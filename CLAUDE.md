# Didakora · herramientas digitales para docentes

Web estática de Jorge Delgado Aguilera (antes «Caja de herramientas digitales» del portfolio pasadoproximo.github.io).
Se publicará con GitHub Pages en el repo `didakora` → https://pasadoproximo.github.io/didakora/ (hay `.nojekyll`).

## Estructura

- `_build/build.py` → genera todas las páginas (portada, `todas/`, `destacadas/`, `categorias/`, una ficha por herramienta
  y `alternativas/`). **Las páginas son generadas: no editarlas a mano.** Las rutas cuelgan de `B` (`/didakora`);
  para un dominio propio: `DK_BASE= python _build/build.py`.
- `tools.js` → los datos de las herramientas (`SECTIONS`, `TOOLS`, `CHANGES`). `logos/` → logos de cada herramienta.
- `_build/didakora.css` y `_build/didakora.js` → se copian a la raíz al generar. Si cambian, subir `V` en `build.py`.
- `didakora-datos.js` → generado (categoría, etapas y logo de cada herramienta para el listado).
- `_build/marca.py` → genera los logos de `marca/` con el nombre en trazos (necesita `fonttools` y `uharfbuzz`;
  fuente en `_build/fuentes/`, licencia OFL). Las PNG de `marca/` (og, icono, redes, avatar) se sacaron con el navegador.
- `propuestas/` → maquetas de paleta y logo, solo en local (no se sube: está en `.gitignore`).

## Flujo

1. `python _build/build.py` (en este equipo: `%LOCALAPPDATA%/Programs/Python/Python312/python.exe`).
2. Probar en local sirviendo la carpeta padre (`El pasado próximo`) para que exista `/didakora/`:
   `python -m http.server 8020` → http://127.0.0.1:8020/didakora/ . Revisar escritorio y móvil (390 px).
3. Commit con autor `Jorge Delgado Aguilera <jorgedelagui@gmail.com>` y mensaje en español.

## Identidad

- Paleta «cielo y coral», de la familia del portfolio: cielo `#9FB3FF` (cabecera, con texto navy), coral `#FF8A6B`
  (subrayado del titular, círculo de la cabecera, iconos y etiquetas; suave `#FFE1D8`), navy `#061033` (texto y botones),
  `#1B2C6B`, hielo `#DDE4F6`, fondo `#F2F4F9`.
- Logo: caja abierta (solapas cielo y coral, caja navy). Logotipo «B2» en la web (el cuerpo de la caja mide lo que la «d»);
  apilado para redes. Nombre siempre en minúsculas: «didakora», en Bricolage Grotesque 800.
- Tipografías: Bricolage Grotesque (títulos) y Alegreya Sans (texto).

## Normas de contenido

- No inventar métricas, capturas ni testimonios. Edad mínima solo con fuente oficial.
- Nunca coma antes de «y».
- Nunca publicar en redes en nombre de Jorge: dejarlo preparado.
