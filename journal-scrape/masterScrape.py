import requests 
from bs4 import BeautifulSoup 
from urllib.error import HTTPError 
from urllib.error import URLError
from urllib.request import urlopen 
import re
import csv

CPINAMES = "http://inequality.stanford.edu/_affiliates.csv"
JPAMURL = "http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1520-6688"
JOMFURL = "http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1741-3737"
WILEYURL = "http://onlinelibrary.wiley.com/"
OUPURL = "http://academic.oup.com/"
DEMOGRAPHYURL = "https://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=13524"
NBERURL = "http://www.nber.org/new.html"
APSRURL = "https://www.cambridge.org/core/journals/american-political-science-review"
ASJURL = "http://www.journals.uchicago.edu/toc/ajs/current"
ASRURL = "http://journals.sagepub.com/toc/ASR/current"


def firstLast(content):
	return " ".join(content)

def lastFirst(content):
	return ", ".join(content[::-1])

def firstInitialLast(content):
	content[0] = content[0][:1]
	return ", ".join(content[::-1])

def lastFirstInitial(content):
	return " ".join(content)

def getAffiliateNames(url):
	html = urlopen(url)
	cr = csv.reader(html.read().decode('utf-8').splitlines())
	included_cols = [0, 1]
	nameDict = {}

	for row in cr:
		content = list(row[i] for i in included_cols)
		name = [firstLast(content), lastFirst(content), firstInitialLast(content), lastFirstInitial(content)]
		nameDict[firstLast(content)] = name

	for key in nameDict:
		for name in nameDict[key]:
			print(name)
	return nameDict



def openUrlRequests(url):
	try:
 	    html = requests.get(url).text # open journal home page
 	    return html
	except HTTPError as e: # print error if it encounters any
   	    print(e)
   	    return None

def removeMiddleName(allNames):
	nameList = list()
	for name in allNames: 
		fml = name.split(" ") # obtain first middle last name
		fm = [fml[0], fml[-1]]
		nameList.append(" ".join(fm))
	return(nameList)

def findAsjAuthors(url):
     html = openUrlRequests(url)
     try:
     	bsObj = BeautifulSoup(html, "html.parser")
     	allNamesUnclean = bsObj.findAll("span", {"class":"hlFld-ContribAuthor"})
     	allNames = list()
     	for name in allNamesUnclean:
     		allNames.append(name.get_text())
     	return removeMiddleName(allNames)
     except AttributeError as e: # return if there is an attribute error
     	return None

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
		return removeMiddleName(allNames)
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
	nameList = list() # create an empty set of the actual names
	for name in soupList: # find all the names in the soupList, excluding "See all entries..."
		if not "articles" in name.get_text(): # remove the "See all articles..."
			nameList.append(name.getText().lstrip()) # remove the white space in the front
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
	finalName = list() # problem: some names have period after them, some names have more than one initial
	for name in allNames:
		uncleanNames = name.split(" ") # split names with spaces
		uncleanNames[1] = uncleanNames[1][:1] # for the first name (in the second index), get only the first leter
		finalName.append(" ".join(uncleanNames)) # join the names back together
	return finalName # return all names

def openRss(journal): # open into the rss feed
	try:
		html = urlopen(OUPURL + journal) # open webpage and read
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
          currentUrl = WILEYURL + current.attrs['href'] # get to the current issue
     except AttributeError as e: # return if there is an attribute error
          return None
     return findWileyAuthors(currentUrl)

cpiAffliates = getAffiliateNames(CPINAMES)

jpam = openCurrentWiley(JPAMURL) # journal of policy analysis and management

jomf = openCurrentWiley(JOMFURL) # journal of marriage and family

sp = openRss("sp") # social politics 

sf = openRss("sf") # social force

qje = openRss("qje") # quarterly journal of economics

demography = findDemographyAuthors(DEMOGRAPHYURL) # demography

nber = findNberAuthors(NBERURL) # nber

apsr = findApsrAuthors(APSRURL) # american political science review

asj = findAsjAuthors(ASJURL) # american sociology journal

asr = findAsrAuthors(ASRURL) # american sociological review


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

