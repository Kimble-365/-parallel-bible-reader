'use strict';
(()=>{
 const KEY='bible-reader-highlights-v1',colors=['yellow','green','blue','pink'];
 const records=new WeakMap();let active=null,origin=null,pointer=null;
 const make=(tag,text)=>{const n=document.createElement(tag);if(text)n.textContent=text;return n;};
 const dialog=make('dialog');dialog.id='verse-actions';dialog.setAttribute('aria-labelledby','verse-actions-title');
 const title=make('h2');title.id='verse-actions-title';const edition=make('p');edition.id='verse-actions-edition';
 const preview=make('p');preview.id='verse-actions-preview';preview.dir='auto';
 const tools=make('div');tools.className='notes-actions';const status=make('p');status.id='verse-actions-status';status.setAttribute('role','status');
 const close=make('button','Back to reading');close.type='button';close.onclick=()=>dialog.close();
 dialog.append(title,edition,preview,tools,status,close);document.body.append(dialog);
 let highlights={},corrupt=false;
 function read(){try{const raw=localStorage.getItem(KEY);if(raw===null)return {};if(raw.length>300000)throw Error('oversized');const v=JSON.parse(raw);if(!v||Array.isArray(v)||typeof v!=='object'||Object.keys(v).length>2000||Object.entries(v).some(([k,c])=>k.length>250||!colors.includes(c)))throw Error('invalid');return v;}catch{corrupt=true;return {};}}
 highlights=read();
 const key=r=>JSON.stringify([r.edition,r.book,String(r.chapter),String(r.verse)]);
 function paint(node,r){const value=Object.hasOwn(highlights,key(r))?highlights[key(r)]:'';if(value)node.dataset.highlight=value;else delete node.dataset.highlight;}
 function setHighlight(color){if(!active)return;if(corrupt){status.textContent='Existing highlights could not be read. They have not been overwritten.';return;}const next={...highlights},id=key(active);if(color){if(!Object.hasOwn(next,id)&&Object.keys(next).length>=2000){status.textContent='Highlight limit reached. Remove an older highlight first.';return;}next[id]=color;}else delete next[id];
  try{const raw=JSON.stringify(next);if(raw.length>300000)throw Error('Highlight storage limit');localStorage.setItem(KEY,raw);highlights=next;document.querySelectorAll('#verses .translation').forEach(n=>{const r=records.get(n);if(r)paint(n,r);});status.textContent=color?'Highlight saved on this device.':'Highlight removed.';}catch{status.textContent='Highlight not saved. Your browser could not save changes.';}}
 function button(label,fn){const b=make('button',label);b.type='button';b.onclick=fn;tools.append(b);return b;}
 button('Copy',async()=>{if(!active)return;const text=window.ReaderVerseBridge.copy(active);try{await navigator.clipboard.writeText(text);status.textContent='Verse copied.';}catch{fallback.hidden=false;fallback.value=text;fallback.focus();fallback.select();status.textContent='Use your browser’s Copy command on the selected text.';}});
 button('Copy to Notes',()=>{if(!active)return;try{window.ReaderNotesUI.addQuote(window.ReaderVerseBridge.quote(active));dialog.close();}catch(e){status.textContent=e.message;}});
 const bookmark=button('Bookmark',()=>{if(!active)return;window.ReaderVerseBridge.bookmark(active);bookmark.setAttribute('aria-pressed',String(window.ReaderVerseBridge.isBookmarked(active)));bookmark.textContent=window.ReaderVerseBridge.isBookmarked(active)?'Remove bookmark':'Bookmark';status.textContent=document.getElementById('reading-feedback').textContent;});
 button('Share',()=>{if(!active)return;const r=active;dialog.close();window.ReaderVerseBridge.share(r);});
 const compare=make('section');compare.id='verse-comparison';compare.hidden=true;dialog.insertBefore(compare,status);
 button('Compare',()=>{if(!active)return;compare.replaceChildren(make('h3','Selected translations'),make('p','Comparison by displayed verse labels only, not verified equivalent passages. Independent source chapters may differ.'));for(const item of window.ReaderVerseBridge.comparison(active)){const section=make('section'),heading=make('h4','Text '+item.slot+' · '+item.edition),text=make('p',item.quote?.text||item.reason);section.append(heading);if(item.quote){section.append(make('p',item.quote.reference));text.lang=item.quote.language;text.dir=item.quote.direction;}section.append(text);compare.append(section);}compare.hidden=false;compare.scrollIntoView({block:'nearest'});});
 const imageButton=button('Verse image',async()=>{if(!active)return;const selected=active,q=window.ReaderVerseBridge.quote(selected),bodyStyle=getComputedStyle(document.body),sample=origin.querySelector('.original,.roman'),family=sample?getComputedStyle(sample).fontFamily:'serif';imageButton.disabled=true;status.textContent='Creating PNG on this device…';try{const blob=await ReaderVerseMedia.image(q,{family,background:bodyStyle.backgroundColor,ink:bodyStyle.color});if(active!==selected||!dialog.open)return;const url=URL.createObjectURL(blob),a=make('a');a.href=url;a.download='bible-verse-'+selected.book+'-'+String(selected.chapter)+'-'+String(selected.verse)+'.png';a.hidden=true;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);status.textContent='PNG created. Your verse was not uploaded.';}catch(e){if(active===selected)status.textContent=e.message;}finally{imageButton.disabled=false;}});
 const palette=make('fieldset'),legend=make('legend','Highlight');palette.append(legend);
 for(const color of colors){const b=make('button',color[0].toUpperCase()+color.slice(1));b.type='button';b.dataset.color=color;b.onclick=()=>setHighlight(color);palette.append(b);}
 const remove=make('button','Remove highlight');remove.type='button';remove.onclick=()=>setHighlight('');palette.append(remove);dialog.insertBefore(palette,status);
 const fallback=make('textarea');fallback.id='verse-copy-fallback';fallback.readOnly=true;fallback.hidden=true;fallback.setAttribute('aria-label','Verse text to copy');dialog.insertBefore(fallback,status);
 function open(node,r){if(!window.ReaderVerseBridge||!node.isConnected)return;active=r;origin=node;const q=window.ReaderVerseBridge.quote(r);title.textContent=q.reference;edition.textContent='Text '+r.slot+' · '+q.edition;preview.textContent=q.text;preview.lang=q.language;preview.dir=q.direction;fallback.hidden=true;compare.hidden=true;status.textContent=corrupt?'Existing highlights could not be read. They have not been overwritten.':'';bookmark.textContent=window.ReaderVerseBridge.isBookmarked(r)?'Remove bookmark':'Bookmark';bookmark.setAttribute('aria-pressed',String(window.ReaderVerseBridge.isBookmarked(r)));dialog.showModal();tools.querySelector('button').focus();}
 dialog.addEventListener('close',()=>{active=null;if(origin?.isConnected)origin.focus({preventScroll:true});});
 function bind(node,r){if(records.has(node))return;records.set(node,r);node.tabIndex=0;node.setAttribute('role','button');node.setAttribute('aria-haspopup','dialog');node.setAttribute('aria-label','Verse actions: '+window.ReaderVerseBridge.reference(r)+' — Text '+r.slot+'. '+node.textContent);paint(node,r);
  node.addEventListener('pointerdown',e=>{pointer={x:e.clientX,y:e.clientY,node};});
  node.addEventListener('click',e=>{if(e.target.closest('a,button,input,select')||getSelection()?.toString().trim())return;if(pointer?.node===node&&Math.hypot(e.clientX-pointer.x,e.clientY-pointer.y)>10)return;open(node,r);});
  node.addEventListener('keydown',e=>{if(e.target===node&&(e.key==='Enter'||e.key===' ')){e.preventDefault();open(node,r);}});
 }
 new MutationObserver(()=>{if(dialog.open&&!origin?.isConnected)dialog.close();}).observe(document.getElementById('verses'),{childList:true,subtree:true});
 window.addEventListener('storage',e=>{if(e.key===KEY||e.key===null){corrupt=false;highlights=read();document.querySelectorAll('#verses .translation').forEach(n=>{const r=records.get(n);if(r)paint(n,r);});}});
 window.ReaderVerseActions={bind};document.querySelectorAll('#verses .translation').forEach(n=>{if(n._verseActionRecord)bind(n,n._verseActionRecord);});
})();

