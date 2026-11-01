"""Real browser: all slots, RTL, shared lexical lookup, integrity and offline text."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import itertools, sys
ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}/releases/v1.25/'
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 1280, 'height': 900})
        context.add_init_script('window.DecompressionStream=undefined')
        page = context.new_page()
        errors, requests = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: requests.append(r.url))
        page.goto(base + '?edition=syc-peshitta-ot&compare1=syc-etcbc-biblical&compare2=&compare3=&text=original#GEN.1.1')
        page.wait_for_selector('[data-edition="syc-peshitta-ot"] .original')
        assert 'ܒܪܫܝܬ' in page.locator('#verses').inner_text()
        assert page.locator('[data-edition="syc-peshitta-ot"] .original').first.get_attribute('dir') == 'rtl'
        assert not any('/syriac-index/' in u or '/syriac-lexicon/' in u for u in requests)
        # Exercise every explicit slot combination; all slots may be empty.
        ids = ['syc-peshitta-ot', 'syc-etcbc-biblical', 'syc-peshitta-ot', 'syc-etcbc-biblical']
        for mask in itertools.product([False, True], repeat=4):
            print('Checking explicit slot mask:', mask, flush=True)
            params = '&'.join(k + '=' + (ids[i] if enabled else '') for i, (k, enabled) in enumerate(zip(['edition', 'compare1', 'compare2', 'compare3'], mask)))
            page.goto(base + '?' + params + '&text=original#GEN.1.1')
            page.wait_for_function('typeof ReaderOffline!=="undefined" && document.querySelector("#primary option")')
            if any(mask):
                page.wait_for_function('(n)=>document.querySelectorAll("#verses [data-edition] .original").length>=n', arg=sum(mask))
                slots = page.locator('#verses [data-slot]').evaluate_all('(es)=>[...new Set(es.map(e=>Number(e.dataset.slot)))]')
                assert sorted(slots) == [i + 1 for i, enabled in enumerate(mask) if enabled], (mask, slots)
            else:
                page.wait_for_function('document.querySelector("#heading").textContent.includes("Choose a translation")')
                assert page.locator('#verses [data-edition]').count() == 0
        page.goto(base + '?edition=syc-dsc-nt&compare1=&compare2=&compare3=&text=original#JHN.1.1')
        page.wait_for_selector('[data-edition="syc-dsc-nt"] .original')
        assert 'ܒ' in page.locator('#verses').inner_text()
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.goto(base + 'syriac-study.html?edition=syc-etcbc-biblical&book=GEN&chapter=1&verse=1')
        page.wait_for_selector('.token')
        page.locator('.token').first.click()
        page.wait_for_function('document.querySelector("#lexical-result").textContent.includes("etcbc:")')
        assert 'CC BY-NC 4.0' in page.locator('#lexical-result').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.goto(base + 'syriac-study.html?edition=syc-dsc-nt&book=LUK&chapter=11&verse=42')
        page.wait_for_function('document.querySelector("#source-note").textContent.includes("Duplicate source label")')
        assert 'No word-level analysis' in page.locator('#lexical-result').inner_text()
        # Save the NT reading, then verify fresh offline page/route and text load.
        page.goto(base + '?edition=syc-dsc-nt&compare1=&compare2=&compare3=&text=original#JHN.1.1')
        page.wait_for_selector('[data-edition="syc-dsc-nt"] .original')
        page.evaluate('async()=>{await navigator.serviceWorker.ready;await ReaderOffline.download(["syc-dsc-nt"])}')
        page.wait_for_function('!!navigator.serviceWorker.controller')
        context.set_offline(True)
        page.goto(base + '?edition=syc-dsc-nt&compare1=&compare2=&compare3=&text=original#REV.22.1')
        page.wait_for_selector('[data-edition="syc-dsc-nt"] .original')
        assert '܀' in page.locator('#verses').inner_text() or 'ܐ' in page.locator('#verses').inner_text()
        assert not errors, errors
        browser.close()
        print('PASS: 16 slot combinations, RTL, mobile, shared lexical lookup, duplicate-label warning, gzip fallback and saved NT offline Revelation; no page errors')
finally:
    if sys.exc_info()[0]:
        print('Captured page errors:', errors, flush=True)
        try:
            print('Current heading/status:', page.locator('#heading').inner_text(), page.locator('#status').inner_text(), flush=True)
        except Exception:
            pass
    server.shutdown()
