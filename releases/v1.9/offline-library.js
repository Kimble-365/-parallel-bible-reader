/* Selected-text IndexedDB store; source bundles are parsed as JSON, never evaluated. */
'use strict';
window.ReaderOffline=(()=>{
 const C=window.BibleCatalog,editions=new Map(C.editions.map(e=>[e.id,e]));
 const baseIds=new Set(['hin2017','pan','bgc','urd','dgo','xnr','kfs','mjl','bfz','bhd','fin-kr1938','engwebp','benirv','bfz-mahasui','cdh','gbk','guj2017','kanirv','kfx','kfx-outer','mal','mar','npiulb','ory','tam2017','tel2017','urdoucv']);
 const revision=C.version,dbName='parallel-bible-reader-offline-1.9';let dbPromise;
 const pending=new Map(),memory=new Map();
 function database(){if(!dbPromise)dbPromise=new Promise((resolve,reject)=>{const request=indexedDB.open(dbName,1);request.onupgradeneeded=()=>{request.result.createObjectStore('texts');request.result.createObjectStore('metadata')};request.onsuccess=()=>{request.result.onversionchange=()=>{request.result.close();dbPromise=null};resolve(request.result)};request.onerror=()=>reject(request.error);request.onblocked=()=>reject(Error('Close other reader tabs and try again.'))}).catch(e=>{dbPromise=null;throw e});return dbPromise}
 const key=(id,book)=>revision+'|'+id+'|'+book;
 async function get(id,book){const db=await database();return new Promise((resolve,reject)=>{const r=db.transaction('texts').objectStore('texts').get(key(id,book));r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)})}
 async function list(){const db=await database();return new Promise((resolve,reject)=>{const r=db.transaction('metadata').objectStore('metadata').getAll();r.onsuccess=()=>resolve(r.result.filter(x=>x.revision===revision));r.onerror=()=>reject(r.error)})}
 async function put(id,book,rows){const db=await database(),bytes=new Blob([JSON.stringify(rows)]).size;return new Promise((resolve,reject)=>{const tx=db.transaction(['texts','metadata'],'readwrite');tx.objectStore('texts').put(rows,key(id,book));tx.objectStore('metadata').put({id,book,revision,bytes,verses:rows.length},key(id,book));tx.oncomplete=()=>resolve();tx.onabort=()=>reject(tx.error||Error('Saving was interrupted.'));tx.onerror=()=>{}})}
 function validate(data,book){if(!data||typeof data!=='object'||(data.book&&data.book!==book)||!data.editions||typeof data.editions!=='object')throw Error('Unexpected book data for '+book);return data}
 function parseBundle(text,book){const marker=/window\.(?:ExtraBibleBooks|BibleBooks)\["([A-Z0-9]{3})"\]\s*=\s*/g;const m=marker.exec(text);if(!m||m[1]!==book)throw Error('Unexpected source bundle for '+book);return validate(JSON.parse(text.slice(marker.lastIndex).trim().replace(/;\s*$/,'')),book)}
 async function bundle(book,extra,signal){const url=new URL((extra?'../v1.8/extra-data/':document.documentElement.dataset.dataPath||'../../data/')+book+'.js?v='+encodeURIComponent(revision),location.href).href;
  if(!signal&&pending.has(url))return pending.get(url);
  const request=(async()=>{let response;try{response=await fetch(url,{signal,cache:'no-store'})}catch(e){if(e.name==='AbortError')throw e;throw Error('Could not download '+book+'. Check your connection or save this text before going offline.')} if(!response.ok)throw Error('Could not download '+book+' (HTTP '+response.status+').');return parseBundle(await response.text(),book)})();if(!signal)pending.set(url,request);try{return await request}finally{if(!signal)pending.delete(url)}}
 async function loadBook(book,ids,{signal,forceOnline=false}={}){
  ids=[...new Set(ids)].filter(id=>editions.get(id)?.book_codes.includes(book));const result={book,editions:{}};if(!ids.length)return result;
  const missing=[];
  for(const id of ids){const k=key(id,book);let rows;try{rows=await get(id,book)}catch{}if(!rows&&memory.has(k))rows=memory.get(k);if(rows)result.editions[id]=rows;else missing.push(id)}
  if(missing.length){if(navigator.onLine===false)throw Error(book+' is not saved for every selected text. Reconnect and use Save selected texts.');
   const groups=[false,true].filter(extra=>missing.some(id=>!baseIds.has(id)===extra));
   for(const extra of groups){const data=await bundle(book,extra,signal);for(const id of missing.filter(id=>!baseIds.has(id)===extra)){const rows=data.editions[id];if(!Array.isArray(rows)||!rows.length||!rows.every(r=>Array.isArray(r)&&r.length>=3&&['number','string'].includes(typeof r[0])&&['number','string'].includes(typeof r[1])&&typeof r[2]==='string'))throw Error('Incomplete text data: '+id+' / '+book);const chapters=new Set(rows.map(r=>r[0]));if(!editions.get(id).positions.filter(p=>p[0]===book).every(p=>chapters.has(p[1])))throw Error('Incomplete chapters: '+id+' / '+book);result.editions[id]=rows;if(!forceOnline){memory.set(key(id,book),rows);while(memory.size>8)memory.delete(memory.keys().next().value)}}}
  }return result;
 }
 async function download(ids,onProgress,signal){ids=[...new Set(ids)].filter(id=>editions.has(id));if(!ids.length)throw Error('Choose at least one text above.');await database();const jobs=C.books.map(([book])=>({book,ids:ids.filter(id=>editions.get(id).book_codes.includes(book))})).filter(x=>x.ids.length);let done=0;
  for(const job of jobs){if(signal?.aborted)throw new DOMException('Stopped','AbortError');const data=await loadBook(job.book,job.ids,{signal,forceOnline:true});for(const id of job.ids){if(signal?.aborted)throw new DOMException('Stopped','AbortError');await put(id,job.book,data.editions[id])}onProgress?.({done:++done,total:jobs.length,book:job.book})}
 }
 async function remove(id){const entries=await list(),db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction(['texts','metadata'],'readwrite');for(const item of entries.filter(x=>x.id===id)){const k=key(id,item.book);tx.objectStore('texts').delete(k);tx.objectStore('metadata').delete(k);memory.delete(k)}tx.oncomplete=resolve;tx.onabort=()=>reject(tx.error)})}
 return {loadBook,download,list,remove,dbName};
})();
