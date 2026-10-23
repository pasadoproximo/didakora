---
name: boletin
description: Actualidad (el blog de Didákora), aparte del ciclo del catálogo. «buscar»: el Cronista trae noticias y Jorge guarda las que le interesan. «encargar»: un post con una o varias noticias guardadas. «post <id>»: lleva un post por sus pasos (Redactor → texto → tres miniaturas → miniatura elegida → el post con ella → visto bueno → publicación con commit local). Varios posts pueden ir a la vez.
argument-hint: "[monasterio] buscar | encargar <ids> | post <id>"
disable-model-invocation: true
---

Coordina **Actualidad**, la sección de blog de Didákora (`/actualidad/`). Es **independiente de `/ciclo`**: no lances al Rastreador, al Coordinador ni al Administrador; al Auditor, solo en su modo boletín. Los agentes no hablan con Jorge: las consultas las haces tú (en el chat) o el monasterio (pestaña «Gaceta» del Libro). Argumentos: $ARGUMENTS. Si empiezan por `monasterio`, sigue además «Modo monasterio».

Hay tres trabajos, que pueden ir a la vez (la búsqueda y hasta dos posts):

- **buscar**: Fray Tomás (Cronista) trae noticias nuevas y repasa las guardadas; Jorge **guarda** las que le interesan. Ahí termina.
- **encargar `<ids>`** (solo en el chat; en el monasterio lo hace el servidor): Jorge elige una o varias **noticias guardadas** y se crea un post. Con una, el post va solo de esa; con varias, **un único post** que reúne la información de todas.
- **post `<id>`**: lleva ese post al siguiente paso según su fase.

## Archivos (privados, en `agentes/boletin/`)

- `busqueda.json`: la búsqueda en curso `{ "id", "fase", "ronda", "inicio", "fin", "origen", "nota", "agentes": { "cronista": {estado, desde, nota} } }`. Fases: `sin-busqueda`, `investigacion`, `esperando-guardar`, `decidido-guardar` (Jorge pidió otra búsqueda), `cerrada`, `descartada`, `interrumpido`. Carpeta de cada búsqueda: `busquedas/<id>/` (`noticias.json`, `noticias.md`, `decisiones.json`).
- `pendientes.json` (`{"pendientes": [...]}`): las **noticias guardadas** de Jorge, con `id` global (`<id de la búsqueda>/<N>`), `desde`, `guardada` y, si ya están en un post, `en_post` (salen de la lista cuando ese post se publica y vuelven a estar libres si se descarta; lo ordena el servidor).
- `numeros/<id>/estado.json`, uno por post: `{ "id", "numero", "fase", "ronda", "inicio", "actualizado", "fin", "origen", "titulo", "slug", "commit", "nota", "agentes": { "redactor", "maquetador", "auditor": {estado, desde, nota} } }`. Fases: `decidido-noticias` (recién encargado), `redaccion`, `esperando-texto`, `decidido-texto`, `miniaturas`, `esperando-miniatura`, `decidido-miniatura`, `maquetacion`, `esperando-diseno`, `decidido-diseno`, `publicacion`, `publicado`, `descartado`, `interrumpido`. En la carpeta del post: `elegidas.json` (las noticias del post), `decisiones.json` (`noticias`, `texto`, `miniatura`, `diseno`: `{ ronda, decision: aprobar|cambios|descartar, nota, fecha, desde, … }`), `borrador.*`, `opciones/`, `diseno.*`, `post.json`, `vista/`, `capturas/`, `publicacion.md` y `estilo.*`.
- `indice.json` (`{"numeros": [...]}`): una entrada por post `{ "id", "numero", "titulo", "slug", "fase", "inicio", "fin", "commit" }`.

Estados de agente: `en-espera`, `en-ejecucion`, `completado`, `error`, `pendiente-aprobacion`, `no-ejecutado`. Horas en UTC con `Z`. Lleva al día **solo el estado de tu trabajo** (la búsqueda o tu post), antes y después de cada paso: puede haber otra sesión trabajando a la vez en otro post.

## buscar

1. Si `busqueda.json` está en `decidido-guardar`, es otra ronda de la misma búsqueda (sube `ronda` y pásale al Cronista la nota de la última decisión). Si no, crea `busquedas/<hoy>/` (si existe, añade `-2`) y pon `busqueda.json` con ese `id`, fase `investigacion` y el Cronista en `en-ejecucion`.
2. Lanza al **Cronista** con la carpeta de la búsqueda. Comprueba `noticias.md` y `noticias.json`.
3. **Consulta · Guardar** (fase `esperando-guardar`, Cronista `pendiente-aprobacion`). En el chat: una sección numerada por noticia nueva (resumen, por qué interesa, fuente con fecha, ámbito, fichas y si la recomienda) y lo que el Cronista anotó de las guardadas (`revision_guardadas`). Jorge dice cuáles **guarda**; añádelas a `pendientes.json` (`id` global, `desde`, `guardada`) y cierra la búsqueda (`cerrada`, Cronista `completado`). Con `cambios`, otra ronda (paso 1). Con `descartar`, `descartada`. En el monasterio lo hace el servidor.

## encargar (chat)

Crea `numeros/<hoy>/` (si existe, `-2`, `-3`…), `numero` = el último de `indice.json` + 1. Escribe `elegidas.json` con las guardadas elegidas (completas), `decisiones.json` con `noticias: [{ decision: "aprobar", elegidas, nota }]`, su `estado.json` en `decidido-noticias` y la entrada del índice; marca esas guardadas con `en_post`. Después sigue como **post `<id>`**.

## post `<id>`

Lee `numeros/<id>/estado.json` y haz **el siguiente paso** según la fase (con `cambios`, sube `ronda` y relanza al mismo agente con la nota de Jorge; con `descartar`, pon el post en `descartado`, los agentes en `en-espera`, haz el Auditor y termina):

- `decidido-noticias` → **Redactor** (fase `redaccion`) con la carpeta del post: escribe un único post con `elegidas.json`. Luego **consulta · Texto** (fase `esperando-texto`): el post entero por secciones numeradas. Jorge aprueba, pide cambios, descarta o **reescribe con sus palabras** (en el chat: copia antes `borrador.json` a `borrador-lucas-r<ronda>.json`, pon sus textos literales solo en los campos de texto, añade `"editado_por_jorge": true` y anota cuántos en su decisión; en el monasterio lo hace el servidor). Al aprobar, pon el `titulo` del post en su `estado.json` y en el índice.
- `decidido-texto` (aprobado) → **Maquetador, modo miniaturas** (fase `miniaturas`). Luego **consulta · Miniatura** (fase `esperando-miniatura`): las tres, numeradas (ábrelas con Read en el chat), con lo que se ve, la foto y su licencia. Jorge elige una (`"miniatura": "2"`) o pide otras.
- `decidido-miniatura` (aprobada) → **Maquetador, modo diseño** (fase `maquetacion`) con la elegida. Luego **consulta · El post con su miniatura** (fase `esperando-diseno`): la miniatura elegida, otras imágenes del post y la vista previa (`http://127.0.0.1:8020/didakora/agentes/boletin/numeros/<id>/vista/`) con sus capturas. Jorge da el visto bueno, pide cambios o descarta.
- `decidido-diseno` (aprobado) → **publicación** (fase `publicacion`):
  1. **Pide turno** para publicar: `curl -s -X POST -H "X-Monasterio: 1" -H "Content-Type: application/json" -d '{"id":"<id>","accion":"pedir"}' http://127.0.0.1:8020/api/boletin/turno`. Si responde `"ocupado"`, otro post está publicando: espera con `sleep 30` y vuelve a pedirlo (hasta 20 veces; si no, deja el post en `interrumpido` con la nota). En el chat, sin servidor, publica directamente.
  2. **Maquetador, modo publicación**. Comprueba el commit con `git show --stat HEAD`.
  3. **Suelta el turno** (`"accion":"soltar"`), aunque algo haya fallado.
  4. Pon el post en `publicado` con `fin`, `slug` y `commit` (también en el índice) y los agentes en `completado`. Las guardadas del post salen de la lista solas (servidor); en el chat, quítalas tú de `pendientes.json`.
  5. **Auditor, modo boletín** (también si el post se descarta, si Jorge decidió algo): ponlo en `en-ejecucion` en los `agentes` de **este post**, lánzalo con la carpeta del post diciéndole que es el modo boletín y, al terminar, `completado` con una nota corta.

**En cada consulta en el chat**: registra la decisión en `decisiones.json` (`desde: "chat"`). Jorge también puede decidir en el monasterio (pestaña «Gaceta»): díselo. Deja una espera en segundo plano hasta que el estado de **ese** post (o de la búsqueda) pase a `decidido-…`:
`until node -e "const e=require('./agentes/boletin/numeros/<id>/estado.json');process.exit(String(e.fase).startsWith('decidido-')?0:1)"; do sleep 5; done; echo decidido`
y termina el turno. Sigue cuando Jorge responda o acabe la espera. Una respuesta ambigua no es una aprobación: pregunta.

**Cierre de un post**: título, commit, lo que ha aprendido Fray Custodio y que para publicarlo en la web Jorge escribe él `! git -C "C:/Users/USER/Desktop/El pasado próximo/didakora" push origin rediseno-2026-10:main` (el push está bloqueado para los agentes).

Si un agente falla, márcalo `error` con la nota en el estado de tu trabajo, cuéntaselo a Jorge y pregunta si seguir.

## Modo monasterio

Te ha lanzado el servidor del monasterio sin interfaz (`/boletin monasterio buscar` o `/boletin monasterio post <id>`): nadie lee el chat. Jorge decide en la pestaña «Gaceta» y el servidor te vuelve a lanzar cuando decide.

- Haz **solo un paso** (hasta la siguiente consulta) y termina **sin espera en segundo plano**. No encargues posts ni toques otros posts ni la búsqueda si te han lanzado para un post.
- **No compruebes `git status` al arrancar**: puede haber otro post publicando. Solo al publicar, con el turno pedido.
- Actualiza los JSON con Read, Edit y Write (no con `node -e`). Python se llama `python` a secas y el monasterio ya sirve la web en el puerto 8020: díselo al Maquetador.
- Donde el flujo normal pregunta, **no preguntes**: si un agente falla, pon tu trabajo en `interrumpido` (o el agente en `error`) con una `nota` que explique qué debe hacer Jorge. Después, termina.
- Tu último mensaje, en una o dos frases (queda en el registro del monasterio).
