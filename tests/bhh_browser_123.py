from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(R),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}/releases/v1.23/'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+'?edition=hbo-sp&compare1=hbo-mam&compare2=lat-clementine-thb&compare3=hbo-wlc&text=original#GEN.2.2');page.wait_for_selector('.main-text',timeout=60000)
  page.wait_for_function('window.ReaderOffline && window.BHHTextPacks')
  out=page.evaluate('''async()=>{const ids=['hbo-sp','hbo-mam','lat-clementine-thb'];const d=await ReaderOffline.loadBook('GEN',ids);return Object.fromEntries(ids.map(id=>[id,d.editions[id].find(r=>r[0]===2&&r[1]===2)[2]]))}''');assert 'הששי' in out['hbo-sp'].replace('שׁ','ש');assert 'בַּיּ֣וֹם' in out['hbo-mam'];assert 'sexto' in out['lat-clementine-thb'] or 'séptimo' in out['lat-clementine-thb'] or 'septimo' in out['lat-clementine-thb']
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  assert page.evaluate("async()=>{for(const e of BibleCatalog.editions.filter(x=>x.data_group==='related-english')){const d=await ReaderOffline.loadBook(e.book_codes[0],[e.id]);if(!d.editions[e.id]?.length)return false}return true}")
  # Exercise normal IndexedDB selected-text installation and reload in an offline context.
  page.evaluate("ReaderOffline.download(['hbo-sp'])");assert page.evaluate("ReaderOffline.list().then(x=>x.filter(y=>y.id==='hbo-sp').length)")==5
  ctx.set_offline(True);saved=page.evaluate("ReaderOffline.loadBook('DEU',['hbo-sp']).then(x=>x.editions['hbo-sp'].length)");assert saved>900;ctx.set_offline(False)
  # Tampered payload fails integrity, while another edition remains readable.
  page.route('**/bhh-data/EXO.json.gz*',lambda route:route.fulfill(body=b'corrupt',content_type='application/gzip'))
  result=page.evaluate("ReaderOffline.loadBook('EXO',['hbo-mam','engwebp'],{partial:true}).then(x=>({missing:x.unavailable.map(y=>y.id),ok:!!x.editions.engwebp}))");assert result=={'missing':['hbo-mam'],'ok':True};page.unroute('**/bhh-data/EXO.json.gz*')
  page.goto(base+'bhh.html');page.wait_for_selector('#scroll option',state='attached');assert page.locator('#scroll option').count()==997
  # Use a small source with explicit restored sign flags.
  page.select_option('#scroll',label='4Q10 · '+str(page.evaluate("BHHLibrary.scrolls.find(x=>x.name==='4Q10').units"))+' source units');page.click('#read-scroll');page.wait_for_function("document.querySelector('#status').textContent.startsWith('Verified')");page.fill('#filter','1941896');assert page.locator('#output .restored').count()==1;assert 'rec' in page.locator('#output').inner_text();page.click('#save');page.wait_for_function("document.querySelector('#status').textContent.startsWith('Saved verified')")
  page.evaluate("navigator.serviceWorker.register('sw.js')");page.wait_for_function("navigator.serviceWorker.ready.then(()=>true)");page.reload();page.wait_for_function('!!navigator.serviceWorker.controller');ctx.set_offline(True);page.reload();page.wait_for_selector('#scroll option',state='attached');idx=page.evaluate("BHHLibrary.scrolls.findIndex(x=>x.name==='4Q10')");page.select_option('#scroll',str(idx));page.fill('#filter','1941896');page.click('#read-scroll');page.wait_for_function("document.querySelector('#status').textContent.startsWith('Verified')");assert page.locator('#output .restored').count()==1;ctx.set_offline(False)
  assert not errors,errors;b.close();print('PASS Chromium: four mixed editions, Hebrew/Latin mobile width, SP offline IndexedDB, corrupt-pack isolation, DSS physical/damage display and independently cached source reading after offline reload; no page errors')
finally:s.shutdown()
