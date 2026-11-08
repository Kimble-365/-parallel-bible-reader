'use strict';
/* Project reading aids, MIT. Versioned estimates, never a source-text replacement. */
(()=>{
 const cons={'א':'ʼ','ב':'v','ג':'g','ד':'d','ה':'h','ו':'v','ז':'z','ח':'kh','ט':'t','י':'y','כ':'kh','ך':'kh','ל':'l','מ':'m','ם':'m','נ':'n','ן':'n','ס':'s','ע':'ʼ','פ':'f','ף':'f','צ':'ts','ץ':'ts','ק':'k','ר':'r','ש':'sh','ת':'t'};
 const vowels={'\u05b1':'e','\u05b2':'a','\u05b3':'o','\u05b4':'i','\u05b5':'e','\u05b6':'e','\u05b7':'a','\u05b8':'a','\u05b9':'o','\u05ba':'o','\u05bb':'u','\u05c7':'o'};
 function clusters(word){return [...word.normalize('NFD').matchAll(/([א-ת])([\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]*)/gu)].map(m=>({letter:m[1],marks:m[2]}))}
 function hebrewWord(word,phonetic){
  const cs=clusters(word);if(!cs.length)return word;
  // Conventional synagogue reading of the divine name, explicitly documented.
  if(phonetic&&cs.map(c=>c.letter).join('')==='יהוה')return cs.some(c=>c.marks.includes('\u05b4'))?'Elohim':'Adonai';
  const vowel=c=>[...c.marks].map(m=>vowels[m]||'').join('');let out='';
  for(let i=0;i<cs.length;i++){
   const c=cs[i],next=cs[i+1],prev=cs[i-1];let sound=cons[c.letter]||c.letter,v=vowel(c);
   if(c.letter==='ש'&&c.marks.includes('\u05c2'))sound='s';
   if(c.marks.includes('\u05bc'))sound=({'ב':'b','כ':'k','ך':'k','פ':'p','ף':'p'}[c.letter]||sound);
   if(phonetic){
    if(c.letter==='ו'&&c.marks.includes('\u05bc')&&!v){out+='u';continue}
    if(c.letter==='ו'&&/[\u05b9\u05ba]/u.test(c.marks)){out+='o';continue}
    if(c.letter==='י'&&!v&&!c.marks.includes('\u05b0')&&prev&&/[\u05b4\u05b5]/u.test(prev.marks))continue;
    if(c.letter==='ה'&&i===cs.length-1&&!v&&!c.marks.includes('\u05bc'))continue;
    // Furtive patah: vowel precedes final guttural; not an extra following syllable.
    if(i===cs.length-1&&/[חעה]/u.test(c.letter)&&c.marks.includes('\u05b7')&&prev&&(/[\u05b4\u05b5\u05b9\u05ba\u05bb]/u.test(prev.marks)||prev.letter==='ו')){out+='a'+sound;continue}
    if(c.marks.includes('\u05b0')){
     // Bounded vocal-sheva heuristic. The visible notice discloses lexical ambiguity.
     v=i===0||prev?.marks.includes('\u05b0')||c.marks.includes('\u05bc')?'e':'';
     if(i===cs.length-1)v='';
    }
    if(c.letter==='א'&&!v)sound='';
   }else if(c.marks.includes('\u05b0'))v='ə';
   out+=sound+v;
  }
  return out;
 }
 function hebrew(text,phonetic=true){return String(text).replace(/[א-ת][א-ת\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]*/gu,w=>hebrewWord(w,phonetic)).replace(/\u2060/gu,'').replace(/־/gu,'-').replace(/׃/gu,'.').replace(/׀/gu,'|')}
 const greekCons={β:'v',γ:'gh',δ:'dh',ζ:'z',θ:'th',κ:'k',λ:'l',μ:'m',ν:'n',ξ:'ks',π:'p',ρ:'r',σ:'s',ς:'s',τ:'t',φ:'f',χ:'kh',ψ:'ps'};
 function greekWord(word){
  const cs=[...word.normalize('NFD').toLowerCase().matchAll(/([α-ωϲ])([\u0300-\u036f]*)/gu)].map(m=>({letter:m[1]==='ϲ'?'σ':m[1],marks:m[2]}));let out='';if(!cs.length)return word;
  const stress=(value,...parts)=>parts.some(p=>/[\u0300\u0301\u0342]/u.test(p?.marks||''))?value.replace(/[aeiou]/u,v=>v+'\u0301'):value;
  const front=c=>c&&/[ειηυ]/u.test(c.letter);const voiced=c=>!c||!/[θκξπστφχψ]/u.test(c.letter);
  for(let i=0;i<cs.length;i++){
   const c=cs[i],n=cs[i+1],pair=c.letter+(n?.letter||'');let value;
   const combine=n&&!n.marks.includes('\u0308')&&!/[\u0300\u0301\u0342]/u.test(c.marks);
   if(combine&&['αι','ει','οι','υι','ου'].includes(pair)){value=stress(pair==='αι'?'e':pair==='ου'?'u':'i',c,n);i++}
   else if(combine&&['αυ','ευ','ηυ'].includes(pair)){value=stress((pair[0]==='α'?'a':pair[0]==='ε'?'e':'i')+(voiced(cs[i+2])?'v':'f'),c,n);i++}
   else if(['μπ','ντ','γκ','γγ','γξ','γχ','τσ','τζ'].includes(pair)){value=({'μπ':i===0?'b':'mb','ντ':i===0?'d':'nd','γκ':i===0?'g':'ng','γγ':'ng','γξ':'nks','γχ':'nkh','τσ':'ts','τζ':'dz'})[pair];i++}
   else if(/[αεηιουω]/u.test(c.letter))value=stress(({'α':'a','ε':'e','η':'i','ι':'i','ο':'o','υ':'i','ω':'o'})[c.letter],c);
   else {value=greekCons[c.letter]||c.letter;if(c.letter==='γ'&&(front(n)||pair==='γα'&&cs[i+2]?.letter==='ι'))value='y';if(c.letter==='σ'&&n&&/[βγδμνρ]/u.test(n.letter))value='z';if(n?.letter===c.letter&&c.letter!=='ρ')i++;}
   out+=value;
  }
  return out.normalize('NFC');
 }
 function greek(text){return String(text).replace(/[\p{Script=Greek}][\p{Script=Greek}\p{M}]*/gu,greekWord).replace(/\u037e|;/gu,'?').replace(/\u0387|·/gu,';')}
 const api={version:'reading-estimate-1',hebrew,greek};window.ReaderPronunciation=Object.freeze(api);
})();
