const fs=require('fs'),vm=require('vm'),assert=require('assert');const ctx={window:{}};vm.createContext(ctx);vm.runInContext(fs.readFileSync('releases/v1.4/script-adapters.js','utf8'),ctx);const A=ctx.window.ScriptAdapters;
assert(A.supported('urdoucv'));assert(!A.supported('hin2017'));assert.equal(A.convert('hin2017','deva','ख़ुदा'),null);
let arab=A.convert('urd','arab','ख़ुदा १२३');assert(arab.text.includes('خ'));assert(arab.text.includes('۱۲۳'));assert(arab.text.includes('د'));assert(!/[\u0900-\u097f]/.test(arab.text));assert.equal(arab.direction,'rtl');
let deva=A.convert('urdoucv','deva','پ ٹ چ ڈ ڑ ژ گ ں ھ ہ ء ی ے ۱۲۳');assert(deva.text.includes('प्'));assert(deva.text.includes('ट्'));assert(deva.text.includes('ड़्'));assert(deva.text.includes('१२३'));assert(!/[\u0600-\u06ff]/.test(deva.text));
assert.notEqual(A.convert('urdoucv','deva','بِ').text,A.convert('urdoucv','deva','ب').text);assert(A.convert('urdoucv','deva','ب').text.endsWith('्'));
assert(A.convert('urdoucv','deva','خدا').notice.includes('Not pronunciation'));assert.equal(A.convert('urd','deva','उर्दू'),null);
assert(A.convert('urdoucv','deva','خدا').text.includes('ख़'));assert(A.convert('urdoucv','deva','love خدا').text.includes('love'));
console.log('PASS: supported languages, Urdu consonants/nukta, short-vowel distinction, numerals, bidi metadata, mixed-script preservation and uncertainty notices');
