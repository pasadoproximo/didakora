---
name: ciclo
description: Ciclo manual de mantenimiento de didákora con los agentes Rastreador, Coordinador editorial, Administrador web y Auditor, con pausa obligatoria para que Jorge apruebe las propuestas.
argument-hint: "[prueba]"
disable-model-invocation: true
---

Ejecuta el ciclo de mantenimiento de didákora. Tú (la sesión principal) eres quien coordina: los agentes no pueden hablar con Jorge, así que **la pausa de aprobación la haces tú**. No invoques al Optimizador.

Si el argumento es `prueba` ($ARGUMENTS), sigue la sección «Modo prueba» en lugar de este flujo. Si es `monasterio`, sigue el flujo normal con los cambios de la sección «Modo monasterio».

## Estado real

Lleva `agentes/estado.json` al día **antes y después** de cada paso; es lo que leerá el panel visual. Nunca escribas un estado que no sea cierto.

```json
{ "actualizado": "AAAA-MM-DDTHH:MM", 
  "ciclo": { "id": "AAAA-MM-DD", "fase": "sin-ciclo|rastreo|propuestas|esperando-aprobacion|implementacion|auditoria|cerrado|interrumpido", "inicio": "…", "fin": null },
  "agentes": { "rastreador": { "estado": "en-espera|en-ejecucion|completado|error|pendiente-aprobacion|no-ejecutado", "desde": "…", "nota": "" },
               "coordinador-editorial": {…}, "administrador-web": {…}, "auditor": {…}, "optimizador": {…} } }
```

Las horas van siempre en UTC con `Z` (`new Date().toISOString()`, p. ej. `2026-10-21T10:42:00Z`); el panel las pasa a hora local.

Lleva también `agentes/ciclos/indice.json` (`{"ciclos": [...]}`): al arrancar añade `{ "id", "inicio", "fin": null, "fase", "archivos": [] }` y en cada cambio de fase actualiza `fase` y `archivos` (los `.md` que ya existen en la carpeta del ciclo). Es lo que usa el panel del monasterio (`agentes/monasterio/`) para el historial.

Si `agentes/` o alguno de sus archivos no existe, créalo (con `tareas.json` = `{"tareas": []}`).

## Pasos

1. **Arranque.** `git status -sb`. Si hay cambios sin commit, enséñaselos a Jorge y pregunta antes de seguir. Lee `agentes/estado.json`: si hay un ciclo sin cerrar, ofrece retomarlo desde su fase o darlo por interrumpido. Si está en `esperando-aprobacion` y ya no quedan tareas suyas en `propuesta` (Jorge decidió en el monasterio), retómalo directamente desde el paso 6. Crea `agentes/ciclos/AAAA-MM-DD/` (si ya existe, añade `-2`).
2. **Enlaces.** `python _build/comprobar_enlaces.py --json agentes/ciclos/<ciclo>/enlaces.json` (`python` ya es Python 3.12 en este equipo; úsalo así, sin la ruta completa).
3. **Rastreador.** Lánzalo con la ruta de la carpeta del ciclo. Al terminar, comprueba que existe `hallazgos.md`.
4. **Coordinador editorial.** Lánzalo con la carpeta del ciclo. Comprueba que existen `propuestas.md` y las tareas nuevas en `tareas.json`.
5. **Pausa de aprobación.** Pon el ciclo en `esperando-aprobacion` y enseña a Jorge **una sección numerada por herramienta** («1. Nombre de la herramienta») con toda su información junta (qué se cambia, motivo, fuentes, dudas y opciones si las hay) y, **al final de cada sección, una línea** con tipo, prioridad, si es propuesta, a vigilar o descartado y qué se le pide. Nada de detalles sueltos en otro sitio: Jorge no quiere subir y bajar; responde por número («1 A, 2 rechazar»). Pídele que diga, para cada una: **aprobar**, **rechazar** o **editar** (con su cambio). Si no hay propuestas, salta al paso 8.
   Jorge puede decidir **aquí o en el monasterio** (`/monasterio`, tablón del claustro o Fray Anselmo): díselo. Antes de terminar el turno, deja una espera en segundo plano (Bash con `run_in_background`) que acabe cuando no quede ninguna tarea del ciclo en `propuesta`:
   `until node -e "const t=require('./agentes/tareas.json').tareas.filter(x=>x.ciclo==='<ciclo>');process.exit(t.some(x=>x.estado==='propuesta')?1:0)"; do sleep 5; done; echo decidido`
   **Termina tu turno aquí.** Sigue solo cuando Jorge responda en el chat (entonces para la espera con TaskStop) o cuando la espera termine (decidió en el monasterio). Una respuesta ambigua no es una aprobación: pregunta.
6. **Registra la decisión** en `tareas.json`: `estado` `aprobada` o `rechazada`, `decision` con la fecha y `nota_jorge` con sus palabras si edita o explica algo. Si decidió en el monasterio, el servidor ya lo ha escrito (`decision` «… desde el monasterio», `nota_jorge` con la opción y su nota): compruébalo sin reescribirlo y resúmele en el chat lo que decidió.
7. **Administrador web** con la lista de tareas aprobadas; después, **Auditor** con la carpeta del ciclo. Si el Administrador para por un problema, enséñaselo a Jorge antes de auditar.
8. **Cierre.** Escribe `resumen.md` en la carpeta del ciclo (qué se encontró, qué se aprobó y rechazó, commits, resultado de la auditoría, pendientes), pon el ciclo en `cerrado` y los agentes en `completado` o `no-ejecutado` según corresponda.

Termina con un mensaje corto para Jorge, con el mismo formato numerado (por tarea: resultado, commit, auditoría y, al final de cada una, su estado y lo pendiente). Si hay commits, dile que para publicar debe revisar y escribir él mismo `! git push` (el push está bloqueado para los agentes).

Si un agente falla, márcalo como `error` con la nota, cuéntaselo a Jorge y pregunta si seguir. Nunca marques una tarea como hecha sin evidencia.

## Modo monasterio

Te ha lanzado la campana del monasterio (`agentes/monasterio/servidor.py`) sin interfaz: **nadie lee el chat** y no puedes preguntar. Jorge lo sigue todo en el monasterio, así que lo que importa es lo que escribes en `agentes/`.

- Pon `"origen": "monasterio"` en `estado.json` → `ciclo` al arrancar (el servidor lo usa para reanudar el ciclo cuando Jorge decida).
- Actualiza `estado.json`, `ciclos/indice.json` y `tareas.json` con las herramientas Read, Edit y Write (no con `node -e`). Python se llama `python` a secas y el monasterio ya sirve la web en el puerto 8020: díselo al Auditor y al Administrador en su encargo.
- Donde el flujo normal pregunta a Jorge, **no preguntes**: si hay cambios sin commit, si hay otro ciclo a medias en una fase distinta de `esperando-aprobacion` o si un agente falla, deja el ciclo en `interrumpido` (o el agente en `error`) con una `nota` que explique qué ha pasado y qué debe hacer Jorge. Después termina.
- **Pausa (paso 5):** deja las propuestas en `tareas.json` (con `cambio`, `motivo`, `dudas` y `opciones`), pon el ciclo en `esperando-aprobacion` y termina **sin espera en segundo plano**. El servidor te volverá a lanzar en cuanto Jorge selle todos los pergaminos.
- **Al reanudar:** si el ciclo está en `esperando-aprobacion` y ya no quedan tareas suyas en `propuesta`, sigue desde el paso 6 (las decisiones ya están escritas).
- **Al terminar:** el resumen va en `resumen.md`; tu último mensaje, en una o dos frases (queda en el registro del monasterio). El push sigue siendo cosa de Jorge.

## Modo prueba

Sirve para comprobar el flujo sin gastar búsquedas ni tocar el catálogo. Trabaja en `agentes/prueba/` (bórrala antes si existe) con su propio `estado.json` y `tareas.json`, nunca con los reales.

1. Escribe a mano en `agentes/prueba/ciclo/hallazgos.md` tres hallazgos **marcados como ficticios**: uno nuevo, uno duplicado de una herramienta del catálogo y uno de una herramienta que ha cambiado de dominio.
2. Lanza al Coordinador editorial indicándole que use `agentes/prueba/` en lugar de `agentes/` y que no use WebFetch. Comprueba que descarta el duplicado y que deja las tareas en `propuesta`.
3. Haz la pausa de aprobación como en el ciclo real.
4. No lances al Administrador: describe qué cambiaría con lo aprobado. Lanza al Auditor solo para que verifique `agentes/prueba/` y las tareas (sin build).
5. Informa de qué ha funcionado y qué no. `git status` debe seguir limpio.
