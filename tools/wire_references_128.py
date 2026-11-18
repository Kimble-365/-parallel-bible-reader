from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'releases/v1.28'
for name in ['offline-library.js','reader.js','index.html','sw.js','translations/metadata.js','simple-ui.js','study-menu.js']:
 p=R/name;p.write_text((ROOT/'releases/v1.27'/name).read_text(encoding='utf-8').replace('1.27','1.28'),encoding='utf-8',newline='\n')
p=R/'catalog.js';catalog=json.loads(p.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'));old=json.loads((ROOT/'releases/v1.27/catalog.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'));catalog['version']=old['version'];catalog['release_version']='1.28';p.write_text('window.BibleCatalog='+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
p=R/'offline-library.js';s=p.read_text(encoding='utf-8')
s=s.replace("kind==='bhh'?'../v1.23/bhh-data/':", "kind==='references'?'study-data/':kind==='bhh'?'../v1.23/bhh-data/':")
s=s.replace("book+(['bhh'", "book+(kind==='references'?'.json':['bhh'")
s=s.replace(".includes(kind)?'.json.gz':'.js')", ".includes(kind)?'.json.gz':'.js')")
# The inserted ternary is right associative: references JSON precedes inherited formats.
s=s.replace("if(['bhh','lxxl','ntgl','related','nordic'].includes(kind)){", "if(kind==='references'){const bytes=new Uint8Array(await response.arrayBuffer()),expected=ReaderReferencePacks[book];if(!expected||bytes.length!==expected.bytes)throw Error('Incomplete reference pack.');const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==expected.sha256)throw Error('Reference pack checksum mismatch.');return validate(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes)),book)}if(['bhh','lxxl','ntgl','related','nordic'].includes(kind)){")
s=s.replace("const kindOf=id=>", "const kindOf=id=>editions.get(id)?.data_group==='references-1.28'?'references':")
p.write_text(s,encoding='utf-8',newline='\n')
p=R/'reader.js';s=p.read_text(encoding='utf-8')
s=s.replace("const query=new URLSearchParams(location.search);", "const query=new URLSearchParams(location.search);")
needle=" const view=$('text-display').value;\n function add"
replace=""" if(e.resource_kind==='commentary'&&row[7]?.blocks){
  col.append(element('p',e.id==='tsk-crosswire'?'TSK · KJV source numbering':'Alaviitteet · suomenkielisen laitoksen numerointi','reference-source-label'));
  col.append(element('p',String(row[0])+':'+String(row[1]),'verse-reference'));
  for(const block of row[7].blocks){
   if(!block.targets?.length){col.append(element('p',block.source_reference||block.text,'reference-note'));continue}
   const list=element('p',undefined,'reference-links');
   for(const target of block.targets){const link=element('a',target.book+' '+target.chapter+':'+target.verse+(target.end_verse&&(target.end_book||target.end_chapter!==target.chapter||target.end_verse!==target.verse)?'–'+(target.end_book?target.end_book+' ':'')+(target.end_chapter!==target.chapter||target.end_book?target.end_chapter+':':'')+target.end_verse:''));link.href=shareUrl(id,target.book,target.chapter,target.verse);link.dataset.referenceTarget=[target.book,target.chapter,target.verse].join('.');link.setAttribute('aria-label','Open '+link.textContent+' in '+e.label);link.onclick=event=>{event.preventDefault();sourceOverrides[slot-1]={edition:id,book:target.book,chapter:target.chapter};openChapter(target.book,target.chapter,target.verse,{scroll:true,focusSlot:slot,sourceEdition:id})};list.append(link,document.createTextNode(' · '))}col.append(list);
   if(id==='tsk-crosswire'){const detail=element('details',undefined,'reference-original');detail.append(element('summary',block.unlinked_notation?'Source notation — includes an unlinked reference':'Source notation'),element('p',block.source_reference));col.append(detail)}
  }return col;
 }
 const view=$('text-display').value;
 function add"""
assert needle in s;s=s.replace(needle,replace)
p.write_text(s,encoding='utf-8',newline='\n')
p=R/'index.html';s=p.read_text(encoding='utf-8')
s=s.replace('<script src="offline-library.js', '<script src="reference-manifest.js"></script><script src="offline-library.js')
intro='''<details id="reference-library" class="reader-extras"><summary>TSK and Finnish study references</summary><p>Choose the TSK or Finnish notes companion in any Text slot, just like a Bible. References are clickable; notes remain separate from scripture. TSK retains KJV numbering. Use independent source chapters when comparing different verse systems.</p><p><a id="open-finnish-study" href="?edition=fin-study-v005&amp;compare1=fin-study-notes-v005&amp;compare2=tsk-crosswire&amp;compare3=&amp;layout=source#GEN.1.1">Open Finnish Bible, notes and TSK</a> · <a id="open-tsk" href="?edition=tsk-crosswire&amp;compare1=&amp;compare2=&amp;compare3=&amp;layout=source#GEN.1.1">Read TSK</a> · <a href="reference-guide.html">Sources and reference checks</a></p></details>'''
s=s.replace('<main id="reading"',intro+'<main id="reading"')
s=s.replace('</head>', '<style>.reference-links a{display:inline-block;margin:.1em .15em;overflow-wrap:anywhere}.reference-note{white-space:pre-line;font-size:.85em}.reference-original{font-size:.7em}.reference-source-label{font-size:.65em;color:var(--muted,#59686b)}.translation{min-width:0}.reference-links{font-size:.85em;line-height:1.6}</style></head>')
p.write_text(s,encoding='utf-8',newline='\n')
p=R/'sw.js';s=p.read_text(encoding='utf-8').replace("const ASSETS=[","const ASSETS=['reference-manifest.js','reference-guide.html',");p.write_text(s,encoding='utf-8',newline='\n')
p=R/'translations/metadata.js';s=p.read_text(encoding='utf-8');directory=json.loads(s.split('=',1)[1].strip().rstrip(';'))
for id,label,lang,iso in [('fin-study-v005','Suomenkielinen tutkimusraamattu','Finnish','fin'),('fin-study-notes-v005','Suomenkieliset alaviitteet ja ristiviitteet','Finnish','fin'),('tsk-crosswire','TSK reference companion','English','eng')]:
 directory.append(dict(id=id,language=lang,iso6393=iso,aliases=[label],family='Uralic' if lang=='Finnish' else 'Indo-European',branch='Finnic' if lang=='Finnish' else 'Germanic',subfamily='Finnic' if lang=='Finnish' else 'West Germanic',countries=['Finland'] if lang=='Finnish' else [],continents=['Europe'],states=[],script='Latin',variety=label,classification_source='Project edition metadata',ubs_id=None))
p.write_text('window.TranslationDirectory='+json.dumps(directory,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
print('Reference editions wired into 1.28')
for name in ['study-menu.js','simple-ui.js']:
 p=R/name;s=p.read_text(encoding='utf-8').replace('Reader 1.27','Reader 1.28')
 if name=='simple-ui.js':s=s.replace("['Settings',null],", "['Settings',null],['References','reference-library'],")
 p.write_text(s,encoding='utf-8',newline='\n')
