"""
This program is used to tracks 11 different social science journals and returns whether any CPI affiliates 
have published their works recently. 
The main process of this program is to:
1. Find all the CPI affiliates from a CSV file located in inequality.stanford.edu
2. Track down all 11 of these journals and find all the authors and their publication information
3. Compare these authors against the CPI affiliates. If the authors match, combine all relevant information
and email this information
Additional notes: Unidecode changes non-English characters to the alphabet. This should be helpful
for any names with accents that may not necessarily match.
"""
import requests 
from bs4 import BeautifulSoup 
from urllib.error import HTTPError 
from urllib.error import URLError
from urllib.request import urlopen 
import re
import smtplib
import feedparser
from unidecode import unidecode
import time
#import csv

CPI_NAMES = "http://inequality.stanford.edu/_affiliates.csv"
JPAM_URL = "/journal/10.1002/(ISSN)1520-6688"
JOMF_URL = "/journal/10.1111/(ISSN)1741-3737/"
AER_URL = "/journals/aer/search-results?current=on&journal=1&q="
AER_ADD_LINK = "https://www.aeaweb.org"
WILEY_ADD_LINK = "http://onlinelibrary.wiley.com"
OUP_ADD_LINK = "http://academic.oup.com/"
DEMOGRAPHY_URL = "https://link.springer.com/search?sortOrder=newestFirst&facet-content-type=Article&facet-journal-id=13524"
NBER_ADD_LINK = "http://www.nber.org"
NBER_URL = "/new.html"
APSR_URL = "https://www.cambridge.org/core/journals/american-political-science-review/latest-issue"
AJS_URL = "/toc/ajs/current"
AJS_ADD_LINK = "http://www.journals.uchicago.edu"
ASR_URL = "/toc/ASR/current"
ASR_ADD_LINK = "http://journals.sagepub.com"
TO = ["yueli72@gmail.com"]
GMAIL_USER = "cpiresearchtracker@gmail.com"
GMAIL_PWD = "1f9RMPapwxwB"
SEND_MAIL_NOW = False
# The following is the user agent for googlebot. May eventually need to update?
HEADERS = {
 	'User-Agent':'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}

def printNames(names): # simple printing command for testing (Not needed otherwise)
  if names == None:
         print("Names could not be found")
  else:
    for name in names:
      print(name + "\n" + names[name])  

# Name variations for all affiliates
def firstLast(content): # first name then last name
	return " ".join(content)

def lastFirst(content): # last name then first name 
	return ", ".join(content[::-1])

def firstInitialLast(content): # first initial then last name
	content[0] = content[0][:1]
	return " ".join(content[::-1])

def lastFirstInitial(content): # last name then first name
	return " ".join(content)

# open url using requests package
# handles errors
def openUrlRequests(url, headers = ""):
	try:
 	    html = requests.get(url, headers = headers).text # open journal home page
 	    return html
	except HTTPError as e: # print error if it encounters any
   	    print(e)
   	    return None

# obtain all affiliate names from the inequality.stanford.edu website
# make a dictionary of names. The key will be the website, the values will be 
# the name variations. This way, fetching the website will be easy and we can
# iterate through all possible name variations
# Currently, everything is in .xls format and it's reading like an html page 
# e.g. <tr><td><td>...</td></td></tr> so I'm reading it as such
# However, in the beginning it was reading like an CSV file, so I kept that case 
# Just in case
def getAffiliateNames(url):
	html = openUrlRequests(url)
	try:
		soup = BeautifulSoup(html, "html.parser")
		allInfo = soup.findAll("tr") # finds each individual row
		allAffiliates = {}
		first = True
		if allInfo == []: # in the case it reads like a csv instead of HTML
			try:
				affiliateFile = csv.reader(unidecode(html.read().decode('utf-8')).splitlines()) # read csv file
				included_cols = [0, 1] # include first and last name column
				for row in affiliateFile: # for every row of the file
					if first:
						first = False # ignore the first row
						pass
					try:
						content = list(row[i] for i in included_cols) # create a list with the first name and last name
						# create variations of the name
						name = [firstLast(content), lastFirst(content), firstInitialLast(content), lastFirstInitial(content)]
						allAffiliates[row[2]] = name # as described, key will be affiliate's page, name will be the list of variations
					except IndexError:
						pass
			except: # if reading the CSV does not work, return none
				return None
		else:
			for info in allInfo: 
				if first:
					first = False # skip the first row
					pass
				try:
				# take the first two columns for first and last name
					content = [unidecode(info.findAll("td")[0].get_text()), unidecode(info.findAll("td")[1].get_text())]
					link = unidecode(info.findAll("td")[2].get_text()) # the third column is the link, which is the key
					# create all variations of the name
					name = [firstLast(content), lastFirst(content), firstInitialLast(content), lastFirstInitial(content)]
					allAffiliates[link] = name
				except IndexError:
					pass
		return allAffiliates
	except AttributeError as e:
		return None

# This gathers all the author information. This was meant to make it easier if we ever
# need to add or change some of the journals
def getAuthorInfo(title = "", issue = "", date = "", authors = "", link = ""):
	message = ""
	if title != "":
		message = message + "\tTitle: " + title
	if issue != "":
		message = message + "\n\tIssue: " + issue
	if date != "":
		message = message + "\n\tDate: " + date
	if authors != "":
		if isinstance(authors, str):
			message = message + "\n\tAuthor(s): " + authors 
		else:
			message = message +  "\n\tAuthor(s): " + ", ".join(authors) 
	if link != "":
		message = message + "\n\tLink: " + link
	return message + "\n"

# remove middle names (takes the first word and the last word)
# returns a list of names without the middle names
# side note: the list of names with the csv file does a similar way of dealing
# with names, so almost all names should match
def removeMiddleName(allNames):
	nameList = list()
	allNames = filter(None, allNames)
	for name in allNames: 
		name = re.sub("\.", "", name) # remove any periods
		fml = name.strip().split(" ") # obtain first middle last name
		pattern = re.compile("Jr|Sr|II|III|IV") 
		if re.search(pattern, fml[-1]): # Ignores suffixes by skipping the last word
			try: # This only applies if length is greater than 1
				fm = [fml[0], fml[-2]]
			except IndexError: 
				pass
		else:
			fm = [fml[0], fml[-1]] # create a list with the first word and the last word (assume first and last name)
		nameList.append(" ".join(fm)) # join together the first and last name as a string, add to the list of names
	return(nameList)

# Find all authors from the American Economic Review
# This one needs headers because I can't open it without changing the user agent to a googlebot
def findAerAuthors(home_url, current_url, headers):
	html = openUrlRequests(home_url + current_url, headers)
	try:
		soup = BeautifulSoup(html, "html.parser")
		allInfo = soup.findAll("li", {"class":"article"})
		allAuthorInfo = {}
		for info in allInfo:
			name = info.find("div") # Where name is located, however some of them don't have authors
			if name != None:
				authors = ' '.join(unidecode(name.get_text()).split()) # Get rid of lots of white spaces
				pattern = re.compile("(by\s)|(,\s)|(\sand\s)") # to check python regex, use pythex.org
				unfiltered_authors = [x for x in pattern.split(authors) if x] # split on by, and, and commas
				# if it's any of the things it's split on, remove it
				list_authors = [x for x in unfiltered_authors if not re.search(pattern, x)] 
				list_authors = removeMiddleName(list_authors)
				title = info.find("h4", {"class":"title"}).get_text().strip("\n")
				link = home_url + info.findAll("a")[1]["href"]
				date = info.find("h5", {"class":"published-at"}).get_text()
				authorInfo = getAuthorInfo(title = title, date = date, authors = authors, link = link)
				for name in list_authors:
					allAuthorInfo[name] = authorInfo
		return allAuthorInfo
	except AttributeError as e:
		return None

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
         	link = AJS_ADD_LINK + info.find("a", {"class":"nowrap"})["href"]
         	authorsTagged = info.findAll("span", {"class":"hlFld-ContribAuthor"})
         	authors = list()
         	for author in authorsTagged:
         		authors.append(unidecode(author.get_text()))
         	authors = removeMiddleName(authors)
         	for author in authors:
         		allAuthorInfo[author] = getAuthorInfo(title = title, issue = issue, authors = authors, link = link)
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
			authors = unidecode(info.find("li", {"class":"author"}).get_text()).replace("\n", " ").title().lstrip(" ")
			authorInfo = getAuthorInfo(title, issue, date, authors, link)
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
			link = ASR_ADD_LINK + info.find("a", {"class":"ref nowrap"})["href"]
			date = info.find("span", {"class":"maintextleft"}).get_text()
			authors = set()
			for author in authorsTagged:
				if not "articles" in author.get_text(): # remove the "See all articles..."
					authors.add(unidecode(author.get_text()).lstrip())
			authorInfo = getAuthorInfo(title, issue, date, authors, link)
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
	    link = NBER_ADD_LINK + info.find("a")["href"]
	    titleAuthors = unidecode(info.get_text()).strip("\n").split("\n")
	    title = titleAuthors[0]
	    allAuthors = re.sub("#.*$","", titleAuthors[1])
	    authorInfo = getAuthorInfo(title = title, authors = allAuthors, date = date, link = link)
	    pattern = re.compile("\s*\,\sand\s|\sand\s|\s*,\s*|\s+$")
	    authors = removeMiddleName([x for x in pattern.split(allAuthors) if x])
	    for author in authors:
	      allAuthorInfo[author] = authorInfo
	  return allAuthorInfo
  except AttributeError as e:
  	return None

def rssFeed(url):
	try:
		feed = feedparser.parse(url)
	except AttributeError:
		return None
	if feed.status == 404: return None
	if feed.status == 503: return None
	allAuthorInfo = {}
	for item in feed["items"]:
		authorInfo = getAuthorInfo(title = unidecode(str(item["title"])), date = unidecode(str(item["published"])), authors = unidecode(str(item["author"])), link = unidecode(str(item["link"])))
		pattern = re.compile("\s*,\s*|\s+$") # pattern to get rid of commas and white spaces
		names = item["author"].rstrip() # get text and the white space at the end
		eachName = removeMiddleName(pattern.split(unidecode(names))) # split at the given patterns
		for name in eachName:
			junk = name.split(" ")
			junk[1] = junk[1][:1] # get the first letter of the first name
			name = " ".join(junk)
			allAuthorInfo[name] = authorInfo
	return allAuthorInfo

def openRss(journal): # open into the rss feed
	try:
		html = urlopen(OUP_ADD_LINK + journal) # open webpage and read
	except HTTPError as e: # print error if it encounters any
   	    print(e)
	try:
   		soup = BeautifulSoup(html, "html.parser")
   		current = soup.find("div", {"class":"current-issue-title widget-IssueInfo__title"}).find("a", {"class":"widget-IssueInfo__link"}) 
   		# find the latest issue
   		currentUrl = OUP_ADD_LINK + current.attrs['href']
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

# find all authors from the Demography journal
# return key of the author's name and title, link, date, and all authors
def findDemographyAuthors(url):
	html = openUrlRequests(url)
	try:
		soup = BeautifulSoup(html, "html.parser")
		allInfo = soup.find("div", {"id":"kb-nav--main"}).findAll("li")
		allAuthorInfo = {}
		for info in allInfo:
			title = info.find("a", {"class":"title"}).get_text().strip()
			link = "https://link.springer.com" + info.find("a", {"class":"title"})["href"]
			date = info.find("span", {"class":"year"})["title"]
			authorsTagged = info.findAll("span", {"class":"authors"})
			authors = list()
			for author in authorsTagged:
				authors = removeMiddleName(unidecode(author.get_text()).split(",\n")) + authors
			authorInfo = getAuthorInfo(title = title, date = date, authors = authors, link = link)
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
            authors = unidecode(record)
          elif re.search(r"\d", record): # if it contains numbers, then it has the date (and a lot of other junk)
            date = re.search("\d+\s[A-Z]*\s\d{4}", record).group() # search for day (digit), month (character), year (four digits) and extract text
          pattern = re.compile("\s*,\s*|\s+$|\sand\s") # compile names by pattern
        if authors != "": # there are a lot of journals w/o author names, ignore those
          splitAuthors = removeMiddleName([x for x in pattern.split(authors) if x]) # split names at the pattern, get rid of middle name
          authorInfo = getAuthorInfo(title, issue, date, authors, link)
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
          currentUrl = WILEY_ADD_LINK + current.attrs['href'] # get to the current issue
     except AttributeError as e: # return if there is an attribute error
          return None
     return findWileyAuthors(currentUrl)


def gatherAllAuthors():
	jpam = openCurrentWiley(WILEY_ADD_LINK + JPAM_URL) # journal of policy analysis and management
	jomf = openCurrentWiley(WILEY_ADD_LINK + JOMF_URL) # journal of marriage and family
	sp = openRss("sp") # social politics 
	sf = openRss("sf") # social force
	qje = openRss("qje") # quarterly journal of economics
	demography = findDemographyAuthors(DEMOGRAPHY_URL) # demography
	nber = findNberAuthors(NBER_ADD_LINK + NBER_URL) # nber
	apsr = findApsrAuthors(APSR_URL) # american political science review
	ajs = findAjsAuthors(AJS_ADD_LINK + AJS_URL) # american sociology journal
	asr = findAsrAuthors(ASR_ADD_LINK + ASR_URL) # american sociological review
	aer = findAerAuthors(AER_ADD_LINK, AER_URL, HEADERS)

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
				  "American Sociology Review" : asr,
				  "American Economic Review" : aer 
	}
	return allAuthors

# Compare against all CPI affiliates and all authors from the journals
def getMessage(allAuthors, cpiAffiliates):
	message = ""
	for journal in allAuthors:
		if allAuthors[journal] is None:
			message = message + "ERROR: " + journal + " cannot be found.\n\n"

	if cpiAffiliates == None or cpiAffiliates == {}:
		message = "List of CPI affiliates was not found.\n\n"
	else:
		for journal in allAuthors:
			first = 0
			if allAuthors[journal] is not None:
				for name in allAuthors[journal]:
					for affiliate in cpiAffiliates:
						for namevariation in cpiAffiliates[affiliate]:
							if namevariation == name and first == 0: # if a name matches
								message = message + journal + "\n\n"
								first = 1
							if namevariation == name:
								message = message + "\t" + journal + ": " + name + " (" + affiliate  + ")\n" + allAuthors[journal][name] + "\n"
	return message
	

# Send the email
def sendAuthorInformation(allAuthors, cpiAffiliates, to, gmail_user, gmail_pwd):
	message = getMessage(allAuthors, cpiAffiliates)
	message = message.encode('ascii', 'ignore').decode('ascii')

	smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo
	smtpserver.login(gmail_user, gmail_pwd)
	header = "To: " + str(to) + '\n' + "From: " + gmail_user + "\n" + "Subject:Research Tracker Report " + time.strftime("%m/%d/%Y") + "\n"
	message = header + message
	smtpserver.sendmail(gmail_user, to, message)
	print("done!")
	smtpserver.close()

# Main task: get all the affiliates, then email all the corresponding information

allAuthors = gatherAllAuthors()
cpiAffiliates = getAffiliateNames(CPI_NAMES) # gather affiliate name

if SEND_MAIL_NOW:
	sendAuthorInformation(allAuthors, cpiAffiliates, TO, GMAIL_USER, GMAIL_PWD) # send email
else:
	print(getMessage(allAuthors, cpiAffiliates))



