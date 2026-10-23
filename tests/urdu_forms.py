from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
from urllib.parse import urlsplit,parse_qs
import os
ROOT=Path(__file__).resolve().parents[1];V=os.environ.get('READER_VERSION','1.4')
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+f'/releases/v{V}/?edition=urdoucv&compare1=urdoucv&compare2=urd&compare3=&form1=deva&form2=auto&form3=arab&text=original#JHN.3.16');page.wait_for_selector('#v16')
  assert page.locator('#v16 [data-slot="1"] .original').get_attribute('dir')=='ltr'
  assert page.locator('#v16 [data-slot="2"] .original').get_attribute('dir')=='rtl'
  assert page.locator('#v16 [data-slot="3"] .original').get_attribute('dir')=='rtl'
  first=page.locator('#v16 [data-slot="1"] .original').inner_text();second=page.locator('#v16 [data-slot="2"] .original').inner_text();assert first!=second
  assert 'Not pronunciation' in page.locator('#v16 [data-slot="1"]').inner_text()
  assert page.evaluate("window.BibleBooks.JHN.editions.urdoucv.find(r=>r[0]===3&&r[1]===16)[2]")==second
  page.locator('#v16 .verse-share').click();link=page.locator('#share-link').input_value();params=parse_qs(urlsplit(link).query);assert params['form1']==['deva'] and params['form3']==['arab'];page.click('#share-close')
  page.click('#browse-3');page.wait_for_selector('#results .entry');page.fill('#find','English');page.locator('a[data-edition="engwebp"]').click();page.wait_for_selector('#v16');assert page.locator('#form-0').input_value()=='deva' and page.locator('#form-2').input_value()=='arab'
  assert page.locator('#form-3').is_disabled();assert not errors,errors;b.close()
  print('PASS: independent Urdu script forms for repeated editions, RTL/LTR, unchanged source, uncertainty notice, share URLs and directory state retention')
finally:s.shutdown()
