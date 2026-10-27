"""Behavior checks for the isolated 1.2 reader. Requires Playwright + Chromium.
Fixtures model different book coverage; real-data smoke runs separately below.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs
from threading import Thread
import json,re,zipfile,tempfile,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}'
VERSION=os.environ.get('READER_VERSION','1.2');RELEASE_PATH='/releases/v'+VERSION+'/'
IDS=['hin2017','fin-kr1938','engwebp','urdoucv'];SLOTS=['primary','compare1','compare2','compare3'];PARAMS=['edition','compare1','compare2','compare3']
BOOKS=[['GEN','Genesis'],['JHN','John'],['REV','Revelation']]
POSITIONS=[[['JHN',1]],[['GEN',1],['JHN',1]],[['GEN',1],['REV',2]],[['JHN',1]]]
ED=[dict(id=id,label='Fixture '+str(i+1),title='Fixture '+str(i+1),language=['hi','fi','en','ur'][i],script=['Devanagari','Latin','Latin','Arabic'][i],direction='rtl' if i==3 else 'ltr',scope='Fixture coverage',book_codes=list(dict.fromkeys(p[0] for p in POSITIONS[i])),positions=POSITIONS[i],available=True,source='https://example.org/source') for i,id in enumerate(IDS)]
CAT=dict(books=BOOKS,editions=ED,unavailable=[],version='fixture-v12',audio_editions=[dict(id='HINDPI',label='Fixture audio',local_editions=['hin2017'],url='https://example.org/audio',full_bible=True)])
DATA={b:dict(editions={}) for b,_ in BOOKS}
for i,id in enumerate(IDS):
 for b,c in POSITIONS[i]:
  rows=[[c,1,'Original needle '+id,'Latin romanonly '+id],[c,2,'Second café '+id,'Second café '+id]]
  if i==0:rows[0][2]='प्रेम originalonly'; rows[0][3]='prema romanonly'
  if i==3:rows[0][2]='محبت needle';rows[0][3]='mḥbt romanonly'
  DATA[b]['editions'][id]=rows

def fixture(browser,storage=None):
 ctx=browser.new_context();page=ctx.new_page();errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)))
 if storage is not None:ctx.add_init_script('localStorage.clear();'+''.join('localStorage.setItem('+json.dumps(k)+','+json.dumps(json.dumps(v))+');' for k,v in storage.items()))
 def catalog(route):route.fulfill(content_type='text/javascript',body='window.BibleCatalog='+json.dumps(CAT)+';')
 def data(route):
  code=Path(urlsplit(route.request.url).path).stem;requests.append(code);route.fulfill(content_type='text/javascript',body='window.BibleBooks['+json.dumps(code)+']='+json.dumps(DATA[code])+';')
 page.route('**/catalog.js?*',catalog);page.route('**/data/*.js?*',data)
 return ctx,page,errors,requests

def open_page(page,values,fragment='JHN.1.1'):
 from urllib.parse import urlencode
 page.goto(BASE+RELEASE_PATH+'?'+urlencode(dict(zip(PARAMS,values)))+'#'+fragment)
 page.wait_for_function("!document.querySelector('#status').textContent.includes('Loading')")

def run():
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  # Independent assertions against all 16 enable/disable combinations.
  for mask in range(16):
   values=[IDS[i] if mask&(1<<i) else '' for i in range(4)];ctx,page,errors,requests=fixture(browser);open_page(page,values)
   expected=[str(i+1) for i,v in enumerate(values) if v]
   actual=page.locator('#verses .verse:first-child .translation').evaluate_all('(xs)=>xs.map(x=>x.dataset.slot)')
   assert actual==expected,(mask,actual,expected)
   assert page.locator('#search-button').is_disabled()==(mask==0)
   if mask==0:
    assert not requests,requests;assert page.locator('#verses').inner_text()=='';assert page.locator('#heading').inner_text()=='Choose a translation to start'
   assert [page.locator('#'+id).input_value() for id in SLOTS]==values
   assert not errors,errors
   ctx.close()
  print('PASS: all 16 slot combinations, including empty slot 1 and all empty; no data request when empty')
  # Same edition in distinct slots must not collapse stable numbering.
  ctx,page,errors,requests=fixture(browser);open_page(page,['','',IDS[0],IDS[0]])
  assert page.locator('#v1 .translation').evaluate_all('(xs)=>xs.map(x=>x.dataset.slot)')==['3','4'];ctx.close()
  # Legacy state migrates; legacy slot IDs and intentional empty selections remain.
  old=dict(edition=IDS[0],compare1='',compare2=IDS[2],book='JHN',chapter=1,verse=1,view='latin',fontScale=120)
  ctx,page,errors,requests=fixture(browser,{'bible-reader-reading-v1':old});page.goto(BASE+RELEASE_PATH+'');page.wait_for_selector('#v1')
  state=page.evaluate("JSON.parse(localStorage.getItem('bible-reader-reading-v2'))")
  assert state['slots']==[IDS[0],'',IDS[2],''] and state['view']=='latin' and state['fontScale']==120,state
  page.select_option('#primary','');page.select_option('#compare2','');page.wait_for_function("document.querySelector('#heading').textContent==='Choose a translation to start'")
  state=page.evaluate("JSON.parse(localStorage.getItem('bible-reader-reading-v2'))");assert state['slots']==['']*4
  # The init script intentionally reseeds legacy data, so remove it by using a new context populated from the saved v2 record.
  ctx.close();ctx,page,errors,requests=fixture(browser,{'bible-reader-reading-v2':state});page.goto(BASE+RELEASE_PATH+'');page.wait_for_function("document.querySelector('#heading').textContent==='Choose a translation to start'");assert not requests;ctx.close()
  print('PASS: v1 preference migration, font/view preservation, and all-empty v2 restoration')
  ctx,page,errors,requests=fixture(browser);open_page(page,[IDS[0],IDS[1],IDS[2],IDS[3]])
  # Book union includes GEN/REV absent from the first slot; enabled slot with no book shows an explicit gap.
  assert page.locator('#book option').evaluate_all('(xs)=>xs.map(x=>x.value)')==['GEN','JHN','REV']
  page.select_option('#book','REV');page.wait_for_selector('#v1 .translation[data-slot="3"]');assert page.locator('#chapter').input_value()=='2'
  assert 'not included' in page.locator('#v1 .translation[data-slot="1"]').inner_text()
  page.locator('#search-panel').evaluate('(x)=>x.open=true');page.select_option('#scope','all');page.fill('#search','needle');page.click('#search-button');page.wait_for_function("document.querySelector('#results').textContent.includes('3/3')")
  assert page.locator('#results .result').filter(has_text='REV 2:1').count()>0
  # Search original / Latin only respects visible forms, with slot and edition identity.
  page.select_option('#book','JHN');page.wait_for_selector('#v1');page.locator('#appearance-settings').evaluate('(x)=>x.open=true');page.select_option('#scope','chapter');page.select_option('#text-display','original');page.fill('#search','romanonly');page.click('#search-button');page.wait_for_function("document.querySelector('#results').textContent.includes('1/1')");assert page.locator('#results .result').count()==0
  page.select_option('#text-display','latin');page.fill('#search','romanonly');page.click('#search-button');page.wait_for_selector('#results .result');assert page.locator('#results .result[data-slot="1"][data-form="Latin"]').count()==1
  page.select_option('#compare3','');assert page.locator('#results .result').count()==0
  page.fill('#search','mḥbt');page.click('#search-button');page.wait_for_function("document.querySelector('#results').textContent.includes('1/1')");assert page.locator('#results .result').count()==0
  # Sharing restores all four positions, including holes.
  page.select_option('#compare1','');page.wait_for_selector('#v1 .verse-share');page.locator('#v1 .verse-share').click();link=page.locator('#share-link').input_value();q=parse_qs(urlsplit(link).query,keep_blank_values=True);assert [q[k][0] for k in PARAMS]==[IDS[0],'',IDS[2],''];page.click('#share-close')
  ctx2,p2,e2,r2=fixture(browser);p2.goto(link);p2.wait_for_selector('#v1');assert [p2.locator('#'+id).input_value() for id in SLOTS]==[IDS[0],'',IDS[2],''];ctx2.close()
  # Bookmark uses an actual visible edition, even if the first slot has no verse at this reference.
  page.select_option('#book','REV');page.wait_for_selector('#v1 .bookmark-toggle');page.locator('#v1 .bookmark-toggle').click();marks=page.evaluate("JSON.parse(localStorage.getItem('bible-reader-bookmarks-v1'))");assert marks[0]['edition']==IDS[2],marks
  # Every theme/mode, narrow width, text size, quiet mode, and RTL original.
  page.locator('#appearance-settings').evaluate('(x)=>x.open=true')
  for theme in ['papyrus-yellow','blue','brown']:
   for mode in ['light','dark']:
    page.select_option('#color-theme',theme);page.select_option('#display-mode',mode);assert page.locator('html').get_attribute('data-theme')==theme
  page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.click('#font-larger');assert page.locator('#font-size').inner_text()=='110%'
  page.locator('#reading-mode').click();assert page.locator('html.quiet').count()==1;page.keyboard.press('Escape');assert page.locator('html.quiet').count()==0
  assert not errors,errors;ctx.close()
  print('PASS: union navigation/search, visible forms, removed-slot exclusion, share URL, bookmarks, 6 themes, mobile and reading tools')
  # Storage unavailable and malformed do not prevent reading.
  for script in ["Storage.prototype.getItem=function(){throw Error('blocked')};Storage.prototype.setItem=function(){throw Error('blocked')}","localStorage.setItem('bible-reader-reading-v2','{bad json')"]:
   ctx,page,errors,requests=fixture(browser);ctx.add_init_script(script);open_page(page,[IDS[0],'','','']);assert page.locator('#v1').count()==1;assert not errors;ctx.close()
  print('PASS: blocked and malformed browser storage')
  # Real data smoke: ensure genuine corpus and Arabic direction still render.
  ctx=browser.new_context();page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(BASE+RELEASE_PATH+'?edition=hin2017&compare1=fin-kr1938&compare2=engwebp&compare3=urdoucv#JHN.3.16');page.wait_for_selector('#v16 .translation[data-slot="4"]',timeout=30000)
  assert page.locator('#v16 .translation').count()==4;assert 'परमेश्वर' in page.locator('#v16 .translation[data-slot="1"]').inner_text();assert page.locator('#v16 [data-slot="4"] [dir="rtl"]').count()==1
  page.screenshot(path=str(Path(tempfile.gettempdir())/'reader-v1.2-desktop.png'),full_page=False);page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(Path(tempfile.gettempdir())/'reader-v1.2-mobile.png'),full_page=False);assert not errors,errors;ctx.close()
  print('PASS: genuine Hindi/Finnish/English/Urdu data, John 3:16, RTL and mobile overflow')
  browser.close()
try:run()
finally:server.shutdown()
