"""Create an explicitly experimental CMUdict-derived phoneme aid for WEB English.
No homograph/context inference. Unknown words remain marked; original text is retained.
"""
from pathlib import Path
import json,re,sqlite3,hashlib
ROOT=Path(__file__).resolve().parents[1];SRC=Path('/workspace/reader-new-sources');OUT=ROOT/'releases/v1.6/pronunciation';OUT.mkdir(parents=True,exist_ok=True)
PH={'AA':'ɑ','AE':'æ','AH':'ʌ','AO':'ɔ','AW':'aʊ','AY':'aɪ','B':'b','CH':'tʃ','D':'d','DH':'ð','EH':'ɛ','ER':'ɝ','EY':'eɪ','F':'f','G':'ɡ','HH':'h','IH':'ɪ','IY':'i','JH':'dʒ','K':'k','L':'l','M':'m','N':'n','NG':'ŋ','OW':'oʊ','OY':'ɔɪ','P':'p','R':'ɹ','S':'s','SH':'ʃ','T':'t','TH':'θ','UH':'ʊ','UW':'u','V':'v','W':'w','Y':'j','Z':'z','ZH':'ʒ'}
def ipa(phones):
 return ''.join('ə' if x=='AH0' else 'ɚ' if x=='ER0' else PH[re.sub('[012]$','',x)] for x in phones)
def main():
 db=sqlite3.connect('file:/workspace/biblical-encyclopedia/encyclopedia.sqlite3?mode=ro',uri=True);words=[]
 for row in db.execute("SELECT original FROM bible_verses WHERE edition='engwebp'"):words.extend(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*",row[0].lower().replace('’',"'")))
 db.close();wanted=set(words);dictionary={};variants={}
 for line in (SRC/'cmudict.dict').read_text().splitlines():
  content=line.split('#',1)[0].split()
  if len(content)<2:continue
  word=re.sub(r'\(\d+\)$','',content[0]);phones=content[1:]
  if word not in wanted:continue
  result=ipa(phones);variants.setdefault(word,[])
  if result not in variants[word]:variants[word].append(result)
  if word not in dictionary:dictionary[word]=result
 report=dict(version='1.6',type='dictionary-based broad phonemic estimate',language='en-US-fonipa',source='https://github.com/cmusphinx/cmudict',source_sha256=hashlib.sha256((SRC/'cmudict.dict').read_bytes()).hexdigest(),vocabulary=len(wanted),dictionary_matches=len(dictionary),tokens=len(words),covered_tokens=sum(w in dictionary for w in words),ambiguous_words=sum(len(v)>1 for v in variants.values()),limitations=['first listed pronunciation only; no context/homograph resolution','not colloquial translation or narrow phonetic transcription','stress and syllable boundaries omitted','unknown words shown as ⟦source word⟧','pipeline not speaker-reviewed'])
 (OUT/'english-ga.js').write_text('window.EnglishPronunciations='+json.dumps(dictionary,ensure_ascii=False,separators=(',',':'))+';')
 (OUT/'CMUDICT-LICENSE.txt').write_bytes((SRC/'CMUDICT-LICENSE.txt').read_bytes());(OUT/'manifest.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
