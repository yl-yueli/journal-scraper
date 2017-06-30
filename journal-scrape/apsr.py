import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import re

def removeMiddleName(allNames): # remove middle names (takes the first word and the last word)
	nameList = list()
	for name in allNames: 
		fml = name.split(" ") # obtain first middle last name
		fm = [fml[0], fml[-1]] # create a list with the first word and the last word (assume first and last name)
		nameList.append(" ".join(fm)) # join together the first and last name as a string, add to the list of names
	return(nameList)

# Find all APSR authors and their information: title, issue, date, all authors, and link
# Split names and assign each author to its corresponding publication
def findApsrAuthors(url):
	try:
		html = requests.get(url).text 
	except HTTPError as e:
		print(e)
	try:
		soup = BeautifulSoup(html, "html.parser")
		allInfo = soup.findAll("ul", {"class":"details"})
		issue = soup.find("h2", {"class":"heading_07"}).get_text().replace("\n", " ")
		allAuthorInfo = {}
		for info in allInfo:
			title = info.find("li", {"class":"title"}).get_text().strip("\n")
			date = info.find("span", {"class":"date"}).get_text()
			link = info.find("a", {"class":"url"}).get_text()
			authors = info.find("li", {"class":"author"}).get_text().replace("\n", " ").title()
			authorInfo = "Title: " + title + "\n\tIssue: " + issue + "\n\tDate: " + date + "\n\tAuthor(s): " + authors + "\n\tLink: " + link + "\n"
			pattern = re.compile("\s*,\s*|\s+$") # remove commas and spaces at the end
			eachName = removeMiddleName(pattern.split(authors))
			for name in eachName:
				allAuthorInfo[name] = authorInfo
		return allAuthorInfo
	except AttributeError as e: # return if there is an attribute error
         return None

def printNames(names): # simple printing command for testing
	if names == None:
         print("Names could not be found")
	else:
		for name in names:
			print(name + "\n" + names[name])

# automatic link to current issue
apsr = findApsrAuthors("https://www.cambridge.org/core/journals/american-political-science-review/latest-issue")
printNames(apsr)
	