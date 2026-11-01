"""Saved apparatus access, saved-only races and filtered UTF-8 downloads."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}/releases/v1.25/'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(accept_downloads=True,viewport={'width':390,'height':844});page=ctx.new_page();errors=[];calls=[];page.on('pageerror',lambda e:errors.append(str(e)))
  fixture=(ROOT/'tests/fixtures/apparatus124/sbl-phm.xml').read_bytes()
  def source(route):
   calls.append(route.request.url);route.fulfill(body=fixture,headers={'Access-Control-Allow-Origin':'*','Content-Type':'application/xml'})
  page.route('https://raw.githubusercontent.com/Faithlife/SBLGNT/**/data/sblgntapp/xml/Phlm.xml',source)
  page.goto(base+'?edition=engwebp&compare1=&compare2=&compare3=&text=original#PHM.1.2');page.wait_for_selector('#v2 .main-text');page.wait_for_selector('#menu-study');assert page.evaluate('BibleCatalog.editions.length')==80
  def open_app():
   page.click('#menu-study');page.click('#menu-apparatus');page.wait_for_function('!document.querySelector("#apparatus-family").disabled')
  def saved():
   page.click('#apparatus-saved');page.wait_for_function('document.querySelector("#apparatus-status").textContent==="Saved apparatus list loaded."')
  open_app();saved();assert page.locator('button[data-source]').count()==0;assert page.locator('button[data-import]').count()==0;assert not calls
  page.get_by_role('button',name='Back to apparatus',exact=True).click();page.wait_for_function('!document.querySelector("#apparatus-family").disabled');page.select_option('#apparatus-book','PHM');page.click('#apparatus-read');page.wait_for_selector('#apparatus-entries .apparatus-entry');assert len(calls)==1;page.click('#apparatus-save');page.wait_for_function('document.querySelector("#apparatus-status").textContent.includes("saved on this device")')
  pack={'format':'parallel-reader-apparatus','version':1,'family':'syriac','title':'FORMAT TEST — NOT HISTORICAL EVIDENCE','source':'Synthetic test source','license':'Synthetic attribution','witnesses':{'EXAMPLE':'Synthetic witness'},'units':[{'id':'one','reference':'GEN.1.11','lemma':'ܐ','readings':[{'text':'ܒ','witnesses':['EXAMPLE'],'note':'Source hand: synthetic-test'}],'status':'unapproved-format','original':{'flags':{'rec':True},'locator':'test-line'}},{'id':'two','reference':'GEN.11.1','lemma':'x','readings':[{'text':'other reading','witnesses':['OTHER']}],'status':'not-adopted'}]}
  page.evaluate('(pack)=>ReaderApparatus.save(pack)',pack)
  saved();assert page.locator('button[data-source="sbl"][data-book="PHM"]').count()==1;assert page.locator('button[data-import]').count()==1
  # Private import opens directly; reference stepping from All starts at the first source reference.
  page.locator('button[data-import]').click();page.wait_for_selector('#apparatus-entries .apparatus-entry');assert page.input_value('#apparatus-family')=='syriac';assert page.input_value('#apparatus-reference')=='';assert page.locator('#apparatus-next').inner_text()=='First reference';page.click('#apparatus-next');assert page.input_value('#apparatus-reference')=='GEN.1.11';page.fill('#apparatus-search','ܒ');page.select_option('#apparatus-witness','EXAMPLE')
  with page.expect_download() as d:page.click('#apparatus-export-text')
  text=Path(d.value.path()).read_text(encoding='utf-8');assert 'ܒ' in text and 'Synthetic attribution' in text and 'unapproved-format' in text;assert '"rec":true' in text and 'test-line' in text;assert 'GEN.11.1' not in text;assert '1 matching entries' in text
  page.fill('#apparatus-search','missing');assert page.locator('#apparatus-export-text').is_disabled();page.fill('#apparatus-search','')
  # Saved source books really survive a full offline reload, independently of private imports.
  page.locator('#apparatus-dialog').get_by_role('button',name='Back to reading',exact=True).click();page.evaluate('async()=>{await ReaderOffline.download(["engwebp"]);await navigator.serviceWorker.ready}');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#v2 .main-text');open_app();saved();page.locator('button[data-source="sbl"][data-book="PHM"]').click();page.wait_for_selector('#apparatus-entries .apparatus-entry');assert 'ἀδελφῇ' in page.locator('#apparatus-entries').inner_text();assert len(calls)==1
  # An unavailable private-import database does not block saved public source books.
  page.evaluate('()=>{window.originalApparatusList=ReaderApparatus.list;ReaderApparatus.list=()=>Promise.reject(Error("TEST private import storage unavailable"))}');page.click('#apparatus-saved');page.wait_for_function('document.querySelector("#apparatus-status").textContent.startsWith("Some saved lists")');page.locator('button[data-source="sbl"][data-book="PHM"]').click();page.wait_for_selector('#apparatus-entries .apparatus-entry');assert len(calls)==1;page.evaluate('()=>{ReaderApparatus.list=window.originalApparatusList}')
  # A list entry can become stale. Clicking it must not fetch from the network.
  ctx.set_offline(False);saved();key=page.evaluate('ReaderStudyStore.list().then(rows=>rows.find(x=>x.key.startsWith("apparatus|sbl|")).key)');page.evaluate('(key)=>ReaderStudyStore.remove(key)',key);page.locator('button[data-source="sbl"][data-book="PHM"]').click();page.wait_for_function('document.querySelector("#apparatus-status").textContent.includes("not been saved")');assert len(calls)==1;assert page.locator('#apparatus-entries').count()==0
  # A subsequent explicit Load is allowed to retrieve the source again.
  page.click('#apparatus-read');page.wait_for_selector('#apparatus-entries .apparatus-entry');assert len(calls)==2;page.click('#apparatus-save');page.wait_for_function('document.querySelector("#apparatus-status").textContent.includes("saved on this device")')
  # Unknown pinned editions are listed honestly, with no Open button.
  page.evaluate('''async()=>{const d=await new Promise((resolve,reject)=>{const r=indexedDB.open('parallel-reader-study-packs-v1',1);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)});await new Promise((resolve,reject)=>{const t=d.transaction('packs','readwrite'),s=t.objectStore('packs');s.put({key:'apparatus|sbl|'+('f'.repeat(40))+'|PHM',label:'UNSUPPORTED PIN TEST',bytes:1,text:'x',sha:'0'.repeat(40)});s.put({key:'unrelated-test-pack',label:'Unrelated pack',bytes:1,text:'x',sha:'0'.repeat(40)});t.oncomplete=resolve;t.onabort=()=>reject(t.error)});d.close()}''')
  saved();old=page.locator('.apparatus-saved-row').filter(has_text='UNSUPPORTED PIN TEST');assert old.get_by_role('button',name='Open saved source').count()==0;assert 'not supported' in old.inner_text();old.get_by_role('button',name='Remove downloaded source').click();page.wait_for_function('!document.querySelector("#apparatus-saved-sources").textContent.includes("UNSUPPORTED PIN TEST")')
  row=page.locator('.apparatus-saved-row').filter(has=page.locator('button[data-source="sbl"]'));row.get_by_role('button',name='Remove downloaded source').click();page.wait_for_function('!document.querySelector("#apparatus-saved-sources").querySelector("button[data-source]")');assert len(page.evaluate('ReaderApparatus.list()'))==1;assert any(x['key']=='unrelated-test-pack' for x in page.evaluate('ReaderStudyStore.list()'))
  page.get_by_role('button',name='Remove private import',exact=True).click();page.wait_for_function('!document.querySelector("#apparatus-saved-imports").querySelector("button[data-import]")');assert len(page.evaluate('ReaderApparatus.list()'))==0;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert not errors,errors
  b.close();print('PASS: saved source/import browser, direct offline reopen after reload, stale-source no-fetch guarantee, explicit reload recovery, old-pin refusal, independent removals, first-reference navigation and filtered attributed UTF-8 export; mobile and no page errors')
finally:s.shutdown()
