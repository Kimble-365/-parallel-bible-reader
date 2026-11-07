"""Actual Matthew 6:13 display, copy, Notes, search, PNG and offline regression."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [390,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':844},permissions=['clipboard-read','clipboard-write'],accept_downloads=True);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   base=f'http://127.0.0.1:{s.server_port}/releases/v1.28/'
   page.goto(base+'?edition=fin-kr1938&compare1=&compare2=&compare3=#MAT.6.13');page.wait_for_selector('#v13 [role=button]');page.wait_for_function('window.ReaderVerseBridge && window.ReaderVerseMedia')
   cell=page.locator('#v13 [data-slot="1"]');text=cell.inner_text();assert 'sillä sinun on valtakunta' in text and 'Amen.' in text and '&lt;' not in text and '<Fo>' not in text
   for view in ['original','latin','both']:
    page.eval_on_selector('#text-display','(e,v)=>{e.value=v;e.dispatchEvent(new Event("change"))}',view);page.wait_for_selector('#v13 [role=button]');assert '&lt;' not in page.locator('#v13').inner_text()
   cell=page.locator('#v13 [data-slot="1"]');cell.click();assert '&lt;' not in page.locator('#verse-actions-preview').inner_text()
   page.get_by_role('button',name='Copy',exact=True).click();copied=page.evaluate('navigator.clipboard.readText()');assert 'KR33/38' in copied and 'Amen.' in copied and '&lt;' not in copied
   page.evaluate("""window.drawn=[];const old=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(t,...args){drawn.push(t);return old.call(this,t,...args)}""")
   with page.expect_download() as d:page.get_by_role('button',name='Verse image',exact=True).click()
   assert Path(d.value.path()).read_bytes().startswith(b'\x89PNG');drawn=page.evaluate('drawn.join(" ")');assert 'Amen.' in drawn and '&lt;' not in drawn
   page.get_by_role('button',name='Copy to Notes',exact=True).click();assert '&lt;' not in page.locator('#notes-quotes').inner_text();assert 'valtakunta' in page.locator('#notes-quotes').inner_text();page.click('#notes-close')
   q=page.evaluate("ReaderNotebookSource.passage('MAT 6:13')");assert '&lt;' not in q['text'] and 'Amen.' in q['text']
   page.evaluate('document.querySelector("#scope").value="chapter";document.querySelector("#search").value="valtakunta";document.querySelector("#search-button").click()');page.wait_for_function('document.querySelector("#search-stop").hidden');assert '6:13' in page.locator('#results').inner_text();assert '&lt;' not in page.locator('#results').inner_text()
   page.evaluate('document.querySelector("#search").value="FO";document.querySelector("#search-button").click()');page.wait_for_function('document.querySelector("#search-stop").hidden');assert '6:13' not in page.locator('#results').inner_text()
   page.evaluate('async()=>{await ReaderOffline.download(["fin-kr1938"])}');page.evaluate('navigator.serviceWorker.register("sw.js")');page.wait_for_function('!!navigator.serviceWorker.controller');page.reload();page.wait_for_selector('#v13 [role=button]');ctx.set_offline(True);page.reload();page.wait_for_selector('#v13 [role=button]');assert '&lt;' not in page.locator('#v13').inner_text();assert not errors,errors;ctx.close()
  browser.close()
 print('PASS KR33/38: mobile/desktop display forms, attributed clipboard, Notes paths, drawn PNG, search and offline')
finally:s.shutdown()
