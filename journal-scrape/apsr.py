import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError

def apsr(url):
     html = requests.get(url).text
     bsObj = BeautifulSoup(html, "html.parser")
     nameList = bsObj.findAll("li", {"class":"author"})
     for name in nameList:
     	print(name.get_text())

apsr = apsr("https://www.cambridge.org/core/journals/american-political-science-review")