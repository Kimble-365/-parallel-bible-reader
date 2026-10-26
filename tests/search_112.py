"""Search regressions: real text, persistent index, incomplete offline scope and paging."""
import os
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/releases/v{os.environ.get("READER_VERSION","1.12")}/'
def run(page,q):
 page.fill('#search',q);page.click('#search-button');page.wait_for_function("document.querySelector('#search-stop').hidden && document.querySelector('#results > p')?.textContent.includes('searched')",timeout=60000)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=browser.new_context();page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url+'?edition=engwebp&compare1=&compare2=&compare3=#JHN.3.16');page.wait_for_selector('#v16');assert page.locator('#scope').input_value()=='all';page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');run(page,'God world');assert page.locator('#results .result').filter(has_text='JHN 3:16').count()==1;run(page,'he');assert page.locator('#results .result').count()>0
  page.select_option('#scope','book');run(page,'the');assert page.locator('#results .result').count()==100;page.get_by_role('button',name='Show next 100 results').click();assert page.locator('#results .result').count()==200;assert 'showing 200' in page.locator('#results > p').inner_text();assert page.evaluate('ReaderSearch.metrics.built')>0
  page.reload();page.wait_for_selector('#v16');page.locator('#search-panel').evaluate('(x)=>x.open=true');run(page,'world');assert page.evaluate('ReaderSearch.metrics.persistentHits')>0;assert page.evaluate('ReaderSearch.metrics.built')==0
  # A warm public index must avoid book payload reads, not merely rebuild faster.
  page.evaluate("window.debugSigs=[];window.p0=ReaderSearch.prepare;ReaderSearch.prepare=(args)=>p0(args).then(x=>{debugSigs.push({key:args.key,hash:x.hash,expected:ReaderSearchManifest.editions[args.edition]?.[args.key.split('|')[0]]});return x});BibleCatalog.editions.find(e=>e.id==='engwebp').book_codes=['GEN','JHN']");page.select_option('#scope','all');run(page,'God world')
  page.evaluate("window.originalBookLoader=ReaderOffline.loadBook;window.searchPayloadReads=0;window.searchTrace=[];ReaderOffline.loadBook=(...args)=>{searchPayloadReads++;searchTrace.push({book:args[0],ids:args[1],stack:new Error().stack});return originalBookLoader(...args)};void 0");run(page,'God');assert page.evaluate('searchPayloadReads')==0, page.evaluate("({reads:searchPayloadReads,metrics:ReaderSearch.metrics,fingerprints:debugSigs,trace:searchTrace})");page.evaluate('ReaderOffline.loadBook=originalBookLoader;void 0')
  # Save only John, then reproduce the previous failure: Genesis must not stop the search.
  page.evaluate("async()=>{BibleCatalog.editions.find(e=>e.id==='engwebp').book_codes=['JHN'];await ReaderOffline.download(['engwebp'])}");page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#v16');page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','all');run(page,'God');assert 'Incomplete' in page.locator('#results > p').inner_text();assert '66/66' in page.locator('#results > p').inner_text();assert page.locator('#results .result').filter(has_text='JHN 3:16').count()==1
  page.select_option('#scope','saved');run(page,'God');assert page.locator('#results > p').inner_text().startswith('Complete');assert '1/1' in page.locator('#results > p').inner_text()
  page.evaluate("localStorage.setItem('search-test-marker','keep')");before=len(page.evaluate('ReaderOffline.list()'));page.get_by_text('Search help',exact=True).click();page.click('#search-clear-index');page.wait_for_function("document.querySelector('#search-index-status').textContent.includes('cleared')");assert len(page.evaluate('ReaderOffline.list()'))==before;assert page.evaluate("localStorage.getItem('search-test-marker')")=='keep'
  ctx.set_offline(False);page.goto(url+'?edition=grc-source&compare1=&compare2=&compare3=&text=original#JHN.1.1');page.wait_for_selector('#v1');page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');run(page,'λογος');assert page.locator('#results .result[data-book="JHN"][data-chapter="1"][data-verse="1"]').count()==1;page.check('#search-exact-marks');run(page,'λογος');assert page.locator('#results .result[data-book="JHN"][data-chapter="1"][data-verse="1"]').count()==0
  # Exact same edition/form in two slots produces one entry per verse with both slot labels.
  page.goto(url+'?edition=engwebp&compare1=engwebp&compare2=&compare3=#JHN.3.16');page.wait_for_selector('#v16');page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');run(page,'God world');hit=page.locator('#results .result').filter(has_text='JHN 3:16');assert hit.count()==1;assert 'Text 1, 2' in hit.inner_text();hit.click();page.wait_for_selector('#v16')
  # Clear stale results when the query changes; do not display hits for an old query.
  page.fill('#search','other query');assert page.locator('#results .result').count()==0
  # Stop an in-flight network search; keep an honest stopped state and recover.
  held=[]
  page.evaluate('ReaderSearch.clearAll()');page.route('**/data/*.js?*',lambda route:held.append(route));page.select_option('#scope','all');page.fill('#search','God')
  with page.expect_request('**/data/GEN.js?*'):page.click('#search-button')
  page.click('#search-stop');page.wait_for_function("document.querySelector('#results > p')?.textContent.startsWith('Stopped')");page.unroute('**/data/*.js?*')
  for route in held:
   try:route.abort()
   except Exception:pass
  # One unavailable comparison must not hide the readable text or prevent opening a hit.
  page.evaluate('ReaderSearch.clearAll()');page.route('**/v1.8/extra-data/JHN.js*',lambda route:route.abort());page.goto(url+'?edition=engwebp&compare1=grc-source&compare2=&compare3=#JHN.3.16');page.wait_for_selector('#v16');assert 'God' in page.locator('#v16 [data-slot="1"]').inner_text();assert page.locator('#v16 [data-slot="2"] .missing').count()==1
  page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');run(page,'God world');assert 'Incomplete' in page.locator('#results > p').inner_text();page.locator('#results .result[data-verse="16"]').click();page.wait_for_selector('#v16 [data-slot="1"]');assert 'God' in page.locator('#v16 [data-slot="1"]').inner_text();assert not errors,errors;browser.close();print('PASS: all-word/short search, >100 paging, persistent warm index, prior offline fail-fast regression, saved-only scope, safe cache clearing, Greek marks/exact option, duplicate slot merging, result opening and input invalidation')
finally:server.shutdown()
