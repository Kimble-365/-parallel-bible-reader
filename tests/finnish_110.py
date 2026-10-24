"""Real Biblia 1776 and user-provided private LLL integration, including ZIP/ONT."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import zipfile,json
ROOT=Path(__file__).resolve().parents[1];PRIVATE=Path('/workspace/reader-new-sources/LLL.zip')
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/releases/v1.10/'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=b.new_context();page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
  page.goto(url+'?edition=fin-biblia1776&compare1=fin-kr1938&compare2=&compare3=#GEN.1.1');page.wait_for_selector('#s1-v1');assert 'Alussa loi Jumala' in page.locator('#s1-v1').inner_text();assert page.evaluate('BibleCatalog.editions.length')==44;page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller')
  page.locator('#finnish-library').evaluate('(x)=>x.open=true');page.select_option('#private-slot','2');page.set_input_files('#private-file',str(PRIVATE));page.click('#private-import');page.wait_for_selector('#s3-v1',timeout=60000);assert page.locator('#compare2').input_value()=='fin-lll-local';assert 'Alussa Jumala loi taivaat ja maan.' in page.locator('#s3-v1').inner_text();assert page.evaluate('BibleCatalog.editions.length')==45
  page.goto(url+'?edition=fin-lll-local&compare1=&compare2=&compare3=#JHN.3.16');page.wait_for_selector('#s1-v16');assert 'Jumala' in page.locator('#s1-v16').inner_text();assert 'maailmaa' in page.locator('#s1-v16').inner_text()
  page.click('#browse-1');page.wait_for_selector('#results .entry');page.fill('#find','LLL');assert 'private copy' in page.locator('#results').inner_text();page.click('#back');page.wait_for_selector('#s1-v16')
  ctx.set_offline(True);page.reload();page.wait_for_selector('#s1-v16');assert 'maailmaa' in page.locator('#s1-v16').inner_text();page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');page.fill('#search','maailmaa');page.click('#search-button');page.wait_for_selector('#results .result');assert not posts,posts
  ctx.set_offline(False);raw=zipfile.ZipFile(PRIVATE).read('LLL.ont').decode('utf-8-sig');body=page.evaluate('''async text=>{const parsed=await PrivateBibleImport.parse(new File([text],'LLL.ont'), 'lll');return {books:parsed.meta.book_codes.length,first:parsed.books.GEN[0][2],last:parsed.books.REV.at(-1)[2]}}''',raw);assert body['books']==66;assert 'armo' in body['last']
  rejected=page.evaluate('''async text=>{try{await PrivateBibleImport.parse(new File([text],'wrong.ont'),'kr92');return false}catch{return true}}''',raw);assert rejected
  # The protected-format branches use synthetic fixture text, never their real copyrighted bodies.
  for edition,description in [('kr92','Kirkkoraamattu 1992'),('rk','Raamattu Kansalle 2012')]:
   meta=page.evaluate('''async input=>{const text=Array(31102).fill('Synthetic test text, not scripture.').join('\\n')+'\\ndescription='+input.description;const parsed=await PrivateBibleImport.parse(new File([text],'fixture.ont'),input.edition);await ReaderOffline.installPrivate(parsed.meta,parsed.books);return parsed.meta.id}''',dict(edition=edition,description=description));assert meta.endswith('-local')
  page.evaluate("ReaderOffline.download(['fin-biblia1776'])");assert len([x for x in page.evaluate('ReaderOffline.list()') if x['id']=='fin-biblia1776'])==78
  ctx.set_offline(True);page.goto(url+'?edition=fin-biblia1776&compare1=&compare2=&compare3=#WIS.1.1');page.wait_for_selector('#s1-v1');assert page.locator('#s1-v1').inner_text()
  assert not any(p.name.lower().startswith('lll') for p in (ROOT/'releases/v1.10').rglob('*'));assert not errors,errors;b.close();print('PASS: 1776 and KR33/38, private real LLL ZIP to Text 3, 66-book map / John 3:16 / Revelation, directory, offline reload and search, plain ONT, mismatched-edition rejection; no POST uploads')
finally:server.shutdown()
