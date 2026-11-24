'use strict';
window.ReaderStudyModel=(()=>{
 const KEY='parallel-reader-study-v1';
 function today(d=new Date()){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
 function validDate(s){if(!/^\d{4}-\d{2}-\d{2}$/.test(s||''))return false;const d=new Date(s+'T00:00:00Z');return !isNaN(d)&&d.toISOString().slice(0,10)===s}
 function day(s){return Date.parse(s+'T00:00:00Z')/86400000}
 function empty(){return {schema:1,history:[],start:today(),completed:[]}}
 function validate(x){if(!x||x.schema!==1||!Array.isArray(x.history)||!Array.isArray(x.completed)||!validDate(x.start))throw Error('Invalid study data.');return {schema:1,history:x.history.filter(r=>r&&typeof r.query==='string'&&r.query.length<=4000&&/^#[A-Z0-9]{3}\.[A-Za-z0-9]+\.\d+[A-Za-z0-9]*$/.test(r.hash)&&typeof r.title==='string'&&r.title.length<=500&&typeof r.edition==='string'&&r.edition.length<=500&&typeof r.time==='string').slice(0,100),start:x.start,completed:x.completed.filter(v=>/^\d{4}-\d{2}-\d{2}:\d$/.test(v)).slice(-1000)}}
 function load(storage){const s=storage.getItem(KEY);return s?validate(JSON.parse(s)):empty()}
 function save(storage,state){const s=validate(state);storage.setItem(KEY,JSON.stringify(s));return s}
 function visit(state,url,title,edition,now=new Date()){const u=new URL(url),r={query:u.search,hash:u.hash,title:String(title).slice(0,500),edition:String(edition).slice(0,500),time:now.toISOString()},key=r.query+'|'+r.hash.split('.').slice(0,2).join('.');state.history=[r,...state.history.filter(x=>x.query+'|'+x.hash.split('.').slice(0,2).join('.')!==key)].slice(0,100);return state}
 function planIndex(state,date=today()){if(!validDate(date))throw Error('Invalid date');return Math.floor(day(date)-day(state.start))}
 function mark(state,index,value){if(!Number.isInteger(index)||index<0||index>6)throw Error('Invalid reading');const key=state.start+':'+index;state.completed=state.completed.filter(x=>x!==key);if(value)state.completed.push(key);return state}
 return {KEY,today,validDate,empty,load,save,validate,visit,planIndex,mark};
})();
