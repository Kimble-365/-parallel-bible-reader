"""PNG export/Unicode/RTL/offline and comparison without changing reading slots."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import struct
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start()
def png(download):
 data=Path(download.path()).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',data[16:24]);assert w==1080 and 540<=h<=8192;assert len(data)>3000
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [320,390,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':844},accept_downloads=True);page=ctx.new_page();errors=[];external=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:external.append(r.url) if not r.url.startswith('http://127.0.0.1:') else None)
   base=f'http://127.0.0.1:{s.server_port}/releases/v1.28/'
   page.goto(base+'?edition=engwebp&compare1=&compare2=fin-kr1938&compare3=&layout=auto#JHN.3.16');page.wait_for_selector('#v16 .translation[role=button]');page.locator('#v16 [data-slot="3"]').click();slots=page.evaluate('["primary","compare1","compare2","compare3"].map(id=>document.getElementById(id).value)')
   page.get_by_role('button',name='Compare',exact=True).click();assert page.locator('#verse-comparison section').count()==2;assert 'Text 1' in page.locator('#verse-comparison').inner_text() and 'Text 3' in page.locator('#verse-comparison').inner_text();assert 'not verified' in page.locator('#verse-comparison').inner_text();assert slots==page.evaluate('["primary","compare1","compare2","compare3"].map(id=>document.getElementById(id).value)')
   with page.expect_download() as d:page.get_by_role('button',name='Verse image',exact=True).click()
   png(d.value);assert d.value.suggested_filename.endswith('.png');page.wait_for_function('document.querySelector("#verse-actions-status").textContent.includes("PNG created")')
   page.keyboard.press('Escape');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   # Check a Hebrew source, source-specific reference and actual RTL canvas operation.
   page.goto(base+'?edition=&compare1=&compare2=hbo-wlc&compare3=&layout=auto#GEN.1.1');page.wait_for_selector('#v1 [data-slot="3"][role=button]');page.locator('#v1 [data-slot="3"]').click();assert page.locator('#verse-actions-preview').get_attribute('dir')=='rtl';page.get_by_role('button',name='Compare',exact=True).click();assert page.locator('#verse-comparison section').count()==1;assert page.locator('#primary').input_value()==''
   with page.expect_download() as d:page.get_by_role('button',name='Verse image',exact=True).click()
   png(d.value);page.keyboard.press('Escape')
   if width==390:
    page.evaluate('async()=>{await ReaderOffline.download(["hbo-wlc"])}');page.evaluate('navigator.serviceWorker.register("sw.js")');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#v1 [data-slot="3"][role=button]');page.locator('#v1 [data-slot="3"]').click()
    with page.expect_download() as d:page.get_by_role('button',name='Verse image',exact=True).click()
    png(d.value);page.get_by_role('button',name='Compare',exact=True).click();assert page.locator('#verse-comparison section').count()==1;ctx.set_offline(False)
   # Reject oversized content instead of silently truncating the image.
   result=page.evaluate('async()=>{try{await ReaderVerseMedia.image({reference:"GEN 1:1",edition:"Fixture",text:"x".repeat(12001)});return false;}catch(e){return e.message.includes("too long")}}');assert result
   # Exercise Indic/Greek/CJK Unicode with no remote fonts or services.
   assert page.evaluate('async()=>{const text="हिन्दी தமிழ் 日本語 Ἐν ἀρχῇ";const q={reference:"Unicode fixture",edition:"Test only",text, direction:"ltr"};const b=await ReaderVerseMedia.image(q);return b.type==="image/png"&&q.text===text;}')
   assert not errors,errors;assert not external,external;ctx.close()
  browser.close()
 print('PASS: downloaded PNG signature/dimensions, Unicode/RTL canvas, offline PNG/Compare, 320/390/1280px, preserved empty slots and no external requests')
finally:s.shutdown()
