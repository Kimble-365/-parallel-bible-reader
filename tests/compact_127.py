"""Compact sticky reader controls and the actual source-report register."""
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
  for width in [320,390,768,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':844},accept_downloads=True);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{s.server_port}/releases/v1.27/?edition=engwebp&compare1=&compare2=&compare3=&text=original#GEN.1.1');page.wait_for_selector('#v1 .main-text');page.wait_for_selector('#menu-study');page.wait_for_function('window.ReaderApparatusUI')
   assert page.locator('#top-menu #chapter-navigation #prev').count()==1
   assert page.locator('#top-menu #chapter-navigation #next').count()==1
   assert page.locator('#reading #book,#reading #chapter,#reading #prev,#reading #next').count()==0
   assert page.locator('#reader-menu-actions #menu-study').count()==1
   boxes=page.locator('#reader-menu-actions > *').evaluate_all('(nodes)=>nodes.map(n=>n.getBoundingClientRect().top)');assert max(boxes)-min(boxes)<2
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
   height=page.locator('#top-menu').bounding_box()['height'];assert height<155,(width,height)
   page.evaluate('scrollTo(0,600)');assert abs(page.locator('#top-menu').bounding_box()['y'])<2
   page.locator('#next').click();page.wait_for_function('document.querySelector("#chapter").value==="2"');page.locator('#prev').click();page.wait_for_function('document.querySelector("#chapter").value==="1"')
   if width==390:
    page.route('https://raw.githubusercontent.com/Kimble-365/-parallel-bible-reader/**/releases/v1.27/lxxl-source-register.jsonl',lambda r:r.fulfill(body=(ROOT/'releases/v1.27/lxxl-source-register.jsonl').read_bytes(),headers={'Access-Control-Allow-Origin':'*'}))
    page.locator('#menu-study').click();page.locator('#menu-apparatus').click();page.wait_for_function('!document.querySelector("#apparatus-family").disabled');page.select_option('#apparatus-family','lxx');page.click('#apparatus-read');page.wait_for_function('document.querySelector("#apparatus-count")?.textContent.startsWith("8 matching")');page.select_option('#apparatus-kind','edition_report');assert page.locator('.apparatus-entry').count()==5
    page.select_option('#apparatus-witness','q*');assert page.locator('.apparatus-entry').count()==1;assert 'Not independently encoded (null)' in page.locator('#apparatus-entries').inner_text()
    with page.expect_download() as d:page.click('#apparatus-export-text')
    assert 'q*' in Path(d.value.path()).read_text();page.click('#apparatus-save');page.wait_for_function('document.querySelector("#apparatus-status").textContent.includes("saved on this device")');page.click('#apparatus-saved');page.wait_for_selector('button[data-source="lxxl"]');ctx.set_offline(True);page.click('button[data-source="lxxl"]');page.wait_for_function('document.querySelector("#apparatus-count")?.textContent.startsWith("8 matching")');ctx.set_offline(False)
   if width==1280:
    page.goto(f'http://127.0.0.1:{s.server_port}/releases/v1.27/?edition=fin-kr1938&compare1=engwebp&compare2=&compare3=&text=original#PSA.5.3');page.wait_for_selector('#v3 .main-text');page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))');quote=page.evaluate('ReaderNotebookSource.passage(null,"reference")');assert 'Kuuntele' in quote['text'] and quote['reference'].endswith('5:3'),quote
    assert page.evaluate('ReaderStateUrl()').endswith('#PSA.5.3')
   assert not errors,errors;ctx.close()
  browser.close()
 print('PASS: compact single-row tools at 320/390/768/1280px, sticky header, grouped navigation, real LXXL filters/export and saved-only offline reopening')
finally:s.shutdown()
