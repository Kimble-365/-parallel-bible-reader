from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
from urllib.parse import urlsplit,parse_qs
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();page.goto(base+'/?edition=engwebp&compare1=&compare2=&compare3=&theme=blue&mode=dark#JHN.3.16');page.wait_for_selector('#v16');u=urlsplit(page.url);assert u.path.startswith('/releases/v');assert u.fragment=='JHN.3.16';assert parse_qs(u.query)['edition']==['engwebp'];assert page.locator('#primary').input_value()=='engwebp';assert 'God' in page.locator('#v16').inner_text();assert page.locator('html').get_attribute('data-theme')=='blue';assert page.locator('html').get_attribute('data-mode')=='dark'
  page.goto(base+'/legacy/?edition=engwebp&compare1=&compare2=#JHN.3.16');page.wait_for_selector('#v16');assert page.evaluate('BibleCatalog.editions.length')==27;assert 'God' in page.locator('#v16').inner_text();assert page.locator('base').get_attribute('href')=='../';b.close();print('PASS: main URL opens numbered reader with query/hash/theme intact; archived original 27-edition reader still loads shared root text assets')
finally:s.shutdown()
