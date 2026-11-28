"""Opt-in trusted-LAN quiz host. No cloud service, account or persistent player data."""
import argparse,json,secrets,time,threading,re
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlsplit

class QuizError(Exception):
 def __init__(self,message,status=400):self.status=status;super().__init__(message)

class QuizStore:
 def __init__(self,bank,clock=time.time):self.bank=bank;self.rooms={};self.lock=threading.RLock();self.clock=clock
 def call(self,op,d,token=''):
  with self.lock:
   now=self.clock();self.rooms={k:r for k,r in self.rooms.items() if now-r['created']<7200}
   if op=='create':
    if len(self.rooms)>=16:raise QuizError('Host is full. Try later.',429)
    level=d.get('level');count=d.get('count',5);seconds=d.get('seconds',30)
    if type(level)!=int or not 1<=level<=10 or count!=5 or type(seconds)!=int or seconds not in [0,30,60]:raise QuizError('Invalid game settings.')
    deck=[dict(q) for q in self.bank if q['level']==level];secrets.SystemRandom().shuffle(deck);deck=deck[:count]
    if len(deck)!=count:raise QuizError('Not enough questions for this level.')
    for q in deck:
     choices=list(enumerate(q['options']));secrets.SystemRandom().shuffle(choices);q['answer']=next(i for i,(old,_) in enumerate(choices) if old==q['answer']);q['options']=[x[1] for x in choices]
    pin=str(secrets.randbelow(900000)+100000)
    while pin in self.rooms:pin=str(secrets.randbelow(900000)+100000)
    host=secrets.token_urlsafe(32);self.rooms[pin]={'created':now,'host':host,'deck':deck,'players':{},'phase':'lobby','index':-1,'seconds':seconds,'deadline':None,'level':level,'version':0}
    return {'pin':pin,'token':host,'role':'host'}
   pin=d.get('pin','');r=self.rooms.get(pin)
   if not r:raise QuizError('Game not found or expired.',404)
   if op=='join':
    name=d.get('name','')
    if not isinstance(name,str) or not 1<=len(name.strip())<=24 or any(ord(c)<32 for c in name):raise QuizError('Use a name of 1–24 characters.')
    if r['phase']!='lobby':raise QuizError('This game has already started.',409)
    if len(r['players'])>=32:raise QuizError('Game is full.',429)
    if any(p['name'].casefold()==name.strip().casefold() for p in r['players'].values()):raise QuizError('That name is already in use.',409)
    r['version']+=1;key=secrets.token_urlsafe(32);r['players'][key]={'name':name.strip(),'score':0,'answer':None,'answered':False};return {'pin':pin,'token':key,'role':'player'}
   host=secrets.compare_digest(token,r['host'])
   if not host and token not in r['players']:raise QuizError('Rejoin with your saved player session.',403)
   if r['phase']=='question' and r['deadline'] and now>=r['deadline']:r['phase']='reveal';r['version']+=1
   if op in ['start','next','reveal','close']:
    if not host:raise QuizError('Only the host can control the game.',403)
    if op=='close':del self.rooms[pin];return {'closed':True}
    if op=='reveal':
     if r['phase']!='question':raise QuizError('No open question.',409)
     r['phase']='reveal';r['version']+=1
    elif op=='start' or op=='next':
     if (op=='start' and r['phase']!='lobby') or (op=='next' and r['phase']!='reveal'):raise QuizError('Wait for the current question.',409)
     if not r['players']:raise QuizError('Wait for at least one player.',409)
     r['index']+=1;r['version']+=1
     if r['index']>=len(r['deck']):r['phase']='finished'
     else:
      r['phase']='question';r['deadline']=now+r['seconds'] if r['seconds'] else None
      for p in r['players'].values():p.update(answer=None,answered=False)
   elif op=='answer':
    if host:raise QuizError('Join as a player to answer.',403)
    if r['phase']!='question' or d.get('question')!=r['deck'][r['index']]['id']:raise QuizError('This question is closed.',409)
    p=r['players'][token];choice=d.get('choice')
    if p['answered']:raise QuizError('Answer already recorded.',409)
    if type(choice)!=int or not 0<=choice<4:raise QuizError('Invalid answer.')
    p.update(answer=choice,answered=True);r['version']+=1
    if choice==r['deck'][r['index']]['answer']:p['score']+=1000
   elif op!='state':raise QuizError('Unknown operation.',404)
   # Before reveal, scores and correct answers are withheld from all clients.
   reveal=r['phase'] in ['reveal','finished'];q=r['deck'][r['index']] if 0<=r['index']<len(r['deck']) else None
   public={k:q[k] for k in ['id','prompt','options']} if q else None
   if public and reveal:public.update({k:q[k] for k in ['answer','ref','verse','edition']})
   return {'version':r['version'],'pin':pin,'role':'host' if host else 'player','phase':r['phase'],'level':r['level'],'question':public,'number':min(r['index']+1,len(r['deck'])),'total':len(r['deck']),'remaining':max(0,int(r['deadline']-now+0.999)) if r['deadline'] and r['phase']=='question' else None,'players':[{'name':p['name'],'answered':p['answered'],**({'score':p['score']} if reveal else {})} for p in r['players'].values()],'me':None if host else {'name':r['players'][token]['name'],'answered':r['players'][token]['answered']}}

def handler(root,store):
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*a,**k):super().__init__(*a,directory=str(root),**k)
  def log_message(self,*a):pass # Never log player tokens/names or request bodies.
  def do_POST(self):
   try:
    origin=self.headers.get('Origin');host=self.headers.get('Host','')
    if origin and urlsplit(origin).netloc!=host:raise QuizError('Origin rejected.',403)
    if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise QuizError('JSON required.',415)
    length=int(self.headers.get('Content-Length','0'))
    if not 0<length<=4096:raise QuizError('Request too large.',413)
    if not self.path.startswith('/api/quiz/'):raise QuizError('Not found.',404)
    data=json.loads(self.rfile.read(length))
    if not isinstance(data,dict):raise QuizError('Invalid request.')
    auth=self.headers.get('Authorization','');token=auth[7:] if auth.startswith('Bearer ') else ''
    result=store.call(self.path.removeprefix('/api/quiz/'),data,token);self.reply(200,result)
   except QuizError as e:self.reply(e.status,{'error':str(e)})
   except (ValueError,TypeError,KeyError):self.reply(400,{'error':'Invalid request.'})
  def reply(self,status,data):
   raw=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  def do_GET(self):
   path=urlsplit(self.path).path
   # Only the static reader tree is shared; never serve .git, profiles or local tools.
   resolved=Path(self.translate_path(path)).resolve()
   if any(x.startswith('.') for x in Path(path).parts) or not resolved.is_relative_to(root.resolve()) or any(x.startswith('.') for x in resolved.relative_to(root.resolve()).parts) or not path.startswith(('/releases/','/data/','/reader-guides.js','/LICENSE')):
    self.send_error(404);return
   if resolved.is_dir() and not (resolved/'index.html').is_file():self.send_error(404);return
   super().do_GET()
 return Handler

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=(Path(__file__).resolve().parent if (Path(__file__).resolve().parent/'releases/v2.0').is_dir() else Path(__file__).resolve().parents[2]));p.add_argument('--port',type=int,default=8766);p.add_argument('--lan',action='store_true',help='Share with devices on your trusted local network');a=p.parse_args()
 if not 1024<=a.port<=65535:p.error('Choose a port from 1024 to 65535.')
 root=a.root.resolve();bank=json.loads((root/'releases/v2.0/quiz-bank.json').read_text())['questions'];server=ThreadingHTTPServer(('0.0.0.0' if a.lan else '127.0.0.1',a.port),handler(root,QuizStore(bank)))
 print(f'Open http://127.0.0.1:{a.port}/releases/v2.0/quiz.html',flush=True)
 if a.lan:print(f'Phones: open http://<this-computer-LAN-IP>:{a.port}/releases/v2.0/quiz.html on the same Wi-Fi. Allow this port only on your trusted local network. No Internet port forwarding.',flush=True)
 print('Temporary games: up to 32 players each; lost when the host stops. Ctrl+C to stop.',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
