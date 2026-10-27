"""Actual mobile layout, native Finnish verse labels, copy/share and offline shell."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}/releases/v1.16/'
def copy(page,selector):
 return page.evaluate('''sel=>{const n=document.querySelector(sel),r=document.createRange();r.selectNodeContents(n);const selection=getSelection();selection.removeAllRanges();selection.addRange(r);const data=new DataTransfer(),event=new ClipboardEvent('copy',{clipboardData:data,bubbles:true,cancelable:true});n.dispatchEvent(event);return {text:data.getData('text/plain'),handled:event.defaultPrevented}}''',selector)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+'?edition=fin-kr1938&compare1=&compare2=&compare3=&text=original#PSA.5.1');page.wait_for_selector('#v1 .verse-line');page.wait_for_function("typeof document.querySelector('#notes-open').onclick==='function'")
  assert page.locator('#v1 .verse-reference').all_text_contents()==['5:1','5:2'];assert page.locator('#v2 .verse-reference').all_text_contents()==['5:3'];assert '{5:' not in page.locator('#verses').inner_text();assert page.locator('#verses h3').count()==0;assert 'Text 1' not in page.locator('#edition-info').inner_text()
  gap=page.locator('#v1').bounding_box()['y']-(page.locator('#edition-info').bounding_box()['y']+page.locator('#edition-info').bounding_box()['height']);assert gap<40,gap
  assert page.locator('#reading-feedback').evaluate('(e)=>getComputedStyle(e).display')=='none'
  assert page.locator('#v1').evaluate('(e)=>getComputedStyle(e).borderBottomWidth')=='0px';assert page.locator('#v2').evaluate('(e)=>getComputedStyle(e).borderBottomWidth')=='0px'
  copied=copy(page,'#verses');assert copied['handled'];assert copied['text'].startswith('5:1 Veisuunjohtajalle');assert '\n5:2 Ota korviisi' in copied['text'];assert '\n5:3 Kuuntele' in copied['text'];assert all(x not in copied['text'] for x in ['Text 1','KR33','{','}','☆','↗','—']);assert 'minun sanani' in copied['text']
  page.locator('#v2 .verse-share').click();assert page.locator('#share-text').input_value().startswith('Psalms 5:3 Kuuntele');assert 'KR33' not in page.locator('#share-text').input_value();assert '{' not in page.locator('#share-text').input_value();page.click('#share-close')
  # Partial selection stays partial; the clipboard handler does not invent text.
  partial=page.evaluate('''()=>{const n=document.querySelector('#v2 .verse-line').lastChild,r=document.createRange();r.setStart(n,1);r.setEnd(n,9);const selection=getSelection();selection.removeAllRanges();selection.addRange(r);const data=new DataTransfer(),e=new ClipboardEvent('copy',{clipboardData:data,bubbles:true,cancelable:true});n.parentElement.dispatchEvent(e);return data.getData('text/plain')}''');assert partial=='Kuuntele',partial
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  # Independent source panels also have one reference per displayed passage and no per-verse titles.
  page.goto(base+'?edition=grc-source&compare1=&compare2=&compare3=&text=both&layout=source#JHN.3.16');page.wait_for_selector('#s1-v16 .verse-line');assert page.locator('#s1-v16 h3').count()==0;assert page.locator('#s1-v16 .verse-reference').first.inner_text()=='3:16';assert page.locator('#s1-v16').evaluate('(e)=>getComputedStyle(e).borderBottomWidth')=='0px'
  ids=['hin2017','fin-kr1938','engwebp','urdoucv'];params=['edition','compare1','compare2','compare3']
  for mask in range(16):
   page.goto(base+'?'+'&'.join(k+'='+(ids[i] if mask&(1<<i) else '') for i,k in enumerate(params))+'&text=original&layout=auto#JHN.3.16');page.wait_for_function("!document.querySelector('#status').textContent.includes('Loading') && !!document.querySelector('#top-menu')")
   if mask:
    page.wait_for_selector('#v16 .verse-line');assert page.locator('#v16 .translation').count()==mask.bit_count();assert page.locator('#v16 .verse-reference').count()==mask.bit_count();assert page.locator('#verses h3').count()==0
   else:assert page.locator('#verses').inner_text()==''
  page.goto(base+'?edition=fin-kr1938&compare1=&compare2=&compare3=&text=original#PSA.5.1');page.wait_for_selector('#v1 .verse-line');page.evaluate("async()=>await ReaderOffline.download(['fin-kr1938'])");page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#v1 .verse-line');assert copy(page,'#verses')['text'].startswith('5:1 Veisuunjohtajalle');assert page.locator('#v2 .verse-reference').inner_text()=='5:3';assert not errors,errors;browser.close()
  print('PASS: mobile Psalms 5 gap <40px; no repeated edition titles or verse borders; native 5:1/5:2/5:3 labels; clean whole/partial selection and share text; independent source panels; all 16 slot combinations; full Finnish Bible saved; offline native references and copy; no page errors')
finally:s.shutdown()
