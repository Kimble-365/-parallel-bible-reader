"""Actual maintained 2.0 UI, gzip fallback, saved text and checksum rejection."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(R),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [390,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':844},permissions=['clipboard-read','clipboard-write']);page=ctx.new_page();page.set_default_timeout(120000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script('window.DecompressionStream=undefined');base=f'http://127.0.0.1:{s.server_port}/releases/v2.0/'
   page.goto(base+'?edition=&compare1=&compare2=fin&compare3=#JHN.3.16');page.wait_for_selector('#v16 [data-slot="3"][role=button]');assert page.locator('#primary').input_value()=='';assert page.locator('#compare2').input_value()=='fin';assert page.evaluate('BibleCatalog.editions.length')==200
   text=page.locator('#v16 [data-slot="3"]').inner_text();assert len(text)>30
   page.locator('#v16 [data-slot="3"]').click();page.get_by_role('button',name='Copy',exact=True).click();assert 'Biblica' in page.evaluate('navigator.clipboard.readText()')
   page.get_by_role('button',name='Copy to Notes',exact=True).click();assert 'Biblica' in page.locator('#notes-quotes').inner_text();page.click('#notes-close')
   # All new editions independently load a complete representative book in the actual loader.
   loaded=page.evaluate('''async()=>{const out=[];for(const e of BibleCatalog.editions.filter(e=>e.data_group==='europe-english-1.29')){const b=e.book_codes[0];const d=await ReaderOffline.loadBook(b,[e.id]);if(!d.editions[e.id]?.length)throw Error(e.id);out.push(e.id)}return out}''');assert len(loaded)==116
   page.evaluate("ReaderOffline.download(['fin'])");assert any(x['id']=='fin' for x in page.evaluate('ReaderOffline.list()'))
   page.reload();page.wait_for_selector('#v16 [data-slot="3"][role=button]');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#v16 [data-slot="3"][role=button]');assert page.locator('#v16 [data-slot="3"]').inner_text()==text;ctx.set_offline(False)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert not errors,errors;ctx.close()
  # A new context has no cached book. Wrong expanded hash must reject the new group.
  ctx=browser.new_context();page=ctx.new_page();page.goto(base+'?edition=&compare1=&compare2=&compare3=');page.wait_for_function('window.ReaderOffline&&window.EuropeanTextPacks');result=page.evaluate('''async()=>{EuropeanTextPacks.GEN.sha256='0'.repeat(64);try{await ReaderOffline.loadBook('GEN',['eng-asv']);return 'BAD'}catch(e){return e.message}}''');assert 'checksum mismatch' in result,result;ctx.close();browser.close()
 print('PASS: 390/1280px 2.0 UI; all 116 incoming edition loads; forced JS gzip fallback; attributed copy/Notes; intentional empty slots; Finnish NT saved/reopened offline; corrupt manifest rejected; no page errors')
finally:s.shutdown()
