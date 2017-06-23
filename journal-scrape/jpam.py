import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import re

def wiley(url):
     html = requests.get(url).text
     soup = BeautifulSoup(html, "html.parser")
     allP = soup.findAll("p")
     nameListNew = set()
     nameList = list()
     for name in allP:
     	name = name.get_text()
     	if not re.search(r"\d|(Public)|(National)|^$", name):
     		nameListNew.add(name)
     for name in nameListNew:
          pattern = re.compile("\s*,\s*|\s+$|\sand")
          names = [x for x in pattern.split(name) if x]
          nameList.append(names)
     for name in nameList:
          print(name)

jpam = wiley("http://onlinelibrary.wiley.com/doi/10.1002/pam.2017.36.issue-3/issuetoc")
jomf = wiley("http://onlinelibrary.wiley.com/doi/10.1111/jomf.2017.79.issue-3/issuetoc")