'use strict';
(()=>{
 const $=id=>document.getElementById(id),R=LexicalPackReader,base=new URL('packs/manifest.json',location.href);
 let library=null,loaded=null,companion=null,active=null,chapter='1',request=0,tokenIndex=new Map(),eventsIndex=new Map(),segmentsIndex=new Map(),recordIndex=new Map(),selected=null;
 const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n};
 function status(text,error=false){$('status').textContent=text;$('status').classList.toggle('error',error)}
 function option(select,value,label){const o=el('option',label);o.value=String(value);select.append(o)}
 function group(rows,key){const m=new Map();for(const r of rows){if(!m.has(r[key]))m.set(r[key],[]);m.get(r[key]).push(r)}return m}
 function chapters(){return [...new Set(active.verses.map(v=>v.chapter))]}
 function safeLink(label,url){const a=el('a',label);try{const u=new URL(url);if(u.protocol==='https:'){a.href=u.href;a.rel='noopener'}}catch{}return a}
 function install(book){
  active=book;selected=null;tokenIndex=group(book.tokens,'verse_key');eventsIndex=group(book.events,'verse_key');segmentsIndex=group(book.segments,'token_id');recordIndex=group(book.research,'verse_key');
  $('chapter').replaceChildren();for(const c of chapters())option($('chapter'),c,c);$('save').disabled=!loaded;
  const count=book.manifest.coverage;$('coverage').textContent=`${book.manifest.book}: ${book.manifest.verses.toLocaleString()} source verses · ${count.ingested.toLocaleString()} word attestations · ${count.morphologically_analyzed.toLocaleString()} imported morphology annotations · ${count.semantically_reviewed} contextually reviewed · ${count.manuscript_checked} manuscript checked · ${count.translations_checked} translations checked · ${count.fully_verified} fully verified.`;
  $('study').replaceChildren(el('h2','Study this Hebrew word'),el('p','Select a source word. Research gaps remain pending.'));
 }
 function setLocation(verse,token){const p=new URLSearchParams();p.set('book',active.manifest.book);p.set('chapter',chapter);if(verse)p.set('verse',verse);if(token)p.set('token',token);history.replaceState(null,'','#'+p);}
 function currentVerse(){return active?.verses.find(v=>v.chapter===chapter)}
 function mainLink(verse){return '../releases/v1.27/?edition=hbo-wlc&compare1=engwebp&compare2=&compare3=&text=original#'+active.manifest.book+'.'+chapter+'.'+verse}
 function draw(){
  if(!active)return;const values=chapters();if(!values.includes(chapter))chapter=values[0];$('chapter').value=chapter;
  $('previous').disabled=values.indexOf(chapter)===0;$('next').disabled=values.indexOf(chapter)===values.length-1;
  $('main-reader').href=mainLink(currentVerse().verse_label);const fragment=document.createDocumentFragment(),eid=$('comparison').value;
  for(const v of active.verses.filter(v=>v.chapter===chapter)){
   const section=el('article',undefined,'verse');section.id='verse-'+v.verse_label;section.dataset.verse=v.verse_label;
   section.append(el('p',v.verse_key,'reference'));const texts=el('div',undefined,'texts'+(!eid?' single':'')),source=el('div',undefined,'source');source.dir='rtl';source.lang='he';
   for(const event of eventsIndex.get(v.verse_key)||[]){
    if(event.token_id){const token=active.tokenMap.get(event.token_id),button=el('button',event.text,'word');button.type='button';button.dataset.token=token.id;button.setAttribute('aria-label',`Study this Hebrew word: ${event.text}, ${v.verse_key}, ${token.position}`);button.setAttribute('aria-pressed',String(selected===token.id));button.onclick=()=>study(token.id);source.append(button)}else source.append(document.createTextNode(event.text));
   }
   texts.append(source);
   if(eid){const side=el('div'),meta=library?.comparison_editions?.[eid];side.append(el('p',meta?.label||eid,'reference'));const matches=companion?.data.editions?.[eid]?.filter(r=>String(r[0])===v.chapter&&String(r[1])===v.verse_label)||[];const p=el('div',matches.length?matches.map(r=>r[2]||'').join('\n'):'No acquired text under this source label.','parallel');p.dir=meta?.direction||'ltr';side.append(p);texts.append(side)}
   section.append(texts);const variants=(tokenIndex.get(v.verse_key)||[]).filter(t=>['qere','alternative'].includes(t.attestation));
   if(variants.length){const detail=el('details'),summary=el('summary','Qere / alternative source attestations');detail.append(summary);for(const t of variants){const b=el('button',t.display_form+' · '+t.attestation);b.dir='rtl';b.onclick=()=>study(t.id);detail.append(b)}section.append(detail)}
   fragment.append(section);
  }
  $('verses').replaceChildren(fragment);
 }
 function field(dl,label,value){dl.append(el('dt',label),el('dd',value===null||value===undefined||value===''?'Pending / not supplied by source':String(value)))}
 function study(id,scroll=false){
  const t=active?.tokenMap.get(id);if(!t)return;selected=id;const v=active.verses.find(v=>v.verse_key===t.verse_key);
  if(chapter!==v.chapter){chapter=v.chapter;draw()}
  for(const b of $('verses').querySelectorAll('button.word'))b.setAttribute('aria-pressed',String(b.dataset.token===id));
  const pane=$('study');pane.replaceChildren(el('h2',t.display_form,'hebrew'),el('p',t.id,'token-id'));pane.firstElementChild.dir='rtl';
  const dl=el('dl');field(dl,'Reference / attestation',t.verse_key+' · '+t.attestation);field(dl,'Source form with segmentation',t.form);field(dl,'Language',t.language==='arc'?'Biblical Aramaic':t.language==='hbo'?'Biblical Hebrew':'Not tagged');field(dl,'Raw OSHB morphology',t.morphology);field(dl,'Source lemma identity',t.lemma);field(dl,'Qere alignment',t.aligned_to);pane.append(dl);
  const lexical=el('section');lexical.append(el('h3','Lexical segments'));
  for(const s of segmentsIndex.get(id)||[]){
   const l=active.lemmaMap.get(s.lemma_id);const block=el('div');block.append(el('p',s.form,'hebrew'));const d=el('dl');field(d,'Stable lemma identity',s.lemma_id);field(d,'Dictionary headword',l?.headword);field(d,'Headword transliteration',l?.transliteration);field(d,'Historical dictionary gloss — general, not contextual',l?.gloss);field(d,'Segment morphology',s.morphology);field(d,'Review state',l?.verification);block.append(d);
   const source=active.sourceMap.get(l?.source_id);if(source)block.append(safeLink('Dictionary / annotation source',source.url),el('p',source.attribution+' · '+source.license,'notice'));
   if(l?.gloss)block.append(el('p','A broad Strong-number link does not resolve augmented homographs or validate this occurrence’s sense.','notice'));lexical.append(block);
  }
  pane.append(lexical,el('h3','Contextual meaning'),el('p','Pending: this occurrence has not received independent semantic review.'));
  const evidence=el('details');evidence.append(el('summary','Manuscripts, ancient versions and research'));
  const imported=recordIndex.get(t.verse_key)||[],published=companion?.data.research_records?.filter(r=>r.locus===t.verse_key)||[];
  for(const record of [...imported,...published]){const item=el('details');item.append(el('summary',(record.id||'Research record')+' · '+(record.evidence_class||'editorial draft')),el('p','Source report / inherited research status; no new manuscript collation or occurrence-level adoption is asserted.','notice'),el('pre',record.record_json||JSON.stringify(record,null,2)));evidence.append(item)}
  if(!imported.length&&!published.length)evidence.append(el('p','Not checked for this occurrence. No absence of variants or manuscript agreement is inferred.'));
  evidence.append(safeLink('Existing BHH source library','https://kimble-365.github.io/-parallel-bible-reader/releases/v1.27/bhh.html'),document.createTextNode(' · '),safeLink('Existing LXXL source apparatus','https://kimble-365.github.io/-parallel-bible-reader/releases/v1.27/?edition=hbo-wlc#'+active.manifest.book+'.'+v.chapter+'.'+v.verse_label));pane.append(evidence);
  const concordance=el('details');concordance.append(el('summary','Concordance within this source book'));
  const lids=new Set((segmentsIndex.get(id)||[]).map(s=>s.lemma_id).filter(Boolean));const ids=new Set(active.segments.filter(s=>lids.has(s.lemma_id)).map(s=>s.token_id));const list=el('div',undefined,'concordance');
  for(const otherId of ids){const other=active.tokenMap.get(otherId),b=el('button',other.verse_key+' · '+other.display_form);b.onclick=()=>study(otherId,true);list.append(b)}
  concordance.append(el('p',ids.size+' attestations sharing a source lemma ID in this book; no sense counts or cross-book completeness is asserted.','notice'),list);pane.append(concordance);
  const row=el('p'),position=active.tokens.findIndex(x=>x.id===id);
  for(const [label,delta]of [['Previous occurrence',-1],['Next occurrence',1]]){const b=el('button',label),target=active.tokens[position+delta];b.disabled=!target;b.onclick=()=>study(target.id,true);row.append(b,document.createTextNode(' '))}pane.append(row);
  const citation=`${t.verse_key}, ${t.attestation}, ${t.id}; OSHB ${active.manifest.source_revision}; source SHA-256 ${active.manifest.source_sha256}. Research pending.`,copy=el('button','Copy citation');copy.onclick=async()=>{try{await navigator.clipboard.writeText(citation);status('Citation copied.')}catch{status(citation)}};pane.append(copy,safeLink('Open full parallel reader',new URL(mainLink(v.verse_label),location.href).href));
  const raw=el('details');raw.append(el('summary','Exact source verse XML'),el('pre',v.source_xml));pane.append(raw);setLocation(v.verse_label,id);
  if(scroll)$('verse-'+v.verse_label)?.scrollIntoView({block:'start'});
 }
 async function openBook(code,desiredChapter='1',desiredVerse=null,desiredToken=null){
  const seq=++request,meta=library?.books.find(b=>b.book===code);if(!meta)return;status('Loading and verifying '+code+'…');$('save').disabled=true;
  try{
   const next=await R.load(meta,base);let comparison=null,warning='';try{comparison=await R.companion(meta.parallel,base)}catch(e){warning=' Comparison unavailable: '+e.message}
   if(seq!==request)return;loaded=next;companion=comparison;install(next.book);chapter=desiredChapter;$('book').value=code;draw();setLocation(desiredVerse||currentVerse().verse_label);
   if(desiredToken)study(desiredToken);if(desiredVerse)$('verse-'+desiredVerse)?.scrollIntoView({block:'start'});
   status('Verified '+code+'. Select a word to study.'+warning,!!warning);
  }catch(e){if(seq!==request)return;$('save').disabled=!loaded;status('Could not open '+code+': '+e.message+' Your previously opened text is retained.',true);if(active)$('book').value=active.manifest.book}
 }
 $('book').onchange=()=>openBook($('book').value);
 $('chapter').onchange=()=>{chapter=$('chapter').value;draw();setLocation(currentVerse().verse_label)};
 for(const [id,delta]of [['previous',-1],['next',1]])$(id).onclick=()=>{const list=chapters(),next=list[list.indexOf(chapter)+delta];if(next){chapter=next;draw();setLocation(currentVerse().verse_label)}};
 $('comparison').onchange=()=>{draw();if(selected)study(selected)};
 $('save').onclick=async()=>{if(!loaded)return;const chosen=loaded,comparison=companion;try{await R.save(chosen);await R.saveCompanion(comparison);status('Verified '+chosen.book.manifest.book+' saved offline with its available parallel texts.')}catch(e){status('Could not save: '+e.message,true)}};
 $('clear').onclick=async()=>{try{await R.clear();status('DavarQadosh saved book packs removed. Other reader stores are unchanged.')}catch(e){status(e.message,true)}};
 $('open-local').onclick=async()=>{const pack=$('local-pack').files[0],manifest=$('local-manifest').files[0];try{if(!pack||!manifest)throw Error('Choose both pack and manifest.');if(pack.size>R.limits.MAX_PACK||manifest.size>65536)throw Error('Local file exceeds the supported limit.');const meta=JSON.parse(await manifest.text()),bytes=new Uint8Array(await pack.arrayBuffer()),book=await R.open(bytes,meta);request++;loaded=null;companion=null;install(book);chapter='1';draw();setLocation(currentVerse().verse_label);status('Verified local '+meta.book+' pack opened. Parallel sidecar is not included in this local-file import.')}catch(e){status('Could not open local pack: '+e.message,true)}};
 async function start(){
  if('serviceWorker'in navigator)try{await navigator.serviceWorker.register('sw.js')}catch{}
  try{const r=await fetch(base);if(!r.ok)throw Error('Build or download the reader artifact containing packs/manifest.json.');library=await r.json();if(library.format!=='davarqadosh-library'||library.version!==1||!Array.isArray(library.books)||!library.books.length)throw Error('Unsupported or empty library manifest.');for(const m of library.books){R.validateManifest(m);option($('book'),m.book,m.book)}const p=new URLSearchParams(location.hash.slice(1));await openBook(p.get('book')||library.books[0].book,p.get('chapter')||'1',p.get('verse'),p.get('token'))}catch(e){status(e.message+' You can also open a local pack below.',true)}
 }
 window.DavarQadosh={study,openBook,get book(){return active},get library(){return library}};start();
})();
