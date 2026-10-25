"""Point the main URL at a verified numbered reader, retaining the original reader."""
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
def promote(version):
 if not re.fullmatch(r'\d+\.\d+',version):raise ValueError('Use a numbered release such as 1.11')
 release=ROOT/'releases'/('v'+version)
 if not (release/'index.html').is_file():raise ValueError('Reader release is missing')
 legacy=ROOT/'legacy';legacy.mkdir(exist_ok=True)
 if not (legacy/'index.html').exists():
  old=(ROOT/'index.html').read_text()
  if '<script src="reader.js' not in old:raise ValueError('Original reader not found; do not archive a redirect')
  old=old.replace('<head>','<head><base href="../">',1).replace('<body>','<body><p class="notice">Archived original reader · <a href="./">Open latest reader</a></p>',1)
  (legacy/'index.html').write_text(old)
 target='releases/v'+version+'/'
 (ROOT/'index.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Parallel Bible Reader — latest version</title><link rel="canonical" href="https://kimble-365.github.io/-parallel-bible-reader/'''+target+'''">\n<script>const target=new URL('''+repr(target)+''',location.href);target.search=location.search;target.hash=location.hash;window.location.replace(target.href);</script>\n</head><body style="font:1.1rem/1.7 system-ui;max-width:50rem;margin:3rem auto;padding:1rem"><h1>Parallel Bible Reader</h1><p>Opening the current reader, version '''+version+'''…</p><p><a id="latest-reader" href="'''+target+'''">Open reader '''+version+'''</a> · <a href="legacy/">Archived original reader</a> · <a href="releases/">Version history</a></p><noscript><p>Enable JavaScript to use the reader. The links above remain available.</p></noscript></body></html>\n''')
 print('Main URL → '+target+'; original reader retained under legacy/')
if __name__=='__main__':promote(sys.argv[1])
