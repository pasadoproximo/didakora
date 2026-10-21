---
name: monasterio
description: Abre el panel del monasterio de agentes de didákora en el navegador, arrancando el servidor local si hace falta.
disable-model-invocation: true
---

Abre el panel local del monasterio (`agentes/monasterio/`). No cambies nada: solo lo abres.

1. Comprueba si el servidor ya responde: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8020/didakora/agentes/monasterio/`.
2. Si no responde 200, arráncalo **en segundo plano** (con `run_in_background`) sirviendo la carpeta padre del repo:
   `"$LOCALAPPDATA/Programs/Python/Python312/python.exe" -m http.server 8020 --bind 127.0.0.1 --directory "C:/Users/USER/Desktop/El pasado próximo"`
   y repite la comprobación hasta que responda (unos segundos). Si `agentes/monasterio/index.html` no existe, díselo a Jorge y para.
3. Ábrelo en el navegador de Jorge: `cmd //c start "" "http://127.0.0.1:8020/didakora/agentes/monasterio/"`.
4. Responde en una línea: que está abierto, la dirección y que el servidor se cierra al cerrar esta sesión de Claude Code (o se para con «para el servidor del monasterio»).
