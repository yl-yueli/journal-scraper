import requests 
from bs4 import BeautifulSoup 
from urllib.error import HTTPError 
from urllib.error import URLError
from urllib.request import urlopen 
import re
import csv
import smtplib
import feedparser

CPI_NAMES = "http://inequality.stanford.edu/_affiliates.csv"
JPAM_URL = "http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1520-6688"
JOMF_URL = "http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1741-3737"
WILEY_URL = "http://onlinelibrary.wiley.com"
OUP_URL = "http://academic.oup.com/"
DEMOGRAPHY_URL = "https://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=13524"
NBER_URL = "http://www.nber.org/new.html"
APSR_URL = "https://www.cambridge.org/core/journals/american-political-science-review/latest-issue"
AJS_URL = "http://www.journals.uchicago.edu/toc/ajs/current"
ASR_URL = "http://journals.sagepub.com/toc/ASR/current"
TO = "yueli72@gmail.com"
GMAIL_USER = "cpiresearchtracker@gmail.com"
GMAIL_PWD = "1f9RMPapwxwB"
sendMailNow = True

def printNames(names): # simple printing command for testing
  if names == None:
         print("Names could not be found")
  else:
    for name in names:
      print(name + "\n" + names[name])  


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
	first = True
	for row in affiliateFile: # for every row of the file
		if first:
			first = False
			continue 
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

# remove middle names (takes the first word and the last word)
def removeMiddleName(allNames):
	nameList = list()
	for name in allNames: 
		fml = name.lstrip().split(" ") # obtain first middle last name
		fm = [fml[0], fml[-1]] # create a list with the first word and the last word (assume first and last name)
		nameList.append(" ".join(fm)) # join together the first and last name as a string, add to the list of names
	return(nameList)

# Find authors for American Journal of Sociology including issue, title, authors, and link
# In this case, names are already in a list, so we individually loop through the names instead
# of having to split the names
def findAjsAuthors(url): 
     html = openUrlRequests(url)
     try:
         soup = BeautifulSoup(html, "html.parser")
         allInfo = soup.findAll("table", {"class":"articleEntry"})
         issue = soup.find("h1", {"class","widget-header header-regular toc-heading"}).get_text().rstrip("\n")
         allAuthorInfo = {}
         for info in allInfo:
         	title = info.find("span", {"class":"hlFld-Title"}).get_text()
         	link = "http://www.journals.uchicago.edu" + info.find("a", {"class":"nowrap"})["href"]
         	authorsTagged = info.findAll("span", {"class":"hlFld-ContribAuthor"})
         	authors = list()
         	for author in authorsTagged:
         		authors.append(author.get_text())
         	authors = removeMiddleName(authors)
         	for author in authors:
         		allAuthorInfo[author] = "Title: " + title + "\n\tIssue: " + issue + "\n\tAuthor(s): " + ", ".join(authors)  + "\n\tLink: " + link + "\n"
         return allAuthorInfo
     except AttributeError as e:
        return None

# Find all APSR authors and their information: title, issue, date, all authors, and link
# Split names and assign each author to its corresponding publication
def findApsrAuthors(url):
	html = openUrlRequests(url)
	try:
		soup = BeautifulSoup(html, "html.parser")
		allInfo = soup.findAll("ul", {"class":"details"})
		issue = soup.find("h2", {"class":"heading_07"}).get_text().replace("\n", " ")
		allAuthorInfo = {}
		for info in allInfo:
			title = info.find("li", {"class":"title"}).get_text().strip("\n")
			date = info.find("span", {"class":"date"}).get_text()
			link = info.find("a", {"class":"url"}).get_text()
			authors = info.find("li", {"class":"author"}).get_text().replace("\n", " ").title().lstrip(" ")
			authorInfo = "Title: " + title + "\n\tIssue: " + issue + "\n\tDate: " + date + "\n\tAuthor(s): " + authors + "\n\tLink: " + link + "\n"
			pattern = re.compile("\s*,\s*|\s+$") # remove commas and spaces at the end
			eachName = removeMiddleName(pattern.split(authors))
			for name in eachName:
				allAuthorInfo[name] = authorInfo
		return allAuthorInfo
	except AttributeError as e: # return if there is an attribute error
         return None


def findAsrAuthors(url): # find all authors for the American Sociological Review
	html = openUrlRequests(url) # use requests to open the page
	try:
		soup = BeautifulSoup(html, "html.parser")
		# this soupList contains "See all articles..." which has the same tag, so remove it later
		allInfo = soup.findAll("table", {"class":"articleEntry"})
		issue = soup.find("title").get_text()
		allAuthorInfo = {}
		for info in allInfo:
			authorsTagged = info.findAll("a", class_="entryAuthor", href=re.compile("^(/author/).*(\%2C\+).*$"))
			title = info.find("span", {"class":"hlFld-Title"}).get_text()
			link = "http://journals.sagepub.com/" + info.find("a", {"class":"ref nowrap"})["href"]
			date = info.find("span", {"class":"maintextleft"}).get_text()
			authors = set()
			for author in authorsTagged:
				if not "articles" in author.get_text(): # remove the "See all articles..."
					authors.add(author.get_text().lstrip())
			authorInfo = "Title: " + title + "\n\tIssue: " + issue + "\n\tDate: " + date + "\n\tAuthor(s): " + ", ".join(authors) + "\n\tLink: " + link + "\n"
			authors = removeMiddleName(authors)
			for author in authors:
				allAuthorInfo[author] = authorInfo
		return allAuthorInfo
	except AttributeError as e:
		return None


def findNberAuthors(url):
  html = openUrlRequests(url)
  try:
	  soup = BeautifulSoup(html, "html.parser")
	  date = re.search("[A-z]*\s+\d+\,\s\d{4}$", soup.findAll("b")[1].get_text()).group()
	  allInfo = soup.find("ul").findAll("li")
	  allAuthorInfo = {}
	  for info in allInfo:
	    link = "http://www.nber.org" + info.find("a")["href"]
	    titleAuthors = info.get_text().strip("\n").split("\n")
	    title = titleAuthors[0]
	    allAuthors = re.sub("#.*$","", titleAuthors[1])
	    authorInfo = "Title: " + title + "\n\tAuthor(s): " + allAuthors + "\n\tDate: " + date + "\n\tLink: " + link + "\n"
	    pattern = re.compile("\s*\,\sand\s|\sand\s|\s*,\s*|\s+$")
	    authors = removeMiddleName([x for x in pattern.split(allAuthors) if x])
	    for author in authors:
	      allAuthorInfo[author] = authorInfo
	  return allAuthorInfo
  except AttributeError as e:
  	return None

def rssFeed(url):
	feed = feedparser.parse(url)
	allAuthorInfo = {}
	for item in feed["items"]:
		authorInfo = str("Title: " + item["title"] + "\n\tAuthor(s): " + item["author"] + "\n\tLink: " + item["link"] + "\n")
		pattern = re.compile("\s*,\s*|\s+$") # pattern to get rid of commas and white spaces
		names = item["author"].rstrip() # get text and the white space at the end
		eachName = pattern.split(names) # split at the given patterns
		for name in eachName:
			junk = name.split(" ")
			junk[1] = junk[1][:1]
			name = " ".join(junk)
			allAuthorInfo[name] = authorInfo
	return allAuthorInfo

def openRss(journal): # open into the rss feed
	try:
		html = urlopen(OUP_URL + journal) # open webpage and read
	except HTTPError as e: # print error if it encounters any
   	    print(e)
	try:
   		soup = BeautifulSoup(html, "html.parser")
   		current = soup.find("div", {"class":"current-issue-title widget-IssueInfo__title"}).find("a", {"class":"widget-IssueInfo__link"}) 
   		# find the latest issue
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
				authors = removeMiddleName(author.get_text().split(",\n")) + authors
			authorInfo = "Title: " + title + "\n\tLink: " + link + "\n\tAuthor(s): " + ", ".join(authors) + "\n\tDate: " + date + "\n"
			for author in authors:
				allAuthorInfo[author] = authorInfo
		return allAuthorInfo
	except AttributeError as e:
		return None

# Find all Wiley authors and the following information: title, link, date, and authors
# Differentiate between all the authors and give them each a separate name so it will be easy to iterate over
def findWileyAuthors(url): # find authors in Journal of Family & Marriage and Policy & Management
     html = openUrlRequests(url)
     try:
      soup = BeautifulSoup(html, "html.parser")
      issue = soup.find("p", {"class":"issueAndVolume"}).get_text()
      allInfo = soup.findAll("div", {"class":"citation tocArticle"}) # tag works best for p
      allAuthorInfo = {} # empty dictionary, author name as key and author info as the value
      for info in allInfo:
        # regex for the article link e.g. doi/10.1002/pam.21989/full
        title = info.find("a", {"href":re.compile("^\/(doi)\/(\d+\.\d+)/[a-z]*\.\d*\/(full)$")}).get_text().replace("\u2013", "-")
        link = "http://onlinelibrary.wiley.com" + info.find("a", {"href":re.compile("^\/(doi)\/(\d+\.\d+)/[a-z]*\.\d*\/(full)$")})["href"] # get the actual link
        name_date = info.findAll("p") # tag to find the author names and date
        date = ""
        authors = ""
        for record in name_date: # this for loops determines whether it's a name or date
          record = record.get_text()
          # if it does not contain a digit (i.e. not a date), does not contain the name of the journal)
          if not re.search(r"\d|(Public)|(National)|^$", record): 
            authors = record
          elif re.search(r"\d", record): # if it contains numbers, then it has the date (and a lot of other junk)
            date = re.search("\d+\s[A-Z]*\s\d{4}", record).group() # search for day (digit), month (character), year (four digits) and extract text
          pattern = re.compile("\s*,\s*|\s+$|\sand\s") # compile names by pattern
        if authors != "": # there are a lot of journals w/o author names, ignore those
          splitAuthors = removeMiddleName([x for x in pattern.split(authors) if x]) # split names at the pattern, get rid of middle name
          authorInfo = "Title: " + title + "\n\tIssue: " + issue + "\n\tDate: " + date + "\n\tAuthors: " + authors + "\n\tLink: " + link +"\n"
          for author in splitAuthors: # go through the list of split authors, give them all the same values
            allAuthorInfo[author] = authorInfo # give the author their info
      return allAuthorInfo # return the dictionary
     except AttributeError as e:
          return None

def openCurrentWiley(url): # navigate to the current issue
     html = openUrlRequests(url)
     try:
          soup = BeautifulSoup(html, "html.parser")
          current = soup.find("a", {"id":"currentIssueLink"}) # find the link to the current issue
          currentUrl = WILEY_URL + current.attrs['href'] # get to the current issue
     except AttributeError as e: # return if there is an attribute error
          return None
     return findWileyAuthors(currentUrl)

jomf = openCurrentWiley(JOMF_URL)
print(jomf)
printNames(jomf)


def gatherAllAuthors():
	jpam = openCurrentWiley(JPAM_URL) # journal of policy analysis and management
	jomf = openCurrentWiley(JOMF_URL) # journal of marriage and family
	sp = openRss("sp") # social politics 
	sf = openRss("sf") # social force
	qje = openRss("qje") # quarterly journal of economics
	demography = findDemographyAuthors(DEMOGRAPHY_URL) # demography
	nber = findNberAuthors(NBER_URL) # nber
	apsr = findApsrAuthors(APSR_URL) # american political science review
	ajs = findAjsAuthors(AJS_URL) # american sociology journal
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
				  "American Journal of Sociology" : ajs,
				  "American Sociology Review" : asr 
	}
	return allAuthors

allAuthors = gatherAllAuthors()
cpiAffliates = getAffiliateNames(CPI_NAMES) # gather affiliate name

def sendAuthorInformation(allAuthors, to, gmail_user, gmail_pwd):
	message = ""

	for affiliate in cpiAffliates: # loop through all affiliates
		for namevariation in cpiAffliates[affiliate]: # loop through all name variations
			for journal in allAuthors: # loop through the journals
				if allAuthors[journal] is not None:
					for name in allAuthors[journal]: # loop through all authors of the journal
						if namevariation == name: # if a name matches
							print(journal + ": " + name + " (" + affiliate  + ")\n" + allAuthors[journal][name])
							message = message + "\n" + journal + ": " + name + " (" + affiliate  + ")\n" + allAuthors[journal][name] # add to email message

	message = message.encode("utf-8").decode("utf-8")

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

if sendMailNow:
	sendAuthorInformation(allAuthors, TO, GMAIL_USER, GMAIL_PWD) # send email
else:
	for affiliate in cpiAffliates: # loop through all affiliates
		for namevariation in cpiAffliates[affiliate]: # loop through all name variations
			for journal in allAuthors: # loop through the journals
				if allAuthors[journal] is not None:
					for name in allAuthors[journal]: # loop through all authors of the journal
						if namevariation == name: # if a name matches
							print(journal + ": " + name + " (" + affiliate  + ")\n" + allAuthors[journal][name])


