"""WLC actual source typography and separate source/Latin volumes in Chromium."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
raw=ROOT/'original-documents/reference-editions/salkinson-ginsburg'
m=json.loads((raw/'IMPORT-REPORT.json').read_text())
with ZipFile(raw/'hebsg_usfm.zip') as z:
 assert all(hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256'] for f in m['raw_files'])
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [390,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':844},permissions=['clipboard-read','clipboard-write'],accept_downloads=True);page=ctx.new_page();errors=[];outside=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:outside.append(r.url) if not r.url.startswith('http://127.0.0.1:') else None)
   base=f'http://127.0.0.1:{s.server_port}/releases/v2.0/'
   page.goto(base+'?edition=&compare1=&compare2=hbo-wlc&compare3=#DEU.6.4');page.wait_for_selector('#v4 [data-slot="3"][role=button]');page.wait_for_function('window.ReaderVerseMedia')
   cell=page.locator('#v4 [data-slot="3"]');assert 'seg type' not in cell.inner_text() and 'H8085' not in cell.inner_text();assert ''.join(cell.locator('[data-source-typography="large"]').all_text_contents())=='עד'
   cell.click();page.get_by_role('button',name='Copy',exact=True).click();copied=page.evaluate('navigator.clipboard.readText()');assert 'שְׁמַ' in copied and 'seg' not in copied and 'H8085' not in copied
   page.get_by_role('button',name='Copy to Notes',exact=True).click();assert 'seg' not in page.locator('#notes-quotes').inner_text();notes=page.evaluate('localStorage.getItem("parallel-reader-notes-v1")');slots=page.evaluate('localStorage.getItem("bible-reader-reading-v1")')
   page.goto(base+'reading-volumes.html?volume=wlc-israeli&book=DEU&chapter=6');page.wait_for_selector('#verses article');assert page.locator('#volume option').count()==12;assert 'estimate' in page.locator('#notice').inner_text();assert 'Adonai' in page.locator('#verses article').filter(has=page.get_by_role('heading',name='Deuteronomy 6:4',exact=True)).inner_text()
   assert page.evaluate('localStorage.getItem("parallel-reader-notes-v1")')==notes;assert page.evaluate('localStorage.getItem("bible-reader-reading-v1")')==slots
   for volume in ['delitzsch-original','delitzsch-written','salkinson-original','salkinson-written','greek-modern','swete-modern']:
    b='GEN' if volume=='swete-modern' else 'JHN'
    page.goto(base+'reading-volumes.html?volume='+volume+'&book='+b+'&chapter=1');page.wait_for_selector('#verses article');content=page.locator('#verses article p').first.inner_text();assert len(content)>10
    if volume.endswith('original'):assert any('\u05d0'<=c<='\u05ea' for c in content)
    else:assert not any('\u05d0'<=c<='\u05ea' for c in content)
    with page.expect_download() as d:page.click('#export')
    text=Path(d.value.path()).read_text();assert '1:1' in text and content in text and 'Source:' in text;assert d.value.suggested_filename==volume+'-'+b+'.txt'
   page.goto(base+'reading-volumes.html?volume=swete-modern&book=EST&chapter=prologue');page.wait_for_selector('#verses article');assert page.locator('#chapter').input_value()=='prologue';assert 'prologue:' in page.locator('#verses article').first.inner_text()
   # Full source coverage, not just the displayed chapter, must reach each volume export.
   page.goto(base+'reading-volumes.html?volume=salkinson-written&book=JHN&chapter=1');page.wait_for_selector('#verses article')
   with page.expect_download(timeout=120000) as d:page.click('#export-volume')
   text=Path(d.value.path()).read_text();assert 'Matthew\n' in text and 'Revelation\n' in text and '22:21' in text
   page.click('#save');page.wait_for_function('document.querySelector("#status").textContent.startsWith("Source saved")');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#verses article');assert 'Not fully saved' not in page.locator('#status').inner_text();ctx.set_offline(False)
   page.locator('summary').last.click();page.fill('#private-text','λόγος αὐτός');
   with page.expect_download() as d:page.click('#private-export')
   assert 'lóghos aftós' in Path(d.value.path()).read_text();assert page.locator('aside').inner_text().find('not installed')>=0
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert not errors,errors;assert not outside,outside;ctx.close()
  browser.close()
 print('PASS Hebrew browsers: mobile/desktop Shema/copy/Notes/large letters; separate Hebrew sources/Latin/Modern Greek, source-key preservation, 27-book export, checksummed offline Salkinson, private converter and ABP external-only status; no outside requests')
finally:s.shutdown()
