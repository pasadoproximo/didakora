// Prueba el buscador fuera del navegador: node _build/probar_buscador.js
// Las recién añadidas (RECIENTES en tools.js) se prueban además con sus búsquedas típicas (campo q): entre las 5 primeras.
// Comprueba que cada herramienta se encuentra por su nombre, por cada palabra del nombre, por el principio
// del nombre, por su nombre anterior y con una errata; y que las búsquedas habituales de clase dan resultados.
const fs = require('fs'), path = require('path');
const R = path.join(__dirname, '..');
const src = ['tools.js', 'didakora-datos.js'].map(f => fs.readFileSync(path.join(R, f), 'utf8')).join('\n');
const js = fs.readFileSync(path.join(R, 'didakora.js'), 'utf8');
const motor = js.slice(js.indexOf('function dkMotor'), js.indexOf('// ---------- listado completo'));
const { TOOLS, SECTIONS, CAJA, RECIENTES, dkMotor } = new Function(src + '\n' + motor + '\nreturn {TOOLS,SECTIONS,CAJA,RECIENTES:typeof RECIENTES==="undefined"?[]:RECIENTES,dkMotor};')();
const M = dkMotor(TOOLS, SECTIONS, CAJA);
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const fallos = [];
const pos = (q, id) => { const r = M.buscar(q); const l = r.exactas.length ? r.exactas : r.parecidas; return { i: l.findIndex(t => t.id === id), exacta: r.exactas.length > 0, n: l.length }; };
const errata = w => w.length < 5 ? null : w.slice(0, 2) + w.slice(3); // quita la tercera letra

let pruebas = 0;
for (const t of TOOLS) {
  const m = t.n.match(/^(.+?)\s*\((.+)\)$/), nombre = m ? m[1] : t.n, alias = m ? m[2] : '';
  const casos = [[nombre, 'nombre', 3]];                                   // el nombre: entre los 3 primeros
  if (alias) casos.push([alias.replace(/^antes\s+/i, ''), 'alias', 5]);
  casos.push([nombre.slice(0, Math.min(4, nombre.length)), 'principio', 30]);
  norm(nombre).split(/[^a-z0-9ñ]+/).filter(w => w.length >= 3).forEach(w => casos.push([w, 'palabra «' + w + '»', 40]));
  const e = errata(norm(nombre).replace(/[^a-z0-9ñ ]/g, '').split(' ').sort((a, b) => b.length - a.length)[0]);
  if (e) casos.push([e, 'errata «' + e + '»', 10]);
  for (const [q, tipo, max] of casos) {
    pruebas++;
    const r = pos(q, t.id);
    if (r.i < 0 || r.i >= max) fallos.push(`${t.n} · ${tipo} («${q}»): ${r.i < 0 ? 'no sale' : 'puesto ' + (r.i + 1) + ' de ' + r.n}`);
  }
}
const tareas = ['evaluar', 'rúbrica', 'vídeo', 'podcast', 'mapa mental', 'gamificar', 'gamificación', 'línea del tiempo', 'presentaciones',
  'dislexia', 'sin registro', 'matemáticas', 'programar', 'inteligencia artificial', 'IA', '3D', 'familias', 'cuestionario', 'encuesta',
  'infografía', 'cómic', 'música', 'imágenes gratis', 'historia', 'geografía', 'ciencias', 'robótica', 'murales', 'colaborar', 'tareas',
  'notas', 'cuaderno del profesor', 'pizarra', 'temporizador', 'audio', 'diapositivas', 'juegos', 'concurso', 'repasar', 'atención a la diversidad',
  'lectura', 'accesibilidad', 'planificar', 'crear actividades', 'formularios', 'insignias', 'aula virtual', 'moodle', 'quizizz', 'traducir',
  'voz', 'voces', 'locución', 'narrar', 'narración', 'doblaje', 'texto a voz', 'voz en off', 'audiolibro'];
const vacias = [];
for (const q of tareas) { pruebas++; const r = M.buscar(q); if (!r.exactas.length) vacias.push(q + (r.parecidas.length ? ` (solo ${r.parecidas.length} parecidas)` : ' (nada)')); }
// las recién añadidas: cada búsqueda típica de un docente (campo q de RECIENTES) tiene que sacarla entre las 5 primeras
const usos = [];
for (const x of RECIENTES) {
  if (!(x.q || []).length) { usos.push(`${x.id}: sin búsquedas típicas en RECIENTES (añade q)`); continue; }
  for (const q of x.q) { pruebas++; const r = pos(q, x.id); if (r.i < 0 || r.i >= 5) usos.push(`${x.id} · «${q}»: ${r.i < 0 ? 'no sale' : 'puesto ' + (r.i + 1) + ' de ' + r.n}`); }
}
console.log(`${TOOLS.length} herramientas · ${pruebas} búsquedas probadas`);
console.log(fallos.length ? `\nNo se encuentran bien (${fallos.length}):\n- ` + fallos.join('\n- ') : '\nTodas las herramientas se encuentran por nombre, palabras, principio, nombre anterior y con errata.');
console.log(usos.length ? `\nLas nuevas no salen bien por lo que hacen (${usos.length}):\n- ` + usos.join('\n- ') : '\nLas recién añadidas se encuentran por lo que hacen (entre las 5 primeras).');
console.log(vacias.length ? `\nBúsquedas de clase sin coincidencia completa (${vacias.length}):\n- ` + vacias.join('\n- ') : '\nTodas las búsquedas de clase dan resultados.');
