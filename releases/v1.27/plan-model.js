'use strict';
window.ReaderPlanModel=(()=>{
 const KEY='parallel-reader-multi-plans-v1',plans=ReaderReadingPlans;
 const today=()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')};
 function date(s){return /^\d{4}-\d{2}-\d{2}$/.test(s||'')&&!isNaN(Date.parse(s+'T00:00:00Z'))&&new Date(s+'T00:00:00Z').toISOString().slice(0,10)===s}
 const day=s=>Date.parse(s+'T00:00:00Z')/86400000,keys=plan=>plan.days.flatMap((d,i)=>d.readings.map((r,j)=>i+':'+j));
 function record(){return {start:today(),dated:false,complete:[]}}
 function empty(){return {schema:1,selected:plans[0].id,records:Object.fromEntries(plans.map(p=>[p.id,record()]))}}
 function validate(x){if(!x||x.schema!==1||!x.records||typeof x.records!=='object'||Array.isArray(x.records)||!plans.some(p=>p.id===x.selected))throw Error('Invalid reading-plan data.');const records={};for(const p of plans){const r=x.records[p.id]??record(),allowed=new Set(keys(p));if(!date(r.start)||typeof r.dated!=='boolean'||!Array.isArray(r.complete)||r.complete.length>1000||r.complete.some(k=>typeof k!=='string'||!allowed.has(k)))throw Error('Invalid reading-plan progress.');records[p.id]={start:r.start,dated:r.dated,complete:[...new Set(r.complete)]}}return {schema:1,selected:x.selected,records}}
 function load(storage){const raw=storage.getItem(KEY);return raw===null?empty():validate(JSON.parse(raw))}
 function save(storage,state){const clean=validate(state);storage.setItem(KEY,JSON.stringify(clean));return clean}
 function mark(state,id,i,j,value){const plan=plans.find(p=>p.id===id);if(!plan?.days[i]?.readings[j])throw Error('Unknown plan reading.');const r=state.records[id],key=i+':'+j;r.complete=r.complete.filter(k=>k!==key);if(value)r.complete.push(key);return state}
 function progress(state,id){const p=plans.find(p=>p.id===id);if(!p)throw Error('Unknown reading plan.');const marked=new Set(state.records[id].complete),done=p.days.map((d,i)=>d.readings.every((_,j)=>marked.has(i+':'+j)));return {readings:marked.size,total:keys(p).length,days:done.filter(Boolean).length,totalDays:p.days.length,next:done.findIndex(x=>!x),done}}
 function calendar(start,index){if(!date(start)||!Number.isInteger(index)||index<0||index>10000)throw Error('Invalid plan date.');return new Date((day(start)+index)*86400000).toISOString().slice(0,10)}
 function todayIndex(start,now=today()){if(!date(start)||!date(now))throw Error('Invalid plan date.');return day(now)-day(start)}
 return {KEY,today,date,load,save,empty,validate,mark,progress,calendar,todayIndex};
})();
