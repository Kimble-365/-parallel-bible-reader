from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os
ROOT=Path(__file__).resolve().parents[1];V=os.environ.get('READER_VERSION','1.6')
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
  page.goto(base+f'/releases/v{V}/?edition=engwebp&compare1=engwebp&compare2=hin2017&compare3=&text=original#JHN.3.16');page.wait_for_selector('#v16');assert not any('english-ga.js' in u for u in requests)
  page.select_option('#form-0','ga');page.wait_for_function("document.querySelector('#v16 [data-slot=\"1\"]')?.textContent.includes('phoneme estimate')");text=page.locator('#v16 [data-slot="1"] .original').inner_text();assert '/ɡɑd/' in text;assert 'God' in page.locator('#v16 [data-slot="2"] .original').inner_text();assert any('english-ga.js' in u for u in requests);assert page.locator('#form-2').is_disabled()
  page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');page.fill('#search','ɡɑd');page.click('#search-button');page.wait_for_selector('#results .result');assert page.locator('#results .result').evaluate_all('(xs)=>xs.every(x=>x.dataset.slot==="1")')
  page.locator('#v16 .verse-share').click();assert 'form1=ga' in page.locator('#share-link').input_value();assert '/ɡɑd/' in page.locator('#share-text').input_value();page.click('#share-close');page.reload();page.wait_for_function("document.querySelector('#v16 [data-slot=\"1\"]')?.textContent.includes('phoneme estimate')")
  page.select_option('#form-0','auto');page.wait_for_function("document.querySelector('#v16 [data-slot=\"1\"] .original')?.textContent.includes('God')");assert not errors,errors;b.close();print('PASS: opt-in dictionary loading, independent source/pronunciation slots, visible-form indexed IPA search, share and state, source restoration')
finally:s.shutdown()
