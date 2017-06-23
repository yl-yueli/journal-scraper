import requests
from bs4 import BeautifulSoup
import re

def springer(url):
	html = requests.get(url).text
	bsObj = BeautifulSoup(html, "html.parser")
	nameList = bsObj.findAll("a", href=re.compile("^(\/search\?facet-creator=\%22).*$"))
	for name in nameList:
		print(name.get_text())

springer("https://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=13524")
