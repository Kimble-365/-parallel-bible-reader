/* Exercise real UI handlers with a minimal DOM; this is not a browser compatibility test. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
class Element{
 constructor(tag='div'){this.tagName=tag;this.children=[];this.value='';this.textContent='';this.hidden=false;this.disabled=false;this.files=[];this.attributes={};this.classList={toggle(){}}}
 append(...xs){this.children.push(...xs)}replaceChildren(...xs){this.children=xs}setAttribute(k,v){this.attributes[k]=v}focus(){}scrollIntoView(){}click(){return this.onclick?.()}
}
function setup(storage,source){const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)},downloads=[];get('notes-panel').hidden=true;const context=vm.createContext({window:null,TextEncoder,Date,Math,JSON,Blob,console,confirm:()=>true,localStorage:storage,ReaderNotebookSource:source,document:{getElementById:get,createElement:tag=>new Element(tag)},URL:{createObjectURL(blob){downloads.push(blob);return 'blob:test'},revokeObjectURL(){}},setTimeout:fn=>{fn();return 1}});context.window=context;for(const file of ['notes-model.js','notes-ui.js'])vm.runInContext(fs.readFileSync('releases/v1.13/'+file,'utf8'),context);return {get,context,downloads}}
const tick=()=>new Promise(r=>setImmediate(r));
(async()=>{
 const data=new Map(),storage={getItem:k=>data.get(k)??null,setItem:(k,v)=>data.set(k,v)};let id='edition-one',calls=[];
 const source={label:()=>id,reference:()=>'JHN 3:16',async passage(input,mode){calls.push({id,input,mode});return {reference:input||'John 3:16',edition:id,editionId:id,text:'Original passage from '+id,language:'en',direction:'ltr'}}};
 let ui=setup(storage,source),$=ui.get;await $('notes-open').click();await tick();assert.equal($('notes-panel').hidden,false);assert.equal($('notes-quotes').children.length,1);assert.ok($('notes-quotes').children[0].children[1].textContent.includes('edition-one'));assert.equal(calls[0].mode,'current');
 $('notes-title').value='My first note';$('notes-title').oninput();$('notes-body').value='Keep my personal observations';$('notes-body').oninput();assert.ok(storage.getItem('parallel-reader-notes-v1').includes('Keep my personal observations'));
 // Source changes add a separately attributed quotation without replacing the first.
 id='edition-two';$('notes-reference').value='GEN 1:1-3';await $('notes-insert').click();assert.equal($('notes-quotes').children.length,2);assert.ok($('notes-quotes').children[0].children[0].textContent.includes('edition-one'));assert.ok($('notes-quotes').children[1].children[0].textContent.includes('edition-two'));assert.equal($('notes-body').value,'Keep my personal observations');
 // Removal after editing uses the current note, not a stale pre-save object.
 $('notes-quotes').children[0].children[2].click();assert.equal($('notes-quotes').children.length,1);assert.ok($('notes-quotes').children[0].children[0].textContent.includes('edition-two'));
 await $('notes-insert').click();assert.equal($('notes-quotes').children.length,1);assert.match($('notes-status').textContent,/already/);
 $('notes-export-text').click();assert.match(await ui.downloads.at(-1).text(),/Keep my personal observations/);$('notes-export').click();const backup=await ui.downloads.at(-1).text();assert.equal(JSON.parse(backup).notes.length,1);
 // Reopening retains edited content and never silently imports a new current verse.
 ui=setup(storage,source);$=ui.get;$('notes-open').click();assert.equal($('notes-body').value,'Keep my personal observations');assert.equal($('notes-quotes').children.length,1);
 $('notes-file').files=[{size:backup.length,text:async()=>backup}];await $('notes-import').click();assert.equal(JSON.parse(storage.getItem('parallel-reader-notes-v1')).length,2);assert.equal(new Set(JSON.parse(storage.getItem('parallel-reader-notes-v1')).map(n=>n.id)).size,2);
 await $('notes-new').click();assert.equal(JSON.parse(storage.getItem('parallel-reader-notes-v1')).length,3);assert.equal($('notes-body').value,'');
 // A full browser store must retain the draft and prevent closing with silent data loss.
 storage.setItem=()=>{throw Error('quota')};$('notes-body').value='Unsaved draft';$('notes-body').oninput();assert.match($('notes-status').textContent,/Not saved/);$('notes-close').click();assert.equal($('notes-panel').hidden,false);assert.equal($('notes-body').value,'Unsaved draft');$('notes-export-text').click();assert.match(await ui.downloads.at(-1).text(),/Unsaved draft/);
 const broken={getItem:()=>'{broken',setItem(){throw Error('must not overwrite')}};const bad=setup(broken,source);bad.get('notes-open').click();assert.equal(bad.get('notes-new').disabled,true);assert.match(bad.get('notes-status').textContent,/could not be read/);
 console.log('PASS: real notes UI handlers, automatic Text 1 quotation, edits, source-change attribution, removal after edit, duplicate protection, text/JSON exports, reload, additive import, new notes and storage-failure draft protection (minimal DOM)');
})().catch(e=>{console.error(e);process.exitCode=1});
