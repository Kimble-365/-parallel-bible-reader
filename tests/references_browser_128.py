"""Actual browser checks for reference editions, navigation, source view and offline."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import os,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/releases/v1.28/'
report={};out=Path(os.environ.get('REFERENCE_TEST_OUTPUT',str(ROOT/'test-results/references-1.28')));out.mkdir(parents=True,exist_ok=True)
try:
 with sync_playwright() as p:
  print('PLAYWRIGHT READY',flush=True)
  exe=os.environ.get('CHROMIUM_EXECUTABLE')
  browser=p.chromium.launch(**({'executable_path':exe} if exe else {}),args=['--no-sandbox'])
  for width in [390,1280]:
   print('VIEWPORT',width,flush=True)
   ctx=browser.new_context(viewport={'width':width,'height':900},accept_downloads=True);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(base+'?edition=fin-study-v005&compare1=fin-study-notes-v005&compare2=tsk-crosswire&compare3=&layout=source&text=original#GEN.1.1')
   print('PAGE OPENED',flush=True)
   page.wait_for_selector('#s3-v1 .reference-links',timeout=60000);page.wait_for_selector('#top-menu');page.wait_for_function('window.ReaderLayoutReady&&document.querySelector("#reader-release")?.textContent==="Reader 1.28"')
   assert page.locator('#verses .source-pane').count()==3
   assert 'Alussa Jumala loi' in page.locator('#s1-v1').inner_text()
   assert 'Alun voi kääntää myös' in page.locator('#s2-v1').inner_text()
   assert page.locator('#s2-v1 a[data-reference-target="JHN.1.1"]').count()==1
   assert page.locator('#s3-v1 a[data-reference-target="JHN.1.1"]').count()>=1
   assert 'KJV' in page.locator('#s3-v1').inner_text()
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
   page.screenshot(path=str(out/f'references-{width}.png'),full_page=False)
   page.locator('#s3-v1 a[data-reference-target="JHN.1.1"]').first.click()
   page.wait_for_selector('#s3-v1 .reference-links');page.wait_for_function('document.querySelector("#book").value==="JHN"')
   assert 'JHN' in page.locator('#heading').inner_text() or 'John' in page.locator('#heading').inner_text()
   # Old slots/None remain independently selectable. Source and aligned rendering both work.
   page.select_option('#alignment-mode','auto',force=True);page.dispatch_event('#alignment-mode','change');page.wait_for_selector('#v1 .reference-links')
   assert page.locator('#v1 .translation').count()==3
   page.evaluate("document.querySelector('#compare2').value='';document.querySelector('#compare2').dispatchEvent(new Event('change'))")
   page.wait_for_function('document.querySelectorAll("#v1 .translation").length===2')
   # Save complete selected data using the actual IndexedDB loader, then reopen without network.
   result=page.evaluate("""async()=>{let progress;await ReaderOffline.download(['fin-study-v005','fin-study-notes-v005','tsk-crosswire'],p=>progress=p);return {progress,items:(await ReaderOffline.list()).filter(x=>['fin-study-v005','fin-study-notes-v005','tsk-crosswire'].includes(x.id)).length}}""")
   print('SAVED',result,flush=True)
   assert result['items']==198,result
   page.wait_for_function('navigator.serviceWorker.controller!==null',timeout=60000)
   ctx.set_offline(True)
   page.goto(base+'?edition=fin-study-v005&compare1=fin-study-notes-v005&compare2=tsk-crosswire&compare3=&layout=source#PSA.23.1')
   page.wait_for_selector('#s3-v1 .reference-links',timeout=60000)
   assert 'TSK' in page.locator('#s3-v1').inner_text()
   saved=page.evaluate("async()=>{const d=await ReaderOffline.loadBook('REV',['tsk-crosswire'],{savedOnly:true});return d.editions['tsk-crosswire'].length}")
   assert saved==404
   assert not errors,errors
   report[str(width)]={'three_independent_panes':True,'clickable_finnish_and_tsk_refs':True,'aligned_cells':True,'none_slot_preserved':True,'offline_saved_items':198,'offline_reopen_and_last_book':True,'page_errors':errors}
   ctx.close()
  ctx=browser.new_context();page=ctx.new_page()
  broken=bytearray((ROOT/'releases/v1.28/study-data/GEN.json').read_bytes());broken[20]^=1
  page.route('**/study-data/GEN.json?*',lambda route:route.fulfill(body=bytes(broken),content_type='application/json'))
  page.goto(base+'?edition=tsk-crosswire&compare1=&compare2=&compare3=#GEN.1.1')
  page.wait_for_function('document.querySelector("#reading-feedback").textContent.includes("No selected text could be loaded")',timeout=60000)
  result=page.evaluate("async()=>{const d=await ReaderOffline.loadBook('GEN',['tsk-crosswire'],{partial:true});return {ids:Object.keys(d.editions),reason:d.unavailable[0]?.reason}}")
  assert result['ids']==[] and 'checksum mismatch' in result['reason'],result
  ctx.close();report['tampered_pack_rejected']=True
  browser.close()
 (out/'browser-validation.json').write_text(json.dumps({'status':'PASS','viewports':report},indent=2),encoding='utf-8');print('PASS: reference browser, navigation, 390/1280 layout, 198 saved book-editions and offline reopening')
finally:server.shutdown()
