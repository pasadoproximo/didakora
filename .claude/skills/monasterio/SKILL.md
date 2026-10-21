---
name: monasterio
description: Abre el monasterio de didákora (juego local para trabajar con los agentes) en el navegador, arrancando su servidor si hace falta.
disable-model-invocation: true
---

Abre el monasterio (`agentes/monasterio/`): Jorge recorre el monasterio, habla con los monjes-agentes, lee los informes y decide sobre las propuestas. No cambies nada: solo lo abres.

1. Comprueba si el servidor del monasterio ya responde: `curl -s http://127.0.0.1:8020/api/salud` debe devolver `"servidor": "monasterio"`.
2. Si no responde, arráncalo **en segundo plano** (con `run_in_background`):
   `"$LOCALAPPDATA/Programs/Python/Python312/python.exe" -I "C:/Users/USER/Desktop/El pasado próximo/didakora/agentes/monasterio/servidor.py" 8020`
   y repite la comprobación hasta que responda (unos segundos). Si el puerto 8020 está ocupado por otra cosa (responde, pero no es el monasterio), díselo a Jorge y no lo cierres sin preguntar. Si `agentes/monasterio/servidor.py` no existe, díselo y para.
3. Ábrelo en el navegador de Jorge: `cmd //c start "" "http://127.0.0.1:8020/didakora/agentes/monasterio/"`.
4. Responde en una línea: que está abierto, la dirección y que el servidor se cierra al cerrar esta sesión de Claude Code (o con «para el servidor del monasterio»).

El servidor solo escucha en 127.0.0.1, rechaza peticiones de otras webs y únicamente puede escribir decisiones sobre tareas en «propuesta» (`agentes/tareas.json`) y aprendizajes (`agentes/aprendizajes.md`). No ejecuta comandos.
