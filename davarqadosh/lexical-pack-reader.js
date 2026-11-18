'use strict';
/* WLEXPACK/1: verified book-at-a-time ZIP + read-only SQLite. No SQL/eval. */
window.LexicalPackReader=(()=>{
 const MAX_PACK=32*1024*1024,MAX_DB=128*1024*1024,CACHE='davarqadosh-verified-packs-v1',MAX_CACHE=64*1024*1024;
 const decode=b=>new TextDecoder('utf-8',{fatal:true}).decode(b);
 const hash=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),v=>v.toString(16).padStart(2,'0')).join('');
 async function boundedResponse(response,max){
  if(!response.ok)throw Error('Download failed (HTTP '+response.status+'). Try again online or open a saved book.');
  const reader=response.body.getReader(),parts=[];let size=0;
  try{for(;;){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>max)throw Error('Download exceeds the book size limit.');parts.push(value)}}catch(e){await reader.cancel().catch(()=>{});throw e}
  const out=new Uint8Array(size);let at=0;for(const p of parts){out.set(p,at);at+=p.length}return out;
 }
 function inflate(bytes,length,max,raw=true){
  if(!Number.isSafeInteger(length)||length<0||length>max)throw Error('Unsupported expanded size.');
  const parts=[];let size=0;const d=new pako.Inflate({raw,chunkSize:65536});
  d.onData=part=>{size+=part.length;if(size>length||size>max)throw Error('Expanded book exceeds its declared limit.');parts.push(part)};
  d.push(bytes,true);if(d.err||!d.ended||size!==length)throw Error('Incomplete compressed book.');
  const out=new Uint8Array(size);let at=0;for(const p of parts){out.set(p,at);at+=p.length}return out;
 }
 function validateManifest(m){
  if(m?.format!=='wlexpack'||m.version!==1||m.schema_version!==1||m.payload!=='book.sqlite'||m.codec!=='deflate')throw Error('Unsupported lexical pack version. Rebuild with schema 1.');
  for(const [field,max] of [['packed_bytes',MAX_PACK],['sqlite_bytes',MAX_DB]])if(!Number.isSafeInteger(m[field])||m[field]<=0||m[field]>max)throw Error('Invalid pack length.');
  for(const field of ['packed_sha256','sqlite_sha256','source_sha256'])if(!/^[a-f0-9]{64}$/.test(m[field]))throw Error('Invalid pack hash.');
  if(!/^[A-Z0-9]{3}$/.test(m.book))throw Error('Invalid book code.');return m;
 }
 async function open(bytes,manifest){
  const m=validateManifest(manifest);if(bytes.length!==m.packed_bytes||await hash(bytes)!==m.packed_sha256)throw Error('Lexical pack checksum mismatch. The existing saved book has not been replaced.');
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength),entries=new Map();let at=0;
  for(const wanted of ['manifest.json','book.sqlite']){
   if(at+30>bytes.length||view.getUint32(at,true)!==0x04034b50)throw Error('Invalid ZIP book header.');
   const flags=view.getUint16(at+6,true),codec=view.getUint16(at+8,true),packed=view.getUint32(at+18,true),length=view.getUint32(at+22,true),names=view.getUint16(at+26,true),extra=view.getUint16(at+28,true),start=at+30+names+extra,end=start+packed;
   if(flags&9||end>bytes.length||decode(bytes.subarray(at+30,at+30+names))!==wanted)throw Error('Unsupported ZIP entry.');
   const cap=wanted==='manifest.json'?65536:MAX_DB;
   if(length>cap||![0,8].includes(codec)||(wanted==='book.sqlite'&&length!==m.sqlite_bytes))throw Error('Invalid ZIP entry size or codec.');
   const data=bytes.subarray(start,end);entries.set(wanted,codec===8?inflate(data,length,cap):data);
   if(entries.get(wanted).length!==length)throw Error('ZIP entry length mismatch.');at=end;
  }
  if(at+4>bytes.length||view.getUint32(at,true)!==0x02014b50)throw Error('Missing ZIP directory.');
  const embedded=JSON.parse(decode(entries.get('manifest.json')));
  for(const [key,value]of Object.entries(embedded))if(JSON.stringify(m[key])!==JSON.stringify(value))throw Error('Embedded manifest differs from discovery metadata.');
  const payload=entries.get('book.sqlite');if(await hash(payload)!==m.sqlite_sha256)throw Error('SQLite payload checksum mismatch.');
  const db=ReaderSQLite.open(payload);
  function rows(name){const table=db.read(name);return table.rows.map(row=>Object.fromEntries(table.columns.map((key,n)=>[key,row[n]])))}
  const meta=Object.fromEntries(rows('metadata').map(r=>[r.key,r.value]));
  if(meta.book!==m.book||meta.schema_version!=='1'||meta.source_sha256!==m.source_sha256)throw Error('SQLite identity mismatch.');
  const verses=rows('verses'),tokens=rows('tokens'),segments=rows('token_segments'),lemmas=rows('lemmas'),events=rows('display_events'),research=rows('research_records'),sources=rows('sources');
  if(tokens.length!==m.coverage.ingested||verses.length!==m.verses)throw Error('Book coverage mismatch.');
  const tokenMap=new Map(tokens.map(t=>[t.id,t])),lemmaMap=new Map(lemmas.map(l=>[l.id,l])),sourceMap=new Map(sources.map(s=>[s.id,s]));
  return {manifest:m,meta,verses,tokens,segments,lemmas,events,research,sources,tokenMap,lemmaMap,sourceMap};
 }
 function packURL(meta,base){const u=new URL(meta.url,base);if(u.origin!==location.origin)throw Error('Pack must be on this reader origin.');u.searchParams.set('sha256',meta.packed_sha256);return u.href}
 async function load(meta,base){
  const url=packURL(meta,base);let response=null;
  if('caches'in window)try{response=await(await caches.open(CACHE)).match(url)}catch{}
  if(!response)response=await fetch(url);
  const bytes=await boundedResponse(response,MAX_PACK);return {book:await open(bytes,meta),bytes,url};
 }
 async function save(loaded){
  await open(loaded.bytes,loaded.book.manifest);
  if(!('caches'in window))throw Error('Offline storage is unavailable in this browser.');
  if(navigator.storage?.estimate){const e=await navigator.storage.estimate();if(e.quota&&e.quota-(e.usage||0)<loaded.bytes.length*2)throw Error('Not enough offline space. Remove a saved book first.');}
  const cache=await caches.open(CACHE);const entries=await cache.keys();let size=loaded.bytes.length;
  for(const req of entries){if(req.url===loaded.url)continue;const r=await cache.match(req);size+=Number(r.headers.get('x-pack-bytes')||0)}
  for(const req of entries){if(size<=MAX_CACHE)break;if(req.url===loaded.url)continue;const r=await cache.match(req);await cache.delete(req);size-=Number(r.headers.get('x-pack-bytes')||0)}
  await cache.put(loaded.url,new Response(loaded.bytes,{headers:{'Content-Type':'application/octet-stream','x-pack-bytes':String(loaded.bytes.length)}}));
 }
 async function clear(){if('caches'in window)await caches.delete(CACHE)}
 async function companion(meta,base){
  if(!meta)return null;const url=new URL(meta.url,base);if(url.origin!==location.origin)throw Error('Invalid comparison origin.');
  let r;try{r=await(await caches.open(CACHE)).match(url.href)}catch{}
  if(!r)r=await fetch(url);const bytes=await boundedResponse(r,8*1024*1024);
  if(bytes.length!==meta.packed_bytes||await hash(bytes)!==meta.packed_sha256)throw Error('Comparison checksum mismatch.');
  const raw=inflate(bytes,meta.bytes,16*1024*1024,false);if(await hash(raw)!==meta.sha256)throw Error('Comparison payload mismatch.');
  return {data:JSON.parse(decode(raw)),bytes,url:url.href};
 }
 async function saveCompanion(c){if(c&&c.bytes.length<=8*1024*1024)await(await caches.open(CACHE)).put(c.url,new Response(c.bytes,{headers:{'x-pack-bytes':String(c.bytes.length)}}))}
 function researchFor(book,token){return book.research.filter(record=>record.verse_key===token.verse_key&&(record.token_id==null||record.token_id===token.id))}
 return {open,load,save,clear,companion,saveCompanion,hash,inflate,boundedResponse,validateManifest,researchFor,limits:{MAX_PACK,MAX_DB,MAX_CACHE}};
})();
