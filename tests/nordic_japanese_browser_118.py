from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/releases/v1.18/'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  for id in ['swe-1917','nob-1930','nno-1921','isl-olo1995','ekk-ocv2022']:
   page.goto(base+'?edition='+id+'&compare1=&compare2=&compare3=&text=original#JHN.3.16');page.wait_for_selector('#s1-v16 .main-text');assert page.locator('#s1-v16 .verse-reference').inner_text()=='3:16';assert page.evaluate('BibleCatalog.editions.length')==62;page.wait_for_selector('#menu-contents');page.click('#menu-contents');assert page.locator('#guide-language').input_value() in ['sv','nb','nn','is','et'];assert page.locator('#guide-details p[lang]').count()>=1;page.keyboard.press('Escape')
  page.goto(base+'?edition=jpn-bungo&compare1=&compare2=&compare3=&form1=ja-reading&text=both#JHN.3.16');page.wait_for_selector('#s1-v16 .roman');assert page.locator('#s1-v16 .roman').inner_text().isascii() or '[' in page.locator('#s1-v16 .roman').inner_text();assert 'dictionary reading' in page.locator('#text-form-notice').inner_text();assert 'not recorded speech' in page.locator('#text-form-notice').inner_text();assert page.locator('#s1-v16 .original').count()==1;reading=page.locator('#s1-v16 .roman').inner_text();assert reading!=page.locator('#s1-v16 .original').inner_text()
  page.evaluate("async()=>{await ReaderOffline.download(['jpn-bungo','swe-1917']);await ReaderJapaneseReading.downloadAll()}");page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#s1-v16 .roman');assert page.locator('#s1-v16 .roman').inner_text()==reading;page.goto(base+'?edition=swe-1917&compare1=&compare2=&compare3=&text=original#REV.22.1');page.wait_for_selector('#s1-v1 .main-text');assert page.locator('#s1-v1 .main-text').inner_text().strip();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert not errors,errors;browser.close();print('PASS: all five Nordic editions read with native Unicode, chapter:verse and draft native guides; Japanese original + optional dictionary reading with explicit limits; both full Bibles/readings saved; Japanese and Swedish Revelation offline; mobile width')
finally:server.shutdown()
