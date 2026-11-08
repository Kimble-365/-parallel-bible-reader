"""Verify two byte-identical ZIPs and the actual extracted 84-edition reader."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import argparse,hashlib,json,os,socket,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from package_reader_20 import build,digest

def main(out,commit):
 out=Path(out).resolve();first=build(ROOT,out,commit)
 with TemporaryDirectory() as work:
  second=build(ROOT,Path(work)/'repeat',commit);assert first['sha256']==second['sha256'],'Non-reproducible ZIP'
  target=Path(work)/'extracted';target.mkdir();archive=out/first['archive']
  with ZipFile(archive) as z:
   assert z.testzip() is None;names=z.namelist();assert len(names)==len(set(names));assert not any(n.startswith('/') or '..' in Path(n).parts for n in names)
   manifest=json.loads(z.read('PACKAGE-MANIFEST.json'));assert manifest['edition_count']==84 and manifest['source_commit']==commit
   for entry in manifest['files']:
    data=z.read(entry['path']);assert len(data)==entry['bytes'];assert hashlib.sha256(data).hexdigest()==entry['sha256']
    if entry['kind']=='verbatim-repository':assert digest(ROOT/entry['path'])==entry['sha256'],entry['path']
   z.extractall(target)
  with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
  process=subprocess.Popen([sys.executable,str(target/'START-READER.py'),'--no-browser','--port',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  base=f'http://127.0.0.1:{port}'
  try:
   for attempt in range(100):
    try:
     with urllib.request.urlopen(base,timeout=1) as response:assert response.status==200
     break
    except OSError:time.sleep(.1)
   else:raise AssertionError('Local package launcher did not start')
   with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844},accept_downloads=True,permissions=['clipboard-read','clipboard-write']);page=ctx.new_page();page.set_default_timeout(120000);errors=[];bad=[];external=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:bad.append(r.url) if r.status>=400 else None)
    page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base+'/') else (external.append(r.request.url),r.abort())[1]);page.add_init_script('window.DecompressionStream=undefined')
    page.goto(base+'/?edition=engwebp&compare1=&compare2=fin-kr1938&compare3=&layout=auto#JHN.3.16');page.wait_for_selector('#v16 [data-slot="3"][role=button]');page.wait_for_function('window.ReaderFaithLibrary');assert '/releases/v2.0/' in page.url
    # Every installed edition must load a nonempty representative book locally.
    loaded=page.evaluate('''async()=>{const result=[];for(const e of BibleCatalog.editions){const book=e.book_codes[0],data=await ReaderOffline.loadBook(book,[e.id]);const rows=data.editions[e.id];if(!rows?.some(r=>r[2]||r[3]))throw Error('No text: '+e.id);result.push({id:e.id,book,rows:rows.length});}return result;}''');assert len(loaded)==84
    page.locator('#v16 [data-slot="3"]').click();page.get_by_role('button',name='Blue',exact=True).click();page.get_by_role('button',name='Copy to Notes',exact=True).click();assert 'KR33/38' in page.locator('#notes-quotes').inner_text();page.click('#notes-close');page.reload();page.wait_for_selector('#v16 [data-slot="3"][data-highlight="blue"]');page.locator('#v16 [data-slot="3"]').click()
    with page.expect_download() as d:page.get_by_role('button',name='Verse image',exact=True).click()
    assert Path(d.value.path()).read_bytes().startswith(b'\x89PNG\r\n\x1a\n');page.get_by_role('button',name='Pray',exact=True).click();page.select_option('#faith-choice','healing');assert 'promises no' in page.locator('#faith-note').inner_text();page.locator('#faith-library button').filter(has_text='Back to reading').click()
    page.get_by_role('button',name='Settings',exact=True).click();page.locator('#appearance-settings').evaluate('(e)=>e.open=true');page.select_option('#reading-font','classic');page.get_by_role('button',name='Back to reading',exact=True).first.click();page.reload();page.wait_for_function('document.documentElement.dataset.readerFont==="classic"');assert page.locator('#compare1').input_value()=='' and page.locator('#compare3').input_value()=='';assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    # Complex shared text families and gzip fallback remain local and usable.
    for edition,ref in [('hbo-wlc','GEN.1.1'),('syc-dsc-nt','JHN.3.16'),('jpn-bungo','JHN.3.16'),('grc-swete','WIS.1.1')]:
     page.goto(base+'/releases/v2.0/?edition='+edition+'&compare1=&compare2=&compare3=&layout=auto#'+ref);page.wait_for_selector('#verses .main-text');assert page.locator('#verses .main-text').first.inner_text().strip()
    assert not errors,errors;assert not external,external;assert not bad,bad
    filectx=browser.new_context();filepage=filectx.new_page();filepage.goto((target/'index.html').as_uri());assert 'START-READER.py' in filepage.locator('body').inner_text();assert 'browser' in filepage.locator('body').inner_text();filectx.close();ctx.close();browser.close()
   report={**first,'reproducible':True,'manifest_files_verified':len(manifest['files']),'representative_editions_loaded':loaded,'tests':['exact ZIP extraction','verbatim source hashes','complete packaged shell assets','all 84 edition delivery samples','mobile font/Notes/highlights/PNG/Pray','empty slot preservation','Hebrew/Syriac/Japanese/LXX gzip fallback','no outside-network requests','file launcher limitations shown'],'not_verified':['physical Safari/Edge/iPhone','every verse linguistic accuracy','source-hosted study resources without Internet']}
   (out/'VERIFICATION-REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
   print('PASS: two byte-identical ZIPs; every manifest file verified; 84 edition samples; actual extracted mobile 2.0 reader and local launcher; no external or failed local requests')
  finally:process.terminate();process.wait(timeout=10)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--commit',required=True);a=p.parse_args();main(a.out,a.commit)
