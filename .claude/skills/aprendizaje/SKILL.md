---
name: aprendizaje
description: Registra una corrección o preferencia de Jorge para el sistema de agentes de Didákora, con la propuesta de cambio mínimo, sin aplicarla.
argument-hint: "[corrección o preferencia]"
disable-model-invocation: true
---

Registra en `agentes/aprendizajes.md` esta corrección o preferencia de Jorge: $ARGUMENTS

Añade una entrada al final (crea el archivo si no existe):

```markdown
## AAAA-MM-DD · título corto
- Corrección: lo que ha dicho Jorge, con sus palabras.
- Contexto: ciclo, tarea o archivo donde ocurrió.
- Afecta a: agente(s), instrucción, validación o procedimiento.
- Cambio mínimo propuesto: texto o diff concreto.
- Cómo comprobarlo: qué debería pasar en el próximo ciclo.
- Estado: pendiente
```

Los agentes leen este archivo en cada ciclo y deben respetar lo registrado, pero **no modifiques sus instrucciones**: el cambio propuesto lo aplica Jorge o el Optimizador con su aprobación. No guardes secretos ni datos personales innecesarios. No ejecutes al Optimizador.
