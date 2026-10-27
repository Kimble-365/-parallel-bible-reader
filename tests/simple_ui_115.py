"""Browser flow for simplified menu; requires localhost sockets and Chromium."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}/releases/v1.15/'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base);page.wait_for_selector('#quick-bible');page.wait_for_selector('.main-text');assert page.locator('#compare1').input_value()=='' and page.locator('#compare2').input_value()=='' and page.locator('#compare3').input_value()=='';assert page.locator('#text-display').input_value()=='original';assert not page.locator('#primary').is_visible();assert not page.locator('#reader-settings').is_visible()
  page.get_by_role('button',name='Settings',exact=True).click();assert page.locator('#primary').is_visible();page.select_option('#primary','dan-1819');page.click('#favorite-0');page.select_option('#compare2','epo-londona');page.select_option('#compare1','engwebp');page.select_option('#compare1','');assert page.locator('#compare2').input_value()=='epo-londona';page.locator('#appearance-settings').evaluate('(e)=>e.open=true');page.select_option('#text-display','both');page.get_by_role('button',name='Back to reading',exact=True).first.click();assert not page.locator('#reader-settings').is_visible();assert '★' in page.locator('#quick-bible').inner_text();page.reload();page.wait_for_selector('#quick-bible');assert page.locator('#compare2').input_value()=='epo-londona'
  for name,selector in [('Search','#search-panel'),('Listen','#audio-panel'),('Watch','#film-panel'),('Offline','#offline-panel')]:
   page.get_by_role('button',name=name,exact=True).click();assert page.locator(selector).is_visible();page.keyboard.press('Escape');assert not page.locator('#reader-settings').is_visible()
  page.get_by_role('button',name='Notes',exact=True).first.click();assert page.locator('#notes-panel').is_visible();page.click('#notes-close');page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert not errors,errors;browser.close();print('PASS: single-text default, menu/modal/Escape, favorites, independent comparisons, persistence, notes, mobile width')
finally:s.shutdown()
