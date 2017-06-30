import requests
from bs4 import BeautifulSoup
import re

def printNames(names): # simple printing command for testing
	if names == None:
         print("Names could not be found")
	else:
		for name in names:
			print("This worked " + name + "\n" + names[name])

def springer(url):
	html = requests.get(url).text
	soup = BeautifulSoup(html, "html.parser")
	allInfo = soup.find("div", {"id":"kb-nav--main"}).findAll("li")
	allAuthorInfo = {}
	for info in allInfo:
		title = info.find("a", {"class":"title"}).get_text()
		link = "https://link.springer.com" + info.find("a", {"class":"title"})["href"]
		date = info.find("span", {"class":"year"})["title"]
		authorsTagged = info.findAll("span", {"class":"authors"})
		authors = list()
		for author in authorsTagged:
			authors = author.get_text().split(",\n") + authors
		authorInfo = "Title: " + title + "\n\tLink: " + link + "\n\tAuthor(s): " + ", ".join(authors) + "\n\tDate: " + date + "\n"
		for author in authors:
			allAuthorInfo[author] = authorInfo
	return allAuthorInfo

springer = springer("https://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=13524")
printNames(springer)