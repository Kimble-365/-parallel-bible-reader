'use strict';
/* Maintained-reader adapter: exact source text or a separate source-token picker. */
(()=>{
 const script=document.currentScript,home=new URL('./',script.src),manifestURL=new URL('packs/manifest.json',home),$=id=>document.getElementById(id);
 const create=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n};
 let library=null,loaded=null,pending=null,generation=0,observer=null,scheduled=false;
 const state={book:null,verifiedVerses:0,unmappedVerses:0,error:null};
 function dependency(){if(window.LexicalPackReader)return Promise.resolve();return new Promise((resolve,reject)=>{const s=create('script');s.src=new URL('lexical-pack-reader.js',home);s.onload=resolve;s.onerror=()=>reject(Error('The lexical pack reader could not load.'));document.head.append(s)})}
 async function getLibrary(){if(library)return library;const r=await fetch(manifestURL);if(!r.ok)throw Error('Lexical packs are unavailable here. Build or download the DavarQadosh reader artifact.');const m=await r.json();if(m.format!=='davarqadosh-library'||m.version!==1||!Array.isArray(m.books))throw Error('Unsupported DavarQadosh catalog.');library=m;return m}
 async function getBook(code){
  if(loaded?.book.manifest.book===code)return loaded.book;
  if(pending?.code===code)return pending.promise;
  const promise=(async()=>{await dependency();const m=(await getLibrary()).books.find(b=>b.book===code);if(!m)throw Error('No lexical pack for this source book.');const next=await LexicalPackReader.load(m,manifestURL);loaded=next;return next.book})();pending={code,promise};
  try{return await promise}finally{if(pending?.promise===promise)pending=null}
 }
 function context(cell){
  const row=cell.closest('.verse,.source-verse');if(!row)return null;
  const pane=cell.closest('.source-pane'),source=pane?.querySelector('select[data-source-slot]');
  return {book:$('book')?.value,chapter:String(source?.value||$('chapter')?.value),verse:String(row.dataset.verse)};
 }
 function sourceKey(book,c){return book.meta.source_book+'.'+c.chapter+'.'+c.verse}
 function reset(title){const dialog=$('study-dialog');if(!dialog)return null;$('study-title').textContent=title;$('study-content').replaceChildren();$('study-status').textContent='';if(!dialog.open)dialog.showModal();return $('study-content')}
 function message(text){if($('study-status'))$('study-status').textContent=text}
 function linkFor(c,token){const url=new URL('index.html',home),p=new URLSearchParams({book:c.book,chapter:c.chapter,verse:c.verse});if(token)p.set('token',token);url.hash=p;return url.href}
 function sourceLink(label,value){const n=create('a',label);try{const u=new URL(value);if(u.protocol==='https:'){n.href=u.href;n.rel='noopener'}}catch{}return n}
 function detail(book,token,c){
  const content=$('study-content');if(!content)return;content.replaceChildren();$('study-title').textContent='Study this Hebrew word';
  const h=create('h3',token.display_form);h.dir='rtl';h.lang=token.language==='arc'?'arc':'he';content.append(h);
  const id=create('p',token.id);id.className='dq-occurrence-id';content.append(id);
  const dl=create('dl');const field=(label,value)=>dl.append(create('dt',label),create('dd',value==null||value===''?'Pending / not supplied':String(value)));
  field('Source reference',token.verse_key);field('Attestation',token.attestation);field('Language',token.language==='arc'?'Biblical Aramaic':token.language==='hbo'?'Biblical Hebrew':'Not tagged');field('Source morphology',token.morphology);field('Source lemma identity',token.lemma);content.append(dl);
  for(const segment of book.segments.filter(s=>s.token_id===token.id)){
   const lemma=book.lemmaMap.get(segment.lemma_id),block=create('section');block.append(create('h4',segment.form));
   block.append(create('p','Lemma ID: '+(segment.lemma_id||'Pending')),create('p','Headword: '+(lemma?.headword||'Pending')),create('p','Headword transliteration: '+(lemma?.transliteration||'Pending')),create('p','Historical dictionary explanation (general, not contextual): '+(lemma?.gloss||'Pending')));
   const source=book.sourceMap.get(lemma?.source_id);if(source)block.append(sourceLink('Dictionary / annotation source',source.url),create('p',source.attribution+' · '+source.license));content.append(block);
  }
  content.append(create('p','Contextual meaning, manuscript checking and independent scholarly verification remain pending.'));
  const full=create('a','Open full contextual research and concordance');full.className='dq-open-research';full.href=linkFor(c,token.id);content.append(full);
  const back=create('button','Choose another source word');back.type='button';back.onclick=()=>picker(book,c);content.append(create('p'),back);message('Verified source occurrence. Imported annotations are not independent contextual review.');back.focus();
 }
 function picker(book,c){
  const content=reset('Study this Hebrew word');if(!content)return;const key=sourceKey(book,c),verse=book.verses.find(v=>v.verse_key===key);
  if(!verse){message('This exact source verse label is unavailable. No approximate occurrence was selected.');return}
  content.append(create('p',key+' · Select a source-defined token. Ketiv and qere remain separate attestations.'));
  const words=create('div');words.className='dq-source-words';words.dir='rtl';
  for(const token of book.tokens.filter(t=>t.verse_key===key)){
   const b=create('button',token.display_form);b.type='button';b.dataset.occurrence=token.id;b.setAttribute('aria-label',token.display_form+' · '+token.attestation+' · '+token.position);b.onclick=()=>detail(book,token,c);if(['qere','alternative'].includes(token.attestation))b.append(create('small',' ['+token.attestation+']'));words.append(b,document.createTextNode(' '));
  }
  content.append(words);message('Source tokens loaded from the verified book database. This picker does not infer a token from an older display.');words.querySelector('button')?.focus();
 }
 async function open(c,tokenId=null){
  reset('Study this Hebrew word');message('Loading and verifying the selected source book…');
  try{const book=await getBook(c.book);if(tokenId){const t=book.tokenMap.get(tokenId);if(!t||t.verse_key!==sourceKey(book,c))throw Error('The occurrence does not belong to this source verse.');detail(book,t,c)}else picker(book,c)}catch(e){message(e.message)}
 }
 function exactTokens(line,book,c){
  const key=sourceKey(book,c),verse=book.verses.find(v=>v.verse_key===key),ref=line.querySelector(':scope > .verse-reference');
  if(!verse||!ref||line.textContent!==ref.textContent+' '+verse.display_text)return false;
  const events=book.events.filter(e=>e.verse_key===key).sort((a,b)=>a.position-b.position),text=events.map(e=>e.text).join('');
  if(text!==verse.display_text)return false;
  if(line.dataset.dqVerified===book.manifest.source_sha256){const targets=[...line.querySelectorAll('.dq-inline-word')],expected=events.filter(e=>e.token_id);return targets.length===expected.length&&targets.every((b,n)=>b.dataset.occurrence===expected[n].token_id&&b.textContent===expected[n].text)}
  if(line.children.length!==1)return false;
  const fragment=document.createDocumentFragment();fragment.append(ref.cloneNode(true),document.createTextNode(' '));
  for(const event of events){if(!event.token_id){fragment.append(document.createTextNode(event.text));continue}
   const token=book.tokenMap.get(event.token_id);if(!token||token.verse_key!==key||token.display_form!==event.text)return false;
   const b=create('button',event.text);b.type='button';b.className='dq-inline-word';b.dataset.occurrence=token.id;b.setAttribute('aria-label','Study this Hebrew word: '+event.text+', '+key+', '+token.position);b.onclick=()=>open(c,token.id);fragment.append(b);
  }
  line.dataset.dqVerified=book.manifest.source_sha256;line.replaceChildren(fragment);return true;
 }
 async function refresh(){
  const seq=++generation,cells=[...$('verses').querySelectorAll('.translation[data-edition="hbo-wlc"]')];state.verifiedVerses=state.unmappedVerses=0;
  if(!cells.length){state.book=null;state.error=null;return}
  const first=context(cells[0]);if(!first)return;state.book=first.book;
  for(const cell of cells){const c=context(cell);if(!c||cell.querySelector(':scope > .dq-verse-action'))continue;const b=create('button','Study this Hebrew word');b.type='button';b.className='dq-verse-action';b.onclick=()=>open(c);cell.append(b)}
  try{const book=await getBook(first.book);if(seq!==generation)return;state.error=null;
   observer.disconnect();try{for(const cell of cells){const c=context(cell);if(!c)continue;for(const line of cell.querySelectorAll('.original .verse-line')){if(exactTokens(line,book,c))state.verifiedVerses++;else{for(const b of line.querySelectorAll('.dq-inline-word'))b.replaceWith(document.createTextNode(b.textContent));delete line.dataset.dqVerified;state.unmappedVerses++}}}}finally{observe()}
  }catch(e){if(seq===generation)state.error=e.message}
 }
 function observe(){observer.observe($('verses'),{childList:true,subtree:true})}
 function queue(){if(scheduled)return;scheduled=true;queueMicrotask(()=>{scheduled=false;refresh()})}
 function menu(){const content=$('study-content');if(!content||$('menu-davarqadosh'))return;
  const cells=[...$('verses').querySelectorAll('.translation[data-edition="hbo-wlc"]')];if(!cells.length)return;
  const b=create('button','DavarQadosh — Hebrew word study');b.id='menu-davarqadosh';b.type='button';b.onclick=()=>{const hash=new URL(ReaderStateUrl()).hash.slice(1).split('.'),cell=cells.find(c=>context(c)?.verse===hash[2])||cells[0];open(context(cell))};const p=create('p');p.append(b);content.append(p);
 }
 async function install(){
  if(!$('verses')||!$('menu-study'))return;
  const style=create('style');style.textContent='.dq-inline-word{display:inline;font:inherit;line-height:inherit;padding:0;border:0;border-radius:0;background:transparent;color:inherit;user-select:text;vertical-align:baseline}.dq-inline-word:hover{background:var(--button,#e0ead5)}.dq-inline-word:focus-visible{outline:2px solid var(--accent,#75501a)}.dq-verse-action{font:14px/1.5 system-ui;margin-top:.5em}.dq-source-words button{font:24px/1.8 serif;margin:.15em}.dq-occurrence-id{overflow-wrap:anywhere;font:12px/1.6 monospace}';document.head.append(style);
  observer=new MutationObserver(queue);observe();$('menu-study').addEventListener('click',menu);await refresh();
 }
 window.DavarQadoshIntegration={open,refresh,get state(){return {...state}},get sourceBook(){return loaded?.book}};
 Promise.resolve(window.ReaderLayoutReady).then(install).catch(e=>{state.error=e.message});
})();
