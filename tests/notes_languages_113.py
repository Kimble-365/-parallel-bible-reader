"""Real Chromium, source text, notebook persistence/exports and offline reopening."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(ROOT), **k)
    def log_message(self, *a): pass

server = ThreadingHTTPServer(('127.0.0.1', 0), H)
Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/releases/v1.13/'
ids = ['por-onbv', 'ces-bkr1613', 'kor-krv', 'tgl-angbiblia1905', 'npi-oncv2024']
def open_reader(page, edition):
    page.goto(url + f'?edition={edition}&compare1=&compare2=&compare3=#JHN.3.16')
    page.wait_for_selector('#s1-v16 .main-text')
    page.wait_for_function("typeof document.querySelector('#notes-open').onclick === 'function'")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        ctx = browser.new_context(accept_downloads=True)
        page = ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        for edition in ids:
            open_reader(page, edition)
            source = page.evaluate("async id=>(await ReaderOffline.loadBook('JHN',[id])).editions[id].find(r=>r[0]===3&&r[1]===16)[2]", edition)
            assert source and source in page.locator('#s1-v16').inner_text(), edition
            if edition in ['kor-krv', 'npi-oncv2024']:
                assert page.locator('#s1-v16 .roman').inner_text() != source
            page.locator('#search-panel').evaluate('(e)=>e.open=true')
            page.select_option('#scope', 'chapter')
            page.select_option('#search-match', 'contains')
            page.fill('#search', source[:8])
            page.click('#search-button')
            page.wait_for_function("document.querySelector('#results > p')?.textContent.startsWith('Complete')")
            assert page.locator('#results .result[data-verse="16"]').count() == 1, edition
        open_reader(page, 'por-onbv')
        page.click('#notes-open')
        page.wait_for_selector('#notes-quotes .notes-quote')
        assert 'Portuguese' in page.locator('#notes-quotes').inner_text()
        assert 'Deus' in page.locator('#notes-quotes').inner_text()
        page.fill('#notes-title', 'My study')
        page.fill('#notes-body', 'My own writing <script>literal</script>')
        page.fill('#notes-reference', 'JHN 3:17-18')
        page.click('#notes-insert')
        page.wait_for_function("document.querySelectorAll('.notes-quote').length===2")
        assert '17–18' in page.locator('.notes-quote').nth(1).inner_text()
        page.reload()
        page.wait_for_selector('#s1-v16')
        page.click('#notes-open')
        assert page.locator('#notes-body').input_value() == 'My own writing <script>literal</script>'
        assert page.locator('.notes-quote').count() == 2
        page.fill('#notes-reference', 'JHN 999:1')
        page.click('#notes-insert')
        page.wait_for_function("document.querySelector('#notes-status').textContent.includes('not included')")
        assert page.locator('.notes-quote').count() == 2
        with page.expect_download() as dl:
            page.click('#notes-export')
        raw = Path(dl.value.path()).read_bytes()
        assert json.loads(raw)['notes'][0]['title'] == 'My study'
        page.set_input_files('#notes-file', {'name':'backup.json', 'mimeType':'application/json', 'buffer':raw})
        page.get_by_text('Restore a notes backup', exact=True).click()
        page.click('#notes-import')
        page.wait_for_function("document.querySelector('#notes-list').options.length===2")
        assert len({n['id'] for n in page.evaluate("JSON.parse(localStorage.getItem('parallel-reader-notes-v1'))")}) == 2
        open_reader(page, 'kor-krv')
        page.click('#notes-open')
        page.click('#notes-current')
        page.wait_for_function("document.querySelectorAll('.notes-quote').length===3")
        assert 'Korean' in page.locator('.notes-quote').nth(2).inner_text()
        assert '하나님' in page.locator('.notes-quote').nth(2).inner_text()
        assert 'Portuguese' in page.locator('.notes-quote').first.inner_text()
        assert page.locator('#notes-body').input_value() == 'My own writing <script>literal</script>'
        page.evaluate("async ids=>{await ReaderOffline.download(ids)}", ids)
        assert len([r for r in page.evaluate("ReaderOffline.list()") if r['id'] in ids]) == 330
        page.evaluate('navigator.serviceWorker.ready')
        page.wait_for_function('!!navigator.serviceWorker.controller')
        ctx.set_offline(True)
        page.reload()
        page.wait_for_selector('#s1-v16')
        page.click('#notes-open')
        assert page.locator('.notes-quote').count() == 3
        assert '하나님' in page.locator('.notes-quote').nth(2).inner_text()
        page.fill('#notes-body', 'Written while offline')
        page.reload()
        page.wait_for_selector('#s1-v16')
        page.click('#notes-open')
        assert page.locator('#notes-body').input_value() == 'Written while offline'
        ctx.set_offline(False)
        page.goto(url + '?edition=&compare1=engwebp&compare2=&compare3=#JHN.3.16')
        page.wait_for_selector('#v16')
        page.click('#notes-open')
        page.click('#notes-new')
        page.wait_for_function("document.querySelector('#notes-title').value==='Untitled note'")
        assert page.locator('.notes-quote').count() == 0
        assert 'Choose a translation in Text 1' in page.locator('#notes-source').inner_text()
        assert not errors, errors
        browser.close()
        print('PASS: all five real 66-book editions load/search; Korean/Nepali Latin; Text 1 original quotes/range; notes edits/reload/JSON export/additive restore; source changes preserve attribution; all five complete editions saved (330 books); offline notes/reload; absent Text 1 never uses Text 2; no page errors')
finally:
    server.shutdown()
