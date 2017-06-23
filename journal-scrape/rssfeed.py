from urllib.request import urlopen 
import requests
from bs4 import BeautifulSoup 
from urllib.error import HTTPError 
from urllib.error import URLError

def rssFeed(url):
	try:
 	    html = urlopen(url)
	except HTTPError as e:
   	    print(e)
	try:
	    soup = BeautifulSoup(html, "html.parser")
	    nameList = soup.findAll("author")
	except AttributeError as e:
         return None
	allNames = list()
	for name in nameList:
	    allNames = allNames + (name.getText().split(","))
	return allNames

def openrss(journal): # open into the rss feed
	html = urlopen("https://academic.oup.com/" + journal) # open webpage and read
	soup = BeautifulSoup(html, "html.parser")
	current = soup.find("div", {"class":"current-issue-title widget-IssueInfo__title"}).find("a", {"class":"widget-IssueInfo__link"}) # find the latest issue
	currentUrl = "https://academic.oup.com" + current.attrs['href']
	currentIssue = urlopen(currentUrl)
	currentSoup = BeautifulSoup(currentIssue, "html.parser")
	rssFeedTag = currentSoup.find("div", {"class":"widget widget-feeds"}).find("a")
	return rssFeed(rssFeedTag.attrs['href'])

def printNames(names):
	if names == None:
         print("Names could not be found")
	else:
   	     print(names)

sp = openrss("sp")
printNames(sp)

sf = openrss("sf")
printNames(sf)

qje = openrss("qje")
printNames(qje)