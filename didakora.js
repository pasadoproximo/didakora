// Didakora: comportamiento común de todas sus páginas y listado con buscador (/todas/)
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
// compartir la ficha: menú del sistema si existe; si no, se copia el enlace
document.addEventListener('click',async e=>{const b=e.target.closest('[data-share]');if(!b)return;
 const data={title:document.title,url:location.href};
 try{if(navigator.share){await navigator.share(data);return;}await navigator.clipboard.writeText(location.href);const o=b.innerHTML;b.textContent='Enlace copiado';setTimeout(()=>{b.innerHTML=o},1800);}catch(err){}
});
})();

// ---------- motor de búsqueda (lo usa el listado; se puede probar fuera del navegador)
// Puntúa cada herramienta según dónde aparece cada palabra: en el nombre (lo que más cuenta), en la descripción,
// la categoría, el apartado o la materia, y en las ideas de uso. Entiende plurales, términos relacionados, el
// principio de una palabra («pres» → presentaciones) y una errata por palabra («kahot» → Kahoot!).
function dkMotor(TOOLS,SECTIONS,CAJA){
 const norm=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const stem=w=>w.length>4&&w.endsWith('es')?w.slice(0,-2):w.length>3&&w.endsWith('s')?w.slice(0,-1):w;
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
  diversidad:['dislexia','lectura en voz alta','dictado','accesibilidad','dificultades','inclusion'],inclusion:['diversidad','accesibilidad','dislexia','dificultades'],
  planificar:['programacion','planificacion','preparar'],traducir:['traduccion','idiomas']};
 const PHRASES=[['atencion a la diversidad','diversidad'],['inteligencia artificial','ia'],['realidad aumentada','ra'],['tres dimensiones','3d'],['no necesita cuenta','nocuenta'],['sin cuenta','nocuenta'],['sin registro','nocuenta'],['sin registrarse','nocuenta'],['educacion fisica','educacionfisica']];
 const SYNS=Object.fromEntries(Object.entries(SYN).map(([k,v])=>[stem(k),v]));
 const words=s=>norm(s).split(/[^a-z0-9ñ]+/).filter(Boolean);
 const CATKW={'aula:ia':'apoyo al aprendizaje','aula:cienc':'','aula:arte':''};
 const PROG='tecnologia informatica programar programacion';
 const SUBJ={geogebra:'matematicas geometria',desmos:'matematicas',phet:'ciencias fisica quimica biologia matematicas',gizmos:'ciencias fisica quimica biologia matematicas',
  bodymaps:'ciencias biologia anatomia',anatomy3d:'ciencias biologia anatomia',vertebrados:'ciencias biologia',bolsa:'economia',
  tinkercad:PROG+' robotica arduino',scratch:PROG,snap:PROG,blockly:PROG,codeorg:PROG,appinventor:PROG,cospaces:PROG,coppelia:PROG+' robotica',thunkable:'tecnologia informatica',snatchbot:'tecnologia informatica',
  musescore:'musica',incredibox:'musica',musictheory:'musica',librecad:'dibujo tecnico tecnologia'};
 const IDX={};
 const flat=s=>' '+s.replace(/[^a-z0-9ñ]+/g,' ')+' ';
 const joinPh=s=>{let r=' '+s.replace(/[^a-z0-9ñ]+/g,' ')+' ';PHRASES.forEach(([a,b])=>{r=r.split(' '+a+' ').join(' '+b+' ')});return r.trim();};
 const ETN={I:'infantil',P:'primaria',S:'secundaria bachillerato eso'};
 TOOLS.forEach(t=>{const k=t.s+':'+t.cat,c=CAJA.t[t.id];
  const core=norm([t.d,t.a,t.p,SECTIONS[t.s].n,k in CATKW?CATKW[k]:SECTIONS[t.s].cats[t.cat],CAJA.cats[c[0]][0],c[3],SUBJ[t.id],c[1].map(e=>ETN[e]).join(' '),t.c,t.nota,t.coste,t.cta,t.s==='aula'&&/^no necesita/i.test(t.cta)?'nocuenta':''].filter(Boolean).join(' '));
  const ideas=joinPh(norm((t.i||[]).join(' '))),coreJ=joinPh(core),name=joinPh(norm(t.n));
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
