import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import re

def openUrlRequests(url):
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
        title = info.find("a", {"href":re.compile("^\/(doi)\/(\d+\.\d+)/[a-z]*\.\d*\/(full)$")}).get_text() 
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
          authorInfo = "Title: " + title + "\n\tIssue: " + issue + "\n\tDate: " + date + "\n\tAuthors: " + authors + "\n\tLink: " + link 
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
          currentUrl = "http://onlinelibrary.wiley.com/" + current.attrs['href'] # get to the current issue
     except AttributeError as e: # return if there is an attribute error
          return None
     return findWileyAuthors(currentUrl)

def printNames(names): # simple printing command for testing
  if names == None:
         print("Names could not be found")
  else:
    for name in names:
      print(name + "\n" + names[name])  


jpam = openCurrentWiley("http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1520-6688")
jomf = openCurrentWiley("http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1741-3737")

printNames(jpam)
printNames(jomf)