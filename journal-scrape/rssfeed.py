from urllib.request import urlopen 
import requests
from bs4 import BeautifulSoup 
from urllib.error import HTTPError 
from urllib.error import URLError
import re

def rssFeed(url):
	try:
 	    html = urlopen(url) # open journal home page
	except HTTPError as e: # print error if it encounters any
   	    print(e)
	try:
	    soup = BeautifulSoup(html, "html.parser") # create beautiful soup object
	    nameList = soup.findAll("author") # find all author names
	except AttributeError as e: # return if there is an attribute error
         return None
	allNames = list() # create empty list
	pattern = re.compile("\s*,\s*|\s+$") # pattern to get rid of commas and white spaces
	for name in nameList: # loop through all the names
		name = name.get_text().rstrip() # get text and the white space at the end
		allNames = allNames + pattern.split(name) # split at the given patterns
	return allNames # return all names

def openRss(journal): # open into the rss feed
	try:
		html = urlopen("https://academic.oup.com/" + journal) # open webpage and read
	except HTTPError as e: # print error if it encounters any
   	    print(e)
	try:
   		soup = BeautifulSoup(html, "html.parser")
   		current = soup.find("div", {"class":"current-issue-title widget-IssueInfo__title"}).find("a", {"class":"widget-IssueInfo__link"}) # find the latest issue
   		currentUrl = "https://academic.oup.com" + current.attrs['href']
	except AttributeError as e: # return if there is an attribute error
   		return None
	try:
		currentIssue = urlopen(currentUrl) # open current url
	except HTTPError as e: # return if there is an error opening the page
		print(e)
	try:
		currentSoup = BeautifulSoup(currentIssue, "html.parser")
		rssFeedTag = currentSoup.find("div", {"class":"widget widget-feeds"}).find("a")
	except AttributeError as e: # return if there is an attribute error
		return None
	return rssFeed(rssFeedTag.attrs['href']) # using the rss url, return all the authors found in the rss feed

def printNames(names): # simple printing command for testing
	if names == None:
         print("Names could not be found")
	else:
		for name in names:
			print(name)

sp = openRss("sp") # social politics 
printNames(sp)

sf = openRss("sf") # social force
printNames(sf)

qje = openRss("qje") # quarterly journal of economics
printNames(qje)