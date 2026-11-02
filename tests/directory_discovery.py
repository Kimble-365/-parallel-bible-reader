"""Real directory interaction and offline search; no Bible payload changes."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [320,390,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{s.server_port}/releases/v1.27/translations/?slot=compare2&edition=hin2017&compare1=&compare2=engwebp&compare3=&text=both&form1=auto&reference=PSA.119.1');page.wait_for_function('document.querySelectorAll("#results .entry").length===84')
   page.fill('#find','Swedihs');assert page.locator('#results .entry').count()==0;assert page.locator('#suggestions').is_visible();assert page.locator('#suggestions button').filter(has_text='Swedish').count()==1
   candidate=page.locator('#suggestions button').filter(has_text='Swedish')
   if width==1280:candidate.focus();page.keyboard.press('Enter')
   else:candidate.click()
   assert page.locator('#find').input_value()=='Swedish';assert page.locator('#find').evaluate('(e)=>e===document.activeElement');assert page.locator('#results .entry').count()>0
   href=page.locator('a[data-edition="swe-1917"]').get_attribute('href');u=urlparse(href);q=parse_qs(u.query,keep_blank_values=True);assert q['edition']==['hin2017'] and q['compare1']==[''] and q['compare2']==['swe-1917'] and q['compare3']==[''];assert u.fragment=='PSA.119.1'
   page.select_option('#language','Finnish');page.fill('#find','Swedihs');assert page.locator('#suggestions').is_hidden();assert page.locator('#results .entry').count()==0;page.click('#reset');assert page.locator('#results .entry').count()==84
   for term in ['fin','اردو','தமிழ்','swedish 1917']:
    page.fill('#find',term);assert page.locator('#results .entry').count()>0,term
   page.fill('#find','<img src=x onerror=alert(1)>');assert page.locator('#results img').count()==0;page.click('#reset');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
   if width==390:
    page.evaluate('navigator.serviceWorker.register("../sw.js",{scope:"../"})');page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_function('document.querySelectorAll("#results .entry").length===84');page.fill('#find','Swedihs');assert page.locator('#suggestions button').filter(has_text='Swedish').count()==1;ctx.set_offline(False)
   assert not errors,errors;ctx.close()
  browser.close()
 print('PASS: 84-edition browser search, explicit suggestions/focus, combined filters, native names, exact slot/reference preservation, plain-text rendering, 320/390/1280px and offline reload')
finally:s.shutdown()
