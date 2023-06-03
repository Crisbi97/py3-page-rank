import ssl
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup


# return context that ignore SSL certificate error
def getcontext():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

# return True if url is valid False else
def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# return domain from url or none (ex: https://www.wikipedia.org/ > wikipedia)
def get_urldomain(url):

    try:
        domain = urlparse(url).netloc
    except:
        return None

    lpos = domain.find('.')
    rpos = domain.rfind('.')
    if lpos == rpos: lpos = -1

    return domain[lpos + 1:rpos]

# return clean url or none (ex: https://www.wikipedia.org/loreipsum > https://www.wikipedia.org)
def get_cleanurl(url):
    result = urlparse(url)
    return result.scheme + "://" + result.netloc


# return document, list of href link from url
def get_url_detail(url, ctx):

    try:
        document = urlopen(url, context=ctx).read()
    except:
        return None

    linklist = list()

     # parsing html w bs4
    soup = BeautifulSoup(document, "html.parser")

    # retrieve all the anchor tags
    tags = soup('a')

    # for every tag
    for tag in tags:
        link = str(tag.get('href', None))
        if is_url(link): linklist.append(link)

    return document, linklist













