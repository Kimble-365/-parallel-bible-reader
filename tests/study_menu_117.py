from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os
VERSION=os.environ.get('READER_VERSION','1.17')
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}/releases/v{VERSION}/'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base+'?edition=engwebp&compare1=&compare2=&compare3=&text=original#JHN.3.16');page.wait_for_selector('#menu-study');assert page.locator('#reader-release').inner_text()=='Reader '+VERSION;assert page.locator('#verses').get_by_text('Reader '+VERSION).count()==0
  page.click('#menu-study');page.click('#menu-history');assert 'John 3' in page.locator('#history-list').inner_text();page.keyboard.press('Escape');page.click('#menu-study');page.click('#menu-plan');assert page.locator('#plan-list li').count()==7;page.locator('#plan-list input').first.check();page.keyboard.press('Escape');page.reload();page.wait_for_selector('#menu-study');page.click('#menu-study');page.click('#menu-plan');assert page.locator('#plan-list input').first.is_checked();page.keyboard.press('Escape')
  page.click('#menu-study');page.click('#menu-present');assert page.locator('#presentation-dialog').is_visible();first=page.locator('#presentation-text').inner_text();assert first.startswith('3:1');page.keyboard.press('ArrowRight');assert page.locator('#presentation-text').inner_text()!=first;assert page.locator('#presentation-count').inner_text().startswith('2 /');page.keyboard.press('Escape');assert not page.locator('#presentation-dialog').is_visible()
  page.click('#menu-contents');assert 'not Scripture' in page.locator('#study-content').inner_text();page.select_option('#guide-book','GEN');assert 'Genesis tells' in page.locator('#guide-details').inner_text();assert page.locator('.chapter-links button').count()==50;page.keyboard.press('Escape');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.goto(base+'translations/');page.select_option('#family','Indo-European');page.select_option('#subfamily','Indo-Iranian');assert page.locator('#results a[data-edition="hin2017"]').count()==1;assert page.locator('#results a[data-edition="engwebp"]').count()==0;assert page.locator('#results a[data-edition="fin-kr1938"]').count()==0;assert 'subgroup of Indo-European' in page.locator('body').inner_text();assert not errors,errors;browser.close();print('PASS: reader version only at text start; reading history; dated plan/manual progress survives reload; presentation/keyboard/close; combined guides and chapter navigation; mobile width; Indo-Iranian subgroup filtering')
finally:s.shutdown()
