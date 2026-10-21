---
name: optimizar
description: Invoca solo al Optimizador de didákora para que proponga mejoras a los agentes a partir de los registros. Nunca aplica cambios.
disable-model-invocation: true
---

Invoca únicamente al agente `optimizador`. No ejecutes el ciclo ni otros agentes.

1. Pon `optimizador` en `en-ejecucion` en `agentes/estado.json` (sin tocar el resto) y lánzalo.
2. Cuando termine, ponlo en `completado` (o `error`, con la nota) y enseña a Jorge un resumen de cada propuesta (M1, M2…) con la ruta del informe en `agentes/mejoras/`.
   Si te ha lanzado el monasterio (argumento `monasterio`: $ARGUMENTS), nadie lee el chat: actualiza `estado.json` con Read y Edit, no preguntes nada y termina con una frase; Jorge leerá las mejoras en el monasterio.
3. No apliques ninguna propuesta. Si Jorge aprueba una, aplica solo ese cambio, enséñale el diff, ejecuta las pruebas pertinentes y anota en el informe de mejoras «M… aplicada el AAAA-MM-DD» o «rechazada». Si el cambio amplía el alcance o implica coste o permisos, para y pregunta.
