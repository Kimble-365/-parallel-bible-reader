"""Read actual native review package bytes without executing or extracting applications."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import plistlib
import re
import struct
import subprocess
import tarfile
import zipfile


def safe(name):
    p=PurePosixPath(name.replace('\\','/'))
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('Unsafe archive member')
    return str(p)


def identity(stream):
    h=hashlib.sha256();size=0;head=b''
    while True:
        b=stream.read(1024*1024)
        if not b:break
        if len(head)<64:head=(head+b)[:64]
        h.update(b);size+=len(b)
    result={'bytes':size,'sha256':h.hexdigest()}
    if head.startswith(b'\x7fELF') and len(head)>=20:
        result['binary']={'format':'ELF','class':head[4],'machine':int.from_bytes(head[18:20],'little' if head[5]==1 else 'big')}
    elif head[:4] in (b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf'):
        result['binary']={'format':'Mach-O64','cpu_type':struct.unpack('<I' if head[:4]==b'\xcf\xfa\xed\xfe' else '>I',head[4:8])[0]}
    elif head.startswith(b'MZ'):result['binary']={'format':'PE/DOS-stub','payload_architecture_not_inferred':True}
    return result


def inspect(path,kind,run=subprocess.run):
    path=Path(path)
    with path.open('rb') as f: outer=identity(f)
    result={'package':path.name,'kind':kind,**outer,'members':[],
            'application_executed':False,'embedded_frontend_resources_decoded':False,
            'public_release_approved':False}
    seen=set()
    def add(name,stream=None,**extra):
        name=safe(name)
        if name in seen:raise ValueError('Duplicate archive member')
        seen.add(name);entry={'path':name,**extra}
        if stream is not None:entry.update(identity(stream))
        result['members'].append(entry)
    if kind=='android':
        with zipfile.ZipFile(path) as z:
            for m in z.infolist():
                if not m.is_dir():
                    with z.open(m) as f:add(m.filename,f)
            if 'AndroidManifest.xml' not in seen:raise ValueError('Missing Android manifest')
        native=[p for p in result['members'] if p['path'].startswith('lib/arm64-v8a/') and p['path'].endswith('.so')]
        if not native or any(p.get('binary',{}).get('machine')!=183 for p in native):raise ValueError('Expected ARM64 Android shared libraries')
        result['classification']='Android debug review APK; no signing/physical-device verification'
    elif kind in ('macos','ios'):
        plists=[]
        with tarfile.open(path,'r:gz') as t:
            for m in t:
                if m.isfile():
                    with t.extractfile(m) as f:add(m.name,f)
                    if m.name.endswith('/Info.plist'):
                        with t.extractfile(m) as f:plists.append({'path':safe(m.name),'value':plistlib.load(f)})
                elif m.issym() or m.islnk():add(m.name,link_target=m.linkname,link_dereferenced=False)
                elif not m.isdir():raise ValueError('Unsupported special archive member')
        result['bundle_identities']=[{'path':p['path'],'identifier':p['value'].get('CFBundleIdentifier'),
                                      'version':p['value'].get('CFBundleShortVersionString'),
                                      'executable':p['value'].get('CFBundleExecutable')} for p in plists]
        if not any(p.get('identifier')=='org.kimble365.parallelbiblereader' for p in result['bundle_identities']):
            raise ValueError('Expected app bundle identifier not found')
        if not any(p.get('binary',{}).get('format')=='Mach-O64' for p in result['members']):raise ValueError('Expected Mach-O executable')
        result['classification']='Unsigned Mac review app' if kind=='macos' else 'iOS simulator review app; not a physical-device IPA'
    elif kind=='windows':
        if outer.get('binary',{}).get('format')!='PE/DOS-stub':raise ValueError('Expected PE installer')
        listing=run(['7z','l','-slt',str(path)],capture_output=True,text=True,check=True).stdout
        if not re.search(r'(?:Parallel Bible Reader|parallel-bible-reader)\.exe',listing,re.I):raise ValueError('Expected application payload missing from installer listing')
        result['installer_listing']=listing
        result['installer_listing_sha256']=hashlib.sha256(listing.encode()).hexdigest()
        result['classification']='Unsigned Windows NSIS review installer; installer stub architecture is not payload architecture'
    else:raise ValueError('Unknown package kind')
    result['loose_notice_path_candidates']=[p['path'] for p in result['members'] if any(x in p['path'].lower() for x in ('license','licence','notice','copyright'))]
    result['limits']=['File inventory and binary headers are static evidence, not native GUI/device execution or full linked-component/licence assessment.',
                      'No loose notice path is not proof of absent embedded notices; Tauri frontend assets can be embedded/compressed in executable resources.',
                      'Symbolic/hard links are recorded without dereferencing; no archive member is extracted or executed.']
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path',required=True)
    parser.add_argument('--kind',choices=('macos','ios','android','windows'),required=True)
    parser.add_argument('--source-commit',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    paths=sorted(Path('.').glob(args.path))
    if not paths:raise ValueError('No actual package matched')
    reports=[inspect(p,args.kind) for p in paths]
    result={'source_commit':args.source_commit,'packages':reports,'native_gui_tested':False,'public_release_approved':False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for r in reports:
        print(json.dumps({k:r[k] for k in ('package','kind','bytes','sha256','classification')}|{'members':len(r['members']),'binary_headers':[p for p in r['members'] if 'binary' in p],'bundle_identities':r.get('bundle_identities',[]),'loose_notice_candidates':r['loose_notice_path_candidates']}))
