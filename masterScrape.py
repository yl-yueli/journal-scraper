import requests 
from bs4 import BeautifulSoup 
from urllib.error import HTTPError 
from urllib.error import URLError
from urllib.request import urlopen 
import re
import csv
import smtplib

CPI_NAMES = "http://inequality.stanford.edu/_affiliates.csv"
JPAM_URL = "http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1520-6688"
JOMF_URL = "http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1741-3737"
WILEY_URL = "http://onlinelibrary.wiley.com/"
OUP_URL = "http://academic.oup.com/"
DEMOGRAPHY_URL = "https://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=13524"
NBER_URL = "http://www.nber.org/new.html"
APSR_URL = "https://www.cambridge.org/core/journals/american-political-science-review"
ASJ_URL = "http://www.journals.uchicago.edu/toc/ajs/current"
ASR_URL = "http://journals.sagepub.com/toc/ASR/current"
TO = "yueli72@gmail.com"
GMAIL_USER = "cpiresearchtracker@gmail.com"
GMAIL_PWD = "1f9RMPapwxwB"


def firstLast(content): # first name then last name
	return " ".join(content)

def lastFirst(content): # last name then first name 
	return ", ".join(content[::-1])

def firstInitialLast(content): # first initial then last name
	content[0] = content[0][:1]
	return " ".join(content[::-1])

def lastFirstInitial(content): # last name then first name
	return " ".join(content)

def getAffiliateNames(url): # obtain all affiliate names
	html = urlopen(url)
	affiliateFile = csv.reader(html.read().decode('utf-8').splitlines()) # read csv file
	included_cols = [0, 1] # include first and last name column
	nameDict = {} # create a name dictionary. The key will be the affiliate's page, values will be all combinations of the name

	for row in affiliateFile: # for every row of the file
		content = list(row[i] for i in included_cols) # create a list with the first name and last name
		name = [firstLast(content), lastFirst(content), firstInitialLast(content), lastFirstInitial(content)]
		# create variations of the name
		nameDict[row[2]] = name # as described, key will be affiliate's page, name will be the list of variations
	return nameDict


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

def findAsjAuthors(url): # find authors for American Sociology Journal
     html = openUrlRequests(url) # use requests to open the page
     try:
     	bsObj = BeautifulSoup(html, "html.parser")
     	allNamesUnclean = bsObj.findAll("span", {"class":"hlFld-ContribAuthor"}) # tag for author listing
     	nameList = list()
     	for name in allNamesUnclean: # unclean list of names with tags
     		nameList.append(name.get_text()) 
     	return removeMiddleName(nameList) # return after removing middle name
     except AttributeError as e: # return if there is an attribute error
     	return None

def findApsrAuthors(url): # find all authors for American Political Science Review
	html = openUrlRequests(url) # use requests to open page
	try:
		soup = BeautifulSoup(html, "html.parser")
		allNamesUnclean = soup.findAll("li", {"class":"author"}) # tag for author listing
		nameList = list()
		pattern = re.compile("\s*,\s*|\s+$") # remove commas and spaces at the end
		for name in allNamesUnclean:
			name = name.get_text().lstrip("\n").title() # remove new line at the end of names, change to title case
			nameList = nameList + pattern.split(name) # split names at the given pattern
		return removeMiddleName(nameList) # return after removing middle name
	except AttributeError as e: # return if there is an attribute error
         return None


def findAsrAuthors(url): # find all authors for the American Sociological Review
	html = openUrlRequests(url) # use requests to open the page
	try:
		soup = BeautifulSoup(html, "html.parser")
		# this soupList contains "See all articles..." which has the same tag, so remove it later
		soupList = soup.findAll("a", class_="entryAuthor", href=re.compile("^(/author/).*(\%2C\+).*$")) # tag for author listing
	except AttributeError as e:
		return None
	nameList = list() # create an empty set of the actual names
	for name in soupList: # find all the names in the soupList, excluding "See all entries..."
		if not "articles" in name.get_text(): # remove the "See all articles..."
			nameList.append(name.getText().lstrip()) # remove the white space in the front
	return removeMiddleName(nameList) # return the names removing middle name


def findNberAuthors(url): # get names for National Bureau of Economic Research
     html = openUrlRequests(url)
     soup = BeautifulSoup(html, "html.parser")
     allTitles = soup.find("ul").findAll("li") # tag for the authors
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
     return removeMiddleName(nameList)

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
		html = urlopen(OUP_URL + journal) # open webpage and read
	except HTTPError as e: # print error if it encounters any
   	    print(e)
	try:
   		soup = BeautifulSoup(html, "html.parser")
   		current = soup.find("div", {"class":"current-issue-title widget-IssueInfo__title"}).find("a", {"class":"widget-IssueInfo__link"}) # find the latest issue
   		currentUrl = OUP_URL + current.attrs['href']
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
	return removeMiddleName(nameList)

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
	return removeMiddleName(nameList)

def openCurrentWiley(url): # navigate to the current issue
     html = openUrlRequests(url)
     try:
          soup = BeautifulSoup(html, "html.parser")
          current = soup.find("a", {"id":"currentIssueLink"}) # find the link to the current issue
          currentUrl = WILEY_URL + current.attrs['href'] # get to the current issue
     except AttributeError as e: # return if there is an attribute error
          return None
     return findWileyAuthors(currentUrl)

def gatherAllAuthors():
	jpam = openCurrentWiley(JPAM_URL) # journal of policy analysis and management
	jomf = openCurrentWiley(JOMF_URL) # journal of marriage and family
	sp = openRss("sp") # social politics 
	sf = openRss("sf") # social force
	qje = openRss("qje") # quarterly journal of economics
	demography = findDemographyAuthors(DEMOGRAPHY_URL) # demography
	nber = findNberAuthors(NBER_URL) # nber
	apsr = findApsrAuthors(APSR_URL) # american political science review
	asj = findAsjAuthors(ASJ_URL) # american sociology journal
	asr = findAsrAuthors(ASR_URL) # american sociological review

	# create a dictionary of all authors, journal name as key and the list of names as values
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
	return allAuthors

allAuthors = gatherAllAuthors()

def sendAuthorInformation(allAuthors, to, gmail_user, gmail_pwd):
	message = ""
	cpiAffliates = getAffiliateNames(CPI_NAMES) # gather affiliate name

	for affiliate in cpiAffliates: # loop through all affiliates
		for namevariation in cpiAffliates[affiliate]: # loop through all name variations
			for journal in allAuthors: # loop through the journals
				for name in allAuthors[journal]: # loop through all authors of the journal
					if namevariation == name: # if a name matches
						print(journal + ": " + name + " " + affiliate)
						message = message + "\n" + journal + ": " + name + " " + affiliate + " \n" # add to email message

	smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo
	smtpserver.login(gmail_user, gmail_pwd)
	header = "To: " + to + '\n' + "From: " + gmail_user + "\n" + "Subject:Research Tracker Report\n"
	message = header + message
	smtpserver.sendmail(gmail_user, to, message)
	print("done!")
	smtpserver.close()

sendAuthorInformation(allAuthors, TO, GMAIL_USER, GMAIL_PWD) # send email

