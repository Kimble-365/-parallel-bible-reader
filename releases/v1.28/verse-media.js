'use strict';
(function(root){
 function graphemes(text){if(typeof Intl.Segmenter==='function')return [...new Intl.Segmenter(undefined,{granularity:'grapheme'}).segment(text)].map(x=>x.segment);const out=[];for(const c of Array.from(text)){if(out.length&&(/\p{M}/u.test(c)||c==='\u200d'||out.at(-1).endsWith('\u200d')))out[out.length-1]+=c;else out.push(c);}return out;}
 function wrap(text,measure,width){if(typeof text!=='string'||text.length>12000)throw Error('This passage is too long for a verse image. Use Copy instead.');const lines=[];for(const paragraph of text.split('\n')){let line='';for(const token of paragraph.match(/\s+|\S+/gu)||[]){if(measure(line+token)<=width){line+=token;continue;}if(line){lines.push(line);line='';}if(measure(token)<=width){line=token;continue;}if(typeof Intl.Segmenter!=='function')throw Error('This browser cannot safely wrap this passage for an image. Use Copy instead.');for(const part of graphemes(token)){if(line&&measure(line+part)>width){lines.push(line);line='';}line+=part;}}lines.push(line);}return lines;}
 async function image(q,{family='serif',background='#fff8df',ink='#302916'}={}){
  if(!q||typeof q.text!=='string'||typeof q.reference!=='string'||typeof q.edition!=='string')throw Error('Verse data is unavailable.');
  await root.document.fonts?.ready;const canvas=root.document.createElement('canvas');canvas.width=1080;let ctx=canvas.getContext('2d');if(!ctx)throw Error('Image creation is unavailable in this browser. Use Copy instead.');
  const font='40px '+family;ctx.font=font;const body=wrap(q.text,t=>ctx.measureText(t).width,936);ctx.font='28px system-ui, sans-serif';const heading=wrap(q.reference+' — '+q.edition,t=>ctx.measureText(t).width,936);const height=144+heading.length*44+32+body.length*64+60;
  if(height>8192)throw Error('This passage is too long for a readable verse image. Use Copy instead.');canvas.height=Math.max(540,height);ctx=canvas.getContext('2d');ctx.fillStyle=background;ctx.fillRect(0,0,canvas.width,canvas.height);ctx.fillStyle=ink;ctx.textBaseline='top';ctx.font='28px system-ui, sans-serif';let y=72;
  ctx.direction='ltr';ctx.textAlign='left';for(const line of heading){ctx.fillText(line,72,y);y+=44;}y+=32;ctx.font=font;ctx.direction=q.direction==='rtl'?'rtl':'ltr';ctx.textAlign=q.direction==='rtl'?'right':'left';for(const line of body){ctx.fillText(line,q.direction==='rtl'?1008:72,y);y+=64;}
  return await new Promise((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(Error('Could not create the PNG. Use Copy instead.')),'image/png'));
 }
 const api=Object.freeze({graphemes,wrap,image});if(typeof module==='object'&&module.exports)module.exports=api;root.ReaderVerseMedia=api;
})(typeof window==='object'?window:globalThis);
