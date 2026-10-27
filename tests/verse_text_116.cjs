'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');global.window=global;vm.runInThisContext(fs.readFileSync('releases/v1.16/verse-text.js','utf8'));
const first=[5,1,'Veisuunjohtajalle; Daavidin virsi. {5:2} Ota korviisi minun sanani.'];const before=JSON.stringify(first);
assert.deepEqual(ReaderVerseText.segments('fin-kr1938',first,first[2]),[{reference:'5:1',text:'Veisuunjohtajalle; Daavidin virsi.'},{reference:'5:2',text:'Ota korviisi minun sanani.'}]);
assert.equal(ReaderVerseText.plain('fin-kr1938',[5,2],'{5:3} Kuuntele huutoni ääntä.'),'5:3 Kuuntele huutoni ääntä.');assert.equal(JSON.stringify(first),before);
assert.equal(ReaderVerseText.plain('engwebp',[3,16],'For God so loved'),'3:16 For God so loved');assert.equal(ReaderVerseText.plain('other',[3,16],'Keep {3:17} literal'),'3:16 Keep {3:17} literal');assert.equal(ReaderVerseText.plain('grc-source',[0,0],'Ἐν ἀρχῇ'),'0:0 Ἐν ἀρχῇ');assert.equal(ReaderVerseText.plain('other',[3,'16a','',null,18],'Text'),'3:16a Text');
console.log('PASS: Finnish source markers become separate native chapter:verse lines; ordinary/zero/letter references remain; unrelated braces and source rows unchanged');
