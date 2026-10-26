"""Actual SW navigation and IndexedDB offline text persistence; real text subset."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json,os
ROOT=Path(__file__).resolve().parents[1];V=os.environ.get('READER_VERSION','1.9')
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}';url=base+'/releases/v'+V+'/'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);context=browser.new_context();page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url+'?edition=engwebp&compare1=&compare2=heb-delitzsch-historical&compare3=#JHN.3.16');page.wait_for_selector('#s3-v16');page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');assert page.evaluate('navigator.serviceWorker.controller.scriptURL').endswith('/releases/v'+V+'/sw.js');assert 'God' in page.locator('#s1-v16').inner_text();assert page.locator('#s3-v16 [dir="rtl"]').count()==1
  # Save a real chapter book for two editions. Subset is test-only: production UI downloads every book.
  page.evaluate("for(const e of BibleCatalog.editions)if(['engwebp','heb-delitzsch-historical'].includes(e.id))e.book_codes=['JHN']");page.locator('#offline-panel').evaluate('(x)=>x.open=true');page.click('#offline-save');page.wait_for_function("document.querySelector('#offline-status').textContent.includes('Selected texts are saved')")
  saved=page.evaluate('ReaderOffline.list()');assert {x['id'] for x in saved}=={'engwebp','heb-delitzsch-historical'};assert all(x['book']=='JHN' for x in saved)
  # Check other language bundles were not persisted.
  assert len(saved)==2
  page.evaluate("localStorage.setItem('bible-reader-bookmarks-v1',JSON.stringify([{edition:'engwebp',book:'JHN',chapter:3,verse:16,preview:'Test bookmark'}]))")
  context.set_offline(True);page.reload();page.wait_for_selector('#s3-v16');assert 'God' in page.locator('#s1-v16').inner_text();assert page.locator('#s3-v16 .roman').inner_text();assert page.locator('#s3-v16 [dir="rtl"]').count()==1
  page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');page.fill('#search','God');page.click('#search-button');page.wait_for_selector('#results .result')
  page.click('#browse-1');page.wait_for_selector('#results .entry');assert 'Hebrew' in page.locator('#results').inner_text();page.click('#back');page.wait_for_selector('#s1-v16')
  page.locator('#offline-panel').evaluate('(x)=>x.open=true');assert '1/66 books saved' in page.locator('#offline-saved').inner_text()
  # Offline pronunciation shell asset is precached, not dependent on an audio connection.
  page.select_option('#form-0','ga');page.wait_for_function("document.querySelector('#s1-v16')?.textContent.includes('phoneme estimate')")
  page.select_option('#primary','hin2017')
  if tuple(map(int,V.split('.'))) >= (1,12):
   page.wait_for_function("document.querySelector('.source-pane .missing')?.textContent.includes('not saved')");assert page.locator('#s3-v16 [dir="rtl"]').count()==1
  else:
   page.wait_for_function("document.querySelector('#status').textContent.includes('not saved')");assert 'not saved' in page.locator('#status').inner_text()
  context.set_offline(False);page.goto(url+'?edition=engwebp&compare1=&compare2=&compare3=#JHN.3.16');page.wait_for_selector('#v16');page.evaluate("ReaderOffline.remove('engwebp')");assert all(x['id']!='engwebp' for x in page.evaluate('ReaderOffline.list()'));assert page.evaluate("JSON.parse(localStorage.getItem('bible-reader-bookmarks-v1')).length")==1
  # Cancelling after a committed book preserves it; resuming must finish the rest.
  page.evaluate("""async()=>{const a=new AbortController();try{await ReaderOffline.download(['engwebp'],()=>a.abort(),a.signal);throw Error('unexpected completion')}catch(e){if(e.name!=='AbortError')throw e}}""")
  assert len([x for x in page.evaluate('ReaderOffline.list()') if x['id']=='engwebp'])==1
  page.locator('#offline-panel').evaluate('(x)=>x.open=true');page.click('#offline-save');page.wait_for_function("document.querySelector('#offline-status').textContent.includes('Selected texts are saved')",timeout=180000);assert len([x for x in page.evaluate('ReaderOffline.list()') if x['id']=='engwebp'])==66
  context.set_offline(True);page.goto(url+'?edition=engwebp&compare1=&compare2=&compare3=#REV.22.21');page.wait_for_selector('#v21');assert 'Jesus' in page.locator('#v21').inner_text();page.locator('#offline-panel').evaluate('(x)=>x.open=true');assert '66/66 books saved' in page.locator('#offline-saved').inner_text();assert 'Ready offline' in page.locator('#offline-saved').inner_text()
  assert page.evaluate("async v=>{const cache=await caches.open('parallel-reader-shell-'+v+'-r1');return (await cache.keys()).every(r=>!r.url.includes('/data/')&&!r.url.includes('/extra-data/'))}",V);assert not errors,errors
  blocked=browser.new_context();blocked.add_init_script("indexedDB.open=()=>{throw Error('Blocked storage')}");bp=blocked.new_page();bp.goto(url+'?edition=engwebp&compare1=&compare2=&compare3=#JHN.3.16');bp.wait_for_selector('#v16');bp.locator('#offline-panel').evaluate('(x)=>x.open=true');bp.wait_for_function("document.querySelector('#offline-status').textContent.includes('unavailable')");assert bp.locator('#offline-save').is_disabled();blocked.close();browser.close();print('PASS: real English/Hebrew saved separately; offline reload, RTL/Latin, search, directory, pronunciation; unsaved text error; removal preserves bookmarks; mid-download cancellation/resume; full 66-book English save and Revelation offline; SW scope/shell; blocked storage online fallback')
finally:server.shutdown()
