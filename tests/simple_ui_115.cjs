/* Actual menu handlers against a small DOM fixture; not a browser/layout test. */
'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const ids=new Map(),events={};
class E{
 constructor(tag='div',id=''){this.tagName=tag.toUpperCase();this.children=[];this.attributes={};this.value='';this.textContent='';this.open=false;this.handlers={};if(id){this.id=id;ids.set(id,this)}}
 append(...nodes){for(const n of nodes){n.parent?.removeChild(n);this.children.push(n);n.parent=this}}
 prepend(...nodes){for(const n of [...nodes].reverse()){n.parent?.removeChild(n);this.children.unshift(n);n.parent=this}}
 before(n){if(!this.parent)return;const p=this.parent;n.parent?.removeChild(n);p.children.splice(p.children.indexOf(this),0,n);n.parent=p}
 removeChild(n){this.children.splice(this.children.indexOf(n),1);n.parent=null}
 replaceChildren(...nodes){for(const c of this.children)c.parent=null;this.children=[];this.append(...nodes)}
 setAttribute(k,v){this.attributes[k]=v}focus(){this.focused=true}scrollIntoView(){}showModal(){this.open=true}close(){this.open=false}click(){this.onclick?.()}
 get options(){return this.children.flatMap(c=>c.tagName==='OPTGROUP'?c.children:[c])}
 matches(sel){return sel.split(',').some(s=>s==='aside'&&this.tagName==='ASIDE'||s==='footer'&&this.tagName==='FOOTER'||s==='details.reader-extras'&&this.tagName==='DETAILS')}
 querySelector(sel){if(this.tagName==='HEADER')return sel.startsWith('nav')?chapter:selectors;return this.children[0]||null}
 addEventListener(k,fn){this.handlers[k]=fn}dispatchEvent(e){this.lastEvent=e}
}
const body=new E('body'),header=new E('header'),chapter=new E('nav'),selectors=new E('div'),aside=new E('aside'),extra=new E('details','offline-panel'),footer=new E('footer'),main=new E('main');body.append(header,aside,extra,main,footer);header.append(selectors,chapter);main.append(new E('details','book-intro'));
for(const id of ['font-smaller','font-size','font-larger','reading-mode','notes-open','text-display','primary','browse-0','search-panel','audio-panel','film-panel']){const e=new E('div',id);header.append(e)}
ids.get('text-display').append(...['both','original','latin'].map(value=>{const o=new E('option');o.value=value;return o}));const primary=ids.get('primary');primary.value='current';ids.get('browse-0').href='translations/?edition=current#JHN.3.16';let noteClicks=0;ids.get('notes-open').onclick=()=>noteClicks++;
const storage=new Map([['bible-reader-favorites-v1','["favorite"]']]);const context={document:{body,getElementById:id=>ids.get(id)||body.children.flatMap(x=>[x,...x.children]).find(x=>x.id===id),createElement:t=>new E(t),querySelector:()=>header,addEventListener:(name,fn)=>events[name]=fn},localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},BibleCatalog:{editions:[{id:'current',label:'Current'},{id:'favorite',label:'Favorite'},{id:'other',label:'Other'}]},MutationObserver:class{observe(){}},Event:class{constructor(type,opts){this.type=type;this.bubbles=opts?.bubbles}}};
vm.runInNewContext(fs.readFileSync('releases/v1.15/simple-ui.js','utf8'),context);
const bar=body.children[0],nav=body.children[1],dialog=body.children.find(x=>x.id==='reader-settings'),quick=bar.children[1].children[0];assert.equal(nav,chapter);assert.ok(dialog.children.includes(header));assert.equal(extra.parent.id,'additional-tools');assert.equal(footer.parent,extra.parent);assert.equal(ids.get('book-intro').parent,extra.parent);assert.equal(dialog.open,false);assert.deepEqual(quick.options.map(x=>x.value),['current','favorite']);assert.equal(quick.value,'current');assert.ok(!quick.options.some(x=>x.value==='other'));
bar.children.find(x=>x.textContent==='Settings').click();assert.equal(dialog.open,true);dialog.children.find(x=>x.textContent==='Back to reading').click();assert.equal(dialog.open,false);bar.children.find(x=>x.textContent==='Search').click();assert.equal(ids.get('search-panel').open,false); // fixture target is a DIV; no accidental DETAILS state
assert.equal(dialog.open,true);quick.value='favorite';quick.onchange();assert.equal(primary.value,'favorite');assert.equal(primary.lastEvent.type,'change');assert.ok(primary.lastEvent.bubbles);bar.children.find(x=>x.textContent==='Notes').click();assert.equal(noteClicks,1);assert.equal(storage.get('bible-reader-simple-ui-115'),'true');assert.equal(bar.children.find(x=>x.textContent==='Languages').href,ids.get('browse-0').href);assert.equal(ids.get('text-display').options[0].textContent,'Text + transliteration');
console.log('PASS: actual menu handlers move all controls into settings; closed by default; open/close, favorite-only/current options, primary change event, language link context, notes action, persistent migration flag and display labels (DOM fixture)');
