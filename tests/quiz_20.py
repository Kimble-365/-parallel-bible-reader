from pathlib import Path
import sys,json,hashlib,unittest,threading
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools/local'))
from quiz_server_20 import QuizStore,QuizError
BANK=json.loads((R/'releases/v2.0/quiz-bank.json').read_text())['questions']
class QuizTests(unittest.TestCase):
 def test_bank_sources(self):
  self.assertEqual(len(BANK),60);self.assertEqual(len({q['id'] for q in BANK}),60);books={}
  for q in BANK:
   self.assertEqual(len(q['options']),4);self.assertEqual(len(set(q['options'])),4);b,c,v=q['ref'].split('.')
   if b not in books:books[b]=json.loads((R/'data'/f'{b}.js').read_text().split(f'window.BibleBooks["{b}"]=',1)[1].rstrip(';\n'))['editions']['engwebp']
   text=next(r[2] for r in books[b] if str(r[0])==c and str(r[1])==v);self.assertEqual(text,q['verse']);self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),q['source_sha256']);self.assertIn(q['options'][q['answer']].lower(),text.lower())
  for level in range(1,11):self.assertEqual(sum(q['level']==level for q in BANK),6)
  self.assertEqual(json.loads((R/'releases/v2.0/quiz-data.js').read_text().split('=',1)[1].strip().removesuffix(';')),BANK)
 def setUp(self):
  self.now=1000;self.s=QuizStore(BANK,lambda:self.now);self.h=self.s.call('create',{'level':1});self.pin=self.h['pin'];self.a=self.s.call('join',{'pin':self.pin,'name':'Ada'});self.b=self.s.call('join',{'pin':self.pin,'name':'Bob'})
 def call(self,op,who=None,**kw):return self.s.call(op,{'pin':self.pin,**kw},(who or self.h)['token'])
 def test_round_and_authority(self):
  with self.assertRaises(QuizError):self.call('start',self.a)
  self.call('start');seen=set()
  for i in range(5):
   state=self.call('state',self.a);q=state['question'];self.assertNotIn(q['id'],seen);seen.add(q['id']);self.assertNotIn('answer',q);self.assertNotIn('verse',q);self.assertNotIn('score',state['players'][0]);answer=self.s.rooms[self.pin]['deck'][i]['answer']
   self.call('answer',self.a,question=q['id'],choice=answer)
   with self.assertRaises(QuizError):self.call('answer',self.a,question=q['id'],choice=answer)
   with self.assertRaises(QuizError):self.call('answer',self.b,question='stale',choice=answer)
   self.call('answer',self.b,question=q['id'],choice=(answer+1)%4);r=self.call('reveal');self.assertEqual(r['question']['answer'],answer);self.assertEqual(r['players'][0]['score'],1000*(i+1));self.assertEqual(r['players'][1]['score'],0)
   with self.assertRaises(QuizError):self.call('answer',self.b,question=q['id'],choice=answer)
   self.call('next')
  self.assertEqual(self.call('state')['phase'],'finished')
 def test_timer_and_tokens(self):
  self.call('start');q=self.call('state')['question'];self.now+=31
  with self.assertRaises(QuizError):self.call('answer',self.a,question=q['id'],choice=0)
  self.assertEqual(self.call('state')['phase'],'reveal')
  with self.assertRaises(QuizError):self.s.call('state',{'pin':self.pin},'wrong')
  self.now+=7201
  with self.assertRaises(QuizError):self.call('state')
 def test_concurrent_duplicate(self):
  self.call('start');q=self.s.rooms[self.pin]['deck'][0];results=[]
  def answer():
   try:self.call('answer',self.a,question=q['id'],choice=q['answer']);results.append('ok')
   except QuizError:results.append('rejected')
  ts=[threading.Thread(target=answer) for _ in range(8)]
  for t in ts:t.start()
  for t in ts:t.join()
  self.assertEqual(results.count('ok'),1);self.assertEqual(self.s.rooms[self.pin]['players'][self.a['token']]['score'],1000)
 def test_names_levels_decks(self):
  with self.assertRaises(QuizError):self.s.call('join',{'pin':self.pin,'name':'ADA'})
  for level in [0,11,True,'1']:
   with self.assertRaises(QuizError):self.s.call('create',{'level':level})
  for level in range(1,11):
   h=self.s.call('create',{'level':level});deck=self.s.rooms[h['pin']]['deck'];self.assertEqual(len(deck),5);self.assertEqual(len({q['id'] for q in deck}),5);self.assertTrue(all(q['level']==level for q in deck))
if __name__=='__main__':unittest.main(verbosity=2)
