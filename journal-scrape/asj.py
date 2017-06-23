import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError

def asj(url):
     html = requests.get(url).text
     bsObj = BeautifulSoup(html, "html.parser")
     nameList = bsObj.findAll("span", {"class":"hlFld-ContribAuthor"})
     for name in nameList:
     	print(name.get_text())

asj = asj("http://www.journals.uchicago.edu/toc/ajs/current")