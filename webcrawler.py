'''
The program get a starting url (root url) and crawl the pages reachable from the root url.
It can rank the pages based of the number of link that have and show the graph on an html page

1. check if there are root url in db root
    1.1 if not ask for a new root url to start crawling
    1.2 if yes ask if continue to continue the crawl from an existing root or get a new

2. if new root url: insert into db Pages as not explored

3. check if there are some pages not explore
    3.1 if true: continue
    3.2 if false: ask for a new root url or stop

4. pick a random page not explored and explore the html, flag as explored, add all the link as not_explored and count the occurrences from > to

5. iterate untill user stop or no more to crawl
'''

import dbmanager as db
import webparser as web

# db root connect
db_root = db.root_connect()
root_conn = db_root[0]
root_cur = db_root[1]

# check existing roots
roots = db.root_geturl(root_cur)
check_new_root = False
if roots is None:
    check_new_root = True

# there is at least one root in db
if not check_new_root:
    while True:
        print("There are", len(roots), "URL roots:")
        for r in roots: print(r[0], "-", r[1])

        control = input("\nSelect an URL to continue the web crawling (0 for a fresh start): ")

        try:
            control = int(control)
        except:
            print("Input not valid, enter a number between 0 and", len(roots))
            continue

        if control < 0 or control > len(roots):
            print("Input not valid, enter a number between 0 and", len(roots))
            continue

        # continue to crawl a root already in db
        if control > 0:
            new_root = None
            old_root = roots[control-1][1]
            print("URL selected:", old_root)

            # check if root is already explored
            if db.get_root_explored(root_cur, old_root)[0]:
                print("There are no URL to explore")
                quit()

            break

        # crawl a new root
        else:
            check_new_root = True
            break

# there are no root in db or crawl from a new root
if check_new_root:
    old_root = None
    while True:
        new_root = input("Enter a URL as a start for web crawling: ")

        # cleaning the url root
        if web.is_url(new_root):
            clean_root = web.get_cleanurl(new_root)
            if new_root != clean_root:
                new_root = clean_root
                print("Cleaning the URL:", new_root)

            # insert the new root in db
            db.root_puturl(root_conn, root_cur, new_root)
            break
        else:
            print(new_root, "is not a valid URL")
            continue

if new_root is None:
    root_url = old_root
elif old_root is None:
    root_url = new_root

# db url connect
domain_root = web.get_urldomain(root_url)
db_url = db.url_connect(domain_root)
url_conn = db_url[0]
url_cur = db_url[1]

# insert in db root_url (new_root) as not explored url
if new_root is not None:
    db.insert_url_noexp(url_cur, root_url)
    url_conn.commit()

# web crawling loop
#while True:
# check for a not explored url
new_url = db.select_url_noexp(url_cur)

# no url to explore
if new_url is None:
    print("There are no URL to explore")
    db.set_root_explored(root_conn, root_cur, root_url)
    quit()
else:
    print('parse the new url')