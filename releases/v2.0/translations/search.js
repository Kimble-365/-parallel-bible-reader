/* Translation-name discovery only. Never normalize Scripture payloads. */
'use strict';
window.ReaderDirectorySearch=(()=>{
 const key=value=>String(value??'').normalize('NFKC').toLocaleLowerCase('en').normalize('NFD').replace(/(\p{Script=Latin})[\u0300-\u036f]+/gu,'$1').normalize('NFC').replace(/\s+/g,' ').trim();
 const strings=values=>[...new Set(values.filter(v=>typeof v==='string'&&v.trim()).map(v=>v.trim()))];
 function build(rows,labels={}){return rows.map(row=>{const aliases=strings(row.aliases||[]),language=strings([row.language]),codes=strings([row.iso6393,row.id]),titles=strings([labels[row.id],row.variety]);return {row,codes:codes.map(key),language:language.map(key),aliases:aliases.map(key),titles:titles.map(key),fields:strings([...codes,...language,...aliases,...titles]).map(key),names:[...language,...aliases]}})}
 function distance(a,b,limit){
  if(Math.abs(a.length-b.length)>limit)return limit+1;let before=null,previous=Array.from({length:b.length+1},(_,i)=>i);
  for(let i=1;i<=a.length;i++){const next=[i];for(let j=1;j<=b.length;j++){next[j]=Math.min(next[j-1]+1,previous[j]+1,previous[j-1]+(a[i-1]===b[j-1]?0:1));if(i>1&&j>1&&a[i-1]===b[j-2]&&a[i-2]===b[j-1])next[j]=Math.min(next[j],before[j-2]+1)}before=previous;previous=next}return previous[b.length];
 }
 function search(index,input,accept=()=>true){
  if(typeof input!=='string'||input.length>160)return {rows:[],suggestions:[],limited:true};const term=key(input),parts=term.split(' ').filter(Boolean),available=index.filter(e=>accept(e.row));
  function rank(e){if(!term)return 10;if(e.codes.includes(term))return 0;if(e.language.includes(term))return 1;if(e.aliases.includes(term))return 2;if(e.titles.includes(term))return 3;if(e.codes.some(s=>s.startsWith(term)))return 4;if(e.language.some(s=>s.startsWith(term)))return 5;if(e.aliases.some(s=>s.startsWith(term)))return 6;return 7}
  const matched=available.filter(e=>!term||parts.every(p=>e.fields.some(s=>s.includes(p)))).map(e=>({entry:e,rank:rank(e)})).sort((a,b)=>a.rank-b.rank||a.entry.row.language.localeCompare(b.entry.row.language,'en')||a.entry.row.id.localeCompare(b.entry.row.id,'en'));
  const result={rows:matched.map(e=>e.entry.row),suggestions:[],limited:false};
  // Suggestions are explicit alternatives, never results or automatic selection.
  if(result.rows.length||term.length<4||term.length>48||!/^[a-z]+(?: [a-z]+)*$/.test(term))return result;
  const limit=term.length>=8?2:1,candidates=new Map();
  for(const e of available)for(const name of e.names){const normalized=key(name);if(normalized.length<4||normalized.length>48||!/^[a-z]+(?: [a-z]+)*$/.test(normalized))continue;const d=distance(term,normalized,limit);if(d>limit)continue;const found=candidates.get(normalized);if(found){found.editionIds.push(e.row.id);continue}candidates.set(normalized,{term:name,distance:d,editionIds:[e.row.id]})}
  result.suggestions=[...candidates.values()].sort((a,b)=>a.distance-b.distance||a.term.localeCompare(b.term,'en')).slice(0,5);return result;
 }
 return {key,build,search};
})();
