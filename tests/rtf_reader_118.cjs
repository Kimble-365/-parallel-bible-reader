'use strict';const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');global.window=global;vm.runInThisContext(fs.readFileSync('releases/v1.18/rtf-reader.js','utf8'));const R=ReaderRTF;
assert.equal(R.text(String.raw`{\rtf1\ansi{\fonttbl{\f0 Arial;}}Hello \b world\b0.\par New line.}`),'Hello world.\nNew line.');
assert.equal(R.text(String.raw`{\rtf1\ansi \'e4\'f6\'e5}`),'äöå');
assert.equal(R.text(String.raw`{\rtf1\uc1\u26085?\u26412?\u35486?}`),'日本語');
assert.equal(R.text(String.raw`{\rtf1\uc0\u-10179\u-8704}`),'😀');
assert.equal(R.text(String.raw`{\rtf1 text {\*\fldinst HYPERLINK "javascript:bad"}{\fldrslt visible} \{literal\}}`),'text visible {literal}');
assert.equal(R.text(String.raw`\cf2 Plain fragment`),'Plain fragment');
assert.throws(()=>R.text(String.raw`{\rtf1 unclosed`),/Unclosed/);assert.throws(()=>R.text(String.raw`\ansicpg99999 test`),/Unsupported/);
console.log('PASS: RTF groups/formatting, omitted font and field instructions, visible field results, code-page hex, Unicode fallback/surrogate pairs, escaped literal braces and malformed input');
