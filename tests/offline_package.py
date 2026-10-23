"""Check the actual ZIP extracted, with all outside-network requests blocked."""
from pathlib import Path
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
from urllib.parse import urlsplit
import os
ROOT=Path(__file__).resolve().parents[1];V=os.environ.get('READER_VERSION','1.6');zpath=ROOT/'releases'/('v'+V)/('parallel-bible-reader-'+V+'.zip')
with TemporaryDirectory(dir='/workspace') as tmp:
 with ZipFile(zpath) as z:
  assert z.testzip() is None;assert 'index.html' in z.namelist();assert 'data/GEN.js' in z.namelist()
  if tuple(map(int,V.split('.'))) >= (1,3):assert 'translations/index.html' in z.namelist()
  if tuple(map(int,V.split('.'))) >= (1,5):assert 'sources/hebrew-usfm.zip' in z.namelist()
  z.extractall(tmp)
 class H(SimpleHTTPRequestHandler):
  def __init__(self,*a,**k):super().__init__(*a,directory=tmp,**k)
  def log_message(self,*a):pass
 s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}'
 try:
  with sync_playwright() as p:
   b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];failed=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:failed.append(r.url) if r.status>=400 else None);page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base) else route.abort())
   page.goto(base+'/?edition=hin2017&compare1=&compare2=engwebp&compare3=#JHN.3.16');page.wait_for_selector('#v16');assert page.locator('#v16 .translation').count()==2
   if tuple(map(int,V.split('.'))) >= (1,3):page.click('#browse-1');page.wait_for_selector('#results .entry');assert 'Finnish' in page.locator('#results').inner_text()
   if tuple(map(int,V.split('.'))) >= (1,5):
    page.goto(base+'/?edition=hbo-source&compare1=grc-source&compare2=&compare3=#GEN.1.1');page.wait_for_selector('#v1 [data-slot="1"] [dir="rtl"]')
   if tuple(map(int,V.split('.'))) >= (1,6):
    page.goto(base+'/?edition=engwebp&compare1=&compare2=&compare3=&form1=ga#JHN.3.16');page.wait_for_function("document.querySelector('#v16')?.textContent.includes('phoneme estimate')");assert '/ɡɑd/' in page.locator('#v16').inner_text()
   assert not errors,errors;assert not failed,failed;b.close();print('PASS: actual extracted '+V+' ZIP, local-only text/catalog/original languages/pronunciation assets and no failed local requests')
 finally:s.shutdown()
