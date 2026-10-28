from pathlib import Path
import sqlite3
p=Path('/tmp/reader-sqlite-fixtures');p.mkdir(exist_ok=True)
for label,encoding in [('utf8','UTF-8'),('utf16','UTF-16be')]:
 f=p/(label+'.bblx');f.unlink(missing_ok=True)
 con=sqlite3.connect(f);con.execute('PRAGMA encoding="'+encoding+'"');con.execute('CREATE TABLE Bible (Book INTEGER, Chapter INTEGER, Verse INTEGER, Scripture TEXT)');con.execute('CREATE TABLE Details (Title TEXT)');con.execute('INSERT INTO Details VALUES (?)',('Fixture — not Bible text',));con.executemany('INSERT INTO Bible VALUES(1,1,?,?)',[(i+1,'Unicode: äöå Ελληνικά 日本語 אֱלֹהִים العربية' if i==0 else 'Test verse '+str(i)) for i in range(1000)]);con.execute('INSERT INTO Bible VALUES(1,2,1,?)',('長い本文 '*3000,));con.commit();con.close()
print('Created real UTF-8/UTF-16BE SQLite import fixtures with internal/overflow pages')
