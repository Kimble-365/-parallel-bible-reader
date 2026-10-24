"""New native Uralic texts, exact partial scope, offline corpus and 1.10 private continuity."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}';url=origin+'/releases/v1.11/'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=b.new_context();page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url+'?edition=hun-karoli1908&compare1=ekk-pkp-partial&compare2=fin-biblia1776&compare3=#JHN.3.16');page.wait_for_selector('#s3-v16');assert 'világot' in page.locator('#s1-v16').inner_text();assert 'Jumal' in page.locator('#s2-v16').inner_text();assert page.evaluate('BibleCatalog.editions.length')==46;assert len(page.evaluate("BibleCatalog.editions.find(e=>e.id==='ekk-pkp-partial').book_codes"))==5
  page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');page.locator('#uralic-library').evaluate('(x)=>x.open=true')
  with page.expect_download() as pending:page.locator('a[href="sources/hun-karoli1908-display-usfm.zip"]').click()
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'source.zip';pending.value.save_as(path);assert zipfile.is_zipfile(path);assert zipfile.ZipFile(path).testzip() is None
  page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');page.fill('#search','világot');page.click('#search-button');page.wait_for_selector('#results .result');assert page.locator('#results .result').evaluate_all("xs=>xs.every(x=>x.dataset.edition==='hun-karoli1908')")
  page.goto(url+'?edition=ekk-pkp-partial&compare1=hun-karoli1908&compare2=&compare3=#GEN.1.1');page.wait_for_selector('#s2-v1');assert 'not included' in page.locator('.source-pane').first.inner_text()
  page.click('#browse-1');page.wait_for_selector('#results .entry');page.select_option('#family','Uralic');assert 'Hungarian' in page.locator('#results').inner_text();assert 'Estonian' in page.locator('#results').inner_text();assert 'Biblia 1776' in page.locator('#results').inner_text();assert 'KR33/38' in page.locator('#results').inner_text()
  page.goto(url+'?edition=hun-karoli1908&compare1=ekk-pkp-partial&compare2=&compare3=#JHN.3.16');page.wait_for_selector('#s1-v16');page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');page.evaluate("ReaderOffline.download(['hun-karoli1908','ekk-pkp-partial'])");saved=page.evaluate('ReaderOffline.list()');assert sum(x['id']=='hun-karoli1908' for x in saved)==66;assert sum(x['id']=='ekk-pkp-partial' for x in saved)==5
  ctx.set_offline(True);page.reload();page.wait_for_selector('#s2-v16');assert 'világot' in page.locator('#s1-v16').inner_text();assert 'Jumal' in page.locator('#s2-v16').inner_text();ctx.set_offline(False)
  # Use the exact same origin and a real old-version import to prove continuity.
  page.goto(origin+'/releases/v1.10/?edition=engwebp&compare1=&compare2=&compare3=#GEN.1.1');page.wait_for_selector('#v1');page.locator('#finnish-library').evaluate('(x)=>x.open=true');page.set_input_files('#private-file','/workspace/reader-new-sources/LLL.zip');page.click('#private-import');page.wait_for_selector('#s1-v1',timeout=60000);assert page.locator('#primary').input_value()=='fin-lll-local'
  page.goto(url+'?edition=fin-lll-local&compare1=hun-karoli1908&compare2=&compare3=#JHN.3.16');page.wait_for_selector('#s2-v16');assert 'maailmaa' in page.locator('#s1-v16').inner_text();assert 'világot' in page.locator('#s2-v16').inner_text();assert page.evaluate('BibleCatalog.editions.length')==47
  ctx.set_offline(True);page.reload();page.wait_for_selector('#s1-v16');assert 'maailmaa' in page.locator('#s1-v16').inner_text();assert not errors,errors;b.close();print('PASS: 46 public editions, Hungarian/Estonian/Finnish native text, accent search, Uralic directory, explicit 5-book coverage, 66+5 offline save/reload, real 1.10 private LLL retained in 1.11 without reimport')
finally:server.shutdown()
