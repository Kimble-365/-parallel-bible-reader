from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json,os,time,sqlite3
ROOT=Path(__file__).resolve().parents[1];V=os.environ.get('READER_VERSION','1.5')
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+f'/releases/v{V}/?edition=hbo-source&compare1=grc-source&compare2=engwebp&compare3=#GEN.1.1');page.wait_for_selector('#v1 .translation[data-slot="1"] [dir="rtl"]');assert 'רֵאשִׁ' in page.locator('#v1 [data-slot="1"]').inner_text();assert 'not included' in page.locator('#v1 [data-slot="2"]').inner_text();assert page.locator('#v1 [data-slot="1"] .roman').inner_text()
  page.select_option('#book','JHN');page.wait_for_function("document.querySelector('#v1 [data-slot=\"2\"]')?.textContent.includes('λόγος')");assert page.locator('#v1 [data-slot="2"] .roman').inner_text();assert 'not included' in page.locator('#v1 [data-slot="1"]').inner_text()
  page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');page.fill('#search','λόγος');start=time.monotonic();page.click('#search-button');page.wait_for_selector('#results .result[data-edition="grc-source"]');elapsed=time.monotonic()-start;assert page.evaluate('searchIndexes.size')>0
  count=page.locator('#results .result').count();page.click('#search-button');page.wait_for_selector('#results .result');assert page.locator('#results .result').count()==count
  page.click('#browse-3');page.wait_for_selector('#results .entry');page.fill('#find','עברית');assert page.locator('#results .entry').count()==1;page.fill('#find','grc');assert page.locator('#results .entry').count()==1
  assert not errors,errors;b.close();print('PASS: Hebrew/Greek source scripts and Latin, coverage gaps, original-language alias search, indexed Greek query; first chapter search %.3fs'%elapsed)
 db=sqlite3.connect('/workspace/biblical-encyclopedia/encyclopedia.sqlite3');assert db.execute('select count(*) from reader_source_usfm').fetchone()[0]==66;assert db.execute('select count(*) from reader_search_originals_v1').fetchone()[0]==31103;assert db.execute("select count(*) from reader_search_originals_v1 where reader_search_originals_v1 match 'λόγος'").fetchone()[0]>0;db.close();print('PASS: 66 preserved raw USFM books and 31,103 indexed source verse records')
finally:s.shutdown()
