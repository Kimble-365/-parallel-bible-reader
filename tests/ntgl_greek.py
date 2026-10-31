"""Greek-pack integrity, known source-format boundaries, and browser integration."""
from pathlib import Path
import json,gzip,hashlib,mimetypes
from urllib.parse import urlsplit,unquote
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.22'
def js(p):return json.loads(p.read_text().split('=',1)[1].strip().rstrip(';'))
C=js(O/'catalog.js');M=js(O/'ntgl-manifest.js');ids=['grc-tischendorf8','grc-nestle1904','grc-sblgnt','grc-westcott-hort','grc-opengnt-koine'];by={e['id']:e for e in C['editions']};assert len(C['editions'])==73
for id in ids:
 assert by[id]['books']==27 and len(by[id]['positions'])==260,(id,len(by[id]['positions']))
 assert by[id]['verses']>7900
for code,info in M.items():
 z=(O/'ntgl-data'/(code+'.json.gz')).read_bytes();raw=gzip.decompress(z);assert len(raw)==info['bytes'] and hashlib.sha256(raw).hexdigest()==info['sha256'];assert hashlib.sha256(z).hexdigest()==info['packed_sha256']
 d=json.loads(raw)
 for id in ids:
  rows=d['editions'][id];assert rows and len({(x[0],x[1]) for x in rows})==len(rows)
  assert all(x[2].strip() and '\ufffd' not in x[2] and '<font' not in x[2] for x in rows)
def verse(code,id,c,v):return next(x[2] for x in json.loads(gzip.decompress((O/'ntgl-data'/(code+'.json.gz')).read_bytes()))['editions'][id] if x[:2]==[c,v])
assert 'μέλη' in verse('1CO','grc-nestle1904',6,15)
assert 'Καίσαρι' in verse('LUK','grc-nestle1904',20,22)
assert 'μοιχεύσεις' in verse('MAT','grc-nestle1904',5,27)
assert 'κλάδους' in verse('MRK','grc-nestle1904',4,32)
assert 'Γαλιλαίαν' in verse('MRK','grc-nestle1904',14,28)
assert 'κυριεύσει' in verse('ROM','grc-nestle1904',6,14)
assert 'ἀνατολῆς' not in verse('MRK','grc-nestle1904',16,20)
assert 'ἀνατολῆς' in json.loads((O/'sources/ntgl-paratext.json').read_text())[0]['text']
assert 'οὐδέν' in verse('JHN','grc-sinaiticus-original-pilot',1,3)
assert 'οὐδὲ ἕν' in verse('JHN','grc-sinaiticus-ca-pilot',1,3)
study=json.loads(gzip.decompress((O/'ntgl-data/study.json.gz').read_bytes()));assert len(study['lexicon']['entries'])==6153;assert len(study['morphgnt_pilot'])==61
base='https://reader.test/releases/v1.22/'
def local_transport(route):
 path=(R/unquote(urlsplit(route.request.url).path).lstrip('/')).resolve()
 if path.is_dir():path=path/'index.html'
 if path.is_relative_to(R) and path.is_file():route.fulfill(body=path.read_bytes(),content_type=mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
 else:route.fulfill(status=404,body='Missing local test asset')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);context=browser.new_context(service_workers='block');context.route('https://reader.test/**',local_transport);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+'?edition=grc-nestle1904&compare1=grc-tischendorf8&compare2=grc-sblgnt&compare3=grc-opengnt-koine#JHN.1.1');page.wait_for_selector('#v1');page.wait_for_function("document.querySelector('#v1')?.textContent.includes('λόγος')")
  assert page.locator('#primary').input_value()=='grc-nestle1904'
  assert page.locator('#v1 .translation').count()==4
  assert 'λόγος' in page.locator('#v1').inner_text()
  for id in ids:
   data=page.evaluate('async id=>{const d=await ReaderOffline.loadBook("JHN",[id]);return d.editions[id]}',id);assert len(data)>870
  page.evaluate('async()=>{await ReaderOffline.download(["grc-sinaiticus-original-pilot"],null);}')
  context.set_offline(True)
  assert page.evaluate('async()=>{const d=await ReaderOffline.loadBook("JHN",["grc-sinaiticus-original-pilot"],{savedOnly:true});return d.editions["grc-sinaiticus-original-pilot"].length}')==5
  context.set_offline(False)
  study_page=context.new_page();study_page.on('pageerror',lambda e:errors.append(str(e)));study_page.goto(base+'ntgl-resources.html');study_page.click('#load');study_page.wait_for_function("document.querySelector('#status').textContent.includes('6153')");study_page.fill('#query','λόγος');study_page.wait_for_selector('#results article');assert study_page.locator('#morph tr').count()==61;assert study_page.locator('#projects article').count()==13
  assert not errors,errors
  page.screenshot(path='/tmp/ntgl-parallel-reader.png',full_page=False);browser.close()
 print('PASS: five complete NT editions; seven installed comparison entries; source-format regressions; browser four-column reading, all new full-text loaders, offline saved pilot, lexicon/morphology/project resources.')
finally:pass
