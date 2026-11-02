'use strict';
/* Display adapter only: never rewrites source rows or stored source keys. */
(()=>{
 function segments(id,row,text){
  const fallback=String(row[0])+':'+String(row[1])+(row[4]&&row[4]>row[1]?'–'+row[4]:'');
  if(id!=='fin-kr1938')return [{reference:fallback,text:String(text||'')}];
  const input=String(text||''),matches=[...input.matchAll(/\{(\d+):(\d+[a-z]?)\}/gi)];
  if(!matches.length)return [{reference:fallback,text:input}];
  const out=[],opening=input.slice(0,matches[0].index).trim();if(opening)out.push({reference:fallback,text:opening});
  matches.forEach((m,i)=>{const words=input.slice(m.index+m[0].length,matches[i+1]?.index??input.length).trim();if(words)out.push({reference:m[1]+':'+m[2],text:words})});return out;
 }
 function plain(id,row,text){return segments(id,row,text).map(s=>s.reference+' '+s.text).join('\n')}
 window.ReaderVerseText={segments,plain};
})();
