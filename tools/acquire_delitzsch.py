"""Acquire attributed historical Delitzsch pages from Hebrew Wikisource.
Uses the public read API, modest concurrency and an on-disk cache. Does not use the copyrighted 2003 revision.
"""
from pathlib import Path
import json,re,urllib.request,urllib.parse,concurrent.futures,hashlib,time
HOME=Path('/workspace/reader-new-sources/delitzsch');HOME.mkdir(exist_ok=True)
INDEX=json.loads(Path('/workspace/reader-new-sources/lxx-verified-9.txt').read_text())['parse']['wikitext']['*']
LINKS=re.findall(r'\[\[([^]|]+)(?:\|[^]]+)?\]\]',INDEX)[2:29]
assert len(LINKS)==27
CODES=['MAT','MRK','LUK','JHN','ACT','ROM','1CO','2CO','GAL','EPH','PHP','COL','1TH','2TH','1TI','2TI','TIT','PHM','HEB','JAS','1PE','2PE','1JN','2JN','3JN','JUD','REV']
def fetch(title):
 p=HOME/(hashlib.sha256(title.encode()).hexdigest()+'.json')
 if p.exists():return json.loads(p.read_text())
 url='https://he.wikisource.org/w/api.php?'+urllib.parse.urlencode(dict(action='parse',page=title,prop='wikitext|revid',format='json',maxlag=5))
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ParallelBibleReader/1.8 historical text acquisition'}),timeout=30) as r:d=json.load(r)
   if 'parse' not in d:raise ValueError(str(d))
   p.write_text(json.dumps(d,ensure_ascii=False));return d
  except Exception:
   if attempt==2:raise
   time.sleep(1)

def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:books=list(ex.map(fetch,LINKS))
 jobs=[];manifest=[]
 for code,title,book in zip(CODES,LINKS,books):
  w=book['parse']['wikitext']['*'];chapters=list(dict.fromkeys(x for x in re.findall(r'\[\[([^]|]+)(?:\|[^]]+)?\]\]',w) if (x.startswith(title+' ') or x.startswith(title+'/')) and 'פרק' in x))
  if not chapters:chapters=[title]
  for i,t in enumerate(chapters,1):jobs.append(t);manifest.append(dict(book=code,chapter=i,title=t))
 assert len(jobs)<=280,len(jobs)
 print('Historical Delitzsch source pages:',len(jobs),flush=True)
 # Batch query reduces server load. Cached pages are never requested again.
 assert len(jobs)==260,len(jobs)
 missing=[m for m in manifest if not (HOME/(hashlib.sha256(m['title'].encode()).hexdigest()+'.json')).exists()]
 for offset in range(0,len(missing),10):
  batch=missing[offset:offset+10]
  url='https://he.wikisource.org/w/api.php?'+urllib.parse.urlencode(dict(action='query',prop='revisions',rvprop='ids|content',rvslots='main',titles='|'.join(m['title'] for m in batch),format='json',formatversion=2,maxlag=5))
  for attempt in range(4):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ParallelBibleReader/1.8 (https://github.com/Kimble-365/-parallel-bible-reader) historical source acquisition'}),timeout=35) as response:d=json.load(response)
    if 'error' in d:raise ValueError(str(d['error']))
    pages=d['query']['pages'];bytitle={page['title']:page for page in pages}
    for m in batch:
     page=bytitle[m['title']];revision=page['revisions'][0];parsed={'parse':{'title':page['title'],'revid':revision['revid'],'wikitext':{'*':revision['slots']['main']['content']}}};(HOME/(hashlib.sha256(m['title'].encode()).hexdigest()+'.json')).write_text(json.dumps(parsed,ensure_ascii=False))
    break
   except urllib.error.HTTPError as e:
    if e.code not in [429,503] or attempt==3:raise
    delay=int(e.headers.get('Retry-After','60'));print('Source rate limit; respecting Retry-After:',delay,'seconds',flush=True)
    while delay>0:pause=min(delay,60);time.sleep(pause);delay-=pause
  print('Cached batch',min(offset+10,len(missing)),'of',len(missing),'missing pages',flush=True);time.sleep(2)
 for m in manifest:
  d=json.loads((HOME/(hashlib.sha256(m['title'].encode()).hexdigest()+'.json')).read_text());m['revid']=d['parse']['revid'];m['cache']=hashlib.sha256(m['title'].encode()).hexdigest()+'.json'
 for m in manifest:
  cached=json.loads((HOME/m['cache']).read_text())['parse']
  if cached['title']!=m['title']:m['redirect_from']=m['title'];m['title']=cached['title']
 (HOME/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('Acquired',len(manifest),'pages',flush=True)
if __name__=='__main__':main()
