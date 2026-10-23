"""Real-source tests for native LXX numbering and Hebrew source display."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json,sqlite3
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/releases/v1.8/'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];failed=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:failed.append(r.url) if r.status>=400 else None)
  page.goto(base+'?edition=grc-swete&compare1=fra-giguet-lxx&compare2=engwebp&compare3=#PSA.9.1');page.wait_for_selector('#s1-v1');assert page.locator('.source-pane').count()==3;assert page.locator('#v1').count()==0;assert 'Independent source' in page.locator('#alignment-note').inner_text()
  page.select_option('[data-source-slot="2"]','10');page.wait_for_function("document.querySelector('[data-source-slot=\"2\"]')?.value==='10' && document.querySelector('#s2-v1 a')?.textContent.includes('10:1')");assert page.locator('[data-source-slot="1"]').input_value()=='9';assert page.locator('[data-source-slot="3"]').input_value()=='9'
  page.click('#s2-v1 .verse-share');url=page.locator('#share-link').input_value();assert 'source2=PSA.10' in url;assert 'source1=PSA.9' in url;page.goto(url);page.wait_for_selector('#s2-v1');assert page.locator('[data-source-slot="2"]').input_value()=='10';assert page.locator('[data-source-slot="1"]').input_value()=='9'
  page.goto(base+'?edition=grc-swete&compare1=&compare2=&compare3=#JOS.15.59a');page.wait_for_selector('#s1-v59a');assert '59a' in page.locator('#s1-v59a').inner_text();page.click('#s1-v59a .bookmark-toggle');page.click('#s1-v59a .verse-share');assert '#JOS.15.59a' in page.locator('#share-link').input_value();page.click('#share-close');page.click('#browse-1');page.wait_for_selector('#results .entry');assert '#JOS.15.59a' in page.locator('#back').get_attribute('href')
  page.goto(base+'?edition=grc-swete&compare1=fra-giguet-lxx&compare2=&compare3=#WIS.1.1');page.wait_for_selector('#s1-v1');assert page.locator('.source-pane').count()==2;assert page.locator('#s1-v1 .original').inner_text();assert page.locator('#s2-v1 .roman').inner_text()
  page.goto(base+'?edition=hbo-wlc&compare1=heb-delitzsch-historical&compare2=&compare3=#MAT.1.1');page.wait_for_selector('#s2-v1');assert page.locator('#s2-v1 [dir="rtl"]').count()==1;assert page.locator('#s2-v1 .roman').inner_text();assert 'not included' in page.locator('.source-pane').first.inner_text()
  page.goto(base+'?edition=ell-vamvas1850&compare1=&compare2=&compare3=#GEN.1.1');page.wait_for_selector('#s1-v1');assert page.locator('#s1-v1 .original').inner_text()
  page.goto(base+'?edition=grc-swete&compare1=&compare2=&compare3=#EST.prologue.1');page.wait_for_selector('#s1-v1');assert page.locator('[data-source-slot="1"]').input_value()=='prologue';page.goto(base+'?edition=grc-swete&compare1=&compare2=&compare3=#EST.4.1a1');page.wait_for_selector('#s1-v1a1');
  for edition,book in [('grc-swete-theodotion','DAN'),('chu-elizabeth','GEN'),('eng-thomson-partial','GEN')]:
   page.goto(base+'?edition='+edition+'&compare1=&compare2=&compare3=#'+book+'.1.1');page.wait_for_selector('#s1-v1');assert page.locator('#s1-v1 .roman').inner_text()
  assert not errors,errors;assert not failed,failed;b.close()
 print('PASS: independent source chapters, shared state, letter-suffixed references, apocryphal books, Hebrew RTL, Latin, Greek OT; no browser errors')
 c=sqlite3.connect('/workspace/biblical-encyclopedia/encyclopedia.sqlite3');assert c.execute("select count(*) from reader_source_units where verse_key='59a'").fetchone()[0]>0;assert c.execute('select count(*) from reader_search_source_units_v1').fetchone()[0]==c.execute('select count(*) from reader_source_units').fetchone()[0];print('PASS: opaque source references and complete SQLite source-unit FTS');c.close()
finally:server.shutdown()
