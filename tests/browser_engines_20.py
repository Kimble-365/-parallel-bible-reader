"""2.0 startup, source typography and app choices in three Playwright engines."""
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
  for engine in ['chromium','firefox','webkit']:
   browser=getattr(p,engine).launch();ctx=browser.new_context(viewport={'width':390,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_default_timeout(60000)
   base=f'http://127.0.0.1:{s.server_port}/releases/v2.0/'
   page.goto(base+'?edition=&compare1=&compare2=hbo-wlc&compare3=#DEU.6.4');page.wait_for_selector('#v4 [data-slot="3"][role=button]');cell=page.locator('#v4 [data-slot="3"]');assert 'H8085' not in cell.inner_text();assert ''.join(cell.locator('[data-source-typography="large"]').all_text_contents())=='עד';assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.evaluate('localStorage.setItem("native-20-engine-check","שמע λόγος")');page.goto(base+'apps.html');page.wait_for_function('()=>!document.querySelector("#runtime-summary").textContent.includes("Detecting")');assert page.locator('[data-platform]').count()==4;assert page.evaluate('localStorage.getItem("native-20-engine-check")')=='שמע λόγος';assert not errors,errors
   ctx.close();browser.close();print('PASS',engine,'2.0 actual startup, Shema typography, mobile layout, app choices and Unicode storage')
finally:s.shutdown()
