'use strict';
let finishLayout;window.ReaderLayoutReady=new Promise(resolve=>{finishLayout=resolve});
(async()=>{try{await ReaderOffline.hydrate()}catch{}try{for(const name of ['reader.js','offline-ui.js','private-ui.js','notes-ui.js','media-ui.js','simple-ui.js','reading-fonts.js','verse-media.js','verse-actions.js','faith-resources.js','faith-library.js','page-turn.js','study-menu.js','study-extras.js','apparatus-ui.js','import-ui.js'])await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=name+'?v=1.28';script.onload=resolve;script.onerror=()=>reject(Error('Could not load '+name));document.head.append(script)})}finally{finishLayout()}})().catch(e=>{document.getElementById('status').textContent=e.message});




