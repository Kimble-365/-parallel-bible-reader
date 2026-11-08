"""Exercise standard SQLite/Unicode tools without rewriting source or user databases."""
import sqlite3,unicodedata,json
texts=['שְׁמַ֖ע יִשְׂרָאֵ֑ל','λόγος ἀγάπη','प्रेम','اردو','𝄞']
with sqlite3.connect(':memory:') as db:
 db.execute('create table verses(id integer primary key, text text not null)')
 db.executemany('insert into verses(text) values (?)',[(t,) for t in texts]);assert [r[0] for r in db.execute('select text from verses order by id')]==texts
 db.execute('create virtual table search using fts5(text)');db.execute('insert into search(text) values (?)',(texts[1],));assert db.execute('select count(*) from search where search match ?',('λόγος',)).fetchone()[0]==1
 for text in texts:assert unicodedata.normalize('NFC',unicodedata.normalize('NFD',text))==unicodedata.normalize('NFC',text)
 print(json.dumps({'sqlite':sqlite3.sqlite_version,'unicode':unicodedata.unidata_version,'fts5':True,'exact_unicode_roundtrip':len(texts),'persistent_databases_modified':False}))
print('PASS SQLite FTS5 and Unicode tools: mixed Hebrew/Greek/Indic/RTL/astral text, memory-only verification')
