'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const dir=process.env.FONT_TEST_DIR||path.join(__dirname,'../releases/v1.28');
const fonts=require(path.join(dir,'reading-fonts.js'));
const map=new Map([['parallel-reader-notes-v1','PRIVATE NOTE'],['bible-reader-appearance','{"theme":"blue"}']]);
const storage={getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,v)};
assert.equal(fonts.read(storage),'default');
for(const choice of fonts.choices){assert(fonts.save(storage,choice.id));assert.equal(fonts.read(storage),choice.id);}
for(const bad of ['url(https://example.com)', '<script>',null,{},'__proto__','SYSTEM'])assert.equal(fonts.normalize(bad),'default');
assert.equal(fonts.read({getItem(){throw Error('denied');}}),'default');
assert.equal(fonts.save({setItem(){throw Error('quota');}},'book'),false);
assert.equal(fonts.save(null,'book'),false);
assert.equal(map.get('parallel-reader-notes-v1'),'PRIVATE NOTE');assert.equal(map.get('bible-reader-appearance'),'{"theme":"blue"}');
const shell=fs.readFileSync(path.join(dir,'sw.js'),'utf8');assert(shell.includes("'reading-fonts.js'"));assert(shell.includes("'reading-fonts.css'"));
const boot=fs.readFileSync(path.join(dir,'boot.js'),'utf8');assert(boot.indexOf('simple-ui.js')<boot.indexOf('reading-fonts.js'));
assert.equal(new Set(fonts.choices.map(c=>c.id)).size,6);
console.log('PASS: six font choices, strict whitelist, unavailable/quota storage, preserved note/theme stores and offline inclusion');
