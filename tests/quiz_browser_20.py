from pathlib import Path
import sys,json,threading,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools/local'))
from quiz_server_20 import QuizStore,handler
bank=json.loads((R/'releases/v2.0/quiz-bank.json').read_text())['questions'];answers={q['id']:q['options'][q['answer']] for q in bank}
server=ThreadingHTTPServer(('127.0.0.1',0),handler(R,QuizStore(bank)));threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}';base=origin+'/releases/v2.0/quiz.html'
try:
 for path in ['/.git/config','/releases/%2e%2e/%2egit/config','/tools/local/quiz_server_20.py']:
  try:urllib.request.urlopen(origin+path);raise AssertionError(path)
  except urllib.error.HTTPError as e:assert e.code==404
 req=urllib.request.Request(origin+'/api/quiz/create',data=b'{"level":1}',headers={'Content-Type':'application/json','Origin':'https://wrong.example'})
 try:urllib.request.urlopen(req);raise AssertionError('Cross-origin accepted')
 except urllib.error.HTTPError as e:assert e.code==403
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[]
  solo=b.new_context(viewport={'width':390,'height':844});page=solo.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base);page.evaluate('localStorage.setItem("parallel-reader-notes-v1","preserve-me")');page.select_option('#seconds','0');page.click('#solo');page.wait_for_selector('#choices button')
  for i in range(5):page.locator('#choices button').first.click();page.wait_for_selector('#explanation:not([hidden])');assert page.locator('#verse').inner_text();page.click('#advance')
  assert page.locator('#heading').inner_text()=='Round complete';assert page.evaluate('localStorage.getItem("parallel-reader-notes-v1")')=='preserve-me';page.click('#leave');page.select_option('#level','10');page.click('#solo');assert 'Level 10' in page.locator('#progress').inner_text();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.click('#leave');page.wait_for_function('!!navigator.serviceWorker.controller');solo.set_offline(True);page.reload();page.wait_for_selector('#solo');page.click('#solo');page.locator('#choices button').first.click();page.wait_for_selector('#explanation:not([hidden])');solo.close()
  host=b.new_context(viewport={'width':1280,'height':900});hp=host.new_page();hp.on('pageerror',lambda e:errors.append(str(e)));hp.goto(base);hp.select_option('#seconds','0');hp.click('#host');hp.wait_for_function('document.querySelector("#heading").textContent.startsWith("Game code:")');pin=hp.locator('#heading').inner_text().split(': ')[1]
  players=[]
  for name in ['Ada','Bob']:
   ctx=b.new_context(viewport={'width':390,'height':844});gp=ctx.new_page();gp.on('pageerror',lambda e:errors.append(str(e)));gp.goto(base);gp.fill('#pin',pin);gp.fill('#name',name);gp.locator('#join button').click();gp.wait_for_function('document.querySelector("#status").textContent.includes("Waiting") || !document.querySelector("#game").hidden');players.append((ctx,gp))
  hp.wait_for_function('document.querySelectorAll("#players li").length===2');hp.click('#advance')
  for i in range(5):
   for ctx,gp in players:gp.wait_for_function('(n)=>document.querySelector("#progress").textContent.includes("Question "+n+" of")',arg=i+1);gp.wait_for_selector('#choices button:not([disabled])')
   qid=hp.evaluate('JSON.parse(sessionStorage.getItem("reader-quiz-session-v1"))').get('pin');assert qid==pin
   # Choose the first answer on both devices; server still owns scoring.
   for ctx,gp in players:gp.locator('#choices button').first.click();gp.wait_for_function('document.querySelectorAll("#choices button:not([disabled])").length===0')
   hp.wait_for_function('Array.from(document.querySelectorAll("#players li")).every(e=>e.textContent.includes("Answer received"))');hp.click('#reveal');hp.wait_for_selector('#explanation:not([hidden])');assert hp.locator('#verse').inner_text();hp.click('#advance')
  hp.wait_for_function('document.querySelector("#heading").textContent==="Final scores"');assert hp.locator('#players li').count()==2
  # Reconnect uses the tab token, preserving the finished score.
  gp=players[0][1];gp.reload();gp.click('#resume');gp.wait_for_function('document.querySelector("#heading").textContent==="Final scores"');assert 'Ada' in gp.locator('#players').inner_text();assert not errors,errors
  for ctx,gp in players:ctx.close()
  host.close();b.close()
 print('PASS quiz: solo 390px, five questions/results, level 10, unchanged Notes, offline reload; independent host and two phone-size clients, PIN join, five live rounds, reveal/scoreboard, session reconnect; static traversal and cross-origin API rejection')
finally:server.shutdown();server.server_close()
