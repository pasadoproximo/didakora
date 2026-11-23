// Prueba «Monta tu sesión» fuera del navegador: node _build/probar_sesion.js  (después de python _build/build.py)
// Recorre TODOS los caminos del árbol (cada opción de cada pregunta) y en cada sesión que sale comprueba que:
//  · hay exactamente un paso principal y ninguna idea se repite en dos pasos;
//  · todas las herramientas cumplen lo contestado (etapa, dispositivos, sin registro, sin las de INTEF en rojo);
//  · «Otra idea» y «También encajan» no rompen nada, y el enlace (#o=…) devuelve la misma sesión.
// También prueba enlaces rotos o inventados: tienen que acabar en una pregunta o en una sesión, nunca en un error.
const fs = require('fs'), path = require('path');
const R = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(R, 'sesion', 'index.html'), 'utf8');
const D = JSON.parse(html.match(/window\.dkS=dkSesion\((\{.*\})\)<\/script>/s)[1].replace(/<\\\//g, '</'));
const js = fs.readFileSync(path.join(R, 'didakora.js'), 'utf8');
const motor = js.slice(js.indexOf('function dkSesion'), js.indexOf('\n// Agentation'));

function arranca(hash, guardado) {
  const el = () => ({ innerHTML: '', hidden: false, classList: { add() {}, remove() {} }, scrollIntoView() {}, querySelector() { return null; } });
  const $q = el(), $r = el(); let clic = null; const mem = { 'dk-sesion': guardado || null };
  const env = {
    document: { getElementById: id => id === 'ar' ? $q : $r, addEventListener: (t, f) => { clic = f; } },
    window: {}, location: { hash: hash || '', pathname: '/sesion/' },
    history: { replaceState: (a, b, u) => { env.location.hash = u.startsWith('#') ? u : ''; } },
    localStorage: { getItem: k => mem[k], setItem: (k, v) => { mem[k] = v; } },
  };
  const api = new Function('document', 'window', 'location', 'history', 'localStorage', 'D', motor + '\nreturn dkSesion(D);')(env.document, env.window, env.location, env.history, env.localStorage, D);
  const pulsa = ds => clic({ target: { closest: () => ({ dataset: ds }) } });
  const opciones = () => [...$q.innerHTML.matchAll(/<button type="button" data-q="(\w)" data-v="([^"]*)"( disabled)?>/g)].map(m => ({ q: m[1], v: m[2], off: !!m[3] }));
  return { api, pulsa, opciones, $q, $r, env, mem };
}
const fallos = []; let hojas = 0, preguntasMax = 0; const pasosPorReceta = {};
function comprueba(a, camino) {
  const { st, vista, cabe, receta } = a.api, P = receta().pasos, im = P.findIndex(p => p.main);
  const ideas = Object.keys(vista).filter(k => k !== 'main').map(k => vista[k]).filter(Boolean);
  const donde = camino.map(c => c.q + '=' + c.v).join(' ');
  if (!vista[im]) fallos.push(`${donde}: sin idea principal`);
  if (new Set(ideas).size !== ideas.length) fallos.push(`${donde}: una idea repetida`);
  for (const x of ideas) if (!cabe(x, st)) fallos.push(`${donde}: «${x.i}» (${x.n}) no cumple lo contestado`);
  if (st.r === '0' && ideas.some(x => x.r)) fallos.push(`${donde}: herramienta con registro`);
  if (st.d === 'p' && ideas.some(x => x.d !== 'p')) fallos.push(`${donde}: herramienta que no vale solo con el proyector`);
  if (st.e && st.e !== '-' && ideas.some(x => !x.e.includes(st.e))) fallos.push(`${donde}: herramienta de otra etapa`);
  if (st.x === '1' && ideas.some(x => x.x)) fallos.push(`${donde}: herramienta en rojo en la guía del INTEF`);
  if (!/class="ms-p[^"]* main"/.test(a.$r.innerHTML) || (a.$r.innerHTML.match(/class="ms-p[^"]* main"/g) || []).length !== 1) fallos.push(`${donde}: no hay un único paso principal`);
  return (a.$r.innerHTML.match(/<li class="ms-p/g) || []).length;
}
function recorre(camino) {
  const a = arranca('');
  for (const c of camino) a.pulsa({ q: c.q, v: c.v });
  const ops = a.opciones();
  if (!ops.length) {
    hojas++; preguntasMax = Math.max(preguntasMax, camino.length);
    const n = comprueba(a, camino), nombre = a.api.receta().n;
    (pasosPorReceta[nombre] = pasosPorReceta[nombre] || new Set()).add(n);
    // «Otra idea» en cada paso y «También encajan»
    a.api.receta().pasos.forEach((p, i) => { if (!p.voz && a.api.vista[i]) { a.pulsa({ paso: String(i) }); comprueba(a, camino.concat({ q: 'otra', v: i })); } });
    const usar = a.$r.innerHTML.match(/data-usar="(\d+)"/); if (usar) { a.pulsa({ usar: usar[1] }); comprueba(a, camino.concat({ q: 'usar', v: usar[1] })); }
    // el enlace devuelve una sesión con las mismas respuestas
    const b = arranca(a.env.location.hash);
    if (b.opciones().length || b.api.receta().n !== nombre) fallos.push(`${a.env.location.hash}: el enlace no devuelve la misma sesión`);
    return;
  }
  if (ops.every(o => o.off)) { fallos.push(camino.map(c => c.q + '=' + c.v).join(' ') + ': pregunta sin ninguna opción'); return; }
  for (const o of ops) if (!o.off) recorre(camino.concat(o));
}
recorre([]);
// enlaces rotos, inventados o imposibles, y respuestas recordadas que ya no valen
for (const h of ['#o=zzz', '#k=b', '#o=equ&k=zzz', '#o=exp&k=gh&e=I&d=p&r=0', '#o=cre&k=t&e=I', '#e=S&d=a', '#o=*&k=b&x=9', '#o=eva&k=fin&e=Q&d=&r=7', '#%%%', '#o=equ&k=b&e=S&d=a&r=1&x=1']) {
  try { const a = arranca(h, '{"e":"Z","d":"p","r":"0"}'); if (!a.opciones().length && a.$r.hidden !== false) fallos.push(h + ': ni pregunta ni sesión'); if (!a.opciones().length) comprueba(a, [{ q: 'enlace', v: h }]); }
  catch (e) { fallos.push(h + ': error ' + e.message); }
}
// con respuestas recordadas, la segunda sesión no vuelve a preguntar por el aula
{ const a = arranca('', '{"e":"S","d":"a","r":"1"}'); a.pulsa({ q: 'o', v: 'equ' }); a.pulsa({ q: 'k', v: 'b' });
  if (a.opciones().some(o => 'edr'.includes(o.q))) fallos.push('recordadas: vuelve a preguntar por el aula'); }
console.log(`sesión: ${hojas} caminos, hasta ${preguntasMax} preguntas · pasos por tipo de sesión: ` + Object.entries(pasosPorReceta).map(([k, v]) => `${k} ${[...v].join('/')}`).join(', '));
if (fallos.length) { console.log(fallos.length + ' FALLOS:\n' + [...new Set(fallos)].slice(0, 40).join('\n')); process.exit(1); }
console.log('sin fallos');
