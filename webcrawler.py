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
        print("There are", len(roots), "ROOT URL:")
        for r in roots: print(r[0], "-", r[1])

        control = input("\nSelect a ROOT URL to continue the web crawling (0 for a fresh start): ")

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
            print("ROOT URL selected:", old_root)

            # check if root is already explored
            if db.get_root_explored(root_cur, old_root)[0]: # ! Change function name as "is_root_explored" and return cur.fetchone[0] > (1 || 0)
                print("ROOT URL", old_root, "already explored\n")
                continue

            break

        # crawl a new root
        else:
            check_new_root = True
            break

# there are no root in db or crawl from a new root
if check_new_root:
    old_root = None
    while True:
        new_root = input("Enter a ROOT URL as a start for web crawling: ")

        # cleaning the url root
        if web.is_url(new_root):
            clean_root = web.get_cleanurl(new_root)
            if new_root != clean_root:
                new_root = clean_root
                print("Cleaning the ROOT URL:", new_root)

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
    db.insert_url_noexp(url_conn, url_cur, root_url)
    #url_conn.commit() > commit already in func insert_url_noexp

# get contex that ignore SSL certificate error
ctx = web.getcontext()

exp_count = 0
exp_max = 0
# web crawling loop
while True:

    # how many url to explore?
    if exp_max == 0:
        while True:
            iteration = input("How many URL to explore? ")

            try:
                exp_max = int(iteration)
            except:
                print("Input not valid")
                continue

            if exp_max <= 0:
                print("Select a number > 0")
                continue
            else: break

    # commit db ops every 10 iterations
    #elif exp_count > 0 and exp_count%10 == 0:
        #url_conn.commit()

    # number of iteration done
    elif exp_count == exp_max:
        print("Explored", exp_count, "URL")

        while True:
            iteration = input("Type -1 to exit or a number to explore more URL:")

            try:
                iteration = int(iteration)
            except:
                print("Input not valid")
                continue

            if iteration == -1:
                quit()
            elif iteration <= 0:
                print("Select a number greater than 0")
                continue
            else:
                exp_max = exp_max + iteration
                break

    # continue to explore
    else:
        # check for a not explored url
        new_url = db.select_url_noexp(url_cur)

        # if no url to explore > root already explored
        if new_url is None:
            print("There are no more URL to explore")
            db.set_root_explored(root_conn, root_cur, root_url)
            quit()
        # at least one url to explore > new_url
        else:
            print('> Exploring URL:', new_url[0], "-", new_url[1])
            resp = web.get_url_detail(new_url[1], ctx)

            # can't open new_url
            if resp is None:
                print("<!> Can't open URL:", new_url[0], "-", new_url[1])
                db.insert_url_err(url_conn, url_cur, -1, new_url[1])
                continue
            else:
                html = resp[0]
                http_code = resp[1]
                http_content_type = resp[2]
                link_lst = resp[3]

                # check url http error
                if http_code != 200:
                    print("<!> Error", http_code, "on URL:", new_url[0], "-", new_url[1])
                    db.insert_url_err(url_conn, url_cur, http_code, new_url[1])
                    continue

                # check content type url (text/html)
                if 'text/html' != http_content_type:
                    print("<!> URL not HTML:", new_url[0], "-", new_url[1])
                    db.insert_url_err(url_conn, url_cur, -1, new_url[1])
                    continue

                # mark as explored new url in db
                db.insert_url_exp(url_conn, url_cur, new_url[1], html, http_code)

                # new_url does not link to other url
                if len(link_lst) < 1:
                    print("<!> No links from URL:", new_url[0], "-", new_url[1])

                # insert all new link as not exp and update links table
                else:
                    for link in link_lst:
                        db.insert_url_noexp(url_conn, url_cur, link)
                        link_id = db.select_id(url_cur, link)
                        db.update_links(url_cur, new_url[0], link_id)

                exp_count += 1

print("Explored:", exp_count, "URL")
db.db_close(root_conn, root_cur)
db.db_close(url_conn, url_cur)
quit()
