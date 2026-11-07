'use strict';
/* Display adapter only: never rewrites source rows or stored source keys. */
(()=>{
 // Known legacy formatting delimiters, not Scripture. Keep all words and punctuation.
 // Scope to this edition; never evaluate HTML or remove textual square brackets.
 function clean(id,text){const input=String(text||'');return id==='fin-kr1938'?input.replace(/(?:&lt;|<)FO(?:&gt;|>)/gi,''):input}
 function segments(id,row,text){
  const fallback=String(row[0])+':'+String(row[1])+(row[4]&&row[4]>row[1]?'–'+row[4]:'');
  if(id!=='fin-kr1938')return [{reference:fallback,text:String(text||'')}];
  const input=clean(id,text),matches=[...input.matchAll(/\{(\d+):(\d+[a-z]?)\}/gi)];
  if(!matches.length)return [{reference:fallback,text:input}];
  const out=[],opening=input.slice(0,matches[0].index).trim();if(opening)out.push({reference:fallback,text:opening});
  matches.forEach((m,i)=>{const words=input.slice(m.index+m[0].length,matches[i+1]?.index??input.length).trim();if(words)out.push({reference:m[1]+':'+m[2],text:words})});return out;
 }
 function plain(id,row,text){return segments(id,row,text).map(s=>s.reference+' '+s.text).join('\n')}
 window.ReaderVerseText={segments,plain,clean,revision:'kr1938-format-1'};
})();
