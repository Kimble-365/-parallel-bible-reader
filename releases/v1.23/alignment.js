'use strict';
window.ReaderAlignment=(()=>{
 // Keys are source labels, never row offsets. Keep gaps and ranges explicit.
 const key=v=>/^\d+$/.test(String(v))?Number(v):v;
 function rows(id,input){
  if(id!=='fin-kr1938')return input;
  // Some source books move text across chapter boundaries. Without a verified
  // chapter map keep that entire book's source keys, rather than inventing one.
  if(input.some(row=>[...String(row[2]).matchAll(/\{(\d+):\d+[a-z]?\}/gi)].some(m=>Number(m[1])!==Number(row[0]))))return input;
  const out=[];for(const row of input){const parts=ReaderVerseText.segments(id,row,row[2]);for(const part of parts){const m=part.reference.match(/^(\d+):(\d+[a-z]?)$/i);if(!m){out.push(row);continue}const next=[Number(m[1]),key(m[2]),part.text,null,null];next.sourceVerse=row[1];out.push(next)}}return out;
 }
 function map(id,input,chapter){const out=new Map();for(const row of rows(id,input)){if(chapter!==undefined&&String(row[0])!==String(chapter))continue;const k=key(row[1]);if(out.has(k)){const old=out.get(k),merged=[...old];merged[2]=old[2]+'\n'+row[2];if(old[3]||row[3])merged[3]=[old[3],row[3]].filter(Boolean).join('\n');out.set(k,merged)}else out.set(k,row)}return out}
 function fromSource(id,input,verse,chapter){return rows(id,input).find(r=>(chapter===undefined||String(r[0])===String(chapter))&&String(r.sourceVerse??r[1])===String(verse))?.[1]??verse}
 return {map,rows,fromSource};
})();
