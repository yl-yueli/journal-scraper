import csv
from urllib.request import urlopen

def firstLast(content):
	return " ".join(content)

def lastFirst(content):
	return ", ".join(content[::-1])

def firstInitialLast(content):
	content[0] = content[0][:1]
	return ", ".join(content[::-1])

def lastFirstInitial(content):
	return " ".join(content)

url = 'http://inequality.stanford.edu/_affiliates.csv'
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
