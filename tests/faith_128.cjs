'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const dir=process.env.FAITH_TEST_DIR||path.join(__dirname,'../releases/v1.28');
const context={window:{}};vm.runInNewContext(fs.readFileSync(path.join(dir,'faith-resources.js'),'utf8'),context);const rows=context.window.ReaderFaithResources;
assert.equal(rows.length,14);assert.equal(new Set(rows.map(r=>r.id)).size,14);
assert.equal(rows.filter(r=>r.kind==='Introduction').length,3);assert.equal(rows.filter(r=>r.kind==='Original prayer').length,8);assert.equal(rows.filter(r=>r.kind==='Historic prayer').length,3);
for(const r of rows){assert(r.text&&r.title&&r.credit);assert(r.text.length<6000);if(r.source){assert(r.source.startsWith('https://'));assert(r.rights);}}
assert.equal(rows.find(r=>r.id==='jesus-prayer').text.split(/\s+/).length,12);
assert(rows.find(r=>r.id==='healing').note.includes('promises no'));assert(rows.find(r=>r.id==='freedom').note.includes('does not diagnose'));
const sw=fs.readFileSync(path.join(dir,'sw.js'),'utf8');for(const f of ['faith-resources.js','faith-library.js','PRAYER-SOURCES.md'])assert(sw.includes("'"+f+"'"));
console.log('PASS: 14 distinct editorial resources, all historic selections attributed, bounded text, explicit care/diagnosis limits and offline assets');
