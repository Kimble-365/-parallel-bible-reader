"""Actual Chromium app-choice page and native bridge dispatch, without native-runtime claims."""
import json
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def end_headers(self):
  c=json.loads((ROOT/'apps/native-20/src-tauri/tauri.conf.json').read_text())['app']['security']['csp'];self.send_header('Content-Security-Policy',c);super().end_headers()
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for native in [False,True]:
   ctx=browser.new_context(viewport={'width':390,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:print('Browser:',m.text) if m.type=='error' else None)
   page.add_init_script('''Object.defineProperty(navigator,'platform',{value:'MacIntel'});Object.defineProperty(navigator,'userAgentData',{value:{platform:'macOS'}});Object.defineProperty(navigator,'maxTouchPoints',{value:5});window.calls=[];'''+('''window.__TAURI__={core:{invoke:async(cmd,args)=>{calls.push({cmd,args});if(cmd==='runtime_info')return {os:'windows',arch:'x86_64',native:true,version:'2.0.0'};if(cmd==='save_export')return 'C:/App/exports/reader.txt';}}};''' if native else ''))
   page.goto(f'http://127.0.0.1:{s.server_port}/releases/v2.0/apps.html');page.wait_for_function('()=>!document.querySelector("#runtime-summary").textContent.includes("Detecting")')
   assert page.locator('[data-recommended=true]').get_attribute('data-platform')==('windows' if native else 'ios')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert '1.29 remains reserved' in page.locator('body').inner_text();assert page.locator('a[download]').count()==0
   page.evaluate('localStorage.setItem("parallel-reader-notes-v1",JSON.stringify({preserve:"שמע λόγος"}))');before=page.evaluate('localStorage.getItem("parallel-reader-notes-v1")')
   if native:
    page.evaluate('navigator.clipboard.writeText("שמע λόγος")');assert page.evaluate('calls.at(-1).args.text')=='שמע λόγος'
    page.get_by_role('link',name='Build status and review artifacts').click();assert page.evaluate('calls.at(-1).cmd')=='open_external';assert page.url.endswith('apps.html')
    page.once('dialog',lambda d:d.accept());page.evaluate('''()=>{const a=document.createElement('a');a.download='reader.txt';a.href=URL.createObjectURL(new Blob(['שמע λόγος'],{type:'text/plain'}));a.click()}''');page.wait_for_function('()=>calls.some(c=>c.cmd==="save_export")')
    encoded=page.evaluate('calls.find(c=>c.cmd==="save_export").args.bytes');assert bytes(encoded)=='שמע λόγος'.encode()
   page.reload();assert page.evaluate('localStorage.getItem("parallel-reader-notes-v1")')==before;assert not errors,errors;ctx.close()
  browser.close()
 print('PASS 2.0 actual Chromium: mobile app choices, iPad browser hint/native Windows precedence, clipboard/link/export dispatch with exact Unicode bytes and retained Notes; bridge mocked')
finally:s.shutdown()
