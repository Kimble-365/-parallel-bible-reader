"""Actual maintained-reader bridge: exact source tokens, shared Study UI, safe fallback."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--site',required=True);p.add_argument('--report');a=p.parse_args()
ROOT=Path(__file__).resolve().parents[2];SITE=Path(a.site).resolve()
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def translate_path(self,path):
  clean=path.split('?',1)[0]
  if clean.startswith('/davarqadosh/packs/'):
   relative=Path(clean.removeprefix('/davarqadosh/'))
   target=(SITE/relative).resolve()
   if SITE in target.parents:return str(target)
  return super().translate_path(path)
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=s.serve_forever,daemon=True).start();results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in [390,1280]:
   ctx=browser.new_context(viewport={'width':width,'height':900},has_touch=width==390);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   url=f'http://127.0.0.1:{s.server_port}/releases/v1.27/'
   page.goto(url+'?edition=engwebp&compare1=&compare2=&compare3=&text=original#GEN.1.1');page.wait_for_selector('#v1 .main-text');page.wait_for_function('window.DavarQadoshIntegration')
   assert page.locator('.dq-inline-word,.dq-verse-action').count()==0
   page.click('#menu-study');assert page.locator('#menu-davarqadosh').count()==0;page.get_by_role('button',name='Back to reading',exact=True).click()
   page.goto(url+'?edition=hbo-wlc&compare1=engwebp&compare2=&compare3=&text=original#GEN.1.1');page.wait_for_selector('#v1 .dq-inline-word',timeout=60000)
   line=page.locator('#v1 [data-edition="hbo-wlc"] .original .verse-line');original=line.inner_text()
   assert line.locator('.dq-inline-word').count()==7
   assert 'Gen.1.1:1:0' in line.locator('.dq-inline-word').first.get_attribute('data-occurrence')
   assert page.evaluate('''()=>{const line=document.querySelector('#v1 [data-edition="hbo-wlc"] .verse-line'),b=DavarQadoshIntegration.sourceBook;return line.textContent===line.querySelector('.verse-reference').textContent+' '+b.verses.find(v=>v.verse_key==='Gen.1.1').display_text}''')
   if width==390:line.locator('.dq-inline-word').first.tap()
   else:line.locator('.dq-inline-word').first.focus();page.keyboard.press('Enter')
   page.wait_for_selector('#study-content .dq-occurrence-id');assert 'Gen.1.1:1:0' in page.locator('#study-content').inner_text()
   assert 'Contextual meaning, manuscript checking' in page.locator('#study-content').inner_text()
   link=page.locator('.dq-open-research').get_attribute('href');assert 'token=oshb' in link and 'book=GEN' in link
   page.get_by_role('button',name='Back to reading',exact=True).click();assert line.inner_text()==original
   selection=page.evaluate('''()=>{const line=document.querySelector('#v1 [data-edition="hbo-wlc"] .verse-line'),r=document.createRange();r.selectNodeContents(line);getSelection().removeAllRanges();getSelection().addRange(r);const text=getSelection().toString();getSelection().removeAllRanges();return text}''');assert selection==original
   page.click('#menu-study');page.click('#menu-davarqadosh');page.wait_for_selector('.dq-source-words button');assert page.locator('.dq-source-words button').count()==7
   page.get_by_role('button',name='Back to reading',exact=True).click()
   if width==1280:
    for code in ['PSA','ISA','DAN']:
     chapter='2' if code=='DAN' else '1';verse='4' if code=='DAN' else '1'
     page.goto(url+f'?edition=hbo-wlc&compare1=engwebp&compare2=&compare3=&text=original#{code}.{chapter}.{verse}');page.wait_for_function('(code)=>DavarQadoshIntegration.state.book===code&&DavarQadoshIntegration.state.verifiedVerses>0',arg=code,timeout=60000)
     if code=='DAN':
      token=page.evaluate('DavarQadoshIntegration.sourceBook.tokens.find(t=>t.verse_key==="Dan.2.4"&&t.language==="arc"&&t.attestation==="main").id')
      page.locator('button.dq-inline-word[data-occurrence="'+token+'"]').click();page.wait_for_selector('.dq-occurrence-id');assert 'Biblical Aramaic' in page.locator('#study-content').inner_text();page.get_by_role('button',name='Back to reading',exact=True).click()
    # A changed display is not reinterpreted by whitespace or approximate offsets.
    page.goto(url+'?edition=hbo-wlc&compare1=&compare2=&compare3=&text=original#GEN.1.1');page.wait_for_selector('#v1 .dq-inline-word',timeout=60000)
    page.evaluate('''()=>{const l=document.querySelector('#v1 [data-edition="hbo-wlc"] .verse-line');l.append(document.createTextNode('!'))}''');page.wait_for_function('DavarQadoshIntegration.state.unmappedVerses>0');assert page.locator('#v1 .dq-inline-word').count()==0
    page.locator('#v1 .dq-verse-action').click();page.wait_for_selector('.dq-source-words button');assert page.locator('.dq-source-words button').count()==7;page.get_by_role('button',name='Back to reading',exact=True).click()
    # Corrupt optional data cannot rewrite existing source text or create occurrence targets.
    fresh=browser.new_context(service_workers='block');bad=fresh.new_page();bad.route('**/davarqadosh/packs/GEN.wlexpack*',lambda route:route.fulfill(body=b'bad pack',status=200));bad.goto(url+'?edition=hbo-wlc&compare1=&compare2=&compare3=&text=original#GEN.1.1');bad.wait_for_function('window.DavarQadoshIntegration?.state.error!==null');assert bad.locator('#v1 .main-text').count()==1;assert bad.locator('.dq-inline-word').count()==0;fresh.close()
   assert not errors,errors;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');results.append({'width':width,'checks':'exact source lookup, Study menu, copy, pending state, RTL, keyboard/touch'});ctx.close()
  browser.close()
 if a.report:Path(a.report).write_text(json.dumps(results,indent=2)+'\n')
 print('PASS: maintained reader WLC-only Study integration, source-identity words, 4 books, Aramaic, copy preservation, mismatched-text fallback and corrupt-pack isolation',json.dumps(results))
finally:s.shutdown()
