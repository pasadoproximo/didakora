---
name: ciclo
description: Ciclo manual de mantenimiento de didákora con los agentes Rastreador, Coordinador editorial, Administrador web y Auditor, con pausa obligatoria para que Jorge apruebe las propuestas.
argument-hint: "[prueba]"
disable-model-invocation: true
---

Ejecuta el ciclo de mantenimiento de didákora. Tú (la sesión principal) eres quien coordina: los agentes no pueden hablar con Jorge, así que **la pausa de aprobación la haces tú**. No invoques al Optimizador.

Si el argumento es `prueba` ($ARGUMENTS), sigue la sección «Modo prueba» en lugar de este flujo.

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

1. **Arranque.** `git status -sb`. Si hay cambios sin commit, enséñaselos a Jorge y pregunta antes de seguir. Lee `agentes/estado.json`: si hay un ciclo sin cerrar, ofrece retomarlo desde su fase o darlo por interrumpido. Crea `agentes/ciclos/AAAA-MM-DD/` (si ya existe, añade `-2`).
2. **Enlaces.** `python _build/comprobar_enlaces.py --json agentes/ciclos/<ciclo>/enlaces.json` (en este equipo: `%LOCALAPPDATA%/Programs/Python/Python312/python.exe`).
3. **Rastreador.** Lánzalo con la ruta de la carpeta del ciclo. Al terminar, comprueba que existe `hallazgos.md`.
4. **Coordinador editorial.** Lánzalo con la carpeta del ciclo. Comprueba que existen `propuestas.md` y las tareas nuevas en `tareas.json`.
5. **Pausa de aprobación.** Pon el ciclo en `esperando-aprobacion` y enseña a Jorge **una sola tabla con toda la información** de cada propuesta (qué se cambia, motivo, fuentes, dudas y opciones si las hay), sin detalles sueltos debajo: Jorge no quiere tener que subir y bajar. Pídele que diga, para cada una: **aprobar**, **rechazar** o **editar** (con su cambio). Si no hay propuestas, salta al paso 8. **Termina tu turno aquí y no sigas hasta que Jorge responda.** Una respuesta ambigua no es una aprobación: pregunta.
6. **Registra la decisión** en `tareas.json`: `estado` `aprobada` o `rechazada`, `decision` con la fecha y `nota_jorge` con sus palabras si edita o explica algo.
7. **Administrador web** con la lista de tareas aprobadas; después, **Auditor** con la carpeta del ciclo. Si el Administrador para por un problema, enséñaselo a Jorge antes de auditar.
8. **Cierre.** Escribe `resumen.md` en la carpeta del ciclo (qué se encontró, qué se aprobó y rechazó, commits, resultado de la auditoría, pendientes), pon el ciclo en `cerrado` y los agentes en `completado` o `no-ejecutado` según corresponda.

Termina con un mensaje corto para Jorge, también en una tabla con toda la información (por tarea: resultado, commit, auditoría, pendiente), y, si hay commits, que para publicar debe revisar y escribir él mismo `! git push` (el push está bloqueado para los agentes).

Si un agente falla, márcalo como `error` con la nota, cuéntaselo a Jorge y pregunta si seguir. Nunca marques una tarea como hecha sin evidencia.

## Modo prueba

Sirve para comprobar el flujo sin gastar búsquedas ni tocar el catálogo. Trabaja en `agentes/prueba/` (bórrala antes si existe) con su propio `estado.json` y `tareas.json`, nunca con los reales.

1. Escribe a mano en `agentes/prueba/ciclo/hallazgos.md` tres hallazgos **marcados como ficticios**: uno nuevo, uno duplicado de una herramienta del catálogo y uno de una herramienta que ha cambiado de dominio.
2. Lanza al Coordinador editorial indicándole que use `agentes/prueba/` en lugar de `agentes/` y que no use WebFetch. Comprueba que descarta el duplicado y que deja las tareas en `propuesta`.
3. Haz la pausa de aprobación como en el ciclo real.
4. No lances al Administrador: describe qué cambiaría con lo aprobado. Lanza al Auditor solo para que verifique `agentes/prueba/` y las tareas (sin build).
5. Informa de qué ha funcionado y qué no. `git status` debe seguir limpio.
