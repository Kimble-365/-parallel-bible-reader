'use strict';
(function(root){
 const KEY='bible-reader-font-v1';
 const choices=Object.freeze([
  {id:'default',label:'Reader default',stack:''},
  {id:'system',label:'System sans serif',stack:'system-ui, "Noto Sans", sans-serif'},
  {id:'book',label:'Book serif (Georgia)',stack:'Georgia, "Noto Serif", serif'},
  {id:'classic',label:'Classic serif (Palatino)',stack:'Palatino, "Palatino Linotype", "Book Antiqua", "Noto Serif", serif'},
  {id:'humanist',label:'Humanist sans (Trebuchet)',stack:'"Trebuchet MS", "Noto Sans", sans-serif'},
  {id:'mono',label:'Monospace',stack:'ui-monospace, "Noto Sans Mono", monospace'}
 ]);
 const normalize=value=>choices.some(c=>c.id===value)?value:'default';
 function read(storage){try{return normalize(storage.getItem(KEY));}catch{return 'default';}}
 function save(storage,value){try{storage.setItem(KEY,normalize(value));return true;}catch{return false;}}
 const model=Object.freeze({KEY,choices,normalize,read,save});
 if(typeof module==='object'&&module.exports)module.exports=model;
 if(!root.document)return;
 root.ReaderFonts=model;
 const document=root.document,appearance=document.querySelector('#appearance-settings .appearance');
 if(!appearance||document.getElementById('reading-font'))return;
 const label=document.createElement('label');label.textContent='Reading font';label.htmlFor='reading-font';
 const select=document.createElement('select');select.id='reading-font';select.setAttribute('aria-describedby','reading-font-help reading-font-status');
 for(const choice of choices){const option=document.createElement('option');option.value=choice.id;option.textContent=choice.label;select.append(option);}
 label.append(select);appearance.append(label);
 const panel=document.createElement('section');panel.id='reading-font-preview';panel.setAttribute('aria-label','Reading font preview');
 const help=document.createElement('p');help.id='reading-font-help';help.className='notice';help.textContent='Fonts use your device’s installed typefaces. Missing fonts and characters use script-specific fallbacks. No font download is required. Original spelling, accents and transliteration are unchanged.';
 panel.append(help);
 for(const [lang,dir,text] of [['en','ltr','Faith, hope and love — Å ä ö'],['hi','ltr','हिन्दी • தமிழ் • ಕನ್ನಡ • മലയാളം'],['he','rtl','בְּרֵאשִׁית • ܒܪܫܝܬ • اُردُو'],['el','ltr','Ἐν ἀρχῇ • 日本語']]){const p=document.createElement('p');p.lang=lang;p.dir=dir;p.className='font-sample';p.textContent=text;panel.append(p);}
 const status=document.createElement('p');status.id='reading-font-status';status.className='notice';status.setAttribute('role','status');panel.append(status);appearance.after(panel);
 function storage(){try{return root.localStorage;}catch{return null;}}
 function apply(value){const id=normalize(value),choice=choices.find(c=>c.id===id);select.value=id;document.documentElement.dataset.readerFont=id;if(choice.stack)document.documentElement.style.setProperty('--reading-font-family',choice.stack);else document.documentElement.style.removeProperty('--reading-font-family');}
 apply(read(storage()));
 select.addEventListener('change',()=>{apply(select.value);status.textContent=save(storage(),select.value)?'Reading font saved on this device.':'Font applied for this visit. Your browser could not save the preference.';});
 root.addEventListener('storage',event=>{if(event.key===KEY||event.key===null){apply(read(storage()));status.textContent='Reading font updated from this device’s settings.';}});
})(typeof window==='object'?window:globalThis);
