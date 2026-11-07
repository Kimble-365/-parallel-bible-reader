"""Verse-specific actions, note/store preservation and offline UI."""
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
   ctx=browser.new_context(viewport={'width':width,'height':844},permissions=['clipboard-read','clipboard-write']);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   base=f'http://127.0.0.1:{s.server_port}/releases/v1.28/'
   page.goto(base+'?edition=engwebp&compare1=&compare2=fin-kr1938&compare3=#JHN.3.16');page.wait_for_selector('#v16 .translation[role=button]')
   assert page.locator('#verses .verse-gutter button').count()==0
   cell=page.locator('#v16 [data-slot="3"]');cell.focus();page.keyboard.press('Enter');page.wait_for_selector('#verse-actions[open]');assert 'KR33/38' in page.locator('#verse-actions-edition').inner_text()
   assert '3:16' in page.locator('#verse-actions-title').inner_text()
   page.get_by_role('button',name='Copy',exact=True).click();copied=page.evaluate('navigator.clipboard.readText()');assert 'KR33/38' in copied and '3:16' in copied and 'Jumala' in copied
   page.get_by_role('button',name='Blue',exact=True).click();assert cell.get_attribute('data-highlight')=='blue'
   page.get_by_role('button',name='Bookmark',exact=True).click();assert page.get_by_role('button',name='Remove bookmark',exact=True).get_attribute('aria-pressed')=='true'
   page.get_by_role('button',name='Copy to Notes',exact=True).click();page.wait_for_selector('#notes-panel:not([hidden])');assert 'KR33/38' in page.locator('#notes-quotes').inner_text();assert 'Jumala' in page.locator('#notes-quotes').inner_text()
   saved=page.evaluate("JSON.parse(localStorage.getItem('parallel-reader-notes-v1'))");assert len(saved)==1 and saved[0]['quotes'][0]['editionId']=='fin-kr1938'
   page.click('#notes-close');page.reload();page.wait_for_selector('#v16 .translation[role=button]');cell=page.locator('#v16 [data-slot="3"]');assert cell.get_attribute('data-highlight')=='blue'
   # Selecting text must not open the action sheet.
   cell.evaluate('e=>{const r=document.createRange();r.selectNodeContents(e);getSelection().removeAllRanges();getSelection().addRange(r);}');cell.dispatch_event('click');assert not page.locator('#verse-actions').evaluate('(e)=>e.open');page.evaluate('getSelection().removeAllRanges()')
   cell.click();page.get_by_role('button',name='Remove highlight',exact=True).click();assert cell.get_attribute('data-highlight') is None
   page.get_by_role('button',name='Share',exact=True).click();page.wait_for_selector('#share-dialog[open]');assert 'KR33/38' in page.locator('#share-edition').inner_text();assert 'compare1=&' in page.locator('#share-link').input_value();page.click('#share-close')
   # Independent source chapters use the clicked edition/slot, not Text 1.
   page.get_by_role('button',name='Settings',exact=True).click();page.locator('#appearance-settings').evaluate('(e)=>e.open=true');page.select_option('#alignment-mode','source');page.get_by_role('button',name='Back to reading',exact=True).first.click();page.wait_for_selector('#s3-v16 .translation[role=button]');page.locator('#s3-v16 .translation').click();assert 'KR33/38' in page.locator('#verse-actions-edition').inner_text();page.keyboard.press('Escape')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   if width==390:
    page.evaluate('async()=>{await ReaderOffline.download(["engwebp","fin-kr1938"])}');page.evaluate('navigator.serviceWorker.register("sw.js")');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#s3-v16 .translation[role=button]');page.locator('#s3-v16 .translation').click();page.get_by_role('button',name='Pink',exact=True).click();assert 'saved' in page.locator('#verse-actions-status').inner_text();ctx.set_offline(False)
   # Failed writes do not falsely show a saved highlight or destroy notes.
   if not page.locator('#verse-actions').evaluate('(e)=>e.open'):page.locator('#s3-v16 .translation').click()
   before=page.evaluate("localStorage.getItem('parallel-reader-notes-v1')");page.evaluate("()=>{Storage.prototype.setItem=function(){throw new DOMException('quota','QuotaExceededError')};}");page.get_by_role('button',name='Green',exact=True).click();assert 'not saved' in page.locator('#verse-actions-status').inner_text();assert page.evaluate("localStorage.getItem('parallel-reader-notes-v1')")==before
   page.goto(base+'?edition=&compare1=&compare2=fin-kr1938&compare3=#JHN.3.16');page.wait_for_selector('#v16 [data-slot="3"][role=button]');page.locator('#v16 [data-slot="3"]').click();page.get_by_role('button',name='Copy to Notes',exact=True).click();assert 'KR33/38' in page.locator('#notes-quotes').inner_text();assert page.locator('#primary').input_value()==''
   assert not errors,errors;ctx.close()
  browser.close()
 print('PASS: verse-specific clipboard/Notes/bookmarks/highlights, selection, keyboard, source mode, empty slot preservation, storage failure and mobile/offline behavior')
finally:s.shutdown()
