'use strict';
(()=>{
 const $=id=>document.getElementById(id),eds=BibleCatalog.editions.filter(e=>e.data_group==='syriac-1.23'),names=new Map(BibleCatalog.books);let generation=0;
 const option=(select,value,text)=>{const o=document.createElement('option');o.value=value;o.textContent=text;select.append(o)};
 eds.forEach(e=>option($('source-edition'),e.id,e.label));
 const query=new URLSearchParams(location.search);if(eds.some(e=>e.id===query.get('edition')))$('source-edition').value=query.get('edition');else $('source-edition').value='syc-etcbc-biblical';
 function books(){const e=eds.find(e=>e.id===$('source-edition').value);$('source-book').replaceChildren();e.book_codes.forEach(b=>option($('source-book'),b,names.get(b)||b));}
 books();if([...$('source-book').options].some(o=>o.value===query.get('book')))$('source-book').value=query.get('book');
 for(const [field,name]of [['chapter','source-chapter'],['verse','source-verse']])if(/^\d+$/.test(query.get(field)||''))$(name).value=query.get(field);
 async function render(event){event?.preventDefault();const run=++generation,id=$('source-edition').value,book=$('source-book').value,c=Number($('source-chapter').value),v=Number($('source-verse').value),e=eds.find(e=>e.id===id);
  $('source-status').textContent='Loading source…';$('source-text').textContent='';$('source-tokens').replaceChildren();$('lexical-result').textContent='Select a source segment to see its shared lexical entry and morphology.';$('source-note').hidden=true;$('source-locator').textContent='';$('source-credit').textContent='';
  try{
   const [text,index]=await Promise.all([ReaderSyriac.loadText(id,book),ReaderSyriac.loadIndex(id,book)]);if(run!==generation)return;
   const row=text.editions[id].find(r=>r[0]===c&&r[1]===v),info=index.verses[c+':'+v];if(!row||!info)throw Error('This reference is not included under this label in the source.');
   $('source-text').textContent=row[2];$('source-credit').textContent=e.attribution;$('source-locator').textContent=JSON.stringify({revision:SyriacPacks.editions[id].commit,node:info.node,source_book:info.source_book,slots:info.slots,source_path:info.source_path,xpath:info.xpath,source_units:info.source_units,no_surface_in_source:info.no_surface_in_source},null,2);
   const notes=[];if(info.slots?.length>1)notes.push('This source verse has discontinuous slot spans. Intervening source units are not part of this verse; this is not a manuscript lacuna.');if(info.no_surface_in_source?.length)notes.push('Some morphological segments have no surface string in the source. No letters have been supplied.');if(info.source_marker_only)notes.push('This source unit contains only source markers, not a readable word.');if(row[6])notes.push(row[6]);
   if(notes.length){$('source-note').textContent=notes.join(' ');$('source-note').hidden=false;}
   if(info.tokens){const chars=Array.from(row[2]);for(const token of info.tokens){const b=document.createElement('button');b.type='button';b.className='token';b.textContent=chars.slice(token[1],token[1]+token[2]).join('')||'∅';b.setAttribute('aria-label','Source segment '+token[0]);b.onclick=async()=>{try{const item=await ReaderSyriac.entry(token[3]);if(run!==generation)return;const fields=SyriacPacks.fields.slice(4).map((name,i)=>name+'='+token[i+4]).join('; ');$('lexical-result').textContent=item.lemma+' — '+item.gloss+'\n'+fields+'\n'+item.id+'; source segment '+token[0]+'. ETCBC source analysis; CC BY-NC 4.0.';}catch(error){if(run===generation)$('lexical-result').textContent=error.message}};$('source-tokens').append(b)}}
   else $('lexical-result').textContent='No word-level analysis is imported for this edition. The source text and locator remain available.';
   $('source-status').textContent=names.get(book)+' '+c+':'+v+' — '+(info.tokens?info.tokens.length+' source segments':'source text only');
  }catch(error){if(run===generation)$('source-status').textContent=error.message}
 }
 $('source-edition').addEventListener('change',()=>{books();generation++;$('source-text').textContent='';$('source-tokens').replaceChildren();$('source-status').textContent='Choose a reference and open the source passage.'});
 $('source-form').addEventListener('submit',render);render();
})();
