"""Real UI backup round trips and source verse navigation."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}/releases/v1.22/'
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(accept_downloads=True,viewport={'width':390,'height':844});page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+'?edition=engwebp&compare1=&compare2=&compare3=&text=original#JHN.3.16');page.wait_for_selector('#v16 .main-text');page.wait_for_selector('#menu-study')
  def manager():
   page.click('#menu-study');page.click('#menu-vocabulary');page.wait_for_selector('#vocabulary-import')
  def upload(raw):page.set_input_files('#vocabulary-import',{'name':'vocabulary.json','mimeType':'application/json','buffer':raw.encode()})
  manager();assert page.locator('#vocabulary-count').inner_text()=='0 shown / 0 saved words'
  word=json.loads((ROOT/'tests/fixtures/study121/jhn-3-16.json').read_text())['words'][0];hebrew=json.loads((ROOT/'tests/fixtures/study121/gen-1-1.json').read_text())['words'][0]
  page.evaluate('(w)=>ReaderWordStudy.add(w,"JHN 3:16")',word);page.fill('#vocabulary-search','Thus');assert page.locator('#vocabulary-rows .library-card').count()==1;page.fill('#vocabulary-search','')
  with page.expect_download() as d:page.click('#vocabulary-export-json')
  backup=Path(d.value.path()).read_text();assert json.loads(backup)['cards'][0]['source'];assert json.loads(backup)['cards'][0]['original']==word['original']
  page.get_by_role('button',name='Remove word',exact=True).click();assert not page.evaluate('ReaderWordStudy.cards()');upload(backup);page.wait_for_function('!document.querySelector("#vocabulary-import-confirm").disabled');assert not page.evaluate('ReaderWordStudy.cards()');assert '1 new words' in page.locator('#vocabulary-preview').inner_text();page.click('#vocabulary-import-confirm');assert page.evaluate('ReaderWordStudy.cards().length')==1
  upload(backup);page.wait_for_function('document.querySelector("#library-status").textContent.includes("All words already exist")');assert page.locator('#vocabulary-import-confirm').is_disabled();page.get_by_role('button',name='Cancel import',exact=True).click()
  incoming=json.loads(backup);incoming['cards'].append({**hebrew,'reference':'GEN 1:1'});upload(json.dumps(incoming));page.wait_for_function('!document.querySelector("#vocabulary-import-confirm").disabled');page.evaluate('(w)=>ReaderWordStudy.add({...w,gloss:"Changed after preview"},"JHN 3:16")',word);page.click('#vocabulary-import-confirm');assert 'changed after the preview' in page.locator('#library-status').inner_text();assert page.evaluate('ReaderWordStudy.cards().length')==2
  upload(json.dumps(incoming));page.wait_for_function('!document.querySelector("#vocabulary-import-confirm").disabled');page.click('#vocabulary-import-confirm');assert page.evaluate('ReaderWordStudy.cards().length')==3
  upload('{broken');page.wait_for_function('document.querySelector("#library-status").textContent.startsWith("Cannot import")');assert page.locator('#vocabulary-import-confirm').is_disabled();assert page.evaluate('ReaderWordStudy.cards().length')==3
  with page.expect_download() as d:page.click('#vocabulary-export-csv')
  csv=Path(d.value.path()).read_text(encoding='utf-8-sig');assert hebrew['original'] in csv and 'sourceUrl' in csv
  page.fill('#vocabulary-search','GEN 1:1');assert page.locator('#vocabulary-rows .library-card').count()==1;page.fill('#vocabulary-search','missing-word');assert page.locator('#vocabulary-rows .library-card').count()==0
  page.get_by_role('button',name='Back to reading',exact=True).last.click();page.reload();page.wait_for_selector('#menu-study');manager();assert '3 saved words' in page.locator('#vocabulary-count').inner_text();page.get_by_role('button',name='Practice saved words',exact=True).click();assert page.locator('#flashcard-back').is_hidden();page.click('#flashcard-reveal');assert page.locator('#flashcard-back').is_visible();page.get_by_role('button',name='Manage words & backups',exact=True).click();assert page.locator('#vocabulary-rows .library-card').count()==3
  page.get_by_role('button',name='Back to reading',exact=True).last.click();page.click('#menu-study');page.click('#menu-words');page.wait_for_function('!document.querySelector("#word-read").disabled');page.select_option('#word-book','JHN');page.wait_for_function('document.querySelector("#word-chapter").options.length===21');page.select_option('#word-chapter','3');page.select_option('#word-verse','16');page.click('#word-read');page.wait_for_selector('#word-tokens .interlinear-word',timeout=60000);assert page.locator('#word-tokens .interlinear-word').count()==26
  page.fill('#word-search','no-match');page.click('#word-next');page.wait_for_function('document.querySelector("#word-verse").value==="17" && !document.querySelector("#word-read").disabled');assert page.input_value('#word-search')=='';assert page.locator('#word-tokens .interlinear-word').count()>0;page.click('#word-previous');page.wait_for_function('document.querySelector("#word-verse").value==="16" && !document.querySelector("#word-read").disabled');assert page.locator('#word-tokens .interlinear-word').count()==26
  page.select_option('#word-verse','36');page.click('#word-next');page.wait_for_function('document.querySelector("#word-chapter").value==="4" && document.querySelector("#word-verse").value==="1" && !document.querySelector("#word-read").disabled');assert page.locator('#word-tokens .interlinear-word').count()>0;page.click('#word-previous');page.wait_for_function('document.querySelector("#word-chapter").value==="3" && document.querySelector("#word-verse").value==="36" && !document.querySelector("#word-read").disabled')
  page.select_option('#word-chapter','1');page.select_option('#word-verse','1');assert page.locator('#word-previous').is_disabled();page.select_option('#word-chapter','21');page.select_option('#word-verse','25');assert page.locator('#word-next').is_disabled();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert not errors,errors
  b.close();print('PASS: mobile vocabulary search, JSON download/preview/restore/deduplication/stale-preview refusal, invalid file preservation, UTF-8 CSV download, reload persistence/practice, live verse forward/back/chapter navigation and book boundaries; no page errors')
finally:s.shutdown()
