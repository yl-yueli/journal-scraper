from urllib.request import urlopen
from bs4 import BeautifulSoup

def rssfeed(url):
	html = urlopen(url)
	bsObj = BeautifulSoup(html, "html.parser")
	nameList = bsObj.findAll("author")
	allNames = list()
	for name in nameList:
	    allNames = allNames + (name.getText().split(","))
	print(allNames)

sp = rssfeed("https://academic.oup.com/rss/site_5418/3279.xml")
qje = rssfeed("https://academic.oup.com/rss/site_5504/3365.xml")
sf = rssfeed("https://academic.oup.com/rss/site_5513/3374.xml")