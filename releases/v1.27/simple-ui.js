'use strict';
(()=>{
 const $=id=>document.getElementById(id),make=(tag,text)=>{const e=document.createElement(tag);if(text)e.textContent=text;return e};
 const bar=make('nav');bar.id='top-menu';bar.setAttribute('aria-label','Reader menu');
 const title=make('a','Bible Reader');title.href='#reading';const home=make('div');home.id='reader-home';home.append(title);bar.append(home);const menu=make('div');menu.id='reader-menu-actions';menu.setAttribute('role','group');menu.setAttribute('aria-label','Reader tools');bar.append(menu);
 const quickLabel=make('label','Favorite Bible');quickLabel.htmlFor='quick-bible';const quick=make('select');quick.id='quick-bible';quickLabel.append(quick);home.append(quickLabel);
 const dialog=make('dialog');dialog.id='reader-settings';dialog.setAttribute('aria-labelledby','settings-title');const heading=make('h2','Reader settings & tools');heading.id='settings-title';const close=make('button','Back to reading');close.type='button';close.onclick=()=>dialog.close();dialog.append(heading,close);
 const textSize=make('div');textSize.className='notes-actions';textSize.setAttribute('aria-label','Text size');for(const id of ['font-smaller','font-size','font-larger','reading-mode'])textSize.append($(id));dialog.append(textSize);
 const header=document.querySelector('body > header');const chapterNav=header.querySelector('nav[aria-label="Book and chapter"]');chapterNav.id='chapter-navigation';
 const tools=make('div');tools.id='additional-tools';
 for(const node of [...document.body.children])if(node!==header&&node.matches('aside,details.reader-extras,footer'))tools.append(node);
 const intro=$('book-intro');if(intro)tools.append(intro);const publication=$('lxxl-publication');if(publication)tools.append(publication);dialog.append(header,tools);chapterNav.prepend($('prev'));chapterNav.append($('next'));bar.append(chapterNav);document.body.prepend(bar);document.body.append(dialog);
 function open(target){if(!dialog.open)dialog.showModal();if(target){const el=$(target);if(el){if(el.tagName==='DETAILS')el.open=true;el.scrollIntoView({block:'start'});el.querySelector('input,select,button,summary')?.focus()}}else{dialog.scrollTop=0;close.focus()}}
 for(const [label,target]of [['Settings',null],['Search','search-panel'],['Listen','audio-panel'],['Watch','film-panel'],['Offline','offline-panel']]){const b=make('button',label);b.type='button';b.setAttribute('aria-haspopup','dialog');b.onclick=()=>open(target);menu.append(b)}
 const notes=make('button','Notes');notes.type='button';notes.onclick=()=>$('notes-open').click();menu.append(notes);
 const library=make('a','Languages');library.href='translations/';menu.append(library);new MutationObserver(()=>{for(const child of [...bar.children])if(child!==home&&child!==menu&&child!==chapterNav)menu.append(child)}).observe(bar,{childList:true});
 const selectors=header.querySelector('.selectors');selectors.id='text-settings';const explain=make('p','Choose one to four Bibles below. Each comparison can be set to None independently. Under Reading appearance choose Original, Both (text + transliteration), or Latin.');selectors.before(explain);
 const display=$('text-display');for(const o of display.options)if(o.value==='both')o.textContent='Text + transliteration';else if(o.value==='original')o.textContent='Text only';else if(o.value==='latin')o.textContent='Transliteration only';
 function sync(){library.href=$('browse-0').href;let ids=[];try{ids=JSON.parse(localStorage.getItem('bible-reader-favorites-v1')||'[]')}catch{}if(!Array.isArray(ids))ids=[];const current=$('primary').value;const rows=BibleCatalog.editions.filter(e=>ids.includes(e.id)||e.id===current);quick.replaceChildren();for(const e of rows){const o=make('option',e.label+(ids.includes(e.id)?' ★':''));o.value=e.id;quick.append(o)}if(!current){const o=make('option','Choose a Bible in Settings');o.value='';quick.prepend(o)}quick.value=current;}
 quick.onchange=()=>{const select=$('primary');if(![...select.options].some(o=>o.value===quick.value)){const o=make('option',BibleCatalog.editions.find(e=>e.id===quick.value)?.label||quick.value);o.value=quick.value;select.append(o)}select.value=quick.value;select.dispatchEvent(new Event('change',{bubbles:true}))};
 new MutationObserver(sync).observe($('primary'),{childList:true,subtree:true});document.addEventListener('change',sync);dialog.addEventListener('click',e=>{if(e.target.closest('.result'))dialog.close()});document.addEventListener('click',e=>{if(e.target.closest('[id^="favorite-"]'))sync()});sync();
 try{localStorage.setItem('bible-reader-simple-ui-115','true')}catch{}
})();

