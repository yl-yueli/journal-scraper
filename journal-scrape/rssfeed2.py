from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError

def rssfeed(url):
	try:
 	    html = urlopen(url)
	except HTTPError as e:
   	    print(e)
	try:
	    bsObj = BeautifulSoup(html, "html.parser")
	    nameList = bsObj.findAll("author")
	except AttributeError as e:
         return None
	allNames = list()
	for name in nameList:
	    allNames = allNames + (name.getText().split(","))
	return allNames
	

sp = rssfeed("https://academic.oup.com/rss/site_5418/3279.xml")
qje = rssfeed("https://academic.oup.com/rss/site_5504/3365.xml")
sf = rssfeed("https://academic.oup.com/rss/site_5513/3374.xml")

def printNames(names):
	if names == None:
         print("Names could not be found")
	else:
   	     print(names)

printNames(sp)
printNames(qje)
printNames(sf)
