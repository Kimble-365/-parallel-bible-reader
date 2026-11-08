'use strict';
(()=>{
 function detect(navigator){const ua=navigator.userAgent||'',platform=navigator.userAgentData?.platform||navigator.platform||'';let os='unknown';if(/Android/i.test(ua))os='android';else if(/iPad|iPhone|iPod/i.test(ua)||(/Mac/i.test(platform)&&navigator.maxTouchPoints>1))os='ios';else if(/Win/i.test(platform+' '+ua))os='windows';else if(/Mac/i.test(platform+' '+ua))os='macos';else if(/Linux/i.test(platform+' '+ua))os='linux';return {os,native:false,confidence:'browser hint',arch:'unknown'}}
 const invoke=window.__TAURI__?.core?.invoke;let current=detect(navigator);window.ReaderRuntime={detect,get:()=>({...current})};
 async function native(){if(!invoke)return;try{current=await invoke('runtime_info');current.confidence='native build target';document.documentElement.dataset.runtime=current.os;window.dispatchEvent(new CustomEvent('reader-runtime',{detail:current}))}catch{}}
 if(invoke){
  // Native clipboard writing only; no native clipboard-reading permission is exposed.
  try{Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:text=>invoke('copy_text',{text:String(text)})}})}catch{}
  document.addEventListener('click',event=>{const link=event.target.closest?.('a[href]');if(!link)return;let u;try{u=new URL(link.href,location.href)}catch{return}if(['http:','https:'].includes(u.protocol)&&u.origin!==location.origin){event.preventDefault();invoke('open_external',{url:u.href}).catch(e=>alert(String(e)))}},true);
  const click=HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click=function(){if(this.download&&this.href.startsWith('blob:')){const a=this;(async()=>{try{const bytes=new Uint8Array(await (await fetch(a.href)).arrayBuffer());const path=await invoke('save_export',{name:a.download,bytes:Array.from(bytes)});alert('Export saved to:\n'+path)}catch(e){alert('Export was not saved: '+String(e))}})();return}return click.call(this)};
 }
 function render(){const node=document.getElementById('runtime-summary');if(node){const names={windows:'Windows PC',macos:'Mac',ios:'iPad / iOS',android:'Android',linux:'Linux',unknown:'Unrecognized platform'};node.textContent=(names[current.os]||current.os)+' · '+(current.native?'Rust application '+current.version+' ('+current.arch+')':'Web reader; '+current.confidence)+'.';}document.querySelectorAll('[data-platform]').forEach(el=>{el.dataset.recommended=String(el.dataset.platform===current.os)})}
 document.addEventListener('DOMContentLoaded',render);window.addEventListener('reader-runtime',render);native();
})();
