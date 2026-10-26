'use strict';
const CACHE='parallel-reader-shell-1.13-r1';
const ASSETS=['./','index.html','manifest.webmanifest','reader.js','notes-model.js','notes-ui.js','search-engine.js','search-manifest.js','offline-library.js','offline-ui.js','boot.js','private-import.js','private-ui.js','ont-map.js','script-adapters.js','catalog.js','LICENSES.md','translations/','translations/index.html','translations/directory.js','translations/directory-boot.js','translations/metadata.js','icons/icon-192.png','icons/icon-512.png','icons/apple-touch-icon.png','../../reader-guides.js','../v1.8/pronunciation/english-ga.js','../v1.8/pronunciation/CMUDICT-LICENSE.txt'];
const paths=new Set(ASSETS.map(p=>new URL(p,self.registration.scope).pathname));
const readerRoutes=new Set(['./','index.html','translations/','translations/index.html'].map(p=>new URL(p,self.registration.scope).pathname));
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const key of await caches.keys())if(key.startsWith('parallel-reader-shell-1.13-')&&key!==CACHE)await caches.delete(key);await self.clients.claim()})()));
self.addEventListener('message',e=>{if(e.data?.type==='ACTIVATE_UPDATE')self.skipWaiting()});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
 if(e.request.mode==='navigate'&&readerRoutes.has(u.pathname)){e.respondWith((async()=>{const cache=await caches.open(CACHE);if(u.pathname.endsWith('/translations/')||u.pathname.endsWith('/translations/index.html'))return (await cache.match(new URL('translations/index.html',self.registration.scope)))||fetch(e.request);return (await cache.match(new URL('index.html',self.registration.scope)))||fetch(e.request)})());return}
 if(paths.has(u.pathname))e.respondWith((async()=>{const c=await caches.open(CACHE);return (await c.match(u.origin+u.pathname,{ignoreSearch:true}))||fetch(e.request)})());
});
