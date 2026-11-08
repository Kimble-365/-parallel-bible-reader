"""Export the actual browser's separate source/Latin volumes as attributed UTF-8 files."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import argparse,hashlib,json,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
def main(out,commit):
 assert re.fullmatch('[0-9a-f]{40}',commit)
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 s=ThreadingHTTPServer(('127.0.0.1',0),H);Thread(target=s.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=browser.new_context(accept_downloads=True);page=context.new_page();page.set_default_timeout(120000);errors=[];external=[];page.on('pageerror',lambda e:errors.append(str(e)))
   base=f'http://127.0.0.1:{s.server_port}'
   page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base+'/') else (external.append(r.request.url),r.abort())[1])
   page.goto(base+'/releases/v2.0/reading-volumes.html');page.wait_for_selector('#verses article')
   volumes=page.evaluate('ReadingVolumes.volumes');assert len(volumes)==12;report=[]
   for v in volumes:
    page.select_option('#volume',v['id']);page.wait_for_selector('#verses article');
    with page.expect_download(timeout=240000) as download:page.click('#export-volume')
    name=v['id']+'-complete.txt';assert download.value.suggested_filename==name;target=out/name;download.value.save_as(target);data=target.read_bytes();text=data.decode('utf-8');assert text.startswith(v['label']+'\n') and 'Source:' in text and len(data)>100000;assert 'seg type=' not in text and "'l s=" not in text
    # Source-based verse count, not file size, establishes full exported coverage.
    count=page.evaluate('''async source=>{if(source==='salkinson')return SalkinsonVolume.verse_count;const e=BibleCatalog.editions.find(e=>e.id===source);let count=0;for(const b of e.book_codes)count+=(await ReaderOffline.loadBook(b,[source])).editions[source].length;return count}''',v['source'])
    actual=len(re.findall(r'^\S+:\S+ ',text,re.M));assert actual==count,(name,actual,count)
    if v['kind']!='original':assert 'estimate' in text or 'transliteration' in text
    report.append({'file':name,'source':v['source'],'kind':v['kind'],'source_rows':count,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
   # Verify a repeat export is byte-identical rather than timestamp-sensitive.
   page.select_option('#volume','salkinson-written');page.wait_for_selector('#verses article')
   with page.expect_download(timeout=240000) as d:page.click('#export-volume')
   assert Path(d.value.path()).read_bytes()==(out/'salkinson-written-complete.txt').read_bytes()
   assert not errors,errors;assert not external,external;context.close();browser.close()
  manifest={'source_commit':commit,'adapter':'reading-estimate-1','files':report,'repeat_export_verified':'salkinson-written','outside_network_requests':external,'status':'software-verified reading estimates; not exhaustive linguistic review','abp':'Not included: publisher copyright 1996/2013; no project redistribution/adaptation grant located.'}
  (out/'VOLUME-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(out/'METHODS-AND-RIGHTS.md').write_bytes((ROOT/'releases/v2.0/PRONUNCIATION-SOURCES.md').read_bytes())
  print(json.dumps({'volume_files':len(report),'total_bytes':sum(f['bytes'] for f in report),'source_commit':commit,'rows':{f['file']:f['source_rows'] for f in report}},ensure_ascii=False));print('PASS: 12 complete attributed UTF-8 source/Latin volumes exported by actual reader; exact source row counts; repeat bytes; no outside requests')
 finally:s.shutdown()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--commit',required=True);a=p.parse_args();main(a.out,a.commit)
