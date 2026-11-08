"""Select only jobs affected by a patch; workflow steps are compared per job."""
import copy,json,os,subprocess
from pathlib import Path
import yaml
JOBS=('reader','desktop','android','ios','dependency-audit')
WORKFLOW='.github/workflows/reader-native-20.yml'
def job_body(job):
 job=copy.deepcopy(job or {});job.pop('needs',None);job.pop('if',None);return job

def select(paths,old,new,dispatch=False):
 result={j:dispatch for j in JOBS}
 for path in paths:
  if path==WORKFLOW:
   for j in JOBS:
    if job_body(old.get('jobs',{}).get(j))!=job_body(new.get('jobs',{}).get(j)):result[j]=True
  elif path=='tools/local/native_ci_scope_20.py':
   # The selector has its own fixture checks in the always-run scope job.
   pass
  elif path.startswith(('apps/native-20/','releases/v2.0/')) or path in ('tools/package_reader_20.py','tools/local/prepare_native_20.py'):
   for j in JOBS:result[j]=True
  elif path=='tools/local/reader_native_20.ps1':result['desktop']=True
  elif path.startswith('tests/') or path=='tools/local/export_reading_volumes.py':result['reader']=True
 return result

def self_test():
 old={'jobs':{'android':{'steps':[{'run':'old SDK'}]},'desktop':{'steps':[{'run':'cargo build'}]}}};new=copy.deepcopy(old);new['jobs']['android']['steps'][0]['run']='fixed SDK';new['jobs']['desktop']['needs']='scope';new['jobs']['desktop']['if']='scope output'
 r=select([WORKFLOW],old,new);assert r['android'] and not any(v for k,v in r.items() if k!='android')
 assert all(select(['apps/native-20/src-tauri/Cargo.lock'],old,old).values())
 assert select(['tools/local/reader_native_20.ps1'],old,old)['desktop']
 assert select(['tests/browser_engines_20.py'],old,old)['reader']
 assert not any(select(['PROJECT_PROGRESS.md'],old,old).values())
 assert all(select([],old,old,True).values())
 print('PASS CI scope: isolated SDK workflow change selects Android only; shared native changes select all; PowerShell/browser checks and dispatch retained')

def main():
 self_test();new=yaml.safe_load(Path(WORKFLOW).read_text());old=yaml.safe_load(subprocess.check_output(['git','show','HEAD^:'+WORKFLOW],text=True));paths=subprocess.check_output(['git','diff','--name-only','HEAD^','HEAD'],text=True).splitlines();result=select(paths,old,new,os.environ.get('GITHUB_EVENT_NAME')=='workflow_dispatch')
 print(json.dumps(result))
 with open(os.environ['GITHUB_OUTPUT'],'a') as f:
  for k,v in result.items():f.write(k+'='+str(v).lower()+'\n')
if __name__=='__main__':main()
