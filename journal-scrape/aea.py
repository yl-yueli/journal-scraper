import requests
from bs4 import BeautifulSoup
import re
import ssl
from functools import wraps
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar

ssl.wrap_socket = sslwrap(ssl.wrap_socket)

page = requests.get('https://www.aeaweb.org/issues/466').text
print(page)
soup = BeautifulSoup(page, "html.parser")
soup.prettify()
nameList = soup.findAll("li", {"class":"author"})
print(nameList)
for name in nameList:
	print(name.get_text())
