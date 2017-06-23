import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import re

def apsr(url):
     html = requests.get(url).text
     soup = BeautifulSoup(html, "html.parser")
     allTitles = soup.find("ul").findAll("li")
     nameListAppend = set()
     for title in allTitles:
          title = title.get_text()
          nameTitle = re.split("\n", title)
          for name in nameTitle:
               if "#" in name:
                    name = re.sub("#.*$","", name)
                    nameListAppend.add(name)
     nameList = list()
     for name in nameListAppend:
          pattern = re.compile("\s*,\s*|\s+$|\sand")
          names = [x for x in pattern.split(name) if x]
          nameList.append(names)
     for name in nameList:
          print(name)

apsr = apsr("http://www.nber.org/new.html")