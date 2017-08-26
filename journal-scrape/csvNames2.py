import csv
from urllib.request import urlopen

url = 'http://inequality.stanford.edu/_affiliates.csv'
html = urlopen(url)
cr = csv.reader(html.read().decode('utf-8').splitlines())
included_cols = [0, 1]
for row in cr:
    content = list(row[i] for i in included_cols)
    print(content)
