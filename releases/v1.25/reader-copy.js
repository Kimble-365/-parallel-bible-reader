'use strict';
(()=>{
 const root=document.getElementById('verses');
 function plain(node){if(node.nodeType===3)return node.nodeValue;if(node.nodeType!==1&&node.nodeType!==11)return '';if(node.nodeType===1&&node.matches('rt,rp,button,select,h3,.verse-gutter,.source-actions,.notice,.missing'))return '';const value=[...node.childNodes].map(plain).join('');return node.nodeType===1&&node.matches('div,p,section,br')?value.replace(/\n+$/,'')+'\n':value;}
 document.addEventListener('copy',event=>{const selection=window.getSelection();if(!selection?.rangeCount||selection.isCollapsed||!event.clipboardData)return;const parts=[];for(let i=0;i<selection.rangeCount;i++){const range=selection.getRangeAt(i);if(!root.contains(range.startContainer)||!root.contains(range.endContainer))return;parts.push(plain(range.cloneContents()).trim())}const text=parts.filter(Boolean).join('\n').replace(/\n{3,}/g,'\n\n');if(text){event.clipboardData.setData('text/plain',text);event.preventDefault()}});
})();
