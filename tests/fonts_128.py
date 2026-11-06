"""Actual 1.28 font settings, script fallback, preservation and offline checks."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start()
def settings(page):
 page.get_by_role('button',name='Settings',exact=True).click()
 page.locator('#appearance-settings').evaluate('(el)=>el.open=true')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [320,390,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{s.server_port}/releases/v1.28/?edition=engwebp&compare1=&compare2=&compare3=#GEN.1.1');page.wait_for_selector('#v1 .main-text');page.wait_for_selector('#reading-font',state='attached')
   original=page.locator('#v1 .main-text').inner_text();settings(page)
   assert page.locator('#reading-font option').count()==6
   for choice in ['system','book','classic','humanist','mono','default']:
    page.select_option('#reading-font',choice)
    assert page.locator('html').get_attribute('data-reader-font')==choice
    assert page.locator('#v1 .main-text').inner_text()==original
   page.select_option('#reading-font','book');assert 'Georgia' in page.locator('#v1 .main-text').evaluate('(e)=>getComputedStyle(e).fontFamily')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert page.locator('#reading-font').evaluate('(e)=>e.labels.length===1')
   page.reload();page.wait_for_selector('#reading-font',state='attached');assert page.locator('html').get_attribute('data-reader-font')=='book'
   # Exercise script rules on exact Unicode text nodes without fetching extra corpora.
   text='בְּרֵאשִׁית Ἐν ἀρχῇ اُردُو हिन्दी தமிழ் 日本語 ܒܪܫܝܬ'
   page.evaluate('''text=>{const n=document.createElement('div');n.id='font-fixtures';for(const lang of ['he','syc','ur','ja','hi','ta']){const e=document.createElement('div');e.className='original';e.lang=lang;e.dir=['he','syc','ur'].includes(lang)?'rtl':'ltr';e.textContent=text;n.append(e);}document.querySelector('#reading').append(n);}''',text)
   for lang,font in [('he','Hebrew'),('syc','Syriac'),('ur','Arabic'),('ja','Mincho')]:
    node=page.locator(f'#font-fixtures [lang="{lang}"]');assert node.inner_text()==text;assert font in node.evaluate('(e)=>getComputedStyle(e).fontFamily')
   # Preference changes from another tab and corrupt stored values are bounded.
   page.evaluate("localStorage.setItem('bible-reader-font-v1','classic');dispatchEvent(new StorageEvent('storage',{key:'bible-reader-font-v1'}))")
   assert page.locator('html').get_attribute('data-reader-font')=='classic'
   page.evaluate("localStorage.setItem('bible-reader-font-v1','url(evil)');dispatchEvent(new StorageEvent('storage',{key:'bible-reader-font-v1'}))")
   assert page.locator('html').get_attribute('data-reader-font')=='default'
   settings(page);page.evaluate("()=>{Storage.prototype.setItem=function(){throw new DOMException('quota','QuotaExceededError')};}")
   page.select_option('#reading-font','humanist');assert 'could not save' in page.locator('#reading-font-status').inner_text();assert page.locator('html').get_attribute('data-reader-font')=='humanist'
   page.reload();page.wait_for_selector('#reading-font',state='attached')
   if width==390:
    settings(page);page.select_option('#reading-font','mono');page.get_by_role('button',name='Back to reading',exact=True).click()
    page.evaluate('navigator.serviceWorker.register("sw.js")');page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#reading-font',state='attached');assert page.locator('html').get_attribute('data-reader-font')=='mono';settings(page);page.select_option('#reading-font','system');assert 'saved' in page.locator('#reading-font-status').inner_text()
   assert not errors,errors;ctx.close()
  browser.close()
 print('PASS: 320/390/1280px real font settings, exact text preservation, script fallback, persistence, corrupt values, cross-tab updates, failed storage and offline settings')
finally:s.shutdown()
