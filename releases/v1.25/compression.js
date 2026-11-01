'use strict';
/* Native gzip where available, bundled Pako otherwise; both paths are bounded. */
window.ReaderCompression=(()=>{
 async function unpack(input,declared,max){
  const bytes=input instanceof Uint8Array?input:new Uint8Array(input);
  if(!Number.isInteger(declared)||declared<0||declared>max)throw Error('Invalid expanded pack length.');
  if(bytes[0]!==31||bytes[1]!==139){if(bytes.length>declared)throw Error('Text pack exceeds its declared length.');return bytes}
  function collect(){const parts=[];let size=0;return {add(part){size+=part.length;if(size>declared||size>max)throw Error('Expanded pack exceeds its declared length.');parts.push(part)},result(){const out=new Uint8Array(size);let at=0;for(const part of parts){out.set(part,at);at+=part.length}return out}}}
  if(typeof DecompressionStream==='function'){
   let reader;try{const output=collect();reader=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();for(;;){const {done,value}=await reader.read();if(done)break;output.add(value)}return output.result()}catch(error){try{await reader?.cancel()}catch{}/* Older engines may expose an unusable gzip implementation. */}
  }
  if(!window.pako?.Inflate)throw Error('The local gzip decoder could not load. Reload the reader while online.');
  const output=collect(),decoder=new window.pako.Inflate({chunkSize:65536});decoder.onData=chunk=>output.add(chunk);
  decoder.push(bytes,true);if(decoder.err||!decoder.ended)throw Error('Incomplete or invalid gzip text pack.');return output.result();
 }
 return {unpack};
})();
