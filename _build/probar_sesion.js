// Prueba «Monta tu sesión» (después de python _build/build.py): node _build/probar_sesion.js
// Comprueba cada combinación de filtros, que no haya páginas sin generar y que los pasos sumen los minutos anunciados.
const fs = require('fs'), path = require('path'), R = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(R, 'sesion/index.html'), 'utf8'), fallos = [];
const C = [...html.matchAll(/<article class="xa c\d" data-id="([^"]+)" data-e="(\w+)" data-o="(\w+)" data-s="([^"]+)" data-d="(\w)"/g)].map(m => ({ id: m[1], e: m[2], o: m[3], s: m[4].split(' '), d: m[5] }));
const v = k => [...html.match(new RegExp(`<select data-k="${k}">(.*?)</select>`))[1].matchAll(/value="([^"]+)"/g)].map(m => m[1]);
if (!C.length) fallos.push('no se ha leído ninguna sesión');
let vacias = 0, total = 0;
for (const e of v('e')) for (const d of v('d')) { const n = C.filter(c => c.e.includes(e) && 'pea'.indexOf(c.d) <= 'pea'.indexOf(d)).length; total++; if (!n) fallos.push(`sin sesiones: etapa ${e}, dispositivos ${d}`); }
for (const e of v('e')) for (const d of v('d')) for (const s of v('s')) if (!C.some(c => c.e.includes(e) && 'pea'.indexOf(c.d) <= 'pea'.indexOf(d) && (c.s.includes(s) || c.s.includes('*')))) vacias++;
for (const k of ['o', 's']) for (const x of v(k)) if (!C.some(c => k === 'o' ? c.o === x : c.s.includes(x))) fallos.push(`filtro sin sesiones: ${x}`);
for (const c of C) { const p = path.join(R, 'sesion', c.id, 'index.html'); if (!fs.existsSync(p)) { fallos.push('falta ' + c.id); continue; }
  const h = fs.readFileSync(p, 'utf8'), t = +h.match(/<dd>(\d+) minutos/)[1], suma = [...h.matchAll(/class="sp-m">(\d+)/g)].reduce((a, m) => a + +m[1], 0); if (t !== suma) fallos.push(`${c.id}: ${suma} de ${t} minutos`); }
console.log(`sesiones: ${C.length} · etapa × dispositivos: ${total} combinaciones · con materia, ${vacias} sin sesión (esas opciones salen apagadas)`);
if (fallos.length) { console.log(fallos.join('\n')); process.exit(1); }
console.log('sin fallos');
