import requests
from bs4 import BeautifulSoup
import re
from urllib.error import HTTPError 
from urllib.error import URLError

def findAsrAuthors(url):
	try:
		page = requests.get(url).text # open the page
	except HTTPError as e: # print if there's an error opening the page
		print(e)
	try:
		soup = BeautifulSoup(page, "html.parser")
		# this soupList contains "See all articles..." which has the same tag, so remove it later
		allInfo = soup.findAll("table", {"class":"articleEntry"})
		allAuthorInfo = {}
		for info in allInfo:
			authorsTagged = info.findAll("a", class_="entryAuthor", href=re.compile("^(/author/).*(\%2C\+).*$"))
			title = info.find("span", {"class":"hlFld-Title"}).get_text()
			link = "http://journals.sagepub.com/" + info.find("a", {"class":"ref nowrap"})["href"]
			date = info.find("span", {"class":"maintextleft"}).get_text()
			authors = set()
			for author in authorsTagged:
				if not "articles" in author.get_text(): # remove the "See all articles..."
					authors.add(author.get_text())
			authorInfo = "Title: " + title + "\n\tLink: " + link + "\n\tAuthor(s): " + ", ".join(authors) + "\n" + "\n\tDate: " + date
			for author in authors:
				allAuthorInfo[author] = authorInfo
		return allAuthorInfo
		#soupList = soup.findAll("a", class_="entryAuthor", href=re.compile("^(/author/).*(\%2C\+).*$")) 
	except AttributeError as e:
		return None
	#nameList = set() # create an empty set of the actual names
	#for name in soupList: # find all the names in the soupList, excluding "See all entries..."
	#	if not "articles" in name.get_text(): # remove the "See all articles..."
	#		nameList.add(name.getText().lstrip()) # remove the white space in the front
	#for name in nameList: # print the names
	#	print(name)
	#return nameList # return the names

def printNames(names): # simple printing command for testing
	if names == None:
         print("Names could not be found")
	else:
		for name in names:
			print(name + "\n" + names[name])	

asr = findAsrAuthors("http://journals.sagepub.com/toc/ASR/current")
printNames(asr)