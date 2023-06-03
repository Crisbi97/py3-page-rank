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

# insert into root db a new url
def root_puturl(conn, cur, url):
    cur.execute('INSERT OR IGNORE INTO ROOT (url, explored) VALUES (?, 0)', (url,))
    conn.commit()

def get_root_explored(cur, url):
    cur.execute('SELECT explored FROM Root WHERE url = ?', (url,))
    return cur.fetchone()

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
    http_error INTEGER,
    old_rank REAL,
    new_rank REAL);

    CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER,
    to_id INTEGER,
    UNIQUE(from_id, to_id));
    ''')

    return conn, cur

# select id, url of a not explored page
def select_url_noexp(cur):
    cur.execute('SELECT id, url FROM Pages WHERE html is NULL and http_error is NULL ORDER BY RANDOM() LIMIT 1')
    return cur.fetchone()

# insert a not explored page
def insert_url_noexp (conn, cur, url):
    print(url)
    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', (url,))
    conn.commit()

def insert_url_exp (conn, cur, url, html, http_code):

    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', (url,))
    cur.execute('UPDATE Pages SET (html, http_error) VALUES (?, ?) WHERE url=?', (memoryview(html), http_code, url))
    conn.commit()


def insert_url_err (conn, cur, url):
    cur.execute('UPDATE Pages SET http_error=-1 WHERE url=?', (url,))
    conn.commit()

#def update_links(cur, from_id, to_id):
   # cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES ( ?, ? )', (fromid, toid))

def db_close(conn, cur):
    cur.close()

    # commit before closing
    conn.commit()
    conn.close()







