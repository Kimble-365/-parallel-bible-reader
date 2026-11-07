'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),crypto=require('crypto');
const ctx={window:{},TextEncoder};vm.createContext(ctx);
for(const file of ['verse-text.js','notes-model.js'])vm.runInContext(fs.readFileSync('releases/v1.28/'+file,'utf8'),ctx);
const V=ctx.window.ReaderVerseText,N=ctx.window.ReaderNotesModel;
const bytes=fs.readFileSync('data/MAT.js');
assert.equal(crypto.createHash('sha1').update(Buffer.concat([Buffer.from('blob '+bytes.length+'\0'),bytes])).digest('hex'),'ba2e81d0e95ed5683cea5a6851c97f53b1e96ba7');
vm.runInContext(bytes.toString(),ctx);const rows=ctx.window.BibleBooks.MAT.editions['fin-kr1938'],r=rows.find(r=>r[0]===6&&r[1]===13),before=JSON.stringify(rows);
const expected='Äläkä saata meitä kiusaukseen; vaan päästä meidät pahasta, sillä sinun on valtakunta ja voima ja kunnia iankaikkisesti. Amen.';
assert.equal(V.segments('fin-kr1938',r,r[2])[0].text,expected);assert.equal(V.plain('fin-kr1938',r,r[3]),'6:13 '+expected);
assert.equal(V.clean('fin-kr1938','[Amen.] <FO>test<Fo>'),'[Amen.] test');
assert.equal(V.clean('other','&lt;FO&gt;[Amen.]&lt;Fo&gt;'),'&lt;FO&gt;[Amen.]&lt;Fo&gt;');
const edition={id:'fin-kr1938',label:'KR33/38',language:'fi'};
assert.equal(N.passage(edition,[['MAT','Matthew']],{book:'MAT',chapter:6,verse:13},rows).text,expected);
assert(!N.passage(edition,[['MAT','Matthew']],{book:'MAT',chapter:6,verse:12,end:14},rows).text.includes('&lt;'));
assert.equal(JSON.stringify(rows),before);
let count=0,changed=0;for(const name of fs.readdirSync('data').filter(n=>n.endsWith('.js')&&!['catalog.js'].includes(n))){
 const src=fs.readFileSync('data/'+name,'utf8');if(!src.includes('window.BibleBooks['))continue;
 vm.runInContext(src,ctx);
 const book=name.slice(0,-3),all=ctx.window.BibleBooks[book]?.editions?.['fin-kr1938']||[];
 for(const row of all){count++;const text=V.clean('fin-kr1938',row[2]);if(text!==row[2])changed++;assert(!/&lt;.*?&gt;|<[^>]*>/.test(text),book+':'+row[0]+':'+row[1]);}
}
assert.equal(count,31087);assert.equal(changed,1);console.log('PASS KR33/38: 31,087 rows audited; only MAT 6:13 adapted; original MAT blob pinned; brackets and other editions preserved; Notes single/range clean');
