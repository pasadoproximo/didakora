---
name: boletin
description: Ciclo del boletín de didákora, aparte del ciclo del catálogo. Cronista (noticias) → Jorge aprueba → Redactor (texto) → Jorge aprueba → Maquetador (diseño) → Jorge aprueba → publicación con commit local.
argument-hint: "[monasterio]"
disable-model-invocation: true
---

Ejecuta el ciclo del boletín de didákora. Es **independiente de `/ciclo`**: no lances al Rastreador, al Coordinador, al Administrador ni al Auditor. Tú (la sesión principal) coordinas y haces las **tres pausas** de aprobación: los agentes no hablan con Jorge. Si el argumento es `monasterio` ($ARGUMENTS), sigue además la sección «Modo monasterio».

## Archivos (todos privados, en `agentes/boletin/`)

- `estado.json` (lo lee el monasterio; llévalo al día **antes y después** de cada paso, horas en UTC con `Z`):
  ```json
  { "actualizado": "…", "numero": { "id": "AAAA-MM-DD", "numero": 1, "fase": "…", "ronda": 1, "inicio": "…", "fin": null, "origen": "chat|monasterio", "nota": "" },
    "agentes": { "cronista": { "estado": "…", "desde": "…", "nota": "" }, "redactor": {…}, "maquetador": {…} } }
  ```
  Fases: `sin-numero`, `investigacion`, `esperando-noticias`, `redaccion`, `esperando-texto`, `maquetacion`, `esperando-diseno`, `publicacion`, `publicado`, `descartado`, `interrumpido` y, mientras el monasterio espera a que lo retomes, `decidido-noticias`, `decidido-texto`, `decidido-diseno`. Estados de agente: los de `/ciclo` (`en-espera`, `en-ejecucion`, `completado`, `error`, `pendiente-aprobacion`, `no-ejecutado`).
- `indice.json` (`{"numeros": [...]}`): una entrada por número `{ "id", "numero", "titulo", "fase", "inicio", "fin", "commit" }`.
- `numeros/<id>/`: lo de cada número (`noticias.*`, `borrador.*`, `boletin.json`, `diseno.*`, `vista/`, `capturas/`, `publicacion.md`) y `decisiones.json`:
  ```json
  { "noticias": [ { "ronda": 1, "decision": "aprobar|cambios|descartar", "elegidas": ["N1", "N3"], "nota": "…", "fecha": "…", "desde": "chat|monasterio" } ],
    "texto": [ … ], "diseno": [ … ] }
  ```
  `cambios` = el mismo agente lo rehace con la nota de Jorge (la nota es obligatoria); `descartar` = el número se abandona.

Si falta algo, créalo (`estado.json` con fase `sin-numero`, `indice.json` con `{"numeros": []}`).

## Pasos

1. **Arranque.** `git status -sb`: si hay cambios sin commit, enséñaselos a Jorge y pregunta antes de seguir. Lee `estado.json`:
   - si hay un número en `decidido-…`, retómalo desde ese punto (paso 3, 5 o 7);
   - si está en otra fase sin cerrar, ofrece retomarlo o darlo por interrumpido;
   - si no, crea `numeros/<hoy>/` (si existe, añade `-2`), con `numero` = el último de `indice.json` + 1; añádelo al índice.
2. **Cronista** (fase `investigacion`): lánzalo con la carpeta del número (y la nota de Jorge si es otra ronda). Comprueba que existen `noticias.md` y `noticias.json`.
3. **Consulta 1 · Noticias** (fase `esperando-noticias`, Cronista `pendiente-aprobacion`). Enséñale a Jorge **una sección numerada por noticia** («1. Título»), con todo junto: resumen, por qué interesa, fuente con fecha, ámbito y formato propuesto, fichas del catálogo relacionadas y, al final de cada una, una línea con estado, si el Cronista la recomienda y qué se le pide. Pídele: qué noticias entran («1, 3, 5» o «las recomendadas»); si quiere cambios («cambios: busca más de la Junta») o descartar el número.
4. **Redactor** (fase `redaccion`) con las elegidas. Comprueba `borrador.json` y `borrador.md`.
5. **Consulta 2 · Texto** (fase `esperando-texto`). Enséñale el texto completo por bloques numerados («1. Título del bloque»), como se leerá, con su fuente al final de cada uno. Pídele **aprobar**, **cambios** (con lo que quiere) o **descartar**.
6. **Maquetador, modo diseño** (fase `maquetacion`), con el número del boletín. Comprueba `boletin.json`, `vista/index.html` y la captura.
7. **Consulta 3 · Diseño** (fase `esperando-diseno`). Dale la vista previa (`http://127.0.0.1:8020/didakora/agentes/boletin/numeros/<id>/vista/`, que se ve con el servidor del monasterio o con `python -m http.server 8020` desde la carpeta padre), la captura del móvil (ábrela con Read para describirla); y, por bloque numerado, su tipo, tono e imagen o vídeo con licencia. Pídele **aprobar**, **cambios** o **descartar**.
8. **Maquetador, modo publicación** (fase `publicacion`). Comprueba el commit con `git show --stat HEAD`. Pon el número en `publicado` con `fin` y `commit` y los tres agentes en `completado`.

**En cada consulta**: registra la decisión en `decisiones.json` (`desde: "chat"`), con sus palabras en `nota`. Jorge también puede decidir **en el monasterio** (Scriptorium de la Gaceta, o la pestaña «Gaceta» del Libro): díselo. Antes de terminar el turno, deja una espera en segundo plano (Bash con `run_in_background`) que acabe cuando el monasterio escriba la decisión:
`until node -e "const e=require('./agentes/boletin/estado.json');process.exit(String(e.numero.fase).startsWith('decidido-')?0:1)"; do sleep 5; done; echo decidido`
**Termina tu turno ahí.** Sigue cuando Jorge responda en el chat (para la espera con TaskStop) o cuando acabe la espera (lee la última entrada de `decisiones.json`, ya escrita por el servidor; resúmesela). Una respuesta ambigua no es una aprobación: pregunta. Con `cambios`, sube `ronda`, relanza al mismo agente con la nota y vuelve a la misma consulta. Con `descartar`, pon el número en `descartado` y los agentes en `en-espera`; después, termina.

**Cierre.** Mensaje corto para Jorge: título y número, commit y que para publicarlo en la web debe escribir él `! git push` (el push está bloqueado para los agentes). Si hay `para_el_rastreador` en `noticias.json`, recuérdale que puede pasárselas al próximo `/ciclo`.

Si un agente falla, márcalo `error` con la nota, cuéntaselo a Jorge y pregunta si seguir.

## Modo monasterio

Te ha lanzado la **campanilla del Scriptorium de la Gaceta** (`agentes/monasterio/servidor.py`) sin interfaz: nadie lee el chat. Jorge lo sigue y decide en el monasterio.

- Pon `"origen": "monasterio"` en `estado.json` → `numero` al crear o retomar el número. Actualiza los JSON con Read, Edit y Write (no con `node -e`). Python se llama `python` a secas y el monasterio ya sirve la web en el puerto 8020: díselo al Maquetador.
- Donde el flujo normal pregunta, **no preguntes**: si hay cambios sin commit, otro número a medias en una fase que no sea `decidido-…` o un agente falla, pon el número en `interrumpido` (o el agente en `error`) con una `nota` que explique qué debe hacer Jorge. Después, termina.
- **En cada consulta** deja la fase `esperando-…` y termina **sin espera en segundo plano**: el servidor te vuelve a lanzar en cuanto Jorge decida.
- Tu último mensaje, en una o dos frases (queda en el registro del monasterio).
