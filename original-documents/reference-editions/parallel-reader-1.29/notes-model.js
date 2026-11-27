/* Local plain-text notebook model. No remote requests or HTML evaluation. */
'use strict';
window.ReaderNotesModel=(()=>{
 const KEY='parallel-reader-notes-v1',MAX_NOTES=100,MAX_BYTES=2000000;
 const uid=()=>globalThis.crypto?.randomUUID?.()||Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
 function string(value,max){if(typeof value!=='string'||value.length>max)throw Error('Invalid or oversized notebook text.');return value}
 function quote(q){if(!q||typeof q!=='object')throw Error('Invalid passage.');return {reference:string(q.reference,200),edition:string(q.edition,200),editionId:string(q.editionId,100),text:string(q.text,100000),language:string(q.language||'',50),direction:['ltr','rtl','auto'].includes(q.direction)?q.direction:'auto'}}
 function note(n){if(!n||typeof n!=='object'||!Array.isArray(n.quotes)||n.quotes.length>100)throw Error('Invalid note.');return {id:string(n.id,100),title:string(n.title,200),body:string(n.body,100000),quotes:n.quotes.map(quote),updated:string(n.updated||'',50)}}
 function validate(notes){if(!Array.isArray(notes)||notes.length>MAX_NOTES)throw Error('A notebook can hold up to 100 notes.');const clean=notes.map(note);if(new Set(clean.map(n=>n.id)).size!==clean.length)throw Error('Duplicate note identifiers.');if(new TextEncoder().encode(JSON.stringify(clean)).length>MAX_BYTES)throw Error('Notebook is full. Export a backup before removing older notes.');return clean}
 function read(storage){const raw=storage.getItem(KEY);return raw===null?[]:validate(JSON.parse(raw))}
 function save(storage,notes){const clean=validate(notes);storage.setItem(KEY,JSON.stringify(clean));return clean}
 function create(passage){const q=passage?quote(passage):null;return {id:uid(),title:q?q.reference:'Untitled note',body:'',quotes:q?[q]:[],updated:new Date().toISOString()}}
 function parseBackup(raw){const data=JSON.parse(raw);if(data?.format!=='parallel-reader-notes'||data.version!==1)throw Error('Choose a Parallel Reader notes backup (.json).');return validate(data.notes).map(n=>({...n,id:uid()}))}
 function backup(notes){return JSON.stringify({format:'parallel-reader-notes',version:1,notes:validate(notes)},null,2)}
 function plain(n){n=note(n);return [n.title,...n.quotes.map(q=>q.reference+' — '+q.edition+'\n'+q.text),n.body].filter(Boolean).join('\n\n')+'\n'}
 function plan(input,current,edition,books,mode='reference'){
  if(!edition)throw Error('Choose a translation in Text 1 first. Other text columns are not used.');
  let result={...current,chapterOnly:mode==='chapter'};
  if(input!==null&&input!==undefined){const match=String(input).trim().match(/^(.+?)\s*\.?(\d+|[A-Za-z]+)\s*[:.](\d+[A-Za-z0-9]*)(?:\s*[-–]\s*(\d+[A-Za-z0-9]*))?$/);if(!match)throw Error('Use a book code or English book name and a reference, for example JHN 3:16-18.');const name=match[1].trim().replace(/\.$/,'').toLowerCase(),book=books.find(([code,label])=>code.toLowerCase()===name||label.toLowerCase()===name);if(!book)throw Error('Unknown book. Use a three-letter code such as GEN or JHN.');result={book:book[0],chapter:/^\d+$/.test(match[2])?Number(match[2]):match[2],verse:match[3],end:match[4],chapterOnly:false};}
  if(!edition.positions.some(([b,c])=>b===result.book&&String(c)===String(result.chapter)))throw Error('This book or chapter is not included in Text 1.');
  return result;
 }
 function passage(edition,books,request,rows){
  const chapter=rows.filter(r=>String(r[0])===String(request.chapter)),key=x=>String(x),start=key(request.verse),end=key(request.end??request.verse);
  function covers(row,v){return key(row[1])===v||row[4]&&/^\d+$/.test(v)&&Number(v)>=Number(row[1])&&Number(v)<=Number(row[4])}
  const first=chapter.findIndex(r=>covers(r,start)),last=chapter.findIndex(r=>covers(r,end));
  if(!request.chapterOnly&&(first<0||last<first))throw Error('That verse or range is not present in Text 1. Use its own source reference labels.');
  const chosen=request.chapterOnly?chapter:chapter.slice(first,last+1);if(!chosen.length||chosen.some(r=>!r[2]?.trim()))throw Error('The requested source text is unavailable or empty.');
  const label=row=>String(row[1])+(row[4]&&row[4]!==row[1]?'–'+row[4]:''),name=new Map(books).get(request.book)||request.book,ref=name+' '+request.chapter+(request.chapterOnly?'':':'+(chosen.length===1?label(chosen[0]):chosen[0][1]+'–'+(chosen.at(-1)[4]||chosen.at(-1)[1])));
  return quote({reference:ref,edition:edition.label,editionId:edition.id,language:edition.language,direction:edition.direction||'auto',text:chosen.length===1?chosen[0][2]:chosen.map(r=>label(r)+' '+r[2]).join('\n')});
 }
 return {KEY,MAX_BYTES,read,save,create,quote,validate,parseBackup,backup,plain,plan,passage};
})();
