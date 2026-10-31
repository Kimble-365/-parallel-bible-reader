'use strict';
const fs=require('node:fs/promises'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
global.window=global;if(!global.crypto)Object.defineProperty(global,'crypto',{value:require('node:crypto').webcrypto});
global.document={documentElement:{dataset:{dataPath:'../../data/'}}};global.location={href:'https://reader.test/releases/v1.23/'};
Object.defineProperty(global,'navigator',{value:{onLine:true},configurable:true});let corrupt=false;const urls=[];
global.fetch=async input=>{const u=new URL(input,location.href);urls.push(u.pathname);try{let b=await fs.readFile(path.join(process.cwd(),u.pathname));if(corrupt&&u.pathname.includes('/syriac-data/')){b=Buffer.from(b);b[20]^=255}return {ok:true,status:200,arrayBuffer:async()=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),text:async()=>b.toString()}}catch{return {ok:false,status:404}}};
(async()=>{
 for(const file of ['catalog.js','vendor/pako_inflate.min.js','compression.js','syriac-manifest.js','syriac-data.js','offline-library.js'])vm.runInThisContext(await fs.readFile('releases/v1.23/'+file,'utf8'));
 const gen=await ReaderOffline.loadBook('GEN',['syc-peshitta-ot','syc-etcbc-biblical'],{forceOnline:true});
 assert.equal(Object.keys(gen.editions).length,2);assert.match(gen.editions['syc-peshitta-ot'][0][2],/^ܒܪܫܝܬ/);assert.equal(gen.editions['syc-peshitta-ot'][0][3],undefined);
 assert.ok(urls.every(u=>!u.includes('syriac-index')&&!u.includes('syriac-lexicon')),'ordinary reading must not download analyses');
 const psa=await ReaderOffline.loadBook('PSA',['syc-peshitta-ot','syc-syrohexapla-ps'],{forceOnline:true});assert.equal(psa.editions['syc-syrohexapla-ps'].length,464);
 const nt=await ReaderOffline.loadBook('JHN',['syc-dsc-nt'],{forceOnline:true});assert.ok(nt.editions['syc-dsc-nt'].length>800);
 const idx=await ReaderSyriac.loadIndex('syc-etcbc-biblical','GEN');const token=idx.verses['1:1'].tokens[0];const entry=await ReaderSyriac.entry(token[3]);assert.equal(entry.lemma,'B');assert.ok(entry.gloss);assert.ok(urls.some(u=>u.includes('syriac-lexicon')));
 const raw=await ReaderSyriac.loadText('syc-dsc-nt','LUK');assert.equal(raw.source['11:42'].source_units.length,2);assert.ok(raw.editions['syc-dsc-nt'].find(r=>r[0]===11&&r[1]===42)[6]);
 corrupt=true;await assert.rejects(ReaderSyriac.loadText('syc-dsc-nt','ROM'),/checksum|incorrect|invalid|data|gzip/i);
 console.log('PASS four Syriac editions, lazy shared lexicon, source defect and corrupt-pack rejection');
})().catch(error=>{console.error(error);process.exitCode=1});
