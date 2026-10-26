/* Content-validated per-book word indexes. Private-edition indexes stay in RAM. */
'use strict';
window.ReaderSearch=(()=>{
 const SCHEMA='word-search-1.13-r1',BUDGET=32*1024*1024,cache=new Map();let used=0,dbPromise,blocked=false;
 const metrics={built:0,memoryHits:0,persistentHits:0,persisted:0};
 function aborted(signal){if(signal?.aborted)throw new DOMException('Stopped','AbortError')}
 function normalize(text,policy='preserve',exact=false){let s=String(text).normalize('NFC').toLowerCase().replace(/ς/g,'σ').replace(/[’‘ʼ]/g,"'").replace(/[\u2010-\u2015\u2212]/g,'-').replace(/\s+/gu,' ');
  if(!exact){if(policy==='hebrew')s=s.replace(/[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]/g,'');else if(policy==='arabic')s=s.replace(/[\u0610-\u061a\u0640\u064b-\u0652\u0670\u06d6-\u06ed]/g,'');else if(policy==='greek'||policy==='latin')s=s.normalize('NFD').replace(/\p{M}/gu,'').normalize('NFC')}
  return s.trim();
 }
 const words=s=>s.match(/[\p{L}\p{M}\p{N}\u200c\u200d]+/gu)||[];
 const continuous=s=>/[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Thai}\p{Script=Lao}\p{Script=Khmer}\p{Script=Myanmar}]/u.test(s);
 function boundary(s,index,length,q){if(continuous(q))return true;const letter=c=>!!c&&/[\p{L}\p{M}\p{N}\u200c\u200d]/u.test(c),first=[...q][0],last=[...q].at(-1),before=[...s.slice(0,index)].at(-1),after=[...s.slice(index+length)][0];return (!letter(first)||!letter(before))&&(!letter(last)||!letter(after))}
 function phrase(s,q){if(!q)return false;for(let i=s.indexOf(q);i>=0;i=s.indexOf(q,i+1))if(boundary(s,i,q.length,q))return true;return false}
 async function database(){if(blocked||!('indexedDB'in window))return null;if(!dbPromise)dbPromise=new Promise((resolve,reject)=>{const r=indexedDB.open('parallel-bible-reader-search-index',1);r.onupgradeneeded=()=>r.result.createObjectStore('indexes');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.onblocked=()=>reject(Error('Search cache blocked'))}).catch(()=>{blocked=true;return null});return dbPromise}
 async function read(key){try{const db=await database();if(!db)return null;return await new Promise((resolve,reject)=>{const r=db.transaction('indexes').objectStore('indexes').get(key);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)})}catch{return null}}
 async function write(key,value){try{const db=await database();if(!db)return;await new Promise((resolve,reject)=>{const t=db.transaction('indexes','readwrite');t.objectStore('indexes').put(value,key);t.oncomplete=resolve;t.onabort=()=>reject(t.error);t.onerror=()=>{}});metrics.persisted++}catch{/* Cache failure must never prevent a search. */}}
 function remember(key,index){if(cache.has(key)){used-=cache.get(key).bytes;cache.delete(key)}if(index.bytes>BUDGET)return;while(used+index.bytes>BUDGET&&cache.size){const first=cache.keys().next().value;used-=cache.get(first).bytes;cache.delete(first)}cache.set(key,index);used+=index.bytes}
 async function fingerprint(rows){const bytes=new TextEncoder().encode(JSON.stringify(rows));if(globalThis.crypto?.subtle){const digest=await crypto.subtle.digest('SHA-256',bytes);return [...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('')}return null}
 async function cached({key,expectedHash,exact=false,signal}){if(!expectedHash)return null;aborted(signal);const k=SCHEMA+'|'+key+'|'+exact,old=cache.get(k);if(old?.hash===expectedHash){metrics.memoryHits++;remember(k,old);return old}const saved=await read(k);aborted(signal);if(saved?.schema===SCHEMA&&saved.hash===expectedHash&&saved.groups instanceof Map&&[...saved.groups.values()].every(g=>Array.isArray(g.docs)&&g.postings instanceof Map)){metrics.persistentHits++;remember(k,saved);return saved}return null}
 async function prepare({key,edition,rows,forms,exact=false,persist=true,signal}){aborted(signal);const hash=await fingerprint(rows);aborted(signal);const k=SCHEMA+'|'+key+'|'+exact,old=cache.get(k);if(hash&&old?.hash===hash){metrics.memoryHits++;remember(k,old);return old}
  if(hash&&persist){const saved=await read(k);aborted(signal);if(saved?.schema===SCHEMA&&saved.hash===hash&&saved.groups instanceof Map&&[...saved.groups.values()].every(g=>Array.isArray(g.docs)&&g.postings instanceof Map)){metrics.persistentHits++;remember(k,saved);return saved}}
  const groups=new Map();let bytes=0;
  for(let r=0;r<rows.length;r++){if(r%128===0){aborted(signal);await new Promise(resolve=>setTimeout(resolve,0))}const row=rows[r];for(const form of forms(row)){if(!form.text)continue;const policy=form.policy||'preserve';if(!groups.has(policy))groups.set(policy,{docs:[],postings:new Map()});const group=groups.get(policy),normalized=normalize(form.text,policy,exact),n=group.docs.length;group.docs.push({chapter:row[0],verse:row[1],name:form.name,text:form.text,normalized});bytes+=(normalized.length+form.text.length)*2+128;for(const word of new Set(words(normalized))){if(!group.postings.has(word)){group.postings.set(word,[]);bytes+=word.length*2+96}group.postings.get(word).push(n);bytes+=8}}}
  const index={schema:SCHEMA,edition,hash,groups,bytes};metrics.built++;aborted(signal);remember(k,index);if(hash&&persist)await write(k,index);aborted(signal);return index;
 }
 function matches(index,query,mode='words',exact=false){const found=[];
  for(const [policy,group]of index.groups){const q=normalize(query,policy,exact);if(!q)continue;const terms=[...new Set(words(q))];let candidates;
   if(mode==='words'){if(!terms.length)continue;const indexed=terms.filter(t=>!continuous(t)),lists=indexed.map(t=>group.postings.get(t)||[]).sort((a,b)=>a.length-b.length);if(lists.length){if(!lists[0].length)continue;const rest=lists.slice(1).map(l=>new Set(l));candidates=lists[0].filter(n=>rest.every(s=>s.has(n)))}else candidates=group.docs.map((_,n)=>n);const fragments=terms.filter(continuous);for(const n of candidates){const d=group.docs[n];if(fragments.every(t=>d.normalized.includes(t)))found.push(d)}}
   else{for(const d of group.docs)if(mode==='contains'?d.normalized.includes(q):phrase(d.normalized,q))found.push(d)}
  }return found;
 }
 async function clearAll(){cache.clear();used=0;try{const db=await database();if(!db)return false;await new Promise((resolve,reject)=>{const t=db.transaction('indexes','readwrite');t.objectStore('indexes').clear();t.oncomplete=resolve;t.onabort=()=>reject(t.error)});return true}catch{return false}}
 async function invalidateEdition(id){for(const [key,index]of cache)if(index.edition===id){used-=index.bytes;cache.delete(key)}try{const db=await database();if(!db)return;await new Promise((resolve,reject)=>{const t=db.transaction('indexes','readwrite'),r=t.objectStore('indexes').openCursor();r.onsuccess=()=>{const c=r.result;if(c){if(c.value.edition===id)c.delete();c.continue()}};t.oncomplete=resolve;t.onabort=()=>reject(t.error)})}catch{}}
 return {prepare,cached,matches,normalize,clearAll,invalidateEdition,metrics,clearMemory(){cache.clear();used=0}};
})();
