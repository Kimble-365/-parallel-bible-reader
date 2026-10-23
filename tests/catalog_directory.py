from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
from urllib.parse import urlsplit,parse_qs
import os
ROOT=Path(__file__).resolve().parents[1];VERSION=os.environ.get('READER_VERSION','1.3')
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+f'/releases/v{VERSION}/?edition=hin2017&compare1=&compare2=engwebp&compare3=#JHN.3.16');page.wait_for_selector('#v16');assert page.locator('#primary option').count()<20
  page.click('#favorite-0');assert page.locator('#favorite-0').get_attribute('aria-pressed')=='true';page.reload();page.wait_for_selector('#v16');assert page.locator('#favorite-0').get_attribute('aria-pressed')=='true'
  page.click('#browse-3');page.wait_for_selector('#results .entry');assert 'Text 4' in page.locator('#target').inner_text()
  page.fill('#find','اردو');assert page.locator('#results .entry').count()==2
  page.locator('a[data-edition="urdoucv"]').click();page.wait_for_selector('#v16');assert page.locator('#compare3').input_value()=='urdoucv';assert page.locator('#compare1').input_value()=='';assert page.locator('#compare2').input_value()=='engwebp';assert page.locator('#chapter').input_value()=='3'
  page.click('#browse-1');page.wait_for_selector('#results .entry');page.select_option('#family','Uralic');assert page.locator('#results').inner_text().find('Finnish')>=0;page.select_option('#countries','India');assert page.locator('#count').inner_text()=='0 installed editions';page.click('#reset');page.select_option('#states','Haryana');assert page.locator('#results .entry').count()==1;assert 'Haryanvi' in page.locator('#results').inner_text()
  page.click('#reset');page.fill('#find','pan');assert 'Punjabi' in page.locator('#results').inner_text();page.fill('#find','தமிழ்');assert 'Tamil' in page.locator('#results').inner_text();page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert not errors,errors
  b.close();print('PASS: popular/favorite selectors; native aliases; independent slot return and reference; combined family/country/state filters; ISO lookup and mobile catalog')
finally:s.shutdown()
