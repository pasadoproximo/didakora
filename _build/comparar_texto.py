# Compara el texto de Fray Lucas (borrador-lucas-r<ronda>.json) con el que aprobó Jorge (borrador.json) campo a campo.
# Lo usa el Auditor al cerrar cada número del boletín para anotar cómo escribe Jorge (agentes/boletin/estilo-jorge.md).
#   python _build/comparar_texto.py agentes/boletin/numeros/<id>            → informe en Markdown por la salida
# Por cada texto cambiado: dónde está, lo de Lucas, lo de Jorge, palabras quitadas y añadidas y la longitud antes y después.
import difflib, json, os, re, sys

CAMPOS = ("etiqueta", "titulo", "texto", "intro", "ejemplo")

def textos(b):
    """{ruta legible: texto} con todos los campos que Jorge puede editar"""
    out = {"Titular": b.get("titulo", ""), "Entradilla": b.get("entradilla", "")}
    for i, bl in enumerate(b.get("bloques", []), 1):
        for k in CAMPOS:
            if k in bl: out[f"Bloque {i} ({bl.get('tipo')}) · {k}"] = bl[k]
        for lista in ("items", "pasos"):
            for j, it in enumerate(bl.get(lista) or [], 1):
                for k in ("titulo", "texto"):
                    if k in it: out[f"Bloque {i} · {lista[:-1] if lista == 'items' else 'paso'} {j} · {k}"] = it[k]
    return out

palabras = lambda s: re.findall(r"\w+|[^\w\s]", str(s or ""))

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2: sys.exit("uso: python _build/comparar_texto.py agentes/boletin/numeros/<id>")
    carpeta = sys.argv[1]
    final = json.load(open(os.path.join(carpeta, "borrador.json"), encoding="utf-8"))
    rondas = sorted((f for f in os.listdir(carpeta) if re.fullmatch(r"borrador-lucas-r\d+\.json", f)), key=lambda f: int(re.findall(r"\d+", f)[0]))
    if not rondas: print("Jorge no ha reescrito ningún texto en este número."); return
    for r in rondas:
        lucas = json.load(open(os.path.join(carpeta, r), encoding="utf-8"))
        a, b = textos(lucas), textos(final)
        cambiados = [k for k in a if k in b and a[k].strip() != b[k].strip()]
        print(f"## {r} → borrador.json: {len(cambiados)} de {len(a)} textos cambiados\n")
        for k in cambiados:
            pa, pb = palabras(a[k]), palabras(b[k])
            quitadas, puestas = [], []
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, pa, pb).get_opcodes():
                if op in ("replace", "delete"): quitadas.append(" ".join(pa[i1:i2]))
                if op in ("replace", "insert"): puestas.append(" ".join(pb[j1:j2]))
            print(f"### {k}\n- Lucas ({len(a[k].split())} palabras): {a[k]!r}\n- Jorge ({len(b[k].split())} palabras): {b[k]!r}")
            if quitadas: print(f"- Quita: {' | '.join(quitadas)}")
            if puestas: print(f"- Pone: {' | '.join(puestas)}")
            print()

if __name__ == "__main__":
    main()
