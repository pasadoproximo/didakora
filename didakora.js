// Didakora: comportamiento común de todas sus páginas y listado con buscador (/todas/)
(()=>{
// compartir la ficha: menú del sistema si existe; si no, se copia el enlace
document.addEventListener('click',async e=>{const b=e.target.closest('[data-share]');if(!b)return;
 const data={title:document.title,url:location.href};
 try{if(navigator.share){await navigator.share(data);return;}await navigator.clipboard.writeText(location.href);const o=b.innerHTML;b.textContent='Enlace copiado';setTimeout(()=>{b.innerHTML=o},1800);}catch(err){}
});
})();

// ---------- listado completo
function cajaListado(){
 const $=id=>document.getElementById(id);
 const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 const norm=s=>String(s).normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
 // búsqueda: palabras completas, plurales, términos relacionados y frases (la misma que tenía la caja)
 const stem=w=>w.length>4&&w.endsWith('es')?w.slice(0,-2):w.length>3&&w.endsWith('s')?w.slice(0,-1):w;
 const STOP=new Set('de la el los las un una unos unas y o a en con para por del al que se su sus mi me lo como'.split(' '));
 const SYN={evaluacion:['evaluar','rubrica','calificar','corregir'],evaluar:['evaluacion','rubrica','calificar','corregir'],rubrica:['evaluacion','evaluar'],
  cuestionario:['quiz','test','preguntas','encuesta'],quiz:['cuestionario','test','preguntas'],test:['cuestionario','quiz','preguntas'],
  video:['audiovisual','grabar'],mapa:['cartografia'],imagen:['foto','fotografia','ilustracion'],foto:['imagen','fotografia'],podcast:['audio','radio'],
  presentacion:['diapositivas','exposicion'],diapositivas:['presentacion'],cronologia:['linea del tiempo','eje cronologico'],
  equipo:['colaborar','colaborativo','cooperativo'],colaborar:['equipo','colaborativo','cooperativo'],programar:['informatica'],
  gratis:['gratuito','gratuita','sin coste','libre'],gratuito:['gratis','gratuita','sin coste','libre'],
  gamificacion:['juego','jugar','concurso','gamificado'],juego:['jugar','concurso','gamificado'],
  dislexia:['lectura en voz alta','dificultades de lectura','dificultades de escritura','accesibilidad'],accesibilidad:['lectura en voz alta','dictado','dificultades'],familia:['familias']};
 const PHRASES=[['inteligencia artificial','ia'],['realidad aumentada','ra'],['tres dimensiones','3d'],['no necesita cuenta','nocuenta'],['sin cuenta','nocuenta'],['sin registro','nocuenta'],['sin registrarse','nocuenta'],['educacion fisica','educacionfisica']];
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
 TOOLS.forEach(t=>{const k=t.s+':'+t.cat;
  const core=norm([t.n,t.a,t.p,t.d,SECTIONS[t.s].n,k in CATKW?CATKW[k]:SECTIONS[t.s].cats[t.cat],CAJA.cats[CAJA.t[t.id][0]][0],SUBJ[t.id],t.c,t.nota,t.coste,t.cta,t.s==='aula'&&/^no necesita/i.test(t.cta)?'nocuenta':''].filter(Boolean).join(' '));
  const ideas=joinPh(norm((t.i||[]).join(' '))),coreJ=joinPh(core);
  IDX[t.id]={ct:flat(coreJ),it:flat(ideas),nw:words(t.n),cw:new Set(words(coreJ).map(stem)),iw:new Set(words(ideas).map(stem))};});
 const forms=w=>[w,...(SYNS[stem(w)]||[])];
 const hit=(id,w,last)=>{const X=IDX[id];
  if(last&&w.length>=2&&X.nw.some(x=>x.startsWith(w)))return true;
  return forms(w).some(f=>{if(f.includes(' '))return X.ct.includes(' '+f+' ')||X.it.includes(' '+f+' ');const sf=stem(f);return X.cw.has(sf)||(sf.length>3&&X.iw.has(sf));});};
 const query=raw=>{let r=' '+norm(raw).replace(/[^a-z0-9ñ]+/g,' ')+' ';PHRASES.forEach(([a,b])=>{r=r.split(' '+a+' ').join(' '+b+' ')});return words(r).filter(w=>!STOP.has(w));};
 const match=(t,qs)=>!qs.length||qs.every((w,i)=>hit(t.id,w,i===qs.length-1));

 // tarjeta: la misma que generan las páginas estáticas
 const B=window.DK_BASE||'';
 const EXT='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>';
 const lead=t=>t.s==='aula'?t.a:t.s==='docente'?t.p:t.d;
 const card=t=>{const m=t.n.match(/^(.+?)\s*\((.+)\)$/),nm=m?m[1]:t.n,[cs,,hasLogo]=CAJA.t[t.id],[cn,ci]=CAJA.cats[cs];
  const lg=hasLogo?`<img src="${B}/logos/${t.id}.png?v=3" alt="" width="26" height="26" loading="lazy">`:`<b aria-hidden="true">${esc(t.n[0])}</b>`;
  return `<article class="tc"><div class="tc-h"><span class="lg">${lg}</span><h3><a class="tc-a" href="${B}/${t.id}/">${esc(nm)}</a>${m?`<small>${esc(m[2])}</small>`:''}</h3></div><p>${esc(lead(t))}</p>`+
   `<div class="tc-f"><a class="tc-go" href="${esc(t.url)}" rel="noopener" target="_blank">Abrir ${EXT}<span class="sr"> ${esc(nm)} (se abre en otra pestaña)</span></a>`+
   `<a class="tag" href="${B}/categorias/${cs}/"><svg viewBox="0 0 24 24" aria-hidden="true">${ci}</svg>${esc(cn)}</a></div></article>`;};

 const P=new URLSearchParams(location.search);
 const st={q:P.get('q')||'',nivel:P.get('nivel')||'',cat:P.get('cat')||'',nuevas:P.get('nuevas')==='1'};
 const qEl=$('lq'),nEl=$('lnv');qEl.value=st.q;nEl.value=st.nivel;
 const NV={I:'Infantil',P:'Primaria',S:'Secundaria y Bachillerato'};
 function render(){
  const qs=query(st.q);
  const list=TOOLS.filter(t=>match(t,qs)&&(!st.nivel||CAJA.t[t.id][1].includes(st.nivel))&&(!st.cat||CAJA.t[t.id][0]===st.cat)&&(!st.nuevas||t.st==='nueva'));
  $('lgrid').innerHTML=list.map(card).join('')||`<div class="empty"><p>No hay resultados${st.q?` para «${esc(st.q)}»`:''}.</p><p>Prueba con otra palabra o con lo que quieres hacer, por ejemplo «evaluar» o «vídeo».</p><button type="button" class="btn solid" data-reset>Ver todas</button></div>`;
  document.querySelectorAll('#lcats button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.cat===st.cat));
  const extra=[st.nuevas?'nuevas en 2026':'',st.nivel?NV[st.nivel]:''].filter(Boolean).join(' · ');
  $('lcount').textContent=`${list.length} ${list.length===1?'herramienta':'herramientas'}${extra?' · '+extra:''}`;
  const u=new URLSearchParams();if(st.q)u.set('q',st.q);if(st.nivel)u.set('nivel',st.nivel);if(st.cat)u.set('cat',st.cat);if(st.nuevas)u.set('nuevas','1');
  history.replaceState(null,'',location.pathname+(u.toString()?'?'+u:''));
 }
 qEl.addEventListener('input',()=>{st.q=qEl.value;render();});
 nEl.addEventListener('change',()=>{st.nivel=nEl.value;render();});
 $('lcats').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;st.cat=b.dataset.cat;render();});
 document.addEventListener('click',e=>{if(e.target.closest('[data-reset]')){Object.assign(st,{q:'',nivel:'',cat:'',nuevas:false});qEl.value='';nEl.value='';render();qEl.focus();}});
 render();
}

// en pantallas estrechas, el texto de ayuda del buscador corto para que no se corte
(()=>{const mq=matchMedia('(max-width:560px)'),els=[...document.querySelectorAll('#hq,#lq')];
 const f=()=>els.forEach(e=>{e.dataset.ph=e.dataset.ph||e.placeholder;e.placeholder=mq.matches?'Busca una herramienta o tarea…':e.dataset.ph;});
 f();mq.addEventListener('change',f);})();
