'use strict';
const assert=require('node:assert/strict'),path=require('node:path');
const media=require(path.join(process.env.MEDIA_TEST_DIR||path.join(__dirname,'../releases/v1.28'),'verse-media.js'));
const width=s=>Array.from(s).length;
for(const text of ['Å ä ö Ἐν ἀρχῇ','בְּרֵאשִׁית اُردُو','हिन्दी தமிழ் 日本語','e\u0301e\u0301e\u0301','👩‍👩‍👧‍👦']){
 const lines=media.wrap(text,width,10);assert.equal(lines.join(''),text);assert(lines.every(s=>!s.startsWith('\u0301')));
}
assert.deepEqual(media.wrap('one\ntwo',width,20),['one','two']);
assert.throws(()=>media.wrap('x'.repeat(12001),width,10),/too long/);
assert.equal(media.graphemes('e\u0301').length,1);
console.log('PASS: bounded image text, explicit paragraphs, Unicode grapheme wrapping and exact text retained across wrap lines');
