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

def findNberAuthors(url):
  html = openUrlRequests(url)
  soup = BeautifulSoup(html, "html.parser")
  date = soup.findAll("b")[1].get_text()
  allInfo = soup.find("ul").findAll("li")
  allAuthorInfo = {}
  for info in allInfo:
    link = "http://www.nber.org" + info.find("a")["href"]
    titleAuthors = info.get_text().strip("\n").split("\n")
    title = titleAuthors[0]
    allAuthors = re.sub("#.*$","", titleAuthors[1])
    authorInfo = "Title: " + title + "\n\t" + link + "\n\tAuthor(s): " + allAuthors + "\n\tDate: " + date
    pattern = re.compile("\s*\,\sand\s|\sand\s|\s*,\s*|\s+$")
    authors = [x for x in pattern.split(allAuthors) if x]
    for author in authors:
      allAuthorInfo[author] = authorInfo
  return allAuthorInfo

def printNames(names): # simple printing command for testing
  if names == None:
         print("Names could not be found")
  else:
    for name in names:
      print(name + "\n" + names[name])

     #nameListAppend = set()
     #for title in allTitles:
     #     title = title.get_text()
     #     nameTitle = re.split("\n", title)
     #     for name in nameTitle:
     #          if "#" in name:
     #               name = re.sub("#.*$","", name)
     #               nameListAppend.add(name)
     #nameList = list()
     #for name in nameListAppend:
     #     pattern = re.compile("\s*\,\sand\s|\sand\s|\s*,\s*|\s+$")
     #     names = [x for x in pattern.split(name) if x]
     #     nameList = nameList + names
     #for name in nameList:
     #     print(name)

nber = findNberAuthors("http://www.nber.org/new.html")
printNames(nber)
