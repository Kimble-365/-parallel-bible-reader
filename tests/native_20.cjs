'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync('releases/v2.0/runtime.js','utf8');
async function run(native){
 const events={},calls=[],alerts=[],node={textContent:''},platforms=['windows','macos','ios','android'].map(p=>({dataset:{platform:p}}));
 const document={documentElement:{dataset:{}},addEventListener:(n,f)=>events[n]=f,getElementById:()=>node,querySelectorAll:()=>platforms};
 function Anchor(){}Anchor.prototype.click=function(){calls.push(['ordinary-click'])};
 const navigator={platform:'Win32',userAgent:'Windows NT',maxTouchPoints:0};
 const window={addEventListener:(n,f)=>events[n]=f,dispatchEvent:e=>events[e.type]?.(e)};
 if(native)window.__TAURI__={core:{invoke:async(cmd,args)=>{calls.push([cmd,args]);return cmd==='runtime_info'?{os:'ios',native:true,version:'2.0.0',arch:'aarch64'}:cmd==='save_export'?'/app/exports/test.txt':undefined}}};
 const context={window,navigator,document,HTMLAnchorElement:Anchor,location:{href:'http://tauri.localhost/releases/v2.0/',origin:'http://tauri.localhost'},URL,Uint8Array,Array,String,CustomEvent:function(type,x){this.type=type;this.detail=x.detail},alert:x=>alerts.push(x),fetch:async()=>({arrayBuffer:async()=>Uint8Array.from([65,66]).buffer})};
 vm.runInNewContext(source,context);await new Promise(setImmediate);events.DOMContentLoaded();
 const detect=window.ReaderRuntime.detect;
 for(const [n,os] of [[{platform:'MacIntel',maxTouchPoints:5},'ios'],[{platform:'MacIntel'},'macos'],[{userAgent:'Android 15'},'android'],[{platform:'Win32'},'windows'],[{platform:'Linux x86_64'},'linux'],[{},'unknown']])assert.equal(detect(n).os,os);
 if(native){assert.equal(window.ReaderRuntime.get().os,'ios');assert.match(node.textContent,/Rust application 2.0.0/);await navigator.clipboard.writeText('שמע λόγος');assert.equal(calls.at(-1)[1].text,'שמע λόγος');let prevented=false;events.click({target:{closest:()=>({href:'https://ebible.org/hebsg/'})},preventDefault:()=>prevented=true});assert(prevented);assert.equal(calls.at(-1)[0],'open_external');const a=new Anchor();a.download='test.txt';a.href='blob:test';a.click();await new Promise(setImmediate);assert.equal(calls.at(-1)[0],'save_export');assert.deepEqual(Array.from(calls.at(-1)[1].bytes),[65,66]);assert.match(alerts[0],/Export saved/);assert.equal(platforms[2].dataset.recommended,'true')}
 else{assert.equal(window.ReaderRuntime.get().native,false);assert.match(node.textContent,/browser hint/);assert.equal(calls.length,0)}
}
(async()=>{await run(false);await run(true);console.log('PASS 2.0 runtime: browser OS hints/iPad touch distinction, native target precedence, Unicode clipboard, external links and exact export bytes (mock bridge; not native execution)')})().catch(e=>{console.error(e);process.exit(1)});
