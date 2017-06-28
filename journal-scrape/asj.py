import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError

def openUrlRequests(url): # open url using requests package
	try:
 	    html = requests.get(url).text # open journal home page
 	    return html
	except HTTPError as e: # print error if it encounters any
   	    print(e)
   	    return None

def removeMiddleName(allNames): # remove middle names (takes the first word and the last word)
	nameList = list()
	for name in allNames: 
		fml = name.split(" ") # obtain first middle last name
		fm = [fml[0], fml[-1]] # create a list with the first word and the last word (assume first and last name)
		nameList.append(" ".join(fm)) # join together the first and last name as a string, add to the list of names
	return(nameList)

def asj(url):
     html = openUrlRequests(url)
     soup = BeautifulSoup(html, "html.parser")
     allInfo = soup.findAll("table", {"class":"articleEntry"})
     allAuthorInfo = {}
     for info in allInfo:
     	title = info.find("span", {"class":"hlFld-Title"}).get_text()
     	link = "http://www.journals.uchicago.edu" + info.find("a", {"class":"nowrap"})["href"]
     	authorsTagged = info.findAll("span", {"class":"hlFld-ContribAuthor"})
     	authors = list()
     	for author in authorsTagged:
     		authors.append(author.get_text())
     	authorInfo = "Title: " + title + "\n\tLink: " + link + "\n\tAuthor(s): " + ", ".join(authors) + "\n"
     	for author in authors:
     		allAuthorInfo[author] = authorInfo
     return allAuthorInfo

def printNames(names): # simple printing command for testing
	if names == None:
         print("Names could not be found")
	else:
		for name in names:
			print(name + "\n" + names[name])
 

asj = asj("http://www.journals.uchicago.edu/toc/ajs/current")
printNames(asj)