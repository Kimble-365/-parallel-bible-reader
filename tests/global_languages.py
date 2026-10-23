from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json,os,sqlite3
ROOT=Path(__file__).resolve().parents[1];V=os.environ.get('READER_VERSION','1.7')
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+f'/releases/v{V}/?edition=fra-lsg1910&compare1=spa-rv1909&compare2=rus-synodal&compare3=cmn-cuv-hant#JHN.3.16');page.wait_for_selector('#v16 [data-slot="4"] .original');assert page.evaluate('BibleCatalog.editions.length')==35;assert 'Dieu' in page.locator('#v16 [data-slot="1"]').inner_text();assert 'Dios' in page.locator('#v16 [data-slot="2"]').inner_text();assert 'Бог' in page.locator('#v16 [data-slot="3"]').inner_text();assert '神' in page.locator('#v16 [data-slot="4"]').inner_text()
  page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');page.fill('#search','神');page.click('#search-button');page.wait_for_selector('#results .result');assert page.locator('#results .result').evaluate_all('(xs)=>xs.every(x=>x.dataset.edition==="cmn-cuv-hant")')
  page.goto(base+f'/releases/v{V}/?edition=arb-vandyck&compare1=bis-obbr&compare2=&compare3=#ZEC.4.10');page.wait_for_selector('#v10');assert page.locator('#v10 [data-slot="1"] [dir="rtl"]').count()==1;assert 'Combined 2 source units' in page.locator('#v10 [data-slot="2"]').inner_text()
  page.click('#browse-2');page.wait_for_selector('#results .entry');page.select_option('#continents','Australasia');assert 'Bislama' in page.locator('#results').inner_text();page.click('#reset');page.select_option('#countries','Russia');assert 'Russian' in page.locator('#results').inner_text();page.select_option('#family','Uralic');assert page.locator('#count').inner_text()=='0 installed editions';assert not errors,errors;b.close();print('PASS: 35 editions, real French Spanish Russian Chinese and Arabic/Bislama; single-Han indexed search; duplicate-unit notice; Australasia/Russia filters')
 c=sqlite3.connect('/workspace/biblical-encyclopedia/encyclopedia.sqlite3');assert c.execute('select count(*) from reader_search_all_v1').fetchone()[0]==778240;assert c.execute("select count(*) from reader_search_all_v1 where reader_search_all_v1 match 'Dieu'").fetchone()[0]>0;c.close();print('PASS: authoring FTS indexes all 778,240 installed verse records')
finally:s.shutdown()
