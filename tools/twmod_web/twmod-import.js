'use strict';
/* TWmod module import: a .twmod file is either a ZIP container holding
   module.sqlite (+ manifest.json) or a plain SQLite database. Both are read
   fully in memory — no temporary files are written, and the unpacked bytes
   are released when parsing finishes. */
window.ReaderTwmod=(()=>{
 const LIMIT=64*1024*1024;
 const table=Array.from({length:256},(_,n)=>{for(let k=0;k<8;k++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0});
 function crc(bytes){let n=0xffffffff;for(const byte of bytes)n=table[(n^byte)&255]^(n>>>8);return (n^0xffffffff)>>>0}
 function isPacked(bytes){return bytes.length>4&&bytes[0]===0x50&&bytes[1]===0x4b&&bytes[2]===3&&bytes[3]===4}
 function isSqlite(bytes){if(bytes.length<16)return false;const magic='SQLite format 3';for(let i=0;i<15;i++)if(bytes[i]!==magic.charCodeAt(i))return false;return bytes[15]===0}
 async function inflate(payload,size){
  if(typeof DecompressionStream==='function'){
   let reader;try{reader=new Blob([payload]).stream().pipeThrough(new DecompressionStream('deflate-raw')).getReader();const parts=[];let length=0;for(;;){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>size||length>LIMIT){try{await reader.cancel()}catch{}throw Error('Expanded module exceeds its allowed size.')}parts.push(value)}const out=new Uint8Array(length);let at=0;for(const part of parts){out.set(part,at);at+=part.length}return out}catch(error){try{await reader?.cancel()}catch{}if(/allowed size/.test(String(error?.message)))throw error/* engine failure: fall through to pako */}}
  if(!window.pako?.Inflate)throw Error('The local ZIP decoder could not load. Reload the reader while online.');
  const decoder=new window.pako.Inflate({raw:true,chunkSize:65536});const parts=[];let length=0,over=false;
  decoder.onData=chunk=>{length+=chunk.length;if(length>size||length>LIMIT){over=true;return}parts.push(chunk)};
  decoder.push(payload,true);if(over||decoder.err||!decoder.ended)throw Error('Expanded module exceeds its allowed size or is incomplete.');
  const out=new Uint8Array(length);let at=0;for(const part of parts){out.set(part,at);at+=part.length}return out;
 }
 function entry(bytes,name){
  const v=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  let e=-1;for(let p=bytes.length-22;p>=Math.max(0,bytes.length-65557);p--)if(v.getUint32(p,true)===0x06054b50){e=p;break}
  if(e<0)throw Error('Invalid packed module: no ZIP directory.');
  const count=v.getUint16(e+10,true);let p=v.getUint32(e+16,true);
  for(let i=0;i<count;i++){
   if(p+46>bytes.length||v.getUint32(p,true)!==0x02014b50)throw Error('Invalid ZIP central directory.');
   const flags=v.getUint16(p+8,true),method=v.getUint16(p+10,true),sum=v.getUint32(p+16,true),csize=v.getUint32(p+20,true),size=v.getUint32(p+24,true),nlen=v.getUint16(p+28,true),xlen=v.getUint16(p+30,true),comment=v.getUint16(p+32,true),local=v.getUint32(p+42,true);
   const entryName=new TextDecoder().decode(bytes.subarray(p+46,p+46+nlen));
   if(entryName===name){
    if((flags&1)||!size||size>LIMIT||csize>LIMIT||size===0xffffffff||csize===0xffffffff)throw Error('Encrypted, ZIP64 or oversized module content is not supported.');
    if(local+30>bytes.length||v.getUint32(local,true)!==0x04034b50)throw Error('Invalid ZIP entry.');
    const start=local+30+v.getUint16(local+26,true)+v.getUint16(local+28,true);
    if(start+csize>bytes.length)throw Error('Invalid ZIP entry length.');
    return {method,payload:bytes.slice(start,start+csize),size,sum};
   }
   p+=46+nlen+xlen+comment;
  }
  return null;
 }
 async function moduleBytes(bytes){
  if(isSqlite(bytes))return bytes;
  if(!isPacked(bytes))throw Error('A .twmod file must be a ZIP container or a plain SQLite database.');
  const found=entry(bytes,'module.sqlite');
  if(!found)throw Error('This packed module has no module.sqlite.');
  const out=found.method===0?found.payload:found.method===8?await inflate(found.payload,found.size):null;
  if(!out)throw Error('Unsupported ZIP compression in module.');
  if(out.length!==found.size||crc(out)!==found.sum)throw Error('The module archive is damaged (size or checksum mismatch).');
  if(!isSqlite(out))throw Error('module.sqlite is not a readable SQLite database.');
  return out;
 }
 function addRows(db,c){
  const names=db.tables.map(x=>x.toLowerCase());
  if(!names.includes('verses')||!names.includes('books'))throw Error('This module has no Bible books/verses tables; it is not a Bible TWmod.');
  const t=db.read('verses'),cols=t.columns.map(x=>x.toLowerCase());
  const bi=cols.indexOf('book'),ci=cols.indexOf('chapter'),di=cols.indexOf('display_verse'),ti=cols.indexOf('text'),si=cols.indexOf('sequence');
  if(bi<0||ci<0||di<0||ti<0)throw Error('Unsupported TWmod verses schema.');
  const groups=new Map();
  for(const row of t.rows){
   const book=String(row[bi]),display=String(row[di]),text=row[ti];
   if(typeof text!=='string')throw Error('Compressed/encrypted module entries cannot be read.');
   const m=display.match(/^(\d+)[-–](\d+)$/);
   let verse,end=null;
   if(m){verse=Number(m[1]);end=Number(m[2])}else verse=/^\d+$/.test(display)?Number(display):display;
   let g=groups.get(book);if(!g)groups.set(book,g=[]);
   g.push({seq:si>=0?Number(row[si]):0,chapter:row[ci],verse,text,end});
  }
  if(!groups.size)throw Error('The module has no verse rows.');
  for(const [book,rows]of groups){rows.sort((a,b)=>a.seq-b.seq);for(const r of rows)c.add(book,r.chapter,r.verse,r.text,null,r.end)}
 }
 async function add(bytes,c){addRows(ReaderSQLite.open(await moduleBytes(bytes)),c)}
 return {add,moduleBytes,isPacked,isSqlite};
})();
