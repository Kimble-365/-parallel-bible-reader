/* Source-qualified Syriac packs. English source glosses; no generated readings. */
'use strict';
window.ReaderSyriac=(()=>{
 const pending=new Map(),memory=new Map(),M=window.SyriacPacks;
 async function verified(path,meta,{signal}={}){
  if(!meta)throw Error('This source is not included.');
  if(memory.has(path))return memory.get(path);
  if(!signal&&pending.has(path))return pending.get(path);
  const request=(async()=>{
   let response;try{response=await fetch(path,{signal,cache:'no-store'})}catch(e){if(e.name==='AbortError')throw e;throw Error('Syriac source is unavailable. Connect to load it or save the reading text first.');}
   if(!response.ok)throw Error('Syriac source download failed (HTTP '+response.status+').');
   const bytes=new Uint8Array(await response.arrayBuffer());
   if(bytes.length!==meta.packed_bytes)throw Error('Incomplete Syriac pack.');
   const raw=await ReaderCompression.unpack(bytes,meta.bytes,16*1024*1024);
   const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(n=>n.toString(16).padStart(2,'0')).join('');
   if(raw.length!==meta.bytes||hash!==meta.sha256)throw Error('Syriac source checksum mismatch.');
   const data=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));
   memory.set(path,data);while(memory.size>8)memory.delete(memory.keys().next().value);return data;
  })();
  if(!signal)pending.set(path,request);
  try{return await request}finally{if(!signal)pending.delete(path)}
 }
 function meta(edition,book){if(!/^[A-Z0-9]{3}$/.test(book)||!M.editions[edition]?.books[book])throw Error('This book is not in this Syriac edition.');return M.editions[edition].books[book]}
 async function loadText(edition,book,options){const data=await verified('../v1.25/syriac-data/'+edition+'/'+book+'.json.gz',meta(edition,book).text,options);if(data.book!==book||!Array.isArray(data.editions?.[edition]))throw Error('Syriac edition mismatch.');return data}
 async function loadIndex(edition,book,options){const info=meta(edition,book);if(info.index_in_text){const data=await loadText(edition,book,options);return {book,edition,verses:data.source}}const data=await verified('../v1.25/syriac-index/'+edition+'/'+book+'.json.gz',info.index,options);if(data.book!==book||data.edition!==edition)throw Error('Syriac analysis mismatch.');return data}
 async function entry(id,options){if(!/^etcbc:[a-f0-9]{24}$/.test(id))throw Error('Unknown lexeme ID.');const prefix=id.split(':')[1][0],data=await verified('../v1.25/syriac-lexicon/'+prefix+'.json.gz',M.lexicon[prefix],options);const item=data.entries?.[id];if(!Array.isArray(item)||item.length!==2)throw Error('Lexical entry is missing.');return {id,lemma:item[0],gloss:item[1]}}
 return {loadText,loadIndex,entry};
})();
