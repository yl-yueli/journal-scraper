import requests
from bs4 import BeautifulSoup
import re

page = requests.get('http://journals.sagepub.com/toc/ASR/current').text
print(page)
soup = BeautifulSoup(page, "html.parser")
soup.prettify()
soupList = soup.findAll("a", class_="entryAuthor", href=re.compile("^(/author/).*(\%2C\+).*$"))
nameList = set()
for name in soupList:
	nameList.add(name.getText())
for name in nameList:
	print(name)