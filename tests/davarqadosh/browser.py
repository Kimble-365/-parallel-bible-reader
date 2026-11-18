"""Real Chromium: verified SQLite lookup, RTL/touch, corruption, offline and parallel text."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import argparse,json,time
p=argparse.ArgumentParser();p.add_argument('--site',required=True);p.add_argument('--report');a=p.parse_args();root=Path(a.site)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=s.serve_forever,daemon=True).start();report=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [390,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':900},has_touch=width==390,service_workers='allow');page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   start=time.monotonic();page.goto(f'http://127.0.0.1:{s.server_port}/#book=GEN&chapter=1&verse=1');page.wait_for_function('window.DavarQadosh?.book?.manifest.book==="GEN"',timeout=60000);page.wait_for_selector('.word',timeout=60000)
   elapsed=time.monotonic()-start
   assert page.locator('.word').first.inner_text()=='בְּרֵאשִׁ֖ית'
   if width==390:page.locator('.word').first.tap()
   else:page.locator('.word').first.focus();page.keyboard.press('Enter')
   page.wait_for_selector('#study .token-id');assert 'Gen.1.1:1:0' in page.locator('#study').inner_text()
   assert 'Headword transliteration' in page.locator('#study').inner_text()
   assert 'Pending: this occurrence' in page.locator('#study').inner_text()
   assert page.locator('.source').first.get_attribute('dir')=='rtl'
   assert 'beginning' in page.locator('.parallel').first.inner_text().lower()
   page.select_option('#comparison','grc-swete');assert page.locator('.parallel').first.inner_text()=='ΕΝ ΑΡΧΗ ἐποίησεν ὁ θεὸς τὸν οὐρανὸν καὶ τὴν γῆν.'
   page.select_option('#comparison','hbo-mam');assert page.locator('.parallel').first.inner_text().strip()
   # Exact DOM text projection, independent of source button boundaries.
   assert page.evaluate('''()=>{const b=DavarQadosh.book;return [...document.querySelectorAll('.verse')].every(n=>n.querySelector('.source').textContent===b.verses.find(v=>v.chapter==='1'&&v.verse_label===n.dataset.verse).display_text)}''')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
   if width==1280:
    for code in ['PSA','ISA','DAN']:
     page.select_option('#book',code);page.wait_for_function('(code)=>DavarQadosh.book?.manifest.book===code',arg=code,timeout=60000);page.wait_for_selector('.word')
     page.locator('.word').first.click();assert code in page.locator('#coverage').inner_text()
    page.select_option('#chapter','2');page.wait_for_selector('[data-verse="4"] .word')
    aramaic=page.evaluate('DavarQadosh.book.tokens.find(t=>t.verse_key==="Dan.2.4"&&t.language==="arc").id')
    page.evaluate('(id)=>DavarQadosh.study(id)',aramaic);assert 'Biblical Aramaic' in page.locator('#study').inner_text()
    # Corrupt bytes are rejected even when loaded locally, leaving active text intact.
    result=page.evaluate('''async()=>{const m=DavarQadosh.book.manifest,r=await fetch('packs/'+m.book+'.wlexpack'),b=new Uint8Array(await r.arrayBuffer());b[120]^=1;try{await LexicalPackReader.open(b,m);return 'accepted'}catch(e){return e.message}}''');assert 'checksum' in result.lower(),result
    page.click('#save');page.wait_for_function('document.querySelector("#status").textContent.includes("saved offline")',timeout=60000)
    page.wait_for_function('navigator.serviceWorker.controller!==null',timeout=15000);ctx.set_offline(True);page.reload();page.wait_for_function('DavarQadosh.book?.manifest.book==="DAN"',timeout=60000);page.wait_for_selector('.word');assert page.locator('.parallel').count()>0
    ctx.set_offline(False)
   assert not errors,errors
   report.append({'width':width,'genesis_load_seconds':round(elapsed,3),'page_errors':errors});ctx.close()
  browser.close()
 if a.report:Path(a.report).write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: Chromium source text, stable occurrence lookup, dictionary state, parallel texts, RTL, keyboard/touch, four books, Aramaic, corruption rejection and saved-book offline reload',json.dumps(report))
finally:s.shutdown()
