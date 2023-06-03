import sqlite3

# create root db, return connection, cursor
def root_connect():

    conn = sqlite3.connect('_root.sqlite')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS Root
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    url TEXT UNIQUE,
    explored INTEGER NOT NULL)
    ''')

    return conn, cur

# return all (id, url) from root db or none if empty
def root_geturl(cur):

    cur.execute('SELECT id, url FROM Root ORDER BY id')
    result = cur.fetchall()

    if len(result) == 0:
        return None
    else:
        return result

# insert into root db a new root url
def root_puturl(conn, cur, url):
    cur.execute('INSERT OR IGNORE INTO ROOT (url, explored) VALUES (?, 0)', (url,))
    conn.commit()

# return 0 if root url not explored, 1 else
def get_root_explored(cur, url):
    cur.execute('SELECT explored FROM Root WHERE url = ?', (url,))
    return cur.fetchone()

# update into root db a root url as explored
def set_root_explored(conn, cur, url):
    cur.execute('UPDATE Root SET explored = 1 WHERE url = ?', (url,))
    conn.commit()


# create url db, return connection, cursor
def url_connect(url):

    if len(url) <= 0 or url == '_root':
        url = 'default'

    dbname = url + '.sqlite'

    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS Pages
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    url TEXT UNIQUE,
    html TEXT,
    http_code INTEGER,
    old_rank REAL,
    new_rank REAL);

    CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER,
    to_id INTEGER,
    UNIQUE(from_id, to_id));
    ''')

    return conn, cur

# return id from url
def select_id(cur, url):
    cur.execute('SELECT id FROM Pages WHERE url = ?', (url,))
    return cur.fetchone()[0]

# return id, url from not explored url
def select_url_noexp(cur):
    cur.execute('SELECT id, url FROM Pages WHERE html is NULL and http_code is NULL ORDER BY RANDOM() LIMIT 1')
    return cur.fetchone()

# insert url as not explored
def insert_url_noexp (conn, cur, url):

    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', (url,))
    conn.commit()

# insert url as explored
def insert_url_exp (conn, cur, url, html, http_code):

    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', (url,))
    cur.execute('UPDATE Pages SET html=?, http_code=? WHERE url=?', (memoryview(html), http_code, url))
    conn.commit()

# insert url as error url
def insert_url_err (conn, cur, http_code, url):
    cur.execute('UPDATE Pages SET http_code=? WHERE url=?', (http_code, url))
    conn.commit()

# insert into link table a row from_id, to_id
def update_links(cur, from_id, to_id):
    cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES (?, ?)', (from_id, to_id))
    #commit at the closing of db (end of webcrawler.py)

# commit and close db conn, cur
def db_close(conn, cur):
    cur.close()

    # commit before closing
    conn.commit()
    conn.close()







