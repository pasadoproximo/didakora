# «Monta tu sesión» (/sesion/): el árbol de preguntas y las recetas de sesión. Propuesta del 23-11-2026: JORGE REVISA LOS TEXTOS.
#
# En qué se basa (fuentes abiertas el 23-11-2026):
# - ABC Learning Design (UCL, tipos de aprendizaje de Laurillard): una sesión se diseña eligiendo y ordenando actividades por lo que
#   hace el alumnado (adquirir, investigar, practicar, debatir, colaborar, producir); no fija cuántas. De ahí las cinco metas del árbol.
# - Modelo pedagógico REA DUA Andalucía (díptico del proyecto): movilizar → activar los conocimientos previos → explorar → estructurar →
#   aplicar y comprobar → concluir y evaluar. Una sesión suelta recoge lo esencial: activar, explorar o aplicar y comprobar.
# - Rosenshine, «Principles of Instruction»: empezar repasando lo anterior, practicar y comprobar a menudo qué se ha entendido.
# - Estructuras cooperativas simples de Pere Pujolàs (programa CA/AC): la 1-2-4 (solo, en pareja, en equipo) para los pasos sin pantalla.
# - Triple E (Liz Kolb): primero la meta, después la herramienta; la tecnología va donde aporta. Por eso hay pasos «sin pantalla».
# - Guía «El debate educativo» (Junta de Andalucía): equipos, tema, roles, búsqueda de información, debate y evaluación.
# - NN/g sobre asistentes: sirven cuando el camino se ramifica; enseñar por dónde vas, dejar volver atrás y recordar las respuestas.
#
# Una receta = los pasos de una sesión. No son siempre tres: cada meta lleva los que le convienen (de 2 a 4). Tipos de paso:
#   {"t": título, "main": True}                    → la idea que buscaba el docente (sale de sus respuestas)
#   {"t": título, "o"/"k"/"m"/"ideas": filtro, "alt": texto} → otra idea del catálogo que acompaña; si ninguna encaja con el aula
#                                                    del docente, el paso se hace sin pantalla con el texto de «alt» (sin «alt», no sale)
#   {"t": título, "voz": texto}                    → paso sin pantalla
# Filtros: o = meta, k = rama, m = momentos (ini, des, fin), ideas = lista cerrada de textos de idea.

# Segunda pregunta según la meta: (pregunta, [(valor, etiqueta)]). En «exp» el valor es la materia; en «eva», el momento.
RAMAS = {
    "exp": ("¿De qué materia?", [("gh", "Geografía e Historia"), ("cm", "Ciencias y Matemáticas"), ("ma", "Música y Arte"), ("tp", "Tecnología y programación"),
                                 ("ll", "Lengua y lectura"), ("", "Vale para cualquier materia")]),
    "cre": ("¿Qué van a crear?", [("v", "Un póster, una presentación o un libro"), ("m", "Un mapa o una línea del tiempo"), ("d", "Un vídeo o una animación"),
                                  ("a", "Un audio o una canción"), ("p", "Un programa, una app o un robot"), ("t", "Un objeto o un espacio en 3D")]),
    "equ": ("¿Para qué se juntan?", [("b", "Para debatir"), ("o", "Para organizar un proyecto"), ("c", "Para pensar y construir algo juntos")]),
    "rep": ("¿Cómo quieres que repasen?", [("j", "Con un juego"), ("e", "Por equipos"), ("r", "Cada uno a su ritmo")]),
    "eva": ("¿En qué momento de la clase?", [("ini", "Antes de empezar el tema"), ("des", "A mitad de la clase"), ("fin", "Al terminar")]),
}
METAS = [("exp", "Explorar un tema", "Investigar, observar y comparar"), ("cre", "Que creen algo", "Un producto hecho por el alumnado"),
         ("equ", "Trabajar en equipo", "Debatir, organizarse o construir juntos"), ("rep", "Repasar", "Practicar lo ya visto"),
         ("eva", "Comprobar qué saben", "Antes, durante o al final"), ("*", "No lo tengo claro", "Proponme una clase completa")]

ACTIVAR = {"t": "Activa lo que ya saben", "m": ["ini"], "alt": "Una pregunta de arranque en la pizarra: ¿qué sabéis ya de esto? Primero la piensa cada uno, luego la comentan por parejas y al final la pone en común el equipo."}
SALIDA = "Una pregunta en un papel antes de salir. Lo que respondan te dice por dónde empezar mañana."
TICKET = {"t": "Comprueba qué se llevan", "o": "eva", "m": ["fin"], "alt": SALIDA}

RECETAS = {
    "*": {"n": "Una clase completa", "d": "Abrir, trabajar y cerrar: el esquema de casi cualquier sesión.",
          "pasos": [ACTIVAR, {"t": "La actividad de la clase", "main": True}, TICKET]},
    "exp": {"n": "Explorar un tema", "d": "Primero sale lo que ya saben, luego exploran y al final compruebas qué se llevan.",
            "pasos": [ACTIVAR, {"t": "Exploran el tema", "main": True}, TICKET]},
    "cre": {"n": "Crear un producto", "d": "Planifican antes de abrir la herramienta y al final lo enseñan. Lo normal es que ocupe más de una sesión.",
            "pasos": [{"t": "Planifican qué van a hacer", "ideas": ["Planificar un proyecto", "Lluvia de ideas por equipos", "Reparto de tareas de un proyecto"],
                       "alt": "En papel, un guion corto: qué van a contar, en qué orden y quién hace cada parte."},
                      {"t": "Lo crean", "main": True},
                      {"t": "Lo enseñan y lo valoran", "ideas": ["Valorar una exposición de compañeros"],
                       "alt": "En galería: cada equipo enseña lo suyo y el resto apunta una cosa que le ha gustado y una pregunta."}]},
    "equ/b": {"n": "Un debate", "d": "El debate se hace de viva voz: la tecnología va antes para preparar los argumentos y después para ver si alguien ha cambiado de opinión.",
              "pasos": [{"t": "Abre la pregunta", "ideas": ["Encuesta para abrir un debate"], "alt": "Lanza la pregunta y pide una primera postura a mano alzada. Apunta el recuento en la pizarra."},
                        {"t": "Preparan los argumentos", "main": True},
                        {"t": "El debate, de viva voz", "voz": "Por equipos y con turnos: presentar la postura, rebatir la contraria y concluir. Quien no habla hace de jurado."},
                        {"t": "Cierra: ¿alguien ha cambiado de opinión?", "ideas": ["Preguntas anónimas al final de la clase", "Pregunta de metacognición al cerrar"],
                         "alt": "Repite el recuento a mano alzada y pregunta a quien haya cambiado qué argumento le convenció."}]},
    "equ/o": {"n": "Organizar un proyecto", "d": "Dos pasos: primero salen todas las ideas y después se ordenan y se reparten.",
              "pasos": [{"t": "Sacan todas las ideas", "ideas": ["Lluvia de ideas por equipos", "Lluvia de ideas para abrir un tema"], "alt": "Lluvia de ideas con notas adhesivas: una idea por nota y todas a la pared."},
                        {"t": "Se organizan y reparten", "main": True}]},
    "equ/c": {"n": "Construir algo juntos", "d": "El trabajo en común y una puesta en común corta para que todos vean lo de todos.",
              "pasos": [{"t": "Trabajan juntos", "main": True},
                        {"t": "Puesta en común", "voz": "Cada equipo cuenta en un minuto qué ha hecho y qué le ha costado más. El resto puede hacer una pregunta."}]},
    "rep/j": {"n": "Repasar jugando", "d": "El juego repasa y una comprobación corta te dice qué sigue flojo.",
              "pasos": [{"t": "Juegan para repasar", "main": True}, {"t": "Comprueba qué sigue flojo", "o": "eva", "m": ["fin"], "alt": SALIDA}]},
    "rep/e": {"n": "Repasar por equipos", "d": "Compiten por equipos y después se corrige entre todos lo que más se ha fallado.",
              "pasos": [{"t": "Repasan por equipos", "main": True},
                        {"t": "Corregid lo más fallado", "voz": "Vuelve a las dos o tres preguntas con más fallos y que un equipo que acertó explique por qué."}]},
    "rep/r": {"n": "Repasar a su ritmo", "d": "Cada uno practica lo que necesita y al final compruebas cómo ha ido.",
              "pasos": [{"t": "Practican a su ritmo", "main": True}, {"t": "Comprueba cómo ha ido", "o": "eva", "m": ["fin"], "alt": SALIDA}]},
    "eva/ini": {"n": "Ver qué saben antes de empezar", "d": "Una sola herramienta. Lo importante es lo que haces después con lo que salga.",
                "pasos": [{"t": "Pregunta antes de explicar", "main": True},
                          {"t": "Ajusta la clase", "voz": "Lo que casi todos saben, pásalo rápido. Dedica el tiempo a lo que ha salido flojo o equivocado."}]},
    "eva/des": {"n": "Comprobar a mitad de clase", "d": "Una pregunta rápida para decidir si sigues o vuelves atrás.",
                "pasos": [{"t": "Para y pregunta", "main": True},
                          {"t": "Decide con lo que salga", "voz": "Si la mayoría acierta, sigue. Si no, explícalo de otra manera antes de avanzar."}]},
    "eva/fin": {"n": "Ticket de salida", "d": "Una comprobación corta al terminar. Sirve si mañana la usas.",
                "pasos": [{"t": "Pregunta antes de salir", "main": True},
                          {"t": "Úsalo mañana", "voz": "Guarda las respuestas y empieza la clase siguiente por lo que más se ha fallado."}]},
}

FUENTES = [("ABC Learning Design (UCL)", "https://blogs.ucl.ac.uk/abc-ld/", "una sesión se diseña ordenando lo que hace el alumnado: investigar, practicar, debatir, colaborar o producir"),
           ("Modelo pedagógico REA DUA Andalucía", "https://edea.juntadeandalucia.es/bancorecursos/file/64bdd7d0-8dac-4344-bfdc-d009ce0e6000/1/REA_Diptico_sin_enlaces.pdf", "movilizar, activar lo que ya saben, explorar, estructurar, aplicar y comprobar, concluir y evaluar"),
           ("Guía «El debate educativo» (Junta de Andalucía)", "https://www.juntadeandalucia.es/educacion/eaprendizaje/wp-content/uploads/2026/01/GUIA-DE-ASESORAMIENTO-DIDACTICO-EL-DEBATE-EDUCATIVO.pdf", "los pasos de un debate en el aula"),
           ("Principios de instrucción de Rosenshine", "https://www.stmarys.ac.uk/partnerships/docs/research-and-literature-summaries/rl-summary-rosenshines-principles-of-instruction.pdf", "repasar al empezar y comprobar a menudo qué se ha entendido"),
           ("Estructuras cooperativas de Pere Pujolàs (programa CA/AC)", "https://www.orientacionandujar.es/wp-content/uploads/2013/08/el-programa-ca-ac-pere-pujolc3a0s.pdf", "pensar solo, en pareja y en equipo (la 1-2-4) en los pasos sin pantalla")]
