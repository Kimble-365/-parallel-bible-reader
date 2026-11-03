"""Incremental OSHB book shards and deterministic WLEXPACK/1. Python stdlib only."""
from pathlib import Path
import argparse, gzip, hashlib, io, json, os, re, sqlite3, sys, tempfile, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
VERSION = '1'
SOURCE_REVISION = '3d15126fb1ef74867fc1434be1942e837932691f'
LEXICON_REVISION = '21c9add13bc727d3a951361778e97e3ff7afd1ce'
BOOKS = [('Gen','GEN'),('Exod','EXO'),('Lev','LEV'),('Num','NUM'),('Deut','DEU'),('Josh','JOS'),('Judg','JDG'),('Ruth','RUT'),('1Sam','1SA'),('2Sam','2SA'),('1Kgs','1KI'),('2Kgs','2KI'),('1Chr','1CH'),('2Chr','2CH'),('Ezra','EZR'),('Neh','NEH'),('Esth','EST'),('Job','JOB'),('Ps','PSA'),('Prov','PRO'),('Eccl','ECC'),('Song','SNG'),('Isa','ISA'),('Jer','JER'),('Lam','LAM'),('Ezek','EZK'),('Dan','DAN'),('Hos','HOS'),('Joel','JOL'),('Amos','AMO'),('Obad','OBA'),('Jonah','JON'),('Mic','MIC'),('Nah','NAM'),('Hab','HAB'),('Zeph','ZEP'),('Hag','HAG'),('Zech','ZEC'),('Mal','MAL')]
METRICS = ('ingested','morphologically_analyzed','semantically_reviewed','manuscript_checked','translations_checked','fully_verified')
MAX_SQLITE = 128 * 1024 * 1024
MAX_PACK = 32 * 1024 * 1024

def digest(data): return hashlib.sha256(data).hexdigest()
def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',',':')).encode('utf-8')
def tag(e): return e.tag.rsplit('}',1)[-1]
def atomic(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp'); tmp.write_bytes(data); tmp.replace(path)

def source_records(inputs, book):
    """Optional private research stays in private packs, with original review states."""
    if not inputs: return []
    result=[]
    for relative in ['BHH/data/alignments.jsonl','BHH/data/variants.jsonl','LXXL/data/unit-evidence.jsonl']:
        path=Path(inputs)/relative
        if not path.exists(): continue
        raw=path.read_bytes()
        for line in raw.decode().splitlines():
            r=json.loads(line); locus=r.get('locus','')
            if not locus.startswith(book+'.'): continue
            result.append((relative,digest(raw),r))
    return result

def display_projection(verse, add_word):
    """Only explicit source elements define words; XML indentation is not scripture."""
    events=[]; words=[]; last_main=None; position=0
    def add(text, token=None):
        if text: events.append([text, token])
    def space():
        if events and not events[-1][0].endswith((' ','־')): add(' ')
    def word(e, attestation, aligned=None):
        nonlocal position
        position+=1
        token=add_word(e,position,attestation,aligned)
        words.append(token)
        return token
    for e in verse:
        kind=tag(e)
        if kind=='w':
            space(); t=word(e,'ketiv' if e.get('type')=='x-ketiv' else 'main')
            last_main=t; add(t['display_form'],t['id'])
        elif kind=='seg':
            text=''.join(e.itertext())
            if e.get('type') not in ('x-maqqef','x-sof-pasuq'): space()
            add(text)
            if e.get('type') not in ('x-maqqef',): add(' ')
        elif kind=='note':
            for reading in e.findall('.//{*}rdg'):
                att='qere' if reading.get('type')=='x-qere' else 'alternative'
                for w in reading.findall('.//{*}w'):
                    word(w,att,last_main['id'] if last_main and last_main['attestation']=='ketiv' else None)
        else:
            raise ValueError('Unhandled verse element '+kind)
    while events and events[-1][0]==' ': events.pop()
    offset=0
    byid={t['id']:t for t in words}
    for text,tid in events:
        if tid: byid[tid].update(display_start=offset,display_end=offset+len(text))
        offset+=len(text)
    return events,words

def build_book(source_dir, book, out, revision=SOURCE_REVISION, research=None, lexicon=None):
    code=dict(BOOKS)[book]; source=Path(source_dir)/(book+'.xml'); raw=source.read_bytes()
    sha=digest(raw); records=source_records(research,book)
    lexbytes=Path(lexicon).read_bytes() if lexicon else b''
    fingerprint=digest(canonical({'source':sha,'revision':revision,'schema':digest((ROOT/'schema.sql').read_bytes()),'builder':digest(Path(__file__).read_bytes()),'research':records,'lexicon':digest(lexbytes)}))
    out=Path(out); out.mkdir(parents=True,exist_ok=True); dbpath=out/(code+'.sqlite'); checkpoint=out/(code+'.checkpoint.json')
    if checkpoint.exists() and dbpath.exists():
        saved=json.loads(checkpoint.read_text())
        if saved.get('fingerprint')==fingerprint and saved.get('sqlite_sha256')==digest(dbpath.read_bytes()):
            audit_book(dbpath,raw); return saved|{'resumed':True}
    fd,temp=tempfile.mkstemp(dir=out,suffix='.sqlite');os.close(fd)
    db=sqlite3.connect(temp);db.executescript((ROOT/'schema.sql').read_text())
    sid='oshb:'+revision+':'+book
    db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(sid,f'https://github.com/openscriptures/morphhb/blob/{revision}/wlc/{book}.xml',revision,sha,'CC-BY-4.0','Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb'))
    db.execute('INSERT INTO source_files VALUES (?,?)',(sid,gzip.compress(raw,mtime=0)))
    # Byte slices include exact source serialization and all notes. Nothing is normalized.
    slices=list(re.finditer(rb'<verse\b[^>]*>.*?</verse>',raw,re.S))
    verses=ET.fromstring(raw).findall('.//{*}verse')
    if len(slices)!=len(verses): raise ValueError('Verse byte scanner mismatch')
    total=0; annotated=0; aramaic=0; alternatives=0
    for ordinal,(verse,match) in enumerate(zip(verses,slices),1):
        key=verse.get('osisID');parts=key.split('.')
        if len(parts)!=3 or parts[0]!=book: raise ValueError('Unsupported verse identity '+str(key))
        def add_word(e,position,attestation,aligned):
            nonlocal total,annotated,aramaic,alternatives
            form=''.join(e.itertext()); morphology=e.get('morph'); lemma=e.get('lemma')
            language='arc' if (morphology or '').startswith('A') else 'hbo' if (morphology or '').startswith('H') else 'und'
            tid=f'oshb:{revision}:{key}:{position}:0'
            total+=1; annotated+=bool(morphology); aramaic+=language=='arc'; alternatives+=attestation in ('qere','alternative')
            return dict(id=tid,verse_key=key,position=position,attestation=attestation,form=form,display_form=form.replace('/',''),lemma=lemma,morphology=morphology,language=language,source_word_id=e.get('id'),aligned_to=aligned,source_id=sid,verification='source_annotation',display_start=None,display_end=None)
        events,words=display_projection(verse,add_word)
        display=''.join(x[0] for x in events)
        db.execute('INSERT INTO verses VALUES (?,?,?,?,?,?,?,?,?)',(key,code,parts[1],parts[2],ordinal,display,match.group().decode('utf-8'),match.start(),match.end()))
        for w in words:
            db.execute('INSERT INTO tokens VALUES ('+','.join('?' for _ in w)+')',list(w.values()))
            forms=w['form'].split('/'); lemmas=(w['lemma'] or '').split('/'); morphs=(w['morphology'] or '')[1:].split('/')
            for n,form in enumerate(forms):
                # No inferred segment alignment when source list lengths differ.
                lemma=lemmas[n] if len(lemmas)==len(forms) else w['lemma'] if len(forms)==1 else None
                lid=w['language']+':'+lemma if lemma else None
                if lid: db.execute('INSERT OR IGNORE INTO lemmas(id,language,source_lemma,source_id,verification) VALUES (?,?,?,?,?)',(lid,w['language'],lemma,sid,'source_annotation'))
                db.execute('INSERT INTO token_segments VALUES (?,?,?,?,?,?)',(w['id'].rsplit(':',1)[0]+':'+str(n+1),w['id'],n+1,form,lid,morphs[n] if len(morphs)==len(forms) else None))
        db.executemany('INSERT INTO display_events VALUES (?,?,?,?)',[(key,n,text,tid) for n,(text,tid) in enumerate(events)])
    if lexbytes:
        lsid='oshb-strong:'+digest(lexbytes)
        db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(lsid,f'https://github.com/openscriptures/HebrewLexicon/blob/{LEXICON_REVISION}/HebrewStrong.xml',LEXICON_REVISION,digest(lexbytes),'CC-BY-4.0','Open Scriptures Hebrew Bible Project; Strong Hebrew Dictionary (1894), corrected digital edition'))
        entries={e.get('id'):e for e in ET.fromstring(lexbytes).findall('{*}entry')}
        for lid,lemma in db.execute('SELECT id,source_lemma FROM lemmas').fetchall():
            # Strong number is only a broad dictionary link; augmented homographs stay distinct.
            m=re.fullmatch(r'(\d+)(?: [a-z])?',lemma)
            e=entries.get('H'+m[1]) if m else None
            if e is None:continue
            w=e.find('{*}w')
            if w is None:continue
            meaning=e.find('{*}meaning');usage=e.find('{*}usage')
            gloss=''.join(meaning.itertext()) if meaning is not None else ''.join(usage.itertext()) if usage is not None else None
            db.execute('UPDATE lemmas SET headword=?,transliteration=?,gloss=?,source_id=?,verification=? WHERE id=?',(''.join(w.itertext()),w.get('xlit'),gloss,lsid,'historical_dictionary_generic_not_contextual',lid))
    for relative,rsha,r in records:
        rsid='theway:'+relative
        db.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?,?,?)',(rsid,'https://github.com/Kimble-365/TheWay/blob/d208ce9e0b537d4ba6c8bf222af8bad926721399/'+relative,'d208ce9e0b537d4ba6c8bf222af8bad926721399',rsha,'Mixed; see TheWay/BHH and LXXL third-party notices','Kimmo M. Leino / TheWay research projects and named underlying sources'))
        # Verse-level records: draft ordinal IDs are never guessed into new occurrence IDs.
        db.execute('INSERT INTO research_records VALUES (?,?,?,?,?,?,?)',(r['id'],r['locus'],None,rsid,r.get('evidence_class','editorial_draft'),r.get('status',r.get('verification','imported_unreviewed')),canonical(r).decode()))
    counts=dict.fromkeys(METRICS,0);counts['ingested']=total;counts['morphologically_analyzed']=annotated
    db.executemany('INSERT INTO research_progress VALUES (?,?)',counts.items())
    metadata={'schema_version':VERSION,'book':code,'source_book':book,'source_revision':revision,'source_sha256':sha,'fingerprint':fingerprint,'projection':'OSHB direct w/seg projection v1; slash segmentation hidden; ketiv primary; qere separate; notes preserved in source_xml','comparison':'Exact UTF-8 bytes for source_xml slices; exact Unicode codepoints for projected display; no normalization','scholarly_status':'pending','morphology_status':'imported source annotations; not independently reviewed','source_timestamp':'recorded in acquisition ledger, excluded from deterministic payload'}
    db.executemany('INSERT INTO metadata VALUES (?,?)',metadata.items());db.commit();db.execute('VACUUM');db.close()
    try:
        audit_book(Path(temp),raw)
        Path(temp).replace(dbpath)
    finally:
        Path(temp).unlink(missing_ok=True)
    report={'book':code,'source_book':book,'fingerprint':fingerprint,'source_sha256':sha,'source_revision':revision,'sqlite_sha256':digest(dbpath.read_bytes()),'sqlite_bytes':dbpath.stat().st_size,'verses':len(verses),'coverage':counts,'aramaic_tokens':aramaic,'alternative_tokens':alternatives,'research_records':len(records),'content_status':'source_annotations_research_pending'}
    atomic(checkpoint,canonical(report)+b'\n');return report

def audit_book(path, source=None):
    db=sqlite3.connect(f'file:{Path(path).resolve()}?mode=ro',uri=True)
    try:
        if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise ValueError('SQLite integrity failure')
        if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('SQLite foreign key failure')
        if db.execute('PRAGMA user_version').fetchone()[0]!=1:raise ValueError('Unsupported schema')
        raw=gzip.decompress(db.execute('SELECT gzip_bytes FROM source_files').fetchone()[0])
        sha=db.execute("SELECT value FROM metadata WHERE key='source_sha256'").fetchone()[0]
        if digest(raw)!=sha or (source is not None and raw!=source):raise ValueError('Source reconstruction failed')
        for key,text,xml,start,end in db.execute('SELECT verse_key,display_text,source_xml,byte_start,byte_end FROM verses'):
            if raw[start:end]!=xml.encode():raise ValueError('Source verse mismatch '+key)
            projected=''.join(r[0] for r in db.execute('SELECT text FROM display_events WHERE verse_key=? ORDER BY position',(key,)))
            if text!=projected:raise ValueError('Display reconstruction failed '+key)
            for form,a,b in db.execute('SELECT display_form,display_start,display_end FROM tokens WHERE verse_key=? AND display_start IS NOT NULL',(key,)):
                if text[a:b]!=form:raise ValueError('Token boundary mismatch '+key)
        count=db.execute('SELECT COUNT(*) FROM tokens').fetchone()[0]
        if count!=db.execute("SELECT count FROM research_progress WHERE metric='ingested'").fetchone()[0]:raise ValueError('Token completeness failure')
        return {'integrity':'ok','foreign_keys':'ok','source_reconstruction':'exact','tokens':count}
    finally: db.close()

def pack_book(dbpath, out):
    dbpath=Path(dbpath);audit_book(dbpath);payload=dbpath.read_bytes()
    if len(payload)>MAX_SQLITE:raise ValueError('Book exceeds memory cap')
    db=sqlite3.connect(dbpath);meta=dict(db.execute('SELECT key,value FROM metadata'));counts=dict(db.execute('SELECT metric,count FROM research_progress'));verses=db.execute('SELECT COUNT(*) FROM verses').fetchone()[0];db.close()
    embedded={'format':'wlexpack','version':1,'schema_version':1,'book':meta['book'],'payload':'book.sqlite','codec':'deflate','sqlite_sha256':digest(payload),'sqlite_bytes':len(payload),'source_sha256':meta['source_sha256'],'source_revision':meta['source_revision'],'build_fingerprint':meta['fingerprint'],'license':'CC-BY-4.0 (OSHB annotations); private research additions retain separate source terms','coverage':counts,'verses':verses,'content_status':'source_annotations_research_pending'}
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z:
        for name,data,codec in [('manifest.json',canonical(embedded),zipfile.ZIP_STORED),('book.sqlite',payload,zipfile.ZIP_DEFLATED)]:
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=codec;info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,data,compresslevel=9)
    packed=buf.getvalue()
    if len(packed)>MAX_PACK:raise ValueError('Packed book exceeds cap')
    out=Path(out);out.mkdir(parents=True,exist_ok=True);name=meta['book']+'.wlexpack'
    manifest=embedded|{'url':name,'packed_sha256':digest(packed),'packed_bytes':len(packed)}
    atomic(out/name,packed);atomic(out/(meta['book']+'.manifest.json'),canonical(manifest)+b'\n')
    verify_pack(out/name,manifest);return manifest

def verify_pack(path, manifest):
    packed=Path(path).read_bytes()
    if len(packed)>MAX_PACK or len(packed)!=manifest['packed_bytes'] or digest(packed)!=manifest['packed_sha256']:raise ValueError('Pack hash/length mismatch')
    with zipfile.ZipFile(io.BytesIO(packed)) as z:
        if z.namelist()!=['manifest.json','book.sqlite'] or z.testzip():raise ValueError('Invalid pack entries/CRC')
        for entry in z.infolist():
            if entry.flag_bits&1 or entry.file_size>MAX_SQLITE:raise ValueError('Unsafe pack entry')
        embedded=json.loads(z.read('manifest.json'));payload=z.read('book.sqlite')
        if any(manifest.get(k)!=v for k,v in embedded.items()):raise ValueError('Manifest mismatch')
        if embedded.get('format')!='wlexpack' or embedded.get('version')!=1 or embedded.get('schema_version')!=1:raise ValueError('Unsupported pack/schema')
        if len(payload)!=manifest['sqlite_bytes'] or digest(payload)!=manifest['sqlite_sha256']:raise ValueError('SQLite hash mismatch')
    with tempfile.NamedTemporaryFile(suffix='.sqlite') as f:
        f.write(payload);f.flush();audit_book(Path(f.name))
    return payload

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for cmd in ['import-wlc','build-book']:
        q=sub.add_parser(cmd);q.add_argument('--source',required=True);q.add_argument('--book',default='Gen');q.add_argument('--out',required=True);q.add_argument('--revision',default=SOURCE_REVISION);q.add_argument('--research');q.add_argument('--lexicon')
    q=sub.add_parser('pack-book');q.add_argument('database');q.add_argument('--out',required=True)
    for cmd in ['verify-pack','unpack-book']:
        q=sub.add_parser(cmd);q.add_argument('pack');q.add_argument('--manifest',required=True)
        if cmd=='unpack-book':q.add_argument('--out',required=True)
    q=sub.add_parser('audit-corpus');q.add_argument('directory')
    a=p.parse_args()
    if a.command in ('import-wlc','build-book'):
        books=[x[0] for x in BOOKS] if a.book=='all' else a.book.split(',')
        result=[]
        for book in books:
            report=build_book(a.source,book,a.out,a.revision,a.research,a.lexicon);result.append(report);print(json.dumps(report),flush=True)
        atomic(Path(a.out)/'coverage.json',canonical({'books':result,'research_complete':False})+b'\n')
    elif a.command=='pack-book': print(json.dumps(pack_book(a.database,a.out)))
    elif a.command in ('verify-pack','unpack-book'):
        data=verify_pack(a.pack,json.loads(Path(a.manifest).read_text()))
        if a.command=='unpack-book':atomic(a.out,data)
        print(json.dumps({'verified':True,'sqlite_sha256':digest(data)}))
    else:
        reports={str(f.name):audit_book(f) for f in sorted(Path(a.directory).glob('*.sqlite'))}
        if not reports:raise ValueError('No book databases found')
        print(json.dumps(reports))

if __name__=='__main__':main()
