'use strict';
/* Display adapter only: never rewrites source rows or stored source keys. */
(()=>{
 // Known legacy formatting delimiters, not Scripture. Keep all words and punctuation.
 // Scope to this edition; never evaluate HTML or remove textual square brackets.
 const wlcToken=/'(?:l s="H\d+"|\/l|seg type="x-(?:large|small|suspended)"|seg)'/g;
 function runs(id,text){
  if(id!=='hbo-wlc')return null;
  const input=String(text||''),out=[];let start=0,style=null;
  for(const m of input.matchAll(wlcToken)){
   if(m.index>start)out.push({text:input.slice(start,m.index),style});
   if(m[0].startsWith("'seg type="))style=m[0].match(/x-(large|small|suspended)/)[1];
   else if(m[0]==="'seg'")style=null;
   start=m.index+m[0].length;
  }
  if(!start)return null;if(start<input.length)out.push({text:input.slice(start),style});return out;
 }
 function clean(id,text){const input=String(text||'');if(id==='hbo-wlc')return input.replace(wlcToken,'');return id==='fin-kr1938'?input.replace(/(?:&lt;|<)FO(?:&gt;|>)/gi,''):input}
 function append(target,part){
  for(const run of part.runs||[{text:part.text}]){if(!run.style){target.append(document.createTextNode(run.text));continue}
   const span=document.createElement('span');span.textContent=run.text;span.dataset.sourceTypography=run.style;span.title='Source '+run.style+' letter';
   if(run.style==='large')span.style.fontSize='1.35em';if(run.style==='small')span.style.fontSize='.75em';if(run.style==='suspended'){span.style.verticalAlign='super';span.style.fontSize='.8em'}target.append(span);
  }
 }
 function segments(id,row,text){
  const fallback=String(row[0])+':'+String(row[1])+(row[4]&&row[4]>row[1]?'–'+row[4]:'');
  if(id!=='fin-kr1938')return [{reference:fallback,text:clean(id,text),runs:runs(id,text)}];
  const input=clean(id,text),matches=[...input.matchAll(/\{(\d+):(\d+[a-z]?)\}/gi)];
  if(!matches.length)return [{reference:fallback,text:input}];
  const out=[],opening=input.slice(0,matches[0].index).trim();if(opening)out.push({reference:fallback,text:opening});
  matches.forEach((m,i)=>{const words=input.slice(m.index+m[0].length,matches[i+1]?.index??input.length).trim();if(words)out.push({reference:m[1]+':'+m[2],text:words})});return out;
 }
 function plain(id,row,text){return segments(id,row,text).map(s=>s.reference+' '+s.text).join('\n')}
 window.ReaderVerseText={segments,plain,clean,runs,append,revision:'source-format-2'};
})();

