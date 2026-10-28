'use strict';
window.ReaderJapaneseRuby=(()=>{
 const CACHE='parallel-reader-japanese-ruby-1.19',memory=new Map();
 function selected(){return document.getElementById('ruby-readings')?.checked&&['primary','compare1','compare2','compare3'].some(id=>document.getElementById(id)?.value==='jpn-bungo')}
 function url(book){return new URL('ruby-data/'+book+'.json.gz?sha='+ReaderRubyManifest.books[book].sha256,location.href).href}
 async function load(book,{signal,requireSaved=false}={}){
  if(memory.has(book)&&!requireSaved)return memory.get(book);const expected=ReaderRubyManifest.books[book];if(!expected)throw Error('No kana reading pack for this book.');
  let cache=null,response;try{cache=await caches.open(CACHE);response=await cache.match(url(book))}catch{}
  if(!response){response=await fetch(url(book),{signal});if(!response.ok)throw Error('Kana readings are not available offline for this book.')}const copy=response.clone(),bytes=await ReaderCompression.unpack(new Uint8Array(await response.arrayBuffer()),expected.bytes,16*1024*1024);
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');if(bytes.length!==expected.bytes||hash!==expected.sha256)throw Error('Kana reading checksum mismatch.');
  const data=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));if(data.book!==book||data.source_hash!==ReaderSearchManifest.editions['jpn-bungo'][book]||data.source_hash!==expected.source_hash||data.rows.length!==expected.rows)throw Error('Kana readings do not match this source.');const map=new Map(data.rows.map(row=>[row[0]+':'+row[1],row[2]]));
  try{if(cache)await cache.put(url(book),copy);else if(requireSaved)throw Error('Kana offline storage is unavailable.')}catch(e){if(requireSaved)throw e}memory.set(book,map);return map;
 }
 function annotate(node,book,row){const tokens=memory.get(book)?.get(row[0]+':'+row[1]);if(!tokens||tokens.map(t=>t[0]).join('')!==row[2])return false;for(const [original,kana]of tokens){if(/[\u3400-\u9fff]/.test(original)&&/^[\u3040-\u309f\u30fc\s]+$/.test(kana)&&kana!==original){const ruby=document.createElement('ruby'),rt=document.createElement('rt');ruby.append(document.createTextNode(original));rt.textContent=kana;rt.setAttribute('aria-hidden','true');ruby.append(rt);node.append(ruby)}else node.append(document.createTextNode(original))}return true}
 async function downloadAll(progress,signal){let done=0;const books=Object.keys(ReaderRubyManifest.books);for(const book of books){if(signal?.aborted)throw new DOMException('Stopped','AbortError');await load(book,{signal,requireSaved:true});progress?.({book,done:++done,total:books.length})}}
 async function remove(){memory.clear();if(typeof caches!=='undefined')await caches.delete(CACHE)}
 return {load,annotate,selected,downloadAll,remove,has:book=>memory.has(book),text:(book,row)=>memory.get(book)?.get(row[0]+':'+row[1])?.map(t=>t[1]).join('')||'',revision:ReaderRubyManifest.revision};
})();
