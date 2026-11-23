// Didákora: comportamiento común de todas sus páginas y listado con buscador (/todas/)
(()=>{
// desplegable de etapa a medida: ratón, teclado (flechas, Inicio, Fin, Intro, Esc) y lector de pantalla (listbox)
document.querySelectorAll('.dd').forEach(dd=>{
 const btn=dd.querySelector('.dd-b'),list=dd.querySelector('.dd-l'),val=dd.querySelector('.dd-v'),inp=dd.querySelector('input'),ops=[...list.querySelectorAll('[role=option]')];
 let act=0;
 const mark=i=>{act=(i+ops.length)%ops.length;ops.forEach((o,j)=>o.classList.toggle('act',j===act));list.setAttribute('aria-activedescendant',ops[act].id);};
 const open=()=>{list.hidden=false;btn.setAttribute('aria-expanded','true');dd.classList.add('open');mark(Math.max(0,ops.findIndex(o=>o.getAttribute('aria-selected')==='true')));list.focus();};
 const close=(focus)=>{list.hidden=true;btn.setAttribute('aria-expanded','false');dd.classList.remove('open');if(focus)btn.focus();};
 const pick=(i,silent)=>{const o=ops[i];ops.forEach(x=>x.setAttribute('aria-selected',x===o?'true':'false'));val.textContent=o.textContent;inp.value=o.dataset.v;dd.classList.toggle('on',!!o.dataset.v);if(!silent)dd.dispatchEvent(new Event('change',{bubbles:true}));};
 dd.dkSet=v=>{const i=ops.findIndex(o=>o.dataset.v===v);pick(i<0?0:i,true);};
 btn.addEventListener('click',()=>list.hidden?open():close(true));
 btn.addEventListener('keydown',e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();open();}});
 list.addEventListener('click',e=>{const o=e.target.closest('[role=option]');if(!o)return;pick(ops.indexOf(o));close(true);});
 list.addEventListener('mousemove',e=>{const o=e.target.closest('[role=option]');if(o)mark(ops.indexOf(o));});
 list.addEventListener('keydown',e=>{
  if(e.key==='ArrowDown'){e.preventDefault();mark(act+1);}else if(e.key==='ArrowUp'){e.preventDefault();mark(act-1);}
  else if(e.key==='Home'){e.preventDefault();mark(0);}else if(e.key==='End'){e.preventDefault();mark(ops.length-1);}
  else if(e.key==='Enter'||e.key===' '){e.preventDefault();pick(act);close(true);}
  else if(e.key==='Escape'||e.key==='Tab'){close(e.key==='Escape');}});
 document.addEventListener('click',e=>{if(!dd.contains(e.target)&&!list.hidden)close(false);});
});
// botón de volver: vuelve a la página anterior si se llegó desde esta web; si no, sube a la página de la que cuelga
document.addEventListener('click',e=>{const b=e.target.closest('[data-back]');if(!b||e.metaKey||e.ctrlKey||e.shiftKey)return;
 try{if(document.referrer&&new URL(document.referrer).origin===location.origin&&history.length>1){e.preventDefault();history.back();}}catch(err){}
});
// logo del menú: al pulsarlo, la caja hace su animación y después va al inicio
document.addEventListener('click',e=>{const b=e.target.closest('.brand');if(!b||e.metaKey||e.ctrlKey||e.shiftKey||e.button)return;
 if(matchMedia('(prefers-reduced-motion:reduce)').matches)return;
 e.preventDefault();b.classList.remove('tap');void b.offsetWidth;b.classList.add('tap');
 setTimeout(()=>{if(new URL(b.href).pathname!==location.pathname||location.search||location.hash)location.href=b.href;},480);
});
// fila «Compartir»: el botón del enlace lo copia y lo dice al lado
document.addEventListener('click',async e=>{const b=e.target.closest('[data-copia]');if(!b)return;
 const ok=b.closest('.comp').querySelector('.comp-ok');
 try{await navigator.clipboard.writeText(b.dataset.copia);ok.textContent='Enlace copiado';}catch(err){ok.textContent=b.dataset.copia;}
 setTimeout(()=>{ok.textContent=''},2500);
});
// compartir la ficha: menú del sistema si existe; si no, se copia el enlace
document.addEventListener('click',async e=>{const b=e.target.closest('[data-share]');if(!b)return;
 const data={title:document.title,url:location.href};
 try{if(navigator.share){await navigator.share(data);return;}await navigator.clipboard.writeText(location.href);const o=b.innerHTML;b.textContent='Enlace copiado';setTimeout(()=>{b.innerHTML=o},1800);}catch(err){}
});
})();

// ---------- motor de búsqueda (lo usa el listado; se puede probar fuera del navegador)
// Puntúa cada herramienta según dónde aparece cada palabra: en el nombre (lo que más cuenta), en la descripción,
// la categoría, el apartado o la materia, y en las ideas de uso y los textos de su ficha. Entiende plurales, términos relacionados, el
// principio de una palabra («pres» → presentaciones) y una errata por palabra («kahot» → Kahoot!).
function dkMotor(TOOLS,SECTIONS,CAJA){
 const norm=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const stem=w=>w.length>4&&w.endsWith('ces')?w.slice(0,-3)+'z':w.length>4&&w.endsWith('es')?w.slice(0,-2):w.length>3&&w.endsWith('s')?w.slice(0,-1):w;
 const STOP=new Set('de la el los las un una unos unas y o a en con para por del al que se su sus mi me lo como'.split(' '));
 const SYN={evaluacion:['evaluar','rubrica','calificar','corregir'],evaluar:['evaluacion','rubrica','calificar','corregir'],rubrica:['evaluacion','evaluar'],
  cuestionario:['quiz','test','preguntas','encuesta'],quiz:['cuestionario','test','preguntas'],test:['cuestionario','quiz','preguntas'],
  video:['audiovisual','grabar'],mapa:['cartografia'],imagen:['foto','fotografia','ilustracion'],foto:['imagen','fotografia'],podcast:['audio','radio'],
  presentacion:['diapositivas','exposicion'],diapositivas:['presentacion'],cronologia:['linea del tiempo','eje cronologico'],
  equipo:['colaborar','colaborativo','cooperativo'],colaborar:['equipo','colaborativo','cooperativo'],programar:['informatica'],
  gratis:['gratuito','gratuita','sin coste','libre'],gratuito:['gratis','gratuita','sin coste','libre'],
  gamificacion:['juego','jugar','concurso','gamificado'],juego:['jugar','concurso','gamificado'],
  dislexia:['lectura en voz alta','dificultades de lectura','dificultades de escritura','accesibilidad'],accesibilidad:['lectura en voz alta','dictado','dificultades'],familia:['familias'],mural:['muro','tablon'],muro:['mural','tablon'],
  gamificar:['juego','concurso','puntos','jugar','gamificado','gamificacion'],interactivo:['preguntas','interactiva','responde'],
  cooperativo:['cooperativa','cooperativas','equipo','colaborar'],cooperativa:['cooperativo','equipo','colaborar'],trabajo:['trabajar'],
  diversidad:['dislexia','lectura en voz alta','dictado','accesibilidad','dificultades','inclusion'],inclusion:['diversidad','accesibilidad','dislexia','dificultades'],
  planificar:['programacion','planificacion','preparar'],traducir:['traduccion','idiomas'],
  voz:['locucion','narrar','narracion','leer en voz alta'],locucion:['voz','narrar','narracion'],narrar:['narracion','locucion','voz','relato'],narracion:['narrar','locucion','voz','relato'],
  doblaje:['doblar','idiomas','locucion'],doblar:['doblaje','idiomas'],audiolibro:['leer en voz alta','narrar','locucion','audio']};
 const PHRASES=[['atencion a la diversidad','diversidad'],['inteligencia artificial','ia'],['realidad aumentada','ra'],['tres dimensiones','3d'],['no necesita cuenta','nocuenta'],['sin cuenta','nocuenta'],['sin registro','nocuenta'],['sin registrarse','nocuenta'],['educacion fisica','educacionfisica'],['voz en off','locucion'],['texto a voz','locucion']];
 const SYNS=Object.fromEntries(Object.entries(SYN).map(([k,v])=>[stem(k),v]));
 const words=s=>norm(s).split(/[^a-z0-9ñ]+/).filter(Boolean);
 const CATKW={'aula:ia':'apoyo al aprendizaje','aula:cienc':'','aula:arte':''};
 const PROG='tecnologia informatica programar programacion';
 const SUBJ={geogebra:'matematicas geometria',desmos:'matematicas',phet:'ciencias fisica quimica biologia matematicas',gizmos:'ciencias fisica quimica biologia matematicas',
  bodymaps:'ciencias biologia anatomia',anatomy3d:'ciencias biologia anatomia',vertebrados:'ciencias biologia',bolsa:'economia',
  tinkercad:PROG+' robotica arduino',scratch:PROG,snap:PROG,blockly:PROG,codeorg:PROG,appinventor:PROG,cospaces:PROG,coppelia:PROG+' robotica',thunkable:'tecnologia informatica',snatchbot:'tecnologia informatica',
  musescore:'musica',incredibox:'musica',musiclab:'musica componer melodia cancion',scratchjr:PROG+' infantil tableta tablet',gcompris:'infantil letras numeros colores logica juegos educativos',tuxpaint:'infantil dibujo dibujar pintar plastica',musictheory:'musica',librecad:'dibujo tecnico tecnologia'};
 const IDX={};
 const flat=s=>' '+s.replace(/[^a-z0-9ñ]+/g,' ')+' ';
 const joinPh=s=>{let r=' '+s.replace(/[^a-z0-9ñ]+/g,' ')+' ';PHRASES.forEach(([a,b])=>{r=r.split(' '+a+' ').join(' '+b+' ')});return r.trim();};
 const ETN={I:'infantil',P:'primaria',S:'secundaria bachillerato eso'};
 TOOLS.forEach(t=>{const k=t.s+':'+t.cat,c=CAJA.t[t.id];
  const core=norm([t.d,t.a,t.p,SECTIONS[t.s].n,k in CATKW?CATKW[k]:SECTIONS[t.s].cats[t.cat],CAJA.cats[c[0]][0],c[3],SUBJ[t.id],c[1].map(e=>ETN[e]).join(' '),t.c,t.nota,t.coste,t.cta,t.s==='aula'&&/^no necesita/i.test(t.cta)?'nocuenta':''].filter(Boolean).join(' '));
  const ideas=joinPh(norm((t.i||[]).join(' ')+' '+(c[4]||''))),coreJ=joinPh(core),name=joinPh(norm(t.n));
  IDX[t.id]={nc:norm(t.n.replace(/\s*\(.*\)/,'')).replace(/[^a-z0-9ñ]/g,''),nt:flat(name),ct:flat(coreJ),it:flat(ideas),nw:words(name),cwl:words(coreJ),cw:new Set(words(coreJ).map(stem)),iw:new Set(words(ideas).map(stem))};});
 const forms=w=>[w,...(SYNS[stem(w)]||[])];
 // ¿se parecen con una sola letra de diferencia (sobra, falta o cambia)?
 const near=(a,b)=>{if(Math.abs(a.length-b.length)>1||a===b)return a===b;let i=0,j=0,e=0;
  while(i<a.length&&j<b.length){if(a[i]===b[j]){i++;j++;continue;}if(++e>1)return false;
   if(a.length>b.length)i++;else if(b.length>a.length)j++;else{i++;j++;}}
  return e+(a.length-i)+(b.length-j)<=1;};
 const wordScore=(X,w)=>{let best=0;const sw=stem(w);
  if(X.nw.some(x=>x===w||stem(x)===sw))best=10;
  else if(X.nw.some(x=>x.startsWith(w))||(w.length>=3&&X.nc.startsWith(w)))best=8;
  if(best<10&&w.length>=4&&w===X.nc)best=10;
  if(best<5){const fs=forms(w);for(let k=0;k<fs.length;k++){const f=fs[k],ok=f.includes(' ')?(X.nt.includes(' '+f+' ')||X.ct.includes(' '+f+' ')):X.cw.has(stem(f));
   if(ok){best=Math.max(best,k===0?5:Math.max(3,4-k*.15));break;}}}
  if(best<4.5&&w.length>=4&&(X.nw.some(x=>x.length>=4&&near(x,w))||near(X.nc,w)))best=4.5;
  if(best<3&&w.length>=3&&X.cwl.some(x=>x.startsWith(w)))best=3;
  if(best<2&&forms(w).some(f=>f.includes(' ')?X.it.includes(' '+f+' '):(stem(f).length>3&&X.iw.has(stem(f)))))best=2;
  if(best<1&&w.length>=5&&X.cwl.some(x=>x.length>=5&&near(x,w)))best=1;
  // desempate: si además aparecen términos relacionados («voz» → locución, narrar…), la herramienta va más centrada en el tema
  if(best>0){const extra=forms(w).slice(1).filter(f=>f.includes(' ')?(X.ct.includes(' '+f+' ')||X.it.includes(' '+f+' ')):(X.cw.has(stem(f))||X.iw.has(stem(f)))).length;best+=Math.min(.9,extra*.3);}
  return best;};
 const query=raw=>{let r=' '+norm(raw).replace(/[^a-z0-9ñ]+/g,' ')+' ';PHRASES.forEach(([a,b])=>{r=r.split(' '+a+' ').join(' '+b+' ')});return words(r).filter(w=>!STOP.has(w));};
 // devuelve {exactas, parecidas}: exactas = tienen todas las palabras; parecidas = alguna (solo si no hay exactas)
 const buscar=(raw,pool)=>{const qs=query(raw);pool=pool||TOOLS;if(!qs.length)return {qs,exactas:pool,parecidas:[]};
  const sc=pool.map(t=>{const X=IDX[t.id],v=qs.map(w=>wordScore(X,w));return {t,hits:v.filter(Boolean).length,sum:v.reduce((a,b)=>a+b,0)};});
  const by=(a,b)=>b.sum-a.sum;
  const exactas=sc.filter(x=>x.hits===qs.length).sort(by).map(x=>x.t);
  const parecidas=exactas.length?[]:sc.filter(x=>x.hits>0).sort((a,b)=>b.hits-a.hits||by(a,b)).map(x=>x.t);
  return {qs,exactas,parecidas};};
 return {buscar,query};
}

// ---------- listado completo
function cajaListado(){
 const $=id=>document.getElementById(id);
 const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 const M=dkMotor(TOOLS,SECTIONS,CAJA);

 // tarjeta: la misma que generan las páginas estáticas
 const B=window.DK_BASE||'';
 const EXT='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>';
 const lead=t=>t.s==='aula'?t.a:t.s==='docente'?t.p:t.d;
 const card=t=>{const m=t.n.match(/^(.+?)\s*\((.+)\)$/),nm=m?m[1]:t.n,[cs,,hasLogo]=CAJA.t[t.id],[cn,ci]=CAJA.cats[cs];
  const lg=hasLogo?`<img src="${B}/logos/${t.id}.png?v=3" alt="" width="26" height="26" loading="lazy">`:`<b aria-hidden="true">${esc(t.n[0])}</b>`;
  const go=`<a class="td-x" href="${esc(t.url)}" rel="noopener" target="_blank">${EXT}<span class="sr">Abrir ${esc(nm)} (se abre en otra pestaña)</span></a>`;
  const head=`<div class="tc-h"><span class="lg">${lg}</span><h3><a class="tc-a" href="${B}/${t.id}/">${esc(nm)}</a>${m?`<small>${esc(m[2])}</small>`:''}</h3>${st.cat?go:''}</div><p>${esc(lead(t))}</p>`;
  // con una categoría elegida no se repite la etiqueta: la flecha sube junto al nombre
  return st.cat?`<article class="tc td nc">${head}</article>`:
   `<article class="tc td">${head}<div class="tc-f"><a class="tag" href="${B}/categorias/${cs}/"><svg viewBox="0 0 24 24" aria-hidden="true">${ci}</svg>${esc(cn)}</a>${go}</div></article>`;};

 const P=new URLSearchParams(location.search);
 const st={q:P.get('q')||'',nivel:P.get('nivel')||'',cat:P.get('cat')||''};
 const qEl=$('lq'),nEl=$('lnv');qEl.value=st.q;
 const setNv=v=>nEl.dkSet(v);setNv(st.nivel);
 const NV={I:'Infantil',P:'Primaria',S:'Secundaria y Bachillerato'};
 function render(){
  const pool=TOOLS.filter(t=>(!st.nivel||CAJA.t[t.id][1].includes(st.nivel))&&(!st.cat||CAJA.t[t.id][0]===st.cat));
  const r=M.buscar(st.q,pool),list=r.exactas.length?r.exactas:r.parecidas,aprox=!r.exactas.length&&r.parecidas.length>0;
  const note=aprox?`<p class="aprox">Ninguna herramienta tiene todas las palabras de «${esc(st.q)}». Estas tienen alguna:</p>`:'';
  $('lgrid').innerHTML=list.length?note+list.map(card).join(''):`<div class="empty"><p>No hay resultados${st.q?` para «${esc(st.q)}»`:''}.</p><p>Prueba con otra palabra o con lo que quieres hacer, por ejemplo «evaluar» o «vídeo»${st.nivel||st.cat?', o quita los filtros':''}.</p><button type="button" class="btn solid" data-reset>Ver todas</button></div>`;
  document.querySelectorAll('#lcats button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.cat===st.cat));
  const extra=st.nivel?NV[st.nivel]:'';
  $('lcount').textContent=`${list.length} ${list.length===1?'herramienta':'herramientas'}${aprox?' parecidas':''}${extra?' · '+extra:''}`;
  const u=new URLSearchParams();if(st.q)u.set('q',st.q);if(st.nivel)u.set('nivel',st.nivel);if(st.cat)u.set('cat',st.cat);
  history.replaceState(null,'',location.pathname+(u.toString()?'?'+u:''));
 }
 qEl.addEventListener('input',()=>{st.q=qEl.value;render();});
 nEl.addEventListener('change',()=>{st.nivel=nEl.querySelector('input').value;render();});
 $('lcats').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;st.cat=b.dataset.cat;render();});
 document.addEventListener('click',e=>{if(e.target.closest('[data-reset]')){Object.assign(st,{q:'',nivel:'',cat:''});qEl.value='';setNv('');render();qEl.focus();}});
 render();
}

// en pantallas estrechas, el texto de ayuda del buscador corto para que no se corte
(()=>{const mq=matchMedia('(max-width:560px)'),els=[...document.querySelectorAll('#hq,#lq')];
 const f=()=>els.forEach(e=>{e.dataset.ph=e.dataset.ph||e.placeholder;e.placeholder=mq.matches?'Busca una herramienta o tarea…':e.dataset.ph;});
 f();mq.addEventListener('change',f);})();

// Monta tu sesión: un árbol de preguntas que se adapta (solo pregunta lo que cambia el resultado) y acaba en una receta de sesión
// con los pasos que le convienen: la idea que buscaba el docente, otras del catálogo que la acompañan y pasos sin pantalla.
// Datos: _build/sesion_ideas.py (ideas) y _build/sesion_recetas.py (metas, ramas y recetas).
function dkSesion(D){
 const B=window.DK_BASE||'',IDEAS=D.ideas,$q=document.getElementById('ar'),$r=document.getElementById('ar-r');
 const ORDEN=['o','k','e','d','r','x'],st={},vista={};let recordadas={};
 const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 const FIJAS={e:['¿Con qué etapa?',[['S','Secundaria y Bachillerato'],['P','Primaria'],['I','Infantil']]],
  d:['¿Qué dispositivos hay en el aula?',[['a','Uno por alumno'],['e','Uno por pareja o por equipo'],['p','Solo el mío y el proyector']]],
  r:['¿El alumnado puede usar una cuenta?',[['1','Sí, propia o del centro'],['0','No: tiene que ser sin cuenta']]],
  x:['Entre las que encajan hay herramientas que la guía de protección de datos del INTEF marca en rojo. ¿Las quito?',[['1','Sí, quítalas'],['0','Déjalas']]]};
 const pregunta=q=>q==='o'?['¿Qué quieres hacer en clase?',D.metas.map(m=>[m[0],m[1],m[2]])]:q==='k'?D.ramas[st.o]:FIJAS[q];
 // ¿cabe la idea con lo contestado sobre el aula?
 const cabe=(x,s)=>(!s.e||x.e.includes(s.e))&&(!s.d||s.d==='a'||(s.d==='e'?x.d!=='a':x.d==='p'))&&(!s.r||s.r==='1'||x.r===0)&&(s.x!=='1'||!x.x);
 // ¿es una idea de las que buscaba el docente, según la meta y su rama?
 const esMain=(x,s)=>{const o=s.o,k=s.k;if(!o||o==='*')return x.m==='des';if(x.o!==o)return false;
  if(o==='exp')return x.m==='des'&&(k==null||x.s===k);if(o==='eva')return k==null||x.m===k;
  return x.m!=='ini'&&(k==null||x.k===k);};
 const pool=s=>IDEAS.filter(x=>esMain(x,s)&&cabe(x,s));
 const con=(q,v)=>Object.assign({},st,{[q]:v});
 // la siguiente pregunta que cambia algo; las del aula se saltan si todas las opciones dejan las mismas ideas
 const siguiente=()=>{
  for(const q of ['x','r','d','e','k'])if(st.o&&!pool(st).length&&st[q]!=null)delete st[q];   // una combinación sin ideas (un enlace antiguo): se deshace desde la última respuesta
  if(st.o&&!pool(st).length)delete st.o;
  for(const q of ORDEN){if(st[q]!=null)continue;
   if(q==='k'&&st.o==='*'){st.k='*';continue;}
   const ops=pregunta(q)[1].map(o=>({v:o[0],t:o[1],s:o[2]||'',n:pool(con(q,o[0])).length}));
   if(q==='x'){if(!pool(st).some(x=>x.x)||ops[0].n===0){st.x='0';continue;}}
   else if('edr'.includes(q)){if(ops.every(o=>o.n===ops[0].n)){st[q]='-';continue;}
    const g=recordadas[q];if(g&&ops.some(o=>o.v===g&&o.n>0)){st[q]=g;continue;}}
   return {q:q,ops:ops};}
  return null;};
 const limpia=s=>{const c={};for(const q in s)if(s[q]!=='-')c[q]=s[q];return c;};
 const etiqueta=(q,v)=>{if(v==='-'||v==null||(q==='k'&&v==='*')||(q==='x'&&v==='0'))return '';
  if(q==='x')return 'Sin las de INTEF en rojo';const o=pregunta(q)[1].find(o=>o[0]===v);return o?o[1]:'';};
 const guarda=()=>{try{localStorage.setItem('dk-sesion',JSON.stringify({e:st.e,d:st.d,r:st.r}));}catch(e){}
  const h=ORDEN.filter(q=>st[q]!=null&&st[q]!=='-').map(q=>q+'='+encodeURIComponent(st[q])).join('&');
  try{history.replaceState(null,'',h?'#'+h:location.pathname);}catch(e){}};
 const camino=()=>{const c=ORDEN.map(q=>[q,etiqueta(q,st[q])]).filter(p=>p[1]);if(!c.length)return '';
  return '<div class="ar-c"><span class="lab">Tus respuestas</span>'+c.map(p=>'<button type="button" data-volver="'+p[0]+'" title="Cambiar esta respuesta">'+esc(p[1])+'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button>').join('')+
   '<button type="button" class="ar-z" data-volver="o">Empezar de nuevo</button></div>';};
 // ---- la receta
 const receta=()=>D.recetas[st.o+'/'+st.k]||D.recetas[st.o]||D.recetas['*'];
 const candidatas=(p,i)=>{const otras=Object.keys(vista).filter(k=>k!=='main'&&+k!==i).map(k=>vista[k]).filter(Boolean);
  let c=p.main?pool(st):IDEAS.filter(x=>cabe(x,st)&&(p.ideas?p.ideas.includes(x.i):(!p.o||x.o===p.o)&&(!p.k||x.k===p.k)&&(!p.m||p.m.includes(x.m))));
  c=c.filter(x=>!otras.includes(x));
  if(p.main){const d=c.filter(x=>x.m==='des');if(d.length&&st.o!=='eva')c=d;}
  else{const pr=vista.main;const sc=pr?pr.s:'';const g=c.filter(x=>!x.s||x.s===sc);if(g.length)c=g;}   // lo que acompaña, general o de la misma materia
  return {c:c,otras:otras};};
 const elige=(p,i)=>{const r=candidatas(p,i);let c=r.c;if(!c.length)return null;
  const nuevas=c.filter(x=>x!==vista[i]);if(nuevas.length)c=nuevas;
  const libres=c.filter(x=>!r.otras.some(o=>o.t===x.t));if(libres.length)c=libres;
  return c[Math.floor(Math.random()*c.length)];};
 const tarjeta=x=>'<a class="ms-t" href="'+B+'/'+x.t+'/"><span class="lg">'+(x.l?'<img src="'+B+'/logos/'+x.t+'.png?v=3" alt="" width="26" height="26">':'<b>'+esc(x.n[0])+'</b>')+'</span><span><b>'+esc(x.n)+'</b><small>'+esc(x.dt)+' · '+esc(x.ct)+'</small></span></a>';
 // dibuja la sesión con lo que haya en «vista»: un paso que se queda sin idea se hace sin pantalla (su «alt») o no sale
 const dibuja=()=>{const R=receta(),P=R.pasos,im=P.findIndex(p=>p.main);
  const pasos=P.map((p,i)=>({p:(!p.voz&&!vista[i]&&p.alt)?{t:p.t,voz:p.alt}:p,i:i,x:vista[i]})).filter(s=>s.p.voz||s.x);
  const nh=new Set(pasos.filter(s=>s.x).map(s=>s.x.t)).size;
  const otras=pool(st).filter(x=>x!==vista[im]).slice(0,9);
  $r.hidden=false;
  $r.innerHTML='<header class="ar-rh"><span class="lab">Tu sesión</span><h2>'+esc(R.n)+'</h2><p>'+esc(R.d)+'</p><p class="ar-n">'+pasos.length+(pasos.length===1?' paso':' pasos')+' · '+nh+(nh===1?' herramienta':' herramientas')+'</p></header>'+
   '<ol class="ms" style="--n:'+pasos.length+'">'+pasos.map((s,k)=>{const x=s.x,n=x?candidatas(s.p,s.i).c.length:0;
    return '<li class="ms-p'+(s.p.voz?' voz':'')+(s.p.main?' main':'')+'"><span class="ms-n">'+(k+1)+'</span><div class="ms-c"><span class="lab">'+esc(s.p.t)+'</span>'+
     (s.p.voz?'<p class="ms-v">'+esc(s.p.voz)+'</p><span class="ms-sp">Sin pantalla</span>'
      :'<h3>'+esc(x.i)+'</h3>'+tarjeta(x)+(n>1?'<button type="button" class="ms-o" data-paso="'+s.i+'">Otra idea</button>':''))+'</div></li>';}).join('')+'</ol>'+
   (otras.length?'<section class="ar-o" aria-labelledby="h-otras2"><h3 id="h-otras2">También encajan con lo que buscas</h3><ul>'+otras.map(x=>'<li><button type="button" data-usar="'+IDEAS.indexOf(x)+'"><b>'+esc(x.i)+'</b><small>'+esc(x.n)+'</small></button></li>').join('')+'</ul></section>':'');};
 // elige las ideas: todas (sin argumentos), solo un paso («Otra idea») o con una idea principal fijada («También encajan»)
 const resultado=(solo,fija)=>{const P=receta().pasos,im=P.findIndex(p=>p.main);
  if(solo==null){for(const k in vista)delete vista[k];vista[im]=fija||elige(P[im],im);vista.main=vista[im];P.forEach((p,i)=>{if(i!==im&&!p.voz)vista[i]=elige(p,i);});}
  else{vista[solo]=elige(P[solo],solo);if(solo===im)vista.main=vista[im];}
  dibuja();};
 // ---- pintar
 const pinta=()=>{const s=siguiente();guarda();
  if(!s){$q.innerHTML=camino();$q.classList.add('hecho');resultado();return;}
  $q.classList.remove('hecho');$r.hidden=true;$r.innerHTML='';
  const tot=pool(st).length,pr=pregunta(s.q)[0],grande=s.q==='o'||s.q==='k';
  $q.innerHTML=camino()+'<div class="ar-p"><h2>'+esc(pr)+'</h2>'+(st.o?'<p class="ar-n">'+tot+(tot===1?' idea encaja':' ideas encajan')+' de momento</p>':'')+
   '<div class="ar-ops'+(grande?' g':'')+'">'+s.ops.map(o=>'<button type="button" data-q="'+s.q+'" data-v="'+esc(o.v)+'"'+(o.n?'':' disabled')+'><b>'+esc(o.t)+'</b>'+(o.s?'<small>'+esc(o.s)+'</small>':'')+
    '<span>'+(o.n?o.n+(o.n===1?' idea':' ideas'):'Sin ideas todavía')+'</span></button>').join('')+'</div></div>';};
 const foco=()=>{const h=($r.hidden?$q:$r).querySelector('h2');if(h){h.tabIndex=-1;try{h.focus({preventScroll:true});}catch(e){}h.scrollIntoView({block:'nearest',behavior:'smooth'});}};
 const volver=q=>{const i=ORDEN.indexOf(q);ORDEN.forEach((k,n)=>{if(n>=i||st[k]==='-')delete st[k];});
  if('edr'.includes(q)){delete recordadas[q];}if(q==='o'||q==='k'){/* las del aula se conservan como recordadas */}pinta();};
 document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
  if(b.dataset.q){st[b.dataset.q]=b.dataset.v;if('edr'.includes(b.dataset.q))recordadas[b.dataset.q]=b.dataset.v;pinta();foco();}
  else if(b.dataset.volver){const q=b.dataset.volver;if('edr'.includes(q)||q==='x'){delete st[q];delete recordadas[q];ORDEN.forEach(k=>{if(st[k]==='-')delete st[k];});if(q!=='x')delete st.x;pinta();}else volver(q);foco();}
  else if(b.dataset.paso){resultado(+b.dataset.paso);}
  else if(b.dataset.usar){resultado(null,IDEAS[+b.dataset.usar]);$r.scrollIntoView({block:'start',behavior:'smooth'});}});
 // ---- arranque: lo que venga en el enlace manda; si no, se recuerdan las respuestas sobre el aula de la última vez
 try{recordadas=JSON.parse(localStorage.getItem('dk-sesion')||'{}')||{};}catch(e){recordadas={};}
 for(const q in recordadas)if(!recordadas[q]||recordadas[q]==='-')delete recordadas[q];
 new URLSearchParams(location.hash.slice(1)).forEach((v,q)=>{if(ORDEN.includes(q)){st[q]=v;if('edr'.includes(q))recordadas[q]=v;}});
 // solo valores que existan; lo que no cuadre se descarta y se vuelve a preguntar
 if(st.o!=null&&!D.metas.some(m=>m[0]===st.o)){for(const q of ORDEN)delete st[q];}
 if(st.o==null){for(const q of ORDEN)delete st[q];}
 else{if(st.o==='*')delete st.k;else if(st.k!=null&&!D.ramas[st.o][1].some(o=>o[0]===st.k))delete st.k;
  for(const q of ['e','d','r','x'])if(st[q]!=null&&!FIJAS[q][1].some(o=>o[0]===st[q]))delete st[q];}
 for(const q of ['e','d','r'])if(recordadas[q]&&!FIJAS[q][1].some(o=>o[0]===recordadas[q]))delete recordadas[q];
 pinta();
 return {st:st,vista:vista,pool:pool,cabe:cabe,receta:receta};   // para _build/probar_sesion.js
}

// Agentation (anotar la página para Claude Code): solo en local
if(["127.0.0.1","localhost"].includes(location.hostname))import((window.DK_BASE||"")+"/agentation-local.js").catch(()=>{});
