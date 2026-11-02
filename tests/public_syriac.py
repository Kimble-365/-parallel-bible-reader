import os
VERSION=os.environ.get('READER_VERSION','1.25')
"""Verify live promoted Syriac reading and lexical study; never publish data."""
from playwright.sync_api import sync_playwright
BASE='https://kimble-365.github.io/-parallel-bible-reader/'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=b.new_context(viewport={'width':390,'height':844})
 page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(BASE+'?edition=syc-dsc-nt&compare1=&compare2=&compare3=&text=original#JHN.1.1')
 page.wait_for_selector('[data-edition="syc-dsc-nt"] .original',timeout=60000)
 assert ('/releases/v'+VERSION+'/') in page.url
 assert page.evaluate('BibleCatalog.editions.length')>=84
 assert page.locator('[data-edition="syc-dsc-nt"] .original').first.get_attribute('dir')=='rtl'
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.goto(BASE+'releases/v'+VERSION+'/syriac-study.html?edition=syc-etcbc-biblical&book=GEN&chapter=1&verse=1')
 page.wait_for_selector('.token',timeout=60000);page.locator('.token').first.click()
 page.wait_for_function('document.querySelector("#lexical-result").textContent.includes("etcbc:")',timeout=60000)
 assert 'CC BY-NC 4.0' in page.locator('#lexical-result').inner_text()
 assert not errors,errors
 b.close()
 print('PASS live main redirect to '+VERSION+', Syriac NT RTL, mobile width, shared lexical lookup and attribution; no page errors')
