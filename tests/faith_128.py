"""Optional resources and exact selected-verse prayer context, including offline."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
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
   ctx=browser.new_context(viewport={'width':width,'height':844},permissions=['clipboard-read','clipboard-write']);page=ctx.new_page();errors=[];outside=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:outside.append(r.url) if not r.url.startswith('http://127.0.0.1:') else None)
   base=f'http://127.0.0.1:{s.server_port}/releases/v1.28/'
   page.goto(base+'?edition=engwebp&compare1=&compare2=fin-kr1938&compare3=&layout=auto#JHN.3.16');page.wait_for_selector('#v16 [data-slot="3"][role=button]');page.wait_for_function('window.ReaderFaithLibrary');page.locator('#v16 [data-slot="3"]').click();page.get_by_role('button',name='Pray',exact=True).click();page.wait_for_selector('#faith-library[open]');assert 'KR33/38' in page.locator('#faith-verse-context').inner_text();assert 'Jumala' in page.locator('#faith-verse-context').inner_text();assert page.locator('#faith-choice').input_value()=='verse-prayer';assert page.locator('#faith-choice option').count()==14
   page.select_option('#faith-choice','healing');assert 'promises no' in page.locator('#faith-note').inner_text();page.select_option('#faith-choice','freedom');assert 'does not diagnose' in page.locator('#faith-note').inner_text();page.select_option('#faith-choice','jesus-prayer');assert 'Eastern Orthodox' in page.locator('#faith-credit').inner_text();page.get_by_role('button',name='Copy resource',exact=True).click();copied=page.evaluate('navigator.clipboard.readText()');assert 'Lord Jesus Christ' in copied and 'oca.org' in copied
   page.locator('#faith-library button').filter(has_text='Back to reading').click();assert page.locator('#primary').input_value()=='engwebp';assert page.locator('#compare1').input_value()=='';assert page.locator('#compare3').input_value()==''
   page.get_by_role('button',name='Settings',exact=True).click();page.click('#faith-open');assert page.locator('#faith-choice').input_value()=='bible';assert page.locator('#faith-verse-context').is_hidden();page.select_option('#faith-choice','salvation');assert 'gracious' in page.locator('#faith-text').inner_text();assert page.locator('#faith-references a').count()>0;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   # Scripture links close both resources and Settings while preserving all slots.
   page.locator('#faith-references a').first.click();page.wait_for_function('!document.getElementById("faith-library").open&&!document.getElementById("reader-settings").open');assert page.locator('#compare1').input_value()==''
   if width==390:
    page.evaluate('navigator.serviceWorker.register("sw.js")');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_function('window.ReaderFaithLibrary');page.get_by_role('button',name='Settings',exact=True).click();page.click('#faith-open');page.select_option('#faith-choice','restless-heart');assert 'rests in you' in page.locator('#faith-text').inner_text();page.select_option('#faith-choice','praise');assert 'Jesus Christ' in page.locator('#faith-text').inner_text();ctx.set_offline(False)
   assert not errors,errors;assert not outside,outside;ctx.close()
  # Resources remain available when all Bible slots are deliberately empty.
  ctx=browser.new_context();page=ctx.new_page();page.goto(base+'?edition=&compare1=&compare2=&compare3=');page.wait_for_function('window.ReaderFaithLibrary');page.get_by_role('button',name='Settings',exact=True).click();page.click('#faith-open');page.select_option('#faith-choice','faith');assert 'Jesus Christ' in page.locator('#faith-text').inner_text();assert page.locator('#verses .translation').count()==0;ctx.close();browser.close()
 print('PASS: 14 resources, selected Text 3 context, attributed clipboard, empty slots, source links, Scripture navigation, mobile widths and offline library')
finally:s.shutdown()
