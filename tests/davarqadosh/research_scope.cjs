'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'../..'),context={window:{},TextDecoder,Uint8Array,DataView};
vm.runInNewContext(fs.readFileSync(path.join(root,'davarqadosh/lexical-pack-reader.js'),'utf8'),context);
const reader=context.window.LexicalPackReader;
assert.equal(typeof reader.researchFor,'function','Occurrence research needs an explicit token scope');
const book={research:[
 {id:'verse-report',verse_key:'Gen.1.1',token_id:null},
 {id:'first-word',verse_key:'Gen.1.1',token_id:'first'},
 {id:'second-word',verse_key:'Gen.1.1',token_id:'second'},
 {id:'other-verse',verse_key:'Gen.1.2',token_id:null},
 {id:'wrong-verse-same-token',verse_key:'Gen.1.2',token_id:'first'}
]};
const ids=token=>Array.from(reader.researchFor(book,token),r=>r.id);
assert.deepEqual(ids({id:'first',verse_key:'Gen.1.1'}),['verse-report','first-word']);
assert.deepEqual(ids({id:'second',verse_key:'Gen.1.1'}),['verse-report','second-word']);
assert.deepEqual(ids({id:'third',verse_key:'Gen.1.1'}),['verse-report']);
assert.equal(book.research.length,5);
console.log('PASS: occurrence-specific drafts stay with their exact token; verse reports stay available only in that verse.');
