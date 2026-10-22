---
name: boletin
description: Ciclo de Actualidad (el blog de didákora), aparte del ciclo del catálogo. Un post por ciclo. Cronista (noticias y pendientes) → Jorge elige → Redactor (el post) → Jorge aprueba o reescribe → Maquetador (diseño) → Jorge aprueba → publicación con commit local.
argument-hint: "[monasterio]"
disable-model-invocation: true
---

Ejecuta el ciclo de **Actualidad**, la sección de blog de didákora (`/actualidad/`), con noticias de educación digital. **Cada ciclo produce un solo post** (un «número»). Lo que Jorge quiere guardar para otro día va a la **cola de pendientes**. Es **independiente de `/ciclo`**: no lances al Rastreador, al Coordinador ni al Administrador. Al Auditor, solo en su modo boletín (paso 9). Tú (la sesión principal) coordinas y haces las **tres pausas** de aprobación: los agentes no hablan con Jorge. Si el argumento es `monasterio` ($ARGUMENTS), sigue además la sección «Modo monasterio».

## Archivos (todos privados, en `agentes/boletin/`)

- `estado.json` (lo lee el monasterio; llévalo al día **antes y después** de cada paso, horas en UTC con `Z`):
  ```json
  { "actualizado": "…", "numero": { "id": "AAAA-MM-DD", "numero": 1, "fase": "…", "ronda": 1, "inicio": "…", "fin": null, "origen": "chat|monasterio", "nota": "" },
    "agentes": { "cronista": { "estado": "…", "desde": "…", "nota": "" }, "redactor": {…}, "maquetador": {…}, "auditor": {…} } }
  ```
  Fases: `sin-numero`, `investigacion`, `esperando-noticias`, `redaccion`, `esperando-texto`, `maquetacion`, `esperando-diseno`, `publicacion`, `publicado`, `descartado`, `interrumpido` y, mientras el monasterio espera a que lo retomes, `decidido-noticias`, `decidido-texto`, `decidido-diseno`. Estados de agente: los de `/ciclo` (`en-espera`, `en-ejecucion`, `completado`, `error`, `pendiente-aprobacion`, `no-ejecutado`).
- `indice.json` (`{"numeros": [...]}`): una entrada por post `{ "id", "numero", "titulo", "slug", "fase", "inicio", "fin", "commit" }`.
- **`pendientes.json`** (`{"pendientes": [...]}`): la cola de noticias que Jorge eligió para más adelante. Cada una es la noticia tal como la dio el Cronista, con `id` global (`<id del número>/<N>`), `desde` (el número en que se apartó) y `motivo`.
- `numeros/<id>/`: lo de cada post (`noticias.*`, `borrador.*`, `post.json`, `diseno.*`, `vista/`, `capturas/`, `publicacion.md`, `estilo.*`) y `decisiones.json`:
  ```json
  { "noticias": [ { "ronda": 1, "decision": "aprobar|cambios|descartar", "elegidas": ["N1"], "pendientes": ["N3", "N5"], "nota": "…", "fecha": "…", "desde": "chat|monasterio" } ],
    "texto": [ … ], "diseno": [ … ] }
  ```
  `cambios` = el mismo agente lo rehace con la nota de Jorge (la nota es obligatoria); `descartar` = el post se abandona.

Si falta algo, créalo (`estado.json` con fase `sin-numero`, `indice.json` con `{"numeros": []}`, `pendientes.json` con `{"pendientes": []}`).

## Pasos

1. **Arranque.** `git status -sb`: si hay cambios sin commit, enséñaselos a Jorge y pregunta antes de seguir. Lee `estado.json`:
   - si hay un número en `decidido-…`, retómalo desde ese punto (paso 3, 5 o 7);
   - si está en otra fase sin cerrar, ofrece retomarlo o darlo por interrumpido;
   - si no, crea `numeros/<hoy>/` (si existe, añade `-2`), con `numero` = el último de `indice.json` + 1; añádelo al índice.
2. **Cronista** (fase `investigacion`): lánzalo con la carpeta del número (y la nota de Jorge si es otra ronda). Empieza por las pendientes y propone una para el post. Comprueba que existen `noticias.md` y `noticias.json`.
3. **Consulta 1 · Noticias** (fase `esperando-noticias`, Cronista `pendiente-aprobacion`). Enséñale a Jorge **una sección numerada por noticia** («1. Título»; primero las pendientes), con todo junto: resumen, por qué interesa, fuente con fecha de publicación, ámbito, fichas del catálogo relacionadas y, al final de cada una, una línea con estado, si es pendiente, si el Cronista la propone para este post y qué se le pide. Pídele, para cada una: **este post**, **pendiente** o **descartar** (por ejemplo, «1 post; 3 y 5 pendientes; el resto fuera»). Lo normal es una sola para el post. También puede pedir cambios («cambios: busca más de la Junta») o descartar el número.
   **Al aprobar**, actualiza `pendientes.json`: añade las que marcó como pendientes (con `id` global, `desde` y `motivo`) y quita las que han entrado en este post o ha descartado.
4. **Redactor** (fase `redaccion`) con las elegidas. Comprueba `borrador.json` y `borrador.md`.
5. **Consulta 2 · Texto** (fase `esperando-texto`). Enséñale el post completo por secciones numeradas («1. Subtítulo»), como se leerá, con su fuente. Pídele **aprobar**, **cambios** (con lo que quiere) o **descartar**. También puede **reescribir textos con sus palabras**, aquí o en la pestaña «Gaceta» del monasterio. Si lo hace en el chat, copia antes `borrador.json` a `borrador-lucas-r<ronda>.json`. Después pon sus textos **literales** en `borrador.json` (solo los campos de texto: titular, entradilla, `etiqueta`, `titulo`, `texto`, `intro`, `ejemplo` y los de `items` y `pasos`), añade `"editado_por_jorge": true` y anota `editado_por_jorge` (cuántos textos) en su decisión. Si en el monasterio edita y aprueba, el servidor ya lo ha hecho.
6. **Maquetador, modo diseño** (fase `maquetacion`), con el número. Comprueba `post.json`, `vista/index.html` y la captura.
7. **Consulta 3 · Diseño** (fase `esperando-diseno`). Primero, **las tres miniaturas** que propone Fray Isidoro (`diseno.json` → `opciones`): ábrelas con Read y enséñaselas numeradas, con lo que se ve, la foto original y su licencia. Jorge elige una («la 2») o pide otras; sin miniatura elegida no se aprueba. Anota la elegida en la decisión (`"miniatura": "2"`). Enséñale también, aparte, cualquier otra imagen del post (`imagenes`). Después, dale la vista previa (`http://127.0.0.1:8020/didakora/agentes/boletin/numeros/<id>/vista/`, que se ve con el servidor del monasterio o con `python -m http.server 8020` desde la carpeta padre) y la captura del móvil (ábrela con Read para describirla). Dile también, por sección numerada, si lleva caja de color e imagen o vídeo (con su licencia). Pídele **aprobar**, **cambios** o **descartar**.
8. **Maquetador, modo publicación** (fase `publicacion`). Comprueba el commit con `git show --stat HEAD`. Pon el número en `publicado` con `fin`, `slug` y `commit` (también en `indice.json`) y los tres agentes en `completado`.
9. **Auditor, modo boletín** (también si el número se descarta, siempre que Jorge haya decidido algo). Pon `"auditor": {"estado": "en-ejecucion", …}` en los `agentes` de `agentes/boletin/estado.json` (no en el `estado.json` del catálogo) y lánzalo con la carpeta del número **diciéndole que es el modo boletín**. Anota los cambios de Jorge al texto de Fray Lucas y sus decisiones en `estilo.md` y pone al día `agentes/boletin/estilo-jorge.md`. Al terminar, ponlo en `completado` con una nota corta (cuántos textos cambió Jorge y cuántas reglas nuevas).

**En cada consulta**: registra la decisión en `decisiones.json` (`desde: "chat"`), con sus palabras en `nota`. Jorge también puede decidir **en el monasterio** (Scriptorium de la Gaceta, o la pestaña «Gaceta» del Libro): díselo. Antes de terminar el turno, deja una espera en segundo plano (Bash con `run_in_background`) que acabe cuando el monasterio escriba la decisión:
`until node -e "const e=require('./agentes/boletin/estado.json');process.exit(String(e.numero.fase).startsWith('decidido-')?0:1)"; do sleep 5; done; echo decidido`
**Termina tu turno ahí.** Sigue cuando Jorge responda en el chat (para la espera con TaskStop) o cuando acabe la espera (lee la última entrada de `decisiones.json`, ya escrita por el servidor; resúmesela). Si la decisión de noticias viene del monasterio, actualiza tú `pendientes.json` con sus `pendientes` como en el paso 3. Una respuesta ambigua no es una aprobación: pregunta. Con `cambios`, sube `ronda`, relanza al mismo agente con la nota y vuelve a la misma consulta. Con `descartar`, pon el número en `descartado` y los agentes en `en-espera`; después, haz el paso 9 (Auditor) y termina.

**Cierre.** Mensaje corto para Jorge: título del post, commit, cuántas noticias quedan pendientes, lo que ha aprendido Fray Custodio de su forma de escribir y que para publicarlo en la web debe escribir él `! git push` (el push está bloqueado para los agentes). Si hay `para_el_rastreador` en `noticias.json`, recuérdale que puede pasárselas al próximo `/ciclo`.

Si un agente falla, márcalo `error` con la nota, cuéntaselo a Jorge y pregunta si seguir.

## Modo monasterio

Te ha lanzado la **campanilla del Scriptorium de la Gaceta** (`agentes/monasterio/servidor.py`) sin interfaz: nadie lee el chat. Jorge lo sigue y decide en el monasterio.

- Pon `"origen": "monasterio"` en `estado.json` → `numero` al crear o retomar el número. Actualiza los JSON con Read, Edit y Write (no con `node -e`). Python se llama `python` a secas y el monasterio ya sirve la web en el puerto 8020: díselo al Maquetador.
- Donde el flujo normal pregunta, **no preguntes**: si hay cambios sin commit, otro número a medias en una fase que no sea `decidido-…` o un agente falla, pon el número en `interrumpido` (o el agente en `error`) con una `nota` que explique qué debe hacer Jorge. Después, termina.
- **En cada consulta** deja la fase `esperando-…` y termina **sin espera en segundo plano**: el servidor te vuelve a lanzar en cuanto Jorge decida.
- Tu último mensaje, en una o dos frases (queda en el registro del monasterio).
