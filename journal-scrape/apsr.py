import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import re

def findApsrAuthors(url):
	try:
		html = requests.get(url).text 
	except HTTPError as e:
		print(e)
	try:
		soup = BeautifulSoup(html, "html.parser")
		nameList = soup.findAll("li", {"class":"author"})
		allNames = list()
		pattern = re.compile("\s*,\s*|\s+$")
		for name in nameList:
			name = name.get_text().lstrip("\n")
			allNames = allNames + pattern.split(name)
		for name in allNames:
			print(name)
		#print(allNames)
		return allNames
	except AttributeError as e: # return if there is an attribute error
         return None

# automatic link to current issue
apsr = findApsrAuthors("https://www.cambridge.org/core/journals/american-political-science-review")