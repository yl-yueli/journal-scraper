import requests 
from bs4 import BeautifulSoup 
from urllib.error import HTTPError 
from urllib.error import URLError
from urllib.request import urlopen 
import re

def openUrlRequests(url):
	try:
 	    html = requests.get(url).text # open journal home page
 	    return html
	except HTTPError as e: # print error if it encounters any
   	    print(e)
   	    return None


def findAsjAuthors(url):
     html = openUrlRequests(url)
     try:
     	bsObj = BeautifulSoup(html, "html.parser")
     	allNames = bsObj.findAll("span", {"class":"hlFld-ContribAuthor"})
     except AttributeError as e: # return if there is an attribute error
     	return None
     nameList = list()
     for name in allNames:
     	nameList.append(name.get_text())
     return nameList

def findApsrAuthors(url):
	html = openUrlRequests(url)
	try:
		soup = BeautifulSoup(html, "html.parser")
		nameList = soup.findAll("li", {"class":"author"})
		allNames = list()
		pattern = re.compile("\s*,\s*|\s+$")
		for name in nameList:
			name = name.get_text().lstrip("\n").title()
			allNames = allNames + pattern.split(name)
		return allNames
	except AttributeError as e: # return if there is an attribute error
         return None


def findAsrAuthors(url):
	html = openUrlRequests(url)
	try:
		soup = BeautifulSoup(html, "html.parser")
		# this soupList contains "See all articles..." which has the same tag, so remove it later
		soupList = soup.findAll("a", class_="entryAuthor", href=re.compile("^(/author/).*(\%2C\+).*$")) 
	except AttributeError as e:
		return None
	nameList = set() # create an empty set of the actual names
	for name in soupList: # find all the names in the soupList, excluding "See all entries..."
		if not "articles" in name.get_text(): # remove the "See all articles..."
			nameList.add(name.getText().lstrip()) # remove the white space in the front
	return nameList # return the names


def findNberAuthors(url): # get names for National Bureau of Economic Research
     html = openUrlRequests(url)
     soup = BeautifulSoup(html, "html.parser")
     allTitles = soup.find("ul").findAll("li") # 
     nameListAppend = set()
     for title in allTitles:
          title = title.get_text()
          nameTitle = re.split("\n", title)
          for name in nameTitle:
               if "#" in name:
                    name = re.sub("#.*$","", name)
                    nameListAppend.add(name)
     nameList = list()
     for name in nameListAppend:
          pattern = re.compile("\s*\,\sand\s|\sand\s|\s*,\s*|\s+$")
          names = [x for x in pattern.split(name) if x]
          nameList = nameList + names
     return nameList

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

def findDemographyAuthors(url):
	html = openUrlRequests(url)
	try:
		bsObj = BeautifulSoup(html, "html.parser")
		allNamesUnclean = bsObj.findAll("a", href=re.compile("^(\/search\?facet-creator=\%22).*$"))
		nameList = list()
	except AttributeError as e:
		return None
	for name in allNamesUnclean:
		nameList.append(name.get_text())
	return(nameList)

def findWileyAuthors(url): # find authors in Journal of Family and Marriage and Policy and Management
	html = openUrlRequests(url)
	try:
		soup = BeautifulSoup(html, "html.parser")
		allParagraphs = soup.findAll("p") # tag works best for p
	except AttributeError as e:
		return None
	uncleanNames = set() # set of all names in the list of names (John Jay, Alexander...)
	nameList = list() # final list of all names
	for name in allParagraphs:
		name = name.get_text() # get plain text without the tags
		if not re.search(r"\d|(Public)|(National)|^$", name): 
			# get rid of dates of publication (things with digits) as well as some publication information
			uncleanNames.add(name)
	for name in uncleanNames: # have a name, one by one
		pattern = re.compile("\s*,\s*|\s+$|\sand\s") # compile names by pattern
		names = [x for x in pattern.split(name) if x] # split names at the pattern
		nameList = nameList + names # add to the name list
	return nameList

def openCurrentWiley(url): # navigate to the current issue
     html = openUrlRequests(url)
     try:
          soup = BeautifulSoup(html, "html.parser")
          current = soup.find("a", {"id":"currentIssueLink"}) # find the link to the current issue
          currentUrl = "http://onlinelibrary.wiley.com/" + current.attrs['href'] # get to the current issue
     except AttributeError as e: # return if there is an attribute error
          return None
     return findWileyAuthors(currentUrl)


jpam = openCurrentWiley("http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1520-6688") # journal 

jomf = openCurrentWiley("http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1741-3737") # journal of marriage and family

sp = openRss("sp") # social politics 

sf = openRss("sf") # social force

qje = openRss("qje") # quarterly journal of economics

demography = findDemographyAuthors("https://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=13524")

nber = findNberAuthors("http://www.nber.org/new.html")

apsr = findApsrAuthors("https://www.cambridge.org/core/journals/american-political-science-review")

asj = findAsjAuthors("http://www.journals.uchicago.edu/toc/ajs/current")

asr = findAsrAuthors("http://journals.sagepub.com/toc/ASR/current")

allAuthors = {"Journal of Policy and Analysis" : jpam,
			  "Journal of Marriage and Family" : jomf,
			  "Social Politics" : sp,
			  "Social Force" : sf,
			  "Quarterly Journal of Economics" : qje,
			  "Demography" : demography,
			  "NBER" : nber,
			  "American Political Science Review" : apsr,
			  "American Journal of Sociology" : asj,
			  "American Sociology Review" : asr 
}

for key in allAuthors:
	print(key)
	for name in allAuthors[key]:
		print(name)

